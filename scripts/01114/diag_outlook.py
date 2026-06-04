"""
诊断 01114 年报 PDF 的展望文本提取能力
"""
import pdfplumber, re, os, sys, io
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Fix encoding for Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

pdf_path = r"c:\LY\Repo\llm\value-line\data\pdfs\01114\01114_2025_年报.pdf"
if not os.path.exists(pdf_path):
    print(f"FILE NOT FOUND: {pdf_path}")
    sys.exit(1)

pdf = pdfplumber.open(pdf_path)
print(f"Total pages: {len(pdf.pages)}\n")

# 1) Page scan: which pages have outlook keywords
outlook_kw = ["展望", "未来", "前景", "策略", "计划", "战略", "发展目标", "经营计划"]
print("=== PAGE KEYWORD SCAN ===")
for pn in range(len(pdf.pages)):
    text = pdf.pages[pn].extract_text() or ""
    hits = [kw for kw in outlook_kw if kw in text]
    if hits:
        cn = len(re.findall(r'[\u4e00-\u9fff]', text))
        print(f"  Page{pn+1}: hits={hits}  (CN chars: {cn})")

# 2) Extract paragraphs with "outlook" keywords from pages 40-80
print("\n=== PAGES 40-80: PARAGRAPHS WITH OUTLOOK/FUTURE/STRATEGY ===")
for pn in range(39, min(80, len(pdf.pages))):
    text = pdf.pages[pn].extract_text() or ""
    paragraphs = re.split(r'\n\s*\n', text)
    for par in paragraphs:
        par = par.strip()
        cn = len(re.findall(r'[\u4e00-\u9fff]', par))
        if cn < 15:
            continue
        if any(kw in par for kw in ["展望", "未来", "战略"]):
            print(f"\n--- Page {pn+1} ---")
            # Print safely, replace problematic chars
            safe = par[:800].encode('utf-8', errors='replace').decode('utf-8', errors='replace')
            print(safe)

# 3) All CN paragraphs >50 chars from pages 50-65
print("\n\n=== PAGES 50-65: ALL CN PARAGRAPHS (>50 chars) ===")
for pn in range(49, min(65, len(pdf.pages))):
    text = pdf.pages[pn].extract_text() or ""
    paragraphs = re.split(r'\n\s*\n', text)
    for par in paragraphs:
        par = par.strip()
        cn = len(re.findall(r'[\u4e00-\u9fff]', par))
        if cn > 50:
            print(f"\n--- Page {pn+1} (CN chars: {cn}) ---")
            safe = par[:500].encode('utf-8', errors='replace').decode('utf-8', errors='replace')
            print(safe)

# 4) Now run the actual extract_mda classification
print("\n\n=== ACTUAL extract_mda CLASSIFICATION ===")
from extract_mda import extract_chinese_sentences, classify_sentences

full_text = ""
for pn in range(10, min(80, len(pdf.pages))):
    text = pdf.pages[pn].extract_text() or ""
    full_text += text + "\n"

sentences = extract_chinese_sentences(full_text)
print(f"Extracted narrative sentences: {len(sentences)}")

sections, quality = classify_sentences(sentences)
total = sum(quality.values())
print(f"Classification: {quality} (total: {total})")

categories_covered = sum(1 for v in quality.values() if v > 0)
overview_pct = quality.get("overview", 0) / max(total, 1)
print(f"Categories covered: {categories_covered}/6")
print(f"Overview pct: {overview_pct:.1%}")
print(f"Quality check: {categories_covered >= 3 and total >= 10 and overview_pct < 0.70}")

# Show what's in each category
for cat in ["overview", "product", "channel", "region", "cost", "outlook"]:
    print(f"\n[{cat}] ({len(sections.get(cat, []))} sentences):")
    for s in sections.get(cat, [])[:3]:
        safe = s[:200].encode('utf-8', errors='replace').decode('utf-8', errors='replace')
        print(f"  - {safe}")

pdf.close()
print("\nDone")
