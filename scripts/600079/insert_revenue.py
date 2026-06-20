# -*- coding: utf-8 -*-
"""人福医药(600079) 营收结构数据 — 从年报PDF原文提取(分行业)"""
import sqlite3

conn = sqlite3.connect("data/600079.db")

# 金额单位: 亿元 (从年报原文 / 100000000)
# 百分比: 基于分行业营收合计计算
# 数据来源: 各年年报PDF — 主营业务分行业情况表
data = [
    # ========== 2025 ========== 总营收 239.18亿 (来源: 2025年报 P23)
    ("600079", "2025", "by_product", "制造业", 142.14, 59.43),
    ("600079", "2025", "by_product", "批发及其他", 97.04, 40.57),

    # ========== 2024 ========== 总营收 253.86亿 (来源: 2025年报 同比列+2024年报)
    ("600079", "2024", "by_product", "制造业", 142.46, 56.12),
    ("600079", "2024", "by_product", "批发及其他", 111.40, 43.88),

    # ========== 2023 ========== 总营收 243.05亿 (来源: 2024年报 同比列+2023年报)
    ("600079", "2023", "by_product", "医药制造", 130.11, 53.53),
    ("600079", "2023", "by_product", "医药批发", 112.94, 46.47),

    # ========== 2022 ========== 总营收 221.39亿 (来源: 2023年报 同比列+2022年报)
    ("600079", "2022", "by_product", "医药制造", 114.81, 51.86),
    ("600079", "2022", "by_product", "医药批发", 106.58, 48.14),

    # ========== 2021 ========== 总营收 203.22亿 (来源: 2022年报 同比列+2021年报)
    ("600079", "2021", "by_product", "医药制造业", 101.43, 49.91),
    ("600079", "2021", "by_product", "医药批发及相关", 101.79, 50.09),
]

conn.executemany(
    "INSERT OR REPLACE INTO revenue_structure (code, year, dim_type, dim_name, amount, pct) VALUES (?,?,?,?,?,?)",
    data,
)
conn.commit()

rows = conn.execute(
    "SELECT dim_type, year, COUNT(*), ROUND(SUM(pct),1) FROM revenue_structure WHERE code='600079' GROUP BY dim_type, year ORDER BY year, dim_type"
).fetchall()
for r in rows:
    print(f"  {r[1]} {r[0]}: {r[2]} rows, pct_sum={r[3]}%")

total = conn.execute("SELECT COUNT(*) FROM revenue_structure WHERE code='600079'").fetchone()[0]
print(f"\n  总计: {total} 条记录")
conn.close()
print("Done.")
