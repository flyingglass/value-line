# -*- coding: utf-8 -*-
"""
fetch_us_westock.py — WeStock Data CLI → SQLite 美股数据拉取
替代 AKShare 美股路径，基于 westock-data skill 获取更完整的财务数据。

与 HK AKShare 对比：
  ✅ 新增：营收拆分 (BusinessDist + RegionDist) — AKShare 美股无此数据
  ✅ 新增：季度分红明细 (ex date / pay date / amount)
  ✅ 增强：利润表/资产负债表/现金流量表字段更完整（EBIT, EBITDA, FreeCF 等）
  ⚠️ 缺失：实时行情 quote 命令失败，用 kline 最新价 + profile 补齐
  ⚠️ 缺失：SEC 10-K PDF 年报下载 — 待后续实现，暂时用 business_commentary.py fallback

运行: python scripts/fetch_us_westock.py GOOGL
"""
import json, os, re, sqlite3, subprocess, sys, time
from datetime import date

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config

# WeStock Data CLI 命令
WESTOCK_CMD = "npx -y westock-data-clawhub@1.0.4"

# westock-data → engine.py 标准中文 item_name 映射
# engine.py 对美股优先读 indicators 表，income/balance/cashflow 为 fallback

# 利润表映射 (income)
INCOME_MAP = {
    "Sales":               ("营业额", 1),          # 总营收
    "Sales":               ("*营业总收入", 1),      # A-share 命名 (fallback)
    "GrossIncome":         ("毛利", 1),
    "Cogs":                ("营业成本", 1),
    "Cogs":                ("其中：营业成本", 1),
    "EBIT":                ("经营溢利", 1),          # engine.py 主要查询名
    "EBIT":                ("三、营业利润", 1),
    "EBIT":                ("营业利润", 1),
    "NetIncome":           ("股东应占溢利", 1),      # GOOGL 无少数股东权益
    "NetIncome":           ("*归属于母公司所有者的净利润", 1),
    "BasicEPS":            ("每股基本盈利", 1),
    "BasicEPS":            ("（一）基本每股收益", 1),
    "DilutedEPS":          ("每股摊薄盈利", 1),
    "DilutedEPS":          ("（二）稀释每股收益", 1),
    "PretaxIncome":        ("除税前盈利", 1),
    "PretaxIncome":        ("四、利润总额", 1),
    "IncomeTax":           ("所得税", 1),
    "IncomeTax":           ("减：所得税费用", 1),
    "InterestExpense":     ("融资成本", 1),
    "InterestExpense":     ("其中：利息费用", 1),
    "SaleGeneralAdminExp": ("销售及管理费用", 1),
    "EBITDA":              ("EBITDA", 1),
    "SalesPs":             ("每股营收", 1),
}

# 资产负债表映射 (balance)
BALANCE_MAP = {
    "TotalAssets":              ("总资产", 1),
    "TotalLiabilities":         ("总负债", 1),
    "TotalEquity":              ("总权益", 1),
    "ShareHolderEquity":        ("股东权益", 1),
    "CommonStockEquity":        ("归属于母公司所有者权益", 1),
    "CurrentAssets":            ("流动资产合计", 1),
    "CurrentLiabilities":       ("流动负债合计", 1),
    "PPE":                      ("固定资产", 1),
    "IntangibleAssets":         ("无形资产", 1),
    "LongTermDebt":             ("长期贷款", 1),
    "ShortTermDebt":            ("短期贷款", 1),
    "AccountsPayable":          ("应付账款", 1),
    "ShortTermReceivable":      ("应收帐款", 1),
    "CashShortTermInvestment":  ("现金及等价物", 1),
    "Inventory":                ("存货", 1),
    "AdvancedInvestment":       ("长期投资", 1),
    "OtherAssets":              ("其他资产", 1),
    "OtherLiabilities":         ("其他负债", 1),
    "OtherCurrentAssets":       ("其他流动资产", 1),
    "OtherCurrentLiabilities":  ("其他流动负债", 1),
    "DeferredTaxAssets":        ("递延税项资产", 1),
    "TaxPayable":               ("应交税费", 1),
    "BPS":                      ("每股账面价值", 1),
    "CumMinorityInterest":      ("少数股东权益", 1),
}

