# -*- coding: utf-8 -*-
"""亚钾国际(000893) 营收结构数据 — 从年报PDF原文提取

来源: 各年年报 第四节 主营业务分析 / (1) 营业收入构成
      2025年报 p25 / 2024年报 p26 / 2023年报 p23 / 2022年报 p24 / 2021年报 p18

金额单位: 源数据为元 (年报原文), _RAW 中记为亿元, 入库统一换算为百万元 (×100,
          与全库 revenue_structure.amount 约定一致, engine 交叉校验按 1e6 元换算)
百分比: 年报原文 "占营业收入比重"
"""
import sqlite3, os

_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
conn = sqlite3.connect(os.path.join(_root, "data", "000893.db"))

_RAW = [  # (code, year, dim_type, dim_name, 金额亿元, pct)
    # ========== by_product ==========
    # 2025 (来源: 2025年报 p25; 氯化钾52.02亿/卤水0.681亿/其他0.551亿)
    ("000893", "2025", "by_product", "氯化钾", 52.0176, 97.69),
    ("000893", "2025", "by_product", "卤水",    0.6813,  1.28),
    ("000893", "2025", "by_product", "其他",    0.5514,  1.03),
    # 2024 (来源: 2024年报 p26)
    ("000893", "2024", "by_product", "氯化钾", 34.6446, 97.65),
    ("000893", "2024", "by_product", "卤水",    0.4722,  1.33),
    ("000893", "2024", "by_product", "其他",    0.3631,  1.02),
    # 2023 (来源: 2023年报 p23)
    ("000893", "2023", "by_product", "氯化钾", 38.5198, 98.83),
    ("000893", "2023", "by_product", "卤水",    0.3928,  1.01),
    ("000893", "2023", "by_product", "其他",    0.0634,  0.16),
    # 2022 (来源: 2022年报 p24)
    ("000893", "2022", "by_product", "氯化钾", 34.0035, 98.10),
    ("000893", "2022", "by_product", "卤水",    0.6255,  1.81),
    ("000893", "2022", "by_product", "其他",    0.0321,  0.09),
    # 2021 (来源: 2021年报 p18; 谷物贸易当年金额为0, 不入库)
    ("000893", "2021", "by_product", "氯化钾",  8.2104, 98.57),
    ("000893", "2021", "by_product", "卤水",    0.1193,  1.43),

    # ========== by_region ==========
    # 2025 (来源: 2025年报 p25)
    ("000893", "2025", "by_region", "国内", 40.5850, 76.22),
    ("000893", "2025", "by_region", "国外", 12.6653, 23.78),
    # 2024 (来源: 2024年报 p26)
    ("000893", "2024", "by_region", "国内", 26.9978, 76.09),
    ("000893", "2024", "by_region", "国外",  8.4821, 23.91),
    # 2023 (来源: 2023年报 p23)
    ("000893", "2023", "by_region", "国内", 27.3359, 70.14),
    ("000893", "2023", "by_region", "国外", 11.6401, 29.86),
    # 2022 (来源: 2022年报 p24)
    ("000893", "2022", "by_region", "国内", 16.9130, 48.80),
    ("000893", "2022", "by_region", "国外", 17.7482, 51.20),
    # 2021 (来源: 2021年报 p18)
    ("000893", "2021", "by_region", "国内",  2.3682, 28.43),
    ("000893", "2021", "by_region", "国外",  5.9614, 71.57),
]

data = [(c, y, d, n, round(amt * 100.0, 2), p) for (c, y, d, n, amt, p) in _RAW]

conn.execute("DELETE FROM revenue_structure WHERE code='000893'")
conn.executemany(
    "INSERT OR REPLACE INTO revenue_structure (code, year, dim_type, dim_name, amount, pct) VALUES (?,?,?,?,?,?)",
    data,
)
conn.commit()

rows = conn.execute(
    "SELECT dim_type, year, COUNT(*), ROUND(SUM(pct),1), ROUND(SUM(amount)/100.0,2) "
    "FROM revenue_structure WHERE code='000893' GROUP BY dim_type, year ORDER BY year DESC, dim_type"
).fetchall()
for r in rows:
    print(f"  {r[1]} {r[0]}: {r[2]} rows, pct_sum={r[3]}%, amount_sum={r[4]}亿元")

total = conn.execute("SELECT COUNT(*) FROM revenue_structure WHERE code='000893'").fetchone()[0]
print(f"\n  总计: {total} 条记录")
conn.close()
print("Done.")
