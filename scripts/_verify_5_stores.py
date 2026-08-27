# -*- coding: utf-8 -*-
"""校验步骤5: 各期 PDF 门店/机器人数 + 2023中报损益表"""
import pdfplumber, re, warnings
warnings.filterwarnings('ignore')

PDFS = [
    ('2020-06-30', r'data\pdfs\09992\09992_2020_招股书_中文_官网.pdf'),
    ('2020-12-31', r'data\pdfs\09992\09992_2020_年报.pdf'),
    ('2021-06-30', r'data\pdfs\09992\09992_2021_中报.pdf'),
    ('2021-12-31', r'data\pdfs\09992\09992_2021_年报.pdf'),
    ('2022-06-30', r'data\pdfs\09992\09992_2022_中报.pdf'),
    ('2022-12-31', r'data\pdfs\09992\09992_2022_年报.pdf'),
    ('2023-06-30', r'data\pdfs\09992\09992_2023_中报.pdf'),
    ('2023-12-31', r'data\pdfs\09992\09992_2023_年报.pdf'),
]

for period, path in PDFS:
    print(f"\n===== {period} =====")
    with pdfplumber.open(path) as pdf:
        for i, p in enumerate(pdf.pages):
            t = p.extract_text() or ''
            if '機器人商店' in t and re.search(r'機器人商店.{0,120}[\d,]{3,}', t):
                print(f"--- p{i+1} ---")
                # 提取门店/机器人数量行
                for ln in t.split('\n'):
                    if re.search(r'(零售店|機器人商店)', ln) and re.search(r'[\d,]{3,}', ln) and len(ln) < 140:
                        print("  " + ln[:130])
                break
