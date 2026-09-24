# -*- coding: utf-8 -*-
"""fetch_hk_interim.py — 批量下载港股「中报」PDF 到独立目录

用途：按给定港股代码清单，从 HKEXnews 抓最新的中期報告（中报）全文 PDF，
      落到 data/AI软件/<code>/ 下，逐份校验并留 provenance 清单。

注：不放 data/pdfs/ —— 该目录是 VL 流水线的年报/中报仓库（按 <code>/ 存），
    本脚本产出属于「投研候选池的原始资料」，与 data/广州/ 同类，单独建目录。

数据源：HKEXnews（港交所披露易，与 scripts/pdf_downloader.py 同源）
  · activestock_sehk_c.json / inactivestock_sehk_c.json   代码 → stockId
  · titleSearchServlet.do   t2code=40200（中期報告/業績） 抓标题 + FILE_LINK

用法：
  .venv\\Scripts\\python scripts\\fetch_hk_interim.py              # 默认清单，抓最新一期
  .venv\\Scripts\\python scripts\\fetch_hk_interim.py --all-periods # 抓全部历史中报
  .venv\\Scripts\\python scripts\\fetch_hk_interim.py --dump 03317  # 只看某代码的中报条目标题

输出（与 data/广州/ 同构：平铺 + 单一清单，不建代码子目录）：
  data/AI软件/<code>_<名称>_<年>中报.pdf
  data/AI软件/_manifest.json   每份记录 file/year/title/url/date + valid/check
                              （沿用 pdf_downloader 校验，校验结果并入清单后删除
                                .validation.json，保持目录只有 pdf + 清单）
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
OUT_ROOT = os.path.join(ROOT, "data", "AI软件")

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
    # ── 原文点名补充（2026-09-24）：庶人哑士《大模型吞噬软件》点名的港股 7 家里，
    #    这 3 家不在港股通成分，上一版未纳入；本次按用户要求补齐其中报。
    ("09669", "北森控股", ["北森"]),
    ("06608", "百融云创", ["百融"]),
    ("02718", "明略科技", ["明略"]),
]

_INTERIM_OK = re.compile(r"中期報告|中期报告|中期業績|中期业绩|半年度|INTERIM\s+REPORT|INTERIM\s+RESULTS", re.I)
# 排除：摘要/更正/纯程序性文件/含「中期」二字但非报告（股息、暂停过户、代表委任）
# 注：只作用于标题首行（港股标题常把「業績公告 + 股息 + 暫停過戶」并成一条）
_INTERIM_BAD = re.compile(
    r"摘要|已取消|撤销|撤回|更正|補充|补充|通告|月報|月报|翌日披露|Proxy|Circular", re.I)
# 优先级：正式中期報告 > 中期業績公告
_INTERIM_GRADE = [
    (re.compile(r"中期報告|中期报告|INTERIM\s+REPORT", re.I), 0),
    (re.compile(r"中期業績|中期业绩|INTERIM", re.I), 1),
]
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


def grade(title):
    for rx, g in _INTERIM_GRADE:
        if rx.search(title):
            return g
    return 9


def search_interim(s, stock_id, lang="zh"):
    """不限 t2code 全量检索后本地过滤（中期報告/中期業績公告散布在不同 t2code）"""
    p = {
        "lang": lang, "category": "0", "market": "SEHK",
        "stockId": str(stock_id), "searchType": "1", "documentType": "-1",
        "t1code": "-2", "t2code": "-2", "t2Gcode": "-2",
        "fromDate": "20250101", "toDate": "20260924",
        "MB-Daterange": "0", "rowRange": "200",
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
            if _INTERIM_BAD.search(title.split("\n")[0]):
                continue
            iso, _ = parse_date(it.get("DATE_TIME", ""))
            rows.append({
                "date": iso,
                "year": infer_year(title, it.get("DATE_TIME", "")),
                "title": title,
                "url": link if link.startswith("http") else HKEX_BASE + link,
                # API 不按 lang 过滤，同一请求会中英混排 → 按标题本身判语言
                "lang": "zh" if CJK.search(title) else "en",
                "grade": grade(title),
            })
        time.sleep(0.4)
    # 去重：同一 (year, lang) 只留最优等级/最新日期
    rows.sort(key=lambda x: (x["grade"], x["date"]))
    out, seen = [], set()
    for r in rows:
        key = (r["year"], r["lang"])
        if key in seen:
            continue
        seen.add(key)
        out.append(r)
    # 年份倒序 → 等级正序（正式報告優於業績公告）→ 中文優先
    out.sort(key=lambda x: (-int(x["year"] or 0), x["grade"], 0 if x["lang"] == "zh" else 1))
    return out


def _prev_source_url(path):
    """已存在文件的真实来源 URL（.validation.json 已被并入清单，退化为从清单查）"""
    try:
        mf = json.load(open(os.path.join(OUT_ROOT, "_manifest.json"), encoding="utf-8"))
    except Exception:
        return ""
    bn = os.path.basename(path)
    for v in mf.values():
        for f in v.get("files", []):
            if f.get("file") == bn:
                return f.get("url", "")
    return ""


def _absorb_validation(path):
    """读 pdf_downloader 写的 .validation.json → 返回 (valid, detail) 后删除该文件"""
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
    ap.add_argument("--all-periods", action="store_true", help="下载全部历史中报（默认只取最新一期）")
    ap.add_argument("--dump", metavar="CODE", help="只打印某代码的中报条目标题")
    ap.add_argument("--upgrade-zh", action="store_true",
                    help="已下载的是英文版且存在中文版时，删旧重下")
    ap.add_argument("--codes", metavar="C1,C2",
                    help="只处理指定代码（逗号分隔），其余不动；清单增量合并")
    ap.add_argument("--rebuild", action="store_true",
                    help="重建清单（默认在既有 _manifest.json 上增量合并）")
    args = ap.parse_args()

    targets = TARGETS
    if args.codes:
        want = {c.strip().zfill(5) for c in args.codes.split(",") if c.strip()}
        targets = [t for t in TARGETS if t[0] in want]
        if not targets:
            raise SystemExit("--codes 未匹配任何已知代码：%s" % args.codes)

    s = _sess()
    os.makedirs(OUT_ROOT, exist_ok=True)
    manifest_path = os.path.join(OUT_ROOT, "_manifest.json")
    # 增量：以既有清单为基础，只覆盖本次处理到的代码
    manifest = {}
    if not args.rebuild and os.path.exists(manifest_path):
        try:
            manifest = json.load(open(manifest_path, encoding="utf-8"))
        except Exception:
            manifest = {}

    for code, name, alt in targets:
        print("\n== %s %s ==" % (code, name))
        sid = resolve_stock_id(s, code)
        if not sid:
            print("  [skip] HKEXnews 未找到 stockId（可能已更名/退市）")
            manifest[code] = {"name": name, "market": "hk", "status": "fail", "files": [],
                              "note": "HKEXnews 未找到 stockId（可能已更名/退市）"}
            continue
        cands = pick(s, sid)
        if args.dump == code or not cands:
            for c in cands:
                print("   %s [%s] %s" % (c["date"], c["lang"], c["title"][:70]))
        if not cands:
            print("  [miss] 2024 年以来无中报条目")
            manifest[code] = {"name": name, "market": "hk", "status": "miss", "files": [],
                              "note": "2024 年以来无中报条目"}
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
            out = os.path.join(OUT_ROOT, "%s_%s_%s中报.pdf" % (code, name, c["year"]))
            if os.path.exists(out):
                old = _prev_source_url(out)
                if args.upgrade_zh and old and old != c["url"] and c["lang"] == "zh":
                    print("  [upgrade] 现文件非首选语种/版本，重下：%s %s" % (code, c["year"]))
                    try:
                        os.remove(out)
                    except Exception:
                        pass
                else:
                    print("  [skip] 已存在 %s_%s_%s中报.pdf" % (code, name, c["year"]))
                    files.append({"year": c["year"], "file": os.path.basename(out),
                                  "title": c["title"], "url": c["url"],
                                  "date": c["date"], "cached": True})
                    continue
            print("  [get] %s %s" % (c["date"], c["title"][:60]))
            ok = _download_and_validate(c["url"], out, name, "H1", c["year"], alt)
            valid, detail = _absorb_validation(out)
            if ok:
                files.append({"year": c["year"], "file": os.path.basename(out),
                              "title": c["title"], "url": c["url"], "date": c["date"],
                              "valid": valid, "check": detail, "cached": False})
            time.sleep(0.5)
        files.sort(key=lambda x: x["year"], reverse=True)
        manifest[code] = {"name": name, "market": "hk",
                          "status": "ok" if files else "fail", "files": files}

    if args.dump:  # 只查看条目，不改写清单
        return

    mf = os.path.join(OUT_ROOT, "_manifest.json")
    with open(mf, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=1)
    print("\n清单已写入 %s" % mf)
    ok = sum(1 for v in manifest.values() for x in v.get("files", []))
    miss = [k for k, v in manifest.items() if not v.get("files")]
    print("下载/命中 %d 份；无中报的代码：%s" % (ok, ",".join(miss) or "无"))


if __name__ == "__main__":
    main()
