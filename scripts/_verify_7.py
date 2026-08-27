# -*- coding: utf-8 -*-
"""校验步骤7: 2022中报/2024中报/2024年报 门店 + 2025年报24A渠道 + 24H1线上子渠道"""
import pdfplumber, re, warnings
warnings.filterwarnings('ignore')

def dump(path, kws, tag, ctx=120, maxpages=320):
    print("="*10, tag, "="*10)
    with pdfplumber.open(path) as pdf:
        for i, p in enumerate(pdf.pages[:maxpages]):
            t = p.extract_text() or ''
            for kw in kws:
                if kw in t:
                    idx = t.find(kw)
                    seg = t[max(0, idx-ctx): idx+ctx*4].replace('\n', ' ')
                    print("--- p%d [%s] ---" % (i+1, kw))
                    print("  " + seg[:520])
                    print()
                    break

# 2022中报 门店（22H1 内地308 机器人?）
dump(r'data\pdfs\09992\09992_2022_中报.pdf', ['零售店', '機器人商店'], '2022中报 门店', maxpages=30)
# 2024中报 门店海外（24H1 港澳台海外 83? 机器人143?）
dump(r'data\pdfs\09992\09992_2024_中报.pdf', ['港澳台', '機器人商店'], '2024中报 海外门店', maxpages=30)
# 2024年报 门店（24A 内地401 海外120 机器人2472?）
dump(r'data\pdfs\09992\09992_2024_年报.pdf', ['門店數量', '合計零售店', '機器人商店數量'], '2024年报 门店', maxpages=30)
# 2025年报 Note 渠道表（24A渠道拆分）
dump(r'data\pdfs\09992\09992_2025_年报.pdf', ['Retail stores 零售店'], '2025年报 Note渠道', maxpages=100)
# 2025中报 线上子渠道（24H1 抽盒机等）
dump(r'data\pdfs\09992\09992_2025_中报.pdf', ['泡泡瑪特抽盒機', '抽盒機'], '2025中报 线上子渠道', maxpages=130)
