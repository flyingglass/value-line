# -*- coding: utf-8 -*-
"""分众传媒 002027 — VL 经常性净利润口径调整

2025年特殊处理:
  - 数禾科技一次性损失 = 减值准备21.48亿 + 权益法亏损3.76亿 = 25.24亿
  - CAS扣非(27.19亿) 未正确排除这两项 → 显式加回
  - 调整后 VL经常性净利润 ≈ 52.43亿

其他年份:
  - CAS扣非已正确处理政府补助等非经常性项目
  - 但CAS扣非未剔除投资收益(理财收益等) → 手动扣除
  - VL经常性 = CAS扣非 - 投资收益
"""


def adjust_metrics(reader, rd, np_val, tax_rate, stock_cfg):
    """个股净利润口径调整 — 引擎钩子

    Args:
        reader: 数据库读取器 (DataReader)
        rd:     报告日期 "YYYY-12-31"
        np_val: 归母净利润 (HOLDER_PROFIT)
        tax_rate: 实际税率
        stock_cfg: STOCKS[code] 配置

    Returns:
        (adj_np, footnotes_list)
    """
    footnotes = []
    if np_val is None:
        return None, footnotes

    year = rd[:4]

    # 基数: CAS 扣非净利润 (已正确处理政府补助、银行利息等)
    deducted = reader.financial_item("income", "*扣除非经常性损益后的净利润", rd)
    if deducted is None:
        # 兜底: 扣非缺失时用归母净利润
        deducted = np_val

    if year == "2025":
        # ---- 2025: 加回数禾科技一次性损失 ----
        # ① 长期股权投资减值准备 (CAS扣非未正确排除)
        impair = reader.financial_item("income", "资产减值损失", rd) or 0
        # 正常年份减值约 0.1~0.4亿, 2025年飙升至21.48亿均为数禾减值
        # 直接全额加回 (不可税前扣除)

        # ② 权益法投资亏损 (数禾科技 Q4 经营亏损, 体现在投资收益科目)
        # Q3累计投资收益4.79亿, 全年仅2.08亿 → Q4单季-2.71亿
        # 含数禾权益法亏损约3.76亿 (部分被其他投资收益抵消)
        SHUHE_EQUITY_LOSS = 3.76e8

        adj_np = deducted + abs(impair) + SHUHE_EQUITY_LOSS
        shares = stock_cfg.get("shares", 14442000000)

        footnotes.append(
            f"2025年: CAS扣非({deducted/1e8:.1f}亿) "
            f"+ 数禾减值准备({abs(impair)/1e8:.2f}亿) "
            f"+ 权益法投资亏损({SHUHE_EQUITY_LOSS/1e8:.2f}亿) "
            f"= VL经常性净利润{adj_np/1e8:.1f}亿 "
            f"(对应每股收益{adj_np/shares:.2f}元)。"
            f"数禾科技已于2026年1月以7.91亿清仓54.97%股权, 未来不再影响报表。"
        )

        return adj_np, footnotes

    # ---- 其他年份: CAS扣非 − 投资收益 ----
    # CAS扣非已排除政府补助等非经常性项目,
    # 但未排除投资收益(理财收益+权益法损益), 需手动扣除
    invest_income = reader.financial_item("income", "投资收益", rd) or 0
    adj_np = deducted - invest_income

    if abs(invest_income) > 0.5e8:
        footnotes.append(
            f"{year}年: CAS扣非({deducted/1e8:.1f}亿) "
            f"- 投资收益({invest_income/1e8:+.2f}亿) "
            f"= VL经常性{adj_np/1e8:.1f}亿"
        )

    return adj_np, footnotes
