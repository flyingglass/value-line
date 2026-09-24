# -*- coding: utf-8 -*-
"""fetch_hk_interim.py — 批量下载港股「中报」PDF 到独立目录

用途：按给定港股代码清单，从 HKEXnews 抓最新的中期報告（中报）全文 PDF，
      落到 data/pdfs/hk_ai_software/<code>/ 下，逐份校验并留 provenance 清单。

数据源：HKEXnews（港交所披露易，与 scripts/pdf_downloader.py 同源）
  · activestock_sehk_c.json / inactivestock_sehk_c.json   代码 → stockId
  · titleSearchServlet.do   t2code=40200（中期報告/業績） 抓标题 + FILE_LINK

用法：
  .venv\\Scripts\\python scripts\\fetch_hk_interim.py              # 默认清单，抓最新一期
  .venv\\Scripts\\python scripts\\fetch_hk_interim.py --all-periods # 抓全部历史中报
  .venv\\Scripts\\python scripts\\fetch_hk_interim.py --dump 03317  # 只看某代码的中报条目标题

输出：
  data/pdfs/hk_ai_software/<code>/<code>_<年>_中报.pdf
  data/pdfs/hk_ai_software/<code>/<code>_<年>_中报.validation.json （沿用 pdf_downloader 校验）
  data/pdfs/hk_ai_software/_manifest.json                  全部下载清单（标题/日期/URL）
"""
import argparse
import json
import os
import re
import sys
import time

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
from pdf_downloader import PDFValidator, _download_and_validate  # noqa: E402

ROOT = os.path.dirname(_HERE)
OUT_ROOT = os.path.join(ROOT, "data", "pdfs", "hk_ai_software")

HKEX_LIST_URLS = [
    "https://www1.hkexnews.hk/ncms/script/eds/activestock_sehk_c.json",
    "https://www1.hkexnews.hk/ncms/script/eds/inactivestock_sehk_c.json",
]
HKEX_SEARCH = "https://www1.hkexnews.hk/search/titleSearchServlet.do"
HKEX_BASE = "https://www1.hkexnews.hk"
UA = {
    "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"),
    "Referer": "https://www1.hkexnews.hk/search/titlesearch.xhtml?lang=zh",
}

# 六类初筛清单（2026-09-24 港股通·软件服务板块）
TARGETS = [
    # 1 开发端·AI Coding 降本
    ("00354", "中国软件国际", ["中软国际"]),
    ("01675", "亚信科技", ["亚信"]),
    # 2 需求端·TAM 扩大
    ("00268", "金蝶国际", ["金蝶"]),
    ("02556", "迈富时", []),
    ("06687", "聚水潭", []),
    ("02013", "微盟集团", ["微盟"]),
    ("02586", "多点数智", ["多点"]),
    # 3 产品端·工具→同事
    ("03888", "金山软件", ["金山软件"]),
    ("01357", "美图公司", ["美图"]),
    ("06682", "范式智能", ["第四范式", "范式"]),
    ("03317", "迅策", []),
    ("02706", "海致科技集团", ["海致"]),
    ("00696", "中国民航信息网络", ["中航信", "民航信息网络"]),
    # 5 商业模式·订阅转 token
    ("01384", "滴普科技", ["滴普"]),
    ("09678", "云知声", []),
    ("03896", "金山云", []),
    # 6 新品类·AI 原生软件
    ("06651", "五一视界", ["51WORLD"]),
    ("06636", "极视角", []),
    ("01956", "中科闻歌", ["闻歌"]),
    ("01392", "海清智元", []),
    ("06727", "星环科技", ["星环"]),
    ("00068", "群核科技", ["酷家乐", "群核"]),
    # 边界标的（模型/智能供给，是否算软件存疑）
    ("02513", "智谱", ["智谱AI"]),
    ("00100", "MINIMAX-W", ["MiniMax", "MINIMAX"]),
]

_INTERIM_OK = re.compile(r"中期報|中报|中期報|中期報告|中期报告|半年度|INTERIM", re.I)
# 排除：摘要/更正/英文以外的噪音
_INTERIM_BAD = re.compile(r"摘要|已取消|撤销|撤回|更正|補充|补充|通告|月報|月报", re.I)
CJK = re.compile(r"[\u4e00-\u9fff]")

_HKEX_CACHE = {}


def _sess():
    import requests
    s = requests.Session()
    s.trust_env = False
    s.proxies = {}
    s.headers.update(UA)
    return s


def resolve_stock_id(s, code):
    if code in _HKEX_CACHE:
        return _HKEX_CACHE[code]
    code5 = code.zfill(5)
    for url in HKEX_LIST_URLS:
        try:
            r = s.get(url, timeout=20)
            data = r.json()
            stocks = data if isinstance(data, list) else data.get("stocks", [])
            for it in stocks:
                if str(it.get("c", "")).zfill(5) == code5:
                    sid = str(it.get("i", ""))
                    _HKEX_CACHE[code] = sid
                    return sid
        except Exception:
            continue
    _HKEX_CACHE[code] = None
    return None


