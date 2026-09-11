# -*- coding: utf-8 -*-
"""Insert 涪陵榨菜 revenue structure from 2025 annual report

来源: 重庆市涪陵榨菜集团股份有限公司 2025 年年度报告全文
      （data/pdfs/002507/002507_2025_年报.pdf 第 21-22 页「2、收入与成本 (1)营业收入构成」）
金额单位: 百万元 CNY（年报原文单位为元）
校验: 营业收入合计 2,431,922,780.17 元 = 2,431.92 百万；各维度 pct 合计 100%
"""
import sqlite3

code = "002507"
conn = sqlite3.connect(f"data/{code}.db")
conn.execute("DELETE FROM revenue_structure WHERE code=?", (code,))

data = [
    # ── by_product: 分产品 (2025) ──
    (code, '2025', 'by_product', '榨菜',         2059.47, 84.69),
    (code, '2025', 'by_product', '泡菜',          214.24,  8.81),
    (code, '2025', 'by_product', '其他产品',       96.57,  3.97),
    (code, '2025', 'by_product', '萝卜',           57.49,  2.36),
    (code, '2025', 'by_product', '其他业务收入',    4.15,  0.17),

    # ── by_region: 分地区 (2025) ──
    (code, '2025', 'by_region', '华南销售大区',   662.31, 27.23),
    (code, '2025', 'by_region', '华东销售大区',   429.17, 17.65),
    (code, '2025', 'by_region', '华中销售大区',   323.25, 13.29),
    (code, '2025', 'by_region', '华北销售大区',   248.89, 10.23),
    (code, '2025', 'by_region', '西南销售大区',   220.55,  9.07),
    (code, '2025', 'by_region', '中原销售大区',   217.04,  8.93),
    (code, '2025', 'by_region', '西北销售大区',   182.59,  7.51),
    (code, '2025', 'by_region', '东北销售大区',    88.14,  3.62),
    (code, '2025', 'by_region', '出口',            55.82,  2.30),
    (code, '2025', 'by_region', '其他业务收入',     4.15,  0.17),

    # ── by_channel: 分销售模式 (2025) ──
    (code, '2025', 'by_channel', '经销',         2253.12, 92.65),
    (code, '2025', 'by_channel', '直销',          174.65,  7.18),
    (code, '2025', 'by_channel', '其他业务收入',     4.15,  0.17),
]

conn.executemany(
    "INSERT OR REPLACE INTO revenue_structure (code, year, dim_type, dim_name, amount, pct) "
    "VALUES (?,?,?,?,?,?)",
    data
)
conn.commit()

for dim in ['by_product', 'by_region', 'by_channel']:
    rows = conn.execute(
        "SELECT dim_name, amount, pct FROM revenue_structure "
        "WHERE code=? AND year='2025' AND dim_type=? ORDER BY amount DESC",
        (code, dim)).fetchall()
    print(f"\n{dim}: {len(rows)} 行, 金额合计 {sum(r[1] for r in rows):.2f} 百万, "
          f"pct 合计 {sum(r[2] for r in rows):.2f}%")
    for name, amt, pct in rows:
        print(f"  {name}: {amt:,.2f} 百万 ({pct}%)")

conn.close()
print(f"\nDone. {len(data)} rows inserted.")
