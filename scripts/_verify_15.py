# -*- coding: utf-8 -*-
"""校验: 2025中报MD&A 24H1渠道 + 2021-2024全集团渠道Note"""
import pdfplumber, re, warnings
warnings.filterwarnings('ignore')

def grep(path, pat, tag, ctx=200, maxpages=320, max_hits=3):
    print("="*12, tag, "="*12)
    with pdfplumber.open(path) as pdf:
        n = 0
        for i, p in enumerate(pdf.pages[:maxpages]):
            t = p.extract_text() or ''
            m = re.search(pat, t)
            if m:
                idx = m.start()
                seg = t[max(0, idx-ctx): idx+ctx].replace('\n', ' ')
                print("--- p%d ---" % (i+1))
                print("  " + seg[:600])
                print()
                n += 1
                if n >= max_hits:
                    break

# 2025中报 MD&A 渠道（24H1 中国内地 32.06?）
grep(r'data\pdfs\09992\09992_2025_中报.pdf', r'中國內地渠道|中國內地收入', '2025中报MD&A 中国渠道', 250, 12, 2)
grep(r'data\pdfs\09992\09992_2025_中报.pdf', r'港澳台地區及海外', '2025中报MD&A 港澳台海外', 250, 12, 2)

# 2021-2024 年报 全集团渠道Note
for yr in ['2021', '2022', '2023', '2024']:
    grep(rf'data\pdfs\09992\09992_{yr}_年报.pdf', r'零售店銷售收益|Retail store sales 零售店', f'{yr}年报 渠道Note', 100, 330, 2)
    grep(rf'data\pdfs\09992\09992_{yr}_年报.pdf', r'線上渠道|Online.*channels', f'{yr}年报 线上渠道段', 150, 330, 1)
