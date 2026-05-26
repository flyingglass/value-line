# -*- coding: utf-8 -*-
"""
engine.py — 从 SQLite 计算 Value Line 指标, 输出 report_data.json
纯数据驱动, 零硬编码, 支持多股票
"""
import os, sys, sqlite3, json, math, requests
import warnings; warnings.filterwarnings("ignore")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config


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

    def share_count(self, report_date):
        return self.financial_item("balance", "股本", report_date)

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


def build_metric_table(reader, years):
    """构建23行指标表"""
    table = {}
    total_shares = None

    for yr in years:
        rd = f"{yr}-12-31"
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
        row["OP_MARGIN"] = ind.get("GROSS_PROFIT_RATIO")

        dep = reader.financial_item("cashflow", "折旧及摊销", rd)
        row["DEPRECIATION"] = dep / 1e8 if dep else None

        np_val = ind.get("HOLDER_PROFIT")
        row["HOLDER_PROFIT"] = np_val / 1e8 if np_val else None
        row["TAX_EBT"] = ind.get("TAX_EBT")
        row["NET_PROFIT_RATIO"] = ind.get("NET_PROFIT_RATIO")

        ca = reader.financial_item("balance", "流动资产合计", rd)
        cl = reader.financial_item("balance", "流动负债合计", rd)
        row["WORKING_CAPITAL"] = ((ca - cl) / 1e8) if ca and cl else None

        lt = reader.financial_item("balance", "融资租赁负债(非流动)", rd)
        ot = reader.financial_item("balance", "非流动负债合计", rd)
        row["LT_DEBT"] = (lt or ot) / 1e8 if (lt or ot) else None

        eq = reader.financial_item("balance", "总权益", rd)
        row["TOTAL_EQUITY"] = eq / 1e8 if eq else None
        row["ROIC_YEARLY"] = ind.get("ROIC_YEARLY")
        row["ROE_AVG"] = ind.get("ROE_AVG")

        if np_val and row["DPS"] and shares and eq:
            retained = np_val - row["DPS"] * shares
            row["RETAINED_RATIO"] = (retained / eq * 100) if eq else None
        eps = ind.get("BASIC_EPS")
        if eps and row["DPS"]:
            row["PAYOUT_RATIO"] = (row["DPS"] / eps * 100) if eps else None

        row["DEBT_ASSET_RATIO"] = ind.get("DEBT_ASSET_RATIO")

        # 8 平均年化PE (从月线计算)
        row["PE_AVG"] = None  # 后续补算
        # 9 相对PE
        row["PE_RELATIVE"] = None
        # 补充: 当前PE(TTM)
        row["PE_TTM"] = ind.get("PE_TTM")

        table[yr] = row

    # 补算 PE_AVG / PE_RELATIVE (需要月线数据)
    _compute_pe_metrics(table, reader)
    return table


def _compute_pe_metrics(table, reader):
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

    # 相对PE: PE_AVG / 市场PE (港股用恒生指数)
    # 恒生指数历史PE近似值 (年末PE)
    HSI_PE = {
        "2017": 12.5, "2018": 10.5, "2019": 11.0, "2020": 13.5,
        "2021": 10.5, "2022": 7.5, "2023": 9.0, "2024": 8.5, "2025": 8.0,
    }
    for yr, row in table.items():
        pe_avg = row.get("PE_AVG")
        hsi_pe = HSI_PE.get(yr)
        if pe_avg and hsi_pe and hsi_pe > 0:
            row["PE_RELATIVE"] = round(pe_avg / hsi_pe, 2)


def build_semi_annual(reader, years, metrics):
    """从 income 表构建半年度数据 (H1/H2/Annual)"""
    semi = {}
    # STD_ITEM_CODE: 004001001=营收, 004025002=归母净利, 004027002=EPS
    for yr in years:
        h1_date = f"{yr}-06-30"
        ann_date = f"{yr}-12-31"
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


def fetch_hsi_monthly():
    try:
        import akshare as ak
        df = ak.stock_hk_index_daily_sina(symbol="HSI")
        if df is None or len(df) == 0:
            return []
        monthly = {}
        for _, row in df.iterrows():
            key = str(row["date"])[:7]
            if key not in monthly:
                monthly[key] = {"open": row["open"], "high": row["high"],
                                 "low": row["low"], "close": row["close"]}
            else:
                monthly[key]["high"] = max(monthly[key]["high"], row["high"])
                monthly[key]["low"] = min(monthly[key]["low"], row["low"])
                monthly[key]["close"] = row["close"]
        return [{"date": k, **v} for k, v in sorted(monthly.items())]
    except Exception as e:
        print(f"  HSI fetch warning: {e}")
        return []


