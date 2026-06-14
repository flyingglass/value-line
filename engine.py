# -*- coding: utf-8 -*-
"""
engine.py — 从 SQLite 计算 Value Line 指标, 输出 report_data.json
纯数据驱动, 零硬编码, 支持多股票
"""
import os, sys, sqlite3, json, math, requests
import warnings, re; warnings.filterwarnings("ignore")
if sys.platform == 'win32': sys.stdout.reconfigure(encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config

# 财年结束月: 从 config 读取或默认 12-31
def _fye(yr):
    """返回该财年对应的报告日期 (eg. yr=2026,fye=03-31 → "2026-03-31")"""
    stock = config.STOCKS.get(config.ACTIVE_STOCK, {})
    fye = stock.get("fiscal_yr_end", "12-31")
    market = stock.get("market", "hk")
    return f"{yr}-{fye}"


def _resolve_rd(reader, yr, candidates):
    """在 DB indicators 表中查找给定年份的第一个匹配 report_date。返回精确日期或 None。"""
    if isinstance(candidates, list):
        for rd in candidates:
            try:
                r = reader.conn.execute(
                    "SELECT 1 FROM indicators WHERE report_date=? LIMIT 1",
                    (rd,)).fetchone()
                if r:
                    return rd
            except Exception:
                pass
        # fallback: LIKE 查询
        try:
            r = reader.conn.execute(
                "SELECT report_date FROM indicators WHERE report_date LIKE ? ORDER BY report_date DESC LIMIT 1",
                (f"{yr}-01-%",)).fetchone()
            if r:
                return r[0]
        except Exception:
            pass
        return None
    return candidates


def _fye_resolved(reader, yr):
    """返回该财年实际匹配的报告日期 (美股浮动日期自动匹配)"""
    rd = _fye(yr)
    if isinstance(rd, list):
        return _resolve_rd(reader, yr, rd)
    return rd


# ============================================================
# THS A股字段映射
# ============================================================
THS_INDICATOR_MAP = {
    "operating_income_total": "OPERATE_INCOME",
    "parent_holder_net_profit": "HOLDER_PROFIT",
    "basic_eps": "BASIC_EPS",
    "index_weighted_avg_roe": "ROE_AVG",
    "index_per_operating_cash_flow_net": "PER_NETCASH_OPERATE",
    "calc_per_net_assets": "BPS",
    "assets_debt_ratio": "DEBT_ASSET_RATIO",
    "sale_gross_margin": "GROSS_MARGIN",
    "sale_net_interest_ratio": "NET_PROFIT_RATIO",
}
THS_FINANCIAL_MAP = {
    # balance
    "assets_total": "总资产",
    "total_debt": "总负债",
    "holder_equity_total": "总权益",
    "total_current_assets": "流动资产合计",
    "current_total_debt": "流动负债合计",
    "total_cash": "现金及等价物",
    "inventory": "存货",
    "accounts_receivable": "应收帐款",
    "fixed_assets_total": "固定资产",
    "construction_in_process": "在建工程",
    "intangible_assets": "无形资产",
    "goodwill": "商誉",
    "short_term_loans": "短期贷款",
    "long_term_loan": "长期贷款",
    "long_term_payable_total": "长期应付款",
    "lease_debt": "融资租赁负债(非流动)",
    "year_non_current_debt": "融资租赁负债(流动)",
    "bonds_payable_total": "应付债券",
    "non_current_liabilities_total": "非流动负债合计",
    # income
    "operating_income_total": "营业额",
    "operating_profit": "经营溢利",
    "financial_interest_expenses": "融资成本",
    "gross_profit": "毛利",
    "parent_holder_net_profit": "股东应占溢利",
    "operating_costs_total": "营业成本",
    "sales_fee": "销售费用",
    "manage_fee": "管理费用",
    "research_and_development_expenses": "研发费用",
    "taxes_and_surcharges": "税金及附加",
    # cashflow
    "fixed_assets_net_cash": "购建固定资产",
    "depreciation_etc": "加:折旧及摊销",
    "pay_subsidiary_and_other_net_cash": "取得子公司及其他营业单位支付的现金净额",
}
# 旧中文名 → 新THS列名映射 (AKShare THS API 格式变更后的适配)
_THS_NAME_MAP = {
    # Balance
    "总资产": "*资产合计",
    "总负债": "*负债合计",
    "总权益": "*所有者权益（或股东权益）合计",
    "流动资产合计": "流动资产合计",
    "流动负债合计": "流动负债合计",
    "现金及等价物": "总现金",
    "存货": "存货",
    "应收帐款": "其他应收款合计",
    "固定资产": "固定资产合计",
    "在建工程": "在建工程合计",
    "无形资产": "无形资产",
    "商誉": "商誉",
    "短期贷款": "短期借款",
    "长期贷款": "长期借款",
    "长期应付款": "长期应付款合计",
    "非流动负债合计": "非流动负债合计",
    # Income
    "营业额": "*营业总收入",
    "股东应占溢利": "*归属于母公司所有者的净利润",
    "经营溢利": "三、营业利润",
    "营业成本": "其中：营业成本",
    "销售费用": "销售费用",
    "管理费用": "管理费用",
    "研发费用": "研发费用",
    "融资成本": "其中：利息费用",
    "税金及附加": "营业税金及附加",
    "其他收益": "其他收益",
    "减值及拨备": "资产减值损失",
    # Cashflow
    "加:折旧及摊销": "固定资产折旧、油气资产折耗、生产性生物资产折旧",
    "购建固定资产": "购建固定资产、无形资产和其他长期资产支付的现金",
    "取得子公司及其他营业单位支付的现金净额": "取得子公司及其他营业单位支付的现金净额",
}

class DataReader:
    def __init__(self, code):
        self.conn = sqlite3.connect(config.db_path(code))
        self.code = code
        stock = config.STOCKS.get(code, {})
        self.market = stock.get("market", "hk")

    def spot(self):
        r = self.conn.execute(
            "SELECT price, pe, pb, div_yield, mkt_cap, change_pct FROM spot"
        ).fetchone()
        if r: return dict(zip(["price","pe","pb","div_yield","mkt_cap","change_pct"], r))
        return {}

    def db_meta(self, key, default=None):
        r = self.conn.execute(
            "SELECT value FROM meta WHERE key=?", (key,)).fetchone()
        return r[0] if r else default

    def kline_monthly(self):
        rows = self.conn.execute(
            "SELECT date, open, high, low, close, volume FROM kline WHERE adjust='qfq' ORDER BY date"
        ).fetchall()
        monthly = {}
        for d, o, h, l, c, v in rows:
            key = d[:7]
            if key not in monthly:
                monthly[key] = {"open": o, "high": h, "low": l, "close": c, "volume": 0}
            else:
                monthly[key]["high"] = max(monthly[key]["high"], h)
                monthly[key]["low"] = min(monthly[key]["low"], l)
                monthly[key]["close"] = c
            monthly[key]["volume"] += (v or 0)
        return [{"date": k, **v} for k, v in sorted(monthly.items())]

    def indicators(self, report_date):
        rows = self._query_financial("indicators", report_date)
        d = dict(rows) if rows else {}
        if self.market == "cn":
            for ths_name, eng_name in THS_INDICATOR_MAP.items():
                if ths_name in d and eng_name not in d:
                    d[eng_name] = d[ths_name]
            # THS 不提供每股营收，自行计算
            shares = config.STOCKS.get(self.code, {}).get("shares")
            if "OPERATE_INCOME" in d and shares and "PER_OI" not in d:
                d["PER_OI"] = d["OPERATE_INCOME"] / shares
        elif self.market == "us":
            # 美股 API 不提供每股营收，自行计算
            shares = config.STOCKS.get(self.code, {}).get("shares")
            if "OPERATE_INCOME" in d and shares and "PER_OI" not in d:
                d["PER_OI"] = d["OPERATE_INCOME"] / shares
        return d

    def _query_financial(self, table, report_date, item_name=None, item_code=None):
        """查询财务数据，美股自动 fallback 到邻近日期"""
        # 先尝试精确日期
        if item_name:
            r = self.conn.execute(
                f"SELECT amount FROM {table} WHERE item_name=? AND report_date=?",
                (item_name, report_date)).fetchone()
        elif item_code:
            r = self.conn.execute(
                f"SELECT amount FROM {table} WHERE item_code=? AND report_date=?",
                (item_code, report_date)).fetchone()
        else:
            r = self.conn.execute(
                f"SELECT item_name, amount FROM {table} WHERE report_date=?",
                (report_date,)).fetchall()
        if r:
            return r
        # 美股 fallback: 查找年份内最近的 01-xx 日期
        if self.market == "us" and report_date and "-01-" in report_date:
            yr = report_date[:4]
            try:
                if item_name:
                    r = self.conn.execute(
                        f"SELECT amount FROM {table} WHERE item_name=? AND report_date LIKE ? ORDER BY report_date DESC LIMIT 1",
                        (item_name, f"{yr}-01-%")).fetchone()
                elif item_code:
                    r = self.conn.execute(
                        f"SELECT amount FROM {table} WHERE item_code=? AND report_date LIKE ? ORDER BY report_date DESC LIMIT 1",
                        (item_code, f"{yr}-01-%")).fetchone()
                else:
                    r = self.conn.execute(
                        f"SELECT item_name, amount FROM {table} WHERE report_date LIKE ?",
                        (f"{yr}-01-%",)).fetchall()
                if r:
                    return r
            except Exception:
                pass
        return None if item_name or item_code else []

    def financial_item(self, table, item, report_date):
        r = self._query_financial(table, report_date, item_name=item)
        if r is not None:
            return r[0] if isinstance(r, (list, tuple)) else r
        if self.market == "cn":
            # Fallback 1: 旧中文名 → 新THS列名
            ths_name = _THS_NAME_MAP.get(item)
            if ths_name:
                r2 = self.conn.execute(
                    f"SELECT amount FROM {table} WHERE item_name=? AND report_date=?",
                    (ths_name, report_date)
                ).fetchone()
                if r2: return r2[0]
            # Fallback 2: THS_FINANCIAL_MAP 英文名
            for ths_name_eng, cn_name_old in THS_FINANCIAL_MAP.items():
                if cn_name_old == item:
                    r2 = self.conn.execute(
                        f"SELECT amount FROM {table} WHERE item_name=? AND report_date=?",
                        (ths_name_eng, report_date)
                    ).fetchone()
                    if r2: return r2[0]
                    # Also try new THS name
                    new_name = _THS_NAME_MAP.get(cn_name_old)
                    if new_name:
                        r3 = self.conn.execute(
                            f"SELECT amount FROM {table} WHERE item_name=? AND report_date=?",
                            (new_name, report_date)
                        ).fetchone()
                        if r3: return r3[0]
                    break
        return None

    def financial_item_by_code(self, table, item_code, report_date):
        """通过 STD_ITEM_CODE 查询 (半年度数据), A股fallback到item_name"""
        r = self.conn.execute(
            f"SELECT amount FROM {table} WHERE item_code=? AND report_date=?",
            (item_code, report_date)
        ).fetchone()
        if r: return r[0]
        # A股 THS 没有 item_code, 用新THS中文列名回退
        if self.market == "cn":
            cn_map = {
                "004001001": "*营业总收入",
                "004025002": "*归属于母公司所有者的净利润",
                "004027002": "（一）基本每股收益",
                "004027003": "（二）稀释每股收益",
                "004012001": "减：所得税费用",
                "004011999": "四、利润总额",
            }
            ths_name = cn_map.get(item_code)
            if ths_name:
                return self.financial_item(table, ths_name, report_date)
        return None

    def dividends(self):
        rows = self.conn.execute(
            "SELECT report_year, cash_dps FROM dividend ORDER BY report_year"
        ).fetchall()
        return {r[0]: r[1] for r in rows}

    def share_count(self, report_date=None):
        """返回原始股数。
        - 无 report_date: 优先东方财富API → 缓存 → config 兜底 (用于市值等)
        - 有 report_date: 直接用 OPERATE_INCOME/PER_OI 计算当年股本
        """
        if report_date:
            oi = self.financial_item("indicators", "OPERATE_INCOME", report_date)
            psi = self.financial_item("indicators", "PER_OI", report_date)
            if oi and psi and psi > 0:
                return round(oi / psi)
        # 通用查询: 先查缓存
        cached = self.db_meta("total_shares")
        if cached:
            try:
                return int(cached)
            except (ValueError, TypeError):
                pass
        # 东方财富 API
        try:
            import requests
            stock_cfg = config.STOCKS.get(self.code, {})
            market = stock_cfg.get("market", "hk")
            secid_map = {"hk": "116", "cn": {"SSE": "1", "SZSE": "0"}.get(stock_cfg.get("exchange", ""), "0"), "us": "105"}
            secid = secid_map.get(market, "116")
            url = f"https://push2.eastmoney.com/api/qt/stock/get?secid={secid}.{self.code}&fields=f84"
            r = requests.get(url, headers={"User-Agent": "Mozilla/5.0", "Referer": "https://quote.eastmoney.com/"},
                          timeout=10, proxies={"http": None, "https": None})
            data = r.json()
            shares = data.get("data", {}).get("f84")
            if shares and shares > 0:
                self.conn.execute("INSERT OR REPLACE INTO meta VALUES (?,?)", ("total_shares", str(int(shares))))
                self.conn.commit()
                return int(shares)
        except Exception:
            pass
        stock = config.STOCKS.get(self.code, {})
        return stock.get("shares")

    def revenue_structure(self, year, dim_type):
        """从 revenue_structure 表读取营收拆分"""
        rows = self.conn.execute(
            "SELECT dim_name, amount, pct FROM revenue_structure "
            "WHERE code=? AND year=? AND dim_type=? ORDER BY amount DESC",
            (self.code, year, dim_type)
        ).fetchall()
        return [{"name": r[0], "value": r[1], "pct": r[2]} for r in rows]

    def close(self):
        self.conn.close()


def _compute_adj_np(reader, rd, np_val, tax_rate, stock_cfg):
    """默认 VL 口径扣非净利润计算。返回 (adj_np, footnotes_list)

    - A股: 直接读取 income 表 '*扣除非经常性损益后的净利润' (审计后 CAS 标准)
    - 港股: 排除'其他收益' (FVTPL变动/汇兑/并购等非经常); '其他收入' (主要为利息) 默认保留
    - 美股: US GAAP 净利润即运营利润, 直接使用 (无单独扣非项目)
    """
    market = stock_cfg.get("market", "hk")
    footnotes = []

    if np_val is None:
        return None, footnotes

    if market == "us":
        # 美股: US GAAP net income 直接使用, 无需调整
        return np_val, footnotes

    if market == "cn":
        # A股: 直接使用审计扣非净利润 (CAS 标准)
        deducted = reader.financial_item("income", "*扣除非经常性损益后的净利润", rd)
        if deducted is not None:
            val_b = deducted / 1e8
            diff_pct = abs(deducted - np_val) / abs(np_val) * 100 if np_val else 0
            if diff_pct > 0.5:  # 差异 >0.5% 才记录
                footnotes.append(
                    f"A股扣非净利润 {val_b:.1f}亿 (CAS审计标准), "
                    f"较归母净利润{np_val/1e8:.1f}亿调整{diff_pct:.1f}%"
                )
            return deducted, footnotes

    # 港股: 排除非经常项目 (FVTPL/汇兑/资产处置等), 保留经常性经营收益
    # 子项探测: 不同公司财报科目不同, 仅展示实际存在的项目
    _items = [
        ("公允价值变动收益", "FV"), ("汇兑收益", "FX"), ("政府补助", "GS"),
        ("资产处置收益", "IM"), ("其他收益", "OG"),
    ]
    nonrecur_items = []
    for item_name, abbr in _items:
        val = reader.financial_item("income", item_name, rd) or 0
        if abs(val) > 5e6:
            nonrecur_items.append((abbr, val))

    if nonrecur_items:
        # 逐个排除
        adj_np = np_val
        for _, val in nonrecur_items:
            adj_np -= val * (1 - tax_rate)
        # 格式: GovSub +0.3 FVTPL -1.2 → adj NP 105.5亿
        item_str = " ".join([f"{a} {v/1e8:+.1f}" for a, v in nonrecur_items])
        footnotes.append(f"EPS adj: {item_str} → VL经常性 {adj_np/1e8:.1f}亿 (归母{np_val/1e8:.1f}亿)")
    else:
        # 回退: 读取 其他收益 整项
        other_gain = reader.financial_item("income", "其他收益", rd) or 0
        if abs(other_gain) > 5e6:
            adj_np = np_val - other_gain * (1 - tax_rate)
            footnotes.append(f"EPS adj: OG {other_gain/1e8:+.1f} → VL {adj_np/1e8:.1f}亿 (归母{np_val/1e8:.1f}亿)")
        else:
            adj_np = np_val

    return adj_np, footnotes


def _resolve_adj_np(reader, rd, np_val, tax_rate, stock_cfg):
    """尝试加载 per-stock metric_adjustment.py 脚本, 失败则回退到默认计算。
    返回 (adj_np, footnotes_list)

    脚本接口 scripts/<code>/metric_adjustment.py:
        def adjust_metrics(reader, rd, np_val, tax_rate, stock_cfg) -> (adj_np, footnotes_list)
        
    可在此脚本中自定义 Value Line 24 项指标的任意计算逻辑 (EPS口径调整、减值阈值、折旧分摊等)。
    """
    code = reader.code
    try:
        script_path = os.path.join(os.path.dirname(__file__), "scripts", code, "metric_adjustment.py")
        if os.path.exists(script_path):
            import importlib.util, importlib.machinery as _im
            loader = _im.SourceFileLoader(f"ma_{code}", script_path)
            spec = importlib.util.spec_from_file_location(f"ma_{code}", script_path, loader=loader)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            if hasattr(mod, "adjust_metrics"):
                return mod.adjust_metrics(reader, rd, np_val, tax_rate, stock_cfg)
    except Exception:
        pass
    # 回退到默认计算
    return _compute_adj_np(reader, rd, np_val, tax_rate, stock_cfg)


def _resolve_dividends(reader):
    """加载 per-stock adjust_dividends 钩子，解析 DPS + FX 换算。
    优先级: scripts/<code>/metric_adjustment.py:adjust_dividends > DB 通用解析

    钩子接口:
        def adjust_dividends(reader, stock_cfg) -> dict
            reader: DataReader 实例 (可读 dividend 表 raw_text / cash_dps)
            stock_cfg: config.STOCKS[code]
            return: {year: dps_cny} 字典
    """
    code = reader.code
    try:
        script_path = os.path.join(os.path.dirname(__file__), "scripts", code, "metric_adjustment.py")
        if os.path.exists(script_path):
            import importlib.util, importlib.machinery as _im2
            loader = _im2.SourceFileLoader(f"md_{code}", script_path)
            spec = importlib.util.spec_from_file_location(f"md_{code}", script_path, loader=loader)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            if hasattr(mod, "adjust_dividends"):
                stock_cfg = config.STOCKS.get(code, {})
                return mod.adjust_dividends(reader, stock_cfg)
    except Exception:
        pass
    return reader.dividends()


def build_metric_table(reader, years, market="hk"):
    """构建24行指标表 — Value Line 标准公式 (A股/H股双轨)
    返回 (table, footnotes, data_source_note) 
    — footnotes 为每股收益调整说明列表, data_source_note 为数据源边界说明
    """
    table = {}
    all_footnotes = []
    total_shares = None
    has_akshare = False   # 是否有年份走了 AKShare indicators 路径
    has_fallback = False  # 是否有年份走了财报回退路径

    for yr in years:
        rd = _fye(yr)
        ind = reader.indicators(rd)

        # ---- Shares (优先 indicators 反推, 其次 carry-forward, 最后 config) ----
        shares = reader.share_count(rd) or total_shares
        if shares:
            total_shares = shares
        if not shares:
            stock_cfg = config.STOCKS.get(reader.code, {})
            shares = stock_cfg.get("shares")
            if shares:
                total_shares = shares

        if ind and ind.get("OPERATE_INCOME"):
            # ---- 标准路径: indicators 表有完整数据 ----
            has_akshare = True
            rev = ind.get("OPERATE_INCOME")
            np_val = ind.get("HOLDER_PROFIT")
            _tax = ind.get("TAX_EBT")
            # BPS: 优先从 balance 表计算 (保持与回退路径一致), indicators 兜底
            eq_raw = reader.financial_item("balance", "总权益", rd)
            _bps = round(eq_raw / shares, 2) if eq_raw and shares else ind.get("BPS")
            # A股 indicators 无 TAX_EBT, 回退到 income 表当面计算
            if _tax is None:
                tax_exp = (reader.financial_item_by_code("income", "004012001", rd)
                           or reader.financial_item("income", "所得税", rd))
                pretax = (reader.financial_item_by_code("income", "004011999", rd)
                          or reader.financial_item("income", "除税前盈利", rd))
                if tax_exp is not None and pretax and pretax > 0:
                    _tax = round((tax_exp / pretax) * 100, 1)
        else:
            # ---- 回退路径: 从 income/balance/cashflow 原始表当面计算 ----
            has_fallback = True
            # 优先 item_code 查询 (AKShare), 回退 item_name 查询 (TDX)
            rev = (reader.financial_item_by_code("income", "004001001", rd)
                   or reader.financial_item("income", "营业额", rd))
            np_val = (reader.financial_item_by_code("income", "004025002", rd)
                      or reader.financial_item("income", "股东应占溢利", rd))
            if not rev or not np_val or not shares:
                continue

            # 用 EPS 反推加权平均股数 (AKShare 用期末股数, TDX 用年报披露的加权 EPS)
            _eps_raw = reader.financial_item("income", "每股基本盈利", rd)
            if _eps_raw and _eps_raw > 0 and np_val:
                implied_shares = int(np_val / _eps_raw)
                if implied_shares > 0:
                    shares = implied_shares
                    total_shares = shares

            # 税率: 税项 / 除税前利润
            tax_exp = (reader.financial_item_by_code("income", "004012001", rd)
                       or reader.financial_item("income", "所得税", rd))
            pretax = (reader.financial_item_by_code("income", "004011999", rd)
                      or reader.financial_item("income", "除税前盈利", rd))
            if tax_exp is not None and pretax and pretax > 0:
                _tax = round((tax_exp / pretax) * 100, 1)
            else:
                _tax = None

            # BPS: 总权益 / 股数
            eq_raw = reader.financial_item("balance", "总权益", rd)
            _bps = round(eq_raw / shares, 2) if eq_raw and shares else None

        # ---- 基础数据提取 ----
        # (rev, np_val 已在上方路径中设置; shares 已设置)

        # 折旧摊销 (元) — AKShare 在 cashflow, TDX 在 income
        dep = (reader.financial_item("cashflow", "加:折旧及摊销", rd) or 0
               or abs(reader.financial_item("income", "折旧及摊销", rd) or 0))

        # 经营溢利 (元)
        op_profit = reader.financial_item("income", "经营溢利", rd)

        # ---- VL口径净利: 按市场+行业脚本分层计算 ----
        stock_cfg_full = config.STOCKS.get(reader.code, {})
        tax_rate = (_tax / 100) if _tax else 0.25
        adj_np, yr_footnotes = _resolve_adj_np(reader, rd, np_val, tax_rate, stock_cfg_full)
        if yr_footnotes:
            # 从脚注文本提取 adj, diff, src (供 generate_report.js 渲染)
            note_text = yr_footnotes[0] if yr_footnotes else ""
            adj_val, src_val, diff_val = "", "", ""
            m_adj = re.search(r'→ VL(?:经常性)?\s*([\d.]+)亿', note_text)
            m_rep = re.search(r'归母\s*([\d.]+)亿', note_text)
            if m_adj and m_rep:
                adj_f = float(m_adj.group(1))
                rep_f = float(m_rep.group(1))
                diff_f = rep_f - adj_f
                adj_val = f"{adj_f:.1f}亿"
                if abs(diff_f) >= 0.005:
                    s = f"{abs(diff_f):.2f}".rstrip('0').rstrip('.')
                    diff_val = f"({s})" if diff_f < 0 else s
                else:
                    diff_val = "\u2014"
            m2 = re.search(r'EPS adj:\s*(.+?)\s*→', note_text)
            if m2:
                src_val = m2.group(1)
            elif "A股扣非" in note_text and "较归母" in note_text:
                src_val = "CAS\u5ba1\u8ba1\u6807\u51c6"
                m_d = re.search(r'\u6263\u975e\u51c0\u5229\u6da6\s*([\d.]+)\u4ebf', note_text)
                if m_d and m_rep:
                    adj_f = float(m_d.group(1))
                    rep_f = float(m_rep.group(1))
                    diff_f = rep_f - adj_f
                    adj_val = f"{adj_f:.1f}亿"
                    diff_val = f"({abs(diff_f):.1f})" if abs(diff_f) >= 0.05 else "\u2014"
            all_footnotes.append({"year": yr, "notes": yr_footnotes, "adj": adj_val, "diff": diff_val, "src": src_val})

        # ---- 1. 每股营收: Revenue / Shares ----
        row = {}
        row["PER_OI"] = round(rev / shares, 2) if rev and shares else None

        # ---- 2. 每股现金流: (AdjNetProfit + Depreciation) / Shares ----
        row["PER_NETCASH"] = round((adj_np + dep) / shares, 2) if adj_np and shares else None

        # ---- 3. 每股收益: VL = 扣非稀释EPS = adj_np / shares ----
        _eps = round(adj_np / shares, 2) if adj_np and shares else None
        row["BASIC_EPS"] = round(_eps, 2) if _eps is not None else None


        # ---- 4. 每股股息: per-stock脚本 > 通用DB解析 ----
        divs = _resolve_dividends(reader)
        row["DPS"] = divs.get(yr, 0) or 0

        # ---- 5. 每股资本支出: (购建固定资产 + 收购子公司) / Shares ----
        capex_fixed = reader.financial_item("cashflow", "购建固定资产", rd) or 0
        capex_mna = reader.financial_item("cashflow", "取得子公司及其他营业单位支付的现金净额", rd) or 0
        row["CAPEX_PS"] = round((capex_fixed + capex_mna) / shares, 2) if shares else None

        # ---- 6. 每股账面价值: VL = Common Equity / Share (含无形资产) ----
        # 标准公式: 归属母公司权益 / 股数, 与年报披露值可能有 2-5% 口径差异
        row["BPS"] = round(_bps, 2) if _bps else None
        row["BPS_FORMULA"] = "equity/shares"

        # ---- 7. 发行在外股数 (百万股) ----
        row["TOTAL_SHARES"] = round(shares / 1e6, 1) if shares else None  # 百万股

        # ---- 8-10. PE/股息率 (后续补算) ----
        row["PE_AVG"] = None
        row["PE_RELATIVE"] = None
        row["DIV_YIELD"] = None

        # ---- 11. 总营收 (亿) ----
        row["OPERATE_INCOME"] = round(rev / 1e8, 1) if rev else None

        # ---- 12. 营业利润率 = OperatingProfit / Revenue (VL 口径) ----
        row["OP_MARGIN"] = round((op_profit / rev) * 100, 1) if rev and op_profit else None

        # ---- 13. 折旧摊销 (亿) ----
        row["DEPRECIATION"] = round(dep / 1e8, 1) if dep else None

        # ---- 14. 毛利率 = 毛利 ÷ 营收 (优先直接取毛利, 回退REV-COGS) ----
        gp = reader.financial_item("income", "毛利", rd)
        if gp and rev:
            row["GROSS_MARGIN"] = round((gp / rev) * 100, 1)
        else:
            cogs = reader.financial_item("income", "销售成本", rd) or reader.financial_item("income", "营业成本", rd)
            row["GROSS_MARGIN"] = round(((rev - cogs) / rev) * 100, 1) if rev and cogs else None

        # ---- 15. 净利润 (亿) ----
        row["HOLDER_PROFIT"] = round(adj_np / 1e8, 1) if adj_np else None

        # ---- 16. 所得税率 ----
        row["TAX_EBT"] = round(_tax, 1) if _tax is not None else None

        # ---- 17. 净利润率 = AdjNetProfit / Revenue ----
        row["NET_PROFIT_RATIO"] = round((adj_np / rev) * 100, 1) if adj_np and rev else None

        # ---- 18. 营运资金 = CA - CL (亿) ----
        ca = reader.financial_item("balance", "流动资产合计", rd)
        cl = reader.financial_item("balance", "流动负债合计", rd)
        row["WORKING_CAPITAL"] = round((ca - cl) / 1e8, 1) if ca is not None and cl is not None else None

        # ---- 19. 长期债务 = 长期贷款 + 应付债券 + 融资租赁(非流动) + 长期应付款 (亿) ----
        # VL: 所有有息长期债务 (含融资租赁, 不含一年内到期部分)
        long_loan = reader.financial_item("balance", "长期贷款", rd) or 0
        bonds = reader.financial_item("balance", "应付债券", rd) or 0
        lease_lt = reader.financial_item("balance", "融资租赁负债(非流动)", rd) or 0
        lt_payable = reader.financial_item("balance", "长期应付款", rd) or 0
        lt_raw = long_loan + bonds + lease_lt + lt_payable
        row["LT_DEBT"] = round(lt_raw / 1e8, 1) if lt_raw > 0 else None

        # ---- 20. 股东权益 = 总权益 (亿, 含少数股东) ----
        eq = reader.financial_item("balance", "总权益", rd)
        row["TOTAL_EQUITY"] = round(eq / 1e8, 1) if eq else None
        # 归母权益(Common Equity): VL用于RETAINED_RATIO分母
        _com_eq = (reader.financial_item("balance", "股东权益", rd)
                   or reader.financial_item("balance", "归属于母公司所有者权益", rd))
        com_eq = _com_eq or eq

        # ---- 21. ROIC = EBIT / (LT_Debt + Equity) ----
        fin_cost = reader.financial_item("income", "融资成本", rd) or 0
        ebit = (op_profit or 0) + fin_cost
        invested_cap = lt_raw + (eq or 0)
        row["ROIC"] = round((ebit / invested_cap) * 100, 1) if ebit and invested_cap > 0 else None

        # ---- 22. ROE = AdjNI / Total Equity (VL: for common + preferred stockholders) ----
        row["ROE"] = round((adj_np / eq) * 100, 1) if adj_np and eq else None

        # ---- 23. 留存利润再投比 = (AdjNetProfit - Dividends) / Common Equity ----
        # VL: "net income less all dividends... divided by common shareholders' equity"
        if adj_np and com_eq and shares and com_eq > 0:
            div_total = (row["DPS"] or 0) * shares
            retained = adj_np - div_total
            row["RETAINED_RATIO"] = round((retained / com_eq) * 100, 1)
        else:
            row["RETAINED_RATIO"] = None

        # ---- 24. 股利支付率 = Total Dividends / AdjNet Profit ----
        if adj_np and shares and adj_np > 0:
            div_total = (row["DPS"] or 0) * shares
            row["PAYOUT_RATIO"] = round((div_total / adj_np) * 100, 1)
        else:
            row["PAYOUT_RATIO"] = None

        table[yr] = row

    # 补算 PE_AVG / PE_RELATIVE / DIV_YIELD
    _compute_pe_metrics(table, reader, market)

    # 数据源边界说明: 仅港股同时用到 AKShare indicators + TDX 回退时才生成
    data_note = None
    if has_akshare and has_fallback and market == "hk":
        first_ind_yr = min(int(y) for y in years 
            if (ind := reader.indicators(_fye(str(y)))) 
            and ind.get("OPERATE_INCOME"))
        data_note = (
            f"指标数据: {first_ind_yr}年起基于东方财富(EM), "
            f"{first_ind_yr-1}年及以前基于通达信(TDX)财报计算; "
            f"BPS公式: 归属母公司权益÷股数, "
            f"与年报披露加权值可能有小幅差异"
        )
    return table, all_footnotes, data_note


def _compute_ttm_eps(reader, latest_yr):
    """TTM EPS: 最近12个月滚动 (Trailing P/E 口径)
    - 年度财报已发布时: 优先用下一年部分数据 (Q1 或 H1) 做真正滚动 TTM
      - 季度股: TTM = (FY - Q1) + Q1_next = Q2+Q3+Q4 + Q1_next
      - 半年报股: TTM = (FY - H1) + H1_next = H2 + H1_next
    - 无下一年数据时回退到完整年报 EPS
    - 年报未出时拼半年: H1_cur + H2_prev"""
    stock = config.STOCKS.get(config.ACTIVE_STOCK, {})
    fye = stock.get("fiscal_yr_end", "12-31")
    qd_cur = _q_dates(str(latest_yr), fye)   # [q1, h1, 9m, fy]
    qd_prev = _q_dates(str(int(latest_yr) - 1), fye)
    qd_next = _q_dates(str(int(latest_yr) + 1), fye)
    fy_cur = reader.financial_item_by_code("income", "004027003", qd_cur[3])
    h1_cur = reader.financial_item_by_code("income", "004027003", qd_cur[1])
    q1_cur = reader.financial_item_by_code("income", "004027003", qd_cur[0])
    h1_prev = reader.financial_item_by_code("income", "004027003", qd_prev[1])
    fy_prev = reader.financial_item_by_code("income", "004027003", qd_prev[3])
    # 查下一年部分数据 (探测是否有 Q1 或 H1)
    q1_next = reader.financial_item_by_code("income", "004027003", qd_next[0])
    h1_next = reader.financial_item_by_code("income", "004027003", qd_next[1])
    # 方案A: 最新年报已发布 → 尝试用下一年数据做真正的 TTM 滚动
    if fy_cur is not None and fy_cur > 0:
        if q1_next is not None and q1_cur is not None:
            # 季度股: TTM = Q2+Q3+Q4 + Q1_next = (FY - Q1) + Q1_next
            h2_plus = fy_cur - q1_cur
            if h2_plus > 0:
                return h2_plus + q1_next
        if h1_next is not None and h1_cur is not None:
            # 半年报股: TTM = H2 + H1_next = (FY - H1) + H1_next
            h2_cur = fy_cur - h1_cur
            if h2_cur > 0:
                return h2_cur + h1_next
        # 下一年无数据 → 回退到全年 EPS
        return fy_cur
    # 方案B: 仅半年报(年报未出) → TTM = H1_cur + H2_prev
    if h1_cur is not None and fy_prev is not None and h1_prev is not None:
        h2_prev = fy_prev - h1_prev
        if h2_prev > 0:
            return h1_cur + h2_prev
    # 方案C: 去年年报
    if fy_prev is not None and fy_prev > 0:
        return fy_prev
    return None


def _median_pe_iqr(pe_values, years=10):
    """VL Median P/E: 取过去N年PE, IQR过滤异常值后取中位数"""
    if not pe_values:
        return None
    # VL取最多10年
    vals = pe_values[-years:] if len(pe_values) > years else pe_values[:]
    if len(vals) < 2:
        return vals[0]
    sorted_vals = sorted(vals)
    # IQR异常值过滤
    n = len(sorted_vals)
    q1_idx = n // 4
    q3_idx = (3 * n) // 4
    q1 = sorted_vals[q1_idx]
    q3 = sorted_vals[q3_idx]
    iqr = q3 - q1
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr
    filtered = [v for v in sorted_vals if lower <= v <= upper]
    if not filtered:
        filtered = sorted_vals  # 全部被排除则回退
    mid = len(filtered) // 2
    return round(filtered[mid], 1) if len(filtered) % 2 == 1 else round((filtered[mid-1] + filtered[mid]) / 2, 1)


def _compute_pe_metrics(table, reader, market="hk"):
    """利用日K线聚合为月线，计算各年度月均价PE和相对PE (Value Line: Avg Ann'l P/E)"""
    from collections import defaultdict
    # 获取日线 → 日线按 YYYY-MM 分组 → 月均价 = 每月所有交易日收盘价的均值
    kline_rows = reader.conn.execute(
        "SELECT date, close FROM kline WHERE adjust='qfq' ORDER BY date"
    ).fetchall()
    if not kline_rows:
        return

    monthly_closes = defaultdict(list)
    for d, c in kline_rows:
        monthly_closes[d[:7]].append(c)
    monthly_avg = {m: sum(v) / len(v) for m, v in monthly_closes.items()}

    # 月均价按年聚合: 年均价 = 12个月均价的均值
    yearly_closes = defaultdict(list)
    for m, c in monthly_avg.items():
        yearly_closes[m[:4]].append(c)

    # 计算每年均价和PE (汇率调整: 仅当交易币种 ≠ 财报币种时需要换算)
    price_ccy = config.MARKET_CONFIG.get(market, {}).get("currency", "CNY")
    stock_cfg = config.STOCKS.get(reader.code, {})
    rpt_ccy = stock_cfg.get("currency", "CNY")
    need_fx = (price_ccy != rpt_ccy)  # e.g. HKD交易+CNY财报 → 需要; USD交易+USD财报 → 不需要
    for yr, row in table.items():
        closes = yearly_closes.get(yr, [])
        if not closes or not row.get("BASIC_EPS"):
            continue
        avg_price = sum(closes) / len(closes)  # 交易货币(HKD)
        row["AVG_PRICE"] = round(avg_price, 2)
        # 汇率换算: avg_price(HKD) → CNY
        if need_fx:
            fx_yr = _get_fx_rate(f"{yr}-12-31")
            if fx_yr is None or fx_yr <= 0:
                continue  # 无汇率, 无法计算 PE/DIV_YIELD — 跳过该年
        else:
            fx_yr = 1.0
        avg_price_cny = avg_price * fx_yr   # HKD × fx(HKD→CNY) = CNY
        eps = row["BASIC_EPS"]
        if eps and eps > 0:
            row["PE_AVG"] = round(avg_price_cny / eps, 1)
        # 平均股息率 = DPS(CNY) / 年均价(CNY)
        dps = row.get("DPS")
        if dps is not None and avg_price_cny > 0:
            row["DIV_YIELD"] = round((dps / avg_price_cny) * 100, 1) if dps > 0 else 0.0

    # 相对PE: PE_AVG / 市场PE (从 config.MARKET_CONFIG 获取)
    market_cfg = config.MARKET_CONFIG.get(market, {})
    index_pe = market_cfg.get("pe_estimate", {})
    for yr, row in table.items():
        pe_avg = row.get("PE_AVG")
        mkt_pe = index_pe.get(yr)
        if pe_avg and mkt_pe and mkt_pe > 0:
            row["PE_RELATIVE"] = round(pe_avg / mkt_pe, 2)

    # 写回 PE_AVG / DIV_YIELD 到 indicators 表 (供 list_refs / build 确认页读取)
    for yr, row in table.items():
        rd = f"{yr}-12-31"
        for item in ("PE_AVG", "DIV_YIELD"):
            val = row.get(item)
            if val is not None:
                try:
                    reader.conn.execute(
                        "INSERT OR REPLACE INTO indicators VALUES (?,?,?)",
                        (rd, item, float(val)))
                except Exception:
                    pass
    reader.conn.commit()


def _detect_freq(reader, yr):
    """检测该年度可用报告频率: 'quarterly' | 'semi_annual' | 'annual'"""
    # 检查是否有03-31和09-30的季报数据
    stock = config.STOCKS.get(config.ACTIVE_STOCK, {})
    fye = stock.get("fiscal_yr_end", "12-31")
    # 9-30 和 03-31 两个季报点都存在则判断为有季报
    q1 = None
    for patch in ("-03-31", "-09-30"):
        d = f"{yr}{patch}"
        v = reader.financial_item_by_code("income", "004001001", d) or reader.financial_item("income", "营业额", d)
        if v is not None:
            q1 = patch
        else:
            break
    return "quarterly" if q1 else None

def _single_q(cumulative, prev):
    """从累计值计算单季值"""
    return (cumulative - prev) if cumulative is not None and prev is not None else None

def _q_dates(yr, fye):
    """返回该财年4个季度/半年报告日期列表 (从远到近)"""
    y = int(yr)
    if fye == "03-31":
        # 3月底财年: Q1=06-30(上年), H1=09-30(上年), 9M=12-31(上年), FY=03-31(本年)
        return [f"{y-1}-06-30", f"{y-1}-09-30", f"{y-1}-12-31", f"{y}-03-31"]
    else:
        # 标准财年: Q1=03-31, H1=06-30, 9M=09-30, FY=12-31
        return [f"{y}-03-31", f"{y}-06-30", f"{y}-09-30", f"{y}-12-31"]

def _us_fy_quarter(report_date, fye_month):
    """从 report_date (YYYY-MM-DD) 和财年末月推导 (财年, 季度)"""
    parts = report_date.split("-")
    yr, mo = int(parts[0]), int(parts[1])
    # 财年标签: 月度 > 财年末月 → 下一财年
    fy = yr + 1 if mo > fye_month else yr
    # 季度偏移 (财年末月+1 为 Q1 起始月)
    offset = (mo - fye_month - 1) % 12 + 1
    if offset <= 3:
        q = "Q1"
    elif offset <= 6:
        q = "Q2"
    elif offset <= 9:
        q = "Q3"
    else:
        q = "Q4"
    return str(fy), q

def build_us_quarterly(reader, years, metrics):
    """美股: 从 income 表单季报数据构建 QUARTERLY 区域。
    Q1-Q3: 单季金额 (indicator='单季报'), Q4: 年报全值 - Q1 - Q2 - Q3。
    """
    from collections import defaultdict
    qtr = {"sales": [], "eps": [], "dividends": []}
    stock = config.STOCKS.get(config.ACTIVE_STOCK, {})
    fye = stock.get("fiscal_yr_end", "12-31")
    fye_month = int(fye.split("-")[0])

    # 年报日期模式 (用于区分年报/季报)
    yr_end_pats = ["-12-31"] + [f"-01-{d:02d}" for d in range(22, 32)]
    yr_end_like = " OR ".join([f"report_date LIKE '%{p}'" for p in yr_end_pats])
    qtr_like = " AND ".join([f"report_date NOT LIKE '%{p}'" for p in yr_end_pats])

    # 查询 Q1-Q3 单季营收
    rev_q = reader.conn.execute(
        f"SELECT report_date, amount FROM income WHERE item_code='004001001' AND ({qtr_like}) ORDER BY report_date"
    ).fetchall()
    # 查询年报全值营收
    rev_annual = reader.conn.execute(
        f"SELECT report_date, amount FROM income WHERE item_code='004001001' AND ({yr_end_like}) ORDER BY report_date"
    ).fetchall()

    # EPS: Q1-Q3 单季 EPS + 年报全值 EPS
    eps_q = reader.conn.execute(
        f"SELECT report_date, amount FROM income WHERE item_code IN ('004017003','004027003','004027002') AND ({qtr_like}) ORDER BY report_date"
    ).fetchall()
    eps_annual = reader.conn.execute(
        f"SELECT report_date, amount FROM income WHERE item_code IN ('004017003','004027003','004027002') AND ({yr_end_like}) ORDER BY report_date"
    ).fetchall()

    rev_map = {d: a for d, a in rev_q}
    rev_annual_map = {d: a for d, a in rev_annual}
    eps_map = {}
    for d, a in eps_q:
        if d not in eps_map or a is not None:
            eps_map[d] = a
    eps_annual_map = {}
    for d, a in eps_annual:
        if d not in eps_annual_map or a is not None:
            eps_annual_map[d] = a

    # 按财年分组 Q1-Q3 (从单季报日期)
    fy_quarters = defaultdict(dict)
    for d in rev_map:
        fy, q = _us_fy_quarter(d, fye_month)
        fy_quarters[fy][q] = d

    # 年报日期也按财年分组
    fy_annual = {}
    for d, amt in rev_annual_map.items():
        fy, _ = _us_fy_quarter(d, fye_month)
        fy_annual[fy] = (d, amt / 1e8)

    all_fys = sorted(set(list(fy_quarters.keys()) + list(fy_annual.keys())))

    for fy in all_fys:
        qs = fy_quarters.get(fy, {})
        # Q1-Q3 单季营收
        q_rev = {}
        for ql in ["Q1", "Q2", "Q3"]:
            d = qs.get(ql)
            if d and d in rev_map:
                q_rev[ql] = rev_map[d] / 1e8

        # Q4 = 年报全值 - Q1 - Q2 - Q3
        ann_info = fy_annual.get(fy)
        if ann_info:
            ann_date, ann_amt = ann_info
            q1_q3_sum = sum(v for v in q_rev.values() if v is not None)
            q4_val = max(0, ann_amt - q1_q3_sum) if q1_q3_sum > 0 else None
        else:
            q4_val = None
            ann_amt = None

        # EPS
        q_eps = {}
        for ql in ["Q1", "Q2", "Q3"]:
            d = qs.get(ql)
            if d and d in eps_map:
                q_eps[ql] = eps_map[d]
        eps_ann = eps_annual_map.get(ann_info[0]) if ann_info else None
        if eps_ann and q_eps:
            q1_q3_eps = sum(v for v in q_eps.values() if v is not None)
            q4_eps = max(0, round(eps_ann - q1_q3_eps, 2)) if q1_q3_eps > 0 else None
        else:
            q4_eps = None

        if q_rev:
            qtr["sales"].append({
                "year": fy, "has_quarter": True,
                "q1": round(q_rev["Q1"], 1) if q_rev.get("Q1") is not None else None,
                "q2": round(q_rev["Q2"], 1) if q_rev.get("Q2") is not None else None,
                "q3": round(q_rev["Q3"], 1) if q_rev.get("Q3") is not None else None,
                "q4": round(q4_val, 1) if q4_val is not None else None,
                "full": round(ann_amt, 1) if ann_amt is not None else None
            })
        if q_eps:
            qtr["eps"].append({
                "year": fy, "has_quarter": True,
                "q1": round(q_eps["Q1"], 2) if q_eps.get("Q1") is not None else None,
                "q2": round(q_eps["Q2"], 2) if q_eps.get("Q2") is not None else None,
                "q3": round(q_eps["Q3"], 2) if q_eps.get("Q3") is not None else None,
                "q4": q4_eps,
                "full": round(eps_ann, 2) if eps_ann else None
            })

    # 股息
    for yr in years:
        if reader:
            row = reader.conn.execute(
                "SELECT cash_dps, total_amount FROM dividend WHERE report_year=?",
                (yr,)
            ).fetchone()
        else:
            row = None
        dps_val = (row[0] or 0) if row else 0
        ann = metrics.get(yr, {})
        full = ann.get("DPS", 0) or 0
        qtr["dividends"].append({
            "year": yr, "has_quarter": False,
            "q1": 0, "q3": round(full, 3), "full": round(full, 3)
        })
    return qtr

def build_semi_annual(reader, years, metrics):
    """从 income 表构建季度或半年度数据。美股走单季报路径 (build_us_quarterly)。"""
    qtr = {"sales": [], "eps": [], "dividends": []}
    stock = config.STOCKS.get(config.ACTIVE_STOCK, {})
    fye = stock.get("fiscal_yr_end", "12-31")
    market = stock.get("market", "")

    # 美股: 使用单季报数据直接构建季度数据
    if market == "us":
        return build_us_quarterly(reader, years, metrics)
    
    for yr in years:
        qd = _q_dates(yr, fye)  # [q1, h1, 9m, fy]
        # 季度数据查询: 优先 code (AKShare), 回退 name (TDX)
        c1 = reader.financial_item_by_code("income", "004001001", qd[0]) or reader.financial_item("income", "营业额", qd[0])
        c2 = reader.financial_item_by_code("income", "004001001", qd[1]) or reader.financial_item("income", "营业额", qd[1])
        c3 = reader.financial_item_by_code("income", "004001001", qd[2]) or reader.financial_item("income", "营业额", qd[2])
        ca = reader.financial_item_by_code("income", "004001001", qd[3]) or reader.financial_item("income", "营业额", qd[3])
        n1 = reader.financial_item_by_code("income", "004025002", qd[0]) or reader.financial_item("income", "股东应占溢利", qd[0])
        n2 = reader.financial_item_by_code("income", "004025002", qd[1]) or reader.financial_item("income", "股东应占溢利", qd[1])
        n3 = reader.financial_item_by_code("income", "004025002", qd[2]) or reader.financial_item("income", "股东应占溢利", qd[2])
        na = reader.financial_item_by_code("income", "004025002", qd[3]) or reader.financial_item("income", "股东应占溢利", qd[3])
        e1 = (reader.financial_item_by_code("income", "004027003", qd[0]) or reader.financial_item_by_code("income", "004027002", qd[0])
              or reader.financial_item("income", "每股基本盈利", qd[0]))
        e2 = (reader.financial_item_by_code("income", "004027003", qd[1]) or reader.financial_item_by_code("income", "004027002", qd[1])
              or reader.financial_item("income", "每股基本盈利", qd[1]))
        e3 = (reader.financial_item_by_code("income", "004027003", qd[2]) or reader.financial_item_by_code("income", "004027002", qd[2])
              or reader.financial_item("income", "每股基本盈利", qd[2]))
        ea = (reader.financial_item_by_code("income", "004027003", qd[3]) or reader.financial_item_by_code("income", "004027002", qd[3])
              or reader.financial_item("income", "每股基本盈利", qd[3]))
        
        # 判断是否有季报：c1 和 c2 都存在
        is_q = c1 is not None and c2 is not None
        
        if is_q:
            # 单季营收
            sq2 = _single_q(c2, c1)
            sq3 = _single_q(c3, c2)
            sq4 = _single_q(ca, c3)
            # 单季净利
            sn2 = _single_q(n2, n1)
            sn3 = _single_q(n3, n2)
            sn4 = _single_q(na, n3)
            # 单季EPS
            se2 = _single_q(e2, e1)
            se3 = _single_q(e3, e2)
            se4 = _single_q(ea, e3)
            
            ann_rev = (ca / 1e8) if ca else 0
            ann_np  = (na / 1e8) if na else 0
            
            q1_rev = (c1 / 1e8) if c1 else None
            q2_rev = (sq2 / 1e8) if sq2 is not None else None
            q3_rev = (sq3 / 1e8) if sq3 is not None else None
            q4_rev = (sq4 / 1e8) if sq4 is not None else None
            
            q1_eps = e1 if e1 is not None else None
            q2_eps = se2 if se2 is not None else None
            q3_eps = se3 if se3 is not None else None
            q4_eps = se4 if se4 is not None else None
            
            if q1_rev is not None:
                qtr["sales"].append({
                    "year": yr, "has_quarter": True,
                    "q1": round(q1_rev, 1), "q2": round(q2_rev, 1) if q2_rev is not None else None,
                    "q3": round(q3_rev, 1) if q3_rev is not None else None, "q4": round(q4_rev, 1) if q4_rev is not None else None,
                    "full": round(ann_rev, 1)
                })
            if q1_eps is not None:
                qtr["eps"].append({
                    "year": yr, "has_quarter": True,
                    "q1": round(q1_eps, 2), "q2": round(q2_eps, 2) if q2_eps is not None else None,
                    "q3": round(q3_eps, 2) if q3_eps is not None else None, "q4": round(q4_eps, 2) if q4_eps is not None else None,
                    "full": round(ea, 2) if ea else 0
                })
        else:
            # 半年度 (H1/H2) — 取中间点 qd[1] (06-30) 作为 H1
            h1_d = qd[1]
            h1_rev = reader.financial_item_by_code("income", "004001001", h1_d) or reader.financial_item("income", "营业额", h1_d)
            h1_np  = reader.financial_item_by_code("income", "004025002", h1_d) or reader.financial_item("income", "股东应占溢利", h1_d)
            h1_eps = (reader.financial_item_by_code("income", "004027003", h1_d)
                      or reader.financial_item_by_code("income", "004027002", h1_d)
                      or reader.financial_item("income", "每股基本盈利", h1_d))
            
            if h1_rev is None or h1_np is None:
                # 无 H1 数据, 尝试 Q1 前瞻 (2026仅有Q1等场景)
                q1_rev = reader.financial_item_by_code("income", "004001001", qd[0]) \
                         or reader.financial_item("income", "营业额", qd[0])
                q1_np  = reader.financial_item_by_code("income", "004025002", qd[0]) \
                         or reader.financial_item("income", "股东应占溢利", qd[0])
                q1_eps = (reader.financial_item_by_code("income", "004027003", qd[0])
                          or reader.financial_item_by_code("income", "004027002", qd[0])
                          or reader.financial_item("income", "每股基本盈利", qd[0]))
                if q1_rev is not None and q1_np is not None:
                    qtr["sales"].append({
                        "year": yr, "has_quarter": True, "forward": True,
                        "q1": round(q1_rev / 1e8, 1), "q2": None, "q3": None, "q4": None,
                        "full": None
                    })
                    if q1_eps:
                        qtr["eps"].append({
                            "year": yr, "has_quarter": True, "forward": True,
                            "q1": round(q1_eps, 2), "q2": None, "q3": None, "q4": None,
                            "full": None
                        })
                continue
                
            ann = metrics.get(yr, {})
            ann_rev_metric = ann.get("OPERATE_INCOME")
            ann_np_metric  = ann.get("HOLDER_PROFIT")
            ann_eps_metric = ann.get("BASIC_EPS")
            
            h1_rev_b = h1_rev / 1e8
            h1_np_b  = h1_np / 1e8
            h2_rev_b = max(0, ann_rev_metric - h1_rev_b) if ann_rev_metric else 0
            h2_np_b  = max(0, ann_np_metric - h1_np_b) if ann_np_metric else 0
            
            qtr["sales"].append({
                "year": yr, "has_quarter": False,
                "q1": round(h1_rev_b, 1), "q3": round(h2_rev_b, 1),
                "full": round(ann_rev_metric, 1) if ann_rev_metric else None
            })
            if h1_eps and ann_eps_metric:
                h1_eps_v = h1_eps
                h2_eps_v = max(0, ann_eps_metric - h1_eps)
                qtr["eps"].append({
                    "year": yr, "has_quarter": False,
                    "q1": round(h1_eps_v, 2), "q3": round(h2_eps_v, 2), "full": round(ann_eps_metric, 2)
                })
    
    # 追加部分年数据 (最新财年之后, 探测是否有 Q1 或 H1 数据)
    if years:
        next_yr = str(int(years[-1]) + 1)
        qd_next = _q_dates(next_yr, fye)
        c1_next = reader.financial_item_by_code("income", "004001001", qd_next[0]) \
                  or reader.financial_item("income", "营业额", qd_next[0])  # Q1
        c2_next = reader.financial_item_by_code("income", "004001001", qd_next[1]) \
                  or reader.financial_item("income", "营业额", qd_next[1])  # H1
        e1_next = (reader.financial_item_by_code("income", "004027003", qd_next[0])
                   or reader.financial_item_by_code("income", "004027002", qd_next[0])
                   or reader.financial_item("income", "每股基本盈利", qd_next[0]))
        e2_next = (reader.financial_item_by_code("income", "004027003", qd_next[1])
                   or reader.financial_item_by_code("income", "004027002", qd_next[1])
                   or reader.financial_item("income", "每股基本盈利", qd_next[1]))

        if c1_next is not None:
            # 季度股: 有 Q1 累计数据 → 展示单季 Q1
            qtr["sales"].append({
                "year": next_yr, "has_quarter": True,
                "q1": round(c1_next / 1e8, 1), "q2": None, "q3": None, "q4": None, "full": None
            })
            if e1_next is not None:
                qtr["eps"].append({
                    "year": next_yr, "has_quarter": True,
                    "q1": round(e1_next, 2), "q2": None, "q3": None, "q4": None, "full": None
                })
        elif c2_next is not None:
            # 半年报股: 仅有 H1 数据 → H1 放在 Q1 列位
            qtr["sales"].append({
                "year": next_yr, "has_quarter": False,
                "q1": round(c2_next / 1e8, 1), "q3": None, "full": None
            })
            if e2_next is not None:
                qtr["eps"].append({
                    "year": next_yr, "has_quarter": False,
                    "q1": round(e2_next, 2), "q3": None, "full": None
                })

    # 股息数据 (年度)
    for yr in years:
        if reader:
            row = reader.conn.execute(
                "SELECT cash_dps, total_amount FROM dividend WHERE report_year=?",
                (yr,)
            ).fetchone()
        else:
            row = None
        dps_val = (row[0] or 0) if row else 0
        ann = metrics.get(yr, {})
        full = ann.get("DPS", 0) or 0
        qtr["dividends"].append({
            "year": yr, "has_quarter": False,
            "q1": 0, "q3": round(full, 3), "full": round(full, 3)
        })
    
    return qtr

def calc_cagr(values, n_years):
    if len(values) < 2: return None
    first, last = values[0], values[-1]
    if first and first > 0 and last and last > 0:
        return (pow(last / first, 1.0 / n_years) - 1) * 100
    return None


def calc_cagr_multi(metric_values, years):
    vals = [v for v in metric_values if v is not None and v > 0]
    result = {}
    for label, n in [("1yr", 1), ("3yr", 3), ("5yr", 5), ("10yr", 10)]:
        if len(vals) > n:
            result[label] = round(calc_cagr(vals[-n-1:], n), 1)
        else:
            result[label] = None
    return result


def fetch_market_index(market="hk"):
    """获取市场指数月线 (从 config.MARKET_CONFIG 读取市场配置)"""
    mcfg = config.MARKET_CONFIG.get(market, {})
    func_name = mcfg.get("index_akshare_func", "")
    symbol = mcfg.get("index_symbol", "")
    if not func_name or not symbol:
        return []
    try:
        import subprocess, json
        managed_py = r"C:\Users\fly\.workbuddy\binaries\python\versions\3.13.12\python.exe"
        # 不同市场的指数获取函数不同
        if func_name == "stock_hk_index_daily_sina":
            script = f"""
import akshare as ak, json, sys
df = ak.stock_hk_index_daily_sina(symbol="{symbol}")
if df is not None and len(df) > 0:
    df['date'] = df['date'].astype(str)
    result = []
    monthly = {{}}
    for _, row in df.iterrows():
        key = row['date'][:7]
        if key not in monthly:
            monthly[key] = {{"open": row['open'], "high": row['high'],
                            "low": row['low'], "close": row['close']}}
        else:
            monthly[key]["high"] = max(monthly[key]["high"], row['high'])
            monthly[key]["low"] = min(monthly[key]["low"], row['low'])
            monthly[key]["close"] = row['close']
    result = [{{"date": k, **v}} for k, v in sorted(monthly.items())]
    print(json.dumps(result))
else:
    print('[]')
"""
        elif func_name == "stock_zh_index_daily":
            script = f"""
import akshare as ak, json, sys
df = ak.stock_zh_index_daily(symbol="sh{symbol}")
if df is not None and len(df) > 0:
    df['date'] = df['date'].astype(str)
    result = []
    monthly = {{}}
    for _, row in df.iterrows():
        key = row['date'][:7]
        if key not in monthly:
            monthly[key] = {{"open": row['open'], "high": row['high'],
                            "low": row['low'], "close": row['close']}}
        else:
            monthly[key]["high"] = max(monthly[key]["high"], row['high'])
            monthly[key]["low"] = min(monthly[key]["low"], row['low'])
            monthly[key]["close"] = row['close']
    result = [{{"date": k, **v}} for k, v in sorted(monthly.items())]
    print(json.dumps(result))
else:
    print('[]')
"""
        elif func_name == "stock_us_index_daily_sina":
            script = f"""
import akshare as ak, json, sys
df = ak.index_us_stock_sina(symbol="{symbol}")
if df is not None and len(df) > 0:
    df['date'] = df['date'].astype(str)
    result = []
    monthly = {{}}
    for _, row in df.iterrows():
        key = row['date'][:7]
        if key not in monthly:
            monthly[key] = {{"open": row['open'], "high": row['high'],
                            "low": row['low'], "close": row['close']}}
        else:
            monthly[key]["high"] = max(monthly[key]["high"], row['high'])
            monthly[key]["low"] = min(monthly[key]["low"], row['low'])
            monthly[key]["close"] = row['close']
    result = [{{"date": k, **v}} for k, v in sorted(monthly.items())]
    print(json.dumps(result))
else:
    print('[]')
"""
        else:
            return []
        r = subprocess.run([managed_py, "-c", script], capture_output=True, text=True, timeout=60)
        if r.returncode == 0 and r.stdout.strip():
            return json.loads(r.stdout.strip())
        return []
    except Exception as e:
        print(f"  Index fetch warning ({market}/{symbol}): {e}")
        return []


# ============================================================
# 主函数
# ============================================================
def _detect_unit(raw_values):
    """根据原始数值量级自动选择单位和除数
    返回: (unit_str, divisor)
    """
    max_val = max([abs(v) for v in raw_values if v is not None and v > 0] or [0])
    if max_val >= 1e13:
        return "万亿", 1e12
    elif max_val >= 1e8:
        return "亿", 1e8
    elif max_val >= 1e4:
        return "万", 1e4
    else:
        return "", 1


def _build_capital_structure(reader, spot, latest_yr, metrics, fx_rate=None, need_fx=False):
    """CAPITAL STRUCTURE — 资本结构明细 (参照 Timberland Co. Value Line 标准)
    覆盖: Total Debt, Due in 5 Yrs, LT Debt, Total Int, Coverage,
          % of Capital, Pension Assets, Pfd Stock, Common Stock, Market Cap
    单位自动检测, 不硬编码
    """
    rd = _fye(latest_yr)
    result = {}

    # 1. 先获取所有原始值 (不分除)
    raw = {}
    for item, key in [
        ("总资产", "total_assets"), ("总负债", "total_debt"),
        ("总权益", "total_equity"), ("流动资产合计", "current_assets"),
        ("流动负债合计", "current_liabilities"),
        ("现金及等价物", "cash"), ("存货", "inventory"),
        ("应收帐款", "receivables"), ("非流动负债合计", "non_current_liab"),
    ]:
        v = reader.financial_item("balance", item, rd)
        raw[key] = v or 0
    # 兜底: item_code 查找 — 阿里巴巴等港股 item_name 不同
    for item_code, item_name, key in [
        ("004002005", "预付款按金及其他应收款", "receivables"),
        ("005032022", "存货", "inventory"),
        ("005032003", "应收帐款", "receivables"),
    ]:
        if raw.get(key, 0) == 0:
            v = reader.financial_item_by_code("balance", item_code, rd)
            raw[key] = v or 0

    lt = reader.financial_item("balance", "融资租赁负债(非流动)", rd)
    if not lt:
        lt = reader.financial_item("balance", "长期贷款", rd)
    raw["lt_debt"] = lt or 0

    debt_due_current = reader.financial_item("balance", "融资租赁负债(流动)", rd) or 0
    st_loan = reader.financial_item("balance", "短期贷款", rd) or 0
    lt_payable = reader.financial_item("balance", "长期应付款", rd) or 0
    non_cur_due_1yr = reader.financial_item("balance", "一年内到期的非流动负债", rd) or 0
    # VL "Due in 5 Yrs": 所有5年内到期债务 (近似: 短期+1年内到期非流动+长期应付款)
    raw["due_in_5yr"] = debt_due_current + st_loan + lt_payable + non_cur_due_1yr

    total_int = reader.financial_item("income", "融资成本", rd)
    raw["total_int"] = total_int or 0

    # 2. 自动检测单位
    numeric_vals = [v for k, v in raw.items() if isinstance(v, (int, float))]
    unit, divisor = _detect_unit(numeric_vals)
    result["unit"] = unit
    result["divisor"] = divisor

    # 3. 按检测到的单位分除
    for key, val in raw.items():
        result[key] = val / divisor if val else 0

    # 4. 派生指标 (不需要除以 divisor)
    # Coverage
    op_profit = reader.financial_item("income", "经营溢利", rd)
    if total_int and total_int > 0 and op_profit:
        coverage = op_profit / total_int
        if coverage > 25:
            result["coverage"] = ">25x"
            result["coverage_num"] = coverage
        else:
            result["coverage"] = f"{coverage:.1f}x"
            result["coverage_num"] = coverage
    else:
        # VL: NMF = No Meaningful Figure (利息为0或极低时,覆盖倍数无意义)
        result["coverage"] = "NMF"
        result["coverage_num"] = None

    # LT Debt % of total capital
    total_cap = result.get("total_equity", 0) + result.get("lt_debt", 0)
    result["lt_debt_pct"] = round(result["lt_debt"] / total_cap * 100, 1) if total_cap > 0 else 0

    result["pension_assets"] = "N/A"
    result["pfd_stock"] = "None"

    # Common Stock shares
    stock_cfg = config.STOCKS.get(reader.code, {})
    raw_shares = reader.share_count(rd) or stock_cfg.get("shares")
    if raw_shares:
        result["common_shares"] = round(raw_shares / 1e6, 0)
        # 格式化: 带千分号，如 1,342,943,150
        result["common_shares_str"] = f"{raw_shares:,}"
        result["common_shares_raw"] = raw_shares
    else:
        result["common_shares"] = 0
        result["common_shares_str"] = "N/A"
        result["common_shares_raw"] = 0

    # Market Cap (价格(交易货币) × 股数 → 换算为报表货币 CNY)
    price = spot.get("price", 0) if spot else 0
    if need_fx and (fx_rate is None or fx_rate <= 0):
        # 无汇率 — 拒绝计算市值 (无法将 HKD 价格转为 CNY)
        result["mkt_cap"] = "-"
        result["cap_label"] = "-"
    else:
        # 汇率换算: price(HKD) → CNY. 1 HKD = fx CNY, 所以 price_cny = price * fx
        fx_mc = fx_rate if fx_rate and fx_rate > 0 else 1.0
        price_cny = price * fx_mc
        mkt_cap_raw = price_cny * result["common_shares_raw"] if result["common_shares_raw"] else 0
        result["mkt_cap"] = round(mkt_cap_raw / divisor, 1) if divisor else 0
        # Market cap label
        mkt_cap_b = result["mkt_cap"]  # 亿
        if mkt_cap_b > 10000:
            result["cap_label"] = "Mega Cap"
        elif mkt_cap_b > 1000:
            result["cap_label"] = "Large Cap"
        elif mkt_cap_b > 100:
            result["cap_label"] = "Mid Cap"
        else:
            result["cap_label"] = "Small Cap"

    # Business description + 员工人数 (从SQLite meta表读取, PDF提取一次存库)
    result["business_desc"] = reader.db_meta("business_desc", "")
    emp_raw = reader.db_meta("employee_count")
    result["employee_count"] = int(emp_raw) if emp_raw else None
    result["employee_year"] = reader.db_meta("employee_year", "")

    # MD&A分析文本 (从PDF提取一次存库)
    result["mda_text"] = reader.db_meta("mda_text", "")
    result["mda_quality"] = reader.db_meta("mda_quality", "0")  # "1"=高质量, "0"=低质量/兜底生成

    return result


def _parse_mda_text(mda_text):
    """从 extract_mda.py 产出的分段文本提取结构化字段。
    输入格式: 【经营总览】\n...\n【产品/业务结构】\n... 等
    返回: {business_summary, mda_sections, outlook} 或 None (不足时)
    """
    if not mda_text or len(mda_text) < 300:
        return None

    # 按 【章节标题】 分段
    section_names = {
        "overview": "经营总览",
        "product": "产品/业务结构",
        "channel": "渠道发展",
        "region": "分地区表现",
        "cost": "成本与效率",
        "outlook": "未来展望",
    }

    sections = {}
    current_key = None
    current_lines = []

    for line in mda_text.split("\n"):
        line = line.strip()
        if not line:
            continue
        matched = False
        for key, name in section_names.items():
            if f"【{name}】" in line:
                if current_key and current_lines:
                    sections[current_key] = current_lines
                current_key = key
                current_lines = []
                matched = True
                break
        if not matched and current_key:
            current_lines.append(line)
    if current_key and current_lines:
        sections[current_key] = current_lines

    if not sections:
        return None

    # business_summary: 经营总览 前2句
    overview = sections.get("overview", [])
    bs_lines = overview[:2] if overview else sections.get(list(sections.keys())[0], [])[:2]
    business_summary = "；".join(bs_lines) if bs_lines else ""

    # mda_sections: 产品+渠道+地区+成本
    mda_sections = {}
    for key in ["product", "channel", "region", "cost"]:
        lines = sections.get(key, [])
        if lines:
            mda_sections[key] = lines

    outlook_lines = sections.get("outlook", [])

    return {
        "business_summary": business_summary,
        "mda_sections": mda_sections,
        "outlook": outlook_lines,
    }


def _load_per_stock_script(code):
    """尝试加载 scripts/<code>/business_commentary.py, 返回 module 或 None"""
    try:
        script_path = os.path.join(os.path.dirname(__file__), "scripts", code, "business_commentary.py")
        if not os.path.exists(script_path):
            return None
        import importlib.util, importlib.machinery as _im3
        loader = _im3.SourceFileLoader(f"bc_{code}", script_path)
        spec = importlib.util.spec_from_file_location(f"bc_{code}", script_path, loader=loader)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod if hasattr(mod, "build") else None
    except Exception:
        return None


def _build_business_from_data(stock, metrics, rev_struct, years):
    """VL 风格 BUSINESS 描述 — 先讲清生意是什么，再附关键经营数据。"""
    name = stock.get("name", "该公司")

    if not years:
        return f"{name}业务数据暂缺"

    latest_yr = years[-1]
    ly = metrics.get(latest_yr, {})

    # 1. 有 business_desc → 以它为叙事主线，补充最新数据
    desc = stock.get("business_desc", "")
    if desc:
        parts = []
        rev = ly.get("OPERATE_INCOME")
        roe = ly.get("ROE")
        lt_debt = ly.get("LT_DEBT", 0) or 0
        if rev:
            parts.append(f"{latest_yr}年营收{rev:.1f}亿元")
        if roe:
            parts.append(f"ROE {roe:.1f}%")
        if lt_debt == 0:
            parts.append("零长期负债")
        suffix = "；".join(parts) if parts else ""
        return f"{desc} {suffix}。" if suffix else desc

    # 2. 无 business_desc → 从营收结构数据推断业务全貌
    seg = (rev_struct.get("by_segment", []) or rev_struct.get("by_product", [])
           or rev_struct.get("by_ip", []))
    rg = rev_struct.get("by_region", [])
    industry = stock.get("industry", "")
    rev = ly.get("OPERATE_INCOME")
    roe = ly.get("ROE")
    npm = ly.get("NET_PROFIT_RATIO")
    lt_debt = ly.get("LT_DEBT", 0) or 0

    lines = [name]
    if industry:
        ind_label = {
            "Consumer": "消费品", "Consumer Staples": "必需消费品",
            "Technology": "科技", "Energy": "能源",
            "Metals & Mining": "金属与矿业", "Automotive": "汽车",
            "Media": "传媒", "Home Appliances": "家电",
            "Pharmaceuticals": "医药", "Building Materials": "建材",
            "Financial Services": "金融服务", "Insurance": "保险",
            "Utilities": "公用事业", "Packaging": "包装",
            "Healthcare": "医疗健康",
        }.get(industry, industry)
        lines.append(f"属于{ind_label}行业")

    if seg:
        seg_names = [f"{s['name']}（{s['pct']}%）" for s in seg[:3]]
        lines.append("，主营" + "、".join(seg_names))

    # 地域分布
    if rg and len(rg) >= 2:
        domestic = [r for r in rg if any(
            kw in str(r.get('name', '')).lower()
            for kw in ['中国', 'china', '内地', '香港']
        )]
        overseas = [r for r in rg if r not in domestic]
        if domestic and overseas:
            dom_pct = sum(r['pct'] for r in domestic)
            ovs_pct = sum(r['pct'] for r in overseas)
            lines.append(f"。国内市场占比{dom_pct:.0f}%")
            if ovs_pct > 5:
                top_ovs = sorted(overseas, key=lambda x: x['pct'], reverse=True)[:2]
                ovs_names = "、".join([r['name'] for r in top_ovs])
                lines.append(f"，海外市场{ovs_pct:.0f}%（{ovs_names}）")

    # 经营数据
    data_parts = []
    if rev:
        data_parts.append(f"{latest_yr}年营收{rev:.1f}亿元")
    if npm:
        data_parts.append(f"净利润率{npm:.1f}%")
    if roe:
        data_parts.append(f"ROE {roe:.1f}%")
    if lt_debt == 0:
        data_parts.append("零长期负债")

    lines.append("。" + "；".join(data_parts) + "。")
    return "".join(lines)


def _build_commentary_from_data(stock, metrics, rev_struct, years, cagr, spot):
    """VL 风格 4 段 AI Commentary: 业绩快照 + 每股资金流向 + 业务质地 + 转折点检测"""
    name = stock.get("name", "该公司")
    name_short = name.replace("中国", "").replace("集团", "").replace("控股", "").replace("股份", "").replace("有限", "").replace("公司", "")
    if not years:
        return ["数据不足", "", "", ""]

    latest_yr = years[-1]
    ly = metrics.get(latest_yr, {})
    prev_yr = years[-2] if len(years) >= 2 else None
    py = metrics.get(prev_yr, {}) if prev_yr else {}
    today = __import__("datetime").date.today().strftime("%Y年%m月%d日")

    # ── 辅助 ──
    def _chg(cur, prev):  return (cur / prev - 1) * 100 if cur and prev and prev > 0 else None
    def _dir_pct(cur, prev, label=""):
        c = _chg(cur, prev)
        return f"{label}增长{abs(c):.1f}%" if c and c > 0 else f"{label}下降{abs(c):.1f}%" if c and c < 0 else ""

    rev, rev_p = ly.get("OPERATE_INCOME"), py.get("OPERATE_INCOME") if py else None
    np_v, np_p = ly.get("HOLDER_PROFIT"), py.get("HOLDER_PROFIT") if py else None
    eps = ly.get("BASIC_EPS")
    per_oi = ly.get("PER_OI")
    per_cf = ly.get("PER_NETCASH")
    per_capex = ly.get("CAPEX_PS") or 0
    dps = ly.get("DPS", 0) or 0
    op_margin = ly.get("OP_MARGIN")
    gm, gm_p = ly.get("GROSS_MARGIN"), py.get("GROSS_MARGIN") if py else None
    roe, roe_p = ly.get("ROE"), py.get("ROE") if py else None
    npm = ly.get("NET_PROFIT_RATIO")
    pe = spot.get("pe", 0)
    pb = spot.get("pb", 0)
    div_y = spot.get("div_yield", 0)

    # PE 中位数
    pe_vals = [v for yr_k in years for v in [metrics.get(yr_k, {}).get("PE_AVG")] if v]
    med_pe = sorted(pe_vals)[len(pe_vals) // 2] if pe_vals else None

    # ── 每股资金流向 (VL 四大去向) ──
    tax_rate_val = (ly.get("TAX_EBT", 25) or 25) / 100
    op_eps = round(per_oi * (op_margin / 100) * (1 - tax_rate_val), 2) if per_oi and op_margin else None
    nonop_eps = round(eps - op_eps, 2) if eps is not None and op_eps is not None else None
    net_ps = round(per_cf - per_capex - dps, 2) if per_cf is not None else None
    op_pct = round(op_eps / eps * 100) if eps and op_eps and eps != 0 else None
    nonop_pct = round(nonop_eps / eps * 100) if eps and nonop_eps and eps != 0 else None
    payout = ly.get("PAYOUT_RATIO")
    wc_cur = ly.get("WORKING_CAPITAL")
    wc_prev = py.get("WORKING_CAPITAL") if py else None
    shares_cur = ly.get("TOTAL_SHARES")
    shares_prev = py.get("TOTAL_SHARES") if py else None

    # ── 段1: 业绩快照 ──
    p1 = f"{today} — {name_short}{latest_yr}年营收{rev:.1f}亿元({_dir_pct(rev,rev_p)})" if rev else ""
    if np_v is not None:
        p1 += f"，扣非净利润{np_v:.1f}亿元({_dir_pct(np_v,np_p)})"
    if eps:
        p1 += f"，每股收益¥{eps:.2f}"
    # 解释变化原因
    rev_c = _chg(rev, rev_p)
    np_c = _chg(np_v, np_p)
    if np_c is not None and rev_c is not None and (abs(np_c - rev_c) > 10):
        if np_c < rev_c:
            p1 += f"。利润增速落后营收主因毛利率从{gm_p:.1f}%降至{gm:.1f}%，费用端承压" if gm_p and gm and gm < gm_p else ""
        else:
            p1 += f"。利润超营收增长反映经营杠杆改善，净利润率{npm:.1f}%" if npm else ""
    elif gm is not None:
        p1 += f"，毛利率{gm:.1f}%({_dir_pct(gm,gm_p) if gm_p else ''})"
    if roe is not None:
        p1 += f"，ROE {roe:.1f}%"
    p1 += "。"

    # ── 段2: 每股资金流向 (VL 四大去向) ──
    if eps and op_eps is not None and nonop_eps is not None:
        p2 = (f"每股收益¥{eps:.2f}中，主业贡献¥{op_eps:.2f}（{op_pct}%），"
              f"非经营性贡献¥{nonop_eps:.2f}（{nonop_pct}%）。")
        if per_cf is not None and net_ps is not None:
            p2_parts = [
                f"每股现金流¥{per_cf:.2f}（内生现金生成 = 净利润 + 折旧），四大去向：",
                f"① 资本支出¥{per_capex:.2f}/股（扩建/更换厂房设备）；",
            ]
            if wc_cur is not None and wc_prev is not None:
                wc_chg = round(wc_cur - wc_prev, 1)
                wc_chg_ps = f"折合¥{abs(wc_chg * 100 / shares_cur):.2f}/股，" if shares_cur and shares_cur > 0 else ""
                if wc_chg > 0:
                    p2_parts.append(f"② 营运资金占用 +{wc_chg:.1f}亿（{wc_chg_ps}扩张期正常，需关注效率）；")
                elif wc_chg < 0:
                    p2_parts.append(f"② 营运资金释放 {wc_chg:.1f}亿（{wc_chg_ps}快收慢付，竞争优势 ✅）；")
                else:
                    p2_parts.append(f"② 营运资金基本持平；")
            pay_str = f"（支付率{payout:.0f}%）" if payout else ""
            p2_parts.append(f"③ 现金分红¥{dps:.2f}/股{pay_str}；")
            if shares_cur and shares_prev and shares_prev > 0:
                shr_chg = round((shares_cur - shares_prev) / shares_prev * 100, 1)
                if shr_chg < -0.3:
                    p2_parts.append(f"④ 股份回购（股数{shr_chg:+.1f}%）— 增厚每股价值 ✅；")
                elif shr_chg > 1:
                    p2_parts.append(f"④ 股本扩张（股数{shr_chg:+.1f}%）— 摊薄每股指标 ⚠️；")
                else:
                    p2_parts.append(f"④ 股数基本持平；")
            if net_ps > 0:
                p2_parts.append(f"净留存¥{net_ps:.2f}/股，现金流充裕。")
            else:
                p2_parts.append(f"入不敷出¥{net_ps:.2f}/股，消耗存量现金储备。")
            p2 += "".join(p2_parts)
    else:
        p2 = f"每股资金流向：财报数据不足以进行完整拆分。"

    # ── 段3: 业务质地 + 估值 ──
    p3_parts = []
    # 业务结构
    seg = rev_struct.get("by_segment", []) or rev_struct.get("by_product", [])
    if seg and len(seg) >= 2:
        top2 = seg[:2]
        def _short(s):
            t = s.split('/')[0].split('及')[0].split('-')[0].split('（')[0].strip()
            return t[:6] if len(t) > 6 else t
        names = [_short(s['name']) for s in top2]
        p3_parts.append(f"以{'和'.join(names)}为主(合计{sum(s['pct'] for s in top2):.0f}%营收)")

    # 财务质地
    lt_debt = ly.get("LT_DEBT", 0) or 0
    if lt_debt == 0:
        p3_parts.append("公司零长期负债")
    else:
        eq = ly.get("TOTAL_EQUITY", 0)
        if eq > 0:
            p3_parts.append(f"负债率{lt_debt/eq*100:.0f}%")

    # 估值
    if pe and med_pe:
        vs = "低于" if pe < med_pe else "高于"
        p3_parts.append(f"当前PE {pe:.1f}倍({vs}历史中位数{med_pe:.1f}倍)")
    if pb is not None:
        p3_parts.append(f"PB {pb:.2f}倍")
    if div_y and div_y > 0:
        p3_parts.append(f"股息率{div_y:.1f}%")
    if roe is not None:
        roe_str = f"ROE {roe:.1f}%"
        if roe_p:
            trend = "提升" if roe > roe_p else "下滑"
            roe_str += f"(同比{trend})"
        p3_parts.append(roe_str)

    p3 = "，".join([p for p in p3_parts if p]) + "。"

    # ── 段4: 转折点检测 + 验证信号 ──
    p4_parts = []
    triggers = []

    # 营收反转: 1yr>0 AND 5yr<-10
    rev_1yr = cagr.get("revenue", {}).get("1yr")
    rev_5yr = cagr.get("revenue", {}).get("5yr")
    if rev_1yr is not None and rev_1yr > 0 and rev_5yr is not None and rev_5yr < -10:
        triggers.append("营收增速反转：多年下行后重获正增长，关注持续性")

    # 利润率反转: 毛利率1yr>0 AND 3yr趋势<0
    if gm and gm_p and gm > gm_p:
        gm_3y = [metrics.get(str(y), {}).get("GROSS_MARGIN") for y in years[-3:]]
        gm_3y = [v for v in gm_3y if v is not None]
        if len(gm_3y) >= 2 and gm_3y[-1] > gm_3y[0]:
            triggers.append("毛利率止跌回升，盈利质量边际改善")

    # 现金流方向反转
    if net_ps is not None:
        py_cf = py.get("PER_NETCASH")
        py_capex = py.get("CAPEX_PS") or 0
        py_dps = py.get("DPS", 0) or 0
        if py_cf is not None:
            py_net = round(py_cf - py_capex - py_dps, 2)
            if net_ps > 0 > py_net:
                triggers.append("每股净留存由负转正，现金流状况改善")
            elif net_ps < 0 < py_net:
                triggers.append("每股净留存由正转负，现金流承压")

    # ROE 反转: 1yr>0 AND 3yr均值<0
    roe_vals = [metrics.get(str(y), {}).get("ROE") for y in years]
    roe_vals = [v for v in roe_vals if v is not None]
    if len(roe_vals) >= 3:
        avg_before = sum(roe_vals[-4:-1]) / 3 if len(roe_vals) >= 4 else sum(roe_vals[:-1]) / (len(roe_vals)-1)
        if roe_vals[-1] > avg_before * 1.1:
            triggers.append("ROE触底反弹：盈利能力较近年均值大幅改善")

    # 营收趋势
    rev_3yr = cagr.get("revenue", {}).get("3yr")
    if rev_1yr is not None and rev_3yr is not None:
        if rev_1yr > rev_3yr:
            p4_parts.append(f"营收增速加速（1年{rev_1yr:+.1f}% vs 3年{rev_3yr:+.1f}%）")
        elif rev_1yr < rev_3yr and rev_1yr > 0:
            p4_parts.append(f"营收增速放缓（1年{rev_1yr:+.1f}% vs 3年{rev_3yr:+.1f}%）")

    for t in triggers:
        p4_parts.append(t)

    # 验证信号
    eps_1yr = cagr.get("eps", {}).get("1yr")
    watch = []
    if net_ps is not None and net_ps < 0:
        watch.append(f"关注{int(latest_yr)+1}年中报净留存是否回升至正值")
    elif pe and med_pe and pe < med_pe * 0.6:
        watch.append("估值处于历史低位但需业绩拐点确认")
    elif pe and med_pe and pe > med_pe * 1.5 and pe > 15:
        watch.append("估值高于历史中枢需盈利增长验证")
    else:
        watch.append(f"关注{int(latest_yr)+1}年中报营收增速作为趋势验证信号")
    p4_parts.append("验证信号：" + "；".join(watch))

    p4 = "。".join([p for p in p4_parts if p]) + "。"

    return [p1, p2, p3, p4]


def _build_current_position(reader, years):
    """CURRENT POSITION — 短期资产负债 (最近3年对比)"""
    result = {"years": [], "items": []}
    # 取最近3年
    recent_years = years[-3:] if len(years) >= 3 else years
    result["years"] = recent_years

    items_def = [
        ("cash", "现金及等价物", "Cash Assets"),
        ("receivables", "应收帐款", "Receivables"),
        ("inventory", "存货", "Inventory (FIFO)"),
        ("other_ca", None, "Other Current Assets"),
        ("total_ca", "流动资产合计", "Current Assets"),
        ("payables", "应付帐款", "Accounts Payable"),
        ("debt_due", None, "Debt Due"),
        ("other_cl", None, "Other Current Liab"),
        ("total_cl", "流动负债合计", "Current Liabilities"),
    ]
    for _, name_cn, name_en in items_def:
        row = {"name": name_en}
        for yr in recent_years:
            rd = _fye(yr)
            v = reader.financial_item("balance", name_cn, rd) if name_cn else None
            row[yr] = v / 1e8 if v else 0
        result["items"].append(row)

    # Cash Assets = 现金及等价物 + 短期存款 + 短期投资
    for yr in recent_years:
        rd = _fye(yr)
        sd = reader.financial_item("balance", "短期存款", rd) or 0
        st_invest = reader.financial_item("balance", "短期投资", rd) or 0
        result["items"][0][yr] = round(result["items"][0][yr] + (sd + st_invest) / 1e8, 2)

    # Third pass: Debt Due = 短期借款 + 一年内到期非流动负债 + 融资租赁(流动)
    for yr in recent_years:
        rd = _fye(yr)
        st_borrow = reader.financial_item("balance", "短期贷款", rd) or 0
        non_cur_1yr = reader.financial_item("balance", "一年内到期的非流动负债", rd) or 0
        lease_cur = reader.financial_item("balance", "融资租赁负债(流动)", rd) or 0
        result["items"][6][yr] = round((st_borrow + non_cur_1yr + lease_cur) / 1e8, 2)

    # Second pass: compute derived rows
    for yr in recent_years:
        ca_total = result["items"][4][yr]  # Current Assets
        # Other CA = CA - Cash - Receivables - Inventory
        other_ca = ca_total - result["items"][0][yr] - result["items"][1][yr] - result["items"][2][yr]
        result["items"][3][yr] = max(0, round(other_ca, 2))

        cl_total = result["items"][8][yr]  # Current Liabilities
        # Other CL = CL - Payables - DebtDue
        other_cl = cl_total - result["items"][5][yr] - result["items"][6][yr]
        result["items"][7][yr] = max(0, round(other_cl, 2))

    return result


def _build_annual_rates(metrics, years):
    """ANNUAL RATES of Change — CAGR 1yr/3yr/5yr/10yr + Book Value
    列规则: 有10年数据→显示10/5/3yr; 不足10年→显示5/3/1yr
    """
    def get_series(field):
        return [metrics[y].get(field) for y in years if y in metrics and metrics[y].get(field)]

    def cagr_n(values, n):
        if len(values) <= n or not values[-n-1] or values[-n-1] <= 0:
            return None
        if not values[-1] or values[-1] <= 0:
            return None
        return round((pow(values[-1] / values[-n-1], 1.0 / n) - 1) * 100, 1)

    def calc_all(series):
        return {
            "1yr": cagr_n(series, 1),
            "3yr": cagr_n(series, 3) if len(series) > 3 else None,
            "5yr": cagr_n(series, 5) if len(series) > 5 else None,
            "10yr": cagr_n(series, 10) if len(series) > 10 else None,
        }

    rev = get_series("OPERATE_INCOME")
    eps = get_series("BASIC_EPS")
    cfs = get_series("PER_NETCASH")
    dps = get_series("DPS")
    bps = get_series("BPS")

    # 判断是否有10年数据 (用营收判断)
    has_10yr = len(rev) > 10

    return {
        "sales": calc_all(rev),
        "cashflow": calc_all(cfs),
        "earnings": calc_all(eps),
        "dividends": calc_all(dps),
        "book_value": calc_all(bps),
        "has_10yr": has_10yr,
    }


def _calc_position(spot, kline, metrics, years):
    """计算当前估值在历史区间的位置 (统一 CNY)"""
    result = {}
    price = spot.get("price", 0) if spot else 0  # HKD
    pe_ttm = spot.get("pe", 0) if spot else 0    # PE = 价格/收益，币种无关
    pb = spot.get("pb", 0) if spot else 0

    # PE区间: PE 是价格/收益比值，与货币无关 (分子分母同币种抵消)
    pe_vals = [metrics[y]["PE_AVG"] for y in years if y in metrics and metrics[y].get("PE_AVG")]
    if pe_vals:
        result["pe"] = {
            "current": round(pe_ttm, 1),
            "min": round(min(pe_vals), 1),
            "max": round(max(pe_vals), 1),
            "avg": round(sum(pe_vals) / len(pe_vals), 1),
        }
        rng = result["pe"]["max"] - result["pe"]["min"]
        result["pe"]["pct"] = round((pe_ttm - result["pe"]["min"]) / rng * 100, 0) if rng > 0 else 50

    # 价格区间 (从月K线)
    if kline and price:
        all_closes = [k["close"] for k in kline]
        result["price"] = {
            "current": round(price, 1),
            "min": round(min(all_closes), 1),
            "max": round(max(all_closes), 1),
            "avg": round(sum(all_closes) / len(all_closes), 1),
        }
        rng = result["price"]["max"] - result["price"]["min"]
        result["price"]["pct"] = round((price - result["price"]["min"]) / rng * 100, 0) if rng > 0 else 50

    # PB区间 (从市盈率×EPS÷BPS反推)
    pb_vals = []
    for yr in years:
        row = metrics.get(yr, {})
        pe_avg = row.get("PE_AVG")
        eps = row.get("BASIC_EPS")
        bps = row.get("BPS")
        if pe_avg and eps and bps and bps > 0:
            pb_vals.append(pe_avg * eps / bps)
    if pb_vals and pb:
        result["pb"] = {
            "current": pb,
            "min": round(min(pb_vals), 1),
            "max": round(max(pb_vals), 1),
            "avg": round(sum(pb_vals) / len(pb_vals), 1),
        }
        rng = result["pb"]["max"] - result["pb"]["min"]
        result["pb"]["pct"] = round((pb - result["pb"]["min"]) / rng * 100, 0) if rng > 0 else 50

    return result


def _detect_rpt_ccy(reader, stock):
    """自动识别财报货币: 优先DB meta, 其次IS_CNY_CODE, 最后config"""
    # 1. config 优先 (手工维护的货币信息最可靠)
    cfg_ccy = stock.get("currency")
    if cfg_ccy:
        return cfg_ccy
    # 2. DB meta 备选
    db_ccy = reader.db_meta("currency")
    if db_ccy:
        return db_ccy
    # 3. IS_CNY_CODE (AKShare 港股接口对所有股票都标 HKD, 不太可靠)
    try:
        cny_rows = reader.conn.execute(
            "SELECT DISTINCT amount FROM indicators WHERE item_name='IS_CNY_CODE'"
        ).fetchall()
        if cny_rows:
            is_cny = any(r[0] == 1.0 for r in cny_rows)
            return "CNY" if is_cny else stock.get("currency", "CNY")
    except:
        pass
    # 3. config fallback
    return stock.get("currency", "CNY")


def _get_fx_rate(date_str):
    """获取 HKD/CNY 汇率 (100 HKD = ? CNY)，失败返回 None"""
    import sqlite3, os
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "fx_rates.db")
    if not os.path.exists(db_path):
        return None
    try:
        conn = sqlite3.connect(db_path)
        # 先精确匹配日期，否则取最近一天
        row = conn.execute("SELECT hkd_cny FROM daily_rates WHERE date=?", (date_str,)).fetchone()
        if not row:
            row = conn.execute("SELECT hkd_cny FROM daily_rates WHERE date<=? ORDER BY date DESC LIMIT 1", (date_str,)).fetchone()
        conn.close()
        if row:
            return row[0] / 100.0  # 100 HKD = X CNY → 1 HKD = X/100 CNY
    except Exception:
        pass
    return None


def _build_yearly_hl(kline, years):
    """从月K线计算每年最高/最低价 — Yearly High/Low 表格"""
    from collections import defaultdict
    yhl = defaultdict(lambda: {"high": 0, "low": float("inf"), "month_high": "", "month_low": ""})
    for k in kline:
        yr = k["date"][:4]
        if yr not in years:
            continue
        entry = yhl[yr]
        if k["high"] > entry["high"]:
            entry["high"] = k["high"]
            entry["month_high"] = k["date"][:7]
        if k["low"] < entry["low"]:
            entry["low"] = k["low"]
            entry["month_low"] = k["date"][:7]
    result = []
    for yr in sorted(yhl.keys()):
        e = yhl[yr]
        if e["low"] < float("inf"):
            result.append({
                "year": yr,
                "high": round(e["high"], 1),
                "low": round(e["low"], 1),
                "month_high": e["month_high"],
                "month_low": e["month_low"],
            })
    return result


def build_report(code=None):
    code = code or config.ACTIVE_STOCK
    stock = config.STOCKS[code]
    market = stock.get("market", "hk")
    reader = DataReader(code)

    spot = reader.spot()
    kline = reader.kline_monthly()

    # 年份策略: income表全量年份, TDX 数据可追溯至 2001 (不再截断)
    fye = stock.get("fiscal_yr_end", "12-31")
    all_rows = reader.conn.execute(
        "SELECT DISTINCT substr(report_date,1,4) FROM income "
        "WHERE substr(report_date,5,3)=? ORDER BY 1", (f"-{fye[:2]}",)
    ).fetchall()
    full_years = [r[0] for r in all_rows]
    # 最近N年
    num_yr = min(15, len(full_years)) if len(full_years) > 10 else len(full_years)
    years = full_years[-num_yr:]

    metrics, footnotes_data, data_source_note = build_metric_table(reader, years, market)

    # 补算 Header PE(TTM) / PB / 股息率 / 市值 + 汇率转换
    # price_ccy = 交易货币(HKD), rpt_ccy = 报表货币(CNY), 不一致时换算
    price_ccy = config.MARKET_CONFIG.get(market, {}).get("currency", "CNY")
    rpt_ccy = _detect_rpt_ccy(reader, stock)
    need_spot_fx = (price_ccy != rpt_ccy and rpt_ccy == "CNY")
    fx_rate = None
    fx_available = not need_spot_fx  # A股/同币种不需要汇率
    if need_spot_fx:
        # 使用最新可获取汇率 (匹配spot价格日期)，优先当天 → 最近一天
        from datetime import date
        today_str = date.today().strftime("%Y-%m-%d")
        fx_rate = _get_fx_rate(today_str)
        if fx_rate is None:
            # fallback: 财年截止日汇率
            latest_rpt_date = f"{years[-1]}-{fye}" if years else None
            if latest_rpt_date:
                fx_rate = _get_fx_rate(latest_rpt_date)
        fx_available = (fx_rate is not None and fx_rate > 0)

    if spot and years and metrics:
        latest = metrics.get(years[-1], {})
        price = spot.get("price")  # 交易货币(HKD)
        # TTM EPS (原始 CNY, 始终可算)
        ttm_eps = _compute_ttm_eps(reader, years[-1])
        if ttm_eps:
            spot["eps_ttm"] = round(ttm_eps, 2)
        if price:
            # 折算: 股价(HKD) → CNY, 一次换算, 后续所有指标用 CNY 直接算
            fx = fx_rate if fx_rate and fx_rate > 0 else 1.0
            if need_spot_fx and not fx_available:
                spot["pe"] = "-"
                spot["pb"] = "-"
                spot["div_yield"] = "-"
            else:
                price_cny = price * fx
                if ttm_eps and ttm_eps > 0:
                    spot["pe"] = round(price_cny / ttm_eps, 1)
                    spot["eps_ttm_hkd"] = round(ttm_eps / fx, 2)  # 仅显示用
                else:
                    eps_latest = latest.get("BASIC_EPS")
                    if eps_latest and eps_latest > 0:
                        spot["pe"] = round(price_cny / eps_latest, 1)
                bps_latest = latest.get("BPS")
                if bps_latest and bps_latest > 0:
                    spot["pb"] = round(price_cny / bps_latest, 2)
                dps_latest = latest.get("DPS")
                if dps_latest and dps_latest > 0:
                    spot["div_yield"] = round(dps_latest / price_cny * 100, 2)
            # 市值 = 股价(HKD) × 股数, 不依赖汇率
            shares_raw = reader.share_count(_fye(years[-1])) or config.STOCKS.get(code, {}).get("shares")
            if shares_raw and shares_raw > 0:
                spot["mkt_cap"] = round(price * shares_raw / 1e8, 1)  # 股数×股价÷1亿

    # Median P/E: VL 10年PE中位数 (IQR过滤异常值)
    pe_history = [metrics[y]["PE_AVG"] for y in years if y in metrics and metrics[y].get("PE_AVG")]
    spot["median_pe"] = _median_pe_iqr(pe_history)

    # CAGR
    revenue = [metrics[y]["OPERATE_INCOME"] for y in years if y in metrics and metrics[y].get("OPERATE_INCOME")]
    eps_vals = [metrics[y]["BASIC_EPS"] for y in years if y in metrics and metrics[y].get("BASIC_EPS")]
    cfs_vals = [metrics[y]["PER_NETCASH"] for y in years if y in metrics and metrics[y].get("PER_NETCASH")]
    dps_vals = [metrics[y]["DPS"] for y in years if y in metrics and metrics[y].get("DPS", 0) > 0]
    equity_vals = [metrics[y]["TOTAL_EQUITY"] for y in years if y in metrics and metrics[y].get("TOTAL_EQUITY")]

    cagr = {
        "revenue": calc_cagr_multi(revenue, years),
        "eps": calc_cagr_multi(eps_vals, years),
        "cashflow": calc_cagr_multi(cfs_vals, years),
        "dividend": calc_cagr_multi(dps_vals, years),
        "equity": calc_cagr_multi(equity_vals, years),
    }

    # 半年度数据 (从 SQLite income 表读取), 如有最新 Q1 则前瞻一年
    qtr_years = list(years)
    _next_yr = str(int(years[-1]) + 1) if years else None
    if _next_yr:
        _next_q1 = reader.financial_item_by_code("income", "004001001", f"{_next_yr}-03-31") \
                   or reader.financial_item("income", "营业额", f"{_next_yr}-03-31")
        # 半年度报告公司仅有 H1 (06-30), 也需探测
        _next_h1 = reader.financial_item_by_code("income", "004001001", f"{_next_yr}-06-30") \
                   or reader.financial_item("income", "营业额", f"{_next_yr}-06-30")
        if _next_q1 or _next_h1:
            qtr_years.append(_next_yr)
    semi_annual = build_semi_annual(reader, qtr_years, metrics)

    # 营收结构 (从 SQLite revenue_structure 表读取)
    revenue_structure = {}
    latest_yr = years[-1] if years else "2025"
    # 回退: 如果最新年份无数据, 向前查找最近有数据的年份
    for dim in ["by_channel", "by_ip", "by_region", "by_segment", "by_product", "by_industry",
                 "by_tech", "by_app"]:
        data = None
        check_yr = latest_yr
        for _ in range(5):  # 最多回退5年
            data = reader.revenue_structure(check_yr, dim)
            if data:
                break
            check_yr = str(int(check_yr) - 1)
        if data:
            revenue_structure[dim] = data

    # ── 估值线: CF模式或PB模式 ──
    _val_method = reader.db_meta("valuation_method", "cf")
    _cf_mult = float(reader.db_meta("cf_multiplier", "15.0"))
    _pb_mult = float(reader.db_meta("pb_multiplier", "1.0"))

    if need_spot_fx and not fx_available:
        # 无汇率, 无法将 CNY 估值转为 HKD — 估值线留空
        valuation_line = []
    elif _val_method == "pb":
        _fx_cf = fx_rate if fx_rate and fx_rate > 0 else 1.0
        # PB Line: N×BPS, 转换为 HKD(与价格图一致)
        valuation_line = [{"date": y, "value": round(metrics[y].get("BPS", 0) * _pb_mult / _fx_cf, 2)}
                          for y in years if y in metrics and metrics[y].get("BPS")]
    else:
        _fx_cf = fx_rate if fx_rate and fx_rate > 0 else 1.0
        # CF Line: N×PER_NETCASH, 转换为 HKD(与价格图一致)
        valuation_line = [{"date": y, "value": round(metrics[y].get("PER_NETCASH", 0) * _cf_mult / _fx_cf, 2)}
                          for y in years if y in metrics and metrics[y].get("PER_NETCASH")]

    # Capital Structure
    balance_summary = {}
    income_summary = {}
    if latest_yr:
        rd = _fye(latest_yr)
        for item, key in [("总资产", "total_assets"), ("总负债", "total_liabilities"),
                          ("总权益", "total_equity"), ("流动资产合计", "current_assets"),
                          ("流动负债合计", "current_liabilities"),
                          ("现金及等价物", "cash"), ("存货", "inventory"),
                          ("应收帐款", "receivables")]:
            v = reader.financial_item("balance", item, rd)
            if v:
                balance_summary[key] = v / 1e8
        # 兜底: item_code 查找
        for item_code, item_name, key in [
            ("004002005", "预付款按金及其他应收款", "receivables"),
            ("005032022", "存货", "inventory"),
        ]:
            if key not in balance_summary:
                v = reader.financial_item_by_code("balance", item_code, rd)
                if v:
                    balance_summary[key] = v / 1e8
        for item, key in [("营业额", "revenue"), ("毛利", "gross_profit"),
                          ("股东应占溢利", "net_profit")]:
            v = reader.financial_item("income", item, rd)
            if v:
                income_summary[key] = v / 1e8

    # 1. CAPITAL STRUCTURE 资本结构明细
    cap_struct = _build_capital_structure(reader, spot, latest_yr, metrics, fx_rate, need_spot_fx)

    # 2. CURRENT POSITION 短期资产负债 (3年对比)
    cur_pos = _build_current_position(reader, years)

    # 3. ANNUAL RATES of Change (10yr/5yr/Future)
    annual_rates = _build_annual_rates(metrics, years)

    # 4. QUARTERLY TABLES (港股: H1/H2代替), 如有 Q1 则前瞻一年
    quarterly = build_semi_annual(reader, qtr_years, metrics)

    # Current Position 估值定位 (图表用)
    position = _calc_position(spot, kline, metrics, years)

    # Yearly High/Low (从月K线)
    yearly_hl = _build_yearly_hl(kline, years)

    index_kline = fetch_market_index(market)

    # ================================================================
    # % Total Return 计算 (个股 + 指数, 含股息)
    # 公式: (期末价 - 期初价 + 累计股息) / 期初价 × 100
    # ================================================================
    total_returns = {"stock": {}, "index": {}}
    # 取股息数据 (年度DPS)
    div_years = []
    for q in semi_annual.get("dividends", []):
        if q.get("full") > 0:
            div_years.append((str(q["year"]), q["full"]))
    div_map = dict(div_years)

    def _calc_return(prices, n_years):
        """自然年回报: Dec(year-n) → Dec(latest_complete_year)
        prices: [{date, close}] 月线; n_years: [1,3,5]"""
        result = {}
        if not prices:
            return {}
        # 找最近完整年份的12月收盘
        yr_close = {}
        for p in prices:
            yr = int(p["date"][:4])
            m = int(p["date"][5:7])
            if m == 12:
                yr_close[yr] = p["close"]
        if not yr_close:
            return {}
        last_yr = max(yr_close.keys())
        end_close = yr_close[last_yr]
        for n in n_years:
            start_yr = last_yr - n
            if start_yr not in yr_close:
                continue
            start_close = yr_close[start_yr]
            if not start_close or start_close == 0:
                continue
            # 前复权价格已含股息调整
            total_ret = (end_close - start_close) / start_close * 100
            result[f"{n}yr"] = round(total_ret, 1)
        return result

    total_returns["stock"] = _calc_return(kline, [1, 3, 5])
    total_returns["index"] = _calc_return(index_kline, [1, 3, 5])

    # ================================================================
    # 交叉校验 (3层: AKShare内部一致性, AKShare↔PDF, 营收结构完整性)
    # ================================================================
    validation = {
        "checked": [],
        "mismatches": [],
        "warnings": [],
        "sources": {},
        "status": "OK",
        "pdf_years": [],      # 有PDF营收数据的年份
        "checks_passed": 0,
        "checks_total": 0,
    }
    validation["sources"] = {
        "annual_indicators": "AKShare stock_financial_hk_analysis_indicator_em (年度指标)",
        "semi_annual_income": "AKShare stock_financial_hk_report_em 利润表 (06-30中报)",
        "dividend": "AKShare stock_hk_dividend_payout_em + 手动补充",
        "revenue_structure": "年报PDF提取 → SQLite revenue_structure 表",
        "index_kline": "新浪 stock_hk_index_daily_sina",
    }

    def add_check(year, metric, detail, diff_pct, threshold=1.0):
        validation["checked"].append({
            "year": year, "metric": metric, **detail, "diff_pct": round(diff_pct, 2)
        })
        if diff_pct > threshold:
            validation["mismatches"].append(f"{year} {metric}: {detail.get('summary','')} ({diff_pct:.1f}%)")
            validation["status"] = "MISMATCH"
        elif diff_pct > 0.05 and diff_pct <= threshold:
            validation["warnings"].append(f"{year} {metric}: {detail.get('summary','')} ({diff_pct:.1f}%)")

    def _chk(yr, metric, v1, v2, label1="ak", label2="pdf", threshold=1.0):
        """双值交叉校验: 两数都非空且可比时做差率检验"""
        if v1 is None or v2 is None: return
        if abs(v1) < 1e-6 or abs(v2) < 1e-6: return
        pct = abs(v1 - v2) / max(abs(v1), abs(v2)) * 100
        if pct > 0.001:  # 只在有差异时记录, 0%跳过
            add_check(yr, metric,
                       {"summary": f"{label1}={v1/1e8:.1f}B vs {label2}={v2/1e8:.1f}B",
                        label1: round(v1/1e8,2), label2: round(v2/1e8,2)},
                       pct, threshold=threshold)

    def _val(yr, field, rd):
        """读指标, 回退到 income/balance"""
        v = reader.financial_item("indicators", field, rd)
        if v is not None: return v
        return reader.financial_item("income", field, rd) or reader.financial_item("balance", field, rd)

    # ---- 1. AKShare 内部交叉校验: H1+H2 vs Annual ----
    for yr in years:
        sa = semi_annual.get(yr)
        ann = metrics.get(yr, {})
        if not sa:
            continue

        # 1a. Revenue
        if sa.get("annual_revenue", 0) > 0:
            h1h2_rev = sa["h1_revenue"] + sa["h2_revenue"]
            ann_rev = sa["annual_revenue"]
            rev_diff = abs(h1h2_rev - ann_rev) / max(abs(ann_rev), 0.01) * 100
            add_check(yr, "Revenue H1+H2=Annual",
                       {"summary": f"Revenue: H1+H2={h1h2_rev:.1f} vs Annual={ann_rev:.1f}", "h1h2": round(h1h2_rev,2), "annual": round(ann_rev,2)},
                       rev_diff)

        # 1b. Net Profit
        if sa.get("annual_net_profit", 0) > 0:
            h1h2_np = sa["h1_net_profit"] + sa["h2_net_profit"]
            ann_np = sa["annual_net_profit"]
            np_diff = abs(h1h2_np - ann_np) / max(abs(ann_np), 0.01) * 100
            add_check(yr, "NetProfit H1+H2=Annual",
                       {"summary": f"NP: H1+H2={h1h2_np:.1f} vs Annual={ann_np:.1f}", "h1h2": round(h1h2_np,2), "annual": round(ann_np,2)},
                       np_diff)

        # 1c. EPS
        sa_eps_h1 = sa.get("h1_eps")
        sa_eps_ann = sa.get("annual_eps")
        if sa_eps_h1 is not None and sa_eps_ann is not None and sa_eps_ann > 0:
            h2_eps = sa.get("h2_eps")
            if h2_eps is not None:
                h1h2_eps = sa_eps_h1 + h2_eps
                eps_diff = abs(h1h2_eps - sa_eps_ann) / abs(sa_eps_ann) * 100
                add_check(yr, "EPS H1+H2=Annual",
                           {"summary": f"EPS: H1+H2={h1h2_eps:.2f} vs Annual={sa_eps_ann:.2f}", "h1h2": round(h1h2_eps,4), "annual": round(sa_eps_ann,4)},
                           eps_diff)

    # ---- 2. AKShare ↔ PDF 营收数据交叉校验 ----
    pdf_checks = reader.conn.execute(
        "SELECT DISTINCT year FROM revenue_structure WHERE code=? ORDER BY year",
        (code,)).fetchall()
    pdf_years = [r[0] for r in pdf_checks]
    validation["pdf_years"] = pdf_years

    for pdf_yr in pdf_years:
        pdf_rds = [_fye(pdf_yr)]
        for rd in pdf_rds:
            # 2a. 营收总额: AKShare income.营业额 vs PDF revenue_structure by_region sum
            # 注意: income 存元, revenue_structure 存百万(1e6), 需统一为元
            ak_rev = reader.financial_item("income", "营业额", rd)
            pdf_sum_raw = reader.conn.execute(
                "SELECT SUM(amount) FROM revenue_structure WHERE code=? AND year=? AND dim_type='by_region'",
                (code, str(pdf_yr))).fetchone()[0]

            if ak_rev and pdf_sum_raw and ak_rev > 0:
                pdf_sum = pdf_sum_raw * 1e6  # 百万 → 元
                rev_pct = abs(ak_rev - pdf_sum) / ak_rev * 100
                pdf_th = 5.0
                add_check(str(pdf_yr), "AKShare↔PDF Revenue",
                           {"summary": f"AKShare={ak_rev/1e8:.1f}B vs PDF={pdf_sum/1e8:.1f}B", "akshare": round(ak_rev/1e8,2), "pdf": round(pdf_sum/1e8,2)},
                           rev_pct, threshold=pdf_th)

            # 3. 营收结构维度完整性: 各维度 pct 总和是否 = 100%
            for dim in ["by_channel", "by_ip", "by_region", "by_segment", "by_tech", "by_app"]:
                dim_sum = reader.conn.execute(
                    "SELECT SUM(pct) FROM revenue_structure WHERE code=? AND year=? AND dim_type=?",
                    (code, str(pdf_yr), dim)).fetchone()[0]
                if dim_sum is not None:
                    pct_gap = abs(100 - dim_sum)
                    if pct_gap > 0.5:
                        add_check(str(pdf_yr), f"Revenue {dim} sum=100%",
                                   {"summary": f"{dim}: sum_pct={dim_sum:.1f}% (gap={pct_gap:.1f}%)", "sum_pct": round(dim_sum,2)},
                                   pct_gap, threshold=0.5)

    # ---- 4. 全量指标内部交叉校验: indicators ↔ income/balance (所有年份) ----
    for yr in years:
        rd = _fye(yr)
        row = metrics.get(yr, {})

        # 4a. Revenue
        ak_rev = _val(yr, "OPERATE_INCOME", rd)
        inc_rev = reader.financial_item_by_code("income", "004001001", rd)
        rev_th = 3.0
        _chk(yr, "AKShare↔Income Revenue", ak_rev, inc_rev, threshold=rev_th)

        # 4b. Net Profit
        ak_np = _val(yr, "HOLDER_PROFIT", rd)
        inc_np = reader.financial_item_by_code("income", "004025002", rd)
        _chk(yr, "AKShare↔Income NetProfit", ak_np, inc_np)

        # 4c. Total Assets
        ak_ta = _val(yr, "TOTAL_ASSETS", rd)
        bal_ta = reader.financial_item("balance", "总资产", rd)
        _chk(yr, "AKShare↔Balance TotalAssets", ak_ta, bal_ta)

        # 4d. Total Equity
        ak_eq = _val(yr, "TOTAL_EQUITY", rd)
        bal_eq = reader.financial_item("balance", "股东权益", rd) or reader.financial_item("balance", "权益总额", rd)
        _chk(yr, "AKShare↔Balance Equity", ak_eq, bal_eq)

        # 4e. Depreciation
        ak_dep = row.get("DEPRECIATION")  # 亿
        cf_dep = reader.financial_item("cashflow", "加:折旧及摊销", rd)
        if ak_dep and cf_dep:
            ak_dep_v = ak_dep * 1e8
            _chk(yr, "AKShare↔Cashflow Depreciation", ak_dep_v, cf_dep, threshold=5.0)

        # 4f. Per-share consistency
        sh = row.get("TOTAL_SHARES")
        if sh and sh > 0:
            shares = sh * 1e6
            # PER_OI
            poi = row.get("PER_OI")
            if poi and ak_rev:
                calc = round(ak_rev / shares, 2)
                d = abs(poi - calc) / max(poi, 0.01) * 100
                add_check(yr, "PerSh OI consistency",
                           {"summary": f"PER_OI={poi} vs Rev/Sh={calc}", "actual": poi, "calc": calc},
                           d, threshold=0.5)
            # BPS
            b = row.get("BPS")
            eq_yuan = row.get("TOTAL_EQUITY")
            if b and eq_yuan and eq_yuan > 0:
                calc_b = round(eq_yuan * 1e8 / shares, 2)
                bd = abs(b - calc_b) / max(b, 0.01) * 100
                add_check(yr, "PerSh BPS consistency",
                           {"summary": f"BPS={b} vs Eq/Sh={calc_b}", "actual": b, "calc": calc_b},
                           bd, threshold=20.0)

        # 4g. TOTAL_SHARES 三源交叉
        ish = row.get("TOTAL_SHARES")
        if ish and ish > 0:
            rev_yr = row.get("OPERATE_INCOME")
            poi_yr = row.get("PER_OI")
            if rev_yr and poi_yr and poi_yr > 0:
                sh_oi = round(rev_yr * 100 / poi_yr, 1)
                d1 = abs(ish - sh_oi) / ish * 100
                add_check(yr, "SHARES: ind vs Rev/PER_OI",
                           {"summary": f"ind={ish}M vs OI-der={sh_oi}M",
                            "indicator": ish, "oi_derived": sh_oi},
                           d1, threshold=0.5)
            eq_yr = row.get("TOTAL_EQUITY")
            bps_yr = row.get("BPS")
            if eq_yr and bps_yr and bps_yr > 0:
                sh_bps = round(eq_yr * 100 / bps_yr, 1)
                d2 = abs(ish - sh_bps) / ish * 100
                add_check(yr, "SHARES: ind vs Eq/BPS",
                           {"summary": f"ind={ish}M vs BPS-der={sh_bps}M",
                            "indicator": ish, "bps_derived": sh_bps},
                           d2, threshold=20.0)

    # ---- 统计 ----
    validation["checks_total"] = len(validation["checked"])
    validation["checks_passed"] = validation["checks_total"] - len(validation["mismatches"])
    for m in validation["mismatches"]:
        print(f"    ❌ {m}")
    for w in validation["warnings"]:
        print(f"    ⚠️  {w}")

    source_count = len(validation["sources"])
    print(f"  数据源: {source_count} (AKShare年度/半年度/股息 + PDF营收结构 + HSI)")
    print(f"  交叉校验: {validation['checks_passed']}/{validation['checks_total']} 通过 "
          f"({len(validation['mismatches'])} 失败, {len(validation['warnings'])} 警告)")

    # Business 描述 & AI Commentary: per-stock脚本 > PDF提取(quality=1) > 数据自生成
    # 不再因 quality=="0" 而跳过: 新阈值已放宽, 即使标记0也有可用文本
    mda_parsed = _parse_mda_text(cap_struct.get("mda_text", ""))

    # 尝试加载个股专属脚本
    per_stock_mod = _load_per_stock_script(code)
    per_stock_result = None
    if per_stock_mod:
        try:
            per_stock_result = per_stock_mod.build(stock, metrics, revenue_structure, years, cagr, spot)
        except Exception as e:
            print(f"  ⚠️ per-stock script error: {e}")

    # Business: per-stock > PDF > config.business_desc > generic
    business = None
    if per_stock_result and per_stock_result.get("business"):
        business = per_stock_result["business"]
    elif mda_parsed and mda_parsed.get("business_summary"):
        business = mda_parsed["business_summary"]
    elif stock.get("business_desc"):
        business = stock.get("business_desc")
    else:
        business = _build_business_from_data(stock, metrics, revenue_structure, years)

    # AI Commentary: per-stock > PDF > generic
    commentary_from_mda = []
    if per_stock_result and per_stock_result.get("commentary"):
        commentary_from_mda = per_stock_result["commentary"]
    elif mda_parsed and mda_parsed.get("mda_sections"):
        sec = mda_parsed["mda_sections"]
        if "product" in sec:
            commentary_from_mda.append("【业务结构】" + "；".join(sec["product"][:3]))
        ch_rg = []
        if "channel" in sec:
            ch_rg.append("渠道：" + "；".join(sec["channel"][:2]))
        if "region" in sec:
            ch_rg.append("地区：" + "；".join(sec["region"][:2]))
        if ch_rg:
            commentary_from_mda.append("；".join(ch_rg))
        if "cost" in sec:
            commentary_from_mda.append("【成本与效率】" + "；".join(sec["cost"][:3]))
        if mda_parsed.get("outlook"):
            commentary_from_mda.append("【展望】" + "；".join(mda_parsed["outlook"][:2]))

    if not commentary_from_mda:
        commentary_from_mda = _build_commentary_from_data(stock, metrics, revenue_structure, years, cagr, spot)

    analyst = {
        "business": business,
        "commentary": commentary_from_mda,
        "commentary_from_mda": bool(mda_parsed and mda_parsed.get("mda_sections")),
        "commentary_from_script": bool(per_stock_result and per_stock_result.get("commentary")),
        "recommendation": "",
    }

    report = {
        "meta": {
            "code": code, "name": stock["name"], "name_en": stock["name_en"],
            "market": stock["market"], "currency": stock.get("currency", reader.db_meta("currency", "CNY")),
            "industry": stock.get("industry", ""),
            "ceo": stock.get("ceo", ""),
            "inc": stock.get("inc", ""),
            "website": stock.get("website", ""),
            # 股价货币 & 市场指数 — 从 MARKET_CONFIG 驱动, 不硬编码
            "price_ccy": config.MARKET_CONFIG.get(stock.get("market", ""), {}).get("currency", "CNY"),
            "index_name": config.MARKET_CONFIG.get(stock.get("market", ""), {}).get("index_name", "Index"),
            "index_name_cn": config.MARKET_CONFIG.get(stock.get("market", ""), {}).get("index_name_cn", "市场指数"),
            # 财报货币: DB meta优先, 其次config, 最后从IS_CNY_CODE推断
            "rpt_ccy": _detect_rpt_ccy(reader, stock),
            "generated": str(__import__("datetime").datetime.now()),
        },
        "spot": spot,
        "kline": kline,
        "index_kline": index_kline,
        "total_returns": total_returns,
        "years": years,
        "metric_defs": [{"order": m[0], "name_cn": m[1], "name_en": m[2],
                          "field": m[3], "unit": m[4], "source": m[5]}
                        for m in config.VL_METRICS],
        "data": metrics,
        "cagr": cagr,
        "quarterly": semi_annual,
        "valuation_line": valuation_line,
        "valuation_method": _val_method,
        "cf_multiplier": _cf_mult,
        "pb_multiplier": _pb_mult,
        "balance_summary": balance_summary,
        "income_summary": income_summary,
        "revenue_structure": revenue_structure,
        "capital_structure": cap_struct,
        "current_position": cur_pos,
        "annual_rates": annual_rates,
        "quarterly": quarterly,
        "yearly_hl": yearly_hl,
        "position": position,
        "analyst": analyst,
        "validation": validation,
        "footnotes": footnotes_data,
        "bps_source": "归属于母公司权益 ÷ 股数 (计算值, 与年报披露口径可能有小幅差异)",
        "data_source_note": data_source_note,
    }

    out_dir = os.path.dirname(os.path.abspath(__file__))
    out_path = os.path.join(out_dir, "report_data.json")
    out_tmp = out_path + ".tmp"
    try:
        with open(out_tmp, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2, default=str)
        os.replace(out_tmp, out_path)
    except Exception:
        out_path2 = os.path.join(os.environ.get("TEMP", "/tmp"), "report_data.json")
        with open(out_path2, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2, default=str)
        out_path = out_path2
    reader.close()
    print(f"report_data.json 写入: {out_path}")
    print(f"  年数: {len(years)} ({years[0]}-{years[-1]})")
    print(f"  K线: {len(kline)} 个月 | HSI: {len(index_kline)} 个月")
    print(f"  季度/半年: {len(quarterly.get('sales',[]))} 年")
    return out_path


if __name__ == "__main__":
    build_report()
