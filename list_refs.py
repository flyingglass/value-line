#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""批量提取所有股票的歷史PE/PB均值參考值。純只讀, 不寫任何文件。"""

import os, sys, sqlite3

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config

BASE = os.path.dirname(os.path.abspath(__file__))


def db_path(code):
    return os.path.join(BASE, "data", f"{code}.db")


def _get_hist_valuation_ref(code, method):
    """從 DB 讀取歷史 PE/PB 均值。返回 (label, avg_val, year_range) 或 None。"""
    db = db_path(code)
    if not os.path.exists(db):
        return None
    try:
        conn = sqlite3.connect(db)
        bps_rows = conn.execute(
            "SELECT report_date, amount FROM indicators WHERE item_name='BPS' AND report_date LIKE '%-12-31'"
        ).fetchall()
        eps_rows = conn.execute(
            "SELECT report_date, amount FROM indicators WHERE item_name='BASIC_EPS' AND report_date LIKE '%-12-31'"
        ).fetchall()
        pe_avg_rows = conn.execute(
            "SELECT report_date, amount FROM indicators WHERE item_name='PE_AVG' AND report_date LIKE '%-12-31'"
        ).fetchall()
        kl_rows = conn.execute(
            "SELECT date, close FROM kline WHERE date LIKE '%-12-%' ORDER BY date"
        ).fetchall()

        yr_price = {}
        for d, c in kl_rows:
            yr_price[d[:4]] = c
        yr_bps = {d[:4]: v for d, v in bps_rows if v and v > 0}
        yr_eps = {d[:4]: v for d, v in eps_rows if v and v > 0}
        yr_pe_avg = {d[:4]: v for d, v in pe_avg_rows if v and v > 0}

        years = sorted(set(yr_bps) & set(yr_eps) & set(yr_price))

        if method == "pb" and years:
            pbs = [yr_price[y] / yr_bps[y] for y in years if yr_bps[y] > 0]
            if pbs:
                avg = sum(pbs) / len(pbs)
                rng = f"{years[0]}-{years[-1]}"
                conn.close()
                return (f"歷史PB均值", round(avg, 2), rng)

        if method == "cf" and years:
            if len(yr_pe_avg) >= 3:
                pes = list(yr_pe_avg.values())
                avg = sum(pes) / len(pes)
                pe_years = sorted(yr_pe_avg.keys())
                rng = f"{pe_years[0]}-{pe_years[-1]}"
                conn.close()
                return (f"歷史PE均值(PE_AVG)", round(avg, 1), rng)
            else:
                pes = [yr_price[y] / yr_eps[y] for y in years if yr_eps[y] > 0]
                if pes:
                    avg = sum(pes) / len(pes)
                    rng = f"{years[0]}-{years[-1]}"
                    conn.close()
                    return (f"歷史PE均值(Price/EPS)", round(avg, 1), rng)

        conn.close()
    except Exception:
        pass
    return None


def main():
    pb_stocks = []
    cf_stocks = []
    no_db_stocks = []

    for code in config.STOCKS:
        stock = config.STOCKS[code]
        name = stock.get("name", code)
        method = stock.get("valuation_method", "cf")

        if not os.path.exists(db_path(code)):
            no_db_stocks.append((code, name, method))
            continue

        ref = _get_hist_valuation_ref(code, method)
        if method == "pb":
            pb_stocks.append((code, name, method, ref))
        else:
            cf_stocks.append((code, name, method, ref))

    print()
    print("=" * 92)
    print("  歷史估值參考一覽 (Historical Valuation Reference)")
    print("=" * 92)

    # ── PB 組 ──
    print(f"\n  {'─' * 88}")
    print(f"  【PB 估值組】共 {len(pb_stocks)} 隻 (需確認 --pb N)")
    print(f"  {'─' * 88}")
    for code, name, method, ref in pb_stocks:
        if ref:
            label, val, yr_range = ref
            print(f"  {code:<8} {name:<12} {label} [{yr_range}] = {val}x")
        else:
            print(f"  {code:<8} {name:<12} (無歷史數據)")

    # ── CF 組 ──
    print(f"\n  {'─' * 88}")
    print(f"  【CF 估值組】共 {len(cf_stocks)} 隻 (需確認 --cf N)")
    print(f"  {'─' * 88}")
    for code, name, method, ref in cf_stocks:
        if ref:
            label, val, yr_range = ref
            print(f"  {code:<8} {name:<12} {label} [{yr_range}] = {val}x")
        else:
            print(f"  {code:<8} {name:<12} (無歷史數據)")

    # ── 無 DB ──
    if no_db_stocks:
        print(f"\n  {'─' * 88}")
        print(f"  【無 DB / 未拉取】共 {len(no_db_stocks)} 隻 (需先跑 fetcher.py)")
        print(f"  {'─' * 88}")
        for code, name, method in no_db_stocks:
            param = "--pb N" if method == "pb" else "--cf N"
            print(f"  {code:<8} {name:<12} {param}")

    print(f"\n{'=' * 92}")
    total = len(pb_stocks) + len(cf_stocks)
    print(f"  有數據: PB {len(pb_stocks)} + CF {len(cf_stocks)} = {total} 隻 | 無DB: {len(no_db_stocks)} 隻")
    print(f"{'=' * 92}\n")


if __name__ == "__main__":
    main()
