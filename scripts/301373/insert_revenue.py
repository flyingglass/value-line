# -*- coding: utf-8 -*-
"""凌玮科技(301373) 营收结构数据 — 从年报PDF原文提取
来源: 2025年报 P26-27 营业收入构成 / 2023年报 P18 / 2022年报 P22
金额单位: 源数据为亿元, 入库统一换算为百万元 (×100, 与全库 revenue_structure.amount 约定一致, engine 交叉校验按 1e6 元换算)
"""
import sqlite3, os
_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
conn = sqlite3.connect(os.path.join(_root, "data/301373.db"))

_RAW = [  # (code, year, dim_type, dim_name, 金额亿元, pct)
    # ========== by_product ==========
    # 2025 (来源: 2025年报 营业收入构成 表)
    ("301373", "2025", "by_product", "纳米新材料",       4.8239, 96.42),
    ("301373", "2025", "by_product", "水性环氧乳液与固化剂", 0.1650, 3.30),
    ("301373", "2025", "by_product", "其他",            0.0139, 0.28),
    # 2024 (来源: 2025年报 同比列, 与2024年报一致)
    ("301373", "2024", "by_product", "纳米新材料",       4.6490, 97.08),
    ("301373", "2024", "by_product", "水性环氧乳液与固化剂", 0.1026, 2.14),
    ("301373", "2024", "by_product", "其他",            0.0374, 0.78),
    # 2023 (来源: 2023年报 营业收入构成)
    ("301373", "2023", "by_product", "纳米新材料",       4.1025, 88.06),
    ("301373", "2023", "by_product", "涂层助剂",         0.4872, 10.46),
    ("301373", "2023", "by_product", "其他",            0.0693, 1.49),
    # 2022 (来源: 2022/2023年报)
    ("301373", "2022", "by_product", "纳米新材料",       3.4378, 85.68),
    ("301373", "2022", "by_product", "涂层助剂",         0.5255, 13.10),
    ("301373", "2022", "by_product", "其他",            0.0491, 1.22),
    # 2021 (来源: 2022年报 同比列)
    ("301373", "2021", "by_product", "纳米新材料",       3.0527, 74.60),
    ("301373", "2021", "by_product", "涂层助剂",         0.9990, 24.41),
    ("301373", "2021", "by_product", "其他",            0.0402, 0.98),

    # ========== by_region ==========
    ("301373", "2025", "by_region", "境内", 4.1325, 82.60),
    ("301373", "2025", "by_region", "境外", 0.8703, 17.40),
    ("301373", "2024", "by_region", "境内", 3.6194, 75.58),
    ("301373", "2024", "by_region", "境外", 1.1696, 24.42),
    ("301373", "2023", "by_region", "境内", 3.7423, 80.33),
    ("301373", "2023", "by_region", "境外", 0.9166, 19.67),
    ("301373", "2022", "by_region", "境内", 3.2983, 82.20),
    ("301373", "2022", "by_region", "境外", 0.7141, 17.80),
    ("301373", "2021", "by_region", "境内", 3.7991, 92.85),
    ("301373", "2021", "by_region", "境外", 0.2927, 7.15),

    # ========== by_channel (分销售模式) ==========
    ("301373", "2025", "by_channel", "终端",   4.2829, 85.61),
    ("301373", "2025", "by_channel", "贸易商", 0.6705, 13.40),
    ("301373", "2025", "by_channel", "经销商", 0.0494, 0.99),
    ("301373", "2024", "by_channel", "终端",   3.8543, 80.48),
    ("301373", "2024", "by_channel", "贸易商", 0.8463, 17.67),
    ("301373", "2024", "by_channel", "经销商", 0.0884, 1.85),
    ("301373", "2023", "by_channel", "终端",   3.6095, 77.47),
    ("301373", "2023", "by_channel", "贸易商", 0.9934, 21.32),
    ("301373", "2023", "by_channel", "经销商", 0.0561, 1.20),
    ("301373", "2022", "by_channel", "终端",   2.9355, 73.16),
    ("301373", "2022", "by_channel", "贸易商", 1.0111, 25.20),
    ("301373", "2022", "by_channel", "经销商", 0.0659, 1.64),
]

data = [(c, y, d, n, round(amt * 100.0, 2), p) for (c, y, d, n, amt, p) in _RAW]

conn.executemany(
    "INSERT OR REPLACE INTO revenue_structure (code, year, dim_type, dim_name, amount, pct) VALUES (?,?,?,?,?,?)",
    data,
)
conn.commit()

rows = conn.execute(
    "SELECT dim_type, year, COUNT(*), ROUND(SUM(pct),1) FROM revenue_structure WHERE code='301373' GROUP BY dim_type, year ORDER BY year, dim_type"
).fetchall()
for r in rows:
    print(f"  {r[1]} {r[0]}: {r[2]} rows, pct_sum={r[3]}%")

total = conn.execute("SELECT COUNT(*) FROM revenue_structure WHERE code='301373'").fetchone()[0]
print(f"\n  总计: {total} 条记录")
conn.close()
print("Done.")
