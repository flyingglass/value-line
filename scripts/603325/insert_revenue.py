# -*- coding: utf-8 -*-
"""博隆技术(603325) 营收结构数据 — 从年报PDF原文提取
来源: 2025年报 P17-18 主营业务分产品/分地区 / 2024年报 P20 / 2023年报 P20
金额单位: 源数据为亿元, 入库统一换算为百万元 (×100, 与全库 revenue_structure.amount 约定一致, engine 交叉校验按 1e6 元换算)
百分比按 主营收入 = 分项金额/主营合计 计算 (与年报"分行业/分产品/分地区"表一致)
主营口径说明: 博隆主营收入即气力输送系统一条行业线 (2023-2025 均占营收 ~99.98%),
  by_product / by_region 均以此主营合计数为分母; by_channel 100% 直销, 不单独入库。
"""
import sqlite3, os
_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
conn = sqlite3.connect(os.path.join(_root, "data/603325.db"))

_RAW = [  # (code, year, dim_type, dim_name, 金额亿元, pct)
    # ========== by_product ==========
    # 2025 (来源: 2025年报 P18 主营业务分产品情况)
    ("603325", "2025", "by_product", "成套系统",          10.6298, 78.56),
    ("603325", "2025", "by_product", "单一功能系统",        2.5356, 18.74),
    ("603325", "2025", "by_product", "部件备件及服务",      0.3652, 2.70),
    # 2024 (来源: 2024年报 P20)
    ("603325", "2024", "by_product", "成套系统",           9.5949, 82.99),
    ("603325", "2024", "by_product", "单一功能系统",        1.6213, 14.02),
    ("603325", "2024", "by_product", "部件备件及服务",      0.3458, 2.99),
    # 2023 (来源: 2023年报 P20)
    ("603325", "2023", "by_product", "成套系统",           9.4952, 77.65),
    ("603325", "2023", "by_product", "单一功能系统",        2.3428, 19.16),
    ("603325", "2023", "by_product", "部件备件及服务",      0.3901, 3.19),
    # ========== by_region ==========
    # 2025 (来源: 2025年报 P18 主营业务分地区情况)
    ("603325", "2025", "by_region", "境内", 11.4722, 84.79),
    ("603325", "2025", "by_region", "境外",  2.0584, 15.21),
    # 2024 (来源: 2024年报 P20)
    ("603325", "2024", "by_region", "境内", 10.9197, 94.45),
    ("603325", "2024", "by_region", "境外",  0.6422, 5.55),
    # 2023 (来源: 2023年报 P20)
    ("603325", "2023", "by_region", "境内", 11.6640, 95.39),
    ("603325", "2023", "by_region", "境外",  0.5641, 4.61),
]

data = [(c, y, d, n, round(amt * 100.0, 2), p) for (c, y, d, n, amt, p) in _RAW]

conn.executemany(
    "INSERT OR REPLACE INTO revenue_structure (code, year, dim_type, dim_name, amount, pct) VALUES (?,?,?,?,?,?)",
    data,
)
conn.commit()

rows = conn.execute(
    "SELECT dim_type, year, COUNT(*), ROUND(SUM(pct),1) FROM revenue_structure WHERE code='603325' GROUP BY dim_type, year ORDER BY year, dim_type"
).fetchall()
for r in rows:
    print(f"  {r[1]} {r[0]}: {r[2]} rows, pct_sum={r[3]}%")

total = conn.execute("SELECT COUNT(*) FROM revenue_structure WHERE code='603325'").fetchone()[0]
print(f"\n  总计: {total} 条记录")
conn.close()
print("Done.")
