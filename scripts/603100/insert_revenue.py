# -*- coding: utf-8 -*-
"""川仪股份(603100) 营收结构数据 — 从年报PDF原文提取
来源:
  2025年报 P25「(1) 主营业务分行业、分产品、分地区、分销售模式情况」
  2024年报 P25-26「(1) 主营业务分行业、分产品、分地区、分销售模式情况」

金额单位: 源数据为万元, 入库统一换算为百万元 (÷100, 与全库 revenue_structure.amount 约定一致,
          engine 交叉校验按 1e6 元换算)
百分比: 分项金额 / 主营业务收入合计
  - 2025 合计 680,494.71 万元 (= 全年营收 680,494.71 万元, 100% 主营)
  - 2024 合计 759,175.05 万元 (= 全年营收 759,175.05 万元, 100% 主营)

口径说明 (重要):
1. 分行业/分销售模式两维均只有单一取值 (仪器仪表行业 100% / 直销 100%), 无信息量, 不入库。
2. 2025年报对 2024 年比较数据做了追溯调整: 原「进出口业务」并入「其他」列示;
   部分电子器件产品升级为整机设备制造, 由「电子器件」分类调整至「工业自动化仪表及装置」。
   本脚本 2024 年 by_product 采用 **2024年报原始口径** (含「进出口业务」单独列示),
   故 2024 与 2025 的产品口径不完全可比, 引用时须注明。
3. 分地区口径 2024/2025 未调整 (南方/北方/出口境外), 两年可比。
"""
import sqlite3, os

_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
conn = sqlite3.connect(os.path.join(_root, "data/603100.db"))

_RAW = [  # (code, year, dim_type, dim_name, 金额万元, pct)
    # ========== by_product ==========
    # 2025 (来源: 2025年报 P25 主营业务分产品情况)
    ("603100", "2025", "by_product", "工业自动化仪表及装置", 598834.49, 88.00),
    ("603100", "2025", "by_product", "复合材料",             66893.60,  9.83),
    ("603100", "2025", "by_product", "电子器件",             10045.26,  1.48),
    ("603100", "2025", "by_product", "其他",                  4721.36,  0.69),
    # 2024 (来源: 2024年报 P25-26, 原始口径未追溯调整)
    ("603100", "2024", "by_product", "工业自动化仪表及装置", 674965.50, 88.91),
    ("603100", "2024", "by_product", "复合材料",             63972.15,  8.43),
    ("603100", "2024", "by_product", "电子器件",             14765.07,  1.94),
    ("603100", "2024", "by_product", "其他",                  3964.87,  0.52),
    ("603100", "2024", "by_product", "进出口业务",            1507.46,  0.20),
    # ========== by_region ==========
    # 2025 (来源: 2025年报 P25 主营业务分地区情况)
    ("603100", "2025", "by_region", "南方地区", 465323.69, 68.38),
    ("603100", "2025", "by_region", "北方地区", 198993.87, 29.24),
    ("603100", "2025", "by_region", "出口境外",  16177.15,  2.38),
    # 2024 (来源: 2024年报 P26 主营业务分地区情况)
    ("603100", "2024", "by_region", "南方地区", 539296.12, 71.04),
    ("603100", "2024", "by_region", "北方地区", 203897.55, 26.86),
    ("603100", "2024", "by_region", "出口境外",  15981.38,  2.11),
]

data = [(c, y, d, n, round(amt / 100.0, 2), p) for (c, y, d, n, amt, p) in _RAW]

conn.executemany(
    "INSERT OR REPLACE INTO revenue_structure (code, year, dim_type, dim_name, amount, pct) VALUES (?,?,?,?,?,?)",
    data,
)
conn.commit()

# 自洽检验: 各维度分项加总应 = 当年主营业务收入
for yr in ("2024", "2025"):
    for dim in ("by_product", "by_region"):
        n, amt_sum, pct_sum = conn.execute(
            "SELECT COUNT(*), ROUND(SUM(amount),2), ROUND(SUM(pct),2) FROM revenue_structure "
            "WHERE code='603100' AND year=? AND dim_type=?", (yr, dim)).fetchone()
        print(f"  {yr} {dim}: {n} rows, amount_sum={amt_sum} 百万元, pct_sum={pct_sum}%")

total = conn.execute("SELECT COUNT(*) FROM revenue_structure WHERE code='603100'").fetchone()[0]
print(f"\n  总计: {total} 条记录")
conn.close()
print("Done.")
