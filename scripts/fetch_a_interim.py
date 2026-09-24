# -*- coding: utf-8 -*-
"""fetch_a_interim.py — 批量下载 A 股「半年度报告（中报）」PDF

与 scripts/fetch_hk_interim.py 同构：平铺文件名 + 单一 _manifest.json，
**清单增量合并**（不去动已有的港股条目）。

数据源：巨潮资讯网 cninfo（本机东财不可用时的主要 A 股源）
  · topSearch/query                         代码 → orgId
  · hisAnnouncement/query  category_bndbg_szsh  半年报条目（标题 + adjunctUrl）
  · static.cninfo.com.cn/<adjunctUrl>      PDF 直链

目标清单：默认取 `scripts/out/ai_sw_filter3.csv` 中**落在三层框架内**的 A 股
（即 [[学股/AI软件/AI软件名单-按吞噬顺序筛选]] 的 41 只里的 A 股部分）。
可用 --codes 自行指定。

用法：
  .venv\\Scripts\\python scripts\\fetch_a_interim.py                # 默认清单
  .venv\\Scripts\\python scripts\\fetch_a_interim.py --codes 688111,600588
  .venv\\Scripts\\python scripts\\fetch_a_interim.py --dump 688111    # 只看条目不下载

输出：
  data/AI软件/<code>_<名称>_2026中报.pdf
  data/AI软件/_manifest.json（增量合并，A 股条目 market="a"）
"""
import argparse
import csv
import json
import os
import re
import sys
import time

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
import requests  # noqa: E402
from pdf_downloader import PDFValidator, _download_and_validate  # noqa: E402

ROOT = os.path.dirname(_HERE)
OUT_ROOT = os.path.join(ROOT, "data", "AI软件")
CSV_IN = os.path.join(_HERE, "out", "ai_sw_filter3.csv")
MANIFEST = os.path.join(OUT_ROOT, "_manifest.json")

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120 Safari/537.36",
      "Referer": "http://www.cninfo.com.cn/new/commonUrl?url=disclosure/list/notice",
      "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
      "X-Requested-With": "XMLHttpRequest"}

STATIC = "http://static.cninfo.com.cn/"

# 三层框架内的层名（与 scripts/ai_sw_rank.py 的 LAYER3 保持一致）
IN_FRAME = ("① 浅层工具（最先被吃）", "② 本体层（吃不到·赋能）", "③ 长尾 workbuddy")


def _post(url, data, timeout=25):
    return requests.post(url, data=data, headers=UA, timeout=timeout)


def org_id(code):
    """代码 → (orgId, 中文简称)"""
    try:
        r = _post("http://www.cninfo.com.cn/new/information/topSearch/query",
                  {"keyWord": code, "maxNum": 10})
        for it in (r.json() or []):
            if it.get("code") == code:
                return it.get("orgId"), it.get("zwjc")
    except Exception as e:
        print("    [warn] orgId 查询失败: %s" % type(e).__name__)
    return None, None


def search_h1(code, oid, year=2026):
    """返回 [(title, url, date)]，按披露时间倒序；已剔除「摘要」"""
    col = "sse" if code.startswith(("6", "9")) else "szse"
    payload = {"stock": "%s,%s" % (code, oid), "tabName": "fulltext",
               "pageSize": 30, "pageNum": 1, "column": col,
               "category": "category_bndbg_szsh",
               "seDate": "%d-01-01~%d-12-31" % (year, year),
               "isHLtitle": "true"}
    j = _post("http://www.cninfo.com.cn/new/hisAnnouncement/query", payload).json()
    out = []
    for a in (j.get("announcements") or []):
        title = (a.get("announcementTitle") or "").strip()
        adj = a.get("adjunctUrl") or ""
        if not adj or not title:
            continue
        if "摘要" in title or "英文" in title or "取消" in title:
            continue
        ts = a.get("announcementTime")
        if isinstance(ts, (int, float)):
            import datetime
            date = datetime.datetime.fromtimestamp(ts / 1000).strftime("%Y-%m-%d")
        else:
            date = str(ts or "")[:10]
        out.append({"title": title, "url": STATIC + adj.lstrip("/"), "date": date})
    return out


