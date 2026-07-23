# -*- coding: utf-8 -*-
"""药明康德(02359) 营收结构数据 — 从年报原文提取"""
import sqlite3

conn = sqlite3.connect("data/02359.db")

# 金额单位: 亿元 (从年报原文 / 100000000)
# 百分比: 年报原文
# 数据来源: 各年年报 — 营业收入构成表
data = [
    # ========== 2025 ========== 总营收 454.56亿 (来源: 2025年报)
    ("02359", "2025", "by_product", "化学业务(WuXi Chemistry)", 364.70, 80.23),
    ("02359", "2025", "by_product", "测试业务(WuXi Testing)", 40.40, 8.89),
    ("02359", "2025", "by_product", "生物学业务(WuXi Biology)", 26.80, 5.90),
    ("02359", "2025", "by_product", "其他业务", 22.66, 4.98),

    # ========== 2024 ========== 总营收 392.41亿 (来源: 2024年报)
    ("02359", "2024", "by_product", "化学业务(WuXi Chemistry)", 290.50, 74.04),
    ("02359", "2024", "by_product", "测试业务(WuXi Testing)", 56.70, 14.45),
    ("02359", "2024", "by_product", "生物学业务(WuXi Biology)", 25.40, 6.48),
    ("02359", "2024", "by_product", "终止经营及其他", 19.81, 5.03),

    # ========== 2023 ========== 总营收 403.41亿 (来源: 2023年报)
    ("02359", "2023", "by_product", "化学业务(WuXi Chemistry)", 291.71, 72.31),
    ("02359", "2023", "by_product", "测试业务(WuXi Testing)", 65.40, 16.21),
    ("02359", "2023", "by_product", "生物学业务(WuXi Biology)", 26.30, 6.52),
    ("02359", "2023", "by_product", "ATU/DDSU及其他", 20.00, 4.96),
]

conn.executemany(
    "INSERT OR REPLACE INTO revenue_structure (code, year, dim_type, dim_name, amount, pct) VALUES (?,?,?,?,?,?)",
    data,
)
conn.commit()

rows = conn.execute(
    "SELECT dim_type, year, COUNT(*), ROUND(SUM(pct),1) FROM revenue_structure WHERE code='02359' GROUP BY dim_type, year ORDER BY year, dim_type"
).fetchall()
for r in rows:
    print(f"  {r[1]} {r[0]}: {r[2]} rows, pct_sum={r[3]}%")

total = conn.execute("SELECT COUNT(*) FROM revenue_structure WHERE code='02359'").fetchone()[0]
print(f"\n  总计: {total} 条记录")
conn.close()
print("Done.")
