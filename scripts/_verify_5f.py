# -*- coding: utf-8 -*-
import pdfplumber, re, warnings
warnings.filterwarnings('ignore')

def dump(path, kws, tag):
    print("=====", tag, "=====")
    with pdfplumber.open(path) as pdf:
        for i, p in enumerate(pdf.pages):
            t = p.extract_text() or ''
            for kw in kws:
                if kw in t:
                    idx = t.find(kw)
                    seg = t[max(0, idx-400): idx+700].replace('\n', ' ')
                    if re.search(r'[\d,]{3,}', seg):
                        print("--- p%d [%s] ---" % (i+1, kw))
                        print("  " + seg[:600])
                        print()
                    break

dump(r'data\pdfs\09992\09992_2020_年报.pdf', ['零售店', 'retail stores'], '2020年报 门店')
dump(r'data\pdfs\09992\09992_2023_中报.pdf', ['55', '143'], '2023中报 门店')
dump(r'data\pdfs\09992\09992_2023_年报.pdf', ['零售店數量', '零售店 數量'], '2023年报 门店')
dump(r'data\pdfs\09992\09992_2024_中报.pdf', ['零售店', '門店數量'], '2024中报 门店')
