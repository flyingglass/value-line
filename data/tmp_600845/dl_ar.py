# -*- coding: utf-8 -*-
"""临时：批量下载宝信软件(600845) 年报 PDF（2021-2025），不改 config.py"""
import os, re
for k in list(os.environ.keys()):
    if any(x in k.upper() for x in ("PROXY", "HTTP_", "HTTPS_", "ALL_PROXY")):
        os.environ.pop(k, None)
import requests as rq
_orig = rq.Session.__init__
def _p(self): _orig(self); self.trust_env = False; self.proxies = {}
rq.Session.__init__ = _p
S = rq.Session()
S.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})

CODE = "600845"
NAME = "宝信软件"
OUT = os.path.join("data", "tmp_600845")
os.makedirs(OUT, exist_ok=True)

r = S.post("http://www.cninfo.com.cn/new/information/topSearch/query",
           data={"keyWord": NAME, "maxNum": "10"}, timeout=20)
org_id = ""
try:
    js = r.json()
    for it in (js if isinstance(js, list) else []):
        if it.get("code") == CODE:
            org_id = it.get("orgId")
except Exception as e:
    print("parse err", e)
print("orgId =", org_id)

for year in [2020, 2021]:
    data = {
        "pageNum": "1", "pageSize": "40", "column": "sse", "tabName": "fulltext",
        "plate": "sh", "stock": f"{CODE},{org_id}", "searchkey": "", "secid": "",
        "category": "category_ndbg_szsh;", "trade": "",
        "seDate": f"{year}-01-01~{year}-12-31",
        "sortName": "time", "sortType": "desc", "isHLtitle": "true",
    }
    try:
        r2 = S.post("http://www.cninfo.com.cn/new/hisAnnouncement/query", data=data, timeout=25)
        anns = (r2.json().get("announcements") or [])
    except Exception as e:
        print(year, "query err", e); continue
    target = None
    for a in anns:
        t = re.sub(r"<[^>]+>", "", a.get("announcementTitle", ""))
        if a.get("adjunctType") != "PDF":
            continue
        if re.search(rf"^{year-1}年年度报告$|^{year-1}年度报告$", t) and "摘要" not in t:
            target = a; break
    if not target:
        titles = [re.sub(r"<[^>]+>", "", a.get("announcementTitle","")) for a in anns][:8]
        print(year, "未找到年报:", titles); continue
    url = "http://static.cninfo.com.cn/" + target["adjunctUrl"].lstrip("/")
    out = os.path.join(OUT, f"{CODE}_{year-1}_年报.pdf")
    rr = S.get(url, timeout=180)
    open(out, "wb").write(rr.content)
    print(year, "saved:", out, len(rr.content) // 1024, "KB")
