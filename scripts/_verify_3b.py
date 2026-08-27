# -*- coding: utf-8 -*-
import pdfplumber, warnings, os
warnings.filterwarnings('ignore')
p = r'data\pdfs\09992\09992_2023_年报.pdf'
print('exists', os.path.exists(p), os.path.getsize(p))
with pdfplumber.open(p) as pdf:
    print('pages', len(pdf.pages))
    for i in range(len(pdf.pages)):
        t = pdf.pages[i].extract_text() or ''
        if ('損益' in t and '收益' in t) or '溢利' in t:
            print('--- p', i+1, 'len', len(t), '---')
            print(t[:500])
            if i > 150:
                break