# 现金流量表映射 (cashflow)
CASHFLOW_MAP = {
    "CFO":          ("经营活动产生的现金流量净额", 1),
    "CFI":          ("投资活动产生的现金流量净额", 1),
    "CFF":          ("融资活动产生的现金流量净额", 1),
    "Capex":        ("购建固定资产", 1),
    "DepCF":        ("加:折旧及摊销", 1),
    "FreeCF":       ("自由现金流", 1),
    "DivCF":        ("股息支付", 1),
    "NetIncomeCF":  ("净利润(CF口径)", 1),
    "StockChgCF":   ("股份回购", 1),
    "DebtCF":       ("债务变动", 1),
    "AcqBusiCF":    ("收购子公司", 1),
}

# westock-data finance 字段的单位 (除以该值得到原始单位)
# westock-data 返回的金额单位: 百万 (1e6)
UNIT_M = 1_000_000


def _run_westock(subcmd: str) -> str:
    """运行 westock-data CLI 命令，返回 stdout"""
    cmd = f"{WESTOCK_CMD} {subcmd}"
    result = subprocess.run(
        cmd, shell=True, capture_output=True, text=True, timeout=60,
        encoding="utf-8", errors="replace")
    if result.returncode != 0 and result.stderr:
        print(f"  [WARN] {subcmd[:60]} stderr: {result.stderr[:200]}")
    return result.stdout or ""


def _parse_markdown_table(text: str) -> list[dict]:
    """解析 westock-data 输出的 Markdown 表格 → dict 列表"""
    lines = text.strip().split("\n")
    # 找到表头行 (以 | 开头)
    header_idx = None
    for i, line in enumerate(lines):
        if line.strip().startswith("|") and not line.strip().startswith("|---"):
            # 检查下一行是否是分隔行
            if i + 1 < len(lines) and "---" in lines[i + 1]:
                header_idx = i
                break
    if header_idx is None:
        return []

    headers = [h.strip() for h in lines[header_idx].split("|")[1:-1]]
    rows = []
    for line in lines[header_idx + 2:]:
        line = line.strip()
        if not line.startswith("|"):
            break
        cells = [c.strip() for c in line.split("|")[1:-1]]
        if len(cells) != len(headers):
            continue
        row = {}
        for h, c in zip(headers, cells):
            row[h] = c
        rows.append(row)
    return rows


def _safe_float(val) -> float:
    """安全转换字符串为 float"""
    if val is None or val == "" or val == "-":
        return 0.0
    try:
        return float(str(val).replace(",", ""))
    except (ValueError, TypeError):
        return 0.0


def _write_income(store, code: str):
    """拉取利润表并写入 income 表"""
    print("  [us_income] ", end="", flush=True)
    out = _run_westock(f"finance us{code} --type income --num 20")
    rows = _parse_markdown_table(out)
    if not rows:
        print("空")
        return

    count = 0
    for row in rows:
        rd = row.get("EndDate", row.get("_date", ""))
        if not rd:
            continue
        for westock_key, (std_name, multiplier) in INCOME_MAP.items():
            val = row.get(westock_key)
            if val is None or val == "" or val == "-":
                continue
            amt = _safe_float(val)
            if amt == 0:
                continue
            # westock-data 金额为百万单位，转成元存储（与 AKShare 一致）
            store.conn.execute(
                "INSERT OR REPLACE INTO income VALUES (?,?,?,?)",
                (rd, std_name, amt * UNIT_M, f"westock:{westock_key}"))
            count += 1
    store.conn.commit()
    annual_dates = set(r.get("EndDate", "") for r in rows if r.get("EndDate", "").endswith("12-31"))
    print(f"OK {count}条 ({len(annual_dates)}年报)")


