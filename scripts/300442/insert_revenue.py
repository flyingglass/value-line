# -*- coding: utf-8 -*-
"""润泽科技(300442) 营收结构数据 — 从年报PDF提取"""
import sqlite3

conn = sqlite3.connect("data/300442.db")

# 金额单位: 亿元
# 数据来源: 2021-2025各年年报、东方财富F10、同花顺
data = [
    # ========== 2025 ========== 总营收 56.74亿
    ("300442", "2025", "by_product", "IDC业务", 31.64, 55.76),
    ("300442", "2025", "by_product", "AIDC业务", 25.10, 44.24),

    # ========== 2024 ========== 总营收 43.65亿
    ("300442", "2024", "by_product", "IDC业务", 29.14, 66.75),
    ("300442", "2024", "by_product", "AIDC业务", 14.51, 33.25),

    # ========== 2023 ========== 总营收 43.51亿
    ("300442", "2023", "by_product", "IDC业务", 31.52, 72.44),
    ("300442", "2023", "by_product", "AIDC业务", 11.99, 27.56),

    # ========== 2022 ========== 总营收 27.15亿 (借壳上市首年，AIDC尚未单独列示)
    ("300442", "2022", "by_product", "IDC业务", 27.15, 100.00),

    # ========== 2021 ========== 总营收 20.47亿 (借壳前)
    ("300442", "2021", "by_product", "IDC业务", 20.47, 100.00),
]

conn.executemany(
    "INSERT OR REPLACE INTO revenue_structure (code, year, dim_type, dim_name, amount, pct) VALUES (?,?,?,?,?,?)",
    data,
)
conn.commit()

# Verify
rows = conn.execute(
    "SELECT dim_type, year, COUNT(*), ROUND(SUM(pct),1) FROM revenue_structure WHERE code='300442' GROUP BY dim_type, year ORDER BY year, dim_type"
).fetchall()
for r in rows:
    print(f"  {r[1]} {r[0]}: {r[2]} rows, pct_sum={r[3]}%")

total = conn.execute("SELECT COUNT(*) FROM revenue_structure WHERE code='300442'").fetchone()[0]
print(f"\n  总计: {total} 条记录")
conn.close()
print("Done.")
