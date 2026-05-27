"""找营收结构按地区划分的PDF原文"""
import pdfplumber

pdf_path = "C:/LY/Repo/llm/value-line/data/pdfs/09992/09992_2025_年报.pdf"
pdf = pdfplumber.open(pdf_path)

print(f"Total pages: {len(pdf.pages)}")

# Look for revenue breakdown by region tables
for i, page in enumerate(pdf.pages):
    text = page.extract_text()
    if not text: continue
    if "中国内地" in text and ("收入" in text or "%" in text):
        idx = text.find("中国内地")
        print(f"\n=== Page {i+1} (found 中国内地) ===")
        print(text[max(0,idx-100):idx+300])
        break

# Also search for "按地区" in table headers
for i, page in enumerate(pdf.pages):
    text = page.extract_text()
    if not text: continue
    if "按地区" in text or "by Region" in text:
        print(f"\n=== Page {i+1} (按地区/by Region) ===")
        print(text[:500])
        break

pdf.close()
