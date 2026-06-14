# -*- coding: utf-8 -*-
"""中国黄金国际 02099 — PDF信息提取: 补充数据"""
import pdfplumber, os

code = "02099"
pdf_dir = f"data/pdfs/02099"
pdfs = sorted([f for f in os.listdir(pdf_dir) if f.endswith('.pdf')]) if os.path.isdir(pdf_dir) else []
if pdfs:
    latest = pdfs[-1]
    pdf = pdfplumber.open(os.path.join(pdf_dir, latest))
    print(f"PDF: {latest}, {len(pdf.pages)} pages")
    for i, page in enumerate(pdf.pages):
        text = page.extract_text()
        if not text: continue
        for kw in ["雇员", "员工", "人数"]:
            if kw in text:
                idx = text.find(kw)
                print(f"\n--- Page {i+1}: [{kw}] ---")
                print(text[max(0,idx-50):idx+300])
                break
    pdf.close()
else:
    print(f"{code}: 无PDF文件")
