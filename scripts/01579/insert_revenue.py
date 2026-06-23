# -*- coding: utf-8 -*-
"""Insert revenue structure data into SQLite for 01579 颐海国际"""
import sqlite3, sys

code = sys.argv[1] if len(sys.argv) > 1 else "01579"
conn = sqlite3.connect(f"data/{code}.db")

data = [
    # by_product (2025 年报) — 火锅调味料/复合调味料/方便速食
    # 来源: 颐海国际2025年度业绩公告
    (code, '2025', 'by_product', '火锅调味料', 4038, 61.1),
    (code, '2025', 'by_product', '方便速食', 1564, 23.7),
    (code, '2025', 'by_product', '复合调味料', 916, 13.8),
    (code, '2025', 'by_product', '其他', 95, 1.4),
]

conn.executemany(
    'INSERT OR REPLACE INTO revenue_structure (code, year, dim_type, dim_name, amount, pct) VALUES (?,?,?,?,?,?)',
    data)
conn.commit()

rows = conn.execute("SELECT dim_type, COUNT(*) FROM revenue_structure GROUP BY dim_type").fetchall()
for r in rows:
    print(f"  {r[0]}: {r[1]} rows")
conn.close()
print("Done.")
