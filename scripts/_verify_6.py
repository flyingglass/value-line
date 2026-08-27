# -*- coding: utf-8 -*-
"""校验步骤6: 23A线上子渠道 / 24A渠道 / 23-24门店"""
import pdfplumber, re, warnings
warnings.filterwarnings('ignore')

def dump_lines(path, kws, tag, ctx=80, maxpages=300):
    print("="*10, tag, "="*10)
    with pdfplumber.open(path) as pdf:
        for i, p in enumerate(pdf.pages[:maxpages]):
            t = p.extract_text() or ''
            for kw in kws:
                if kw in t:
                    idx = t.find(kw)
                    seg = t[max(0, idx-ctx): idx+ctx*3].replace('\n', ' ')
                    print("--- p%d [%s] ---" % (i+1, kw))
                    print("  " + seg[:420])
                    print()
                    break

# 2023年报 线上子渠道
dump_lines(r'data\pdfs\09992\09992_2023_年报.pdf', ['線上銷售收益', '線上渠道'], '2023年报 线上渠道', maxpages=250)
# 2025年报 24A渠道（Note 3）
dump_lines(r'data\pdfs\09992\09992_2025_年报.pdf', ['按渠道', '收益明細'], '2025年报 渠道', maxpages=150)
# 2025中报 24H1线上子渠道
dump_lines(r'data\pdfs\09992\09992_2025_中报.pdf', ['線上銷售收益'], '2025中报 线上渠道', maxpages=120)
# 2023中报/2023年报/2024中报 门店
dump_lines(r'data\pdfs\09992\09992_2023_中报.pdf', ['門店數量', '零售店'], '2023中报 门店', maxpages=30)
dump_lines(r'data\pdfs\09992\09992_2023_年报.pdf', ['門店數量'], '2023年报 门店', maxpages=30)
dump_lines(r'data\pdfs\09992\09992_2024_中报.pdf', ['門店數量'], '2024中报 门店', maxpages=30)