def _write_balance(store, code: str):
    """拉取资产负债表并写入 balance 表"""
    print("  [us_balance] ", end="", flush=True)
    out = _run_westock(f"finance us{code} --type balance --num 20")
    rows = _parse_markdown_table(out)
    if not rows:
        print("空")
        return

    count = 0
    for row in rows:
        rd = row.get("EndDate", row.get("_date", ""))
        if not rd:
            continue
        for westock_key, (std_name, multiplier) in BALANCE_MAP.items():
            val = row.get(westock_key)
            if val is None or val == "" or val == "-":
                continue
            amt = _safe_float(val)
            if amt == 0:
                continue
            store.conn.execute(
                "INSERT OR REPLACE INTO balance VALUES (?,?,?,?)",
                (rd, std_name, amt * UNIT_M, f"westock:{westock_key}"))
            count += 1

    # 营收拆分: BusinessDist + RegionDist (AKShare 美股无此数据!)
    for row in rows:
        rd = row.get("EndDate", row.get("_date", ""))
        if not rd:
            continue
        year = rd[:4]
        # 业务分部
        bd = row.get("BusinessDist", "")
        if bd:
            try:
                segments = json.loads(bd)
                for seg in segments:
                    store.conn.execute(
                        "INSERT OR REPLACE INTO revenue_structure VALUES (?,?,?,?,?,?)",
                        (code, year, "业务分部", str(seg.get("BusinessLabel", "")),
                         _safe_float(seg.get("BusinessSales", 0)) * UNIT_M,
                         _safe_float(seg.get("BusinessSalesRatio", 0))))
                    count += 1
            except (json.JSONDecodeError, TypeError):
                pass
        # 地区分部
        rd_region = row.get("RegionDist", "")
        if rd_region:
            try:
                segments = json.loads(rd_region)
                for seg in segments:
                    label = seg.get("RegionLabel", "")
                    sales = _safe_float(seg.get("RegionSales", 0))
                    ratio = _safe_float(seg.get("RegionSalesRatio", 0))
                    if sales > 0:
                        store.conn.execute(
                            "INSERT OR REPLACE INTO revenue_structure VALUES (?,?,?,?,?,?)",
                            (code, year, "地区分部", label, sales * UNIT_M, ratio))
                        count += 1
            except (json.JSONDecodeError, TypeError):
                pass
    store.conn.commit()
    annual_dates = set(r.get("EndDate", "") for r in rows if r.get("EndDate", "").endswith("12-31"))
    print(f"OK {count}条 ({len(annual_dates)}年报, 含营收拆分)")


def _write_cashflow(store, code: str):
    """拉取现金流量表并写入 cashflow 表"""
    print("  [us_cashflow] ", end="", flush=True)
    out = _run_westock(f"finance us{code} --type cashflow --num 20")
    rows = _parse_markdown_table(out)
    if not rows:
        print("空")
        return

    count = 0
    for row in rows:
        rd = row.get("EndDate", row.get("_date", ""))
        if not rd:
            continue
        for westock_key, (std_name, multiplier) in CASHFLOW_MAP.items():
            val = row.get(westock_key)
            if val is None or val == "" or val == "-":
                continue
            amt = _safe_float(val)
            if amt == 0:
                continue
            store.conn.execute(
                "INSERT OR REPLACE INTO cashflow VALUES (?,?,?,?)",
                (rd, std_name, amt * UNIT_M, f"westock:{westock_key}"))
            count += 1
    store.conn.commit()
    annual_dates = set(r.get("EndDate", "") for r in rows if r.get("EndDate", "").endswith("12-31"))
    print(f"OK {count}条 ({len(annual_dates)}年报)")


