# -*- coding: utf-8 -*-
"""山东赫达(002810) 营收结构 — 数据源: akshare 东财「主营构成」(stock_zygc_em)

口径:
  - 仅取年度报告期 (12-31), 半年报口径不入库
  - amount 单位: 百万元 (接口原始单位元 / 1e6)
  - pct 单位: 百分数 (接口为小数 × 100)
  - dim_type: 按产品→by_product / 按行业→by_industry / 按地区→by_region
"""
import os
import sqlite3

os.environ["NO_PROXY"] = "*"
os.environ["no_proxy"] = "*"

import akshare as ak

CODE = "002810"
SYMBOL = "SZ002810"
YEARS = ["2025", "2024", "2023", "2022", "2021", "2020", "2019", "2018", "2017", "2016"]
DIM_MAP = {
    "按行业分类": "by_industry",
    "按产品分类": "by_product",
    "按地区分类": "by_region",
}

def main():
    df = ak.stock_zygc_em(symbol=SYMBOL)
    rows = []
    for _, r in df.iterrows():
        period = str(r["报告日期"])[:10]
        year = period[:4]
        if year not in YEARS or not period.endswith("12-31"):
            continue
        dim = DIM_MAP.get(str(r["分类类型"]))
        if not dim:
            continue
        amount = float(r["主营收入"]) / 1e6 if r["主营收入"] == r["主营收入"] else 0.0
        pct = float(r["收入比例"]) * 100 if r["收入比例"] == r["收入比例"] else 0.0
        rows.append((CODE, year, dim, str(r["主营构成"]).strip(),
                     round(amount, 2), round(pct, 2)))

    conn = sqlite3.connect(os.path.join("data", "db", f"{CODE}.db"))
    conn.execute("""
        CREATE TABLE IF NOT EXISTS revenue_structure (
            code TEXT, year TEXT, dim_type TEXT, dim_name TEXT,
            amount REAL, pct REAL,
            PRIMARY KEY (code, year, dim_type, dim_name))
    """)
    conn.executemany(
        "INSERT OR REPLACE INTO revenue_structure VALUES (?,?,?,?,?,?)", rows)
    conn.commit()
    for dim in ("by_product", "by_industry", "by_region"):
        n = conn.execute(
            "SELECT COUNT(*) FROM revenue_structure WHERE code=? AND dim_type=?",
            (CODE, dim)).fetchone()[0]
        print(f"  {dim}: {n} 条")
    conn.close()
    print(f"写入完成: {len(rows)} 条 ({min(YEARS, default='-')}~{max(YEARS, default='-')} 年报口径)")

if __name__ == "__main__":
    main()
