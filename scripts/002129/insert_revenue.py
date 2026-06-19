# -*- coding: utf-8 -*-
"""TCL中环(002129) 营收结构数据 — 从年报PDF提取"""
import sqlite3

conn = sqlite3.connect("data/002129.db")

# 金额单位: 亿元 (从年报原始数据)
# 百分比: 基于总营收计算
# 数据来源: 各年年报、富途牛牛、前瞻眼、雪球公开数据
data = [
    # ========== 2025 ========== 总营收 290.50亿 (来源: 2025年报/富途牛牛)
    ("002129", "2025", "by_product", "光伏硅片", 122.38, 42.13),
    ("002129", "2025", "by_product", "光伏组件", 93.24, 32.10),
    ("002129", "2025", "by_product", "半导体材料", 57.07, 19.64),
    ("002129", "2025", "by_product", "光伏电站", 11.63, 4.00),
    ("002129", "2025", "by_product", "其他", 6.18, 2.13),

    # ========== 2024 ========== 总营收 284.19亿 (来源: 2024年报)
    ("002129", "2024", "by_product", "光伏硅片", 166.49, 58.58),
    ("002129", "2024", "by_product", "光伏组件", 58.11, 20.45),
    ("002129", "2024", "by_product", "半导体材料", 46.87, 16.49),
    ("002129", "2024", "by_product", "光伏电站及其他", 12.72, 4.48),

    # ========== 2023 ========== 总营收 591.46亿 (来源: 2023年报/雪球)
    ("002129", "2023", "by_product", "光伏硅片", 437.91, 74.04),
    ("002129", "2023", "by_product", "光伏组件", 93.09, 15.74),
    ("002129", "2023", "by_product", "半导体材料", 32.63, 5.52),
    ("002129", "2023", "by_product", "光伏电站及其他", 27.83, 4.70),

    # ========== 2022 ========== 总营收 670.10亿 (来源: 2022年报/雪球)
    ("002129", "2022", "by_product", "光伏硅片", 509.00, 75.96),
    ("002129", "2022", "by_product", "光伏组件", 108.42, 16.18),
    ("002129", "2022", "by_product", "半导体材料", 30.00, 4.48),
    ("002129", "2022", "by_product", "光伏电站及其他", 22.68, 3.38),

    # ========== 2021 ========== 总营收 411.05亿 (来源: 2021年报/雪球)
    ("002129", "2021", "by_product", "光伏硅片", 317.97, 77.36),
    ("002129", "2021", "by_product", "光伏组件", 61.19, 14.89),
    ("002129", "2021", "by_product", "半导体材料", 21.26, 5.17),
    ("002129", "2021", "by_product", "光伏电站及其他", 10.63, 2.59),
]

conn.executemany(
    "INSERT OR REPLACE INTO revenue_structure (code, year, dim_type, dim_name, amount, pct) VALUES (?,?,?,?,?,?)",
    data,
)
conn.commit()

# Verify
rows = conn.execute(
    "SELECT dim_type, year, COUNT(*), ROUND(SUM(pct),1) FROM revenue_structure WHERE code='002129' GROUP BY dim_type, year ORDER BY year, dim_type"
).fetchall()
for r in rows:
    print(f"  {r[1]} {r[0]}: {r[2]} rows, pct_sum={r[3]}%")

total = conn.execute("SELECT COUNT(*) FROM revenue_structure WHERE code='002129'").fetchone()[0]
print(f"\n  总计: {total} 条记录")
conn.close()
print("Done.")