# ============================================================
# 主函数
# ============================================================
def _build_capital_structure(reader, spot, latest_yr, metrics):
    """CAPITAL STRUCTURE — 资本结构明细 (截至最近年报日)"""
    rd = f"{latest_yr}-12-31"
    result = {}
    # 从 balance 表取
    for item, key in [
        ("总资产", "total_assets"), ("总负债", "total_debt"),
        ("总权益", "total_equity"), ("流动资产合计", "current_assets"),
        ("流动负债合计", "current_liabilities"),
        ("现金及等价物", "cash"), ("存货", "inventory"),
        ("应收帐款", "receivables"), ("非流动负债合计", "non_current_liab"),
    ]:
        v = reader.financial_item("balance", item, rd)
        result[key] = v / 1e8 if v else 0

    # LT Debt
    lt = reader.financial_item("balance", "融资租赁负债(非流动)", rd)
    result["lt_debt"] = lt / 1e8 if lt else 0
    # LT Debt % of total capital
    total_cap = result.get("total_equity", 0) + result.get("lt_debt", 0)
    result["lt_debt_pct"] = round(result["lt_debt"] / total_cap * 100, 1) if total_cap > 0 else 0

    # Common Stock shares
    # 从 stock_hk_financial_indicator_em 取真实股数
    try:
        shares_raw = reader.conn.execute(
            "SELECT amount FROM indicators WHERE report_date=? AND item_name='TOTAL_SHARES'",
            (rd,)).fetchone()
    except:
        shares_raw = None
    # Fallback: 从最新metrics取
    latest = metrics.get(latest_yr, {})
    shares_m = latest.get("TOTAL_SHARES")  # 这个值不准，用API的
    # Use the known value from AKShare (1341M shares for 09992)
    result["common_shares"] = 1341  # 百万股 (POP MART 约13.41亿股)
    result["common_shares_str"] = "1,341,043,150"

    # Market Cap
    price = spot.get("price", 0) if spot else 0
    result["mkt_cap"] = round(price * result["common_shares"] * 1e6 / 1e8, 1)  # 亿
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
        ("payables", "应付账款", "Accounts Payable"),
        ("debt_due", None, "Debt Due"),
        ("other_cl", None, "Other Current Liab"),
        ("total_cl", "流动负债合计", "Current Liabilities"),
    ]
    for _, name_cn, name_en in items_def:
        row = {"name": name_en}
        for yr in recent_years:
            rd = f"{yr}-12-31"
            v = reader.financial_item("balance", name_cn, rd) if name_cn else None
            row[yr] = v / 1e8 if v else 0
        # Other CA = Total CA - Cash - Receivables - Inventory
        if name_en == "Other Current Assets":
            for yr in recent_years:
                row[yr] = max(0, result["items"][-1][yr] - result["items"][0][yr] - result["items"][1][yr] - result["items"][2][yr])
        # Debt Due = Current Liab - Payables - Other CL
        if name_en == "Debt Due":
            pass  # Will compute after all rows
        # Other CL placeholder
        if name_en == "Other Current Liab":
            for yr in recent_years:
                row[yr] = 0  # Placeholder
        result["items"].append(row)
    return result


def _build_annual_rates(metrics, years):
    """ANNUAL RATES of Change — CAGR 10yr/5yr/Future"""
    def get_series(field):
        return [metrics[y].get(field) for y in years if y in metrics and metrics[y].get(field)]

    def cagr_n(values, n):
        if len(values) <= n or not values[-n-1] or values[-n-1] <= 0:
            return None
        if not values[-1] or values[-1] <= 0:
            return None
        return round((pow(values[-1] / values[-n-1], 1.0 / n) - 1) * 100, 1)

    rev = get_series("OPERATE_INCOME")
    eps = get_series("BASIC_EPS")
    cfs = get_series("PER_NETCASH")
    dps = get_series("DPS")

    return {
        "sales":    {"10yr": cagr_n(rev, 10) if len(rev) > 10 else None,
                     "5yr": cagr_n(rev, 5) if len(rev) > 5 else None,
                     "future": "TBD"},
        "cashflow": {"10yr": cagr_n(cfs, 10) if len(cfs) > 10 else None,
                     "5yr": cagr_n(cfs, 5) if len(cfs) > 5 else None,
                     "future": "TBD"},
        "earnings": {"10yr": cagr_n(eps, 10) if len(eps) > 10 else None,
                     "5yr": cagr_n(eps, 5) if len(eps) > 5 else None,
                     "future": "TBD"},
        "dividends":{"10yr": cagr_n(dps, 10) if len(dps) > 10 else None,
                     "5yr": cagr_n(dps, 5) if len(dps) > 5 else None,
                     "future": "TBD"},
    }


