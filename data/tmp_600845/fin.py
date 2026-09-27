# -*- coding: utf-8 -*-
import os
for k in list(os.environ.keys()):
    if any(x in k.upper() for x in ("PROXY","HTTP_","HTTPS_","ALL_PROXY")):
        os.environ.pop(k, None)
import requests as rq
_o = rq.Session.__init__
def _p(self): _o(self); self.trust_env=False; self.proxies={}
rq.Session.__init__=_p
import akshare as ak, pandas as pd
pd.set_option('display.width', 250); pd.set_option('display.max_columns', 60)
try:
    df = ak.stock_financial_abstract(symbol="600845")
    keys = ['营业总收入','营业收入','归母净利润','净利润','销售毛利率','销售净利率','净资产收益率']
    sub = df[df['指标'].astype(str).str.contains('|'.join(keys), regex=True)]
    cols = ['选项','指标'] + [c for c in df.columns if c not in ('选项','指标')]
    print(sub[cols].to_string()[:4000])
except Exception as e:
    print("ERR", type(e).__name__, e)
