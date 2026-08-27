# -*- coding: utf-8 -*-
import pdfplumber, re, warnings
warnings.filterwarnings('ignore')

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

grep(r'data\pdfs\09992\09992_2022_中报.pdf', r'港澳台地區及海外機器人商店', '2022中报 p10 港澳台海外机器人', 500)
grep(r'data\pdfs\09992\09992_2021_中报.pdf', r'機器人商店|零售店', '2021中报 门店', 300, 25)
grep(r'data\pdfs\09992\09992_2024_中报.pdf', r'港澳台地區及海外|83', '2024中报 海外门店', 400, 25)
grep(r'data\pdfs\09992\09992_2024_年报.pdf', r'港澳台地區及海外門店|合計零售店', '2024年报 海外门店', 400, 30)
