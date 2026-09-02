# -*- coding: utf-8 -*-
"""秦安股份(603758) 营收结构数据 — 从年报PDF原文提取
来源: 2025年报 P31-32 主营业务分产品/分地区 / 2024年报 P25 同表
金额单位: 源数据为亿元(由元/1e8换算), 入库统一换算为百万元 (×100, 与全库 revenue_structure.amount 约定一致)
pct = 分项金额/主营合计 (主营=汽车零部件一条行业线, 2024-2025均≈99.9%营收)
by_channel: 100%直销, 不单独入库。
"""
import sqlite3, os
_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
conn = sqlite3.connect(os.path.join(_root, "data/603758.db"))

_RAW = [  # (code, year, dim_type, dim_name, 金额亿元, pct)
    # ========== by_product (2025年报 P32) ==========
    ("603758", "2025", "by_product", "缸盖",             6.91906444, 52.38),
    ("603758", "2025", "by_product", "缸体",             2.85093810, 21.59),
    ("603758", "2025", "by_product", "曲轴",             1.38960097, 10.52),
    ("603758", "2025", "by_product", "变速器箱体及其他", 2.04758936, 15.50),
    # ========== by_region (2025年报 P32) ==========
    ("603758", "2025", "by_region", "重庆市",   7.03556879, 53.27),
    ("603758", "2025", "by_region", "其他地区", 6.17162410, 46.73),
    # ========== by_product (2024年报 P25) ==========
    ("603758", "2024", "by_product", "缸盖",             8.77926016, 55.97),
    ("603758", "2024", "by_product", "缸体",             3.09816029, 19.75),
    ("603758", "2024", "by_product", "曲轴",             1.67480021, 10.68),
    ("603758", "2024", "by_product", "变速器箱体及其他", 2.13477401, 13.61),
    # ========== by_region (2024年报 P25) ==========
    ("603758", "2024", "by_region", "重庆市",       7.69997158, 49.09),
    ("603758", "2024", "by_region", "国内其他地区", 7.98702310, 50.91),
]

data = [(c, y, d, n, round(amt * 100.0, 2), p) for (c, y, d, n, amt, p) in _RAW]

conn.executemany(
    "INSERT OR REPLACE INTO revenue_structure (code, year, dim_type, dim_name, amount, pct) VALUES (?,?,?,?,?,?)",
    data,
)
conn.commit()

rows = conn.execute(
    "SELECT dim_type, year, COUNT(*), ROUND(SUM(pct),1) FROM revenue_structure WHERE code='603758' GROUP BY dim_type, year ORDER BY year, dim_type"
).fetchall()
for r in rows:
    print(f"  {r[1]} {r[0]}: {r[2]} rows, pct_sum={r[3]}%")

total = conn.execute("SELECT COUNT(*) FROM revenue_structure WHERE code='603758'").fetchone()[0]
print(f"\n  总计: {total} 条记录")
conn.close()
print("Done.")
