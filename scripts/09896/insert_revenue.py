# -*- coding: utf-8 -*-
"""名创优品 09896 — 营收结构入库（来源：2025年度报告 综合财务报表附注）

数据出处（data/pdfs/名创优品/09896_名创优品_2025_年报.pdf）：
  - 按地区收入   → 附注 4(iii) Geographic information, 第159页
      中国内地 12,577,451 / 亚洲(中国除外) 2,736,150 / 北美洲 3,342,918
      拉丁美洲 1,560,169 / 欧洲 703,771 / 其他 523,368  (2025, 人民币千元)
  - 分部收入     → 附注 4(i) Segment results, 第156页 External revenue
      名创优品品牌-中国内地 10,896,147 / 名创优品品牌-海外 8,628,754
      TOP TOY品牌 1,915,618 / 未分配 3,308                (2025, 人民币千元)
  - 按渠道收入   → 附注 5(i) Disaggregation of revenue, 第160-161页
      向加盟商销售产品 8,853,156 / 直营店零售 5,410,291 / 向线下代理商销售 3,887,954
      线上销售 1,412,624 / 授权费及服务费 1,061,883 / 其他(装修材料等) 708,731
      其他销售渠道 109,188                              (2025, 人民币千元)
  2024 年同表对照列一并入库（金额同为人民币千元）。

revenue_structure.amount 单位为百万元。
"""
import os
import sqlite3

CODE = "09896"
BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB = os.path.join(BASE, "data", "db", f"{CODE}.db")

# year → dim_type → [(名称, 千元)]
RAW = {
    "2025": {
        "by_region": [
            ("中国内地", 12577451),
            ("北美洲", 3342918),
            ("亚洲（中国除外）", 2736150),
            ("拉丁美洲", 1560169),
            ("欧洲", 703771),
            ("其他地区", 523368),
        ],
        "by_segment": [
            ("名创优品品牌-中国内地", 10896147),
            ("名创优品品牌-海外", 8628754),
            ("TOP TOY 品牌", 1915618),
            ("未分配", 3308),
        ],
        "by_channel": [
            ("向加盟商销售产品", 8853156),
            ("直营店零售", 5410291),
            ("向线下代理商销售", 3887954),
            ("线上销售", 1412624),
            ("授权费及服务费", 1061883),
            ("其他（装修材料等）", 708731),
            ("其他销售渠道", 109188),
        ],
    },
    "2024": {
        "by_region": [
            ("中国内地", 10312116),
            ("亚洲（中国除外）", 2541817),
            ("北美洲", 1985051),
            ("拉丁美洲", 1445691),
            ("欧洲", 414493),
            ("其他地区", 294857),
        ],
        "by_segment": [
            ("名创优品品牌-中国内地", 9328231),
            ("名创优品品牌-海外", 6674334),
            ("TOP TOY 品牌", 983525),
            ("未分配", 7935),
        ],
        "by_channel": [
            ("向加盟商销售产品", 7923836),
            ("向线下代理商销售", 3369238),
            ("直营店零售", 3158895),
            ("线上销售", 941055),
            ("授权费及服务费", 869182),
            ("其他（装修材料等）", 683629),
            ("其他销售渠道", 48190),
        ],
    },
}


def main():
    conn = sqlite3.connect(DB)
    conn.execute("CREATE TABLE IF NOT EXISTS revenue_structure "
                 "(code TEXT, year TEXT, dim_type TEXT, dim_name TEXT, amount REAL, pct REAL)")
    conn.execute("DELETE FROM revenue_structure WHERE code=?", (CODE,))

    rows = []
    for year, dims in RAW.items():
        for dim, items in dims.items():
            total = sum(v for _, v in items)
            for name, kv in items:
                rows.append((CODE, year, dim, name, round(kv / 1e3, 1),
                             round(kv / total * 100, 2)))

    conn.executemany(
        "INSERT OR REPLACE INTO revenue_structure "
        "(code, year, dim_type, dim_name, amount, pct) VALUES (?,?,?,?,?,?)", rows)
    conn.commit()

    for year in sorted(RAW, reverse=True):
        for dim in RAW[year]:
            got = conn.execute(
                "SELECT COUNT(*), ROUND(SUM(amount),1), ROUND(SUM(pct),2) FROM revenue_structure "
                "WHERE code=? AND year=? AND dim_type=?", (CODE, year, dim)).fetchone()
            print(f"  {year} {dim:11s}: {got[0]} 行, 金额合计={got[1]:,.1f} 百万, pct合计={got[2]}%")
    print(f"\nDone. {len(rows)} rows.")
    conn.close()


if __name__ == "__main__":
    main()
