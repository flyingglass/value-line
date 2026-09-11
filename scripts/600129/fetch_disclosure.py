# -*- coding: utf-8 -*-
"""fetch_disclosure.py — 拉取太极集团(600129) 定期报告披露日 / 业绩预告日

用途：案例页《里海案例-太极集团》第二节「事件时间线」业绩列的数据底座。
数据源：AKShare `stock_zh_a_disclosure_report_cninfo`（巨潮资讯，公告标题 + 归档时间 + 公告链接）
输出：data/disclosure/600129_disclosure.json
    {"disclosures": [{date, title, category, url}]}   # date = 巨潮归档日
用法：.venv\\Scripts\\python scripts\\600129\\fetch_disclosure.py [--force]
说明：接口单次只返回第一页，故按「年 × 类别」分段拉取；同一公告被多类别命中时按 (date,title) 去重。
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
OUT = os.path.join(BASE, "data", "disclosure", "600129_disclosure.json")
CODE = "600129"
START, END = "20170101", "20260911"

CATEGORIES = ["年报", "半年报", "一季报", "三季报", "业绩预告", "业绩快报"]
# 注：2021 年及以前定期报告标题为「第一季度报告/第三季度报告」，2022 年起改为
#     「一季度报告/三季度报告」，两套写法都要收。
KEEP_KEYWORDS = ["年度报告", "半年度报告", "季度报告", "业绩预告", "业绩快报"]


def fetch_disclosures():
    rows = []
    for year in range(2017, 2027):
        s, e = "%d0101" % year, "%d1231" % year
        for cat in CATEGORIES:
            try:
                df = ak.stock_zh_a_disclosure_report_cninfo(
                    symbol=CODE, market="沪深京", category=cat,
                    start_date=s, end_date=e,
                )
            except Exception as ex:
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

    seen, uniq = set(), []
    for r in sorted(rows, key=lambda x: (x["date"], x["title"])):
        key = (r["date"], r["title"])
        if key in seen:
            continue
        seen.add(key)
        uniq.append(r)
    return uniq


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true", help="忽略缓存重新拉取")
    args = ap.parse_args()

    if os.path.exists(OUT) and not args.force:
        print("缓存已存在：%s（--force 可强制刷新）" % OUT)
        return

    print("拉取 %s 定期报告披露日 / 业绩预告 ..." % CODE)
    disc = fetch_disclosures()
    print("  合计 %d 条" % len(disc))

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with io.open(OUT, "w", encoding="utf-8") as f:
        json.dump({"disclosures": disc}, f, ensure_ascii=False, indent=1)
    print("已写入 %s" % OUT)


if __name__ == "__main__":
    main()
