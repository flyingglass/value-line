# -*- coding: utf-8 -*-
"""Insert 北新建材 revenue structure from 2025 annual report"""
import sqlite3

code = "000786"
conn = sqlite3.connect(f"data/{code}.db")

# Clear existing
conn.execute("DELETE FROM revenue_structure WHERE code=?", (code,))

data = [
    # by_product (2025) — 分产品 (单位: 百万元)
    (code, '2025', 'by_product', '石膏板', 11963.0, 47.3),
    (code, '2025', 'by_product', '涂料', 5093.0, 20.1),
    (code, '2025', 'by_product', '防水卷材', 3314.0, 13.1),
    (code, '2025', 'by_product', '龙骨', 1972.0, 7.8),
    (code, '2025', 'by_product', '防水工程', 389.0, 1.5),
    (code, '2025', 'by_product', '其他', 2549.0, 10.1),
]

conn.executemany(
    "INSERT OR REPLACE INTO revenue_structure (code, year, dim_type, dim_name, amount, pct) VALUES (?,?,?,?,?,?)",
    data
)
conn.commit()

# Verify
for dim in ['by_product']:
    rows = conn.execute(
        "SELECT dim_name, amount, pct FROM revenue_structure WHERE code=? AND year='2025' AND dim_type=?",
        (code, dim)
    ).fetchall()
    tot = sum(r[2] for r in rows)
    print(f"  {dim}: {len(rows)} rows, pct_sum={tot:.1f}%")
    for r in rows:
        print(f"    {r[0]}: {r[1]:.1f}M ({r[2]}%)")

conn.close()
print(f"\nDone. {len(data)} rows inserted.")
