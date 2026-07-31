import sqlite3
code = "601318"
conn = sqlite3.connect(f"data/{code}.db")
conn.execute("DELETE FROM revenue_structure WHERE code=?", (code,))
data = [(code, '2024', 'by_segment', '寿险及健康险', 450000.0, 48.0), (code, '2024', 'by_segment', '财产保险', 310000.0, 33.0), (code, '2024', 'by_segment', '银行', 120000.0, 13.0), (code, '2024', 'by_segment', '其他', 60000.0, 6.0)]
conn.executemany("INSERT OR REPLACE INTO revenue_structure (code, year, dim_type, dim_name, amount, pct) VALUES (?,?,?,?,?,?)", data)
conn.commit(); conn.close()
print("OK")
