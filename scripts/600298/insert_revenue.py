# -*- coding: utf-8 -*-
"""Insert 安琪酵母 revenue structure from 2025 annual report"""
import sqlite3

code = "600298"
conn = sqlite3.connect(f"data/{code}.db")

# Clear existing
conn.execute("DELETE FROM revenue_structure WHERE code=?", (code,))

data = [
    # by_product (2025) — 分产品 (来源: 2025年年报)
    (code, '2025', 'by_product', '酵母及深加工产品', 11949, 71.4),
    (code, '2025', 'by_product', '食品原料', 2218, 13.3),
    (code, '2025', 'by_product', '制糖', 1339, 8.0),
    (code, '2025', 'by_product', '其他', 789, 4.7),
    (code, '2025', 'by_product', '包装', 360, 2.2),
    # by_region (2025) — 分地区
    (code, '2025', 'by_region', '国内', 9805, 58.6),
    (code, '2025', 'by_region', '国外', 6848, 40.9),
    # by_channel (2025) — 分渠道
    (code, '2025', 'by_channel', '线下', 12462, 74.5),
    (code, '2025', 'by_channel', '线上', 4191, 25.1),
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
        print(f"    {r[0]}: {r[1]:.0f}M ({r[2]}%)")

conn.close()
print(f"\nDone. {len(data)} rows inserted.")
