# -*- coding: utf-8 -*-
"""Insert 康臣药业 revenue structure from 2025 annual report
来源: 康臣药业 2025年报
金额单位: 百万元 CNY
"""
import sqlite3

code = "01681"
conn = sqlite3.connect(f"data/{code}.db")
conn.execute("DELETE FROM revenue_structure WHERE code=?", (code,))

data = [
    # ── by_product: 按产品 (2025) ──
    (code, '2025', 'by_product', '肾科药物', 2402, 70.3),
    (code, '2025', 'by_product', '玉林制药',  473, 13.8),
    (code, '2025', 'by_product', '妇儿药物',  376, 11.0),
    (code, '2025', 'by_product', '医用对比剂', 188,  5.5),
    # Note: 各板块合计 >100% 因内部抵消, 取主要板块
]

conn.executemany(
    "INSERT OR REPLACE INTO revenue_structure (code, year, dim_type, dim_name, amount, pct) VALUES (?,?,?,?,?,?)",
    data
)
conn.commit()

for dim in ['by_product']:
    rows = conn.execute(
        f"SELECT dim_name, amount, pct FROM revenue_structure WHERE code=? AND year='2025' AND dim_type=?",
        (code, dim)).fetchall()
    print(f"\n{dim}:")
    for name, amt, pct in rows:
        print(f"  {name}: {amt/100:.1f}亿 ({pct}%)")

conn.close()
