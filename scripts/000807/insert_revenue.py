# -*- coding: utf-8 -*-
"""Insert 云铝股份 revenue structure from 2025 annual report"""
import sqlite3
code = "000807"
conn = sqlite3.connect(f"data/{code}.db")
conn.execute("DELETE FROM revenue_structure WHERE code=?", (code,))
data = [
    (code, '2025', 'by_product', '电解铝', 35000.0, 70.0),
    (code, '2025', 'by_product', '铝加工产品', 15000.0, 30.0),
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
