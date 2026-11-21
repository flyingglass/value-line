# -*- coding: utf-8 -*-
"""聚水潭 06687 营收结构入库 — 数据源: 2025年报 p10 / 招股章程 p8、p203、p317 / 2025年报 p11

口径（不可违背）:
  - 只取各报告的「本期」年度列 (12-31)，半年报口径不入库；
    招股章程同一张表同时列 2022/2023/2024 年度与 2024H1/2025H1，仅取年度三列。
  - 原始单位为人民币千元，入库 amount 统一为百万元（/1000）；pct 由金额自算。
  - by_product 为顶层四类（合计 = 总收入）。ERP / 协同产品是 SaaS 内部的二级
    拆分，不与顶层并列入库，否则同一年收入会被计两次；该拆分写入评论并标注出处。
  - by_region: 2025年报「管理層討論與分析」只给东南亚收入（2025 约 21.9 百万元、
    2024 约 10.0 百万元），中国 = 总收入 - 东南亚，属减法推算（🟡）；
    依据 2026 中期业绩公告 p8「本集團幾乎所有業績均來自中國」。
  - 年份来源: 2022/2023/2024 → 招股章程；2025 → 2025年报。
"""
import os
import sqlite3

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB = os.path.join(BASE, "data", "db", "06687.db")
CODE = "06687"

# (年度, 维度, [(名称, 人民币千元), ...]) —— 顶层四类，合计必须等于当年总收入
# 2022/2023/2024: 招股章程 p317「收入」表; 2025: 2025年报 p10「收入明細」表
PRODUCT = {
    "2022": [("SaaS", 497935), ("出售配套设备", 17697), ("营销服务费", 6998), ("其他", 448)],
    "2023": [("SaaS", 669874), ("出售配套设备", 17813), ("营销服务费", 8746), ("其他", 758)],
    "2024": [("SaaS", 877530), ("出售配套设备", 18002), ("营销服务费", 13596), ("其他", 622)],
    "2025": [("SaaS", 1104817), ("出售配套设备", 16416), ("营销服务费", 19703), ("其他", 1534)],
}

# 年报 p11 只披露东南亚收入，中国为差额推算；单位人民币千元
REGION = {
    "2024": [("中国", 909750 - 10000), ("东南亚", 10000)],
    "2025": [("中国", 1142470 - 21900), ("东南亚", 21900)],
}

# AKShare income.营业额 (元)，用于写入后自检
TOTAL_FROM_AKSHARE = {
    "2022": 523078000.0,
    "2023": 697191000.0,
    "2024": 909750000.0,
    "2025": 1142470000.0,
}


def rows_from(groups, dim):
    out = []
    for year, items in groups.items():
        total = sum(v for _, v in items)
        for name, amount_k in items:
            out.append((
                CODE, year, dim, name,
                round(amount_k / 1000.0, 4),                 # 千元 → 百万元
                round(amount_k / total * 100, 2),            # pct 由金额自算
            ))
        # 硬校验: 各维度合计必须等于 AKShare 营业额
        ak = TOTAL_FROM_AKSHARE[year] / 1e6
        assert abs(total / 1000.0 - ak) < 0.001, (
            f"{year} {dim} 合计 {total/1000.0:.4f} 百万 != AKShare {ak:.4f} 百万")
    return out


def main():
    rows = rows_from(PRODUCT, "by_product") + rows_from(REGION, "by_region")
    conn = sqlite3.connect(DB)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS revenue_structure (
            code TEXT, year TEXT, dim_type TEXT, dim_name TEXT,
            amount REAL, pct REAL,
            PRIMARY KEY (code, year, dim_type, dim_name))
    """)
    conn.execute("DELETE FROM revenue_structure WHERE code=?", (CODE,))
    conn.executemany(
        "INSERT OR REPLACE INTO revenue_structure VALUES (?,?,?,?,?,?)", rows)
    conn.commit()

    for dim in ("by_product", "by_region"):
        n = conn.execute(
            "SELECT COUNT(*) FROM revenue_structure WHERE code=? AND dim_type=?",
            (CODE, dim)).fetchone()[0]
        print(f"  {dim}: {n} 条")
    print("  年度合计自检:")
    for year in sorted(PRODUCT):
        s = conn.execute(
            "SELECT SUM(amount), SUM(pct) FROM revenue_structure "
            "WHERE code=? AND year=? AND dim_type='by_product'",
            (CODE, year)).fetchone()
        print(f"    {year}: {s[0]:.2f} 百万元 / pct {s[1]:.2f}%")
    conn.close()
    print(f"写入完成: {len(rows)} 条 (2022~2025 年报口径)")


if __name__ == "__main__":
    main()
