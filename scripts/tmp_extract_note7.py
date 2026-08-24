# -*- coding: utf-8 -*-
"""临时脚本：提取 Note 14 PP&E 明细"""
import pdfplumber
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

path = r'c:\LY\Repo\llm\value-line\data\pdfs\09992\09992_2025_年报.pdf'

with pdfplumber.open(path) as pdf:
    for i in [292, 293, 294]:
        txt = pdf.pages[i].extract_text() or ''
        print(f'\n########## PDF PAGE {i+1} ##########')
        print(txt[:3500])
