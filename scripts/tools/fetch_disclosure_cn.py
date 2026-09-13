# -*- coding: utf-8 -*-
"""fetch_disclosure_cn.py — 通用：拉 A 股标的定期报告披露日 / 业绩预告日（巨潮 cninfo）

用途：里海案例页「事件时间线」业绩列 + 周K复盘图「披露带」的数据底座。
数据源：AKShare `stock_zh_a_disclosure_report_cninfo`（巨潮资讯，公告标题 + 归档时间 + 公告链接）
输出：data/disclosure/<code>_disclosure.json
    {"disclosures": [{date, title, category, url}]}   # date = 巨潮归档日

用法：
  .venv\\Scripts\\python scripts\\tools\\fetch_disclosure_cn.py 000830
  .venv\\Scripts\\python scripts\\tools\\fetch_disclosure_cn.py 000830 --start 20150101 --force
说明：接口单次只返回第一页，故按「年 × 类别」分段拉取；同一公告被多类别命中时按 (date,title) 去重。
      2021 年及以前定期报告标题为「第一季度报告/第三季度报告」，2022 年起改为「一季度报告/三季度报告」，两套写法都收。
"""
import argparse
import io
import json
import os
import sys
import time

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# 本机系统代理会导致 akshare 部分接口 RemoteDisconnected，与 fetcher.py 同法禁用代理
for _k in list(os.environ.keys()):
    if any(x in _k.upper() for x in ("PROXY", "HTTP_", "HTTPS_", "ALL_PROXY")):
        os.environ.pop(_k, None)

import requests as _rq
_orig_init = _rq.Session.__init__
def _patched_init(self):
    _orig_init(self)
    self.trust_env = False
    self.proxies = {}
_rq.Session.__init__ = _patched_init

import akshare as ak

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

CATEGORIES = ["年报", "半年报", "一季报", "三季报", "业绩预告"]
# 注：「业绩快报」不是接口支持的 category（会 KeyError），但快报公告会在「业绩预告」类别里返回，
#     故 KEEP_KEYWORDS 仍保留「业绩快报」以收纳标题。
KEEP_KEYWORDS = ["年度报告", "半年度报告", "季度报告", "业绩预告", "业绩快报"]


def fetch_disclosures(code, start_year, end_year):
    rows = []
    for year in range(start_year, end_year + 1):
        s, e = "%d0101" % year, "%d1231" % year
        for cat in CATEGORIES:
            try:
                df = ak.stock_zh_a_disclosure_report_cninfo(
                    symbol=code, market="沪深京", category=cat,
                    start_date=s, end_date=e,
                )
            except Exception as ex:
                msg = "%s: %s" % (type(ex).__name__, ex)
                # 该年该类别无数据时接口返回空表 → akshare 内部取列报 KeyError；网络抖动为 JSONDecodeError。
                # 两者都属"无数据/瞬时失败"，静默跳过（拉完后按总条数校验完整性）。
                if "are in the [columns]" in msg or "JSONDecodeError" in msg:
                    continue
                print("  [warn] %d %s 失败: %s" % (year, cat, msg))
                continue
            if df is None or len(df) == 0 or "公告标题" not in df.columns:
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
            time.sleep(0.25)

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
    ap.add_argument("code", help="6 位 A 股代码，如 000830")
    ap.add_argument("--start", default="20090101", help="起始日 YYYYMMDD（默认 20090101）")
    ap.add_argument("--end", default="20260913", help="截止日 YYYYMMDD")
    ap.add_argument("--force", action="store_true", help="忽略缓存重新拉取")
    args = ap.parse_args()

    out = os.path.join(BASE, "data", "disclosure", "%s_disclosure.json" % args.code)
    if os.path.exists(out) and not args.force:
        print("缓存已存在：%s（--force 可强制刷新）" % out)
        return

    print("拉取 %s 定期报告披露日 / 业绩预告 ..." % args.code)
    disc = fetch_disclosures(args.code, int(args.start[:4]), int(args.end[:4]))
    print("  合计 %d 条" % len(disc))

    os.makedirs(os.path.dirname(out), exist_ok=True)
    with io.open(out, "w", encoding="utf-8") as f:
        json.dump({"code": args.code, "disclosures": disc}, f, ensure_ascii=False, indent=1)
    print("已写入 %s" % out)


if __name__ == "__main__":
    main()
