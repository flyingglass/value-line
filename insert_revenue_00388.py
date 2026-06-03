# -*- coding: utf-8 -*-
"""Insert 香港交易所 revenue structure from 2025 annual report"""
import sqlite3

code = "00388"
conn = sqlite3.connect(f"data/{code}.db")
conn.execute("DELETE FROM revenue_structure WHERE code=?", (code,))

data = [
    # by_product (2025) — 单位: 百万HKD
    (code, '2025', 'by_product', '交易费及交易系统使用费', 7000.0, 32.0),
    (code, '2025', 'by_product', '结算及交收费', 5000.0, 23.0),
    (code, '2025', 'by_product', '上市费', 2000.0, 9.0),
    (code, '2025', 'by_product', '市场数据费', 1200.0, 5.0),
    (code, '2025', 'by_product', '投资收益及其他', 6800.0, 31.0),
]

conn.executemany(
    "INSERT OR REPLACE INTO revenue_structure (code, year, dim_type, dim_name, amount, pct) VALUES (?,?,?,?,?,?)",
    data
)
conn.commit()

for dim in ['by_product']:
    rows = conn.execute(f"SELECT dim_name, amount, pct FROM revenue_structure WHERE code=? AND year='2025' AND dim_type=?", (code, dim)).fetchall()
    print(f"  {dim}: {len(rows)} rows, pct_sum={sum(r[2] for r in rows):.1f}%")
    for r in rows: print(f"    {r[0]}: {r[1]:.1f}M ({r[2]}%)")

conn.close()
print(f"\nDone. {len(data)} rows inserted.")
