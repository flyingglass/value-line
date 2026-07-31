# -*- coding: utf-8 -*-
"""Insert 阜丰集团 revenue structure from 2025 annual report
来源: 富途牛牛 00546 收入构成 (2025/FY)
金额单位: 亿元 CNY
"""
import sqlite3

code = "00546"
conn = sqlite3.connect(f"data/{code}.db")
conn.execute("DELETE FROM revenue_structure WHERE code=?", (code,))

data = [
    # ── by_product: 按业务分部 (2025) ──
    (code, '2025', 'by_product', '食品添加剂',   13389, 48.0),
    (code, '2025', 'by_product', '动物营养',     10527, 37.8),
    (code, '2025', 'by_product', '高档氨基酸',    1974,  7.1),
    (code, '2025', 'by_product', '胶体',          1226,  4.4),
    (code, '2025', 'by_product', '其他',           763,  2.7),
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
