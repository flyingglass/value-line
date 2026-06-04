# -*- coding: utf-8 -*-
"""Insert 东鹏饮料 revenue structure from 2025 annual report"""
import sqlite3

code = "605499"
conn = sqlite3.connect(f"data/{code}.db")
conn.execute("DELETE FROM revenue_structure WHERE code=?", (code,))

data = [
    # by_product (2025) — 单位: 百万元 (营收208.6亿)
    (code, '2025', 'by_product', '东鹏特饮', 15600.0, 74.8),
    (code, '2025', 'by_product', '东鹏补水啦(电解质)', 3274.0, 15.7),
    (code, '2025', 'by_product', '其他饮料', 1986.0, 9.5),
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
