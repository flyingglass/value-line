# -*- coding: utf-8 -*-
"""fetch_disclosure.py — 拉取涪陵榨菜(002507) 定期报告披露日 / 业绩预告日 / 未复权日K

用途：战略股复盘图的数据底座（股价 × 业绩公告时点）。
数据源：AKShare
  · stock_zh_a_disclosure_report_cninfo — 巨潮公告标题+公告时间（年报/半年报/一季报/三季报/业绩预告）
  · stock_zh_a_hist (adjust="") — 未复权日K（用于还原当年真实成交价，对齐里海买卖点）

输出：data/disclosure/002507_disclosure.json
    {
      "disclosures": [{date, title, category, url}],
      "kline_raw":    [{date, open, high, low, close, volume}]
    }

用法：.venv\\Scripts\\python scripts\\002507\\fetch_disclosure.py [--force]
"""
import io
import json
import os
import sys
import time
import argparse

import akshare as ak

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(BASE, "data", "disclosure", "002507_disclosure.json")
CODE = "002507"
START, END = "20150101", "20260911"

CATEGORIES = ["年报", "半年报", "一季报", "三季报", "业绩预告", "业绩快报"]
# 注：2021 年及以前定期报告标题为「第一季度报告/第三季度报告」，
#     2022 年起改为「一季度报告/三季度报告」，两套写法都要收。
KEEP_KEYWORDS = ["年度报告", "半年度报告", "季度报告", "业绩预告", "业绩快报"]


def fetch_disclosures():
    """按年分段查询（接口单次只返回第一页，分段可拿全量）。"""
    rows = []
    for year in range(2015, 2027):
        s, e = "%d0101" % year, "%d1231" % year
        for cat in CATEGORIES:
            try:
                df = ak.stock_zh_a_disclosure_report_cninfo(
                    symbol=CODE, market="沪深京", category=cat,
                    start_date=s, end_date=e,
                )
            except Exception as ex:
                if "业绩快报" not in cat:
                    print("  [warn] %d %s 失败: %s: %s" % (year, cat, type(ex).__name__, ex))
                continue
            n0 = len(rows)
            for _, r in df.iterrows():
                title = str(r.get("公告标题", "")).strip()
                if not any(k in title for k in KEEP_KEYWORDS):
                    continue
                rows.append({
                    "date": str(r.get("公告时间", ""))[:10],
                    "title": title,
                    "category": cat,
                    "url": str(r.get("公告链接", "")),
                })
            if len(rows) > n0:
                print("  %d %s: +%d" % (year, cat, len(rows) - n0))
            time.sleep(0.3)

    # 去重（同一公告可能被多个 category 命中）
    seen, uniq = set(), []
    for r in sorted(rows, key=lambda x: (x["date"], x["title"])):
        key = (r["date"], r["title"])
        if key in seen:
            continue
        seen.add(key)
        uniq.append(r)
    return uniq


def fetch_kline_raw():
    df = ak.stock_zh_a_hist(symbol=CODE, period="daily",
                            start_date=START, end_date=END, adjust="")
    out = []
    for _, r in df.iterrows():
        out.append({
            "date": str(r["日期"])[:10],
            "open": float(r["开盘"]), "high": float(r["最高"]),
            "low": float(r["最低"]), "close": float(r["收盘"]),
            "volume": float(r["成交量"]),
        })
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true", help="忽略缓存重新拉取")
    args = ap.parse_args()

    if os.path.exists(OUT) and not args.force:
        print("缓存已存在：%s（--force 可强制刷新）" % OUT)
        return

    print("拉取定期报告披露日 / 业绩预告 ...")
    disc = fetch_disclosures()
    print("  合计 %d 条" % len(disc))

    print("拉取未复权日K ...")
    try:
        kl = fetch_kline_raw()
        print("  %d 根（%s ~ %s）" % (len(kl), kl[0]["date"], kl[-1]["date"]))
    except Exception as e:
        kl = []
        print("  [warn] 未复权日K 拉取失败：%s: %s（不影响主图，复权口径以 db 为准）" % (type(e).__name__, e))

    with io.open(OUT, "w", encoding="utf-8") as f:
        json.dump({"disclosures": disc, "kline_raw": kl}, f, ensure_ascii=False, indent=1)
    print("已写入 %s" % OUT)


if __name__ == "__main__":
    main()
