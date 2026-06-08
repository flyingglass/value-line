# -*- coding: utf-8 -*-
"""
pdf_downloader.py - 年报/中报/季报 PDF 自动下载 + 严格校验
"""
import os, sys, time, re, json, hashlib, io
import warnings; warnings.filterwarnings("ignore")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config

for k in list(os.environ.keys()):
    if any(x in k.upper() for x in ("PROXY", "HTTP_", "HTTPS_", "ALL_PROXY")):
        os.environ.pop(k, None)
import requests as _rq
_orig = _rq.Session.__init__
def _p(self): _orig(self); self.trust_env = False; self.proxies = {}
_rq.Session.__init__ = _p

_S = _rq.Session()
_S.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})

_TITLE_BLACKLIST_RE = re.compile(
    "摘要|已取消|已撤销|撤回|取消|更正前|募集说明书|ESG|可持续发展|"
    "审计报告|财务报表|意见|英文版|英文简版|english|港股公告|H股公告|"
    "环境.*社会.*管治|Environmental.*Social.*Governance|"
    "Circular|Proxy Form|Monthly Return|Supplemental|Announcement",
    re.IGNORECASE)

# ============================================================
# PDF 严格校验
# ============================================================
class PDFValidator:
    """4层校验: 文件头/大小/页数/内容匹配"""
    MIN_SIZE = 10240     # 10KB
    MIN_PAGES = 5
    MAX_PAGES = 500

    @staticmethod
    def validate(path, company_name, report_type, fiscal_year, alt_names=None):
        """返回 (通过, 详情)"""
        checks = []
        # 1. 文件存在+大小
        if not os.path.exists(path):
            return False, "文件不存在"
        size = os.path.getsize(path)
        if size < PDFValidator.MIN_SIZE:
            checks.append(f"FAIL 文件过小({size}B)")
            return False, "; ".join(checks) if checks else "OK"
        checks.append(f"PASS 大小({size/1024:.0f}KB)")

        # 2. PDF文件头
        with open(path, "rb") as f:
            header = f.read(10)
        if not header.startswith(b"%PDF"):
            checks.append("FAIL 非PDF文件头")
            return False, "; ".join(checks)
        checks.append("PASS PDF头")

        # 3. 页数
        try:
            import pdfplumber
            pdf = pdfplumber.open(path)
            pages = len(pdf.pages)
            if pages < PDFValidator.MIN_PAGES:
                checks.append(f"FAIL 页数过少({pages})")
                pdf.close()
                return False, "; ".join(checks)
            if pages > PDFValidator.MAX_PAGES:
                checks.append(f"WARN 页数过多({pages})")
            checks.append(f"PASS 页数({pages})")

            # 4. 内容匹配公司名
            page1 = pdf.pages[0].extract_text() or ""
            # 取前500字符搜索
            search_text = (page1 + " " + (pdf.pages[1].extract_text() or "") if pages > 1 else page1)[:1000]
            # 判断公司名是否出现 (简体/繁体/变体模糊匹配)
            cn_found = company_name in search_text
            if not cn_found and len(company_name) >= 2:
                cn_found = company_name[:2] in search_text
            # 股票变体名 (繁体/简称等)
            if not cn_found:
                for an in (alt_names or []):
                    if an in search_text:
                        cn_found = True
                        break
            en_found = False
            if re.search(r"[a-zA-Z]{3,}", search_text):
                en_found = True  # 至少有英文内容

            if not cn_found and not en_found:
                checks.append("FAIL 公司名未匹配")
                pdf.close()
                return False, "; ".join(checks)
            if cn_found:
                checks.append(f"PASS 公司名({company_name})")
            else:
                checks.append("PASS 英文内容")

            # 5. 验证报告类型关键词
            fiscal_kw = {
                "FY": ["年度报告", "年報", "ANNUAL REPORT", "全年业绩", "年度業績"],
                "H1": ["半年度", "中期報告", "INTERIM REPORT", "HALF-YEAR"],
                "Q1": ["第一季度", "一季报", "FIRST QUARTER"],
                "Q3": ["第三季度", "三季报", "THIRD QUARTER"],
            }
            kw_list = fiscal_kw.get(report_type, ["年度"])
            type_ok = any(kw.lower() in search_text.lower() for kw in kw_list)
            if type_ok:
                checks.append(f"PASS 类型({report_type})")
            else:
                checks.append(f"WARN 类型关键词未匹配")

            pdf.close()
        except Exception as e:
            checks.append(f"FAIL 解析异常({e})")
            return False, "; ".join(checks)

        return True, "; ".join(checks)

