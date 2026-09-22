# -*- coding: utf-8 -*-
"""待选池标的行情/估值/位置扫描（只读，不入库）

用法：
    .venv\Scripts\python.exe scripts\tools\scan_quotes.py 603983 300482 002841

说明：
    东财接口（stock_zh_a_spot_em / stock_zh_a_hist / stock_individual_info_em）在本项目网络下常
    返回 RemoteDisconnected，故改用 腾讯行情 qt.gtimg.cn（现价/PE-TTM/PB/市值）+ 新浪日线
    （250 日与年内区间分位）。输出为控制台文本，供人工回填 wiki，不写任何数据库。
"""
import sys
import json
import requests

HDR = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)", "Referer": "https://finance.sina.com.cn"}


def sym(code):
    """A 股代码 -> 腾讯/新浪符号（沪市 sh，深市/北交所 sz）"""
    return ("sh" if code.startswith(("6", "9")) else "sz") + code


def quote(code):
    try:
        r = requests.get(f"https://qt.gtimg.cn/q={sym(code)}", headers=HDR, timeout=15)
        r.encoding = "gbk"
        txt = r.text.strip()
        if "~" not in txt:
            print(f"[{code}] 行情空返回：{txt[:120]}")
            return
        f = txt.split('"')[1].split("~")
        print(f"[{code}] {f[1]} 现价={f[3]} 昨收={f[4]} 涨跌幅={f[32]}% 换手={f[38]} "
              f"PE(TTM)={f[39]} PB={f[46]} 流通市值={f[44]}亿 总市值={f[45]}亿 成交额={f[37]}万")
    except Exception as e:
        print(f"[{code}] 行情 FAIL: {type(e).__name__} {e}")


def kline(code, n=250):
    url = ("http://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData"
           f"?symbol={sym(code)}&scale=240&ma=no&datalen={n}")
    try:
        r = requests.get(url, headers=HDR, timeout=15)
        txt = r.text.strip()
        if not txt.startswith("["):
            print(f"   日线空返回：{txt[:120]}")
            return
        data = json.loads(txt)
        hi = max(float(d["high"]) for d in data)
        lo = min(float(d["low"]) for d in data)
        last = float(data[-1]["close"])
        print(f"   K线 {len(data)} 根 {data[0]['day']}~{data[-1]['day']} 收盘={last:.2f}")
        print(f"   {n}日区间 {lo:.2f}~{hi:.2f} 分位={(last-lo)/(hi-lo)*100:.1f}% 距高点={(last/hi-1)*100:.1f}%")
        y = [d for d in data if d["day"] >= "2026-01-01"]
        if y:
            yhi = max(float(d["high"]) for d in y)
            ylo = min(float(d["low"]) for d in y)
            print(f"   2026 年内 {ylo:.2f}~{yhi:.2f} 分位={(last-ylo)/(yhi-ylo)*100:.1f}% "
                  f"年内涨跌={(last/float(y[0]['close'])-1)*100:.1f}%")
    except Exception as e:
        print(f"   日线 FAIL: {type(e).__name__} {e}")


if __name__ == "__main__":
    codes = sys.argv[1:] or ["603983", "300482", "002841", "002832", "003010", "001285"]
    for c in codes:
        print("=" * 70)
        quote(c)
        kline(c)