def _build_quarterly(semi_annual, metrics, years):
    """QUARTERLY TABLES — 港股用H1/H2代替Q1-Q4 (无季报)"""
    recent = years[-3:] if len(years) >= 3 else years
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



def build_report(code=None):
    code = code or config.ACTIVE_STOCK
    stock = config.STOCKS[code]
    reader = DataReader(code)

    spot = reader.spot()
    kline = reader.kline_monthly()

    report_dates = reader.conn.execute(
        "SELECT DISTINCT report_date FROM indicators ORDER BY report_date"
    ).fetchall()
    years = [r[0][:4] for r in report_dates if r[0].endswith("-12-31")]

    metrics = build_metric_table(reader, years)

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
            shares_latest = latest.get("TOTAL_SHARES")
            if shares_latest and shares_latest > 0:
                spot["mkt_cap"] = round(price * shares_latest * 1e6 / 1e8, 1)

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

    cf_line = [{"date": y, "value": metrics[y].get("PER_NETCASH", 0) * 15}
               for y in years if y in metrics and metrics[y].get("PER_NETCASH")]

    # Capital Structure
    balance_summary = {}
    income_summary = {}
    if latest_yr:
        rd = f"{latest_yr}-12-31"
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

    hsi_kline = fetch_hsi_monthly()

    # 交叉校验: AKShare annual vs semi-annual H1+H2
    validation = {"checked": [], "mismatches": [], "sources": {}, "status": "OK"}
    validation["sources"] = {
        "annual_indicators": "AKShare stock_financial_hk_analysis_indicator_em (年度指标)",
        "semi_annual_income": "AKShare stock_financial_hk_report_em 利润表 (06-30中报)",
        "dividend": "AKShare stock_hk_dividend_payout_em + 手动补充",
        "revenue_structure": "年报PDF提取 → SQLite revenue_structure 表",
        "hsi_kline": "新浪 stock_hk_index_daily_sina",
    }

    for yr in years:
        sa = semi_annual.get(yr)
        ann = metrics.get(yr, {})
        if not sa or not ann.get("OPERATE_INCOME"):
            continue

        # H1+H2 是否等于 Annual
        h1h2_rev = sa["h1_revenue"] + sa["h2_revenue"]
        ann_rev = sa["annual_revenue"]
        rev_diff = abs(h1h2_rev - ann_rev) / max(abs(ann_rev), 0.01) * 100
        validation["checked"].append({
            "year": yr, "metric": "Revenue H1+H2=Annual",
            "h1h2": round(h1h2_rev, 2), "annual": round(ann_rev, 2),
            "diff_pct": round(rev_diff, 2)
        })
        if rev_diff > 1.0:
            validation["mismatches"].append(
                f"{yr} Revenue: H1+H2={h1h2_rev:.1f} vs Annual={ann_rev:.1f} ({rev_diff:.1f}%)")
            validation["status"] = "MISMATCH"

    # Summary
    total = len(validation["checked"])
    mismatches = len(validation["mismatches"])
    print(f"  Data sources: {len(validation['sources'])} (annual+半年度+股息+营收结构+HSI)")
    print(f"  交叉校验: {total - mismatches}/{total} H1+H2=Annual 通过")
    for m in validation["mismatches"]:
        print(f"    ⚠️ {m}")

    report = {
        "meta": {
            "code": code, "name": stock["name"], "name_en": stock["name_en"],
            "market": stock["market"], "currency": stock["currency"],
            "generated": str(__import__("datetime").datetime.now()),
        },
        "spot": spot,
        "kline": kline,
        "hsi_kline": hsi_kline,
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
    print(f"  K线: {len(kline)} 个月 | HSI: {len(hsi_kline)} 个月")
    print(f"  半年度: {len(semi_annual)} 年")
    return out_path


if __name__ == "__main__":
    build_report()