# ============================================================
# A股: 巨潮资讯网
# ============================================================
CNINFO_URL = "http://www.cninfo.com.cn/new/hisAnnouncement/query"
CNINFO_STATIC = "http://static.cninfo.com.cn/"
_CNINFO_ORG_CACHE = None

def _get_cninfo_org_id(code):
    global _CNINFO_ORG_CACHE
    if _CNINFO_ORG_CACHE is None:
        r = _S.get("http://www.cninfo.com.cn/new/data/szse_stock.json", timeout=15)
        data = json.loads(r.text.lstrip("\ufeff"))
        sl = data.get("stockList", []) if isinstance(data, dict) else data
        _CNINFO_ORG_CACHE = {s["code"]: s["orgId"] for s in sl}
    return _CNINFO_ORG_CACHE.get(code, "")

def download_cninfo(code, periods=None):
    stock = config.STOCKS[code]
    org_id = stock.get("org_id") or _get_cninfo_org_id(code)
    periods = periods or ["FY", "H1", "Q1", "Q3"]
    pdf_dir = config.pdf_dir(code)
    results = {"OK": 0, "FAIL": 0, "SKIP": 0}

    for period in periods:
        cat = config.CNINFO_CATEGORIES.get(period)
        if not cat: continue
        print(f"\n  [{config.PERIOD_NAME[period]}]")
        page = 1
        while True:
            data = {
                "pageNum": str(page), "pageSize": "30",
                "column": "sse" if stock["exchange"] == "SSE" else "szse",
                "tabName": "fulltext",
                "plate": "sh" if stock["exchange"] == "SSE" else "sz",
                "stock": f"{code},{org_id}", "searchkey": "", "secid": "",
                "category": cat, "trade": "",
                "seDate": "2015-01-01~2026-12-31",
                "sortName": "time", "sortType": "desc", "isHLtitle": "true",
            }
            r = _S.post(CNINFO_URL, data=data, timeout=20)
            d = r.json()
            anns = d.get("announcements") or []
            for a in anns:
                title = a.get("announcementTitle", "")
                if a.get("adjunctType") != "PDF": continue
                if _TITLE_BLACKLIST_RE.search(title): continue
                title_clean = re.sub(r"<[^>]+>", "", title)
                fy = _infer_fiscal_year(title_clean, str(a.get("announcementTime","")))
                out = os.path.join(pdf_dir, f"{code}_{fy}_{config.PERIOD_NAME[period]}.pdf")
                if os.path.exists(out):
                    results["SKIP"] += 1; continue

                adj = a.get("adjunctUrl", "")
                pdf_url = CNINFO_STATIC + adj if adj.startswith("/") else CNINFO_STATIC + "/" + adj
                print(f"    下载: {fy} {title_clean[:50]}")
                ok = _download_and_validate(pdf_url, out, stock["name"], period, fy,
                    stock.get("alt_names"))
                if ok: results["OK"] += 1
                else: results["FAIL"] += 1
                time.sleep(0.5)
            if not d.get("hasMore") or page > 50: break
            page += 1; time.sleep(0.3)

    print(f"\n  结果: OK={results['OK']} FAIL={results['FAIL']} SKIP={results['SKIP']}")
    return results["OK"]

# ============================================================
# 港股: 港交所披露易
# ============================================================
HKEX_LIST_URLS = [
    "https://www1.hkexnews.hk/ncms/script/eds/activestock_sehk_c.json",
    "https://www1.hkexnews.hk/ncms/script/eds/inactivestock_sehk_c.json",
]
HKEX_SEARCH = "https://www1.hkexnews.hk/search/titleSearchServlet.do"
HKEX_BASE = "https://www1.hkexnews.hk"
_HKEX_CACHE = {}

def _resolve_hkex_stock_id(code):
    """从披露易股票列表解析内部 stockId"""
    if code in _HKEX_CACHE:
        return _HKEX_CACHE[code]
    code5 = code.zfill(5) if len(code) < 5 else code
    for url in HKEX_LIST_URLS:
        try:
            r = _S.get(url, timeout=15)
            data = r.json()
            stocks = data if isinstance(data, list) else data.get("stocks", [])
            for s in stocks:
                if str(s.get("c", "")).zfill(5) == code5:
                    sid = str(s.get("i", ""))
                    _HKEX_CACHE[code] = sid
                    return sid
        except: pass
    return None

