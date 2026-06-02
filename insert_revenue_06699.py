# -*- coding: utf-8 -*-
"""Insert revenue structure data for 时代天使 (06699) into SQLite

单位: 百万(HKD) — engine.py 以 *1e6 转元
数据来源: 腾讯自选股财报 MainOperIncomeProduct / MainOperIncomeRegion
"""
import sqlite3

code = "06699"
conn = sqlite3.connect(f"data/{code}.db")

# 原始数据(万元) → 除以100转为百万
data = [
    # === 2025 ===
    # by_product
    (code, '2025', 'by_product', '隐形矫治解决方案', 1542.78, 53.54),
    (code, '2025', 'by_product', '销售隐形矫治器', 1201.41, 41.69),
    (code, '2025', 'by_product', '销售其他产品', 120.68, 4.19),
    (code, '2025', 'by_product', '其他服务', 16.64, 0.58),
    # by_region
    (code, '2025', 'by_region', '中国内地', 1613.38, 55.99),
    (code, '2025', 'by_region', '全球(中国内地除外)', 1268.12, 44.01),

    # === 2024 ===
    # by_product
    (code, '2024', 'by_product', '隐形矫治解决方案', 1394.34, 66.83),
    (code, '2024', 'by_product', '销售隐形矫治器', 574.49, 27.53),
    (code, '2024', 'by_product', '销售其他产品', 98.81, 4.74),
    (code, '2024', 'by_product', '其他服务', 18.82, 0.90),
    # by_region
    (code, '2024', 'by_region', '中国内地', 1461.20, 70.03),
    (code, '2024', 'by_region', '其他国家及地区', 625.26, 29.97),

    # === 2023 ===
    # by_product
    (code, '2023', 'by_product', '隐形矫治解决方案', 1414.71, 86.90),
    (code, '2023', 'by_product', '销售产品(口内扫描仪等)', 194.17, 11.90),
    (code, '2023', 'by_product', '其他服务', 19.81, 1.20),
    # by_region
    (code, '2023', 'by_region', '中国内地', 1468.41, 90.16),
    (code, '2023', 'by_region', '其他国家及地区', 160.29, 9.84),

    # === 2022 ===
    # by_product
    (code, '2022', 'by_product', '隐形矫治解决方案', 1354.11, 95.30),
    (code, '2022', 'by_product', '销售口内扫描仪', 49.69, 3.50),
    (code, '2022', 'by_product', '其他服务', 17.61, 1.20),
]

# 先清旧数据再插入
conn.execute("DELETE FROM revenue_structure WHERE code=?", (code,))
conn.executemany(
    'INSERT OR REPLACE INTO revenue_structure (code, year, dim_type, dim_name, amount, pct) VALUES (?,?,?,?,?,?)',
    data)
conn.commit()

# Verify
rows = conn.execute("SELECT dim_type, COUNT(*), SUM(amount) FROM revenue_structure GROUP BY dim_type").fetchall()
for r in rows:
    print(f"  {r[0]}: {r[1]} rows, sum={r[2]:.2f} 百万")
total = conn.execute("SELECT COUNT(*) FROM revenue_structure").fetchone()[0]
print(f"Total: {total} rows")
conn.close()
print("Done.")
