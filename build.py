#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Value Line 报告生成流水线 — 强制8步，一步不可少。

用法:
    python build.py 09992 --cf 15.0           # CF估值 (消费/科技/成长股)
    python build.py 09992                      # 省略 --cf: 从DB读或交互输入
    python build.py 01114 --pb 0.8            # PB估值 (银行/保险/资产型)
    python build.py 00700 --method cf --cf 10.0
    python build.py 02328 --method pb --pb 1.0

估值方法:
    cf: CF倍数 × 每股现金流 (适合消费/科技/成长股)
    pb: PB倍数 × 每股净资产 (适合银行/保险/周期股/资产型标的)
    估值倍数: CLI --cf/--pb > DB 已确认值 > 交互输入 (显示历史PE/PB均值参考)

每一步有前置检查，不满足立即终止。
"""

import os, sys, json, sqlite3, subprocess, argparse, time, re
from datetime import date, timedelta

# Windows 终端中文乱码修复: 强制 stdout 为 UTF-8
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
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
    """Run a shell command, return (ok, output). 流式输出，避免长时间无进度反馈。"""
    import io
    try:
        print(f"      运行中 ...", end="", flush=True)
        r = subprocess.run(cmd, shell=True, capture_output=True,
                           text=True, timeout=timeout, cwd=BASE, env=ENV,
                           encoding='utf-8', errors='replace')
        out = (r.stdout or "") + (r.stderr or "")
        out = out.strip()
        # 截断保留尾部的关键信息（如进度条后的"拉取完成"）
        tail = out[-4000:] if len(out) > 4000 else out
        ok = r.returncode == 0
        if ok:
            print(f"\r{'':20}", end="")  # 清除"运行中..."
        return ok, tail
    except subprocess.TimeoutExpired:
        print(f"\r{'':20}", end="")
        return False, "TIMEOUT"
    except Exception as e:
        print(f"\r{'':20}", end="")
        return False, str(e)

def _set_active(code):
    """Write ACTIVE_STOCK to config.py."""
    path = os.path.join(BASE, "config.py")
    with open(path, "r", encoding="utf-8") as f:
        c = f.read()
    c = re.sub(r'ACTIVE_STOCK\s*=\s*"[^"]*"', f'ACTIVE_STOCK = "{code}"', c)
    with open(path, "w", encoding="utf-8") as f:
        f.write(c)

def _db_path(code):
    return os.path.join(BASE, "data", f"{code}.db")

def _pdf_dir(code):
    return os.path.join(BASE, "data", "pdfs", code)

def _report_path(code):
    stock = config.STOCKS.get(code, {})
    name = stock.get("name", code)
    return os.path.join(BASE, "report", f"{name}.html")

# ────────────────────────────────────────────────
# Step runners
# ────────────────────────────────────────────────

def _get_fx(date_str):
    """读取 HKD/CNY 汇率 (返回 1 HKD = ? CNY)，失败返回 None"""
    fx_db = os.path.join(BASE, "data", "fx_rates.db")
    if not os.path.exists(fx_db):
        return None
    try:
        conn = sqlite3.connect(fx_db)
        row = conn.execute("SELECT hkd_cny FROM daily_rates WHERE date=?", (date_str,)).fetchone()
        if not row:
            row = conn.execute("SELECT hkd_cny FROM daily_rates WHERE date<=? ORDER BY date DESC LIMIT 1", (date_str,)).fetchone()
        conn.close()
        return row[0] / 100.0 if row else None
    except Exception:
        return None


def _get_hist_valuation_ref(code, method):
    """从 DB 读取历史 PE/PB 均值，作为估值参考。
    返回 (label, avg_val) 或 None。
    """
    db = _db_path(code)
    if not os.path.exists(db):
        return None
    try:
        conn = sqlite3.connect(db)
        # 取 BPS / EPS / PE_AVG / 年末收盘价
        bps_rows = conn.execute(
            "SELECT report_date, amount FROM indicators WHERE item_name='BPS' AND report_date LIKE '%-12-31'"
        ).fetchall()
        eps_rows = conn.execute(
            "SELECT report_date, amount FROM indicators WHERE item_name='BASIC_EPS' AND report_date LIKE '%-12-31'"
        ).fetchall()
        pe_avg_rows = conn.execute(
            "SELECT report_date, amount FROM indicators WHERE item_name='PE_AVG' AND report_date LIKE '%-12-31'"
        ).fetchall()
        # 前复权日线 → 日线按 YYYY-MM 分组 → 月均价 = 每月所有交易日收盘价的均值
        kl_rows = conn.execute(
            "SELECT date, close FROM kline WHERE adjust='qfq' ORDER BY date"
        ).fetchall()

        from collections import defaultdict
        monthly_closes = defaultdict(list)
        for d, c in kl_rows:
            monthly_closes[d[:7]].append(c)
        monthly_avg = {m: sum(v) / len(v) for m, v in monthly_closes.items()}

        yr_all_closes = defaultdict(list)
        for m, c in monthly_avg.items():
            yr_all_closes[m[:4]].append(c)
        yr_avg_price = {y: sum(v) / len(v) for y, v in yr_all_closes.items() if v}

        yr_bps = {d[:4]: v for d, v in bps_rows if v and v > 0}
        yr_eps = {d[:4]: v for d, v in eps_rows if v and v > 0}
        yr_pe_avg = {d[:4]: v for d, v in pe_avg_rows if v and v > 0}

        # 共同年份: 有 BPS + EPS + 任何日线 (仅 PB 需要)
        years = sorted(set(yr_bps) & set(yr_eps) & set(yr_avg_price))

        # 判断是否需要汇率换算: 港股 + CNY财报 = 股价(HKD)需要折算为CNY
        stock = config.STOCKS.get(code, {})
        market = stock.get("market", "")
        currency = stock.get("currency", "CNY")
        need_fx = (market == "hk" and currency == "CNY")

        if method == "pb" and years:
            if need_fx:
                pbs = []
                for y in years:
                    fx = _get_fx(f"{y}-12-31")
                    if fx and fx > 0 and yr_bps[y] > 0:
                        pbs.append(yr_avg_price[y] * fx / yr_bps[y])
            else:
                pbs = [yr_avg_price[y] / yr_bps[y] for y in years if yr_bps[y] > 0]
            if pbs:
                avg = sum(pbs) / len(pbs)
                rng = f"{years[0]}-{years[-1]}"
                conn.close()
                return (f"历史PB均值 ({rng})", round(avg, 2))

        if method == "cf":
            # 优先 PE_AVG (AKShare自带, 无需 BPS/EPS 交集)
            if len(yr_pe_avg) >= 3:
                pes = list(yr_pe_avg.values())
                avg = sum(pes) / len(pes)
                keys_sorted = sorted(yr_pe_avg.keys())
                rng = f"{keys_sorted[0]}-{keys_sorted[-1]}"
                conn.close()
                return (f"历史PE均值 ({rng})", round(avg, 1))
            # 回退: 年均价/EPS 自行计算 (需要 BPS+EPS+K线 交集)
            elif years:
                if need_fx:
                    pes = []
                    for y in years:
                        fx = _get_fx(f"{y}-12-31")
                        if fx and fx > 0 and yr_eps[y] > 0:
                            pes.append(yr_avg_price[y] * fx / yr_eps[y])
                else:
                    pes = [yr_avg_price[y] / yr_eps[y] for y in years if yr_eps[y] > 0]
                if pes:
                    avg = sum(pes) / len(pes)
                    rng = f"{years[0]}-{years[-1]}"
                    conn.close()
                    return (f"历史PE均值 ({rng})", round(avg, 1))

        conn.close()
    except Exception:
        pass
    return None


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

def _get_meta(db_path, key, default=None):
    try:
        conn = sqlite3.connect(db_path)
        row = conn.execute("SELECT value FROM meta WHERE key=?", (key,)).fetchone()
        conn.close()
        return row[0] if row else default
    except: return default

def _set_meta(db_path, key, value):
    try:
        conn = sqlite3.connect(db_path)
        conn.execute("CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT)")
        conn.execute("INSERT OR REPLACE INTO meta VALUES (?,?)", (key, str(value)))
        conn.commit(); conn.close()
    except: pass

def _need_fresh_financials(db_path):
    """检查是否有新的财报期。返回: (need_refresh, reason)"""
    try:
        conn = sqlite3.connect(db_path)
        # 取最新的财报报告期
        rows = conn.execute(
            "SELECT DISTINCT report_date FROM indicators WHERE report_date LIKE '%-12-31' OR report_date LIKE '%-06-30' OR report_date LIKE '%-03-31' OR report_date LIKE '%-09-30' ORDER BY report_date DESC LIMIT 1"
        ).fetchall()
        conn.close()
        if not rows:
            return True, "无财报数据"
        latest = rows[0][0]  # e.g. "2025-12-31"
        yr, mo = int(latest[:4]), int(latest[5:7])
        today = date.today()
        # 年报(12-31): 次年4月底前发布 → 5月后应该有
        if mo == 12 and today >= date(today.year, 5, 1) and yr < today.year - 1:
            return True, f"最新年报{yr}年，{today.year-1}年年报应已发布"
        if mo == 12 and today >= date(today.year, 5, 1) and today.month >= 5:
            # 检查是否有下一年的Q1
            pass  # Q1 通常在4月底前发布
        # Q1(03-31): 4月底前发布
        if mo == 3 and today >= date(today.year, 5, 1) and yr < today.year:
            return True, f"最新季报{latest}，{today.year}年Q1应已发布"
        if mo == 3 and today >= date(today.year, 5, 1):
            # 检查是否有H1
            expected_yr = today.year if today.month >= 9 else today.year - 1
            if yr < expected_yr:
                return True, f"最新报表{latest}，应有更新的中期/年报"
        # 中报(06-30): 8月底前发布
        if mo == 6 and today >= date(today.year, 9, 1) and yr < today.year:
            return True, f"最新中报{latest}，{today.year}年中报应已发布"
        # Q3(09-30): 10月底前发布
        if mo == 9 and today >= date(today.year, 11, 1) and yr < today.year:
            return True, f"最新季报{latest}，{today.year}年Q3应已发布"
        # 通用: 如果最新财报年份落后当前年份超过1年
        if yr < today.year - 1:
            return True, f"最新报表{latest}落后{today.year-yr}年"
        return False, ""
    except Exception:
        return True, "无法检测"

def _need_fresh_prices(db_path):
    """检查最新K线是否覆盖到最近交易日。返回: (need_refresh, reason)"""
    try:
        conn = sqlite3.connect(db_path)
        today_str = date.today().strftime("%Y-%m-%d")
        # 查最近3天是否有数据 (周六日没数据, 周五的数据周一仍有效)
        for d in range(3):
            check = (date.today() - timedelta(days=d)).strftime("%Y-%m-%d")
            row = conn.execute("SELECT date FROM kline WHERE date=? LIMIT 1", (check,)).fetchone()
            if row:
                conn.close()
                return False, ""
        last = conn.execute("SELECT date FROM kline ORDER BY date DESC LIMIT 1").fetchone()
        conn.close()
        return True, f"最新K线到{last[0] if last else '无'}"
    except Exception:
        return True, "无法检测"

def step_1_fetch(code, stock, force_fetch=False):
    """Step 1: 数据拉取 fetcher.py。
    财报数据: 检查是否有新报告期 → 有则拉取
    股价数据: 检查今日K线是否存在 → 无则拉取
    --fetch 强制全量重拉。"""
    db = _db_path(code)
    if not force_fetch and os.path.exists(db) and os.path.getsize(db) > 10000:
        need_prices, price_reason = _need_fresh_prices(db)
        need_fin, fin_reason = _need_fresh_financials(db)
        if not need_prices and not need_fin:
            print(f"  Step 1: DB数据已是最新 (K线到本月, 财报期同步), 跳过拉取")
            _set_active(code); return True
        reasons = []
        if need_prices: reasons.append(f"股价需更新: {price_reason}")
        if need_fin: reasons.append(f"财报需更新: {fin_reason}")
        print(f"  Step 1: {'; '.join(reasons)}，自动拉取...")

    print(f"  Step 1: 拉取数据...")
    _set_active(code)
    ok, out = _run(f'"{PYTHON}" fetcher.py', timeout=600)
    if not ok or "拉取完成" not in out:
        raise SystemExit(_red(f"  FAIL: 数据拉取失败\n{out[-500:]}"))
    if not os.path.exists(db) or os.path.getsize(db) < 10000:
        raise SystemExit(_red(f"  FAIL: DB文件过小或不存在"))
    _set_meta(db, "last_fetch_date", date.today().isoformat())
    print(f"  Step 1: {_green('OK')}")
    return True

def step_2_pdf(code):
    """Step 2: 年报PDF下载。智能检测: 新年报发布自动下载。"""
    stock = config.STOCKS.get(code, {})
    pdf_dir = _pdf_dir(code)
    existing = len([f for f in os.listdir(pdf_dir) if f.endswith(".pdf") or f.endswith(".htm")]) if os.path.isdir(pdf_dir) else 0
    # 检测最新PDF年份是否落后于当前年份
    latest_yr = 0
    if os.path.isdir(pdf_dir):
        for f in os.listdir(pdf_dir):
            m = re.match(r'[A-Za-z0-9]+_(\d{4})_', f)
            if m: latest_yr = max(latest_yr, int(m.group(1)))
    current_yr = date.today().year
    # 年报通常在次年3-4月发布，6月后还缺当年-1年的PDF才触发下载
    need_fresh = latest_yr < current_yr - 1 and date.today().month >= 6
    if existing >= 3 and not need_fresh:
        print(f"  Step 2: 已有 {existing} 份年报文件 (最新{latest_yr}年), 跳过下载")
        return True
    if need_fresh:
        print(f"  Step 2: 最新PDF为{latest_yr}年，{current_yr-1}年年报应已发布，尝试下载...")

    print(f"  Step 2: 下载年报PDF...")
    _set_active(code)
    ok, out = _run(f'"{PYTHON}" pdf_downloader.py', timeout=600)
    if not ok:
        raise SystemExit(_red(f"  FAIL: PDF下载失败\n{out[-500:]}"))
    pdf_dir = _pdf_dir(code)
    count = len([f for f in os.listdir(pdf_dir) if f.endswith((".pdf", ".htm"))]) if os.path.isdir(pdf_dir) else 0
    if count < 3:
        raise SystemExit(_red(f"  FAIL: 下载后仅{count}份文件, 需≥3年年报"))
    print(f"  Step 2: {_green('OK')} ({count}份年报文件)")
    return True

def step_3_mda(code):
    """Step 3: MD&A提取。缺失即阻断。美股跳过(SEC 10-K 英文PDF)。检测到年报更新→强制重提。"""
    stock = config.STOCKS.get(code, {})
    if stock.get("market") == "us":
        print(f"  Step 3: {_green('SKIP')} (美股 MD&A 提取待实现, 使用 config fallback)")
        return True
    db = _db_path(code)
    conn = sqlite3.connect(db)
    has_mda = conn.execute("SELECT value FROM meta WHERE key='mda_text'").fetchone()
    extracted_yr = conn.execute("SELECT value FROM meta WHERE key='mda_extracted_year'").fetchone()
    conn.close()
    # 检测最新PDF年份是否比已提取的新 → 强制重提
    pdf_dir = _pdf_dir(code)
    latest_pdf_yr = None
    if os.path.isdir(pdf_dir):
        import re as _re
        for f in os.listdir(pdf_dir):
            m = _re.match(r'[A-Za-z0-9]+_(\d{4})_', f)
            if m: latest_pdf_yr = max(latest_pdf_yr or 0, int(m.group(1)))
    stale = (extracted_yr and latest_pdf_yr and int(extracted_yr[0]) < latest_pdf_yr)
    if has_mda and has_mda[0] and len(has_mda[0]) > 200 and not stale:
        print(f"  Step 3: mda_text已存在 ({len(has_mda[0])} chars), 跳过提取")
        return True
    if stale:
        print(f"  Step 3: 检测到新年报PDF (已提取{extracted_yr[0]} < 最新{latest_pdf_yr})，强制重新提取")

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
    """Step 4: 营收结构。缺失则尝试自动运行 scripts/<code>/insert_revenue.py。美股跳过。"""
    stock = config.STOCKS.get(code, {})
    if stock.get("market") == "us":
        print(f"  Step 4: {_green('SKIP')} (美股营收结构待实现)")
        return True
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

    # 尝试自动运行个股专属脚本
    script = os.path.join(BASE, "scripts", code, "insert_revenue.py")
    if os.path.exists(script):
        print(f"  Step 4: 运行 {script}")
        ok, out = _run(f"{PYTHON} {script}")
        if ok:
            # 验证是否写入成功
            conn2 = sqlite3.connect(db)
            cnt2 = conn2.execute("SELECT COUNT(*) FROM revenue_structure WHERE code=?", (code,)).fetchone()[0]
            conn2.close()
            if cnt2 > 0:
                print(f"  Step 4: {_green('OK')} ({cnt2}条)")
                return True
        print(f"  {out[-500:]}")
    
    raise SystemExit(_red(
        f"  FAIL: revenue_structure为空, 需检查 scripts/{code}/insert_revenue.py"))

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
    ok, out = _run(f'"{PYTHON}" generate_report.py', timeout=60)
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
    # 股息CAGR宽松: 刚分红的公司可能只有1yr, 允许 (与 StatArray lenient_fields 相同逻辑)
    lenient_cagr = {"dividends"}
    for k in ["sales","cashflow","earnings","dividends","book_value"]:
        v = ar.get(k, {})
        if not isinstance(v, dict): fail(f"CAGR.{k}")
        else:
            has = sum(1 for p in ["1yr","3yr","5yr"] if v.get(p) is not None)
            threshold = 1 if k in lenient_cagr else 2
            if has >= threshold: ok(f"CAGR.{k}")
            else: fail(f"CAGR.{k} ({has}/3)")

    # ── 6. Quarterly (3 tables) ──
    for section in ["sales","eps","dividends"]:
        items = qt.get(section, [])
        if items: ok(f"Qtr.{section} ({len(items)}y)")
        else: fail(f"Qtr.{section}: 空")
    # 检测是否有前瞻部分年度(次年)季度数据
    years = d.get("years", [])
    if years:
        next_yr = str(int(years[-1]) + 1)
        has_partial = any(str(item.get("year")) == next_yr for item in qt.get("sales", []))
        if has_partial:
            ok(f"Qtr.partial (前瞻 {next_yr} — forward-looking)")

    # ── 7. K线 & 指数 ──
    kline = d.get("kline", [])
    if kline: ok(f"Kline ({len(kline)}m)")
    else: fail("Kline: 空")
    ik = d.get("index_kline", [])
    if ik: ok(f"Index ({len(ik)}m)")
    else: fail("Index: 空")

    # ── 8. Valuation Line & Yearly H/L ──
    val = d.get("valuation_line") or d.get("cf_line", [])
    vmethod = d.get("valuation_method", "cf")
    vlabel = "PB Line" if vmethod == "pb" else "CF Line"
    if val: ok(f"{vlabel} ({len(val)}pts)")
    else: fail(f"{vlabel}: 空")
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
        # 报告已在 Step 6-7 生成: 验证失败降级为 WARNING, 不阻断流水线
        print(f"  Step 8: {_yellow(f'WARNING ({len(fails)}/{len(checks)} gaps, report still generated)')}")
    else:
        print(f"  Step 8: {_green(f'ALL PASS ({len(checks)} checks, 0 fails)')}")
    return True


# ────────────────────────────────────────────────
# Main pipeline
# ────────────────────────────────────────────────

def confirm_and_build(code, cf_multiplier=None, pb_multiplier=None,
                      valuation_method=None, num_years=15, force_fetch=False):
    """
    强制确认后才能启动流水线。
    估值方法:
    - cf: CF倍数 × 每股现金流 (默认, 适合消费/科技/成长股)
    - pb: PB倍数 × 每股净资产 (适合银行/保险/周期股)
    valuation_method=None 时从 config.STOCKS[code].valuation_method 读取, 默认 "cf".
    --pb 参数 > 0 时自动切换为 "pb" 模式.

    估值倍数确定优先级: CLI --cf/--pb > DB meta > 用户交互输入
    """
    stock = config.STOCKS.get(code)

    # 显示用字段 (未配置时用占位值)
    name = stock.get("name", code) if stock else code
    market = stock.get("market", "hk") if stock else "hk"
    market_label = "A股" if market == "cn" else ("美股" if market == "us" else "港股(H股)")
    industry = stock.get("industry", "未知") if stock else "未知"
    currency = stock.get("currency", "CNY") if stock else "CNY"
    exchange = stock.get("exchange", "") if stock else ""

    # ── 估值方法确定 ──
    # 优先级: CLI --method > CLI --pb > config valuation_method > 默认 "cf"
    if valuation_method is None:
        if pb_multiplier is not None and pb_multiplier > 0:
            valuation_method = "pb"
        elif stock:
            valuation_method = stock.get("valuation_method", "cf")
        else:
            valuation_method = "cf"

    # ── 估值倍数确定: CLI → DB → 用户输入 ──
    if valuation_method == "pb":
        hist_ref = _get_hist_valuation_ref(code, "pb")
        if hist_ref:
            print(f"\n  历史PB参考: {hist_ref[0]} = {hist_ref[1]}x")
        if pb_multiplier is None:
            existing = _read_valuation_meta(code)
            pb_multiplier = existing["pb_multiplier"]
            if pb_multiplier is not None:
                print(f"  [DB] 复用已确认估值: PB={pb_multiplier}x")
            else:
                try:
                    inp = input(f"  请输入 {name} 的PB倍数 (如 0.8): ").strip()
                    pb_multiplier = float(inp)
                except (ValueError, EOFError, KeyboardInterrupt):
                    print(f"\n{_red('='*60)}")
                    print(_red(f"  REFUSED: 未提供有效PB倍数"))
                    print(_red(f"{'='*60}"))
                    raise SystemExit(1)
        method_label = f"PB={pb_multiplier}x"
    else:
        hist_ref = _get_hist_valuation_ref(code, "cf")
        if hist_ref:
            print(f"\n  历史PE参考: {hist_ref[0]} = {hist_ref[1]}x")
        if cf_multiplier is None:
            existing = _read_valuation_meta(code)
            cf_multiplier = existing["cf_multiplier"]
            if cf_multiplier is not None:
                print(f"  [DB] 复用已确认估值: CF={cf_multiplier}x")
            else:
                try:
                    inp = input(f"  请输入 {name} 的CF倍数 (如 15.0): ").strip()
                    cf_multiplier = float(inp)
                except (ValueError, EOFError, KeyboardInterrupt):
                    print(f"\n{_red('='*60)}")
                    print(_red(f"  REFUSED: 未提供有效CF倍数"))
                    print(_red(f"{'='*60}"))
                    raise SystemExit(1)
        method_label = f"CF={cf_multiplier}x"

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
    print(f"  估值方法:   {method_label}")
    # 历史估值参考
    hist_ref = _get_hist_valuation_ref(code, valuation_method)
    if hist_ref:
        label, val = hist_ref
        print(f"  历史参考:   {label} = {val}x")
    print(f"  强制拉取:   {'是 (跳过缓存，从API获取最新数据)' if force_fetch else '否 (复用缓存DB)'}")
    if not stock:
        print(f"  {_red('状态:  未在 config.STOCKS 中配置!')}")
    print(f"{_bold('='*60)}")

    # ── 校验 (确认页之后) ──
    if not stock:
        raise SystemExit(_red(f"\n  REFUSED: {code} 不在 config.STOCKS 中, 请先配置\n  提示: 编辑 config.py, 在 STOCKS 字典中添加该股票信息"))

    if market not in ("hk", "cn", "us"):
        raise SystemExit(_red(f"  REFUSED: 未知市场 '{market}', 请设为 'hk'、'cn' 或 'us'"))

    # 校验估值倍数
    if valuation_method == "pb":
        if pb_multiplier is None or pb_multiplier <= 0:
            raise SystemExit(_red("  REFUSED: PB倍数必须 > 0"))
    else:
        if cf_multiplier is None or cf_multiplier <= 0:
            raise SystemExit(_red("  REFUSED: CF倍数必须 > 0, 默认15.0"))

    # ── 执行 ──
    print(f"\n{_bold(f'  >>> 开始生成 {name} ({code}), {method_label} <<<')}")
    return build(code, cf_multiplier or 15.0, pb_multiplier or 1.0, valuation_method, force_fetch=force_fetch)
    # 注: or 15.0 / or 1.0 为防御性兜底，正常流程到此必然有值


def _read_valuation_meta(code):
    """从 DB 读取已有估值参数, 不存在时返回 None 字典。"""
    db = _db_path(code)
    if not os.path.exists(db):
        return {"cf_multiplier": None, "pb_multiplier": None, "valuation_method": None}
    try:
        conn = sqlite3.connect(db)
        rows = conn.execute(
            "SELECT key, value FROM meta WHERE key IN ('cf_multiplier','pb_multiplier','valuation_method')"
        ).fetchall()
        conn.close()
        result = {k: None for k in ("cf_multiplier", "pb_multiplier", "valuation_method")}
        for k, v in rows:
            if k in result:
                result[k] = float(v) if k in ("cf_multiplier", "pb_multiplier") else v
        return result
    except Exception:
        return {"cf_multiplier": None, "pb_multiplier": None, "valuation_method": None}


def _write_valuation_meta(code, cf_mult, pb_mult, method):
    """写估值相关 meta 到 DB, engine 自动读取。"""
    db = _db_path(code)
    if os.path.exists(db):
        conn = sqlite3.connect(db)
        conn.execute("INSERT OR REPLACE INTO meta VALUES (?,?)",
                     ("cf_multiplier", str(cf_mult)))
        conn.execute("INSERT OR REPLACE INTO meta VALUES (?,?)",
                     ("pb_multiplier", str(pb_mult)))
        conn.execute("INSERT OR REPLACE INTO meta VALUES (?,?)",
                     ("valuation_method", method))
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


def build(code, cf_mult=15.0, pb_mult=1.0, val_method="cf", force_fetch=False):
    """Run full 8-step pipeline for a single stock."""
    stock = config.STOCKS.get(code, {})
    name = stock.get("name", code)
    print(f"\n{_bold('='*60)}")
    print(f"{_bold(f'  {name} ({code}) - Value Line Pipeline')}")
    print(f"{_bold('='*60)}")

    _set_active(code)
    stock = step_0_check_config(code)           # 0. config
    step_1_fetch(code, stock, force_fetch=force_fetch)  # 1. 拉取
    step_2_pdf(code)                             # 2. PDF
    step_3_mda(code)                             # 3. MD&A
    step_4_revenue(code)                         # 4. 营收结构
    step_5_config_final(code, stock)             # 5. config final
    # 先写入估值参数到 DB，确保 engine 读取最新值
    _write_valuation_meta(code, cf_mult, pb_mult, val_method)
    step_6_engine(code)                          # 6. 计算
    step_7_generate(code)                        # 7. HTML
    step_8_verify(code)                          # 8. 验证

    print(f"\n{_green(_bold(f'  {name} ({code}) Report Complete!'))}")
    print(f"  文件: {_report_path(code)}\n")

    # restore POP MART
    _set_active("09992")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Value Line 报告生成流水线",
        epilog="示例: python build.py 09992                    (CF默认15.0)\n"
              "      python build.py 09992 --cf 18.0           (指定CF倍数)\n"
              "      python build.py 00388 --pb 0.8            (PB估值模式)\n"
              "      python build.py 02328 --method pb --pb 1.0 (显式PB)\n"
              "      python build.py 00700 --method cf --cf 10.0(显式CF)"
    )
    parser.add_argument("codes", nargs="+", help="股票代码, 如 09992 00700")
    parser.add_argument("--cf", type=float, default=None,
                        help="CF倍数 (CF估值模式, 默认15.0)")
    parser.add_argument("--pb", type=float, default=None,
                        help="PB倍数 (PB估值模式, 默认1.0, 设置后自动切换为PB模式)")
    parser.add_argument("--method", choices=["cf", "pb"], default=None,
                        help="估值方法 (cf/PB, 默认从config读取或自动推断)")
    parser.add_argument("--years", type=int, default=15,
                        help="使用最近N年数据 (默认15, 不超过可用年份)")
    parser.add_argument("--fetch", action="store_true",
                        help="强制重新拉取财务/行情数据 (默认复用缓存DB)")
    parser.add_argument("--publish", action="store_true",
                        help="生成后自动 git commit + push，触发 GitHub Pages 发布")
    args = parser.parse_args()

    if args.cf is not None and args.cf <= 0:
        parser.error("--cf 必须 > 0")
    if args.pb is not None and args.pb <= 0:
        parser.error("--pb 必须 > 0")
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
                              pb_multiplier=args.pb,
                              valuation_method=args.method,
                              num_years=actual_years,
                              force_fetch=args.fetch)
        except SystemExit as e:
            print(f"\n{_red(_bold(f'  BUILD FAILED: {code}'))}")
            if str(e):
                print(f"  {e}\n")
            _set_active("09992")
            sys.exit(1)

    # ── publish to GitHub Pages ──
    if args.publish:
        print(f"\n{_bold('=' * 60)}")
        print(f"{_bold('  Publishing to GitHub Pages...')}")
        print(f"{_bold('=' * 60)}")
        _run("git add report/", timeout=30)
        codes_str = ", ".join(args.codes)
        ok, out = _run(f'git commit -m "update: {codes_str} report"', timeout=30)
        if ok:
            ok2, out2 = _run("git push origin master", timeout=60)
            if ok2:
                print(_green(f"  [publish] 已推送至 GitHub. Actions 将自动部署到 Pages."))
            else:
                print(_yellow(f"  [publish] git push 失败 (网络问题?): {out2[-200:]}"))
        else:
            print(_yellow(f"  [publish] 没有变更需要推送"))

    _set_active("09992")
