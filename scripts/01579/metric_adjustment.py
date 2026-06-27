# -*- coding: utf-8 -*-
"""颐海国际 01579 — VL EPS调整: 港股IFRS, 无明显非经常项目
消费品公司, 净利润波动主要来自原材料成本和渠道结构变化"""
def adjust_metrics(reader, rd, np_val, tax_rate, stock_cfg):
    footnotes = []
    if np_val is None: return None, footnotes
    adj_np = np_val
    return adj_np, footnotes
