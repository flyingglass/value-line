# -*- coding: utf-8 -*-
"""Insert 宏昌电子 603002 revenue structure from 2025 annual report

数据来源：603002_2025_年报.pdf「主营业务分行业、分产品、分地区、分销售模式情况」表（单位：元，转为百万元）
- 分行业口径合计 = 营业收入 3,076,276,159.24（含"其他"32,646,008.12）
- 分产品/分地区/分销售模式口径合计 = 主营业务收入 3,043,630,151.12
"""
import sqlite3

code = "603002"
conn = sqlite3.connect(f"data/{code}.db")

# Clear existing
conn.execute("DELETE FROM revenue_structure WHERE code=?", (code,))

data = [
    # by_product (2025) — 分行业（占营业收入 3,076.28M）
    (code, '2025', 'by_product', '环氧树脂', 1961.47, 63.76),
    (code, '2025', 'by_product', '覆铜板/半固化片', 1082.16, 35.18),
    (code, '2025', 'by_product', '其他', 32.65, 1.06),
    # by_segment (2025) — 分产品（占主营业务收入 3,043.63M）
    (code, '2025', 'by_segment', '液态环氧树脂', 1081.30, 35.54),
    (code, '2025', 'by_segment', '覆铜板/半固化片', 1082.16, 35.55),
    (code, '2025', 'by_segment', '阻燃环氧树脂', 525.33, 17.26),
    (code, '2025', 'by_segment', '固态环氧树脂', 237.19, 7.79),
    (code, '2025', 'by_segment', '溶剂环氧树脂', 117.29, 3.85),
    (code, '2025', 'by_segment', '其他环氧树脂', 0.36, 0.01),
    # by_region (2025) — 分地区（毛利率：国内 4.04%、国外 14.80%）
    (code, '2025', 'by_region', '国内', 2865.83, 94.16),
    (code, '2025', 'by_region', '国外', 177.80, 5.84),
    # by_channel (2025) — 分销售模式（内销毛利率 4.04%、外销 14.64%）
    (code, '2025', 'by_channel', '内销', 2863.92, 94.09),
    (code, '2025', 'by_channel', '外销', 179.71, 5.91),
]

conn.executemany(
    "INSERT OR REPLACE INTO revenue_structure (code, year, dim_type, dim_name, amount, pct) VALUES (?,?,?,?,?,?)",
    data
)
conn.commit()

# Verify
for dim in ['by_product', 'by_segment', 'by_region', 'by_channel']:
    rows = conn.execute(
        "SELECT dim_name, amount, pct FROM revenue_structure WHERE code=? AND year='2025' AND dim_type=?",
        (code, dim)
    ).fetchall()
    tot = sum(r[2] for r in rows)
    print(f"  {dim}: {len(rows)} rows, pct_sum={tot:.2f}%")
    for r in rows:
        print(f"    {r[0]}: {r[1]:.2f}M ({r[2]}%)")

conn.close()
print(f"\nDone. {len(data)} rows inserted.")
