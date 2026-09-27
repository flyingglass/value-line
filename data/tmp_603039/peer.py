# -*- coding: utf-8 -*-
"""临时：拉协同软件同业财务（去代理）"""
import os
for k in list(os.environ.keys()):
    if any(x in k.upper() for x in ("PROXY","HTTP_","HTTPS_","ALL_PROXY")):
        os.environ.pop(k, None)
import requests as rq
_o = rq.Session.__init__
def _p(self): _o(self); self.trust_env=False; self.proxies={}
rq.Session.__init__=_p
import akshare as ak
import pandas as pd
pd.set_option('display.width', 200)
pd.set_option('display.max_columns', 40)

for code, name in [("688369","致远互联"), ("300170","汉得信息")]:
    try:
        df = ak.stock_financial_abstract(symbol=code)
        print(f"===== {name} {code} 关键指标 =====")
        cols = [c for c in df.columns if c in ('选项','指标','20251231','20241231','20231231','20221231','20260630','20250630')]
        print(df[cols].to_string()[:3000])
    except Exception as e:
        print(name, "ERR", type(e).__name__, e)
    print()
