# -*- coding: utf-8 -*-
"""ai_sw_us.py — 拉取《大模型吞噬软件》原文点名的 8 家美股软件公司的 FY 数据

出处：raw/research/articles/2026-09-24-庶人哑士-大模型吞噬软件-是叙事还是事实.md
      「无论是美股的 Palantir、SAP、Salesforce、Hubspot、Workday、Datadog、
        Snowflake、Cloudflare……它们都在积极拥抱 AI」

数据源：WeStock Data CLI（npx westock-data-clawhub@1.0.4），与 scripts/fetch_us_westock.py 同源。
⚠️ 该源在本机（2026-09-24 拉取）**最新只到 2025-12-31**，滞后约 3 个季度，
   因此本脚本输出的是 FY2025 vs FY2024，不能与 A/H 股的 26H1 直接比较。

用法：
  .venv\\Scripts\\python scripts\\ai_sw_us.py            # 全量（并发 4）
  .venv\\Scripts\\python scripts\\ai_sw_us.py --only PLTR # 只跑一只（调试）

输出：scripts/out/ai_sw_us.csv
"""
import argparse
import csv
import os
import subprocess
import sys
import threading
import time

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

_HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(_HERE, "out")
CSV_PATH = os.path.join(OUT_DIR, "ai_sw_us.csv")

WESTOCK_CMD = "npx -y westock-data-clawhub@1.0.4"

# 原文点名的 8 家美股（按原文出现顺序）
TARGETS = [
    ("PLTR", "Palantir"),
    ("SAP", "SAP"),
    ("CRM", "Salesforce"),
    ("HUBS", "Hubspot"),
    ("WDAY", "Workday"),
    ("DDOG", "Datadog"),
    ("SNOW", "Snowflake"),
    ("NET", "Cloudflare"),
]

UNIT_M = 1_000_000  # westock 金额单位：百万美元

_lock = threading.Lock()
results = {}


def _run(sub, timeout=180):
    try:
        r = subprocess.run("%s %s" % (WESTOCK_CMD, sub), shell=True,
                           capture_output=True, text=True, timeout=timeout,
                           encoding="utf-8", errors="replace")
        return r.stdout or ""
    except Exception as e:
        print("    [ERR] %s: %s" % (sub, type(e).__name__))
        return ""


def _table(text):
    lines = [l for l in (text or "").strip().split("\n") if l.strip().startswith("|")]
    if len(lines) < 3:
        return []
    hdr = [c.strip() for c in lines[0].split("|")[1:-1]]
    out = []
    for ln in lines[2:]:
        cs = [c.strip() for c in ln.split("|")[1:-1]]
        if len(cs) != len(hdr):
            continue
        out.append(dict(zip(hdr, cs)))
    return out


def _f(v):
    try:
        if v in ("-", "", None):
            return None
        return float(str(v).replace(",", ""))
    except (ValueError, TypeError):
        return None


