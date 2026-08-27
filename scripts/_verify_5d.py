# -*- coding: utf-8 -*-
"""校验步骤5d: 各期门店/机器人数量（批量）"""
import pdfplumber, re, warnings, sys
warnings.filterwarnings('ignore')

JOBS = [
    ('2020-06-30', r'data\pdfs\09992\09992_2020_招股书_中文_官网.pdf'),
    ('2020-12-31', r'data\pdfs\09992\09992_2020_年报.pdf'),
    ('2021-06-30', r'data\pdfs\09992\09992_2021_中报.pdf'),
    ('2022-06-30', r'data\pdfs\09992\09992_2022_中报.pdf'),
    ('2022-12-31', r'data\pdfs\09992\09992_2022_年报.pdf'),
    ('2023-06-30', r'data\pdfs\09992\09992_2023_中报.pdf'),
    ('2023-12-31', r'data\pdfs\09992\09992_2023_年报.pdf'),
]

for tag, path in JOBS:
    print("=====", tag, "=====")
    with pdfplumber.open(path) as pdf:
        for i, p in enumerate(pdf.pages):
            t = p.extract_text() or ''
            if ('機器人商店' in t or '零售店' in t) and re.search(r'[\d,]{3,}', t):
                out = []
                for kw in ['零售店', '機器人商店']:
                    for m in re.finditer(kw, t):
                        s = t[max(0, m.start()-70): m.end()+150].replace('\n', ' ')
                        if re.search(r'[\d,]{3,}', s):
                            out.append(s.strip())
                if out:
                    # 只保留与数量相关的行
                    keep = [s for s in out if re.search(r'(數量|家|台|增至|間|數目|合計|間零售店|台機器人|店)', s)]
                    if keep:
                        print("--- p%d ---" % (i+1))
                        seen = set()
                        for s in keep[:6]:
                            if s[:25] in seen: continue
                            seen.add(s[:25])
                            print("  " + s[:180])
