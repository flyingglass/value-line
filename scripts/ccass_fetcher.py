# -*- coding: utf-8 -*-
"""
ccass_fetcher.py — 港交所 CCASS 席位持股数据抓取 / 入库

数据来源：港交所披露易「中央結算系統持股紀錄查詢服務」
    https://www.hkexnews.hk/sdw/search/searchsdw_c.aspx
公开页面，无需 API key、无需登录。

写入 data/<code>.db 的 ccass_holding 表（日频 × 席位粒度），
为现有基本面数据库补一个「日频资金面 / 筹码结构」维度。

表结构：
    ccass_holding(date, participant_id, participant_name, shares, pct, capital_type)
    PRIMARY KEY (date, participant_id)   -- 天然幂等，重复抓取安全覆盖

⚠️ 实现要点（均为实测结论，改动前请先读）
1. **必须用 GET + query，不是 POST**。该页是 ASP.NET WebForms，照常发 POST
   带 __VIEWSTATE 会原样返回条款页（长度 11251，与 GET 首页完全一致）。
2. **必须解析服务端回写的 txtShareholdingDate 作为真实日期**。非交易日（周末
   /假期）请求不会返回空，而是回退到最近一个有数据的日期，例如请求 2026/01/01
   返回 2025/12/31 的数据。若误用请求日期入库，会把 12/31 的数据错标成 01/01。
   用回写日期后，周末多个请求回退到同一天 → 同一主键 → 自动去重。
3. **逐行加总与页面「於中央結算系統的持股量」必须相等**，不等视为解析异常，
   拒绝入库（宁缺勿错）。00700 实测：419 行加总 = 7,055,842,143 = 页面汇总。
4. 数据窗口为**滚动 12 个月**，超出窗口返回空（实测 2025/09/01 已无数据）。
5. **只请求工作日**，不是省请求，而是避免灌入冗余快照：CCASS 周六记录的是
   前一日的日终数据，仅日期标签不同。实测请求 2026-08-29(六) 与 2026-08-28(五)
   返回的总持股完全相同（7,055,854,844）。周日则回退到周六的标签。
6. **北水是两个席位，必须合并看**：A00003 + A00004（沪深两个通道）。
   00700 @ 2026-09-01 实测合计 1,075,037,080 股，其中 A00004 占 43.2%，
   只统计一个席位会漏掉四成北水。入库时以 capital_type='northbound' 标记。

⚠️ 合规提示
港交所该页使用条款 2.3 禁止「以程序化手段、脚本或其他机械手段接入」，
2.2 禁止「據有關資料建立數據庫或目錄」。本模块仅供个人研究自用，
请勿对外分发数据或用于商业用途。

用法：
    python ccass_fetcher.py 00700                    # 增量：最近 7 天
    python ccass_fetcher.py 00700 --days 30          # 最近 30 个自然日
    python ccass_fetcher.py 00700 --full             # 回填 12 个月（很慢，见下）
    python ccass_fetcher.py 00700 --date 2026-09-01  # 单日
    python ccass_fetcher.py 00700 --summary          # 查看已入库概况

性能：服务端响应约 12 秒/次（350KB HTML，实测含 0.4s sleep 共 153s / 12 次）。
      --full 约 250 个交易日 → 单只标的约 50 分钟。可用 --workers 提速（有反爬风险）。
"""
import argparse
import os
import re
import sqlite3
import sys
import threading
import time
from datetime import date, datetime, timedelta

import requests

# ── 项目路径 ────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

try:
    from config import STOCKS
except ImportError:
    STOCKS = {}

# ── 端点 ────────────────────────────────────────────────────
SEARCH_URL = "https://www.hkexnews.hk/sdw/search/searchsdw_c.aspx"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")

# 无数据的页面长度（条款页，实测 11251）—— 用于快速判定抓取失败
_EMPTY_PAGE_LEN = 11251

TIMEOUT = 30