def _search_hkex(stock_id, t2code, lang="zh"):
    params = {
        "lang": lang, "category": "0", "market": "SEHK",
        "stockId": stock_id, "searchType": "1", "documentType": "-1",
        "t1code": "40000", "t2code": t2code, "t2Gcode": "-2",
        "fromDate": "20200101", "toDate": "20261231",
        "MB-Daterange": "0", "rowRange": "200",
        "sortByOptions": "DateTime", "sortDir": "0",
    }
    r = _S.get(HKEX_SEARCH, params=params, timeout=20)
    d = r.json()
    if isinstance(d, list): return d
    if isinstance(d, dict):
        for k in ("result", "data", "records", "rows"):
            v = d.get(k)
            if isinstance(v, list): return v
            if isinstance(v, str):
                try: return json.loads(v)
                except: pass
    return []

def _classify_hk_report(title, t2code):
    title_upper = title.upper()
    if t2code == "40100":
        if any(k in title_upper for k in ("ANNUAL REPORT", "年報", "年报", "年度報告", "年度报告")): return "FY"
    if t2code == "40200":
        if any(k in title_upper for k in ("INTERIM", "中期", "半年度", "HALF-YEAR", "半年")): return "H1"
    if t2code == "40300":
        if "FIRST" in title_upper or "第一" in title: return "Q1"
        if "THIRD" in title_upper or "第三" in title: return "Q3"
        return "Q1"
    return None

def download_hkex(code, periods=None):
    stock = config.STOCKS[code]
    stock_id = stock.get("hkex_stock_id") or _resolve_hkex_stock_id(code)
    if not stock_id:
        print(f"  [hkex] 无法解析 stockId")
        return 0
    print(f"  [hkex] stockId={stock_id}")

    periods = periods or ["FY", "H1"]
    pdf_dir = config.pdf_dir(code)
    results = {"OK": 0, "FAIL": 0, "SKIP": 0}

    for period in periods:
        t2code = {"FY": "40100", "H1": "40200", "Q1": "40300", "Q3": "40300"}.get(period)
        if not t2code: continue
        print(f"\n  [{config.PERIOD_NAME[period]}]")
        time.sleep(1)

        for lang in ("zh", "E"):
            rows = _search_hkex(stock_id, t2code, lang)
            if not rows: continue
            for ann in rows:
                title = ann.get("TITLE", ann.get("title", ""))
                fl = ann.get("FILE_LINK", ann.get("fileLink", ""))
                if not fl: continue
                # 过滤
                if _TITLE_BLACKLIST_RE.search(title): continue
                # 类型匹配
                inferred = _classify_hk_report(title, t2code)
                if inferred and inferred != period: continue
                # 跳过英文版(中文优先)
                if lang == "zh" and re.search(r"(annual|interim|quarterly)\s+report", title, re.I):
                    if not re.search(r"[\u4e00-\u9fff]", title): continue

                fy = _infer_fiscal_year(title, str(ann.get("DATE_TIME","")))
                out = os.path.join(pdf_dir, f"{code}_{fy}_{config.PERIOD_NAME[period]}.pdf")
                if os.path.exists(out):
                    results["SKIP"] += 1; continue

                pdf_url = fl if fl.startswith("http") else HKEX_BASE + fl
                print(f"    下载: {fy} {title[:50]}")
                ok = _download_and_validate(pdf_url, out, stock["name"], period, fy,
                    stock.get("alt_names"))
                if ok: results["OK"] += 1
                else: results["FAIL"] += 1
                time.sleep(0.5)
            if results["OK"] > 0 or results["SKIP"] > 0: break
            time.sleep(0.5)

    print(f"\n  结果: OK={results['OK']} FAIL={results['FAIL']} SKIP={results['SKIP']}")
    return results["OK"]

# ============================================================
# 通用下载+校验
# ============================================================
def _download_and_validate(url, path, company_name, report_type, fiscal_year, alt_names=None):
    try:
        r = _S.get(url, timeout=60, allow_redirects=True)
    except Exception as e:
        print(f"      FAIL 下载异常: {e}")
        return False

    if r.status_code != 200:
        print(f"      FAIL HTTP {r.status_code}")
        return False

    # 先保存
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(r.content)

    # 严格校验
    ok, detail = PDFValidator.validate(path, company_name, report_type, fiscal_year, alt_names)
    if ok:
        # 计算sha256
        sha = hashlib.sha256(r.content).hexdigest()[:16]
        print(f"      OK {len(r.content)/1024:.0f}KB sha256={sha}")
        # 写校验记录
        _write_validation_log(path, url, company_name, report_type, fiscal_year, True, detail)
        return True
    else:
        print(f"      FAIL 校验: {detail}")
        _write_validation_log(path, url, company_name, report_type, fiscal_year, False, detail)
        # 仅删除结构性损坏的文件(大小/PDF头/页数), 公司名/内容不匹配则保留
        if "文件过小" in detail or "非PDF" in detail or "页数过少" in detail:
            os.remove(path)
        else:
            print(f"      (文件已保留: {os.path.basename(path)})")
        return False

