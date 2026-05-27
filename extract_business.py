"""从年报PDF提取业务简介和员工人数"""
import pdfplumber

pdf_path = "C:/LY/Repo/llm/value-line/data/pdfs/09992/09992_2025_年报.pdf"
pdf = pdfplumber.open(pdf_path)

# Extract MD&A section first page (page 11 in PDF = index 10)
page = pdf.pages[10]
text = page.extract_text()
print("=== MD&A First Page (Business Review) ===")
print(text[:1000])
print()

# Search for employee numbers in the whole PDF
print("=== Searching for employee/雇员 info... ===")
for i, page in enumerate(pdf.pages):
    text = page.extract_text()
    if not text: continue
    if any(kw in text for kw in ["雇员", "员工", "employee", "Employee", "人数", "headcount"]):
        # Find and print the relevant snippet
        for kw in ["雇员", "员工", "employee", "Employee"]:
            if kw in text:
                idx = text.find(kw)
                print(f"\n--- Page {i+1}: [{kw}] ---")
                print(text[max(0,idx-50):idx+300])
                break

pdf.close()
