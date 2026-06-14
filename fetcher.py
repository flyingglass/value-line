# -*- coding: utf-8 -*-
"""
fetcher.py — AKShare 数据获取, 存入 SQLite
运行方式: python fetcher.py [code]
  不加参数: 使用 config.ACTIVE_STOCK
  加参数:   python fetcher.py 600519
"""
import os, sys, time, sqlite3, json, re
import warnings
warnings.filterwarnings("ignore")
if sys.platform == 'win32': sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# 项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config

# ---- 环境准备 ----
for k in list(os.environ.keys()):
    if any(x in k.upper() for x in ("PROXY", "HTTP_", "HTTPS_", "ALL_PROXY")):
        os.environ.pop(k, None)

import requests as _rq
_orig_init = _rq.Session.__init__
def _patched_init(self):
    _orig_init(self)
    self.trust_env = False
    self.proxies = {}
_rq.Session.__init__ = _patched_init

import akshare as ak

# ============================================================
# SQLite 工具
# ============================================================
class Store:
    def __init__(self, code):
        self.path = config.db_path(code)
        self.conn = sqlite3.connect(self.path)
        self._init_tables()

    def _init_tables(self):
        c = self.conn
        c.execute("""CREATE TABLE IF NOT EXISTS meta (
            key TEXT PRIMARY KEY, value TEXT)""")
        c.execute("""CREATE TABLE IF NOT EXISTS spot (
            date TEXT, price REAL, pe REAL, pb REAL, div_yield REAL,
            mkt_cap REAL, change_pct REAL, volume REAL, high_52w REAL, low_52w REAL)""")
        c.execute("""CREATE TABLE IF NOT EXISTS kline (
            date TEXT PRIMARY KEY, open REAL, high REAL, low REAL,
            close REAL, volume REAL, adjust TEXT)""")
        c.execute("""CREATE TABLE IF NOT EXISTS income (
            report_date TEXT, item_name TEXT, amount REAL, item_code TEXT,
            PRIMARY KEY (report_date, item_name))""")
        c.execute("""CREATE TABLE IF NOT EXISTS balance (
            report_date TEXT, item_name TEXT, amount REAL, item_code TEXT,
            PRIMARY KEY (report_date, item_name))""")
        c.execute("""CREATE TABLE IF NOT EXISTS cashflow (
            report_date TEXT, item_name TEXT, amount REAL, item_code TEXT,
            PRIMARY KEY (report_date, item_name))""")
        # 兼容旧表: 添加 item_code 列
        for tbl in ["income", "balance", "cashflow"]:
            try:
                c.execute(f"ALTER TABLE {tbl} ADD COLUMN item_code TEXT")
            except:
                pass  # 列已存在
        c.execute("""CREATE TABLE IF NOT EXISTS indicators (
            report_date TEXT, item_name TEXT, amount REAL,
            PRIMARY KEY (report_date, item_name))""")
        c.execute("""CREATE TABLE IF NOT EXISTS dividend (
            report_year TEXT, cash_dps REAL, special_dps REAL,
            ex_date TEXT, pay_date TEXT, total_amount REAL,
            raw_text TEXT DEFAULT '',
            PRIMARY KEY (report_year))""")
        try: c.execute("ALTER TABLE dividend ADD COLUMN raw_text TEXT DEFAULT ''")
        except Exception: pass
        c.execute("""CREATE TABLE IF NOT EXISTS revenue_structure (
            code TEXT, year TEXT, dim_type TEXT, dim_name TEXT,
            amount REAL, pct REAL,
            PRIMARY KEY (code, year, dim_type, dim_name))""")
        self.conn.commit()

    def set_meta(self, key, value):
        self.conn.execute(
            "INSERT OR REPLACE INTO meta VALUES (?,?)", (key, value))
        self.conn.commit()

    def get_meta(self, key):
        r = self.conn.execute(
            "SELECT value FROM meta WHERE key=?", (key,)).fetchone()
        return r[0] if r else None

    def upsert_indicators(self, report_date, items):
        """批量写入分析指标, 字段名→值"""
        for k, v in items.items():
            if v is None:
                continue
            try:
                self.conn.execute(
                    "INSERT OR IGNORE INTO indicators VALUES (?,?,?)",
                    (str(report_date), k, float(v)))
            except (ValueError, TypeError):
                pass
        self.conn.commit()

    def upsert_financials(self, table, df_batch):
        """将DataFrame行写入财务表"""
        for _, row in df_batch.iterrows():
            rd = str(row.get("REPORT_DATE", "")).split(" ")[0]
            name = str(row.get("STD_ITEM_NAME", ""))
            item_code = str(row.get("STD_ITEM_CODE", ""))
            try:
                amt = float(row.get("AMOUNT", 0))
            except (ValueError, TypeError):
                amt = 0
            self.conn.execute(
                f"INSERT OR REPLACE INTO {table} VALUES (?,?,?,?)",
                (rd, name, amt, item_code))
        self.conn.commit()

    def close(self):
        self.conn.close()

