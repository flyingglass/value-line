# -*- coding: utf-8 -*-
"""广州待选池 35 家 · 位置（赔率第①细项：空头是否衰竭）统一测算

数据源：本地 data/<code>.db 的 kline 表优先；缺失则 AKShare 补拉。
输出：scripts/out/gz_pool_position.csv + 控制台表格。

指标口径（本项目近似，非里海原方法）：
  pct250     现价在近 250 交易日区间中的分位 = (last-low)/(high-low)
  dd_h250    距 250 日高点的回撤
  amp120     近 120 交易日振幅 = (max-min)/min
  low20      最近 20 个交易日内是否出现过 250 日新低（1=是）
  chg60/20   近 60 / 20 交易日涨跌幅
"""

import os
import sqlite3
import sys

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
OUT = os.path.join(ROOT, "scripts", "out")

# 代码 -> (名称, 市场)。市场：cn / hk
POOL = [
    ("000893", "亚钾国际", "cn"), ("301283", "聚胶股份", "cn"),
    ("301373", "凌玮科技", "cn"), ("301683", "慧谷新材", "cn"),
    ("603002", "宏昌电子", "cn"), ("603193", "润本股份", "cn"),
    ("603983", "丸美生物", "cn"), ("688548", "广钢气体", "cn"),
    ("688625", "呈和科技", "cn"),
    ("002030", "达安基因", "cn"), ("01681", "康臣药业", "hk"),
    ("300482", "万孚生物", "cn"), ("603233", "大参林", "cn"),
    ("603882", "金域医学", "cn"), ("688177", "百奥泰", "cn"),
    ("002209", "达意隆", "cn"), ("002833", "弘亚数控", "cn"),
    ("300503", "昊志机电", "cn"), ("688090", "瑞松科技", "cn"),
    ("002192", "融捷股份", "cn"), ("002709", "天赐材料", "cn"),
    ("301323", "新莱福", "cn"),
    ("001389", "广合科技", "cn"), ("002841", "视源股份", "cn"),
    ("000429", "粤高速A", "cn"), ("600428", "中远海特", "cn"),
    ("003010", "若羽臣", "cn"), ("09896", "名创优品", "hk"),
    ("001285", "瑞立科密", "cn"),
    ("002461", "珠江啤酒", "cn"),
    ("002832", "比音勒芬", "cn"),
    ("300438", "鹏辉能源", "cn"),
    ("301638", "南网数字", "cn"),
    ("002967", "广电计量", "cn"),
    ("01860", "汇量科技", "hk"),
]

START, END = "20250101", "20260924"


def from_db(code):
    p = os.path.join(DATA, "%s.db" % code)
    if not os.path.exists(p):
        return None
    try:
        con = sqlite3.connect(p)
        df = pd.read_sql("SELECT date, close FROM kline ORDER BY date", con)
        con.close()
    except Exception:
        return None
    if df.empty:
        return None
    df["date"] = df["date"].astype(str).str.slice(0, 10)
    return df


def from_ak(code, market, retries=4, sleep=3.0):
    import time
    import akshare as ak
    for i in range(retries):
        try:
            if market == "hk":
                df = ak.stock_hk_hist(symbol=code, period="daily",
                                      start_date=START, end_date=END, adjust="qfq")
            else:
                df = ak.stock_zh_a_hist(symbol=code, period="daily",
                                        start_date=START, end_date=END, adjust="qfq")
            if df is None or df.empty:
                return None
            d = df[["日期", "收盘"]].copy()
            d.columns = ["date", "close"]
            d["date"] = d["date"].astype(str).str.slice(0, 10)
            time.sleep(sleep)
            return d
        except Exception as e:
            if i == retries - 1:
                print("  ! %s AKShare 失败(%d 次): %s" % (code, retries, e))
                return None
            time.sleep(sleep * (i + 1))
    return None


def metrics(df):
    s = df["close"].astype(float)
    if len(s) < 30:
        return None
    last = float(s.iloc[-1])
    w250 = s.tail(250)
    hi, lo = float(w250.max()), float(w250.min())
    pct250 = (last - lo) / (hi - lo) * 100 if hi > lo else None
    dd = (last / hi - 1) * 100 if hi else None
    w120 = s.tail(120)
    amp120 = (float(w120.max()) - float(w120.min())) / float(w120.min()) * 100
    low20 = 1 if float(s.tail(20).min()) <= lo * 1.0001 else 0

    def chg(n):
        if len(s) > n:
            return (last / float(s.iloc[-1 - n]) - 1) * 100
        return None

    return {
        "date": df["date"].iloc[-1],
        "close": round(last, 2),
        "pct250": None if pct250 is None else round(pct250, 1),
        "dd_h250": None if dd is None else round(dd, 1),
        "amp120": round(amp120, 1),
        "low20": low20,
        "chg60": None if chg(60) is None else round(chg(60), 1),
        "chg20": None if chg(20) is None else round(chg(20), 1),
        "bars": len(s),
    }


def main():
    os.makedirs(OUT, exist_ok=True)
    csv_path = os.path.join(OUT, "gz_pool_position.csv")
    done = {}
    if os.path.exists(csv_path):
        prev = pd.read_csv(csv_path, dtype={"code": str})
        for _, r in prev.iterrows():
            done[str(r["code"]).zfill(6)] = r.to_dict()

    # 命令行给出代码则只跑这些（用于补跑失败项），否则跑全部
    only = set(sys.argv[1:])
    todo = [(c, n, m) for c, n, m in POOL
            if (not only or c in only) and (c not in done or only)]

    rows = []
    for code, name, mkt in todo:
        df = from_db(code)
        src = "DB"
        if (code in only or df is None
                or str(df["date"].iloc[-1]) < "2026-09-15"):
            df2 = from_ak(code, mkt)
            if df2 is not None and not df2.empty:
                df, src = df2, "AK"
        if df is None:
            print("%-8s %-8s 无数据" % (code, name))
            continue
        m = metrics(df)
        if m is None:
            print("%-8s %-8s 样本不足" % (code, name))
            continue
        m.update({"code": code, "name": name, "src": src})
        rows.append(m)
        print("%-8s %-8s %-4s %s  分位%6s%%  距高%7s%%  振幅120 %6s%%  新低20 %s  "
              "60日%7s%%  20日%7s%%  收盘%s(%s)"
              % (code, name, mkt, src, m["pct250"], m["dd_h250"], m["amp120"],
                 m["low20"], m["chg60"], m["chg20"], m["close"], m["date"]))

    merged = dict(done)
    for r in rows:
        merged[r["code"]] = r
    out = pd.DataFrame(list(merged.values()))
    cols = ["code", "name", "src", "date", "close", "pct250", "dd_h250",
            "amp120", "low20", "chg60", "chg20", "bars"]
    out = out[[c for c in cols if c in out.columns]].sort_values("pct250")
    p = os.path.join(OUT, "gz_pool_position.csv")
    out.to_csv(p, index=False, encoding="utf-8-sig")
    print("\n已写入 %s，累计 %d / %d 家" % (p, len(out), len(POOL)))


if __name__ == "__main__":
    main()
