# -*- coding: utf-8 -*-
"""fetch_gz_h1_2026.py — 批量拉取《广州上市公司名单》标的的 2026 年中报 PDF

背景：名单 md 里 169 家（A股 154 + 港股 15）大多不在 config.STOCKS 里，
      pdf_downloader.py 依赖 config.STOCKS 无法直接复用，故单列本脚本。

数据源：
  A股  → 巨潮资讯网 hisAnnouncement/query（category_bndbg_szsh; 半年度报告）
         必须带 orgId：取自 cninfo szse_stock.json。该 json 虽名 szse，
         实为全市场约 6252 条：深市 gssz000429、沪市 gssh0600004。
 港股  → 港交所披露易 titleSearchServlet（t2code=40200 中期报告）

输出：
  data/广州/<code>_<名称>_2026中报.pdf
  data/广州/_manifest.json   逐条记录 ok/fail/skip 与来源 URL

用法：
  .venv\\Scripts\\python scripts\\tools\\fetch_gz_h1_2026.py --only 000429
  .venv\\Scripts\\python scripts\\tools\\fetch_gz_h1_2026.py --limit 5
  .venv\\Scripts\\python scripts\\tools\\fetch_gz_h1_2026.py              # 全量
  .venv\\Scripts\\python scripts\\tools\\fetch_gz_h1_2026.py --dry-run    # 只解析不下载
"""
import argparse
import json
import os
import re
import sys
import time

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# 本机系统代理会导致巨潮/披露易 RemoteDisconnected，与 pdf_downloader.py 同法禁用
for _k in list(os.environ.keys()):
    if any(x in _k.upper() for x in ("PROXY", "HTTP_", "HTTPS_", "ALL_PROXY")):
        os.environ.pop(_k, None)

import requests  # noqa: E402

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MD = os.path.join(BASE, "research-wiki", "research", "articles", "synthesis",
                  "广州上市公司名单-A股与港股.md")
OUT_DIR = os.path.join(BASE, "data", "广州")
MANIFEST = os.path.join(OUT_DIR, "_manifest.json")

_YEAR = "2026"
_PERIOD = "中报"

_S = requests.Session()
_S.trust_env = False
_S.proxies = {}
_S.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})

# 标题黑名单：摘要/英文版/更正/取消/问询函/财报附注等
_TITLE_BLACKLIST_RE = re.compile(
    "摘要|已取消|已撤销|撤回|取消|更正|补充|修订|英文|english|"
    "ESG|可持续发展|环境.*社会.*管治|审计报告|财务报表|问询|"
    "Circular|Proxy|Monthly Return", re.IGNORECASE)


# ============================================================
# 1. 解析名单 md
# ============================================================
def parse_md(path):
    """返回 [(code, name, market, extra), ...]；market ∈ {cn, hk}"""
    out = []
    section = None  # 'cn' | 'hk'
    with open(path, encoding="utf-8") as f:
        for line in f:
            s = line.strip()
            if s.startswith("## "):
                if s.startswith("## 二、"):
                    section = "cn"
                elif s.startswith("## 三、"):
                    section = "hk"
                elif s.startswith("## 四、"):
                    section = None  # 剔除清单，不下载
                else:
                    section = None
                continue
            if not section or not s.startswith("|"):
                continue
            cells = [c.strip() for c in s.strip("|").split("|")]
            if len(cells) < 2:
                continue
            code = cells[0]
            if not re.fullmatch(r"\d{6}", code):
                continue  # 表头 / 分隔行 / 非代码行
            name = cells[1]
            if name in ("名称", "代码"):
                continue
            out.append((code, name, section, cells[2] if len(cells) > 2 else ""))
    return out


def safe_name(name):
    return re.sub(r'[\\/:*?"<>|]', "", name).strip()


# ============================================================
# 2. A股：巨潮
# ============================================================
CNINFO_URL = "http://www.cninfo.com.cn/new/hisAnnouncement/query"
CNINFO_STATIC = "http://static.cninfo.com.cn/"
_ORG_CACHE = None


def _org_map():
    """code → orgId。szse_stock.json 为全市场约 6252 条（深 gssz / 沪 gssh）"""
    global _ORG_CACHE
    if _ORG_CACHE is None:
        _ORG_CACHE = {}
        try:
            r = _S.get("http://www.cninfo.com.cn/new/data/szse_stock.json", timeout=20)
            data = json.loads(r.text.lstrip("\ufeff"))
            sl = data.get("stockList", []) if isinstance(data, dict) else data
            for s in sl:
                _ORG_CACHE[s["code"]] = s["orgId"]
        except Exception as e:
            print("  [warn] orgId 列表拉取失败: %s %s" % (type(e).__name__, e))
    return _ORG_CACHE