# ============================================================
# 行情数据
# ============================================================
def fetch_spot_hk(store, code):
    """港股实时行情"""
    print("  [spot_hk] ", end="", flush=True)
    df = ak.stock_hk_spot()
    row = df[df["代码"] == code]
    if row.empty:
        print("未找到")
        return
    r = row.iloc[0]
    store.conn.execute("DELETE FROM spot")
    store.conn.execute(
        "INSERT INTO spot VALUES (?,?,?,?,?,?,?,?,?,?)",
        (str(pd.Timestamp.now().date()), float(r.get("最新价", 0)),
         float(r.get("市盈率", 0)), float(r.get("市净率", 0)),
         0.0, float(r.get("总市值", 0)),
         float(r.get("涨跌幅", 0)), float(r.get("成交量", 0)),
         0.0, 0.0))
    store.conn.commit()
    print(f"OK 股价={r['最新价']}")

def fetch_spot_cn(store, code, pfx):
    """A股实时行情 (新浪, 容错: 外网不通时跳过)"""
    print("  [spot_cn] ", end="", flush=True)
    try:
        df = ak.stock_zh_a_spot()
        full_code = f"{pfx}{code}"
        row = df[df["代码"] == full_code]
        if row.empty:
            print("未找到")
            return
        r = row.iloc[0]
        store.conn.execute("DELETE FROM spot")
        store.conn.execute(
            "INSERT INTO spot VALUES (?,?,?,?,?,?,?,?,?,?)",
            (str(pd.Timestamp.now().date()), float(r.get("最新价", 0)),
             float(r.get("市盈率", 0)) if "市盈率" in df.columns else 0,
             float(r.get("市净率", 0)) if "市净率" in df.columns else 0,
             0.0, 0.0,
             float(r.get("涨跌幅", 0)), float(r.get("成交量", 0)),
             0.0, 0.0))
        store.conn.commit()
        print(f"OK 股价={r['最新价']}")
    except Exception as e:
        print(f"跳过 (API不可用: {str(e)[:60]})")

# ============================================================
# K线数据
# ============================================================
def fetch_kline_hk(store, code):
    """港股日线K线 (新浪)"""
    print("  [kline_hk] ", end="", flush=True)
    df = ak.stock_hk_daily(symbol=code, adjust="qfq")
    store.conn.execute("DELETE FROM kline WHERE adjust='qfq'")
    for _, r in df.iterrows():
        store.conn.execute(
            "INSERT OR REPLACE INTO kline VALUES (?,?,?,?,?,?,?)",
            (str(r["date"]).split(" ")[0],
             float(r.get("open", 0)), float(r.get("high", 0)),
             float(r.get("low", 0)), float(r.get("close", 0)),
             float(r.get("volume", 0)), "qfq"))
    store.conn.commit()
    print(f"OK {len(df)}条")

def fetch_kline_cn(store, code, pfx):
    """A股日线K线 (新浪)"""
    print("  [kline_cn] ", end="", flush=True)
    df = ak.stock_zh_a_daily(symbol=f"{pfx}{code}", adjust="qfq")
    store.conn.execute("DELETE FROM kline WHERE adjust='qfq'")
    for _, r in df.iterrows():
        store.conn.execute(
            "INSERT OR REPLACE INTO kline VALUES (?,?,?,?,?,?,?)",
            (str(r["date"]).split(" ")[0],
             float(r.get("open", 0)), float(r.get("high", 0)),
             float(r.get("low", 0)), float(r.get("close", 0)),
             float(r.get("volume", 0)), "qfq"))
    store.conn.commit()
    print(f"OK {len(df)}条")

