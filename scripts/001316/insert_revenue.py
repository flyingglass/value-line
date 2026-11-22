# -*- coding: utf-8 -*-
"""润贝航科 001316 营收结构入库 — 数据源: 2025年报 p21「营业收入构成」

口径（不可违背）:
  - 原始单位为人民币元，入库 amount 统一为百万元（/1e6）；pct 直接取年报原文。
  - 2025 年报同一张表并列 2025 / 2024 两期，故一并入库两年。
  - by_product / by_region / by_channel（分销售模式）三个维度各自合计 = 当年
    营业收入合计，互不叠加；「分行业」仅有「航材分销行业」100% 一项，不入库。
  - 来源: data/pdfs/润贝航科/001316_润贝航科_2025_年报.pdf p21
    「（1）营业收入构成」表，营业收入合计 2025 = 1,216,791,291.50 元、
    2024 = 909,361,866.90 元。
"""
import os
import sqlite3

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB = os.path.join(BASE, "data", "db", "001316.db")
CODE = "001316"

# (年度, 维度, 名称, 金额[元], 年报占比[%])
DATA = [
    # ── 2025 分产品 ──
    ("2025", "by_product", "分销产品", 1125468662.69, 92.49),
    ("2025", "by_product", "自研产品",   91322628.81,  7.51),
    # ── 2025 分地区 ──
    ("2025", "by_region", "内销", 1132762093.58, 93.09),
    ("2025", "by_region", "外销",   84029197.92,  6.91),
    # ── 2025 分销售模式 ──
    ("2025", "by_channel", "非寄售", 979704821.07, 80.52),
    ("2025", "by_channel", "寄售",   237086470.43, 19.48),
    # ── 2024 分产品 ──
    ("2024", "by_product", "分销产品", 841190060.28, 92.50),
    ("2024", "by_product", "自研产品",   68171806.62,  7.50),
    # ── 2024 分地区 ──
    ("2024", "by_region", "内销", 833875853.05, 91.70),
    ("2024", "by_region", "外销",   75486013.85,  8.30),
    # ── 2024 分销售模式 ──
    ("2024", "by_channel", "非寄售", 663098332.03, 72.92),
    ("2024", "by_channel", "寄售",   246263534.87, 27.08),
]

TOTAL_FROM_ANNUAL_REPORT = {
    "2025": 1216791291.50,
    "2024":  909361866.90,
}


def main():
    conn = sqlite3.connect(DB)
    conn.execute("DELETE FROM revenue_structure WHERE code=?", (CODE,))
    rows = [(CODE, yr, dim, name, round(amount / 1e6, 4), pct)
            for yr, dim, name, amount, pct in DATA]
    conn.executemany(
        "INSERT OR REPLACE INTO revenue_structure "
        "(code, year, dim_type, dim_name, amount, pct) VALUES (?,?,?,?,?,?)",
        rows)
    conn.commit()

    for year, total_yuan in TOTAL_FROM_ANNUAL_REPORT.items():
        print(f"\n{year} 年报营业收入合计 {total_yuan/1e6:.4f} 百万元")
        for dim in ("by_product", "by_region", "by_channel"):
            got = conn.execute(
                "SELECT dim_name, amount, pct FROM revenue_structure "
                "WHERE code=? AND year=? AND dim_type=? ORDER BY amount DESC",
                (CODE, year, dim)).fetchall()
            amt_sum = sum(r[1] for r in got)
            pct_sum = sum(r[2] for r in got)
            diff = amt_sum - total_yuan / 1e6
            print(f"  {dim}: {len(got)}项, 金额合计={amt_sum:.4f}百万, "
                  f"与年报差={diff:+.4f}百万, pct合计={pct_sum:.2f}%")
            for name, amt, pct in got:
                print(f"    {name}: {amt:.4f} 百万元 ({pct:.2f}%)")
    conn.close()
    print(f"\nDone. {len(rows)} rows inserted.")


if __name__ == "__main__":
    main()