def _write_indicators(store, code: str):
    """从财务报表数据提取关键指标写入 indicators 表"""
    print("  [us_indicators] ", end="", flush=True)

    # 从 balance 表提取嵌入的指标 (ROE, ROA, CurrentRatio, BPS, GrossMargin 等)
    out_bal = _run_westock(f"finance us{code} --type balance --num 20")
    bal_rows = _parse_markdown_table(out_bal)

    out_inc = _run_westock(f"finance us{code} --type income --num 20")
    inc_rows = _parse_markdown_table(out_inc)

    # 按 EndDate 建立索引
    inc_by_date = {}
    for r in inc_rows:
        rd = r.get("EndDate", "")
        if rd:
            inc_by_date[rd] = r

    count = 0
    for row in bal_rows:
        rd = row.get("EndDate", row.get("_date", ""))
        if not rd:
            continue

        items = {}
        # 从资产负债表提取指标
        roe = _safe_float(row.get("ROE"))
        if roe: items["ROE_AVG"] = roe

        roa = _safe_float(row.get("ROA"))
        if roa: items["ROA"] = roa

        cr = _safe_float(row.get("CurrentRatio"))
        if cr: items["CURRENT_RATIO"] = cr

        bps = _safe_float(row.get("BPS"))
        if bps: items["BPS"] = bps

        lta = _safe_float(row.get("LiabilityToAsset"))
        if lta: items["DEBT_ASSET_RATIO"] = lta

        # 总权益 = ShareHolderEquity + CumMinorityInterest (百万 → 元)
        eq = _safe_float(row.get("ShareHolderEquity"))
        minority = _safe_float(row.get("CumMinorityInterest"))
        if eq: items["TOTAL_EQUITY"] = (eq + minority) * UNIT_M

        ta = _safe_float(row.get("TotalAssets"))
        if ta: items["TOTAL_ASSETS"] = ta * UNIT_M

        # 从利润表提取指标
        inc = inc_by_date.get(rd, {})
        sales = _safe_float(inc.get("Sales"))
        if sales: items["OPERATE_INCOME"] = sales * UNIT_M

        ni = _safe_float(inc.get("NetIncome"))
        if ni: items["HOLDER_PROFIT"] = ni * UNIT_M

        beps = _safe_float(inc.get("BasicEPS"))
        if beps: items["BASIC_EPS"] = beps

        deps = _safe_float(inc.get("DilutedEPS"))
        if deps: items["DILUTED_EPS"] = deps

        gm = _safe_float(inc.get("GrossMargin"))
        if gm: items["GROSS_MARGIN"] = gm

        nm = _safe_float(inc.get("NetMargin"))
        if nm: items["NET_PROFIT_RATIO"] = nm

        gp = _safe_float(inc.get("GrossIncome"))
        if gp: items["GROSS_PROFIT"] = gp * UNIT_M

        # 所得税率 = IncomeTax / PretaxIncome * 100
        tax = _safe_float(inc.get("IncomeTax"))
        pretax = _safe_float(inc.get("PretaxIncome"))
        if pretax > 0:
            items["TAX_EBT"] = round(tax / pretax * 100, 2)

        # 资产负债率反算 (DEBT_ASSET_RATIO 已在上面)
        # 权益比率
        if ta > 0 and eq > 0:
            items["EQUITY_RATIO"] = round((eq + minority) / ta * 100, 2)

        if items:
            store.upsert_indicators(rd, items)
            count += len(items)

    # 保存币种信息
    if inc_rows:
        currency = inc_rows[0].get("DisclosureCurrency", "USD")
        store.set_meta("currency", currency)
        store.set_meta("price_ccy", currency)

    print(f"OK {count}条指标")


def _write_dividend(store, code: str):
    """拉取分红数据写入 dividend 表 (westock-data 返回季度分红)"""
    print("  [us_dividend] ", end="", flush=True)
    out = _run_westock(f"dividend us{code} --years 10")
    rows = _parse_markdown_table(out)
    if not rows:
        # 回退: 从 income 表提取 cash_dps
        print("回退到 income 表提取...", end="", flush=True)
        inc_rows = store.conn.execute(
            "SELECT report_date, amount FROM income WHERE item_name IN ('每股股息', '每股股息-普通股') "
            "ORDER BY report_date").fetchall()
        count = 0
        for rd, dps_raw in inc_rows:
            fy = rd[:4] if rd and rd[0].isdigit() else ""
            if not fy:
                continue
            dps = float(dps_raw) if dps_raw else 0
            store.conn.execute(
                "INSERT OR REPLACE INTO dividend VALUES (?,?,?,?,?,?,?)",
                (fy, dps, 0.0, "", "", 0.0, f"US DPS from income ({rd})"))
            count += 1
        store.conn.commit()
        print(f"OK {count}条")
        return

    # 按年份汇总季度分红
    yearly = {}
    for row in rows:
        ex_date = row.get("exDivDate", "")
        if not ex_date:
            continue
        fy = ex_date[:4]
        dps = _safe_float(row.get("dividend"))
        if fy not in yearly:
            yearly[fy] = {"dps": 0.0, "ex_date": ex_date, "pay_date": row.get("payDate", ""),
                          "raw": row.get("dividendPlan", "")}
        yearly[fy]["dps"] += dps
        yearly[fy]["raw"] += f" | Q{row.get('dividendPlan','')}"
        # 取最早的ex_date作为年度标记
        if ex_date < yearly[fy]["ex_date"]:
            yearly[fy]["ex_date"] = ex_date

    count = 0
    for fy, data in sorted(yearly.items()):
        store.conn.execute(
            "INSERT OR REPLACE INTO dividend VALUES (?,?,?,?,?,?,?)",
            (fy, round(data["dps"], 4), 0.0,
             data["ex_date"], data["pay_date"], 0.0, data["raw"]))
        count += 1
    store.conn.commit()
    print(f"OK {count}条年度DPS (从季度汇总)")