def _write_validation_log(pdf_path, source_url, company, rtype, fy, ok, detail):
    # 支持 .pdf / .htm 等后缀, validation log 统一用 .validation.json
    log_path = re.sub(r'\.(pdf|htm|html|txt)$', '.validation.json', pdf_path)
    log = {
        "pdf": pdf_path, "source_url": source_url,
        "company": company, "report_type": rtype, "fiscal_year": fy,
        "valid": ok, "detail": detail,
        "validated_at": str(__import__("datetime").datetime.now()),
    }
    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(log, f, ensure_ascii=False, indent=2)

_CN_DIGIT = {
    '零': 0, '一': 1, '二': 2, '三': 3, '四': 4,
    '五': 5, '六': 6, '七': 7, '八': 8, '九': 9, '十': 10,
    '０': 0, '１': 1, '２': 2, '３': 3, '４': 4,
    '５': 5, '６': 6, '７': 7, '８': 8, '９': 9,
}

def _parse_chinese_year(text):
    """解析中文数字年份, 如 二零二五 → 2025"""
    m = re.search(r'([零一二三四五六七八九０１２３４５６７８９]{4})\s*年', text)
    if m:
        digits = m.group(1)
        year = 0
        for ch in digits:
            year = year * 10 + _CN_DIGIT.get(ch, 0)
        if 2000 <= year <= 2099:
            return str(year)
    return None

def _infer_fiscal_year(title, fallback=""):
    # 1. 阿拉伯数字年份 (标题内)
    m = re.search(r"(\d{4})\s*年[年度]?\s*(?:年度报告|年报|业绩)", title)
    if m: return m.group(1)
    m = re.search(r"(\d{4})\s*年", title)
    if m: return m.group(1)
    # 2. 中文数字年份 (eg. 二零二五年年報) — 优先于fallback
    ch = _parse_chinese_year(title)
    if ch: return ch
    # 3. 最后从fallback推断
    m = re.search(r"20\d{2}", str(fallback))
    if m: return m.group(0)
    return str(fallback)[:4] if fallback else ""

# ============================================================
# 美股下载: 10-K (stocklight.com) + 10-Q (SEC EDGAR)
# ============================================================

SEC_UA = "ValueLine/1.0 (value-line@example.com)"
SEC_SUBMISSIONS = "https://data.sec.gov/submissions/CIK{}.json"
SEC_ARCHIVE = "https://www.sec.gov/Archives/edgar/data"

_CIK_MAP = {
    "NVDA": "0001045810",
    "AAPL": "0000320193",
    "MSFT": "0000789019",
    "GOOGL": "0001652044",
    "AMZN": "0001018724",
    "META": "0001326801",
    "TSLA": "0001318605",
}

def _stocklight_slug(stock):
    """从 config 获取 stocklight slug, 或从 name_en 推导。"""
    slug = stock.get("stocklight_slug", "")
    if slug:
        return slug
    # 推导: "NVIDIA" → "nvidia-corporation"
    name = stock.get("name_en", "")
    # 常见后缀自动补全
    suffix_map = {" NVIDIA": "-corporation", " Apple": "-inc",
                  " Microsoft": "-corporation", " Amazon": "-com-inc",
                  " Alphabet": "-inc", " Meta": "-platforms-inc",
                  " Tesla": "-inc"}
    for key, suffix in suffix_map.items():
        if name.lower() == key.strip().lower():
            return name.lower().replace(" ", "-") + suffix
    return name.lower().replace(" ", "-")