# ============================================================
# 港股财务数据 (TDX 三大表 + AKShare 指标/分红)
# ============================================================
def fetch_hk_financials(store, code):
    """港股三大表(TDX, 含完整历史) + 分析指标(AKShare) + 分红(AKShare)"""
    import tdx_client

    # ── 三大表: 先 AKShare 写入 (2017+), 再 TDX 补缺 (2001-2016) ──
    # AKShare 为近年数据优先源, TDX 仅 INSERT OR IGNORE 补充早年空缺年份
    table_fetchers = [
        ("income", "利润表", tdx_client.fetch_hk_income),
        ("balance", "资产负债表", tdx_client.fetch_hk_balance),
        ("cashflow", "现金流量表", tdx_client.fetch_hk_cashflow),
    ]
    # TDX 每股类项目已是元, 不乘 10000
    _PS_ITEMS = {"每股基本盈利", "每股摊薄盈利"}

    for table, sym, tdx_fetcher in table_fetchers:
        print(f"  [hk_{table}] ", end="", flush=True)
        # Step A: AKShare 写入 (优先, 主数据源)
        try:
            df = ak.stock_financial_hk_report_em(
                stock=code, symbol=sym, indicator="全部")
            store.upsert_financials(table, df)
            ak_dates = set(str(d)[:10] for d in df["REPORT_DATE"])
            n_ak_annual = sum(1 for d in ak_dates if d.endswith("12-31"))
            print(f"AKShare {len(df)}行 ({n_ak_annual}年报)", end="", flush=True)
        except Exception as e:
            print(f"AKShare fail ({e})", end="", flush=True)
            ak_dates = set()

        # Step B: TDX 补缺 (INSERT OR IGNORE, 不覆盖 AKShare 已有数据)
        try:
            rows = tdx_fetcher(code)
            n_tdx = 0
            for r in rows:
                # 仅当该 (report_date, item_name) 不存在时才写入
                amt = r["amount"] * 10000 if r["item_name"] not in _PS_ITEMS else r["amount"]
                try:
                    store.conn.execute(
                        f"INSERT OR IGNORE INTO {table} VALUES (?,?,?,?)",
                        (r["report_date"], r["item_name"], amt, None))
                    n_tdx += 1
                except Exception:
                    pass
            store.conn.commit()
            tdx_dates = set(r["report_date"] for r in rows)
            n_tdx_annual = sum(1 for d in tdx_dates if d.endswith("12-31"))
            print(f" + TDX补 {n_tdx}条 ({n_tdx_annual}年报)", end="", flush=True)
        except Exception as e:
            print(f" + TDX fail ({e})", end="", flush=True)

        print()

    # ── 分析指标: 仍用 AKShare (TDX 暂无港股指标接口) ──
    print("  [hk_indicators] ", end="", flush=True)
    df = ak.stock_financial_hk_analysis_indicator_em(
        symbol=code, indicator="年度")
    # 将宽表转为 key-value
    for _, row in df.iterrows():
        rd = str(row.get("REPORT_DATE", "")).split(" ")[0]
        items = {}
        for col in df.columns:
            if col in ("SECUCODE", "SECURITY_CODE", "SECURITY_NAME_ABBR",
                       "ORG_CODE", "REPORT_DATE", "DATE_TYPE_CODE",
                       "START_DATE", "FISCAL_YEAR", "CURRENCY"):
                continue
            try:
                items[col] = float(row[col])
            except (ValueError, TypeError):
                pass
        store.upsert_indicators(rd, items)
    print(f"OK {len(df)}行")
    # 保存币种信息到 meta
    if len(df) > 0:
        raw_currency = str(df.iloc[0].get("CURRENCY", ""))
        if raw_currency:
            store.set_meta("currency", raw_currency)

    # 分红
    print("  [hk_dividend] ", end="", flush=True)
    df = ak.stock_hk_dividend_payout_em(symbol=code)
    if df is None or df.empty:
        print(f"OK 0条 (无分红数据)")
        return
    cols = df.columns.tolist()
    # 列名编码乱码, 通过内容特征自动识别各列
    col_fy = None   # 财政年度 (4位数字)
    col_txt = None  # 分红方案 (含数字和"港"/"美"字)
    date_cols = []
    for i, c in enumerate(cols):
        val = str(df.iloc[0][c])
        if val.isdigit() and len(val) == 4:
            col_fy = i
        elif re.search(r'\d+\.\d+', val):  # 含小数点的分红文本列
            col_txt = i
        if val.count("-") == 2 and len(val) == 10:
            date_cols.append(i)

    # 收集所有行, 按财政年度汇总 (普通+特别合算)
    div_map = {}
    for _, r in df.iterrows():
        fy = str(r.iloc[col_fy]) if col_fy is not None else str(r.iloc[1])
        txt = str(r.iloc[col_txt]) if col_txt is not None else ""
        
        # 精确匹配: 每股派人民币0.276元 / 每股派港币5.3元 / 每股派港币1元 / 相当于每股派18.13港元
        m = re.search(r'每股派(?:港币|港元|美元|人民币)?\s*(\d+\.?\d*)', txt)
        if m:
            dps = float(m.group(1))
        else:
            # 回退: 取第一个含小数点的数字
            nums = re.findall(r"(\d+\.?\d*)", txt)
            dps_nums = [float(n) for n in nums if '.' in n]
            dps = dps_nums[0] if dps_nums else 0.0
        
        # HKD→CNY 换算: 分红是港币但报表货币是人民币时需转换
        # 00696 分红是"人民币"无需换算, 00700 分红是"港币"需换算
        if dps > 0 and re.search(r'港[元币]', txt) and '人民币' not in txt:
            stock_cfg = config.STOCKS.get(code, {})
            if stock_cfg.get('currency') == 'CNY':
                fx = _read_fx_rate(f"{fy}-12-31")
                if fx:
                    dps = round(dps * fx, 4)
        
        if fy in div_map:
            div_map[fy]["dps"] += dps  # 叠加特别股息
            div_map[fy]["raw"] += " | " + txt
        else:
            ex = str(r.iloc[date_cols[0]]) if len(date_cols) > 0 else ""
            pay = str(r.iloc[date_cols[-1]]) if len(date_cols) > 1 else ""
            div_map[fy] = {"dps": dps, "ex": ex, "pay": pay, "raw": txt}
    
    for fy, data in div_map.items():
        store.conn.execute(
            "INSERT OR REPLACE INTO dividend VALUES (?,?,?,?,?,?,?)",
            (fy, data["dps"], 0.0, data["ex"], data["pay"], 0.0, data.get("raw", "")))
    store.conn.commit()
    print(f"OK {len(df)}条")

