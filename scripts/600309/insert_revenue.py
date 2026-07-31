import sqlite3
code = "600309"
conn = sqlite3.connect(f"data/{code}.db")
conn.execute("DELETE FROM revenue_structure WHERE code=?", (code,))
data = [(code, '2024', 'by_product', '聚氨酯', 35000.0, 52.0), (code, '2024', 'by_product', '石化', 22000.0, 33.0), (code, '2024', 'by_product', '精细化学品', 10000.0, 15.0)]
conn.executemany("INSERT OR REPLACE INTO revenue_structure (code, year, dim_type, dim_name, amount, pct) VALUES (?,?,?,?,?,?)", data)
conn.commit(); conn.close()
print("OK")
