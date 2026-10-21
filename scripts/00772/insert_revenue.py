# -*- coding: utf-8 -*-
"""阅文集团 00772 — 营收结构入库

数据来源：年报 MD&A「按分部划分的收入」表（人民币千元换算为百万元）
- FY2025 年报 P13（截至2025/2024-12-31）
- FY2024 年报 P12（截至2024/2023-12-31）
"""
import os
import sqlite3

code = "00772"
base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
conn = sqlite3.connect(os.path.join(base, "data", "db", f"{code}.db"))
conn.execute("CREATE TABLE IF NOT EXISTS revenue_structure "
             "(code TEXT, year TEXT, dim_type TEXT, dim_name TEXT, amount REAL, pct REAL)")

data = [
    # ── by_segment: 两大分部 (年报分部资料) ──
    (code, '2025', 'by_segment', '在线业务', 4047.0, 54.9),
    (code, '2025', 'by_segment', '版权运营及其他', 3319.1, 45.1),
    (code, '2024', 'by_segment', '在线业务', 4030.6, 49.6),
    (code, '2024', 'by_segment', '版权运营及其他', 4090.5, 50.4),
    (code, '2023', 'by_segment', '在线业务', 3948.1, 56.3),
    (code, '2023', 'by_segment', '版权运营及其他', 3063.6, 43.7),

    # ── by_product: 年报原始口径五项拆分 ──
    (code, '2025', 'by_product', '自有平台产品', 3562.3, 48.4),
    (code, '2025', 'by_product', '版权运营', 3191.6, 43.3),
    (code, '2025', 'by_product', '第三方平台', 294.2, 3.9),
    (code, '2025', 'by_product', '腾讯产品渠道', 190.6, 2.6),
    (code, '2025', 'by_product', '其他(纸质图书等)', 127.5, 1.8),

    (code, '2024', 'by_product', '版权运营', 3991.2, 49.1),
    (code, '2024', 'by_product', '自有平台产品', 3531.0, 43.5),
    (code, '2024', 'by_product', '第三方平台', 254.2, 3.1),
    (code, '2024', 'by_product', '腾讯产品渠道', 245.3, 3.0),
    (code, '2024', 'by_product', '其他(纸质图书等)', 99.3, 1.3),

    (code, '2023', 'by_product', '自有平台产品', 3413.9, 48.7),
    (code, '2023', 'by_product', '版权运营', 2973.8, 42.4),
    (code, '2023', 'by_product', '腾讯产品渠道', 341.7, 4.9),
    (code, '2023', 'by_product', '第三方平台', 192.6, 2.7),
    (code, '2023', 'by_product', '其他(纸质图书等)', 89.8, 1.3),
]

conn.executemany(
    "INSERT OR REPLACE INTO revenue_structure "
    "(code, year, dim_type, dim_name, amount, pct) VALUES (?,?,?,?,?,?)",
    data)
conn.commit()

rows = conn.execute(
    "SELECT year, dim_type, COUNT(*), ROUND(SUM(pct),1) "
    "FROM revenue_structure WHERE code=? GROUP BY year, dim_type ORDER BY year DESC",
    (code,)).fetchall()
for r in rows:
    print(f"  {r[0]} {r[1]}: {r[2]} rows, pct_sum={r[3]}")
conn.close()
print("Done.")