# ── 席位分类 ────────────────────────────────────────────────
# 保守原则：只标记可确证的类别，其余留空由使用者按席位名称自行判断，
# 不臆测席位背后的资金属性。
# 北水（港股通）在 CCASS 中集中登记于中国结算名下，且存在 A00003 / A00004
# 两个通道（沪深两个），分析时必须合并，只看一个会漏掉约四成北水。
_NORTHBOUND_PAT = re.compile(r"中國証券登記結算|中國證券登記結算|CHINA SECURITIES DEPOSITORY", re.I)


def classify_seat(name: str) -> str:
    """席位资金属性标记。仅北水可确证，其余返回空字符串。"""
    if name and _NORTHBOUND_PAT.search(name):
        return "northbound"
    return ""


# ── 解析正则 ────────────────────────────────────────────────
# 结果行形如：
#   <td class="col-participant-id">
#     <div class="mobile-list-heading">參與者編號:</div>
#     <div class="mobile-list-body">C00019</div>
#   </td>
_TR_RE = re.compile(r"<tr>(.*?)</tr>", re.S)


def _cell_re(col: str) -> re.Pattern:
    # col-shareholding 需负向排除 -percent，否则会误匹配 col-shareholding-percent
    return re.compile(r'class="col-%s(?!-percent)[^"]*">.*?mobile-list-body">(.*?)</div>' % col, re.S)


_ID_RE = _cell_re("participant-id")
_NAME_RE = _cell_re("participant-name")
_SHARES_RE = _cell_re("shareholding")
_PCT_RE = re.compile(r'class="col-shareholding-percent[^"]*">.*?mobile-list-body">(.*?)</div>', re.S)
# 服务端回写的真实持股日期（非交易日会被回退，必须以该值为准）
# 结果页与首屏的 input 属性顺序不同，两种都兼容
_DATE_RE = re.compile(r'id="txtShareholdingDate"[^>]*value="([^"]*)"')
_DATE_RE_ALT = re.compile(r'name="txtShareholdingDate"[^>]*value="([^"]*)"')
_TOTAL_RE = re.compile(r"於中央結算系統的持股量\s*([\d,]+)")


class RateLimiter:
    """全局节流器。并发模式下多个 worker 共享同一速率上限。"""

    def __init__(self, interval: float):
        self.interval = interval
        self._lock = threading.Lock()
        self._last = 0.0

    def wait(self) -> None:
        if self.interval <= 0:
            return
        with self._lock:
            now = time.monotonic()
            gap = now - self._last
            if 0 <= gap < self.interval:
                time.sleep(self.interval - gap)
            self._last = time.monotonic()


