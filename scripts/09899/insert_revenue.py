# -*- coding: utf-8 -*-
"""网易云音乐(09899) 营收结构数据 — 来源: 年报PDF原文学会(按商品/服务种类)"""
import sqlite3

conn = sqlite3.connect("data/09899.db")

# 金额单位: 亿元 (年报原文 / 10000万)
# 数据来源: 各年年报PDF 附注5 — 客戶合約收入分類
data = [
    # ========== 2025 ========== 总营收 77.59亿 (来源: 2025年报 附注5, P175)
    ("09899", "2025", "by_service", "在线音乐服务", 59.94, 77.26),
    ("09899", "2025", "by_service", "社交娱乐服务及其他", 17.65, 22.74),

    # ========== 2024 ========== 总营收 79.50亿 (来源: 2025年报 附注5同比列)
    ("09899", "2024", "by_service", "在线音乐服务", 53.55, 67.35),
    ("09899", "2024", "by_service", "社交娱乐服务及其他", 25.96, 32.65),

    # ========== 2023 ========== 总营收 78.7亿 (来源: 2023年报)
    ("09899", "2023", "by_service", "在线音乐服务", 43.51, 55.28),
    ("09899", "2023", "by_service", "社交娱乐服务及其他", 35.16, 44.72),

    # ========== 2022 ========== 总营收 89.9亿 (来源: 2022年报/IR公告)
    ("09899", "2022", "by_service", "在线音乐服务", 36.99, 41.16),
    ("09899", "2022", "by_service", "社交娱乐服务及其他", 52.93, 58.84),

    # ========== 2021 ========== 总营收 69.98亿 (来源: 2021年报/IR公告)
    ("09899", "2021", "by_service", "在线音乐服务", 33.0, 47.16),
    ("09899", "2021", "by_service", "社交娱乐服务及其他", 36.98, 52.84),
]

conn.executemany(
    "INSERT OR REPLACE INTO revenue_structure (code, year, dim_type, dim_name, amount, pct) VALUES (?,?,?,?,?,?)",
    data,
)
conn.commit()

rows = conn.execute(
    "SELECT dim_type, year, COUNT(*), ROUND(SUM(pct),1) FROM revenue_structure WHERE code='09899' GROUP BY dim_type, year ORDER BY year, dim_type"
).fetchall()
for r in rows:
    print(f"  {r[1]} {r[0]}: {r[2]} rows, pct_sum={r[3]}%")

total = conn.execute("SELECT COUNT(*) FROM revenue_structure WHERE code='09899'").fetchone()[0]
print(f"\n  总计: {total} 条记录")
conn.close()
print("Done.")
