# -*- coding: utf-8 -*-
"""校验步骤3: 运输及物流开支 PDF 原文 + 2023 损益表"""
import pdfplumber, re, warnings
warnings.filterwarnings('ignore')

def dump_context(path, kw, ctx=40, maxpages=200):
    with pdfplumber.open(path) as pdf:
        for i, p in enumerate(pdf.pages[:maxpages]):
            t = p.extract_text() or ''
            if kw in t:
                idx = t.find(kw)
                print(f"--- {path.split(chr(92))[-1]} p{i+1} ---")
                print(t[max(0,idx-ctx*8): idx+ctx*12].replace('\n', '|'))
                print()

dump_context(r'data\pdfs\09992\09992_2026_中报.pdf', '運輸及物流')
dump_context(r'data\pdfs\09992\09992_2025_中报.pdf', '運輸及物流')
