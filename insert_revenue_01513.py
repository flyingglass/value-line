# -*- coding: utf-8 -*-
"""Insert 丽珠集团 revenue structure from 2025 annual report"""
import sqlite3

code = "01513"
conn = sqlite3.connect(f"data/{code}.db")
conn.execute("DELETE FROM revenue_structure WHERE code=?", (code,))

data = [
    # by_product (2025) — 单位: 百万元
    (code, '2025', 'by_product', '化学药', 6000.0, 46.0),
    (code, '2025', 'by_product', '中药', 2800.0, 22.0),
    (code, '2025', 'by_product', '生物药', 1500.0, 11.0),
    (code, '2025', 'by_product', '诊断试剂及设备', 2700.0, 21.0),
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
