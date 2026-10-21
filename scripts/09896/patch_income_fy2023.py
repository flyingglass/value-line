# -*- coding: utf-8 -*-
"""名创优品 09896 — 补齐 FY2023（截至2023-06-30，归一化后标为2023-12-31）缺失科目。

(1) 利润表：TDX 对 FY2023 只提供 12 个科目，缺「毛利 / 销售成本」，毛利率序列在该年断点。
    出处：data/pdfs/名创优品/09896_名创优品_2023_年报.pdf（FY ended 30 June 2023）
      合并损益表：Revenue 11,473,208 千元 / Cost of sales (7,030,156) 千元 / Gross profit 4,443,052 千元
    （与库内 2023-12-31 营业额 11,473,208 千元一致，可交叉验证。）

(2) 资产负债表：TDX 该年科目名写作「应付账款」(账)，而 engine 的 CURRENT POSITION 读「应付帐款」(帐)，
    导致报告中 2023 年应付账款显示 0、 residuals 全部挤进「其他流动负债」。
    此处补一行同名异写「应付帐款」= TDX 的「应付账款」金额，仅改标签不改数值。
"""
import os
import sqlite3

CODE = "09896"
RD = "2023-12-31"
BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB = os.path.join(BASE, "data", "db", f"{CODE}.db")

ITEMS = [
    ("销售成本", -7030156000.0),
    ("毛利", 4443052000.0),
]

BALANCE_ALIAS = ("应付帐款", "应付账款")


def main():
    conn = sqlite3.connect(DB)
    rev = conn.execute("SELECT amount FROM income WHERE report_date=? AND item_name='营业额'",
                       (RD,)).fetchone()
    assert rev and abs(rev[0] - 11473208000.0) < 1e6, f"营业额校验失败: {rev}"
    for name, amount in ITEMS:
        conn.execute("DELETE FROM income WHERE report_date=? AND item_name=?", (RD, name))
        conn.execute("INSERT INTO income (report_date, item_name, amount) VALUES (?,?,?)",
                     (RD, name, amount))

    alias, src = BALANCE_ALIAS
    row = conn.execute("SELECT amount FROM balance WHERE report_date=? AND item_name=?",
                       (RD, src)).fetchone()
    if row and not conn.execute("SELECT 1 FROM balance WHERE report_date=? AND item_name=?",
                                (RD, alias)).fetchone():
        conn.execute("INSERT INTO balance (report_date, item_name, amount) VALUES (?,?,?)",
                     (RD, alias, row[0]))
        print(f"  FY2023 补标签: 应付帐款 = 应付账款 = {row[0]/1e8:.2f}亿")

    conn.commit()
    gm = conn.execute("SELECT amount FROM income WHERE report_date=? AND item_name='毛利'",
                      (RD,)).fetchone()[0]
    print(f"  FY2023 补齐: 销售成本 -{abs(ITEMS[0][1])/1e8:.2f}亿, 毛利 {gm/1e8:.2f}亿, "
          f"毛利率 {gm/rev[0]*100:.1f}%")
    conn.close()


if __name__ == "__main__":
    main()