def fetch_one(code, name):
    print("  [%s] income ..." % code)
    inc = _table(_run("finance us%s --type income --num 24" % code))
    print("  [%s] balance ..." % code)
    bal = _table(_run("finance us%s --type balance --num 8" % code))
    print("  [%s] kline ..." % code)
    kl = _table(_run("kline us%s --period day --limit 3" % code))
    time.sleep(0.3)

    row = {"code": code, "name": name, "ok": False}

    # 年报（EndDate 以 12-31 结尾 → 累计口径可用）
    ann = sorted([d for d in inc if d.get("EndDate", "").endswith("12-31")],
                 key=lambda d: d["EndDate"])
    if len(ann) >= 2:
        cur, prev = ann[-1], ann[-2]
        row["fy_cur"], row["fy_prev"] = cur["EndDate"], prev["EndDate"]
        for key, col in (("rev", "Sales"), ("gm", "GrossMargin"),
                         ("ni", "NetIncome"), ("eps", "BasicEPS")):
            row[key + "_cur"] = _f(cur.get(col))
            row[key + "_prev"] = _f(prev.get(col))

        def yoy(a, b):
            if a is None or b in (None, 0):
                return None
            return round((a - b) / abs(b) * 100, 2)
        row["rev_yoy"] = yoy(row.get("rev_cur"), row.get("rev_prev"))
        row["ni_yoy"] = yoy(row.get("ni_cur"), row.get("ni_prev"))
        if row.get("gm_cur") is not None and row.get("gm_prev") is not None:
            row["gm_chg_pp"] = round(row["gm_cur"] - row["gm_prev"], 2)

        # 单位换算：营收/净利 百万美元 → 亿美元
        for k in ("rev_cur", "rev_prev", "ni_cur", "ni_prev"):
            if row.get(k) is not None:
                row[k] = round(row[k] / 100.0, 3)
        row["ok"] = True

    # 净资产 / BPS → 反推股本 → 市值
    bal_ann = sorted([d for d in bal if d.get("EndDate", "").endswith("12-31")],
                     key=lambda d: d["EndDate"])
    if bal_ann and row.get("fy_cur"):
        d = bal_ann[-1]
        eq = _f(d.get("TotalEquity")) or _f(d.get("CommonStockEquity"))
        bps = _f(d.get("BPS"))
        if eq and bps:
            shares_m = eq * UNIT_M / bps          # 股数
            row["shares_m"] = round(shares_m / 1e6, 2)   # 百万股
            # 市值在拿到股价后算
            row["_shares"] = shares_m

    if kl:
        row["price_date"] = kl[-1].get("date", "")
        row["price"] = _f(kl[-1].get("last")) or _f(kl[-1].get("close"))
    if row.get("price") and row.get("_shares"):
        row["mktcap_bn_usd"] = round(row["price"] * row["_shares"] / 1e9, 2)
    row.pop("_shares", None)

    print("  [%s] done ok=%s rev_cur=%s gm=%s chg=%s" % (
        code, row["ok"], row.get("rev_cur"), row.get("gm_cur"), row.get("gm_chg_pp")))
    return row


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", help="只跑指定代码")
    ap.add_argument("--workers", type=int, default=4)
    args = ap.parse_args()

    os.makedirs(OUT_DIR, exist_ok=True)
    targets = TARGETS
    if args.only:
        targets = [t for t in TARGETS if t[0] == args.only.upper()]
        if not targets:
            raise SystemExit("未找到 %s" % args.only)

    print("== 拉取原文点名的 %d 家美股 ==" % len(targets))

    def worker(chunk):
        for code, name in chunk:
            try:
                row = fetch_one(code, name)
            except Exception as e:
                row = {"code": code, "name": name, "ok": False,
                       "err": "%s: %s" % (type(e).__name__, e)}
            with _lock:
                results[code] = row

    n = max(1, min(args.workers, len(targets)))
    chunks = [targets[i::n] for i in range(n)]
    ts = [threading.Thread(target=worker, args=(c,)) for c in chunks]
    for t in ts:
        t.start()
    for t in ts:
        t.join()

    rows = [results[c] for c, _ in targets if c in results]
    fields = ["code", "name", "fy_cur", "fy_prev", "rev_cur", "rev_prev", "rev_yoy",
              "ni_cur", "ni_prev", "ni_yoy", "gm_cur", "gm_prev", "gm_chg_pp",
              "eps_cur", "price", "price_date", "shares_m", "mktcap_bn_usd", "ok", "err"]
    with open(CSV_PATH, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    print("\n已写入 %s（%d 行）" % (CSV_PATH, len(rows)))

    print("\n%-6s %-11s %10s %10s %8s %8s %8s %8s" % (
        "代码", "名称", "FY营收$亿", "同比%", "毛利率%", "Δpp", "股价", "市值$亿"))
    for r in rows:
        fmt = lambda v, d=1: "-" if v is None else round(v, d)
        print("%-6s %-11s %10s %10s %8s %8s %8s %8s" % (
            r["code"], r["name"],
            fmt(r.get("rev_cur"), 1), fmt(r.get("rev_yoy")),
            fmt(r.get("gm_cur")), fmt(r.get("gm_chg_pp"), 2),
            fmt(r.get("price"), 2),
            "-" if not r.get("mktcap_bn_usd") else round(r["mktcap_bn_usd"] * 10, 1)))


if __name__ == "__main__":
    main()