def search_interim(s, stock_id, lang="zh"):
    """t2code=40200 → 中期報告/中期業績"""
    p = {
        "lang": lang, "category": "0", "market": "SEHK",
        "stockId": str(stock_id), "searchType": "1", "documentType": "-1",
        "t1code": "40000", "t2code": "40200", "t2Gcode": "-2",
        "fromDate": "20240101", "toDate": "20260924",
        "MB-Daterange": "0", "rowRange": "100",
        "sortByOptions": "DateTime", "sortDir": "0",
    }
    r = s.get(HKEX_SEARCH, params=p, timeout=25)
    d = r.json()
    if isinstance(d, list):
        return d
    if isinstance(d, dict):
        v = d.get("result")
        if isinstance(v, str):
            try:
                return json.loads(v)
            except Exception:
                return []
        if isinstance(v, list):
            return v
    return []


def parse_date(raw):
    """DATE_TIME 'DD/MM/YYYY HH:MM' → ('YYYY-MM-DD', year)"""
    try:
        d, m, y = raw.split(" ")[0].split("/")
        return "%s-%s-%s" % (y, m, d), y
    except Exception:
        return "", ""


def infer_year(title, raw_date):
    m = re.search(r"(20\d{2})\s*年", title)
    if m:
        return m.group(1)
    m = re.search(r"(20\d{2})[-\s]?(?:INTERIM|中期)", title, re.I)
    if m:
        return m.group(1)
    _, y = parse_date(raw_date)
    return y


def pick(s, stock_id):
    """返回去重后的候选列表 [{date, year, title, url, lang}]，按日期倒序"""
    rows = []
    for lang in ("zh", "E"):
        try:
            raw = search_interim(s, stock_id, lang)
        except Exception as e:
            print("    [warn] 检索失败 lang=%s: %s" % (lang, e))
            continue
        for it in raw:
            title = (it.get("TITLE") or "").strip()
            link = it.get("FILE_LINK") or ""
            if not title or not link:
                continue
            if not _INTERIM_OK.search(title):
                continue
            if _INTERIM_BAD.search(title):
                continue
            iso, _ = parse_date(it.get("DATE_TIME", ""))
            rows.append({
                "date": iso,
                "year": infer_year(title, it.get("DATE_TIME", "")),
                "title": title,
                "url": link if link.startswith("http") else HKEX_BASE + link,
                "lang": lang,
            })
        time.sleep(0.4)
    # 去重：同一 (year, lang) 只留最新；再按 (year) 优先中文
    rows.sort(key=lambda x: (x["date"], x["lang"] != "zh"), reverse=True)
    out, seen = [], set()
    for r in rows:
        key = (r["year"], r["lang"])
        if key in seen:
            continue
        seen.add(key)
        out.append(r)
    out.sort(key=lambda x: (x["year"], x["lang"] != "zh"), reverse=True)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--all-periods", action="store_true", help="下载全部历史中报（默认只取最新一期）")
    ap.add_argument("--dump", metavar="CODE", help="只打印某代码的中报条目标题")
    args = ap.parse_args()

    s = _sess()
    os.makedirs(OUT_ROOT, exist_ok=True)
    manifest = {}

    for code, name, alt in TARGETS:
        print("\n== %s %s ==" % (code, name))
        sid = resolve_stock_id(s, code)
        if not sid:
            print("  [skip] HKEXnews 未找到 stockId（可能已更名/退市）")
            manifest[code] = {"name": name, "error": "stockId 未解析", "files": []}
            continue
        cands = pick(s, sid)
        if args.dump == code or not cands:
            for c in cands:
                print("   %s [%s] %s" % (c["date"], c["lang"], c["title"][:70]))
        if not cands:
            print("  [miss] 2024 年以来无中报条目")
            manifest[code] = {"name": name, "stock_id": sid, "files": [],
                              "note": "无中报条目"}
            continue
        if args.dump == code:
            continue

        todo = cands if args.all_periods else [cands[0]]
        # 同一年份只取一次（中文优先）
        done_year, files = set(), []
        for c in todo:
            if c["year"] in done_year:
                continue
            done_year.add(c["year"])
            d = os.path.join(OUT_ROOT, code)
            os.makedirs(d, exist_ok=True)
            out = os.path.join(d, "%s_%s_中报.pdf" % (code, c["year"]))
            if os.path.exists(out):
                print("  [skip] 已存在 %s_%s_中报.pdf" % (code, c["year"]))
                files.append({"year": c["year"], "pdf": out, "title": c["title"],
                              "url": c["url"], "date": c["date"], "cached": True})
                continue
            print("  [get] %s %s" % (c["date"], c["title"][:60]))
            ok = _download_and_validate(c["url"], out, name, "H1", c["year"], alt)
            if ok:
                files.append({"year": c["year"], "pdf": out, "title": c["title"],
                              "url": c["url"], "date": c["date"], "cached": False})
            time.sleep(0.5)
        manifest[code] = {"name": name, "stock_id": sid, "files": files}

    mf = os.path.join(OUT_ROOT, "_manifest.json")
    with open(mf, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=1)
    print("\n清单已写入 %s" % mf)
    ok = sum(1 for v in manifest.values() for x in v.get("files", []))
    miss = [k for k, v in manifest.items() if not v.get("files")]
    print("下载/命中 %d 份；无中报的代码：%s" % (ok, ",".join(miss) or "无"))


if __name__ == "__main__":
    main()
