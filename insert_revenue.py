# -*- coding: utf-8 -*-
"""Insert revenue structure data into SQLite (run once per stock)"""
import sqlite3, sys

code = sys.argv[1] if len(sys.argv) > 1 else "09992"
conn = sqlite3.connect(f"data/{code}.db")

data = [
    # by_channel (PRC 2025)
    (code, '2025', 'by_channel', '零售店', 10075, 48.3),
    (code, '2025', 'by_channel', '线上渠道', 8522, 40.9),
    (code, '2025', 'by_channel', '机器人商店', 1346, 6.5),
    (code, '2025', 'by_channel', '批发及其他', 908, 4.3),
    # by_ip (2025)
    (code, '2025', 'by_ip', 'THE MONSTERS', 14161, 38.1),
    (code, '2025', 'by_ip', 'SKULLPANDA', 3540, 9.5),
    (code, '2025', 'by_ip', 'CRYBABY', 2929, 7.9),
    (code, '2025', 'by_ip', 'MOLLY', 2897, 7.8),
    (code, '2025', 'by_ip', 'DIMOO', 2777, 7.5),
    (code, '2025', 'by_ip', '星星人', 2056, 5.5),
    (code, '2025', 'by_ip', 'HIRONO', 1735, 4.7),
    (code, '2025', 'by_ip', '其他IP', 3312, 8.9),
    # by_region (2025)
    (code, '2025', 'by_region', '中国内地', 20852, 56.2),
    (code, '2025', 'by_region', '亚太', 8011, 21.6),
    (code, '2025', 'by_region', '美洲', 6806, 18.3),
    (code, '2025', 'by_region', '欧洲及其他', 1451, 3.9),
]

conn.executemany(
    'INSERT OR REPLACE INTO revenue_structure (code, year, dim_type, dim_name, amount, pct) VALUES (?,?,?,?,?,?)',
    data)
conn.commit()

# Verify
rows = conn.execute("SELECT dim_type, COUNT(*) FROM revenue_structure GROUP BY dim_type").fetchall()
for r in rows:
    print(f"  {r[0]}: {r[1]} rows")
conn.close()
print("Done.")
