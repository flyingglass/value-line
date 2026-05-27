"""提取MD&A关键内容用于生成管理层讨论与分析"""
import pdfplumber, re

pdf_path = "C:/LY/Repo/llm/value-line/data/pdfs/09992/09992_2025_年报.pdf"
pdf = pdfplumber.open(pdf_path)

print("=== 提取MD&A关键信息 ===\n")

# 提取业务回顾部分 (约第11-28页)
mdna_text = ""
for i in range(10, 35):  # Page 11-35 (0-indexed)
    if i >= len(pdf.pages):
        break
    text = pdf.pages[i].extract_text()
    if text and ("MANAGEMENT DISCUSSION" in text or "管理層討論" in text or "業務回顧" in text or "BUSINESS REVIEW" in text):
        mdna_text += text + "\n"

pdf.close()

# 提取关键信息
print("1. 业绩亮点:")
# 收入增长率
m = re.search(r'(\d+(?:\.\d+)?)%.*?(?:同比|year-on-year)', mdna_text)
if m:
    print(f"   - 收入同比增长: {m.group(1)}%")

# 全球化
if "global" in mdna_text.lower() or "全球" in mdna_text:
    print("   - 全球化进程提速")

# IP表现
if "THE MONSTERS" in mdna_text:
    print("   - THE MONSTERS IP表现突出")

if "毛絨" in mdna_text or "plush" in mdna_text.lower():
    print("   - 毛绒产品成为增长主力")

print("\n2. 分地区表现:")
# 中国
m = re.search(r'中國.*?(?:增長|increased).*?(\d+(?:\.\d+)?)%', mdna_text)
if m:
    print(f"   - 中国市场: +{m.group(1)}%")

# 亚太
m = re.search(r'亞太.*?(?:增長|increased).*?(\d+(?:\.\d+)?)%', mdna_text)
if m:
    print(f"   - 亚太市场: +{m.group(1)}%")

# 美洲
m = re.search(r'美洲.*?(?:增長|increased).*?(\d+(?:\.\d+)?)%', mdna_text)
if m:
    print(f"   - 美洲市场: +{m.group(1)}%")

print("\n3. 战略重点:")
keywords = ["IP運營", "IP运营", "product", "產品", "global", "全球", "channel", "渠道", "online", "線上"]
for kw in keywords[:5]:
    if kw in mdna_text:
        print(f"   - 提及: {kw}")

print("\n4. 未来展望:")
if "未來" in mdna_text or "future" in mdna_text.lower():
    # 找包含"未來"的句子
    idx = mdna_text.find("未來")
    if idx > 0:
        snippet = mdna_text[idx:idx+200]
        print(f"   {snippet[:150]}...")

print("\n=== MD&A文本片段 ===")
print(mdna_text[:2000])
