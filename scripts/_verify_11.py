# -*- coding: utf-8 -*-
import pdfplumber, re, warnings
warnings.filterwarnings('ignore')

def dump_para(path, pat, tag, ctx=450, maxpages=320):
    print("="*10, tag, "="*10)
    with pdfplumber.open(path) as pdf:
        for i, p in enumerate(pdf.pages[:maxpages]):
            t = p.extract_text() or ''
            m = re.search(pat, t)
            if m:
                idx = m.start()
                seg = t[max(0, idx-ctx): idx+ctx].replace('\n', ' ')
                print("--- p%d ---" % (i+1))
                print("  " + seg[:650])
                print()
                break

dump_para(r'data\pdfs\09992\09992_2022_中报.pdf', r'機器人商店數量', '2022中报 机器人总数', 450, 15)
dump_para(r'data\pdfs\09992\09992_2024_中报.pdf', r'機器人商店', '2024中报 机器人', 450, 15)
dump_para(r'data\pdfs\09992\09992_2024_年报.pdf', r'機器人商店數量', '2024年报 机器人', 450, 30)
dump_para(r'data\pdfs\09992\09992_2024_中报.pdf', r'零售店', '2024中报 零售店(海外)', 500, 12)
