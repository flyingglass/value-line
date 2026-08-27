# -*- coding: utf-8 -*-
"""校验步骤5b: 门店/机器人完整句子提取"""
import pdfplumber, re, warnings
warnings.filterwarnings('ignore')

PDFS = [
    ('2020-06-30', r'data\pdfs\09992\09992_2020_招股书_中文_官网.pdf', ['零售店', '機器人商店']),
    ('2020-12-31', r'data\pdfs\09992\09992_2020_年报.pdf', ['零售店', '機器人商店']),
    ('2021-06-30', r'data\pdfs\09992\09992_2021_中报.pdf', ['零售店', '機器人商店']),
    ('2021-12-31', r'data\pdfs\09992\09992_2021_年报.pdf', ['零售店', '機器人商店']),
    ('2022-06-30', r'data\pdfs\09992\09992_2022_中报.pdf', ['零售店', '機器人商店']),
    ('2022-12-31', r'data\pdfs\09992\09992_2022_年报.pdf', ['零售店', '機器人商店']),
    ('2023-06-30', r'data\pdfs\09992\09992_2023_中报.pdf', ['零售店', '機器人商店']),
    ('2023-12-31', r'data\pdfs\09992\09992_2023_年报.pdf', ['零售店', '機器人商店']),
]

for period, path, kws in PDFS:
    print(f"\n===== {period} =====")
    with pdfplumber.open(path) as pdf:
        for i, p in enumerate(pdf.pages):
            t = p.extract_text() or ''
            hits = []
            for kw in kws:
                for m in re.finditer(kw, t):
                    s = t[max(0, m.start()-60): m.end()+140]
                    if re.search(r'[\d,]{3,}', s):
                        hits.append(s.replace('\n', ' ').strip())
            if hits:
                print(f"--- p{i+1} ---")
                seen = set()
                for h in hits:
                    key = h[:30]
                    if key in seen: continue
                    seen.add(key)
                    print("  " + h[:180])
