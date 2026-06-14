# -*- coding: utf-8 -*-
"""宁德时代 300750 — A股EPS调整: CAS扣非已处理非经常项目"""
def adjust_metrics(reader, rd, np_val, tax_rate, stock_cfg):
    footnotes = []
    if np_val is None: return None, footnotes
    deducted = reader.financial_item("income", "*扣除非经常性损益后的净利润", rd)
    if deducted and abs(deducted - np_val) > 5e6:
        footnotes.append(f"EPS adj: CD {deducted/1e8:.1f} -> VL {deducted/1e8:.1f}亿 (归母{np_val/1e8:.1f}亿)")
        return deducted, footnotes
    return np_val, footnotes
