# -*- coding: utf-8 -*-
"""Insert 农夫山泉 revenue structure from 2025 annual report"""
import sqlite3

code = "09633"
conn = sqlite3.connect(f"data/{code}.db")
conn.execute("DELETE FROM revenue_structure WHERE code=?", (code,))

data = [
    # by_product (2025) — 单位: 百万元
    (code, '2025', 'by_product', '包装饮用水', 23000.0, 44.0),
    (code, '2025', 'by_product', '茶饮料(东方树叶)', 18000.0, 34.0),
    (code, '2025', 'by_product', '功能饮料(尖叫等)', 6000.0, 12.0),
    (code, '2025', 'by_product', '果汁及其他', 5200.0, 10.0),
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
conn.close(); print(f"Done. {len(data)} rows.")
