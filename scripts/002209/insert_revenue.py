# -*- coding: utf-8 -*-
"""Insert 达意隆(002209) revenue structure from 2025 annual report

来源: 广州达意隆包装机械股份有限公司 2025 年年度报告全文
      （data/pdfs/002209/002209_2025_年报.pdf 第 25 页「2、收入与成本 (1)营业收入构成」）
金额单位: 百万元 CNY（年报原文单位为元）
校验: 营业收入合计 1,850,050,849.69 元 = 1,850.05 百万；各维度 pct 合计 100%
      2024 年合计 1,520,759,758.50 元 = 1,520.76 百万
交叉校验: AKShare stock_zygc_em(SZ002209) 2025-12-31 口径一致
"""
import sqlite3

code = "002209"
conn = sqlite3.connect(f"data/{code}.db")
conn.execute("DELETE FROM revenue_structure WHERE code=?", (code,))

data = [
    # ── 2025 · 分产品 ──
    (code, '2025', 'by_product', '液体包装机械及自动化设备', 1722.80, 93.12),
    (code, '2025', 'by_product', '代加工',                     124.64,  6.74),
    (code, '2025', 'by_product', '其他',                         2.61,  0.14),

    # ── 2025 · 分地区 ──
    (code, '2025', 'by_region', '境外',   786.34, 42.50),
    (code, '2025', 'by_region', '华南',   469.89, 25.40),
    (code, '2025', 'by_region', '华东',   308.87, 16.70),
    (code, '2025', 'by_region', '华北',   177.91,  9.62),
    (code, '2025', 'by_region', '华西',   104.42,  5.64),
    (code, '2025', 'by_region', '其他',     2.61,  0.14),

    # ── 2025 · 分销售模式 ──
    (code, '2025', 'by_channel', '直销', 1409.22, 76.17),
    (code, '2025', 'by_channel', '经销',  438.22, 23.69),
    (code, '2025', 'by_channel', '其他',    2.61,  0.14),

    # ── 2024 · 分产品 ──
    (code, '2024', 'by_product', '液体包装机械及自动化设备', 1360.14, 89.44),
    (code, '2024', 'by_product', '代加工',                     155.89, 10.25),
    (code, '2024', 'by_product', '其他',                         4.73,  0.31),

    # ── 2024 · 分地区 ──
    (code, '2024', 'by_region', '境外',   658.91, 43.33),
    (code, '2024', 'by_region', '华南',   430.29, 28.29),
    (code, '2024', 'by_region', '华东',   243.74, 16.03),
    (code, '2024', 'by_region', '华西',   115.06,  7.57),
    (code, '2024', 'by_region', '华北',    68.04,  4.47),
    (code, '2024', 'by_region', '其他',     4.73,  0.31),

    # ── 2024 · 分销售模式 ──
    (code, '2024', 'by_channel', '直销', 1113.95, 73.25),
    (code, '2024', 'by_channel', '经销',  402.08, 26.44),
    (code, '2024', 'by_channel', '其他',    4.73,  0.31),
]

conn.executemany(
    "INSERT OR REPLACE INTO revenue_structure (code, year, dim_type, dim_name, amount, pct) "
    "VALUES (?,?,?,?,?,?)",
    data
)
conn.commit()

for yr in ('2025', '2024'):
    for dim in ['by_product', 'by_region', 'by_channel']:
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
