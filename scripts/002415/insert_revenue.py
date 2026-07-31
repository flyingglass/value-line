import sqlite3
code = "002415"
conn = sqlite3.connect(f"data/{code}.db")
conn.execute("DELETE FROM revenue_structure WHERE code=?", (code,))
data = [(code, '2024', 'by_segment', '安防主业', 65000.0, 65.0), (code, '2024', 'by_segment', '创新业务', 25000.0, 25.0), (code, '2024', 'by_segment', '其他', 10000.0, 10.0)]
conn.executemany("INSERT OR REPLACE INTO revenue_structure (code, year, dim_type, dim_name, amount, pct) VALUES (?,?,?,?,?,?)", data)
conn.commit(); conn.close()
print("OK")
