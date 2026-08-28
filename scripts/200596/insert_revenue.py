# -*- coding: utf-8 -*-
"""
古井贡B 200596 营收结构 — 来源: 2025年年度报告 P14「营业收入构成」

B股与A股(000596)为同一法律主体, 共用同一份年报, 故数据与 A 股完全一致。
原始金额单位: 元 → 本项目统一存 百万元(M)
2025 营业收入合计 18,831,982,591.24 元 = 18,831.98M

注: fetcher.copy_financials_from() 会从 000596.db 复制本表, 本脚本用于
    独立重建场景 (如清空 DB 后重跑) 保持自洽。
"""
import sqlite3

code = "200596"
conn = sqlite3.connect(f"data/{code}.db")

conn.execute("DELETE FROM revenue_structure WHERE code=?", (code,))

data = [
    # by_product (2025) — 分产品
    (code, '2025', 'by_product', '白酒业务', 18539.72, 98.45),
    (code, '2025', 'by_product', '酒店业务', 88.64, 0.47),
    (code, '2025', 'by_product', '其他', 203.62, 1.08),
    # by_region (2025) — 分地区
    (code, '2025', 'by_region', '华中', 16647.87, 88.40),
    (code, '2025', 'by_region', '华南', 1113.25, 5.91),
    (code, '2025', 'by_region', '华北', 1058.11, 5.62),
    (code, '2025', 'by_region', '国际', 12.75, 0.07),
    # by_channel (2025) — 分销售模式
    (code, '2025', 'by_channel', '线下', 17823.76, 94.65),
    (code, '2025', 'by_channel', '线上', 1008.23, 5.35),
]

conn.executemany(
    "INSERT OR REPLACE INTO revenue_structure (code, year, dim_type, dim_name, amount, pct) VALUES (?,?,?,?,?,?)",
    data
)
conn.commit()

ok = True
for dim in ['by_product', 'by_region', 'by_channel']:
    rows = conn.execute(
        "SELECT dim_name, amount, pct FROM revenue_structure WHERE code=? AND year='2025' AND dim_type=?",
        (code, dim)
    ).fetchall()
    tot = sum(r[2] for r in rows)
    if abs(tot - 100) >= 0.05:
        ok = False
    print(f"  {dim}: {len(rows)} rows, pct_sum={tot:.2f}%")

rows = conn.execute(
    "SELECT SUM(amount) FROM revenue_structure WHERE code=? AND year='2025' AND dim_type='by_product'", (code,)
).fetchone()
print(f"\n  分产品金额合计: {rows[0]:.2f}M  (年报营业收入合计 18,831.98M)")

conn.close()
print(f"\nDone. {len(data)} rows inserted. 勾稽{'通过' if ok else '失败'}.")
