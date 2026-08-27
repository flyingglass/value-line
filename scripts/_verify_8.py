# -*- coding: utf-8 -*-
"""校验步骤8: 港澳台及海外门店/机器人 完整段落"""
import pdfplumber, warnings
warnings.filterwarnings('ignore')

def dump_para(path, kws, tag, maxpages=60):
    print("="*10, tag, "="*10)
    with pdfplumber.open(path) as pdf:
        for i, p in enumerate(pdf.pages[:maxpages]):
            t = p.extract_text() or ''
            for kw in kws:
                if kw in t:
                    idx = t.find(kw)
                    seg = t[max(0, idx-500): idx+900].replace('\n', ' ')
                    print("--- p%d [%s] ---" % (i+1, kw))
                    print("  " + seg[:750])
                    print()
                    break

dump_para(r'data\pdfs\09992\09992_2022_中报.pdf', ['港澳台', '海外'], '2022中报 港澳台海外门店', 20)
dump_para(r'data\pdfs\09992\09992_2023_中报.pdf', ['港澳台', '106'], '2023中报 港澳台海外门店', 20)
dump_para(r'data\pdfs\09992\09992_2023_年报.pdf', ['港澳台'], '2023年报 港澳台海外门店', 30)
dump_para(r'data\pdfs\09992\09992_2024_中报.pdf', ['港澳台'], '2024中报 港澳台海外门店', 20)
dump_para(r'data\pdfs\09992\09992_2024_年报.pdf', ['港澳台'], '2024年报 港澳台海外门店', 30)
