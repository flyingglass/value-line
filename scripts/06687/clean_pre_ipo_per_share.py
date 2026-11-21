# -*- coding: utf-8 -*-
"""清洗 06687 上市前股本口径的「每股类」指标（数据层修正，不改 engine）

问题（2026-11-21 首次 build 实测）:
  AKShare / TDX 对 2025-10-21 上市前各期给出的每股指标，是按重组前约 140 万股
  的股本计算的（PER_OI≈493.8 → 697191000/493.8≈141万股；每股亏损 -140.98 ~ -283.61 元）。
  与上市后 436,263,500 股完全不可比，混算后产生三处硬错误:
    1) engine._compute_ttm_eps 方案B: h2_prev = FY2024(0.07) - H1_2024(-33.03) = 33.10,
       再加 H1_2025(-0.23) → EPS TTM = 32.87 元、P/E = 0.3x（真实 TTM 应为负）。
    2) engine.share_count() 用 OPERATE_INCOME/PER_OI 反推股本，早年取到 141 万股，
       使 PER_NETCASH = (扣非净利+折旧)/141万 → CF 估值线出现 -5782.55、+358.45。
    3) AKShare 派生列 EPS_TTM（2024=8.74 / 2025=-3.79）同属混口径。

处理（留白 / 统一口径，优于错误数字）:
  - income 表每股盈利 item_code 004027002/004027003：2025-06-30 之前置 NULL。
    保留 2025H1 / 2025A / 2026H1（这三期已是上市后或可比口径）。
    → _compute_ttm_eps 三条方案都不成立，返回 None，Header 的 EPS TTM 与 P/E 诚实留白。
  - indicators.PER_OI：2025-12-31 之前置 NULL（保留 2025 年反推出 436,263,500 股）。
    → 早年 share_count 回退到 meta.total_shares / config.shares，CF 线回到 ±几十的量级。
  - indicators.EPS_TTM：全部置 NULL（AKShare 派生列，本引擎自行计算 TTM）。

回滚: 重跑 `python scripts/fetcher.py 06687` 即恢复原始 AKShare/TDX 数值。
本脚本只把失真值置 NULL，不删行、不改写任何真实金额。
"""
import os
import sqlite3

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB = os.path.join(BASE, "data", "db", "06687.db")


def main():
    conn = sqlite3.connect(DB)
    steps = [
        ("income 每股盈利（2025H1 之前）",
         "UPDATE income SET amount=NULL "
         "WHERE item_code IN ('004027002','004027003') AND report_date < '2025-06-30'"),
        ("indicators.PER_OI（2025A 之前）",
         "UPDATE indicators SET amount=NULL "
         "WHERE item_name='PER_OI' AND report_date < '2025-12-31'"),
        ("indicators.EPS_TTM（全部）",
         "UPDATE indicators SET amount=NULL WHERE item_name='EPS_TTM'"),
    ]
    for label, sql in steps:
        cur = conn.execute(sql)
        print(f"  {label}: {cur.rowcount} 行置 NULL")
    note = (
        "上市前每股指标(重组前约141万股口径)与上市后436,263,500股不可比, "
        "已于2026-11-21置NULL; 见 scripts/06687/clean_pre_ipo_per_share.py; "
        "重跑 fetcher.py 06687 可恢复原值"
    )
    conn.execute("INSERT OR REPLACE INTO meta VALUES (?,?)", ("data_clean_note", note))
    conn.commit()

    # 自检
    left = conn.execute(
        "SELECT report_date,item_code,amount FROM income "
        "WHERE item_code IN ('004027002','004027003') "
        "AND amount IS NOT NULL ORDER BY report_date,item_code").fetchall()
    print("  保留的 EPS:", left)
    poi = conn.execute(
        "SELECT report_date,amount FROM indicators "
        "WHERE item_name='PER_OI' AND amount IS NOT NULL").fetchall()
    print("  保留的 PER_OI:", poi)
    conn.close()


if __name__ == "__main__":
    main()
