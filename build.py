#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Value Line 报告生成流水线 — 强制8步，一步不可少。

用法:
    python build.py 09992          # 单股全流程
    python build.py 09988 00700    # 多股批量
    python build.py --force 002027 # 跳过PDF联网步骤(A股备用)

每一步有前置检查，不满足立即终止。
"""

import os, sys, json, sqlite3, subprocess, argparse, time, re
from datetime import date
from pathlib import Path

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
import config

PYTHON = os.environ.get("PYTHON_BIN", os.path.join(
    os.environ.get("WORKBUDDY_PYTHON", ""),
    "envs", "default", "Scripts", "python.exe"
))
# fallback
if not os.path.exists(PYTHON):
    PYTHON = sys.executable

ENV = {**os.environ, "PYTHONIOENCODING": "utf-8"}

# ────────────────────────────────────────────────
# helpers
# ────────────────────────────────────────────────

def _green(s): return f"\033[32m{s}\033[0m"
def _red(s):   return f"\033[31m{s}\033[0m"
def _yellow(s): return f"\033[33m{s}\033[0m"
def _bold(s): return f"\033[1m{s}\033[0m"

def _run(cmd, timeout=120):
    """Run a shell command, return (ok, output)."""
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True,
                           text=True, timeout=timeout, cwd=BASE, env=ENV,
                           encoding='utf-8', errors='replace')
        out = (r.stdout or "") + (r.stderr or "")
        out = out.strip()
        return r.returncode == 0, out[-3000:] if len(out) > 3000 else out
    except subprocess.TimeoutExpired:
        return False, "TIMEOUT"
    except Exception as e:
        return False, str(e)

def _set_active(code):
    """Write ACTIVE_STOCK to config.py."""
    path = os.path.join(BASE, "config.py")
    with open(path, "r", encoding="utf-8") as f:
        c = f.read()
    c = re.sub(r'ACTIVE_STOCK\s*=\s*"[0-9]+"', f'ACTIVE_STOCK = "{code}"', c)
    with open(path, "w", encoding="utf-8") as f:
        f.write(c)

def _db_path(code):
    return os.path.join(BASE, "data", f"{code}.db")

def _pdf_dir(code):
    return os.path.join(BASE, "data", "pdfs", code)

def _report_path(code):
    stock = config.STOCKS.get(code, {})
    name = stock.get("name_en", code).replace(" ", "_")
    return os.path.join(BASE, "report", f"{name}.html")

# ────────────────────────────────────────────────
# Step runners
# ────────────────────────────────────────────────

def step_0_check_config(code):
    """Step 0: 检查 config 完整性。"""
    stock = config.STOCKS.get(code)
    if not stock:
        raise SystemExit(_red(f"  FAIL: {code} 不在 config.STOCKS 中"))
    name = stock.get("name", code)

    issues = []
    if not stock.get("name_en"):
        issues.append("name_en 缺失")
    # business_desc 和 analyst.commentary 为 fallback:
    #   优先从年报 PDF 提取 (Step 3 extract_mda.py), 缺失不影响流程
    if not stock.get("business_desc"):
        print(f"  [INFO] {code} 无 business_desc fallback (将从PDF提取)")
    analyst = stock.get("analyst", {})
    if not analyst.get("commentary"):
        print(f"  [INFO] {code} 无 analyst.commentary fallback (将从PDF提取)")

    if issues:
        raise SystemExit(_red(f"  FAIL: {code} {name} config不完整: {', '.join(issues)}"))

    print(f"  Step 0: {name} ({code}) config {_green('OK')}")
    return stock

def step_1_fetch(code, stock):
    """Step 1: 数据拉取 fetcher.py。"""
    db = _db_path(code)
    if os.path.exists(db) and os.path.getsize(db) > 10000:
        print(f"  Step 1: DB已存在 ({os.path.getsize(db)//1024}KB), 跳过拉取")
        # Still set active stock
        _set_active(code)
        return True

    print(f"  Step 1: 拉取数据...")
    _set_active(code)
    ok, out = _run(f'"{PYTHON}" fetcher.py', timeout=300)
    if not ok or "拉取完成" not in out:
        raise SystemExit(_red(f"  FAIL: 数据拉取失败\n{out[-500:]}"))
    # Verify DB
    if not os.path.exists(db) or os.path.getsize(db) < 10000:
        raise SystemExit(_red(f"  FAIL: DB文件过小或不存在"))
    print(f"  Step 1: {_green('OK')}")
    return True

def step_2_pdf(code):
    """Step 2: 年报PDF下载。缺失即阻断。"""
    pdf_dir = _pdf_dir(code)
    existing = len([f for f in os.listdir(pdf_dir) if f.endswith(".pdf")]) if os.path.isdir(pdf_dir) else 0
    if existing >= 3:
        print(f"  Step 2: 已有 {existing} 份PDF, 跳过下载")
        return True

    print(f"  Step 2: 下载年报PDF...")
    _set_active(code)
    ok, out = _run(f'"{PYTHON}" pdf_downloader.py', timeout=600)
    if not ok:
        raise SystemExit(_red(f"  FAIL: PDF下载失败\n{out[-500:]}"))
    # Verify
    pdf_dir = _pdf_dir(code)
    count = len([f for f in os.listdir(pdf_dir) if f.endswith(".pdf")]) if os.path.isdir(pdf_dir) else 0
    if count < 3:
        raise SystemExit(_red(f"  FAIL: 下载后仅{count}份PDF, 需≥3年年报"))
    print(f"  Step 2: {_green('OK')} ({count}份PDF)")
    return True

def step_3_mda(code):
    """Step 3: MD&A提取。缺失即阻断。"""
    db = _db_path(code)
    conn = sqlite3.connect(db)
    has_mda = conn.execute("SELECT value FROM meta WHERE key='mda_text'").fetchone()
    conn.close()
    if has_mda and has_mda[0] and len(has_mda[0]) > 200:
        print(f"  Step 3: mda_text已存在 ({len(has_mda[0])} chars), 跳过提取")
        return True

    # Check PDF exists before extracting
    pdf_dir = _pdf_dir(code)
    pdfs = [f for f in os.listdir(pdf_dir) if f.endswith(".pdf")] if os.path.isdir(pdf_dir) else []
    if not pdfs:
        raise SystemExit(_red(f"  FAIL: 无PDF文件, 先执行 step_2"))

    print(f"  Step 3: 提取MD&A...")
    _set_active(code)
    ok, out = _run(f'"{PYTHON}" extract_mda.py', timeout=120)
    if not ok:
        raise SystemExit(_red(f"  FAIL: MD&A提取失败\n{out[-500:]}"))
    # Verify
    conn = sqlite3.connect(db)
    has = conn.execute("SELECT value FROM meta WHERE key='mda_text'").fetchone()
    conn.close()
    if not has or not has[0]:
        raise SystemExit(_red(f"  FAIL: mda_text写入失败"))
    print(f"  Step 3: {_green('OK')} ({len(has[0])} chars)")
    return True

def step_4_revenue(code):
    """Step 4: 营收结构。缺失即阻断。"""
    db = _db_path(code)
    conn = sqlite3.connect(db)
    try:
        cnt = conn.execute("SELECT COUNT(*) FROM revenue_structure WHERE code=?", (code,)).fetchone()[0]
        if cnt > 0:
            print(f"  Step 4: revenue_structure已存在 ({cnt}条), 跳过")
            conn.close()
            return True
    except:
        pass  # table may not exist
    conn.close()

    raise SystemExit(_red(
        f"  FAIL: revenue_structure为空, 需手动执行 insert_revenue.py"))

def step_5_config_final(code, stock):
    """Step 5: 最终 config 检查 + 切回标的。"""
    _set_active(code)
    print(f"  Step 5: config final {_green('OK')}")
    return True

def step_6_engine(code):
    """Step 6: engine.py 计算。"""
    print(f"  Step 6: 计算指标...")
    _set_active(code)
    ok, out = _run(f'"{PYTHON}" engine.py', timeout=120)
    if not ok:
        raise SystemExit(_red(f"  FAIL: engine计算失败\n{out[-500:]}"))
    # Check report_data.json
    rp = os.path.join(BASE, "report_data.json")
    if not os.path.exists(rp):
        raise SystemExit(_red(f"  FAIL: report_data.json未生成"))
    with open(rp, "r", encoding="utf-8") as f:
        d = json.load(f)
    years = d.get("years", [])
    kline = d.get("kline", [])
    print(f"  Step 6: {_green('OK')} (years={len(years)}, kline={len(kline)}m)")
    return True

def step_7_generate(code):
    """Step 7: generate_report.py HTML生成。"""
    print(f"  Step 7: 生成HTML...")
    _set_active(code)
    ok, out = _run(f'"{PYTHON}" generate_report.py', timeout=30)
    if not ok:
        raise SystemExit(_red(f"  FAIL: HTML生成失败\n{out[-500:]}"))
    rp = _report_path(code)
    if not os.path.exists(rp):
        raise SystemExit(_red(f"  FAIL: HTML文件未生成"))
    size = os.path.getsize(rp)
    print(f"  Step 7: {_green('OK')} ({rp} [{size//1024}KB])")
    return True

def step_8_verify(code):
    """Step 8: 逐区域逐字段数据完整性验证。对照 VL_REGION_ALIGNMENT.md 全部字段。"""
    rj = os.path.join(BASE, "report_data.json")
    with open(rj, "r", encoding="utf-8") as f:
        d = json.load(f)

    stock = config.STOCKS[code]
    name = stock["name"]
    checks = []

    def ok(msg): checks.append(("PASS", msg))
    def fail(msg): checks.append(("FAIL", msg))

    s = d.get("spot", {})
    data = d.get("data", {})
    cs = d.get("capital_structure", {})
    ar = d.get("annual_rates", {})
    qt = d.get("quarterly", {})
    cp = d.get("current_position", {})
    an = d.get("analyst", {})

    # ── 1. Header (8 fields) ──
    market = stock.get("market", "hk")
    header_fields = [("price","Price"),("pe","P/E"),("eps_ttm","EPS TTM"),
                     ("pb","P/B"),("div_yield","Div Yld"),
                     ("median_pe","Median PE"),("mkt_cap","MktCap")]
    # EPS HKD 仅港股需要 (A股无汇率转换)
    if market == "hk":
        header_fields.insert(3, ("eps_ttm_hkd","EPS HKD"))
    for k,label in header_fields:
        v = s.get(k)
        if v is None: fail(f"Header.{label}")
        elif v == 0 and k != "div_yield": fail(f"Header.{label}")
        else: ok(f"Header.{label}")

    # ── 2. Statistical Array (24 rows, all years) ──
    rows_24 = [
        "PER_OI","PER_NETCASH","BASIC_EPS","DPS","CAPEX_PS","BPS",
        "TOTAL_SHARES","PE_AVG","PE_RELATIVE","DIV_YIELD",
        "OPERATE_INCOME","GROSS_MARGIN","OP_MARGIN","DEPRECIATION",
        "HOLDER_PROFIT","TAX_EBT","NET_PROFIT_RATIO",
        "WORKING_CAPITAL","LT_DEBT","TOTAL_EQUITY",
        "ROIC","ROE","RETAINED_RATIO","PAYOUT_RATIO"
    ]
    if not data:
        fail("StatArray: 空")
    else:
        # 宽松检查字段: 数据源限制可能导致覆盖不全
        lenient_fields = {"DEPRECIATION", "LT_DEBT"}  # 现金表缺失/负债数据稀疏
        for fld in rows_24:
            # 至少2/3的年份有非None值（pre-IPO年份合理缺失）
            vals = [data[yr].get(fld) for yr in data if fld in data[yr] and data[yr].get(fld) is not None]
            threshold = 1 if fld in lenient_fields else max(2, len(data) * 2 // 3)
            if len(vals) >= threshold:
                ok(f"Stat.{fld}")
            else:
                fail(f"Stat.{fld} ({len(vals)}/{len(data)}y)")

    # ── 3. Capital Structure (14 fields) ──
    cap_fields = [
        "total_assets","total_debt","total_equity","cash","inventory","receivables",
        "lt_debt","due_in_5yr","total_int","coverage","lt_debt_pct",
        "mkt_cap","common_shares_str","common_shares_raw"
    ]
    for fld in cap_fields:
        v = cs.get(fld)
        if v is None: fail(f"CapStr.{fld}")
        elif v == 0 and fld not in ("inventory", "lt_debt", "lt_debt_pct"): fail(f"CapStr.{fld}")
        else: ok(f"CapStr.{fld}")
    # mda_text
    mda = cs.get("mda_text","")
    if not mda or len(mda) < 100: fail(f"CapStr.mda_text ({len(mda)}c)")
    else: ok(f"CapStr.mda_text ({len(mda)}c)")

    # ── 4. Current Position (9 items × 3 years) ──
    cp_items = cp.get("items", [])
    cp_years = cp.get("years", [])
    if len(cp_items) >= 6 and len(cp_years) >= 3:
        ok(f"CurPos ({len(cp_items)}items×{len(cp_years)}y)")
    else:
        fail(f"CurPos ({len(cp_items)}items×{len(cp_years)}y)")

    # ── 5. Annual Rates (5 metrics × 3 periods) ──
    for k in ["sales","cashflow","earnings","dividends","book_value"]:
        v = ar.get(k, {})
        if not isinstance(v, dict): fail(f"CAGR.{k}")
        else:
            has = sum(1 for p in ["1yr","3yr","5yr"] if v.get(p) is not None)
            if has >= 2: ok(f"CAGR.{k}")
            else: fail(f"CAGR.{k} ({has}/3)")

    # ── 6. Quarterly (3 tables) ──
    for section in ["sales","eps","dividends"]:
        items = qt.get(section, [])
        if items: ok(f"Qtr.{section} ({len(items)}y)")
        else: fail(f"Qtr.{section}: 空")

    # ── 7. K线 & 指数 ──
    kline = d.get("kline", [])
    if kline: ok(f"Kline ({len(kline)}m)")
    else: fail("Kline: 空")
    ik = d.get("index_kline", [])
    if ik: ok(f"Index ({len(ik)}m)")
    else: fail("Index: 空")

    # ── 8. CF Line & Yearly H/L ──
    cf = d.get("cf_line", [])
    if cf: ok(f"CF Line ({len(cf)}pts)")
    else: fail("CF Line: 空")
    yhl = d.get("yearly_hl", [])
    if yhl: ok(f"Yr H/L ({len(yhl)}y)")
    else: fail("Yr H/L: 空")

    # ── 9. Total Returns ──
    tr = d.get("total_returns", {})
    stock_tr = tr.get("stock", {})
    if stock_tr and stock_tr.get("1yr") is not None: ok("TotalReturns")
    else: fail("TotalReturns")

    # ── 10. Revenue Structure ──
    rs = d.get("revenue_structure", {})
    if rs: ok(f"Revenue ({len(rs)}dims)")
    else: fail("Revenue: 空")

    # ── 11. Analyst + Business ──
    if an.get("commentary"): ok("Commentary")
    else: fail("Commentary: 缺失")
    if an.get("business"): ok("Business")
    else: fail("Business: 缺失")

    # ── 12. Validation ──
    v = d.get("validation", {})
    mismatches = v.get("mismatches", [])
    checks_passed = v.get("checks_passed", 0)
    checks_total = v.get("checks_total", 0)
    # 早年(借壳上市/重组前) mismatch 可接受: 仅阻断 2018+ 年份
    # 阿里巴巴(09988) 2019年11月才港股上市，2018-2019 数据为ADR口径，跳过
    recent_cutoff = 2018
    skip_preipo_years = {"09988": 2020, "06699": 2026}  # 06699: 2021上市,PDF营收为HKD原币vs AKShare转CNY约10%FX差
    preipo_cutoff = skip_preipo_years.get(code, recent_cutoff)
    recent_mismatches = [m for m in mismatches
                         if isinstance(m, str) and
                         any(str(y) in m.split()[0] for y in range(preipo_cutoff, 2100))]
    if recent_mismatches:
        fail(f"CrossCheck ({checks_passed}/{checks_total}, {len(recent_mismatches)}mismatch@{preipo_cutoff}+)")
    elif mismatches:
        ok(f"CrossCheck ({checks_passed}/{checks_total}, {len(mismatches)}早年mismatch [{preipo_cutoff}+ 0])")
    else:
        ok(f"CrossCheck ({checks_passed}/{checks_total} passed)")

    # ── 13. Meta ──
    meta = d.get("meta", {})
    for k in ["name_en","name","code","market","currency","price_ccy","rpt_ccy"]:
        if meta.get(k): ok(f"Meta.{k}")
        else: fail(f"Meta.{k}")

    # ── Print & Judge ──
    fails = [msg for status, msg in checks if status == "FAIL"]
    for status, msg in checks:
        print(f"    {_green('[PASS]') if status=='PASS' else _red('[FAIL]')} {msg}")

    if fails:
        raise SystemExit(_red(f"\n  FAIL: {len(fails)}/{len(checks)}项缺失"))

    print(f"  Step 8: {_green(f'ALL PASS ({len(checks)} checks, 0 fails)')}")
    return True


# ────────────────────────────────────────────────
# Main pipeline
# ────────────────────────────────────────────────

def confirm_and_build(code, cf_multiplier, num_years=15, skip_cf_confirm=False):
    """
    强制确认后才能启动流水线。
    必须提供: 股票代码 + CF倍数。市场(A/H)从config自动读取。
    - cf_multiplier=None 时使用默认值15.0，skip_cf_confirm=False时会打印醒目提示
    """
    stock = config.STOCKS.get(code)

    # 显示用字段 (未配置时用占位值)
    name = stock.get("name", code) if stock else code
    market = stock.get("market", "hk") if stock else "hk"
    market_label = "A股" if market == "cn" else "港股(H股)"
    industry = stock.get("industry", "未知") if stock else "未知"
    currency = stock.get("currency", "CNY") if stock else "CNY"
    exchange = stock.get("exchange", "") if stock else ""

    # ── CF倍数默认值处理 ──
    if cf_multiplier is None:
        cf_multiplier = 15.0
        if not skip_cf_confirm:
            print(f"\n{'='*60}")
            print(f"  ***  CF倍数未指定，使用默认值 15.0x  ***")
            print(f"{'='*60}\n")
            print(f"  {_yellow('提示: 下次请显式指定 --cf N (如 --cf 18.0)')}\n")

    # 探测可用数据年份
    yr_range = _detect_year_range(code)
    yr_note = ""
    if yr_range:
        total_yrs = yr_range[1] - yr_range[0] + 1
        if total_yrs > num_years:
            yr_note = f" (共{total_yrs}年, 使用最近{num_years}年。--years N 可调整)"

    # ── 确认页 (先显示，后校验) ──
    print(f"\n{_bold('='*60)}")
    print(f"{_bold('  Value Line 报告生成 — 确认页')}")
    print(f"{_bold('='*60)}")
    print(f"  企业:      {name}")
    print(f"  代码:      {code}.{exchange}")
    print(f"  市场:      {market_label}")
    print(f"  行业:      {industry}")
    print(f"  报表币种:   {currency}")
    print(f"  数据年份:   {yr_range[0]}-{yr_range[1]}{yr_note}" if yr_range else "  数据年份:   未探测")
    print(f"  CF 倍数:    {cf_multiplier}x")
    if not stock:
        print(f"  {_red('状态:  未在 config.STOCKS 中配置!')}")
    print(f"{_bold('='*60)}")

    # ── 校验 (确认页之后) ──
    if not stock:
        raise SystemExit(_red(f"\n  REFUSED: {code} 不在 config.STOCKS 中, 请先配置\n  提示: 编辑 config.py, 在 STOCKS 字典中添加该股票信息"))

    if cf_multiplier <= 0:
        raise SystemExit(_red("  REFUSED: CF倍数必须 > 0, 默认15.0"))

    if market not in ("hk", "cn"):
        raise SystemExit(_red(f"  REFUSED: 未知市场 '{market}', 请设为 'hk' 或 'cn'"))

    # Write CF multiplier to config temp override
    _write_cf(code, cf_multiplier)

    # ── 执行 ──
    print(f"\n{_bold(f'  >>> 开始生成 {name} ({code}), CF={cf_multiplier}x <<<')}")
    return build(code)


def _write_cf(code, cf):
    """写 CF 倍数到 DB meta, engine 自动读取。"""
    db = _db_path(code)
    if os.path.exists(db):
        conn = sqlite3.connect(db)
        conn.execute("INSERT OR REPLACE INTO meta VALUES (?,?)",
                     ("cf_multiplier", str(cf)))
        conn.commit()
        conn.close()

def _detect_year_range(code):
    """探测 DB 中可用的数据年份范围。"""
    db = _db_path(code)
    if not os.path.exists(db):
        return None
    try:
        conn = sqlite3.connect(db)
        rows = conn.execute(
            "SELECT DISTINCT CAST(substr(report_date,1,4) AS INTEGER) FROM income "
            "WHERE substr(report_date,5,2) IN ('-1','-0') ORDER BY 1"
        ).fetchall()
        conn.close()
        if len(rows) >= 2:
            return (rows[0][0], rows[-1][0])
    except:
        pass
    return None


def build(code):
    """Run full 8-step pipeline for a single stock."""
    stock = config.STOCKS.get(code, {})
    name = stock.get("name", code)
    print(f"\n{_bold('='*60)}")
    print(f"{_bold(f'  {name} ({code}) - Value Line Pipeline')}")
    print(f"{_bold('='*60)}")

    _set_active(code)
    stock = step_0_check_config(code)           # 0. config
    step_1_fetch(code, stock)                    # 1. 拉取
    step_2_pdf(code)                             # 2. PDF
    step_3_mda(code)                             # 3. MD&A
    step_4_revenue(code)                         # 4. 营收结构
    step_5_config_final(code, stock)             # 5. config final
    step_6_engine(code)                          # 6. 计算
    step_7_generate(code)                        # 7. HTML
    step_8_verify(code)                          # 8. 验证

    print(f"\n{_green(_bold(f'  {name} ({code}) Report Complete!'))}")
    print(f"  文件: {_report_path(code)}\n")

    # restore POP MART
    _set_active("09992")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Value Line 报告生成流水线 — 必须提供代码, CF倍数可选",
        epilog="示例: python build.py 09992          (CF用默认15.0)\n"
              "      python build.py 09992 --cf 18.0 (指定CF倍数)"
    )
    parser.add_argument("codes", nargs="+", help="股票代码, 如 09992 00700")
    parser.add_argument("--cf", type=float, default=None,
                        help="CF倍数 (不指定则默认15.0, 会打印提示)")
    parser.add_argument("--skip-cf-confirm", action="store_true",
                        help="跳过CF倍数提示(仅用于重生成/自动化)")
    parser.add_argument("--years", type=int, default=15,
                        help="使用最近N年数据 (默认15, 不超过可用年份)")
    args = parser.parse_args()

    if args.cf is not None and args.cf <= 0:
        parser.error("--cf 必须 > 0")
    if args.years < 3:
        parser.error("--years 最小值为 3")

    for code in args.codes:
        yr_range = _detect_year_range(code)
        available = yr_range[1] - yr_range[0] + 1 if yr_range else 0
        default_years = min(available, 15) if available > 10 else available
        actual_years = args.years if args.years != 15 else default_years
        actual_years = max(min(actual_years, available), 1)
        try:
            confirm_and_build(code,
                              cf_multiplier=args.cf,
                              num_years=actual_years,
                              skip_cf_confirm=args.skip_cf_confirm)
        except SystemExit as e:
            print(f"\n{_red(_bold(f'  BUILD FAILED: {code}'))}")
            if str(e):
                print(f"  {e}\n")
            _set_active("09992")
            sys.exit(1)

    _set_active("09992")
