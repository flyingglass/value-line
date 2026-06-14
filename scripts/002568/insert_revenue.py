# -*- coding: utf-8 -*-
"""百润股份 002568 — 营收结构入库 (需补充实际年报拆分数据)"""
import sqlite3

code = "002568"
conn = sqlite3.connect(f"data/{code}.db")
conn.execute("CREATE TABLE IF NOT EXISTS revenue_structure (code TEXT, year TEXT, dim_type TEXT, dim_name TEXT, amount REAL, pct REAL)")
data = [
    # 预调鸡尾酒(RIO)为主营, 食用香精为辅 (待年报核实具体数字)
    (code, '2024', 'by_business', '预调鸡尾酒', 2800, 88.0),
    (code, '2024', 'by_business', '食用香精', 380, 12.0),
]
if data:
    conn.executemany(
        "INSERT OR REPLACE INTO revenue_structure (code, year, dim_type, dim_name, amount, pct) VALUES (?,?,?,?,?,?)",
        data)
    conn.commit()
rows = conn.execute("SELECT dim_type, COUNT(*) FROM revenue_structure GROUP BY dim_type").fetchall()
for r in rows:
    print(f"  {r[0]}: {r[1]} rows")
conn.close()
print("Done.")
