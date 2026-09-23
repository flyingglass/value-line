import os
for k in ['http_proxy','https_proxy','HTTP_PROXY','HTTPS_PROXY','all_proxy','ALL_PROXY']:
    os.environ.pop(k, None)
os.environ['no_proxy'] = '*'
import akshare as ak
for sym, name in [('000905','中证500'), ('932000','中证2000'), ('399303','国证2000')]:
    try:
        df = ak.index_zh_a_hist(symbol=sym, period='daily', start_date='20260401', end_date='20260922')
        s = df[['日期','收盘']].copy()
        s['日期'] = s['日期'].astype(str)
        pts = {'2026-04-22':None,'2026-07-21':None,'2026-09-22':None}
        row_hi = df.loc[df['最高'].idxmax()]
        row_lo = df.loc[df['最低'].idxmin()]
        last = df.iloc[-1]
        print('%s  最高日 %s %.1f | 最低日 %s %.1f | 最新 %s %.1f | 低点->最新 %+.1f%%' % (
            name, str(row_hi['日期']), row_hi['最高'], str(row_lo['日期']), row_lo['最低'],
            str(last['日期']), last['收盘'], (last['收盘']/row_lo['最低']-1)*100))
    except Exception as e:
        print(name, 'FAIL', type(e).__name__, str(e)[:120])
