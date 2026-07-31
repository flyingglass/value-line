# -*- coding: utf-8 -*-
"""Insert 拼多多 revenue structure from 2025 annual report
来源: PDD Holdings 2025 20-F
金额单位: 百万元 CNY
"""
import sqlite3

code = "PDD"
conn = sqlite3.connect(f"data/{code}.db")
conn.execute("DELETE FROM revenue_structure WHERE code=?", (code,))

data = [
    (code, '2025', 'by_type', '在线营销及其他', 217780, 50.4),
    (code, '2025', 'by_type', '交易服务',       214060, 49.6),
]

conn.executemany(
    "INSERT OR REPLACE INTO revenue_structure (code, year, dim_type, dim_name, amount, pct) VALUES (?,?,?,?,?,?)",
    data
)
conn.commit()

rows = conn.execute(
    "SELECT dim_name, amount, pct FROM revenue_structure WHERE code=? AND year='2025' AND dim_type='by_type'",
    (code,)).fetchall()
print("by_type:")
for name, amt, pct in rows:
    print(f"  {name}: {amt/100:.1f}亿 ({pct}%)")
conn.close()
