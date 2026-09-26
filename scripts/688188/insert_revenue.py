# -*- coding: utf-8 -*-
"""Insert 柏楚电子(688188) revenue structure from 2025 annual report

来源: 上海柏楚电子科技股份有限公司 2025 年年度报告
      （data/pdfs/688188/688188_2025_年报.pdf 第 27-28 页「(1). 主营业务分行业、分产品、分地区、分销售模式情况」）
金额单位: 百万元 CNY（年报原文单位为元）
校验: 主营业务收入合计 2,166,644,760.24 元 = 2,166.64 百万，毛利率 77.92%
      与 income 表「其中：营业收入」2,196.0 百万差 1.36%（本表为主营业务口径，不含其他业务收入，<5% 容差）
2024 反算项: 年报仅披露本期金额+同比增减%，2024 金额 = 2025 金额 ÷ (1+增减%)，🟡 反算
      （反算合计 1,718.04 百万 vs 年报原话「主营业务收入较上年同期增长 44,876.98 万元」倒推的 1,717.87 百万，差 0.01%）
pct 由金额自算，避免手工误差。
"""
import sqlite3

code = "688188"
conn = sqlite3.connect(f"data/{code}.db")
conn.execute("DELETE FROM revenue_structure WHERE code=?", (code,))

# (year, dim_type, dim_name, amount_百万)
raw = [
    # ── 2025 · 分产品（年报 p27-28 原文） ──
    ("2025", "by_product", "平面解决方案", 1292.909787),
    ("2025", "by_product", "管材解决方案", 487.449750),
    ("2025", "by_product", "其他", 322.392556),
    ("2025", "by_product", "三维解决方案", 63.892667),
    # ── 2025 · 分地区（年报 p28 原文） ──
    ("2025", "by_region", "华东", 1552.427767),
    ("2025", "by_region", "华中和华南", 458.865077),
    ("2025", "by_region", "其他", 89.985675),
    ("2025", "by_region", "华北", 62.444944),
    ("2025", "by_region", "东北", 2.921296),
    # ── 2025 · 分销售模式（年报 p28 原文：直销 100%） ──
    ("2025", "by_channel", "直销", 2166.644760),
    # ── 2024 · 分产品（按 2025 年报同比增减% 反算 🟡） ──
    ("2024", "by_product", "平面解决方案", 1292.909787 / 1.1494),
    ("2024", "by_product", "管材解决方案", 487.449750 / 1.2820),
    ("2024", "by_product", "其他", 322.392556 / 1.8312),
    ("2024", "by_product", "三维解决方案", 63.892667 / 1.7373),
    # ── 2024 · 分地区（同上反算 🟡） ──
    ("2024", "by_region", "华东", 1552.427767 / 1.2629),
    ("2024", "by_region", "华中和华南", 458.865077 / 1.1784),
    ("2024", "by_region", "其他", 89.985675 / 1.8888),
    ("2024", "by_region", "华北", 62.444944 / 1.2889),
    ("2024", "by_region", "东北", 2.921296 / 0.9212),
    # ── 2024 · 分销售模式（直销 100%，2025 年报 p28 原文口径） ──
    ("2024", "by_channel", "直销", 1717.867710),
]

# pct 按同年同维度金额自算
from collections import defaultdict
totals = defaultdict(float)
for yr, dim, name, amt in raw:
    totals[(yr, dim)] += amt

data = []
for yr, dim, name, amt in raw:
    pct = round(amt / totals[(yr, dim)] * 100, 2)
    data.append((code, yr, dim, name, round(amt, 2), pct))

conn.executemany(
    "INSERT OR REPLACE INTO revenue_structure (code, year, dim_type, dim_name, amount, pct) "
    "VALUES (?,?,?,?,?,?)",
    data
)
conn.commit()

for yr in ("2025", "2024"):
    for dim in ("by_product", "by_region", "by_channel"):
        rows = conn.execute(
            "SELECT dim_name, amount, pct FROM revenue_structure "
            "WHERE code=? AND year=? AND dim_type=? ORDER BY amount DESC",
            (code, yr, dim)).fetchall()
        print(f"\n{yr} {dim}: {len(rows)} 行, 金额合计 {sum(r[1] for r in rows):.2f} 百万, "
              f"pct 合计 {sum(r[2] for r in rows):.2f}%")
        for name, amt, pct in rows:
            print(f"  {name}: {amt:,.2f} 百万 ({pct}%)")

conn.close()
print(f"\nDone. {len(data)} rows inserted.")