class CCASSFetcher:
    """
    CCASS 抓取器。
    ⚠️ requests.Session 不是线程安全的：--workers > 1 时必须每线程一个实例
    （见 _thread_fetcher），不可跨线程共享本对象。
    """

    def __init__(self, sleep: float = 0.5, timeout: int = TIMEOUT):
        self.sleep = sleep
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": UA, "Referer": SEARCH_URL})
        # 首屏请求建立 cookie（Akamai bm_s / bm_so）
        self.session.get(SEARCH_URL, timeout=timeout)

    def fetch_date(self, code: str, d: date) -> dict:
        """
        抓取单个日期。返回:
            {"date": "2026-09-01", "total": 7055842143, "rows": [...], "ok": True}
        无数据 / 解析异常时 ok=False，并附 reason。
        注意返回的 date 是服务端回写的真实日期，可能不等于请求的 d。
        """
        params = {
            "__EVENTTARGET": "btnSearch", "__EVENTARGUMENT": "",
            "today": d.strftime("%Y%m%d"),
            "sortBy": "shareholding", "sortDirection": "desc",
            "alertMsg": "",
            "txtShareholdingDate": d.strftime("%Y/%m/%d"),
            "txtStockCode": code,
            "txtStockName": "", "txtParticipantID": "",
            "txtParticipantName": "", "txtSelPartID": "",
        }
        try:
            resp = self.session.get(SEARCH_URL, params=params, timeout=self.timeout)
        except requests.RequestException as e:
            return {"ok": False, "reason": f"request failed: {e}"}
        if resp.status_code != 200:
            return {"ok": False, "reason": f"HTTP {resp.status_code}"}

        html = resp.text
        if len(html) <= _EMPTY_PAGE_LEN + 64:
            return {"ok": False, "reason": "empty page (out of 12M window or invalid code)"}

        m = _DATE_RE.search(html) or _DATE_RE_ALT.search(html)
        if not m:
            return {"ok": False, "reason": "cannot locate shareholding date field"}
        real_date = m.group(1).replace("/", "-")

        rows = []
        for tr in _TR_RE.findall(html):
            mid = _ID_RE.search(tr)
            if not mid:
                continue
            pid = mid.group(1).strip()
            if not pid:
                continue
            mname = _NAME_RE.search(tr)
            msh = _SHARES_RE.search(tr)
            mpct = _PCT_RE.search(tr)
            try:
                shares = int((msh.group(1) if msh else "0").replace(",", "").strip() or 0)
            except ValueError:
                continue
            pct_raw = (mpct.group(1) if mpct else "0").replace("%", "").strip()
            try:
                pct = float(pct_raw or 0)
            except ValueError:
                pct = 0.0
            name = (mname.group(1) if mname else "").strip()
            rows.append({
                "participant_id": pid,
                "participant_name": name,
                "shares": shares,
                "pct": pct,
                "capital_type": classify_seat(name),
            })

        if not rows:
            # CCASS 为 T+1 发布：当日数据次日才可得；超出 12 个月滚动窗口同样为空。
            # 实测 2026-09-02 当日查询返回 0 行，页面含 checkShareholdingDate="true"。
            return {"ok": False,
                    "reason": "no data (T+1 not published yet, or out of 12M window)"}

        # 自洽校验：逐行加总必须等于页面汇总，否则拒绝入库
        txt = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html))
        mt = _TOTAL_RE.search(txt)
        total = int(mt.group(1).replace(",", "")) if mt else None
        row_sum = sum(r["shares"] for r in rows)
        if total is not None and total != row_sum:
            return {"ok": False,
                    "reason": f"total mismatch: page={total:,} sum={row_sum:,}"}

        return {"ok": True, "date": real_date, "total": total if total is not None else row_sum,
                "rows": rows}

    def fetch_range(self, code: str, start: date, end: date, skip_weekend: bool = True):
        """按日抓取区间，yield (requested_date, result)。"""
        d = start
        while d <= end:
            if not (skip_weekend and d.weekday() >= 5):
                yield d, self.fetch_date(code, d)
                time.sleep(self.sleep)
            d += timedelta(days=1)


# ── 数据库 ──────────────────────────────────────────────────

def db_path(code: str) -> str:
    return os.path.join(DATA_DIR, f"{code}.db")


def init_table(conn: sqlite3.Connection) -> None:
    conn.execute("""CREATE TABLE IF NOT EXISTS ccass_holding (
        date TEXT,
        participant_id TEXT,
        participant_name TEXT,
        shares INTEGER,
        pct REAL,
        capital_type TEXT DEFAULT '',
        PRIMARY KEY (date, participant_id))""")
    # 按席位查时间序列：WHERE participant_id=? ORDER BY date
    conn.execute("CREATE INDEX IF NOT EXISTS idx_ccass_seat ON ccass_holding(participant_id, date)")
    conn.execute("CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT)")
    conn.commit()


def save_day(conn: sqlite3.Connection, res: dict) -> int:
    """写入单日。返回写入行数。"""
    d = res["date"]
    conn.executemany(
        "INSERT OR REPLACE INTO ccass_holding "
        "(date, participant_id, participant_name, shares, pct, capital_type) "
        "VALUES (?,?,?,?,?,?)",
        [(d, r["participant_id"], r["participant_name"], r["shares"], r["pct"], r["capital_type"])
         for r in res["rows"]])
    conn.commit()
    return len(res["rows"])


def set_meta(conn: sqlite3.Connection, key: str, value: str) -> None:
    conn.execute("INSERT OR REPLACE INTO meta VALUES (?,?)", (key, value))
    conn.commit()


def get_meta(conn: sqlite3.Connection, key: str):
    r = conn.execute("SELECT value FROM meta WHERE key=?", (key,)).fetchone()
    return r[0] if r else None