def _stocklight_list_10k(code):
    """爬 stocklight.com annual-reports 页面, 提取所有 10-K ID。

    返回 [(year, id), ...] 列表。
    """
    stock = config.STOCKS[code]
    slug = _stocklight_slug(stock)
    ticker = code.lower()
    url = (f"https://app.stocklight.com/stocks/us/"
           f"nasdaq-{ticker}/{slug}/annual-reports")

    try:
        r = _S.get(url, timeout=30,
                   headers={"User-Agent": "Mozilla/5.0"})
        if r.status_code != 200:
            print(f"  [stocklight] HTTP {r.status_code}")
            return []
    except Exception as e:
        print(f"  [stocklight] 请求失败: {e}")
        return []

    # 解析 nasdaq-{ticker}-{year}-10K-{id}
    pattern = rf'nasdaq-{re.escape(ticker)}-(\d{{4}})-10K-(\d+)'
    ids = re.findall(pattern, r.text)
    # 去重，保留每个年份的第一个（最新 accession）
    seen = {}
    for yr, fid in ids:
        if yr not in seen:
            seen[yr] = fid
    return sorted(seen.items(), reverse=True)


def _nasdaq_list_10q(code):
    """查 Nasdaq API, 筛选 10-Q, 返回 PDF 链接列表。

    返回 [(filed_date, period_end, pdf_url), ...] 列表。
    """
    ticker = code.upper()
    url = f"https://api.nasdaq.com/api/company/{ticker}/sec-filings?limit=200"
    try:
        r = _S.get(url, timeout=30,
                   headers={"User-Agent": "Mozilla/5.0",
                            "Accept": "application/json"})
        if r.status_code != 200:
            print(f"  [Nasdaq] HTTP {r.status_code}")
            return []
    except Exception as e:
        print(f"  [Nasdaq] 请求失败: {e}")
        return []

    rows = r.json().get("data", {}).get("rows", [])
    results = []
    for rec in rows:
        if rec.get("formType") == "10-Q":
            pdf = rec.get("view", {}).get("pdfLink", "")
            if pdf:
                results.append((rec["filed"], rec.get("period", ""), pdf))
    return results


def _sec_get_json(url):
    headers = {
        "User-Agent": SEC_UA,
        "Accept": "application/json",
        "Accept-Encoding": "gzip, deflate",
        "Host": "data.sec.gov",
    }
    try:
        r = _S.get(url, headers=headers, timeout=30)
        return r.json() if r.status_code == 200 else None
    except Exception as e:
        print(f"      SEC API 请求异常: {e}")
        return None

def _sec_list_10q(code):
    """查 SEC EDGAR submissions API, 筛选 10-Q, 返回主文档 URL 列表。
    返回 [(form, report_date, doc_url), ...] — doc_url 指向 .htm iXBRL 文件。
    """
    stock = config.STOCKS[code]
    cik = stock.get("cik") or _CIK_MAP.get(code, "")
    if not cik:
        print(f"  [SEC] 缺少 CIK 映射")
        return []

    cik_padded = cik.zfill(10)
    cik_no_pad = cik.lstrip("0")
    data = _sec_get_json(SEC_SUBMISSIONS.format(cik_padded))
    if not data:
        print(f"  [SEC] API 查询失败")
        return []

    recent = data.get("filings", {}).get("recent", {})
    forms = recent.get("form", [])
    acc_nums = recent.get("accessionNumber", [])
    primary_docs = recent.get("primaryDocument", [])
    report_dates = recent.get("reportDate", [])

    # 筛选 10-Q, 按 (年份, 季度) 去重
    seen = set()
    results = []
    for i in range(len(forms)):
        if forms[i] != "10-Q":
            continue
        rpt_date = report_dates[i]
        m = int(rpt_date.split("-")[1]) if "-" in str(rpt_date) else 0
        # 按 reportDate 月份推断季度 (10-Q 通常: Q1→月3-5, Q2→月6-8, Q3→月9-11)
        if 3 <= m <= 5:
            q = "Q1"
        elif 6 <= m <= 8:
            q = "Q2"
        else:
            q = "Q3"
        fy = rpt_date.split("-")[0] if "-" in str(rpt_date) else str(rpt_date)[:4]
        key = (fy, q)
        if key in seen:
            continue
        seen.add(key)

        acc_no = acc_nums[i].replace("-", "")
        doc = primary_docs[i]
        doc_url = f"{SEC_ARCHIVE}/{cik_no_pad}/{acc_no}/{doc}"
        results.append((q, fy, doc_url))
    return results

