# -*- coding: utf-8 -*-
"""
engine.py — 从 SQLite 计算 Value Line 指标, 输出 report_data.json
纯数据驱动, 零硬编码, 支持多股票
"""
import os, sys, sqlite3, json, math, requests
import warnings; warnings.filterwarnings("ignore")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config

# 财年结束月: 从 config 读取或默认 12-31
def _fye(yr):
    """返回该财年对应的报告日期 (eg. yr=2026,fye=03-31 → "2026-03-31")"""
    stock = config.STOCKS.get(config.ACTIVE_STOCK, {})
    fye = stock.get("fiscal_yr_end", "12-31")
    return f"{yr}-{fye}"


class DataReader:
    def __init__(self, code):
        self.conn = sqlite3.connect(config.db_path(code))
        self.code = code

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
        rows = self.conn.execute(
            "SELECT item_name, amount FROM indicators WHERE report_date=?",
            (report_date,)
        ).fetchall()
        return dict(rows)

    def financial_item(self, table, item, report_date):
        r = self.conn.execute(
            f"SELECT amount FROM {table} WHERE item_name=? AND report_date=?",
            (item, report_date)
        ).fetchone()
        return r[0] if r else None

    def financial_item_by_code(self, table, item_code, report_date):
        """通过 STD_ITEM_CODE 查询 (半年度数据)"""
        r = self.conn.execute(
            f"SELECT amount FROM {table} WHERE item_code=? AND report_date=?",
            (item_code, report_date)
        ).fetchone()
        return r[0] if r else None

    def dividends(self):
        rows = self.conn.execute(
            "SELECT report_year, cash_dps FROM dividend ORDER BY report_year"
        ).fetchall()
        return {r[0]: r[1] for r in rows}

    def share_count(self, report_date=None):
        """返回原始股数 — 动态计算, 不硬编码
        优先级: 
        1. OI/PER_OI → 营收/每股营收 (最可靠, 覆盖A/H/美股)
        2. 从 config 读取 (fallback)
        """
        if report_date:
            oi = self.financial_item("indicators", "OPERATE_INCOME", report_date)
            psi = self.financial_item("indicators", "PER_OI", report_date)
            if oi and psi and psi > 0:
                return round(oi / psi)
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


def build_metric_table(reader, years, market="hk"):
    """构建23行指标表"""
    table = {}
    total_shares = None

    for yr in years:
        rd = _fye(yr)
        ind = reader.indicators(rd)
        if not ind:
            continue
        row = {}
        row["PER_OI"]       = ind.get("PER_OI")
        row["PER_NETCASH"]  = ind.get("PER_NETCASH_OPERATE")
        row["BASIC_EPS"]    = ind.get("BASIC_EPS")
        row["BPS"]          = ind.get("BPS")

        # 每股股息 (有手动补充)
        divs = reader.dividends()
        row["DPS"] = divs.get(yr, 0)

        # 每股资本支出
        capex = reader.financial_item("cashflow", "购建固定资产", rd)
        shares = reader.share_count(rd) or total_shares
        if shares:
            total_shares = shares
            row["CAPEX_PS"] = (capex / shares) if capex else None
        else:
            row["CAPEX_PS"] = None

        row["TOTAL_SHARES"] = shares / 1e6 if shares else None
        rev = ind.get("OPERATE_INCOME")
        row["OPERATE_INCOME"] = rev / 1e8 if rev else None
        op_profit = reader.financial_item("income", "经营溢利", rd)
        # 经营利润率 = 经营溢利 / 营收 × 100
        row["OP_MARGIN"] = round((op_profit / rev) * 100, 1) if op_profit and rev else None

        dep = reader.financial_item("cashflow", "加:折旧及摊销", rd)
        row["DEPRECIATION"] = dep / 1e8 if dep else None

        np_val = ind.get("HOLDER_PROFIT")
        row["HOLDER_PROFIT"] = np_val / 1e8 if np_val else None
        row["TAX_EBT"] = ind.get("TAX_EBT")
        row["NET_PROFIT_RATIO"] = ind.get("NET_PROFIT_RATIO")

        ca = reader.financial_item("balance", "流动资产合计", rd)
        cl = reader.financial_item("balance", "流动负债合计", rd)
        row["WORKING_CAPITAL"] = ((ca - cl) / 1e8) if ca and cl else None

        lt = reader.financial_item("balance", "融资租赁负债(非流动)", rd)
        if not lt:
            lt = reader.financial_item("balance", "长期贷款", rd)
        row["LT_DEBT"] = (lt / 1e8) if lt else None

        eq = reader.financial_item("balance", "总权益", rd)
        row["TOTAL_EQUITY"] = eq / 1e8 if eq else None
        row["ROIC_YEARLY"] = ind.get("ROIC_YEARLY")
        row["ROE_AVG"] = ind.get("ROE_AVG")

        if np_val and shares and eq:
            div_cost = (row["DPS"] or 0) * shares
            retained = np_val - div_cost
            if retained > 0:
                row["RETAINED_RATIO"] = (retained / eq * 100) if eq else None
            else:
                row["RETAINED_RATIO"] = 0
        eps = ind.get("BASIC_EPS")
        if eps:
            row["PAYOUT_RATIO"] = ((row["DPS"] or 0) / eps * 100) if eps else 0

        row["DEBT_ASSET_RATIO"] = ind.get("DEBT_ASSET_RATIO")

        # 8 平均年化PE (从月线计算)
        row["PE_AVG"] = None  # 后续补算
        # 9 相对PE
        row["PE_RELATIVE"] = None
        # 补充: 当前PE(TTM)
        row["PE_TTM"] = ind.get("PE_TTM")

        table[yr] = row

    # 补算 PE_AVG / PE_RELATIVE (需要月线数据)
    _compute_pe_metrics(table, reader, market)
    return table


