# -*- coding: utf-8 -*-
import pdfplumber, warnings
warnings.filterwarnings('ignore')
with pdfplumber.open(r'data\pdfs\09992\09992_2021_年报.pdf') as pdf:
    print("pages:", len(pdf.pages))
    for i, p in enumerate(pdf.pages[:40]):
        t = p.extract_text() or ''
        if '損益' in t or ('收益' in t and '溢利' in t):
            print(f"--- p{i+1} ---")
            print(t[:1500])
            break
