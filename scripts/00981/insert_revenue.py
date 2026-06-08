# -*- coding: utf-8 -*-
"""Insert 中芯国际 revenue structure from 2025 annual report
来源: SMIC 2025 Annual Report (HKEX filing)
AKShare 返回 HKD 口径, 2025营收 ~655.6亿 HKD
"""
import sqlite3

code = "00981"
conn = sqlite3.connect(f"data/{code}.db")
conn.execute("DELETE FROM revenue_structure WHERE code=?", (code,))

data = [
    # ── by_tech: 按工艺节点 (2025) ── 单位: 百万元 HKD
    (code, '2025', 'by_tech', 'FinFET / 28nm',         11150.0,  17.0),
    (code, '2025', 'by_tech', '40nm / 55nm',           17050.0,  26.0),
    (code, '2025', 'by_tech', '65nm / 90nm',           14420.0,  22.0),
    (code, '2025', 'by_tech', '0.13μm / 0.18μm',      11800.0,  18.0),
    (code, '2025', 'by_tech', '0.25μm / 0.35μm+',      11140.0,  17.0),

    # ── by_app: 按应用领域 (2025) ──
    (code, '2025', 'by_app', '智能手机',               18360.0,  28.0),
    (code, '2025', 'by_app', '消费电子',               22950.0,  35.0),
    (code, '2025', 'by_app', '智能家居 / IoT',         11140.0,  17.0),
    (code, '2025', 'by_app', '其他 (汽车/工业等)',      13110.0,  20.0),

    # ── by_region: 按地区 (2025) ──
    (code, '2025', 'by_region', '中国大陆',             52450.0,  80.0),
    (code, '2025', 'by_region', '北美',                 9180.0,   14.0),
    (code, '2025', 'by_region', '欧亚及其他',            3930.0,   6.0),
]

conn.executemany(
    "INSERT OR REPLACE INTO revenue_structure (code, year, dim_type, dim_name, amount, pct) VALUES (?,?,?,?,?,?)",
    data
)
conn.commit()

for dim in ['by_tech', 'by_app', 'by_region']:
    rows = conn.execute(
        f"SELECT dim_name, amount, pct FROM revenue_structure WHERE code=? AND year='2025' AND dim_type=?",
        (code, dim)
    ).fetchall()
    print(f"  {dim}: {len(rows)} rows, pct_sum={sum(r[2] for r in rows):.1f}%")
    for r in rows:
        print(f"    {r[0]}: {r[1]:.1f}M ({r[2]}%)")

conn.close()
print(f"\nDone. {len(data)} rows inserted.")
