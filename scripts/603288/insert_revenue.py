import sqlite3
code = "603288"
conn = sqlite3.connect(f"data/{code}.db")
conn.execute("DELETE FROM revenue_structure WHERE code=?", (code,))
data = [(code, '2025', 'by_product', '酱油', 13758.0, 50.2), (code, '2025', 'by_product', '蚝油', 4689.0, 17.1), (code, '2025', 'by_product', '调味酱', 2800.0, 10.2), (code, '2025', 'by_product', '其他', 6152.0, 22.5)]
conn.executemany("INSERT OR REPLACE INTO revenue_structure (code, year, dim_type, dim_name, amount, pct) VALUES (?,?,?,?,?,?)", data)
conn.commit()
print("OK")
conn.close()
