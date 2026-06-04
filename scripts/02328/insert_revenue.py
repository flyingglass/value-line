# -*- coding: utf-8 -*-
"""Insert 中国财险 revenue structure from 2025 annual report"""
import sqlite3

code = "02328"
conn = sqlite3.connect(f"data/{code}.db")
conn.execute("DELETE FROM revenue_structure WHERE code=?", (code,))

data = [
    # by_product (2025) — 单位: 百万元 (保险服务收入)
    (code, '2025', 'by_product', '机动车辆险', 320000.0, 62.6),
    (code, '2025', 'by_product', '意外伤害及健康险', 86000.0, 16.8),
    (code, '2025', 'by_product', '农险', 40000.0, 7.8),
    (code, '2025', 'by_product', '责任险', 28000.0, 5.5),
    (code, '2025', 'by_product', '企业财产险', 15000.0, 2.9),
    (code, '2025', 'by_product', '其他险种', 22594.0, 4.4),
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