def _write_kline(store, code: str):
    """拉取日线K线写入 kline 表"""
    print("  [us_kline] ", end="", flush=True)
    out = _run_westock(f"kline us{code} --period day --limit 2000")
    rows = _parse_markdown_table(out)
    if not rows:
        print("空")
        return

    store.conn.execute("DELETE FROM kline WHERE adjust='qfq'")
    count = 0
    for row in rows:
        d = row.get("date", "")
        if not d:
            continue
        store.conn.execute(
            "INSERT OR REPLACE INTO kline VALUES (?,?,?,?,?,?,?)",
            (d,
             _safe_float(row.get("open")),
             _safe_float(row.get("high")),
             _safe_float(row.get("low")),
             _safe_float(row.get("last")),   # westock-data 用 'last' = 收盘价
             _safe_float(row.get("volume")),
             "qfq"))
        count += 1
    store.conn.commit()
    print(f"OK {count}条")


def _write_spot(store, code: str):
    """写入实时行情 (westock-data quote 失败, 用 kline 最新 + profile 补齐)"""
    print("  [us_spot] ", end="", flush=True)

    # 从 kline 表取最新价格
    latest = store.conn.execute(
        "SELECT date, close FROM kline WHERE adjust='qfq' ORDER BY date DESC LIMIT 1").fetchone()
    if not latest:
        print("无K线数据")
        return
    latest_date, price = latest

    # 尝试从 profile 获取市值
    mkt_cap = 0.0
    try:
        out = _run_westock(f"profile us{code}")
        # profile 输出非表格格式, 尝试解析
        m = re.search(r'总市值[：:]\s*([\d,.]+)\s*([万亿美])?', out)
        if not m:
            m = re.search(r'Total\s*Market\s*Cap[：:]?\s*\$?([\d,.]+)\s*([TBM])?', out)
        if m:
            val = float(m.group(1).replace(",", ""))
            unit = m.group(2) if m.lastindex >= 2 else ""
            if unit and unit[0] in "Tt":
                val *= 1_000_000_000_000
            elif unit and unit[0] in "Bb":
                val *= 1_000_000_000
            elif unit and unit[0] in "Mm":
                val *= 1_000_000
            mkt_cap = val
    except Exception:
        pass

    # 估算 PE = 股价 / 最新年度 EPS
    pe = 0.0
    latest_eps = store.conn.execute(
        "SELECT amount FROM indicators WHERE item_name='BASIC_EPS' "
        "ORDER BY report_date DESC LIMIT 1").fetchone()
    if latest_eps and float(latest_eps[0]) > 0:
        pe = round(price / float(latest_eps[0]), 2)

    store.conn.execute("DELETE FROM spot")
    store.conn.execute(
        "INSERT INTO spot VALUES (?,?,?,?,?,?,?,?,?,?)",
        (str(date.today()), price, pe, 0.0, 0.0,  # price, pe, pb, div_yield
         mkt_cap, 0.0, 0.0, 0.0, 0.0))           # mkt_cap, chg, vol, high_52w, low_52w
    store.conn.commit()
    print(f"OK 股价={price} PE≈{pe}")


