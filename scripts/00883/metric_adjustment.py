# -*- coding: utf-8 -*-
"""中国海洋石油 00883 — VL EPS调整: 排除非经常项目 (港股IFRS)
油气行业特点: 资产减值(油气资产impairment)、汇兑收益(FX)、政府补贴(GS)等"""
def adjust_metrics(reader, rd, np_val, tax_rate, stock_cfg):
    footnotes = []
    if np_val is None: return None, footnotes
    items = [
        ("公允价值变动收益", "FV"), ("汇兑收益", "FX"), ("政府补助", "GS"),
        ("资产处置收益", "IM"), ("资产减值损失", "IM"), ("其他收益", "OG"),
    ]
    nonrecur = []
    seen = set()
    for item_name, abbr in items:
        val = reader.financial_item("income", item_name, rd) or 0
        if abs(val) > 5e6 and abbr not in seen:
            nonrecur.append((abbr, val))
            seen.add(abbr)
    if nonrecur:
        adj_np = np_val
        for _, v in nonrecur: adj_np -= v * (1 - tax_rate)
        item_str = " ".join([f"{a} {v/1e8:+.2f}" for a, v in nonrecur])
        footnotes.append(f"EPS adj: {item_str} -> VL {adj_np/1e8:.1f}亿 (归母{np_val/1e8:.1f}亿)")
    else:
        adj_np = np_val
    return adj_np, footnotes
