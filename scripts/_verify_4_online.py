# -*- coding: utf-8 -*-
"""校验步骤4b: 线上渠道数字表（抽盒机/抖音/天猫/其他）"""
import pdfplumber, re, warnings
warnings.filterwarnings('ignore')

for path in [r'data\pdfs\09992\09992_2025_中报.pdf', r'data\pdfs\09992\09992_2025_年报.pdf', r'data\pdfs\09992\09992_2026_中报.pdf']:
    print('='*15, path.split(chr(92))[-1], '='*15)
    with pdfplumber.open(path) as pdf:
        for i, p in enumerate(pdf.pages):
            t = p.extract_text() or ''
            if ('抽盒機' in t and '天貓' in t and '抖音' in t and re.search(r'\d{3,}', t)) or ('抽盒機' in t and re.search(r'抽盒機.{0,80}[\d,]{5,}', t)):
                # 打印该页含数字的渠道行
                print(f"--- p{i+1} ---")
                lines = t.split('\n')
                for ln in lines:
                    if re.search(r'(抽盒機|天貓|抖音|京東|其他|線上)', ln) and re.search(r'[\d,]{4,}', ln):
                        print("  " + ln[:110])
                break
