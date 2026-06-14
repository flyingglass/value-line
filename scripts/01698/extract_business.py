# -*- coding: utf-8 -*-
"""腾讯音乐 01698 — PDF信息提取: 员工人数/用户数等补充数据"""
import pdfplumber, os

code = "01698"
pdf_dir = f"data/pdfs/{code}"
pdfs = sorted([f for f in os.listdir(pdf_dir) if f.endswith('.pdf')]) if os.path.isdir(pdf_dir) else []
if pdfs:
    latest = pdfs[-1]
    pdf = pdfplumber.open(os.path.join(pdf_dir, latest))
    print(f"PDF: {latest}, {len(pdf.pages)} pages")
    for i, page in enumerate(pdf.pages):
        text = page.extract_text()
        if not text: continue
        for kw in ["雇员", "员工", "用户", "MAU", "人数"]:
            if kw in text:
                idx = text.find(kw)
                print(f"\n--- Page {i+1}: [{kw}] ---")
                print(text[max(0,idx-50):idx+300])
                break
    pdf.close()
else:
    print(f"{code}: 无PDF文件")