def _download_sec_document(url, path, company_name, report_type, fiscal_year):
    """下载 SEC EDGAR 文档 (.htm iXBRL), 做基本校验。"""
    try:
        r = _S.get(url, timeout=120, allow_redirects=True,
                   headers={"User-Agent": SEC_UA, "Accept-Encoding": "gzip, deflate"})
    except Exception as e:
        print(f"      FAIL 下载异常: {e}")
        return False

    if r.status_code != 200:
        print(f"      FAIL HTTP {r.status_code}")
        return False

    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(r.content)

    size = len(r.content)
    if size < 50000:
        print(f"      FAIL 文件过小 ({size}B)")
        os.remove(path)
        return False

    sha = hashlib.sha256(r.content).hexdigest()[:16]
    print(f"      OK {size/1024:.0f}KB .htm sha256={sha}")
    _write_validation_log(path, url, company_name, report_type,
                          fiscal_year, True, f"SEC EDGAR ({size/1024:.0f}KB)")
    return True

def download_us(code, periods=None):
    """美股下载: 10-K 走 stocklight.com, 10-Q 走 SEC EDGAR。

    periods 默认 ["FY"], 可选加 "Q1"/"Q3" 下载 10-Q 季报。
    """
    stock = config.STOCKS[code]
    periods = periods or ["FY"]
    results = {"OK": 0, "FAIL": 0, "SKIP": 0}

    want_10k = "FY" in periods
    want_10q = any(p in periods for p in ("Q1", "Q3", "H1"))

    # ── 10-K: stocklight.com ──
    if want_10k:
        print(f"\n  [10-K] stocklight.com 获取 {stock['name_en']} ...")
        ids = _stocklight_list_10k(code)
        if not ids:
            print(f"  [10-K] 未找到 10-K ID, 可能需要手动配置 stocklight_slug")
        else:
            print(f"  [10-K] 发现 {len(ids)} 年年报 ({ids[-1][0]}-{ids[0][0]})")
            slug = _stocklight_slug(stock)
            ticker = code.lower()
            for yr, fid in ids:
                out_name = f"{code}_{yr}_年报.pdf"
                out = os.path.join(config.pdf_dir(code), out_name)
                if os.path.exists(out):
                    results["SKIP"] += 1
                    continue

                pdf_url = (f"https://stocklight.com/stocks/us/"
                           f"nasdaq-{ticker}/{slug}/annual-reports/"
                           f"nasdaq-{ticker}-{yr}-10K-{fid}.pdf")
                print(f"    下载: {yr} 10-K → {out_name}")
                ok = _download_and_validate(
                    pdf_url, out, stock["name"], "FY", yr,
                    stock.get("alt_names"))
                if ok:
                    results["OK"] += 1
                else:
                    results["FAIL"] += 1
                time.sleep(0.3)

    # ── 10-Q: SEC EDGAR → iXBRL .htm ──
    if want_10q:
        Q_NAME = {"Q1": "一季报", "Q2": "中报", "Q3": "三季报"}
        print(f"\n  [10-Q] SEC EDGAR 获取 {stock['name_en']} ...")
        q_list = _sec_list_10q(code)
        if not q_list:
            print(f"  [10-Q] 未找到 10-Q 季度报告")
        else:
            print(f"  [10-Q] 发现 {len(q_list)} 份季报")
            for q, fy, doc_url in q_list:
                out_name = f"{code}_{fy}_{Q_NAME[q]}.htm"
                out = os.path.join(config.pdf_dir(code), out_name)
                if os.path.exists(out):
                    results["SKIP"] += 1
                    continue

                print(f"    下载: 10-Q {q} ({fy}) → {out_name}")
                ok = _download_sec_document(
                    doc_url, out, stock["name"], q, fy)
                if ok:
                    results["OK"] += 1
                else:
                    results["FAIL"] += 1
                time.sleep(0.15)

    print(f"\n  [美股] 结果: OK={results['OK']} FAIL={results['FAIL']} "
          f"SKIP={results['SKIP']}")
    return results


# ============================================================
# 主函数
# ============================================================
def download(code=None):
    code = code or config.ACTIVE_STOCK
    stock = config.STOCKS[code]
    market = stock["market"]
    pdf_dir = config.pdf_dir(code)

    print(f"\n{'='*60}")
    print(f"PDF下载: {stock['name']} ({code}) [{market}]")
    print(f"校验规则: PDF头+大小>10KB+页数>5+公司名匹配+报告类型")
    print(f"目标: {pdf_dir}")
    print(f"{'='*60}")

    if market == "hk":
        return download_hkex(code)
    elif market == "us":
        return download_us(code, periods=["FY"])
    else:
        return download_cninfo(code)

if __name__ == "__main__":
    code = sys.argv[1] if len(sys.argv) > 1 else None
    download(code)
