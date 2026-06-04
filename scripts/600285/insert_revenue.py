# -*- coding: utf-8 -*-
"""Insert 羚锐制药 revenue structure from 2025 annual report"""
import sqlite3

code = "600285"
conn = sqlite3.connect(f"data/{code}.db")

# Clear existing
conn.execute("DELETE FROM revenue_structure WHERE code=?", (code,))

data = [
    # by_product (2025) — 分产品 (单位: 百万元)
    (code, '2025', 'by_product', '贴剂', 2171.0, 56.3),
    (code, '2025', 'by_product', '胶囊剂', 718.0, 18.6),
    (code, '2025', 'by_product', '片剂', 371.0, 9.6),
    (code, '2025', 'by_product', '软膏剂', 136.0, 3.5),
    (code, '2025', 'by_product', '其他(含银谷制药并表)', 453.0, 11.8),
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