def load_targets(codes=None):
    """默认：ai_sw_filter3.csv 中落在三层内的 A 股"""
    if codes:
        want = {c.strip().zfill(6) for c in codes.split(",") if c.strip()}
        rows = []
        with open(CSV_IN, encoding="utf-8-sig") as f:
            for r in csv.DictReader(f):
                if r["code"].zfill(6) in want:
                    rows.append(r)
        return [(r["code"].zfill(6), r["name"]) for r in rows]

    rows = []
    with open(CSV_IN, encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            if r["layer3"] in IN_FRAME and r["market"] == "A":
                rows.append((r["code"].zfill(6), r["name"]))
    # 按层序排列（② → ③ → ①），便于对照页面
    order = {IN_FRAME[1]: 0, IN_FRAME[2]: 1, IN_FRAME[0]: 2}
    with open(CSV_IN, encoding="utf-8-sig") as f:
        lay = {r["code"].zfill(6): r["layer3"] for r in csv.DictReader(f)}
    rows.sort(key=lambda x: (order.get(lay.get(x[0]), 9), x[0]))
    return rows


def _absorb_validation(path):
    vj = re.sub(r"\.pdf$", ".validation.json", path)
    if not os.path.exists(vj):
        return None, None
    try:
        j = json.load(open(vj, encoding="utf-8"))
        valid, detail = j.get("valid"), j.get("detail")
    except Exception:
        valid, detail = None, None
    try:
        os.remove(vj)
    except Exception:
        pass
    return valid, detail


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--codes", help="只处理指定代码（逗号分隔）")
    ap.add_argument("--dump", help="只打印某代码的半年报条目，不下载")
    ap.add_argument("--year", default="2026")
    args = ap.parse_args()

    os.makedirs(OUT_ROOT, exist_ok=True)
    targets = load_targets(args.codes)
    if not targets:
        raise SystemExit("没有待下载标的（检查 %s 是否存在）" % CSV_IN)

    manifest = {}
    if os.path.exists(MANIFEST):
        try:
            manifest = json.load(open(MANIFEST, encoding="utf-8"))
        except Exception:
            manifest = {}

    print("待处理 %d 只（A 股半年报 %s）" % (len(targets), args.year))
    ok_n = fail_n = skip_n = 0

    for code, name in targets:
        print("\n== %s %s ==" % (code, name))
        if code in manifest and manifest[code].get("files"):
            if not args.dump:
                print("  [skip] 清单已有条目")
                skip_n += 1
                continue
        oid, zwjc = org_id(code)
        if not oid:
            print("  [fail] 未取到 orgId")
            manifest[code] = {"name": name, "market": "a", "status": "fail",
                              "files": [], "note": "未取到 orgId"}
            fail_n += 1
            continue
        time.sleep(0.3)
        try:
            cands = search_h1(code, oid, int(args.year))
        except Exception as e:
            print("  [fail] 检索失败 %s %s" % (type(e).__name__, str(e)[:60]))
            fail_n += 1
            continue
        if args.dump and args.dump != code:
            continue
        if not cands:
            print("  [miss] %s 年无半年度报告" % args.year)
            manifest[code] = {"name": name, "market": "a", "status": "miss",
                              "files": [], "note": "%s 年无半年度报告" % args.year}
            fail_n += 1
            continue
        if args.dump == code:
            for c in cands:
                print("   %s %s" % (c["date"], c["title"]))
            continue

        c = cands[0]
        out = os.path.join(OUT_ROOT, "%s_%s_%s中报.pdf" % (code, name, args.year))
        print("  [get] %s %s" % (c["date"], c["title"][:52]))
        alt = [name[:4], (zwjc or "")[:4]]
        try:
            ok = _download_and_validate(c["url"], out, name, "H1", args.year, alt)
        except Exception as e:
            print("  [fail] 下载异常 %s %s" % (type(e).__name__, str(e)[:60]))
            ok = False
        valid, detail = _absorb_validation(out)
        if ok:
            manifest[code] = {
                "name": name, "market": "a", "status": "ok",
                "files": [{"year": args.year, "file": os.path.basename(out),
                           "title": c["title"], "url": c["url"], "date": c["date"],
                           "valid": valid, "check": detail, "cached": False}]}
            ok_n += 1
        else:
            manifest[code] = {"name": name, "market": "a", "status": "fail",
                              "files": [], "note": "下载或校验失败"}
            fail_n += 1
        time.sleep(0.5)

    if args.dump:
        return

    with open(MANIFEST, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=1)
    total = sum(len(v.get("files", [])) for v in manifest.values())
    print("\n清单已写入 %s（合计 %d 份）" % (MANIFEST, total))
    print("本次：成功 %d / 跳过(已有) %d / 失败 %d" % (ok_n, skip_n, fail_n))


if __name__ == "__main__":
    main()
