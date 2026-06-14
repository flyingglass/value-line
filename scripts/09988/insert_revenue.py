# -*- coding: utf-8 -*-
"""阿里巴巴 09988 — 营收结构入库 (需补充实际年报拆分数据)"""
import sqlite3

code = "09988"
conn = sqlite3.connect(f"data/{code}.db")
conn.execute("CREATE TABLE IF NOT EXISTS revenue_structure (code TEXT, year TEXT, dim_type TEXT, dim_name TEXT, amount REAL, pct REAL)")
data = [
    # TODO: 替换为实际年报数据 (淘天集团/国际数字商业/云智能/菜鸟/本地生活等)
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