def cninfo_find(code):
    """返回 (pdf_url, title) 或 (None, reason)"""
    org = _org_map().get(code, "")
    if not org:
        return None, "cninfo orgId 列表中无此代码（可能为已退市/非大盘代码）"
    plate = "sh" if code.startswith("6") else "sz"
    column = "sse" if code.startswith("6") else "szse"
    data = {
        "pageNum": "1", "pageSize": "30", "column": column,
        "tabName": "fulltext", "plate": plate,
        "stock": "%s,%s" % (code, org), "searchkey": "", "secid": "",
        "category": "category_bndbg_szsh;", "trade": "",
        "seDate": "%s-01-01~%s-12-31" % (_YEAR, _YEAR),
        "sortName": "time", "sortType": "desc", "isHLtitle": "true",
    }
    try:
        r = _S.post(CNINFO_URL, data=data, timeout=25)
        d = r.json()
    except Exception as e:
        return None, "查询失败 %s %s" % (type(e).__name__, e)

    picks = []
    for a in (d.get("announcements") or []):
        if a.get("adjunctType") != "PDF":
            continue
        title = re.sub(r"<[^>]+>", "", a.get("announcementTitle", ""))
        if _TITLE_BLACKLIST_RE.search(title):
            continue
        if _YEAR not in title:
            continue
        if "半年" not in title and "中期" not in title and "半年度" not in title:
            continue
        adj = a.get("adjunctUrl", "")
        url = CNINFO_STATIC + adj if adj.startswith("/") else CNINFO_STATIC + "/" + adj
        picks.append((url, title, str(a.get("announcementTime", ""))))

    if not picks:
        return None, "未找到 %s 年半年度报告" % _YEAR
    # 摘要已被黑名单排除；若仍有多份（正文/正文(更新)），取最新
    picks.sort(key=lambda x: x[2], reverse=True)
    return (picks[0][0], picks[0][1]), None


# ============================================================
# 3. 港股：披露易
# ============================================================
HKEX_LIST = ["https://www1.hkexnews.hk/ncms/script/eds/activestock_sehk_c.json",
             "https://www1.hkexnews.hk/ncms/script/eds/inactivestock_sehk_c.json"]
HKEX_SEARCH = "https://www1.hkexnews.hk/search/titleSearchServlet.do"
HKEX_BASE = "https://www1.hkexnews.hk"
_HK_CACHE = {}


def _hkex_stock_id(code):
    if code in _HK_CACHE:
        return _HK_CACHE[code]
    code5 = code.zfill(5)
    for url in HKEX_LIST:
        try:
            r = _S.get(url, timeout=20)
            data = r.json()
            stocks = data if isinstance(data, list) else data.get("stocks", [])
            for s in stocks:
                if str(s.get("c", "")).zfill(5) == code5:
                    _HK_CACHE[code] = str(s.get("i", ""))
                    return _HK_CACHE[code]
        except Exception:
            pass
    _HK_CACHE[code] = None
    return None


def hkex_find(code):
    sid = _hkex_stock_id(code)
    if not sid:
        return None, "无法解析披露易 stockId"
    params = {
        "lang": "zh", "category": "0", "market": "SEHK", "stockId": sid,
        "searchType": "1", "documentType": "-1", "t1code": "40000",
        "t2code": "40200", "t2Gcode": "-2",
        "fromDate": "%s0101" % _YEAR, "toDate": "%s1231" % _YEAR,
        "MB-Daterange": "0", "rowRange": "200",
        "sortByOptions": "DateTime", "sortDir": "0",
    }
    try:
        r = _S.get(HKEX_SEARCH, params=params, timeout=25)
        d = r.json()
    except Exception as e:
        return None, "查询失败 %s %s" % (type(e).__name__, e)

    rows = d if isinstance(d, list) else []
    if isinstance(d, dict):
        for k in ("result", "data", "records", "rows"):
            if isinstance(d.get(k), list):
                rows = d[k]
                break

    picks = []
    for ann in rows:
        title = ann.get("TITLE", ann.get("title", ""))
        fl = ann.get("FILE_LINK", ann.get("fileLink", ""))
        if not fl:
            continue
        if _TITLE_BLACKLIST_RE.search(title):
            continue
        up = title.upper()
        if not any(k in up for k in ("INTERIM", "中期", "半年度", "HALF-YEAR")):
            continue
        if not re.search(r"[\u4e00-\u9fff]", title) and re.search(r"interim\s+report", up):
            continue  # 纯英文版，跳过（中文优先）
        url = fl if fl.startswith("http") else HKEX_BASE + fl
        picks.append((url, title, str(ann.get("DATE_TIME", ""))))

    if not picks:
        return None, "未找到 %s 年中期报告" % _YEAR
    picks.sort(key=lambda x: x[2], reverse=True)
    return (picks[0][0], picks[0][1]), None


