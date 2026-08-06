# -*- coding: utf-8 -*-
"""建滔集团 00148 — 营收结构 (2025年年报)
来源: 同花顺F10 经营分析 + 东方财富公告摘要
金额单位: 百万HKD (百万元港币)
"""
import sqlite3

code = "00148"
conn = sqlite3.connect(f"data/{code}.db")
conn.execute("DELETE FROM revenue_structure WHERE code=?", (code,))

data = [
    # ── by_product: 按业务分部 (2025全年) ──
    # 总营收 45,375百万HKD
    (code, '2025', 'by_product', '覆铜面板',     16911, 37.27),
    (code, '2025', 'by_product', '印刷线路板',    13314, 29.34),
    (code, '2025', 'by_product', '化工产品',      12655, 27.89),
    (code, '2025', 'by_product', '物业',           1526,  3.36),
    (code, '2025', 'by_product', '投资及其他',      969,  2.14),
]

conn.executemany(
    "INSERT OR REPLACE INTO revenue_structure (code, year, dim_type, dim_name, amount, pct) VALUES (?,?,?,?,?,?)",
    data
)
conn.commit()

# 验证
for dim in ['by_product']:
    rows = conn.execute(
        f"SELECT dim_name, amount, pct FROM revenue_structure WHERE code=? AND year='2025' AND dim_type=?",
        (code, dim)).fetchall()
    pct_sum = sum(r[2] for r in rows)
    amt_sum = sum(r[1] for r in rows)
    print(f"\n{dim}: {len(rows)} rows, pct_sum={pct_sum:.2f}%, amt_sum={amt_sum:.1f}M")
    for name, amt, pct in rows:
        print(f"  {name}: {amt/100:.1f}亿 HKD ({pct:.1f}%)")

conn.close()
print(f"\nDone. {len(data)} rows inserted.")
