# -*- coding: utf-8 -*-
"""Insert 陕西煤业 revenue structure from 2025 annual report"""
import sqlite3

code = "601225"
conn = sqlite3.connect(f"data/{code}.db")
conn.execute("DELETE FROM revenue_structure WHERE code=?", (code,))

data = [
    # by_product (2025) — 单位: 百万元 (营收1581.79亿)
    (code, '2025', 'by_product', '自产煤', 102860.0, 65.0),
    (code, '2025', 'by_product', '贸易煤', 47460.0, 30.0),
    (code, '2025', 'by_product', '电力及其他', 7859.0, 5.0),
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
