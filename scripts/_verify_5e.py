# -*- coding: utf-8 -*-
"""校验步骤5e: 2020-2022 门店数量聚焦"""
import pdfplumber, re, warnings
warnings.filterwarnings('ignore')

JOBS = [
    ('2020-12-31', r'data\pdfs\09992\09992_2020_年报.pdf'),
    ('2021-06-30', r'data\pdfs\09992\09992_2021_中报.pdf'),
    ('2022-06-30', r'data\pdfs\09992\09992_2022_中报.pdf'),
    ('2022-12-31', r'data\pdfs\09992\09992_2022_年报.pdf'),
]

for tag, path in JOBS:
    print("=====", tag, "=====")
    with pdfplumber.open(path) as pdf:
        for i, p in enumerate(pdf.pages):
            t = p.extract_text() or ''
            if re.search(r'(零售店|機器人商店).{0,160}[\d,]{3,}', t):
                s = t.replace('\n', ' ')
                for kw in ['零售店', '機器人商店']:
                    for m in re.finditer(kw, s):
                        seg = s[max(0, m.start()-50): m.end()+170]
                        if re.search(r'(數量|增至|家|台|間|合計|數目|開設)', seg) and re.search(r'[\d,]{3,}', seg):
                            print("  p%d: %s" % (i+1, seg.strip()[:190]))
