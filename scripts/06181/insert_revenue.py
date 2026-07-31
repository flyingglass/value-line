# -*- coding: utf-8 -*-
"""Insert 老铺黄金 revenue structure from 2025 annual report
来源: 老铺黄金 2025年报
金额单位: 百万元 CNY
"""
import sqlite3

code = "06181"
conn = sqlite3.connect(f"data/{code}.db")
conn.execute("DELETE FROM revenue_structure WHERE code=?", (code,))

data = [
    # ── by_channel: 按渠道 (2025) ──
    (code, '2025', 'by_channel', '线下门店', 22646, 82.9),
    (code, '2025', 'by_channel', '线上平台',  4657, 17.1),
]

conn.executemany(
    "INSERT OR REPLACE INTO revenue_structure (code, year, dim_type, dim_name, amount, pct) VALUES (?,?,?,?,?,?)",
    data
)
conn.commit()

for dim in ['by_channel']:
    rows = conn.execute(
        f"SELECT dim_name, amount, pct FROM revenue_structure WHERE code=? AND year='2025' AND dim_type=?",
        (code, dim)).fetchall()
    print(f"\n{dim}:")
    for name, amt, pct in rows:
        print(f"  {name}: {amt/100:.1f}亿 ({pct}%)")

conn.close()