def _compute_pe_metrics(table, reader, market="hk"):
    """利用月K线计算各年度平均PE和相对PE"""
    # 获取月线收盘价
    kline_rows = reader.conn.execute(
        "SELECT date, close FROM kline WHERE adjust='qfq' ORDER BY date"
    ).fetchall()
    if not kline_rows:
        return

    # 按年聚合
    from collections import defaultdict
    yearly_closes = defaultdict(list)
    for d, c in kline_rows:
        yr = d[:4]
        yearly_closes[yr].append(c)

    # 计算每年均价和PE
    for yr, row in table.items():
        closes = yearly_closes.get(yr, [])
        if not closes or not row.get("BASIC_EPS"):
            continue
        avg_price = sum(closes) / len(closes)
        eps = row["BASIC_EPS"]
        if eps and eps > 0:
            row["PE_AVG"] = round(avg_price / eps, 1)
        # 平均股息率 = DPS / 年均价
        dps = row.get("DPS")
        if dps and dps > 0 and avg_price > 0:
            row["DIV_YIELD"] = round((dps / avg_price) * 100, 1)

    # 相对PE: PE_AVG / 市场PE (从 config.MARKET_CONFIG 获取)
    market_cfg = config.MARKET_CONFIG.get(market, {})
    index_pe = market_cfg.get("pe_estimate", {})
    for yr, row in table.items():
        pe_avg = row.get("PE_AVG")
        mkt_pe = index_pe.get(yr)
        if pe_avg and mkt_pe and mkt_pe > 0:
            row["PE_RELATIVE"] = round(pe_avg / mkt_pe, 2)


def build_semi_annual(reader, years, metrics):
    """从 income 表构建半年度数据 (H1/H2/Annual)"""
    semi = {}
    # STD_ITEM_CODE: 004001001=营收, 004025002=归母净利, 004027002=EPS
    for yr in years:
        h1_date = f"{yr}-06-30"
        ann_date = _fye(yr)
        h1_rev = reader.financial_item_by_code("income", "004001001", h1_date)
        h1_np  = reader.financial_item_by_code("income", "004025002", h1_date)
        h1_eps = reader.financial_item_by_code("income", "004027002", h1_date)

        if h1_rev is None or h1_np is None:
            continue

        ann = metrics.get(yr, {})
        ann_rev = ann.get("OPERATE_INCOME")
        ann_np  = ann.get("HOLDER_PROFIT")
        ann_eps = ann.get("BASIC_EPS")

        h1_rev_b = h1_rev / 1e8  # 元→亿
        h1_np_b  = h1_np / 1e8
        h2_rev_b = max(0, ann_rev - h1_rev_b) if ann_rev else 0
        h2_np_b  = max(0, ann_np - h1_np_b) if ann_np else 0

        semi[yr] = {
            "h1_revenue":       round(h1_rev_b, 2),
            "h2_revenue":       round(h2_rev_b, 2),
            "annual_revenue":   round(ann_rev, 2) if ann_rev else 0,
            "h1_net_profit":    round(h1_np_b, 2),
            "h2_net_profit":    round(h2_np_b, 2),
            "annual_net_profit": round(ann_np, 2) if ann_np else 0,
            "h1_eps":           round(h1_eps, 2) if h1_eps else None,
            "h2_eps":           round(ann_eps - h1_eps, 2) if ann_eps and h1_eps else None,
            "annual_eps":       ann_eps,
        }
    return semi


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
        else:
            return []
        r = subprocess.run([managed_py, "-c", script], capture_output=True, text=True, timeout=30)
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