def refresh_meta(conn: sqlite3.Connection) -> None:
    r = conn.execute("SELECT MIN(date), MAX(date), COUNT(DISTINCT date) FROM ccass_holding").fetchone()
    if r and r[0]:
        set_meta(conn, "ccass_earliest_date", r[0])
        set_meta(conn, "ccass_latest_date", r[1])
        set_meta(conn, "ccass_days", str(r[2]))
    set_meta(conn, "ccass_updated_at", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


# ── 查询辅助 ────────────────────────────────────────────────

def seat_series(conn: sqlite3.Connection, participant_id: str):
    """单席位持股时间序列。"""
    return conn.execute(
        "SELECT date, shares, pct FROM ccass_holding WHERE participant_id=? ORDER BY date",
        (participant_id,)).fetchall()


def top_holders(conn: sqlite3.Connection, d: str, limit: int = 10):
    """某日持股量 Top N。"""
    return conn.execute(
        "SELECT participant_id, participant_name, shares, pct, capital_type "
        "FROM ccass_holding WHERE date=? ORDER BY shares DESC LIMIT ?",
        (d, limit)).fetchall()


def daily_total(conn: sqlite3.Connection):
    """CCASS 每日总持股与参与者数（判断托管率 / 资金进出总量）。"""
    return conn.execute(
        "SELECT date, SUM(shares), COUNT(*) FROM ccass_holding GROUP BY date ORDER BY date").fetchall()


def seat_delta(conn: sqlite3.Connection, end: str, start: str, limit: int = 10):
    """两日之间席位净变动 Top N（识别谁在真买 / 真卖）。"""
    return conn.execute(
        "SELECT e.participant_id, e.participant_name, s.shares, e.shares, "
        "  (e.shares - s.shares) AS delta "
        "FROM ccass_holding e JOIN ccass_holding s "
        "  ON e.participant_id = s.participant_id "
        "WHERE e.date = ? AND s.date = ? "
        "ORDER BY ABS(e.shares - s.shares) DESC LIMIT ?",
        (end, start, limit)).fetchall()


# ── CLI ─────────────────────────────────────────────────────

def _is_hk(code: str) -> bool:
    info = STOCKS.get(code)
    if info:
        return info.get("market") == "hk"
    return code.isdigit() and len(code) == 5


def _seat_group(name: str) -> str:
    """
    席位粗分组，仅用于结构性统计（看清哪类资金在动）。
    ⚠️ 这是按名称关键词的粗略归类，不是官方分类：
       - 「券商席位」含客户仓与自营，不等于该机构自己在看多
       - 「托管行」背后是各路基金，不代表银行自身持仓
    """
    u = name.upper()
    if _NORTHBOUND_PAT.search(name):
        return "northbound"
    if "銀行" in name or any(k in u for k in ("BANK", "CUSTOD", "NOMINEES")):
        return "custody_bank"
    if "證券" in name or "SECURITIES" in u:
        return "broker"
    return "other"


def cmd_trend(conn: sqlite3.Connection, code: str,
              d0: str = None, d1: str = None) -> None:
    """持仓变化趋势：分组净变动 + 席位增减榜 + 每日净变动。"""
    d1 = d1 or get_meta(conn, "ccass_latest_date")
    d0 = d0 or get_meta(conn, "ccass_earliest_date")
    if not (d0 and d1):
        print(f"{code}: 无 CCASS 数据")
        return

    rows = conn.execute(
        "SELECT h.participant_id, h.participant_name, h.shares, COALESCE(a.shares, 0) "
        "FROM ccass_holding h LEFT JOIN ccass_holding a "
        "  ON a.participant_id = h.participant_id AND a.date = ? "
        "WHERE h.date = ?", (d0, d1)).fetchall()
    if not rows:
        print(f"{code}: {d1} 无数据")
        return

    print(f"=== {code} 持仓变化趋势  {d0} -> {d1} ===")

    g = {}
    for pid, name, end, start in rows:
        t = g.setdefault(_seat_group(name), [0, 0, 0])
        t[0] += 1
        t[1] += start
        t[2] += end

    print("\n[分组净变动]")
    for k, (cnt, s, e) in sorted(g.items(), key=lambda x: -abs(x[1][2] - x[1][1])):
        pct = (e - s) / s * 100 if s else 0
        print(f"  {k:14} 席位{cnt:4}  {s:>15,} -> {e:>15,}  {e - s:+,}  {pct:+.2f}%")

    rs = sorted(rows, key=lambda r: -(r[2] - r[3]))
    print("\n[净增持 Top 8]")
    for pid, name, e, s in rs[:8]:
        tag = "  (期间新增)" if s == 0 else ""
        print(f"  {pid:7} {name[:26]:26} {s:>13,} -> {e:>13,}  {e - s:+,}{tag}")
    print("\n[净减持 Top 8]")
    for pid, name, e, s in rs[-8:]:
        print(f"  {pid:7} {name[:26]:26} {s:>13,} -> {e:>13,}  {e - s:+,}")

    print("\n[每日净变动]")
    prev = None
    for d, tot in conn.execute(
            "SELECT date, SUM(shares) FROM ccass_holding GROUP BY date ORDER BY date"):
        delta = f"{tot - prev:+,}" if prev is not None else "          -"
        print(f"  {d}  {tot:>15,}  {delta}")
        prev = tot


def cmd_summary(code: str) -> None:
    path = db_path(code)
    if not os.path.exists(path):
        print(f"[!] 数据库不存在: {path}")
        return
    conn = sqlite3.connect(path)
    try:
        n = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='ccass_holding'").fetchone()
        if not n:
            print(f"{code}: 尚未抓取 CCASS 数据（ccass_holding 表不存在）")
            return
        earliest = get_meta(conn, "ccass_earliest_date")
        latest = get_meta(conn, "ccass_latest_date")
        days = get_meta(conn, "ccass_days")
        print(f"=== {code} CCASS 概况 ===")
        print(f"  日期范围: {earliest} ~ {latest}  ({days} 天)")
        print(f"  更新时间: {get_meta(conn, 'ccass_updated_at')}")
        if latest:
            print(f"\n  Top 10 席位 @{latest}:")
            for pid, name, sh, pct, ct in top_holders(conn, latest, 10):
                tag = f"[{ct}]" if ct else "      "
                print(f"    {pid:7} {tag:9} {name[:30]:30} {sh:>15,}  {pct:>6}%")
            nb = conn.execute(
                "SELECT SUM(shares) FROM ccass_holding WHERE date=? AND capital_type='northbound'",
                (latest,)).fetchone()[0]
            if nb:
                print(f"\n  北水合计(沪深双通道): {nb:,}")
    finally:
        conn.close()


def main() -> None:
    ap = argparse.ArgumentParser(description="抓取港交所 CCASS 席位持股数据并入库")
    ap.add_argument("code", help="港股代码，如 00700")
    ap.add_argument("--date", help="只抓单日 (YYYY-MM-DD)")
    ap.add_argument("--days", type=int, default=7, help="最近 N 个自然日（默认 7）")
    ap.add_argument("--full", action="store_true", help="回填滚动 12 个月（约 250 个交易日，很慢）")
    ap.add_argument("--since", help="从指定日期抓到今天 (YYYY-MM-DD)")
    ap.add_argument("--until", help="抓取截止日期，配合 --since/--full 分段跑 (YYYY-MM-DD)")
    ap.add_argument("--sleep", type=float, default=0.5, help="请求间隔秒（默认 0.5）")
    ap.add_argument("--timeout", type=int, default=TIMEOUT)
    ap.add_argument("--workers", type=int, default=1, help="并发数，>1 有触发反爬风险（默认 1）")
    ap.add_argument("--summary", action="store_true", help="只查看已入库概况，不抓取")
    ap.add_argument("--trend", action="store_true", help="查看持仓变化趋势（分组净变动/增减榜/每日净变动）")
    ap.add_argument("--from", dest="trend_from", help="趋势起始日期，配合 --trend")
    ap.add_argument("--to", dest="trend_to", help="趋势结束日期，配合 --trend")
    args = ap.parse_args()

    code = args.code.zfill(5) if args.code.isdigit() else args.code
    if not _is_hk(code):
        print(f"[!] {code} 不是港股（CCASS 仅适用于港股）")
        sys.exit(1)

    if args.summary:
        cmd_summary(code)
        return

    if args.trend:
        _p = db_path(code)
        if not os.path.exists(_p):
            print(f"[!] 数据库不存在: {_p}")
            sys.exit(1)
        _conn = sqlite3.connect(_p)
        try:
            cmd_trend(_conn, code, args.trend_from, args.trend_to)
        finally:
            _conn.close()
        return

    today = date.today()
    if args.date:
        targets = [datetime.strptime(args.date, "%Y-%m-%d").date()]
    elif args.since:
        targets = None
        start = datetime.strptime(args.since, "%Y-%m-%d").date()
    elif args.full:
        start = today - timedelta(days=365)
        targets = None
    else:
        start = today - timedelta(days=args.days)
        targets = None

    path = db_path(code)
    if not os.path.exists(path):
        print(f"[!] 数据库不存在: {path}（请先跑 fetcher.py 建立标的库）")
        sys.exit(1)

    conn = sqlite3.connect(path)
    init_table(conn)

    # 增量下界：仅默认模式（--days）应用。
    # 显式 --since / --full 视为「补齐历史缺口」的意图，不套用下界，
    # 从头重抓（写入幂等，重复抓取安全覆盖）。
    if targets is None and not (args.since or args.full):
        latest = get_meta(conn, "ccass_latest_date")
        if latest:
            lb = datetime.strptime(latest, "%Y-%m-%d").date() + timedelta(days=1)
            if lb > start:
                print(f"  增量模式：库中已有至 {latest}，从 {lb} 开始")
                start = lb

    # 展开为工作日列表（周末请求会回退到同一天，不重复请求）
    end = today
    if args.until:
        end = datetime.strptime(args.until, "%Y-%m-%d").date()
    if targets is None:
        if start > end:
            print(f"  起始日 {start} 晚于截止日 {end}，无需抓取")
            conn.close()
            return
        targets = []
        d = start
        while d <= end:
            if d.weekday() < 5:
                targets.append(d)
            d += timedelta(days=1)

    if not targets:
        print("  区间内没有工作日，无需抓取")
        conn.close()
        return

    # 12.8s 为实测均值（含服务端延迟），仅用于预估
    est = len(targets) * 12.8 / max(args.workers, 1)
    print(f"=== CCASS {code}: {len(targets)} 个日期 "
          f"({targets[0]} ~ {targets[-1]})，预计 {est / 60:.1f} 分钟 ===")

    limiter = RateLimiter(args.sleep)
    saved, skipped, failed = 0, 0, 0
    seen_dates = set()

    if args.workers > 1:
        from concurrent.futures import ThreadPoolExecutor
        _tls = threading.local()

        def _thread_fetcher() -> "CCASSFetcher":
            """每线程独立 session —— requests.Session 非线程安全，不可共享。"""
            f = getattr(_tls, "fetcher", None)
            if f is None:
                f = CCASSFetcher(timeout=args.timeout)
                _tls.fetcher = f
            return f

        def _task(d):
            limiter.wait()
            return _thread_fetcher().fetch_date(code, d)

        with ThreadPoolExecutor(max_workers=args.workers) as ex:
            results = list(ex.map(_task, targets))
        pairs = list(zip(targets, results))
    else:
        fetcher = CCASSFetcher(timeout=args.timeout)
        pairs = []
        for d in targets:
            limiter.wait()
            pairs.append((d, fetcher.fetch_date(code, d)))

    for req_d, res in pairs:
        if not res.get("ok"):
            failed += 1
            print(f"  {req_d}: SKIP ({res.get('reason')})")
            continue
        real = res["date"]
        if real in seen_dates:
            skipped += 1
            print(f"  {req_d} -> {real}: 重复快照，跳过")
            continue
        seen_dates.add(real)
        n = save_day(conn, res)
        saved += 1
        print(f"  {req_d} -> {real}: {n} 席位，总持股 {res['total']:,}")

    refresh_meta(conn)
    conn.close()
    print(f"\n完成：写入 {saved} 天，重复跳过 {skipped} 天，失败/无数据 {failed} 天")


if __name__ == "__main__":
    main()
