# -*- coding: utf-8 -*-
"""中国民航信息网络 00696 — 营收结构入库 (需补充实际年报拆分数据)"""
import sqlite3

code = "00696"
conn = sqlite3.connect(f"data/{code}.db")
conn.execute("CREATE TABLE IF NOT EXISTS revenue_structure (code TEXT, year TEXT, dim_type TEXT, dim_name TEXT, amount REAL, pct REAL)")
data = [
    # TODO: 替换为实际年报数据 (航空信息技术服务/结算清算/系统集成等)
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
