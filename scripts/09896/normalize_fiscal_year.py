# -*- coding: utf-8 -*-
"""名创优品 09896 — 财年口径归一化。

背景（披露易年报标题为证）：
  2023-10-19 《2023年度報告》            → 财年截至 2023-06-30（6月30日结束）
  2024-04-16 《2023年度報告(截至2023年12月31日止六個月)》→ 过渡期 2023H2（6个月）
  2025-04-24 《2024年度報告》            → 自然年 2024-01-01~2024-12-31
  2026-04-24 《2025年度報告》            → 自然年 2025

即公司把财年结算日由 6月30日 改为 12月31日，中间夹一个 6 个月过渡期。

归一化规则（让 VL 引擎的 fiscal_yr_end=12-31 口径可用）：
  1. 2019-06-30 ~ 2023-06-30 的五份年报（6月结束财年）按"财年结束年份"
     改标为当年 12-31，即 FY2019→2019-12-31 … FY2023→2023-12-31；
  2. 2023H2 过渡期（原 2023-12-31 行）与 2019-2023 各期半年/季度行
     从三大表移入 fiscal_transition 表存档（不删数据，只移表）；
  3. 2024 起为自然年，日期保持原样。

⚠️ 口径提示（报告与 commentary 必须声明）：
  2024 与 2023 不可直接同比。2023 为 Jul2022-Jun2023，2024 为 Jan-Dec2024，
  中间 2023H2（76.32亿元）不在年度序列里。
  可比 12 个月口径 = 2023H2(76.32) + 2024H1(77.59) = 153.91 亿元 vs FY2023 114.73 亿元。
"""
import os
import sqlite3
import sys

CODE = "09896"
BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB = os.path.join(BASE, "data", "db", f"{CODE}.db")

TABLES = ("income", "balance", "cashflow", "indicators")

# 原日期 → 归一化日期（6月结束财年 → 标为该年 12-31）
RELABLE = {
    "2019-06-30": "2019-12-31",
    "2020-06-30": "2020-12-31",
    "2021-06-30": "2021-12-31",
    "2022-06-30": "2022-12-31",
    "2023-06-30": "2023-12-31",
}

# 需移入 fiscal_transition 存档的旧报告期（2024 前除年报外的全部行 + 2023H2 过渡期）
ARCHIVE = [
    "2020-12-31", "2021-03-31", "2021-12-31",
    "2022-03-31", "2022-09-30", "2022-12-31",
    "2023-03-31", "2023-09-30",
    "2023-12-31",  # 2023H2 过渡期（6个月）
]


def main():
    if not os.path.exists(DB):
        sys.exit(f"DB 不存在: {DB}")
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute("""CREATE TABLE IF NOT EXISTS fiscal_transition (
        src_table TEXT, report_date TEXT, item_name TEXT, amount REAL,
        note TEXT)""")
    cur.execute("DELETE FROM fiscal_transition")

    moved = 0
    for t in ("income", "balance", "cashflow"):
        for rd in ARCHIVE:
            note = "2023H2过渡期(6个月)" if rd == "2023-12-31" else "6月财年的中期报告期"
            n = cur.execute(
                "SELECT COUNT(*) FROM %s WHERE report_date=?" % t, (rd,)).fetchone()[0]
            if n:
                cur.execute(
                    "INSERT INTO fiscal_transition SELECT ?, report_date, item_name, amount, ? "
                    "FROM %s WHERE report_date=?" % t, (t, note, rd))
                cur.execute("DELETE FROM %s WHERE report_date=?" % t, (rd,))
                moved += n
                print(f"  移出 {t:9s} {rd}  {n:3d} 项 → fiscal_transition ({note})")

    # 早期半年/季度行（2019-06-30 之外的年报已在上一步处理，这里清 indicators 以外无需处理）
    for src, dst in RELABLE.items():
        for t in TABLES:
            n = cur.execute(
                "SELECT COUNT(*) FROM %s WHERE report_date=?" % t, (src,)).fetchone()[0]
            if not n:
                continue
            # 目标日期若已有数据（不应发生），先清空以免冲突
            cur.execute("DELETE FROM %s WHERE report_date=?" % t, (dst,))
            cur.execute("UPDATE %s SET report_date=? WHERE report_date=?" % t, (dst, src))
            print(f"  改标 {t:9s} {src} → {dst}  {n:3d} 项")

    conn.commit()

    print("\n归一化后 income 报告期:")
    for rd, in cur.execute("SELECT DISTINCT report_date FROM income ORDER BY report_date"):
        rev = cur.execute(
            "SELECT amount FROM income WHERE report_date=? AND item_name='营业额'", (rd,)).fetchone()
        np_ = cur.execute(
            "SELECT amount FROM income WHERE report_date=? AND item_name='股东应占溢利'", (rd,)).fetchone()
        print(f"  {rd}  营收={rev[0]/1e8 if rev else 0:8.2f}亿  净利={np_[0]/1e8 if np_ else 0:7.2f}亿")

    print("\n指标表报告期:", [r[0] for r in cur.execute(
        "SELECT DISTINCT report_date FROM indicators ORDER BY report_date")])
    print(f"\n合计移出 {moved} 项至 fiscal_transition（数据保留，可复查）")
    conn.close()


if __name__ == "__main__":
    main()
