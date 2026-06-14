# -*- coding: utf-8 -*-
"""腾讯控股 00700 — 营收结构入库 (需补充实际年报拆分数据)"""
import sqlite3

code = "00700"
conn = sqlite3.connect(f"data/{code}.db")
conn.execute("CREATE TABLE IF NOT EXISTS revenue_structure (code TEXT, year TEXT, dim_type TEXT, dim_name TEXT, amount REAL, pct REAL)")
data = [
    # TODO: 替换为实际年报数据 (code, year, dim_type, dim_name, amount, pct)
    # 示例: 增值服务/金融科技/广告/其他 四大板块
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