# ============================================================
# 主入口
# ============================================================
def fetch_us_westock(code: str):
    """WeStock Data → SQLite 美股完整数据拉取"""
    stock = config.STOCKS.get(code, {})
    if not stock:
        raise SystemExit(f"未找到标的: {code}")
    if stock.get("market") != "us":
        raise SystemExit(f"{code} 不是美股 (market={stock.get('market')})")

    print(f"\n{'='*50}")
    print(f"WeStock Data → SQLite: {stock['name']} ({code}) [US]")
    print(f"SQLite: {config.db_path(code)}")
    print(f"{'='*50}\n")

    db_path = config.db_path(code)
    conn = sqlite3.connect(db_path)
    # 初始化表结构 (复用 fetcher.Store 逻辑)
    c = conn
    c.execute("CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS spot (date TEXT, price REAL, pe REAL, pb REAL, div_yield REAL, mkt_cap REAL, change_pct REAL, volume REAL, high_52w REAL, low_52w REAL)")
    c.execute("CREATE TABLE IF NOT EXISTS kline (date TEXT PRIMARY KEY, open REAL, high REAL, low REAL, close REAL, volume REAL, adjust TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS income (report_date TEXT, item_name TEXT, amount REAL, item_code TEXT, PRIMARY KEY (report_date, item_name))")
    c.execute("CREATE TABLE IF NOT EXISTS balance (report_date TEXT, item_name TEXT, amount REAL, item_code TEXT, PRIMARY KEY (report_date, item_name))")
    c.execute("CREATE TABLE IF NOT EXISTS cashflow (report_date TEXT, item_name TEXT, amount REAL, item_code TEXT, PRIMARY KEY (report_date, item_name))")
    c.execute("CREATE TABLE IF NOT EXISTS indicators (report_date TEXT, item_name TEXT, amount REAL, PRIMARY KEY (report_date, item_name))")
    c.execute("CREATE TABLE IF NOT EXISTS dividend (report_year TEXT, cash_dps REAL, special_dps REAL, ex_date TEXT, pay_date TEXT, total_amount REAL, raw_text TEXT DEFAULT '', PRIMARY KEY (report_year))")
    c.execute("CREATE TABLE IF NOT EXISTS revenue_structure (code TEXT, year TEXT, dim_type TEXT, dim_name TEXT, amount REAL, pct REAL, PRIMARY KEY (code, year, dim_type, dim_name))")
    # 兼容旧表
    for tbl in ["income", "balance", "cashflow"]:
        try: c.execute(f"ALTER TABLE {tbl} ADD COLUMN item_code TEXT")
        except: pass
    try: c.execute("ALTER TABLE dividend ADD COLUMN raw_text TEXT DEFAULT ''")
    except: pass
    conn.commit()
    conn.close()

    # 用简易 Store 包装 (仅复用 upsert_indicators)
    class SimpleStore:
        def __init__(self):
            self.conn = sqlite3.connect(db_path)
        def upsert_indicators(self, report_date, items):
            for k, v in items.items():
                if v is None: continue
                try:
                    self.conn.execute("INSERT OR IGNORE INTO indicators VALUES (?,?,?)",
                                      (str(report_date), k, float(v)))
                except (ValueError, TypeError): pass
            self.conn.commit()
        def set_meta(self, key, value):
            self.conn.execute("INSERT OR REPLACE INTO meta VALUES (?,?)", (key, value))
            self.conn.commit()

    store = SimpleStore()

    try:
        _write_kline(store, code);        time.sleep(0.5)
        _write_spot(store, code);         time.sleep(0.3)

        # 三大表 (年报 + 季度, westock-data --num 10 覆盖 ~10期)
        _write_income(store, code);       time.sleep(1.0)
        _write_balance(store, code);      time.sleep(1.0)
        _write_cashflow(store, code);     time.sleep(1.0)

        # 指标 (从财报数据汇总)
        _write_indicators(store, code);   time.sleep(0.3)

        # 分红 (季度明细 → 年度汇总)
        _write_dividend(store, code);     time.sleep(0.5)

        store.set_meta("last_fetch", str(date.today()))
        store.set_meta("last_fetch_date", date.today().isoformat())
        store.set_meta("code", code)
        store.set_meta("market", "us")
        store.set_meta("data_source", "westock-data")

        print(f"\n{'='*50}")
        print("FETCH_OK (westock-data)")
        print(f"数据已存入 {db_path}")
        print(f"{'='*50}")
    finally:
        store.conn.close()


if __name__ == "__main__":
    code = sys.argv[1] if len(sys.argv) > 1 else "GOOGL"
    fetch_us_westock(code)
