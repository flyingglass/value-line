# -*- coding: utf-8 -*-
"""Insert revenue structure data for 华晨中国 (01114) into SQLite

单位: 百万(CNY) — engine.py 以 *1e6 转元
数据来源: 同花顺 F10 + 港交所年报(华晨宝马2022年起为联营公司,不并表)
"""
import sqlite3

code = "01114"
conn = sqlite3.connect(f"data/{code}.db")

data = [
    # === 2025 === (营收 11.82亿, 金杯全面复产)
    # by_product
    (code, '2025', 'by_product', '制造及销售轻型客车/MPV/汽车零部件', 1035, 87.6),
    (code, '2025', 'by_product', '汽车金融服务', 146, 12.4),
    # by_region
    (code, '2025', 'by_region', '中国', 1011, 85.5),
    (code, '2025', 'by_region', '欧洲', 96, 8.1),
    (code, '2025', 'by_region', '拉丁美洲及加勒比海', 37, 3.2),
    (code, '2025', 'by_region', '非洲', 19, 1.6),
    (code, '2025', 'by_region', '其他亚洲国家', 14, 1.2),
    (code, '2025', 'by_region', '其他', 5, 0.4),

    # === 2024 === (营收 10.96亿)
    # by_product
    (code, '2024', 'by_product', '制造及销售轻型客车/MPV/汽车零部件', 930, 84.9),
    (code, '2024', 'by_product', '汽车金融服务', 166, 15.1),
    # by_region
    (code, '2024', 'by_region', '中国', 922, 84.2),
    (code, '2024', 'by_region', '欧洲', 100, 9.1),
    (code, '2024', 'by_region', '拉丁美洲及加勒比海', 57, 5.2),
    (code, '2024', 'by_region', '其他亚洲国家', 9, 0.8),
    (code, '2024', 'by_region', '其他', 8, 0.7),

    # === 2023 === (营收 11.21亿)
    # by_product
    (code, '2023', 'by_product', '制造及销售轻型客车/MPV/汽车零部件', 950, 84.8),
    (code, '2023', 'by_product', '汽车金融服务', 171, 15.2),
    # by_region
    (code, '2023', 'by_region', '中国', 948, 84.6),
    (code, '2023', 'by_region', '欧洲', 102, 9.1),
    (code, '2023', 'by_region', '拉丁美洲及加勒比海', 42, 3.7),
    (code, '2023', 'by_region', '其他亚洲国家', 16, 1.4),
    (code, '2023', 'by_region', '其他', 13, 1.2),

    # === 2022 === (营收 11.31亿, BMW股权转让完成)
    # by_product
    (code, '2022', 'by_product', '制造及销售轻型客车/MPV/汽车零部件', 958, 84.7),
    (code, '2022', 'by_product', '汽车金融服务', 173, 15.3),
    # by_region
    (code, '2022', 'by_region', '中国', 957, 84.6),
    (code, '2022', 'by_region', '欧洲', 103, 9.1),
    (code, '2022', 'by_region', '拉丁美洲及加勒比海', 37, 3.3),
    (code, '2022', 'by_region', '其他亚洲国家', 19, 1.7),
    (code, '2022', 'by_region', '其他', 15, 1.3),
]

# 先清旧数据再插入
conn.execute("DELETE FROM revenue_structure WHERE code=?", (code,))
conn.executemany(
    'INSERT OR REPLACE INTO revenue_structure (code, year, dim_type, dim_name, amount, pct) VALUES (?,?,?,?,?,?)',
    data)
conn.commit()

# Verify
rows = conn.execute("SELECT year, dim_type, COUNT(*), SUM(amount) FROM revenue_structure WHERE code=? GROUP BY 1,2 ORDER BY 1 DESC, 2", (code,)).fetchall()
for r in rows:
    print(f"  {r[0]} {r[1]}: {r[2]} rows, sum={r[3]:.2f} 百万")
total = conn.execute("SELECT COUNT(*) FROM revenue_structure WHERE code=?", (code,)).fetchone()[0]
print(f"Total: {total} rows")
conn.close()
print("Done.")