# ============================================================
# A股财务数据 (同花顺 + 巨潮)
# ============================================================
def _parse_cn_amount(val):
    """解析带中文单位的金额: '29.15亿'→2915000000, '5677.30万'→56773000"""
    if val is None:
        return None
    s = str(val).strip()
    if not s:
        return None
    try:
        return float(s)
    except ValueError:
        pass
    # 处理中文单位
    multipliers = {"亿": 1e8, "万": 1e4, "千": 1e3, "元": 1.0, "%": 1.0}
    for unit, mult in multipliers.items():
        if s.endswith(unit):
            try:
                return float(s[:-len(unit)]) * mult
            except ValueError:
                return None
    # 尝试直接转换(可能含有逗号等)
    try:
        return float(s.replace(",", ""))
    except ValueError:
        return None

def fetch_cn_financials(store, code):
    """A股三大表 (同花顺) + 指标 + 分红 (巨潮)"""
    # 三大表 - 同花顺
    for table, fn in [("income", ak.stock_financial_benefit_ths),
                       ("balance", ak.stock_financial_debt_ths),
                       ("cashflow", ak.stock_financial_cash_ths)]:
        print(f"  [cn_{table}] ", end="", flush=True)
        try:
            df = fn(symbol=code)
        except Exception as e:
            print(f"跳过 (API不可用: {str(e)[:60]})")
            continue
        # 同花顺接口返回的列名不同, 统一处理
        df = fn(symbol=code)
        # 宽表→长表
        for idx, row in df.iterrows():
            item = row.get("报告期", str(idx))
            for col in df.columns[1:]:
                amt = _parse_cn_amount(row[col])
                if amt is None:
                    continue
                store.conn.execute(
                    f"INSERT OR REPLACE INTO {table} VALUES (?,?,?,?)",
                    (str(item), str(col), amt, None))
        store.conn.commit()
        print(f"OK {len(df)}行")

    # 分析指标 - 同花顺新版 (长表格式)
    print("  [cn_indicators] ", end="", flush=True)
    df = ak.stock_financial_abstract_new_ths(
        symbol=code, indicator="按报告期")
    # 新版API返回长表: report_date, metric_name, value, ...
    for _, row in df.iterrows():
        rd = str(row.get("report_date", ""))
        metric = str(row.get("metric_name", ""))
        val = row.get("value")
        if not rd or not metric:
            continue
        try:
            amt = float(val)
        except (ValueError, TypeError):
            continue
        store.conn.execute(
            "INSERT OR REPLACE INTO indicators VALUES (?,?,?)",
            (rd, metric, amt))
    store.conn.commit()
    print(f"OK {len(df)}行")

    # 分红 - 巨潮 (新API格式: 派息比例=每10股派息金额)
    print("  [cn_dividend] ", end="", flush=True)
    df = ak.stock_dividend_cninfo(symbol=code)
    for _, r in df.iterrows():
        try:
            # "报告时间" 格式: "2004年报" → 提取年份
            rpt_time = str(r.get("报告时间", ""))
            fy = rpt_time[:4] if rpt_time and rpt_time[0].isdigit() else ""
            if not fy:
                continue
            # 派息比例 = 每10股派息(元), 转增比例 = 每10股转增(股)
            dps = float(r.get("派息比例", 0) or 0)  # 每10股金额
            cash_dps = round(dps / 10.0, 4) if dps > 0 else 0.0  # 每股息
            trans = float(r.get("转增比例", 0) or 0)
            store.conn.execute(
                "INSERT OR REPLACE INTO dividend VALUES (?,?,?,?,?,?,?)",
                (fy, cash_dps,
                 0.0,  # special_dps
                 str(r.get("除权日", "")),
                 str(r.get("派息日", "")),
                 0.0,  # total_amount
                 str(r.get("方案说明", ""))))  # raw_text
        except Exception:
            pass
    store.conn.commit()
    print(f"OK {len(df)}条")


