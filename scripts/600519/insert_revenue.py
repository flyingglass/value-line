# -*- coding: utf-8 -*-
"""Insert 贵州茅台 revenue structure

数据源:
  - 2025 年度 : 2025年年度报告 PDF
  - 2026H1   : 2026年半年度报告 PDF (data/pdfs/600519/600519_2026_中报.pdf) 第8页「3、销售情况」
               PDF 原文(单位:万元):
                 按产品档次: 茅台酒 7,772,443.79 / 系列酒 1,293,418.65
                 按销售渠道: 直销 5,196,204.70 / 批发代理 3,869,657.74
                 按地区    : 国内 8,962,212.26 / 国外 103,650.18
                 注: 公司通过"i茅台"数字营销平台实现酒类不含税收入 4,026,356.42 万元

口径说明(重要, 修改前必读):
  1. 2026H1 为半年口径, 与年度数据不可比, 禁止当作全年数据使用。
  2. engine 的 revenue_structure 按 year 读取, 且校验逻辑会用 by_region 合计
     与 income 表年报营业额做交叉校验(阈值5%)。若把 H1 数据写入 year='2026',
     2026年报发布后将产生约50%的校验偏差。故 H1 数据以 year='2026H1' 单独存放:
     既不污染年度口径, 也不会被报告误展示(引擎查不到会自动回退到 2025)。
  3. i茅台 是直销渠道的下级细分, 若并入 by_channel 会破坏 pct 加总=100% 的校验,
     故单独存为 dim_type='by_platform'(引擎不展示/不校验该维度, 仅作数据沉淀)。

单位: 百万元 (1e6), 与 2025 年度数据保持一致
"""
import sqlite3

code = "600519"
conn = sqlite3.connect(f"data/{code}.db")

# Clear existing
conn.execute("DELETE FROM revenue_structure WHERE code=?", (code,))

data = [
    # ══════════ 2025 年度 (年报口径) ══════════
    # by_product (2025) — 分产品
    (code, '2025', 'by_product', '茅台酒', 146499.9, 86.8),
    (code, '2025', 'by_product', '其他系列酒', 22274.7, 13.2),
    # by_region (2025) — 分地区
    (code, '2025', 'by_region', '国内', 163924.4, 97.1),
    (code, '2025', 'by_region', '国外', 4850.1, 2.9),
    # by_channel (2025) — 分销售模式
    (code, '2025', 'by_channel', '直销', 84543.0, 50.1),
    (code, '2025', 'by_channel', '批发代理', 84231.6, 49.9),

    # ══════════ 2026H1 (半年口径, 来源: 2026年中报 PDF 第8页) ══════════
    # by_product (2026H1) — 分产品档次
    (code, '2026H1', 'by_product', '茅台酒', 77724.4, 85.7),
    (code, '2026H1', 'by_product', '系列酒', 12934.2, 14.3),
    # by_region (2026H1) — 分地区
    (code, '2026H1', 'by_region', '国内', 89622.1, 98.9),
    (code, '2026H1', 'by_region', '国外', 1036.5, 1.1),
    # by_channel (2026H1) — 分销售渠道
    (code, '2026H1', 'by_channel', '直销', 51962.0, 57.3),
    (code, '2026H1', 'by_channel', '批发代理', 38696.6, 42.7),
    # by_platform (2026H1) — 平台级细分(i茅台), 不参与 by_channel 加总
    (code, '2026H1', 'by_platform', 'i茅台', 40263.6, 44.4),
]

conn.executemany(
    "INSERT OR REPLACE INTO revenue_structure (code, year, dim_type, dim_name, amount, pct) VALUES (?,?,?,?,?,?)",
    data
)
conn.commit()

# Verify
for yr in ['2025', '2026H1']:
    print(f"\n───── {yr} ─────")
    for dim in ['by_product', 'by_region', 'by_channel', 'by_platform']:
        rows = conn.execute(
            "SELECT dim_name, amount, pct FROM revenue_structure WHERE code=? AND year=? AND dim_type=? ORDER BY amount DESC",
            (code, yr, dim)
        ).fetchall()
        if not rows:
            continue
        tot = sum(r[2] for r in rows)
        flag = "OK" if abs(100 - tot) < 0.5 or dim == 'by_platform' else "!! pct!=100"
        print(f"  {dim}: {len(rows)} rows, pct_sum={tot:.1f}%  [{flag}]")
        for r in rows:
            print(f"    {r[0]}: {r[1]:.1f}M ({r[2]}%)")

# 与 PDF 原文勾稽: 三个维度合计应一致 (906.586244 万元亿 = 90658.6 百万)
print("\n───── 勾稽校验 (2026H1) ─────")
for dim in ['by_product', 'by_region', 'by_channel']:
    s = conn.execute(
        "SELECT SUM(amount) FROM revenue_structure WHERE code=? AND year='2026H1' AND dim_type=?",
        (code, dim)).fetchone()[0]
    print(f"  {dim} 合计 = {s:.1f}M ({s/100:.1f}亿)")

conn.close()
print(f"\nDone. {len(data)} rows inserted.")
