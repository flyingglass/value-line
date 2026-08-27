# -*- coding: utf-8 -*-
"""校验: 2025中报Note完整 + 2024年报渠道表 + 港澳台海外机器人"""
import pdfplumber, re, warnings
warnings.filterwarnings('ignore')

print("="*15, "2025中报 Note p76-80 完整", "="*15)
with pdfplumber.open(r'data\pdfs\09992\09992_2025_中报.pdf') as pdf:
    for pg in range(76, 82):
        t = pdf.pages[pg-1].extract_text() or ''
        print(f"----- p{pg} -----")
        print(t[:2400])
        print()

def grep(path, pat, tag, ctx=350, maxpages=320):
    print("="*10, tag, "="*10)
    with pdfplumber.open(path) as pdf:
        for i, p in enumerate(pdf.pages[:maxpages]):
            t = p.extract_text() or ''
            m = re.search(pat, t)
            if m:
                idx = m.start()
                seg = t[max(0, idx-ctx): idx+ctx].replace('\n', ' ')
                print("--- p%d ---" % (i+1))
                print("  " + seg[:600])
                print()
                break

grep(r'data\pdfs\09992\09992_2024_年报.pdf', r'港澳台地區及海外機器人商店', '2024年报 港澳台海外机器人', 450, 35)
grep(r'data\pdfs\09992\09992_2024_中报.pdf', r'港澳台地區及海外機器人商店|robot shops in Hong Kong', '2024中报 港澳台海外机器人', 450, 20)
grep(r'data\pdfs\09992\09992_2024_年报.pdf', r'Roboshops.*Retail stores|Retail stores.*Roboshops', '2024年报 Note渠道', 400, 130)
grep(r'data\pdfs\09992\09992_2023_年报.pdf', r'抖音|DouYin', '2023年报 抖音', 300, 25)