# ============================================================
# 美股数据 (AKShare)
# ============================================================

# US East Money 财务项目名 → 标准 VL 项目名 (兼容 engine.py 查询)
_US_FINANCIAL_ITEM_MAP = {
    # 利润表 income
    "营业收入": "*营业总收入",
    "主营收入": "*营业总收入",
    "归属于母公司股东净利润": "*归属于母公司所有者的净利润",
    "营业利润": "三、营业利润",
    "营业成本": "其中：营业成本",
    "营销费用": "销售费用",
    "营业费用": "管理费用",
    "研发费用": "研发费用",
    "利息支出": "其中：利息费用",
    "其他收入(支出)": "其他收益",
    "所得税": "减：所得税费用",
    "持续经营税前利润": "四、利润总额",
    "基本每股收益-普通股": "（一）基本每股收益",
    "摊薄每股收益-普通股": "（二）稀释每股收益",
    "毛利": "毛利",
    # 资产负债表 balance
    "现金及现金等价物": "现金及等价物",
    "应收账款": "应收帐款",
    "短期债务": "短期贷款",
    "长期负债": "长期贷款",
    "非流动负债合计": "非流动负债合计",
    "流动资产合计": "流动资产合计",
    "流动负债合计": "流动负债合计",
    "总资产": "总资产",
    "总负债": "总负债",
    "物业、厂房及设备": "固定资产",
    "无形资产": "无形资产",
    "商誉": "商誉",
    # 现金流量表 cashflow
    "折旧及摊销": "固定资产折旧、油气资产折耗、生产性生物资产折旧",
    "购买固定资产": "购建固定资产、无形资产和其他长期资产支付的现金",
    "经营活动产生的现金流量净额": "经营活动产生的现金流量净额",
    "投资活动产生的现金流量净额": "投资活动产生的现金流量净额",
    "股息支付": "股息支付",
}


def fetch_spot_us(store, code):
    """美股实时行情 (新浪 stock_us_spot)"""
    print("  [spot_us] ", end="", flush=True)
    try:
        df = ak.stock_us_spot()
        # Sina API 列名: symbol, price, pe, mktcap, chg, volume, name, cname ...
        row = df[df["symbol"].astype(str).str.upper() == code.upper()]
        if row.empty:
            print("未找到")
            return
        r = row.iloc[0]
        store.conn.execute("DELETE FROM spot")
        store.conn.execute(
            "INSERT INTO spot VALUES (?,?,?,?,?,?,?,?,?,?)",
            (str(pd.Timestamp.now().date()), float(r.get("price", 0)),
             float(r.get("pe", 0)) if pd.notna(r.get("pe")) else 0,
             0.0,  # pb (新浪 API 无 PB)
             0.0,  # div_yield (新浪 API 无)
             float(r.get("mktcap", 0)) if pd.notna(r.get("mktcap")) else 0,
             float(r.get("chg", 0)) if pd.notna(r.get("chg")) else 0,
             float(r.get("volume", 0)) if pd.notna(r.get("volume")) else 0,
             0.0, 0.0))  # high_52w, low_52w (新浪 API 无)
        store.conn.commit()
        print(f"OK 股价={r['price']} PE={r.get('pe','N/A')}")
    except Exception as e:
        print(f"跳过 (API不可用: {str(e)[:120]})")


