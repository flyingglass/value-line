# -*- coding: utf-8 -*-
"""校验步骤2g: 搜索损益表标题页并打印关键行"""
import pdfplumber, re, warnings
warnings.filterwarnings('ignore')

PDFS = [
    ('2021-06-30', r'data\pdfs\09992\09992_2021_中报.pdf'),
    ('2021-12-31', r'data\pdfs\09992\09992_2021_年报.pdf'),
    ('2022-06-30', r'data\pdfs\09992\09992_2022_中报.pdf'),
    ('2022-12-31', r'data\pdfs\09992\09992_2022_年报.pdf'),
    ('2023-06-30', r'data\pdfs\09992\09992_2023_中报.pdf'),
    ('2023-12-31', r'data\pdfs\09992\09992_2023_年报.pdf'),
    ('2024-06-30', r'data\pdfs\09992\09992_2024_中报.pdf'),
    ('2024-12-31', r'data\pdfs\09992\09992_2024_年报.pdf'),
    ('2025-06-30', r'data\pdfs\09992\09992_2025_中报.pdf'),
    ('2025-12-31', r'data\pdfs\09992\09992_2025_年报.pdf'),
]

def page_texts(path):
    with pdfplumber.open(path) as pdf:
        return [p.extract_text() or '' for p in pdf.pages]

for period, path in PDFS:
    print(f"\n===== {period} =====")
    texts = page_texts(path)
    for i, t in enumerate(texts):
        if i < 3: continue
        if ('綜合損益' in t and '收益' in t and '溢利' in t) or ('Profit or Loss' in t and '收益' in t and '溢利' in t):
            print(f"[損益表 p{i+1}]")
            lines = t.split('\n')
            # 打印损益表行（含数字），限 30 行
            cnt = 0
            for ln in lines:
                ln = ln.strip()
                if re.search(r'[\d,]{6,}', ln) and cnt < 30:
                    print("  " + ln[:95]); cnt += 1
            break
    else:
        print("  !! 未找到")
