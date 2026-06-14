# -*- coding: utf-8 -*-
"""英伟达 NVDA — PDF信息提取: 员工人数等补充数据"""
import pdfplumber, os

code = "NVDA"
pdf_dir = f"data/pdfs/{code}"
pdfs = sorted([f for f in os.listdir(pdf_dir) if f.endswith('.pdf')]) if os.path.isdir(pdf_dir) else []
if pdfs:
    latest = pdfs[-1]
    pdf = pdfplumber.open(os.path.join(pdf_dir, latest))
    print(f"PDF: {latest}, {len(pdf.pages)} pages")
    for i, page in enumerate(pdf.pages):
        text = page.extract_text()
        if not text: continue
        for kw in ["employee", "headcount", "employees"]:
            if kw.lower() in text.lower():
                idx = text.lower().find(kw.lower())
                print(f"\n--- Page {i+1}: [{kw}] ---")
                print(text[max(0,idx-50):idx+300])
                break
    pdf.close()
else:
    print(f"{code}: 无PDF文件")