def fetch_kline_us(store, code):
    """美股日线K线 (新浪 stock_us_daily)"""
    print("  [kline_us] ", end="", flush=True)
    try:
        df = ak.stock_us_daily(symbol=code, adjust="qfq")
        store.conn.execute("DELETE FROM kline WHERE adjust='qfq'")
        for _, r in df.iterrows():
            store.conn.execute(
                "INSERT OR REPLACE INTO kline VALUES (?,?,?,?,?,?,?)",
                (str(r["date"]).split(" ")[0],
                 float(r.get("open", 0)), float(r.get("high", 0)),
                 float(r.get("low", 0)), float(r.get("close", 0)),
                 float(r.get("volume", 0)), "qfq"))
        store.conn.commit()
        print(f"OK {len(df)}条")
    except Exception as e:
        print(f"跳过 (API不可用: {str(e)[:120]})")


def fetch_us_financials(store, code):
    """美股三大表 (东方财富 stock_financial_us_report_em) + 指标 + 分红"""
    # 三大表 — 统一使用 stock_financial_us_report_em, 通过 symbol 参数切换
    for table, sym in [("income", "综合损益表"),
                       ("balance", "资产负债表"),
                       ("cashflow", "现金流量表")]:
        print(f"  [us_{table}] ", end="", flush=True)
        try:
            df = ak.stock_financial_us_report_em(stock=code, symbol=sym, indicator="年报")
        except Exception as e:
            print(f"跳过 (API不可用: {str(e)[:60]})")
            continue
        if df is None or df.empty:
            print("空")
            continue
        # 东方财富 US API 返回 ITEM_NAME, 需重命名为 STD_ITEM_NAME 以兼容 upsert_financials
        if "ITEM_NAME" in df.columns and "STD_ITEM_NAME" not in df.columns:
            df = df.rename(columns={"ITEM_NAME": "STD_ITEM_NAME"})
            # 同时保存原始 ITEM_NAME 用于 US→标准名映射
            df["ITEM_NAME"] = df["STD_ITEM_NAME"]
        # 写入前先映射 US 项目名 → 标准 VL 项目名 (作为额外行)
        import pandas as _pd
        # 统一将 row 转为 dict 避免 Series/dict 混合导致 DataFrame 构建失败
        mapped_rows = [dict(row) for _, row in df.iterrows()]
        for row_dict in mapped_rows:
            us_name = str(row_dict.get("STD_ITEM_NAME", ""))
            std_name = _US_FINANCIAL_ITEM_MAP.get(us_name)
            if std_name and std_name != us_name:
                mapped_row = dict(row_dict)
                mapped_row["STD_ITEM_NAME"] = std_name
                mapped_rows.append(mapped_row)
        # 美股资产负债表: US GAAP 无直接"总权益"字段, 需从 总资产-总负债 计算
        if table == "balance":
            # 按 REPORT_DATE 分组计算
            from collections import defaultdict
            rd_groups = defaultdict(dict)
            for row_dict in mapped_rows:
                rd = str(row_dict.get("REPORT_DATE", ""))
                name = str(row_dict.get("STD_ITEM_NAME", ""))
                amt = float(row_dict.get("AMOUNT", 0) or 0)
                rd_groups[rd][name] = amt
            for rd, items in rd_groups.items():
                ta = items.get("总资产", 0)
                tl = items.get("总负债", 0)
                if ta and tl:
                    total_eq = ta - tl
                    if abs(total_eq) > 0:
                        # 使用第一个该日期的 row 作为模板
                        template = next((r for r in mapped_rows if str(r.get("REPORT_DATE", "")) == rd), {})
                        new_row = {
                            "SECUCODE": template.get("SECUCODE", ""),
                            "SECURITY_CODE": template.get("SECURITY_CODE", code),
                            "SECURITY_NAME_ABBR": template.get("SECURITY_NAME_ABBR", ""),
                            "REPORT_DATE": rd,
                            "REPORT_TYPE": template.get("REPORT_TYPE", "年报"),
                            "REPORT": template.get("REPORT", ""),
                            "STD_ITEM_CODE": "calc",
                            "AMOUNT": total_eq,
                            "STD_ITEM_NAME": "总权益",
                            "ITEM_NAME": "总权益",
                        }
                        mapped_rows.append(new_row)
                        new_row2 = dict(new_row)
                        new_row2["STD_ITEM_NAME"] = "股东权益"
                        mapped_rows.append(new_row2)
        df_mapped = _pd.DataFrame(mapped_rows)
        store.upsert_financials(table, df_mapped)
        dates = df["REPORT_DATE"].apply(lambda x: str(x)[:10]).unique()
        n_annual = sum(1 for d in dates if any(
            d.endswith(suffix) for suffix in ("12-31", "01-31", "01-25", "01-26", "01-27", "01-28", "01-29", "01-30")
        ))
        print(f"OK {len(df_mapped)}行 ({n_annual}年报)")

        # 额外拉取 income 单季报 (用于填充 QUARTERLY 区域)
        if table == "income":
            print("  [us_income_q] ", end="", flush=True)
            try:
                df_q = ak.stock_financial_us_report_em(stock=code, symbol="综合损益表", indicator="单季报")
            except Exception as e:
                print(f"跳过 ({str(e)[:60]})")
                df_q = None
            if df_q is not None and not df_q.empty:
                if "ITEM_NAME" in df_q.columns and "STD_ITEM_NAME" not in df_q.columns:
                    df_q = df_q.rename(columns={"ITEM_NAME": "STD_ITEM_NAME"})
                store.upsert_financials("income", df_q)
                print(f"OK {len(df_q)}行 (单季)")
            else:
                print("空")

    # 关键指标 (stock_financial_us_analysis_indicator_em)
    print("  [us_indicators] ", end="", flush=True)
    try:
        df = ak.stock_financial_us_analysis_indicator_em(symbol=code, indicator="年报")
        if df is not None and len(df) > 0:
            for _, row in df.iterrows():
                rd = str(row.get("REPORT_DATE", "")).split(" ")[0]
                items = {}
                # 映射 US 英文列名 → 标准 VL 指标名
                _US_INDICATOR_MAP = {
                    "OPERATE_INCOME": "OPERATE_INCOME",
                    "PARENT_HOLDER_NETPROFIT": "HOLDER_PROFIT",
                    "BASIC_EPS": "BASIC_EPS",
                    "DILUTED_EPS": "DILUTED_EPS",
                    "ROE_AVG": "ROE_AVG",
                    "ROA": "ROA",
                    "GROSS_PROFIT_RATIO": "GROSS_MARGIN",
                    "NET_PROFIT_RATIO": "NET_PROFIT_RATIO",
                    "DEBT_ASSET_RATIO": "DEBT_ASSET_RATIO",
                    "CURRENT_RATIO": "CURRENT_RATIO",
                    "GROSS_PROFIT": "GROSS_PROFIT",
                    "EQUITY_RATIO": "EQUITY_RATIO",
                }
                for us_col, vl_key in _US_INDICATOR_MAP.items():
                    val = row.get(us_col)
                    if val is not None and pd.notna(val):
                        try:
                            items[vl_key] = float(val)
                        except (ValueError, TypeError):
                            pass
                if items:
                    store.upsert_indicators(rd, items)
            print(f"OK {len(df)}行")
            # 保存币种信息到 meta
            if len(df) > 0:
                raw_currency = str(df.iloc[0].get("CURRENCY", ""))
                if raw_currency:
                    store.set_meta("currency", raw_currency)
                    # 同时设置 price_ccy (engine.py 生成报告用)
                    store.set_meta("price_ccy", raw_currency)
        else:
            print("空")
    except Exception as e:
        print(f"跳过 (API不可用: {str(e)[:60]})")

    # 分红 — AKShare 无专用美股分红接口, 从 income 表提取 DPS 或跳过
    print("  [us_dividend] ", end="", flush=True)
    try:
        # 从综合损益表中读 "每股股息-普通股" 作为 DPS
        rows = store.conn.execute(
            "SELECT report_date, amount FROM income WHERE item_name=? "
            "OR item_name=? ORDER BY report_date",
            ("每股股息-普通股", "每股股息")).fetchall()
        if rows:
            for rd, dps_raw in rows:
                fy = rd[:4] if rd and rd[0].isdigit() else ""
                if not fy:
                    continue
                dps = float(dps_raw) if dps_raw else 0
                store.conn.execute(
                    "INSERT OR REPLACE INTO dividend VALUES (?,?,?,?,?,?,?)",
                    (fy, dps, 0.0, "", "", 0.0,
                     f"US DPS from income statement ({rd})"))
            store.conn.commit()
            print(f"OK {len(rows)}条 (从损益表提取)")
        else:
            print("空 (无法获取分红数据)")
    except Exception as e:
        print(f"跳过 (API不可用: {str(e)[:60]})")