# ============================================================
# 4. 下载 + 校验
# ============================================================
def validate_pdf(path):
    if not os.path.exists(path):
        return False, "文件不存在"
    size = os.path.getsize(path)
    if size < 10240:
        return False, "文件过小(%dB)" % size
    with open(path, "rb") as f:
        if not f.read(5).startswith(b"%PDF"):
            return False, "非 PDF 文件头"
    return True, "大小 %.0fKB" % (size / 1024.0)


def download(url, path):
    try:
        r = _S.get(url, timeout=90, allow_redirects=True)
    except Exception as e:
        return False, "下载异常 %s %s" % (type(e).__name__, e)
    if r.status_code != 200:
        return False, "HTTP %s" % r.status_code
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(r.content)
    ok, detail = validate_pdf(path)
    if not ok:
        if os.path.exists(path):
            os.remove(path)
    return ok, detail


# ============================================================
# 5. 主流程
# ============================================================
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", help="只处理指定代码，如 000429")
    ap.add_argument("--limit", type=int, default=0, help="只处理前 N 个（调试用）")
    ap.add_argument("--market", choices=["cn", "hk"], help="只处理某市场")
    ap.add_argument("--dry-run", action="store_true", help="只解析名单，不下载")
    ap.add_argument("--force", action="store_true", help="已存在也重新下载")
    args = ap.parse_args()

    entries = parse_md(MD)
    if args.only:
        entries = [e for e in entries if e[0] == args.only]
    if args.market:
        entries = [e for e in entries if e[2] == args.market]
    if args.limit:
        entries = entries[:args.limit]

    n_cn = sum(1 for e in entries if e[2] == "cn")
    n_hk = sum(1 for e in entries if e[2] == "hk")
    print("名单解析：A股 %d 家 + 港股 %d 家 = %d" % (n_cn, n_hk, len(entries)))
    if args.dry_run:
        for code, name, market, extra in entries:
            print("  %s  %-12s %s  %s" % (code, name, market, extra))
        return

    os.makedirs(OUT_DIR, exist_ok=True)
    manifest = {}
    if os.path.exists(MANIFEST):
        try:
            with open(MANIFEST, encoding="utf-8") as f:
                manifest = json.load(f)
        except Exception:
            manifest = {}

    stat = {"ok": 0, "skip": 0, "fail": 0}
    for i, (code, name, market, extra) in enumerate(entries, 1):
        fname = "%s_%s_%s%s.pdf" % (code, safe_name(name), _YEAR, _PERIOD)
        path = os.path.join(OUT_DIR, fname)
        print("\n[%d/%d] %s %s (%s)" % (i, len(entries), code, name, market))

        if os.path.exists(path) and not args.force:
            print("  SKIP 已存在")
            stat["skip"] += 1
            manifest[code] = {"name": name, "market": market, "status": "skip",
                              "file": fname}
            continue

        if market == "cn":
            found, err = cninfo_find(code)
        else:
            found, err = hkex_find(code)

        if not found:
            print("  FAIL %s" % err)
            stat["fail"] += 1
            manifest[code] = {"name": name, "market": market, "status": "fail",
                              "reason": err}
            continue

        url, title = found
        print("  命中：%s" % title[:60])
        ok, detail = download(url, path)
        if ok:
            print("  OK %s → %s" % (detail, fname))
            stat["ok"] += 1
            manifest[code] = {"name": name, "market": market, "status": "ok",
                              "file": fname, "title": title, "url": url}
        else:
            print("  FAIL %s" % detail)
            stat["fail"] += 1
            manifest[code] = {"name": name, "market": market, "status": "fail",
                              "reason": detail, "url": url}
        time.sleep(0.4)

    with open(MANIFEST, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=1)

    print("\n" + "=" * 50)
    print("结果：OK=%d SKIP=%d FAIL=%d  → %s" % (
        stat["ok"], stat["skip"], stat["fail"], OUT_DIR))
    print("=" * 50)


if __name__ == "__main__":
    main()
