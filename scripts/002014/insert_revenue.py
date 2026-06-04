# -*- coding: utf-8 -*-
"""Insert 永新股份 revenue structure from 2025 annual report PDF"""
import sqlite3

code = "002014"
conn = sqlite3.connect(f"data/{code}.db")
conn.execute("DELETE FROM revenue_structure WHERE code=?", (code,))

data = [
    # by_product (2025) — 分产品
    (code, '2025', 'by_product', '彩印包装材料', 2550.2, 68.49),
    (code, '2025', 'by_product', '塑料软包装薄膜', 830.5, 22.31),
    (code, '2025', 'by_product', '油墨业务', 172.6, 4.64),
    (code, '2025', 'by_product', '镀铝包装材料', 61.7, 1.66),
    (code, '2025', 'by_product', '其他业务', 108.4, 2.91),
    # by_region (2025)
    (code, '2025', 'by_region', '国内市场', 3163.0, 84.95),
    (code, '2025', 'by_region', '国际市场', 560.4, 15.05),
    # by_industry (2025) — 分行业
    (code, '2025', 'by_industry', '橡胶和塑料制品业', 3442.4, 92.45),
    (code, '2025', 'by_industry', '涂料油墨颜料制造', 172.6, 4.64),
    (code, '2025', 'by_industry', '其他业务', 108.4, 2.91),
]

conn.executemany(
    "INSERT OR REPLACE INTO revenue_structure VALUES (?,?,?,?,?,?)",
    data
)
conn.commit()

for dim in ['by_product', 'by_region', 'by_industry']:
    rows = conn.execute(
        "SELECT dim_name, amount, pct FROM revenue_structure WHERE code=? AND year='2025' AND dim_type=?",
        (code, dim)
    ).fetchall()
    tot = sum(r[2] for r in rows)
    print(f"  {dim}: {len(rows)} rows, pct_sum={tot:.1f}%")

conn.close()
print(f"\nDone. {len(data)} rows.")