def _read_fx_rate(date_str):
    """读取 HKD/CNY 汇率, 返回 1 HKD = ? CNY, 失败返回 None"""
    fx_db = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "fx_rates.db")
    if not os.path.exists(fx_db):
        return None
    try:
        conn = sqlite3.connect(fx_db)
        row = conn.execute("SELECT hkd_cny FROM daily_rates WHERE date=?", (date_str,)).fetchone()
        if not row:
            row = conn.execute(
                "SELECT hkd_cny FROM daily_rates WHERE date<=? ORDER BY date DESC LIMIT 1",
                (date_str,)).fetchone()
        conn.close()
        return row[0] / 100.0 if row else None
    except Exception:
        return None


# ============================================================
# 汇率数据 (HKD/CNY)
# ============================================================
def fetch_fx_rates():
    """抓取 HKD/CNY 汇率存入 data/fx_rates.db
    DB 表: daily_rates (date TEXT PRIMARY KEY, hkd_cny REAL)
    hkd_cny 存储 100 HKD = ? CNY, 使用时 ÷100
    用途: H股价格(HKD)→报表货币(CNY)换算
    数据源: 外汇管理局中间价 (currency_boc_safe), 覆盖 1994 至今
    """
    import os as _os
    db_path = _os.path.join(config.DATA_DIR, "fx_rates.db")
    print("  [fx_rates] ", end="", flush=True)
    try:
        df = ak.currency_boc_safe()
        if df is None or df.empty or "港元" not in df.columns:
            print("未找到港元汇率列")
            return
        conn = sqlite3.connect(db_path)
        conn.execute(
            "CREATE TABLE IF NOT EXISTS daily_rates (date TEXT PRIMARY KEY, hkd_cny REAL)")
        count = 0
        for _, row in df.iterrows():
            date_str = str(row["日期"])[:10]
            rate = row["港元"]
            if pd.isna(rate) or rate <= 0:
                continue
            conn.execute(
                "INSERT OR REPLACE INTO daily_rates VALUES (?, ?)",
                (date_str, float(rate)))
            count += 1
        conn.commit()
        conn.close()
        latest = df.iloc[-1]
        rate_latest = float(latest["港元"])
        print(f"OK {count}条 (最新 {str(latest['日期'])[:10]}: 100HKD={rate_latest}CNY, 1HKD≈{round(rate_latest/100,4)}CNY)")
    except Exception as e:
        print(f"跳过 (API不可用: {str(e)[:60]})")

