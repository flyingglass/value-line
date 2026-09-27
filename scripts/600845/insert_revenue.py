# -*- coding: utf-8 -*-
"""Insert 宝信软件 (600845) revenue structure

数据源(全部为一手年报/中报原文):
  - 2025 年度 : 2025年年度报告 第11页「主营业务分产品情况」
  - 2026H1   : 2026年半年度报告 第117-118页「营业收入、营业成本的分解信息」

PDF 原文(单位: 元):
  2025 年报 分产品:
    软件开发及工程服务 7,163,930,796.80 / 服务外包 3,765,353,956.54 / 系统集成 28,161,780.41
  2026 中报 按商品类型:
    软件开发及工程服务 3,817,221,362.64 / 服务外包 1,775,984,099.04 / 系统集成 29,797,545.93
  2026 中报 按经营地区:
    境内 5,426,799,173.25 / 境外 196,203,834.36

口径说明(修改前必读):
  1. 2026H1 为半年口径, 与年度数据不可比; 以 year='2026H1' 单独存放,
     不污染年度口径, 也不会被报告误当全年使用。
  2. 2026 中报分解表的"合计 5,623,003,007.61"为**主营业务**口径
     (不含其他业务收入 8,878,853.50), 故 pct 以 5623.00 百万为分母。
  3. 宝信 2025 年报**未披露分地区/分销售模式**, 因此 2025 年只有 by_product 一个维度;
     2026H1 才有 by_region。此为披露限制, 不做推算填补。
  4. 三类业务的官方释义(2025年报 p3「释义」):
       软件开发及工程服务 = 计算机、自动化、网络通讯系统及软硬件产品的研究/设计/开发/
                            制造/集成安装; 冶金、建筑工程设计及工程总承包
       服务外包           = 信息系统运行维护、云计算运营服务、IDC运营服务
       系统集成           = 硬件销售及相关的集成类服务

单位: 百万元 (1e6)
"""
import sqlite3

code = "600845"
conn = sqlite3.connect(f"data/{code}.db")

conn.execute("DELETE FROM revenue_structure WHERE code=?", (code,))

data = [
    # ══════════ 2025 年度 (年报口径, 仅分产品) ══════════
    (code, '2025', 'by_product', '软件开发及工程服务', 7163.93, 65.38),
    (code, '2025', 'by_product', '服务外包', 3765.35, 34.36),
    (code, '2025', 'by_product', '系统集成', 28.16, 0.26),

    # ══════════ 2026H1 (半年口径, 来源: 2026年中报 p117-118) ══════════
    (code, '2026H1', 'by_product', '软件开发及工程服务', 3817.22, 67.89),
    (code, '2026H1', 'by_product', '服务外包', 1775.98, 31.58),
    (code, '2026H1', 'by_product', '系统集成', 29.80, 0.53),
    (code, '2026H1', 'by_region', '境内', 5426.80, 96.51),
    (code, '2026H1', 'by_region', '境外', 196.20, 3.49),
]

conn.executemany(
    "INSERT OR REPLACE INTO revenue_structure (code, year, dim_type, dim_name, amount, pct) VALUES (?,?,?,?,?,?)",
    data
)
conn.commit()

for yr in ['2025', '2026H1']:
    print(f"\n----- {yr} -----")
    for dim in ['by_product', 'by_region']:
        rows = conn.execute(
            "SELECT dim_name, amount, pct FROM revenue_structure WHERE code=? AND year=? AND dim_type=? ORDER BY amount DESC",
            (code, yr, dim)).fetchall()
        if not rows:
            continue
        tot = sum(r[2] for r in rows)
        flag = "OK" if abs(100 - tot) < 0.5 else "!! pct!=100"
        print(f"  {dim}: {len(rows)} rows, pct_sum={tot:.2f}%  [{flag}]")
        for r in rows:
            print(f"    {r[0]}: {r[1]:.2f}M ({r[2]}%)")

print("\n----- 勾稽校验 (2026H1, 应均为 5623.00M) -----")
for dim in ['by_product', 'by_region']:
    s = conn.execute(
        "SELECT SUM(amount) FROM revenue_structure WHERE code=? AND year='2026H1' AND dim_type=?",
        (code, dim)).fetchone()[0]
    print(f"  {dim} 合计 = {s:.2f}M ({s/100:.2f}亿)")

print("\n----- 勾稽校验 (2025, 应均为 10957.44M = 109.57亿) -----")
s = conn.execute(
    "SELECT SUM(amount) FROM revenue_structure WHERE code=? AND year='2025' AND dim_type='by_product'",
    (code,)).fetchone()[0]
print(f"  by_product 合计 = {s:.2f}M ({s/100:.2f}亿)")

conn.close()
print(f"\nDone. {len(data)} rows inserted.")
