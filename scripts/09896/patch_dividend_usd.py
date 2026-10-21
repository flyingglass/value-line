# -*- coding: utf-8 -*-
"""名创优品 09896 — 股息币种换算（美元 → 人民币）。

问题：AKShare 港股分红对名创优品返回的是「每股派美元X元」，fetcher 只做港币→人民币换算，
      美元股息被原样写入 dividend.cash_dps，导致 DPS / 派息率 / 股息率整体偏小约 7 倍。

做法：从外管局中间价（ak.currency_boc_safe）取该财年 12-31 的美元中间价，把每股美元股息
      折成人民币后再写入。所有原始文本保留在 raw_text 列，可复算。

校验：2025 年合计 DPS = 0.1665 美元 × 7.0288 ≈ 1.17 元人民币；
      对应 GAAP EPS 0.98 元派息率 >100%（因永辉权益法亏损压低净利），
      对经调整净利 28.98 亿元则约 50%，与年报披露的股息总额（1.01+1.16 亿美元）一致。
"""
import os
import re
import sqlite3
import sys
import warnings

warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import akshare as ak
import config

CODE = "09896"


def _usd_rates():
    df = ak.currency_boc_safe()[["日期", "美元"]].dropna()
    df["日期"] = df["日期"].astype(str)
    return dict(zip(df["日期"], df["美元"].astype(float) / 100.0))


def main():
    conn = sqlite3.connect(config.db_path(CODE))
    rates = _usd_rates()
    rows = conn.execute("SELECT report_year, cash_dps, raw_text FROM dividend").fetchall()
    done = []
    for fy, dps, raw in rows:
        raw = raw or ""
        if "美元" not in raw:
            continue
        usd = sum(float(x) for x in re.findall(r"每股派美元\s*([\d.]+)", raw))
        if usd <= 0:
            usd = float(dps or 0)
        rd = f"{fy}-12-31"
        fx = rates.get(rd) or next((rates[d] for d in sorted(rates, reverse=True)
                                    if d <= rd and rates[d] > 0), None)
        if not fx:
            print(f"  {fy}: 缺 {rd} 美元中间价, 跳过")
            continue
        cny = round(usd * fx, 4)
        conn.execute("UPDATE dividend SET cash_dps=? WHERE report_year=?", (cny, fy))
        done.append((fy, usd, fx, cny))
        print(f"  {fy}: {usd:.4f} USD × {fx:.4f} = {cny:.4f} CNY "
              f"(原库值 {dps} USD)")
    conn.commit()
    conn.execute("INSERT OR REPLACE INTO meta VALUES (?,?)",
                 ("dividend_note", "AKShare 返回美元股息, 已按外管局财年末美元中间价折为人民币"))
    conn.commit()
    conn.close()
    print(f"\n换算 {len(done)} 年")


if __name__ == "__main__":
    main()