# ============================================================
# 主函数
# ============================================================
import pandas as pd

def fetch(code=None):
    code = code or config.ACTIVE_STOCK
    stock = config.STOCKS[code]
    market = stock["market"]
    print(f"\n{'='*50}")
    print(f"开始拉取: {stock['name']} ({code}) [{market}]")
    print(f"SQLite: {config.db_path(code)}")
    print(f"PDF: {config.pdf_dir(code)}")
    print(f"{'='*50}\n")

    store = Store(code)

    try:
        if market == "hk":
            # 港股
            fetch_fx_rates()           # 抓取 HKD/CNY 汇率 (供引擎换算)
            time.sleep(0.3)
            fetch_spot_hk(store, code)
            time.sleep(0.5)
            fetch_kline_hk(store, code)
            time.sleep(0.5)
            fetch_hk_financials(store, code)
        elif market == "us":
            # 美股
            fetch_spot_us(store, code)
            time.sleep(0.5)
            fetch_kline_us(store, code)
            time.sleep(0.5)
            fetch_us_financials(store, code)
        else:
            # A股
            pfx = stock.get("pfx", "sh")
            fetch_spot_cn(store, code, pfx)
            time.sleep(1)
            fetch_kline_cn(store, code, pfx)
            time.sleep(1)
            fetch_cn_financials(store, code)

        store.set_meta("last_fetch", str(pd.Timestamp.now()))
        store.set_meta("last_fetch_date", pd.Timestamp.now().strftime("%Y-%m-%d"))
        store.set_meta("code", code)
        store.set_meta("market", market)

        print(f"\n{'='*50}")
        print(f"拉取完成! 数据已存入 {config.db_path(code)}")
        print(f"{'='*50}")
    finally:
        store.close()

if __name__ == "__main__":
    code = sys.argv[1] if len(sys.argv) > 1 else None
    fetch(code)
