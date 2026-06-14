# -*- coding: utf-8 -*-
"""分众传媒 002027 — VL EPS调整: CAS扣非 + 数禾一次性加回 - 投资理财收益"""
def adjust_metrics(reader, rd, np_val, tax_rate, stock_cfg):
    footnotes = []
    if np_val is None: return None, footnotes
    year = rd[:4]
    deducted = reader.financial_item("income", "*扣除非经常性损益后的净利润", rd) or np_val

    if year == "2025":
        impair = reader.financial_item("income", "资产减值损失", rd) or 0  # 数禾减值 21.48亿
        SHUHE_EQUITY_LOSS = 3.76e8
        adj_np = deducted + abs(impair) + SHUHE_EQUITY_LOSS
        footnotes.append(f"EPS adj: CD {deducted/1e8:.1f} +IM {abs(impair)/1e8:.1f} +EL {SHUHE_EQUITY_LOSS/1e8:.1f} → VL {adj_np/1e8:.1f}亿 (数禾Q4一次性)")
    else:
        invest_income = reader.financial_item("income", "投资收益", rd) or 0
        adj_np = deducted - invest_income
        if abs(invest_income) > 0.5e8:
            footnotes.append(f"EPS adj: CD {deducted/1e8:.1f} -II {invest_income/1e8:+.1f} → VL {adj_np/1e8:.1f}亿")
    return adj_np, footnotes
