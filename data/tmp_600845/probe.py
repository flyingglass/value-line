# -*- coding: utf-8 -*-
import os, traceback
for k in list(os.environ.keys()):
    if any(x in k.upper() for x in ("PROXY","HTTP_","HTTPS_","ALL_PROXY")):
        os.environ.pop(k, None)
import requests as rq
_o = rq.Session.__init__
def _p(self): _o(self); self.trust_env=False; self.proxies={}
rq.Session.__init__=_p
import akshare as ak
C = "600845"
def t(name, fn):
    try:
        df = fn()
        print(f"[OK] {name}: shape={getattr(df,'shape',None)}")
        print("     cols:", list(df.columns)[:8])
        print(df.head(3).to_string()[:600])
    except Exception as e:
        print(f"[FAIL] {name}: {type(e).__name__} {str(e)[:90]}")
    print()
t("benefit_ths 利润表", lambda: ak.stock_financial_benefit_ths(symbol=C))
t("debt_ths 资产负债表", lambda: ak.stock_financial_debt_ths(symbol=C))
t("cash_ths 现金流", lambda: ak.stock_financial_cash_ths(symbol=C))
t("abstract_new_ths 指标", lambda: ak.stock_financial_abstract_new_ths(symbol=C, indicator="按报告期"))

print("=" * 40)
t("zh_a_daily K线", lambda: ak.stock_zh_a_daily(symbol="sh600845", adjust="qfq"))
t("dividend_cninfo 分红", lambda: ak.stock_dividend_cninfo(symbol=C))
t("zh_a_spot 现价", lambda: ak.stock_zh_a_spot().query("代码=='sh600845'"))

print("=" * 40)
t("zh_a_daily K线", lambda: ak.stock_zh_a_daily(symbol="sh600845", adjust="qfq"))
t("dividend_cninfo 分红", lambda: ak.stock_dividend_cninfo(symbol=C))
t("zh_a_spot 现价", lambda: ak.stock_zh_a_spot().query("代码=='sh600845'"))