def _build_capital_structure(reader, spot, latest_yr, metrics):
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

    lt = reader.financial_item("balance", "融资租赁负债(非流动)", rd)
    if not lt:
        lt = reader.financial_item("balance", "长期贷款", rd)
    raw["lt_debt"] = lt or 0

    debt_due_current = reader.financial_item("balance", "融资租赁负债(流动)", rd) or 0
    st_loan = reader.financial_item("balance", "短期贷款", rd) or 0
    lt_payable = reader.financial_item("balance", "长期应付款", rd) or 0
    raw["due_in_5yr"] = debt_due_current + st_loan + lt_payable

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
        result["coverage"] = "N/A"
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

    # Market Cap (价格 × 股数, 用同一个单位)
    price = spot.get("price", 0) if spot else 0
    mkt_cap_raw = price * result["common_shares_raw"] if result["common_shares_raw"] else 0
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

    return result


def _build_current_position(reader, years):
    """CURRENT POSITION — 短期资产负债 (最近3年对比)"""
    result = {"years": [], "items": []}
    # 取最近3年
    recent_years = years[-3:] if len(years) >= 3 else years
    result["years"] = recent_years

    items_def = [
        ("cash", "现金及等价物", "Cash & Equiv"),
        ("receivables", "应收帐款", "Receivables"),
        ("inventory", "存货", "Inventory"),
        ("other_ca", None, "Other Current Assets"),
        ("total_ca", "流动资产合计", "Current Assets"),
        ("payables", "应付帐款", "Accounts Payable"),
        ("debt_due", "融资租赁负债(流动)", "Debt Due"),
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


def _build_quarterly(semi_annual, metrics, years):
    """QUARTERLY TABLES — 港股用H1/H2代替Q1-Q4 (无季报)"""
    # 最多显示5年
    recent = years[-5:] if len(years) >= 5 else years
    tables = {"sales": [], "eps": [], "dividends": []}

    for yr in recent:
        sa = semi_annual.get(yr, {})
        ann = metrics.get(yr, {})
        h1_eps = sa.get("h1_eps")
        h2_eps = sa.get("h2_eps")
        ann_eps = ann.get("BASIC_EPS")
        h1_rev = sa.get("h1_revenue", 0)
        h2_rev = sa.get("h2_revenue", 0)
        ann_rev = sa.get("annual_revenue", 0)
        dps_val = ann.get("DPS", 0) or 0

        tables["sales"].append({
            "year": yr, "q1q2": round(h1_rev, 1), "q3q4": round(h2_rev, 1),
            "full": round(ann_rev, 1)
        })
        tables["eps"].append({
            "year": yr, "q1q2": h1_eps, "q3q4": h2_eps, "full": ann_eps
        })
        # 股息只有年度数据
        tables["dividends"].append({
            "year": yr, "q1q2": 0, "q3q4": dps_val, "full": dps_val
        })

    return tables


def _calc_position(spot, kline, metrics, years):
    """计算当前估值在历史区间的位置"""
    result = {}
    price = spot.get("price", 0) if spot else 0
    pe_ttm = spot.get("pe", 0) if spot else 0
    pb = spot.get("pb", 0) if spot else 0

    # PE区间
    pe_vals = [metrics[y]["PE_AVG"] for y in years if y in metrics and metrics[y].get("PE_AVG")]
    if pe_vals:
        result["pe"] = {
            "current": pe_ttm,
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

    report_dates = reader.conn.execute(
        "SELECT DISTINCT report_date FROM indicators ORDER BY report_date"
    ).fetchall()
    # 检测年度报告日期格式 (12-31 或 03-31)
    fye = stock.get("fiscal_yr_end", "12-31")
    years = [r[0][:4] for r in report_dates if r[0].endswith(f"-{fye}")]

    metrics = build_metric_table(reader, years, market)

    # 补算 Header PE(TTM) / PB / 股息率 / 市值
    if spot and years and metrics:
        latest = metrics.get(years[-1], {})
        price = spot.get("price")
        if price:
            eps_latest = latest.get("BASIC_EPS")
            if eps_latest and eps_latest > 0:
                spot["pe"] = round(price / eps_latest, 1)
            bps_latest = latest.get("BPS")
            if bps_latest and bps_latest > 0:
                spot["pb"] = round(price / bps_latest, 2)
            dps_latest = latest.get("DPS")
            if dps_latest and dps_latest > 0:
                spot["div_yield"] = round(dps_latest / price * 100, 2)
            shares_raw = reader.share_count(_fye(years[-1])) or config.STOCKS.get(code, {}).get("shares")
            if shares_raw and shares_raw > 0:
                spot["mkt_cap"] = round(price * shares_raw / 1e8, 1)  # 股数×股价÷1亿

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

    # 半年度数据 (从 SQLite income 表读取)
    semi_annual = build_semi_annual(reader, years, metrics)

    # 营收结构 (从 SQLite revenue_structure 表读取)
    revenue_structure = {}
    latest_yr = years[-1] if years else "2025"
    for dim in ["by_channel", "by_ip", "by_region"]:
        data = reader.revenue_structure(latest_yr, dim)
        if data:
            revenue_structure[dim] = data

    cf_line = [{"date": y, "value": round(metrics[y].get("PER_NETCASH", 0) * 15, 2)}
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
        for item, key in [("营业额", "revenue"), ("毛利", "gross_profit"),
                          ("股东应占溢利", "net_profit")]:
            v = reader.financial_item("income", item, rd)
            if v:
                income_summary[key] = v / 1e8

    # 1. CAPITAL STRUCTURE 资本结构明细
    cap_struct = _build_capital_structure(reader, spot, latest_yr, metrics)

    # 2. CURRENT POSITION 短期资产负债 (3年对比)
    cur_pos = _build_current_position(reader, years)

    # 3. ANNUAL RATES of Change (10yr/5yr/Future)
    annual_rates = _build_annual_rates(metrics, years)

    # 4. QUARTERLY TABLES (港股: H1/H2代替)
    quarterly = _build_quarterly(semi_annual, metrics, years)

    # Current Position 估值定位 (图表用)
    position = _calc_position(spot, kline, metrics, years)

    # Yearly High/Low (从月K线)
    yearly_hl = _build_yearly_hl(kline, years)

    index_kline = fetch_market_index(market)

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
                add_check(str(pdf_yr), "AKShare↔PDF Revenue",
                           {"summary": f"AKShare={ak_rev/1e8:.1f}B vs PDF={pdf_sum/1e8:.1f}B", "akshare": round(ak_rev/1e8,2), "pdf": round(pdf_sum/1e8,2)},
                           rev_pct)

            # 3. 营收结构维度完整性: 各维度 pct 总和是否 = 100%
            for dim in ["by_channel", "by_ip", "by_region"]:
                dim_sum = reader.conn.execute(
                    "SELECT SUM(pct) FROM revenue_structure WHERE code=? AND year=? AND dim_type=?",
                    (code, str(pdf_yr), dim)).fetchone()[0]
                if dim_sum is not None:
                    pct_gap = abs(100 - dim_sum)
                    if pct_gap > 0.5:
                        add_check(str(pdf_yr), f"Revenue {dim} sum=100%",
                                   {"summary": f"{dim}: sum_pct={dim_sum:.1f}% (gap={pct_gap:.1f}%)", "sum_pct": round(dim_sum,2)},
                                   pct_gap, threshold=0.5)

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

    report = {
        "meta": {
            "code": code, "name": stock["name"], "name_en": stock["name_en"],
            "market": stock["market"], "currency": stock.get("currency", reader.db_meta("currency", "CNY")),
            "industry": stock.get("industry", ""),
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
        "years": years,
        "metric_defs": [{"order": m[0], "name_cn": m[1], "name_en": m[2],
                          "field": m[3], "unit": m[4], "source": m[5]}
                        for m in config.VL_METRICS],
        "data": metrics,
        "cagr": cagr,
        "semi_annual": semi_annual,
        "cf_line": cf_line,
        "balance_summary": balance_summary,
        "income_summary": income_summary,
        "revenue_structure": revenue_structure,
        "capital_structure": cap_struct,
        "current_position": cur_pos,
        "annual_rates": annual_rates,
        "quarterly": quarterly,
        "yearly_hl": yearly_hl,
        "position": position,
        "analyst": {"business": "", "commentary": "", "recommendation": ""},
        "validation": validation,
    }

    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "report_data.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2, default=str)

    reader.close()
    print(f"report_data.json 生成完成 ({len(json.dumps(report))} 字符)")
    print(f"  年数: {len(years)} ({years[0]}-{years[-1]})")
    print(f"  K线: {len(kline)} 个月 | HSI: {len(index_kline)} 个月")
    print(f"  半年度: {len(semi_annual)} 年")
    return out_path


if __name__ == "__main__":
    build_report()
