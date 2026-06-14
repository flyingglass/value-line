# -*- coding: utf-8 -*-
"""泡泡玛特 09992 — VL 经常性净利润口径调整
港股 IFRS: 排除 FVTPL/汇兑/政府补贴/并购重计量等非经常项目
"""
def adjust_metrics(reader, rd, np_val, tax_rate, stock_cfg):
    footnotes = []
    if np_val is None:
        return None, footnotes

    other_gain = reader.financial_item("income", "其他收益", rd) or 0
    other_income = reader.financial_item("income", "其他收入", rd) or 0
    # 其他收益 = FVTPL变动 + 汇兑 + 并购会计重计量 (全部非经营)
    # 其他收入 = 政府补贴 + 授权费等非核心收入
    nonrecur_adj = (other_gain + other_income) * (1 - tax_rate)
    adj_np = np_val - nonrecur_adj

    parts = []
    if abs(other_gain) > 5e6:
        parts.append(f"FV {other_gain/1e8:+.2f}")
    if abs(other_income) > 5e6:
        parts.append(f"GS {other_income/1e8:+.2f}")
    if parts:
        item_str = " ".join(parts)
        footnotes.append(f"EPS adj: {item_str} → VL {adj_np/1e8:.1f}亿 (归母{np_val/1e8:.1f}亿)")

    return adj_np, footnotes
