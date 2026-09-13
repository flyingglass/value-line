# -*- coding: utf-8 -*-
"""fetch_disclosure_hk.py — 拉取港股标的（默认泡泡玛特 09992）业绩公告日

用途：港股复盘图的「业绩公告时点」数据底座。
      A 股走 scripts/<code>/fetch_disclosure.py（巨潮 cninfo 口径），港股走本脚本（港交所披露易口径）。

数据源：HKEXnews 官方接口（港股公告唯一权威源）
  · prefix.do           股票代码 → stockId（内部 ID）
  · titleSearchServlet  公告标题 + 公布时间（分页，rowRange = 每页条数）

输出：data/disclosure/{code}_disclosure.json
  {"code", "name", "source", "disclosures": [{date, title, category, url}]}

用法：
  .venv\\Scripts\\python scripts\\09992\\fetch_disclosure_hk.py            # 抓取并归类
  .venv\\Scripts\\python scripts\\09992\\fetch_disclosure_hk.py --dump     # 只打印原始标题（定规则用）
  .venv\\Scripts\\python scripts\\09992\\fetch_disclosure_hk.py --force    # 忽略缓存重新抓
"""
import argparse
import io
import json
import os
import sys
import time

import requests

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
UA = {
    "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"),
    "Referer": "https://www1.hkexnews.hk/search/titlesearch.xhtml?lang=zh",
}
PREFIX = "https://www1.hkexnews.hk/search/prefix.do"
SEARCH = "https://www1.hkexnews.hk/search/titleSearchServlet.do"
DOC = "https://www1.hkexnews.hk"

# 业绩类公告的标题关键词归类（繁简兼容）。顺序敏感：先匹配者胜。
# 只收「业绩公布」类事件（股价催化点）：年报 / 中期报告正文（年報、中期報告）是同一报告期的
# 二次披露、日期紧邻业绩公布日，纳入会造成同标签双线，故不归类。
RULES = [
    ("预告", ("盈利預告", "盈利预告", "盈利警告", "盈警", "正面盈利", "利潤預警")),
    ("年报", ("年度業績", "年度业绩", "全年業績", "全年业绩")),
    ("中报", ("中期業績", "中期业绩", "半年度業績", "半年度业绩")),
    ("Q1", ("第一季度", "營運數據", "营运数据", "三個月", "三个月")),
    ("Q3", ("第三季度", "九個月", "九个月")),
]
# 明显不是业绩公告的（月报表 / 翌日披露 / 股东通告等），先排除
EXCLUDE = ("月報表", "月报表", "翌日披露", "股份發行人", "股份发行人", "通函", "委任", "辭任", "辞任")

LABEL_FMT = {"年报": "%sA", "中报": "%sH1", "Q1": "%sQ1", "Q3": "%sQ3", "预告": "%s预"}


def _get(url, params, tries=3):
    last = None
    for _ in range(tries):
        try:
            r = requests.get(url, params=params, headers=UA, timeout=30)
            r.raise_for_status()
            return r
        except Exception as ex:
            last = ex
            time.sleep(1.5)
    raise last


def resolve_stock_id(code):
    """股票代码 → (stockId, name)。"""
    r = _get(PREFIX, {"callback": "cb", "lang": "ZH", "type": "A",
                      "name": code, "market": "SEHK"})
    txt = r.text.strip()
    js = json.loads(txt[txt.index("(") + 1: txt.rindex(")")])
    info = js.get("stockInfo") or []
    if not info:
        raise SystemExit("未找到港股代码 %s（prefix.do 返回空）" % code)
    return info[0]["stockId"], info[0].get("name", "")


def fetch_all(stock_id, from_date, to_date, row_range=1000):
    """一次取全。

    注：该接口的 page / pageNum 实测无效（每页都返回同一批最新记录），只能放大 rowRange 取全量。
        若标的总公告数超过 row_range 会被截断，故打印实际条数以便核对。
    """
    p = {
        "sortDir": "0", "sortByOptions": "DateTime", "category": "0",
        "market": "SEHK", "stockId": str(stock_id), "documentType": "-1",
        "fromDate": from_date, "toDate": to_date, "title": "", "searchType": "1",
        "t1code": "-2", "t2Gcode": "-2", "t2code": "-2",
        "rowRange": str(row_range), "pageNum": "1", "lang": "zh",
    }
    js = json.loads(_get(SEARCH, p).text)
    rows = json.loads(js.get("result") or "[]")
    print("  接口返回 %d 条（rowRange=%d）" % (len(rows), row_range))
    return rows


def classify(title):
    for cat, kws in RULES:
        if any(k in title for k in kws):
            return cat
    return None


def normalize(rows):
    """原始记录 → {date, title, category, url}，按时间正序、同日去重。"""
    out, seen = [], set()
    for r in rows:
        title = (r.get("TITLE") or "").strip()
        raw_dt = (r.get("DATE_TIME") or "").strip()
        if not title or not raw_dt:
            continue
        if any(k in title for k in EXCLUDE):
            continue
        cat = classify(title)
        if cat is None:
            continue
        # DATE_TIME 形如 "01/09/2026 17:32"（日/月/年）
        try:
            d, m, y = raw_dt.split(" ")[0].split("/")
            iso = "%s-%s-%s" % (y, m, d)
        except Exception:
            continue
        key = (iso, title)
        if key in seen:
            continue
        seen.add(key)
        nid = r.get("NEWS_ID", "")
        out.append({
            "date": iso, "title": title, "category": cat,
            "url": "%s/listedco/listconews/sehk/%s/%s/%s.pdf" % (
                DOC, iso[:4], iso[5:7] + iso[8:10], nid) if nid else "",
            "news_id": nid,
        })
    out.sort(key=lambda x: (x["date"], x["title"]))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--code", default="09992")
    ap.add_argument("--from", dest="frm", default="20201201")
    ap.add_argument("--to", dest="to", default="20260912")
    ap.add_argument("--dump", action="store_true", help="只打印原始标题与时间（不写文件）")
    ap.add_argument("--force", action="store_true", help="忽略缓存强制重抓")
    args = ap.parse_args()

    out_path = os.path.join(BASE, "data", "disclosure", "%s_disclosure.json" % args.code)
    if os.path.exists(out_path) and not args.force and not args.dump:
        print("缓存已存在：%s（--force 强制刷新）" % out_path)
        return

    sid, name = resolve_stock_id(args.code)
    print("股票 %s %s → stockId=%s" % (args.code, name, sid))
    print("抓取区间 %s ~ %s ..." % (args.frm, args.to))
    raw = fetch_all(sid, args.frm, args.to)
    print("  原始公告 %d 条" % len(raw))

    if args.dump:
        print("\n---- 全部标题（时间倒序） ----")
        for r in raw:
            print("%s  %s" % (r.get("DATE_TIME", ""), (r.get("TITLE") or "").strip()))
        return

    disc = normalize(raw)
    print("  业绩类公告 %d 条" % len(disc))
    for d in disc:
        print("    %s  %s  %s" % (d["date"], LABEL_FMT[d["category"]] % d["date"][2:4], d["title"]))

    with io.open(out_path, "w", encoding="utf-8") as f:
        json.dump({"code": args.code, "name": name, "source": "HKEXnews",
                   "disclosures": disc}, f, ensure_ascii=False, indent=1)
    print("已写入 %s" % out_path)


if __name__ == "__main__":
    main()
