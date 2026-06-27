# -*- coding: utf-8 -*-
"""颐海国际 01579 — PDF 提取"""
import pdfplumber, re, os, sys
if sys.platform == 'win32': sys.stdout.reconfigure(encoding='utf-8', errors='replace')

code = "01579"
pdf_dir = f"data/pdfs/{code}"
files = sorted([f for f in os.listdir(pdf_dir) if f.endswith('.pdf')])

for fname in files:
    if '2025' not in fname or '年报' not in fname:
        continue
    path = os.path.join(pdf_dir, fname)
    try:
        with pdfplumber.open(path) as pdf:
            full = "\n".join([p.extract_text() or "" for p in pdf.pages])
            m = re.search(r'员工\S*总\S*数[：:是为]?\s*[\d,]+', full)
            if m: print(f"employees: {m.group()}")
            m = re.search(r'研发\S*费\S*[约约为]?\s*[\d.]+亿', full)
            if m: print(f"rd: {m.group()}")
    except: pass
