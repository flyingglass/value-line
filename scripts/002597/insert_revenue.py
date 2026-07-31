# -*- coding: utf-8 -*-
"""Insert 金禾实业 revenue structure from 2025 annual report
来源: 金禾实业 2025年报 (东方财富转载)
金额单位: 百万元 CNY
"""
import sqlite3

code = "002597"
conn = sqlite3.connect(f"data/{code}.db")
conn.execute("DELETE FROM revenue_structure WHERE code=?", (code,))

data = [
    # ── by_product: 按产品 (2025) ──
    (code, '2025', 'by_product', '食品添加剂', 2281, 46.44),
    (code, '2025', 'by_product', '大宗化学品', 1715, 34.93),
    (code, '2025', 'by_product', '其他',          915, 18.63),
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
