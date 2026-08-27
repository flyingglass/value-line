# -*- coding: utf-8 -*-
import pdfplumber, warnings
warnings.filterwarnings('ignore')
for path, pages in [(r'data\pdfs\09992\09992_2023_中报.pdf', [17, 18, 19]), (r'data\pdfs\09992\09992_2022_中报.pdf', [10, 11])]:
    print("="*20, path.split(chr(92))[-1], "="*20)
    with pdfplumber.open(path) as pdf:
        for pg in pages:
            t = pdf.pages[pg-1].extract_text() or ''
            print(f"----- p{pg} -----")
            print(t[:2600])
