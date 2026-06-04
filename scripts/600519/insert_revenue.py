# -*- coding: utf-8 -*-
"""Insert 贵州茅台 revenue structure from 2025 annual report PDF"""
import sqlite3

code = "600519"
conn = sqlite3.connect(f"data/{code}.db")

# Clear existing
conn.execute("DELETE FROM revenue_structure WHERE code=?", (code,))

data = [
    # by_product (2025) — 分产品
    (code, '2025', 'by_product', '茅台酒', 146499.9, 86.8),
    (code, '2025', 'by_product', '其他系列酒', 22274.7, 13.2),
    # by_region (2025) — 分地区
    (code, '2025', 'by_region', '国内', 163924.4, 97.1),
    (code, '2025', 'by_region', '国外', 4850.1, 2.9),
    # by_channel (2025) — 分销售模式
    (code, '2025', 'by_channel', '直销', 84543.0, 50.1),
    (code, '2025', 'by_channel', '批发代理', 84231.6, 49.9),
]

conn.executemany(
    "INSERT OR REPLACE INTO revenue_structure (code, year, dim_type, dim_name, amount, pct) VALUES (?,?,?,?,?,?)",
    data
)
conn.commit()

# Verify
for dim in ['by_product', 'by_region', 'by_channel']:
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
