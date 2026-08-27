# -*- coding: utf-8 -*-
import pdfplumber, warnings
warnings.filterwarnings('ignore')
with pdfplumber.open(r'data\pdfs\09992\09992_2025_中报.pdf') as pdf:
    for pg in [78, 79]:
        t = pdf.pages[pg-1].extract_text() or ''
        print(f"----- p{pg} -----")
        print(t[:3800])
        print()
