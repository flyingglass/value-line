# -*- coding: utf-8 -*-
"""太极集团(600129) 营收结构数据 — 从年报PDF原文提取
来源: 2025年报 P14-15 主营业务分行业/分地区 / 2024年报 P14-15 同表
金额单位: 源数据为万元, 入库统一换算为百万元 (万元/100; 与全库 revenue_structure.amount 约定一致, engine 交叉校验按 1e6 元换算)
pct 口径: 分部间抵销金额不单独入库。
  - by_industry: 分母 = 正向分部合计 (不含抵销), 各分部 pct_sum≈100%
  - by_region:   分母 = 主营总计 (含抵销后合计), 各地区 pct_sum≈100%
"""
import sqlite3, os
_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
conn = sqlite3.connect(os.path.join(_root, "data/600129.db"))

_RAW = [  # (code, year, dim_type, dim_name, 金额万元, pct)
    # ========== by_industry 2025 (2025年报 P14, 正向分部) ==========
    ("600129", "2025", "by_industry", "医药工业",     520036.70, 40.79),
    ("600129", "2025", "by_industry", "医药商业",     621036.79, 48.71),
    ("600129", "2025", "by_industry", "中药材资源",    118332.63,  9.28),
    ("600129", "2025", "by_industry", "大健康及国际",   15365.44,  1.21),
    ("600129", "2025", "by_industry", "服务业及其他",     107.01,  0.01),
    # ========== by_region 2025 (2025年报 P14-15, 分母=主营总计1,036,695.89万) ==========
    ("600129", "2025", "by_region", "西南", 680135.18, 65.61),
    ("600129", "2025", "by_region", "华东", 155057.82, 14.96),
    ("600129", "2025", "by_region", "华北",  59544.34,  5.74),
    ("600129", "2025", "by_region", "华南",  59234.93,  5.71),
    ("600129", "2025", "by_region", "华中",  41262.95,  3.98),
    ("600129", "2025", "by_region", "西北",  22263.97,  2.15),
    ("600129", "2025", "by_region", "东北",  18455.13,  1.78),
    ("600129", "2025", "by_region", "境外",     741.57,  0.07),
    # ========== by_industry 2024 (2024年报 P14, 正向分部) ==========
    ("600129", "2024", "by_industry", "医药工业",     703787.35, 46.01),
    ("600129", "2024", "by_industry", "医药商业",     674022.82, 44.07),
    ("600129", "2024", "by_industry", "中药材资源",    105287.64,  6.88),
    ("600129", "2024", "by_industry", "大健康及国际",   46118.92,  3.02),
    ("600129", "2024", "by_industry", "服务业及其他",     320.55,  0.02),
    # ========== by_region 2024 (2024年报 P15, 分母=主营总计1,223,549.38万) ==========
    ("600129", "2024", "by_region", "西南", 726955.11, 59.41),
    ("600129", "2024", "by_region", "华东", 236391.78, 19.32),
    ("600129", "2024", "by_region", "华北",  83481.62,  6.82),
    ("600129", "2024", "by_region", "华南",  79897.93,  6.53),
    ("600129", "2024", "by_region", "华中",  46662.78,  3.81),
    ("600129", "2024", "by_region", "西北",  29781.73,  2.43),
    ("600129", "2024", "by_region", "东北",  19464.75,  1.59),
    ("600129", "2024", "by_region", "境外",     913.68,  0.07),
]

data = [(c, y, d, n, round(amt / 100.0, 2), p) for (c, y, d, n, amt, p) in _RAW]

conn.executemany(
    "INSERT OR REPLACE INTO revenue_structure (code, year, dim_type, dim_name, amount, pct) VALUES (?,?,?,?,?,?)",
    data,
)
conn.commit()

rows = conn.execute(
    "SELECT dim_type, year, COUNT(*), ROUND(SUM(pct),1) FROM revenue_structure WHERE code='600129' GROUP BY dim_type, year ORDER BY year, dim_type"
).fetchall()
for r in rows:
    print(f"  {r[1]} {r[0]}: {r[2]} rows, pct_sum={r[3]}%")

total = conn.execute("SELECT COUNT(*) FROM revenue_structure WHERE code='600129'").fetchone()[0]
print(f"\n  总计: {total} 条记录")
conn.close()
print("Done.")
