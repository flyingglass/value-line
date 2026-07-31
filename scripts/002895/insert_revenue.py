# -*- coding: utf-8 -*-
"""Insert 川恒股份 revenue structure from 2025 annual report
来源: 川恒股份 2025年报
金额单位: 百万元 CNY
"""
import sqlite3

code = "002895"
conn = sqlite3.connect(f"data/{code}.db")
conn.execute("DELETE FROM revenue_structure WHERE code=?", (code,))

data = [
    # ── by_product: 按产品 (2025) ──
    (code, '2025', 'by_product', '磷酸及饲料级磷酸二氢钙',  4904, 58.9),
    (code, '2025', 'by_product', '磷酸一铵',                1375, 16.5),
    (code, '2025', 'by_product', '磷酸铁及新能源材料',        733,  8.8),
    (code, '2025', 'by_product', '磷矿石',                   566,  6.8),
    (code, '2025', 'by_product', '其他',                     750,  9.0),
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
