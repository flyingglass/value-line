"""
extract_pdf_metadata.py — 从年报PDF提取业务描述+员工人数，存入SQLite
设计原则：提取一次存数据库，后续直接读库，不再重复解析PDF
"""
import pdfplumber, sqlite3, re, sys
sys.path.insert(0, ".")
import config

# 已知的业务描述（从PDF MD&A首段手动整理，适合各股票修改）
# 对泡泡玛特：2025年年报Management Discussion and Analysis首段
BUSINESS_DESC_FALLBACK = (
    "泡泡玛特是中国领先的潮流文化娱乐公司。"
    "2025年全球化进程进一步提速，品牌知名度持续提升，"
    "IP运营与产品研发能力持续增强，推出多款深受全球消费者欢迎的新IP及新品系列，"
    "推动销售业绩实现高速增长。"
)


def extract_business_desc_by_page(pages_text):
    """逐页找业务回顾后的中文段落"""
    for pnum, text in pages_text:
        if "業務回顧" not in text:
            continue
        # 找到"業務回顧"标记
        idx = text.find("業務回顧")
        after = text[idx + 5:]
        # 取第一个含>30个中文字符的段落
        blocks = after.split('\n\n')
        for block in blocks:
            cn_chars = len(re.findall(r'[\u4e00-\u9fff]', block))
            if cn_chars > 50:
                # 清理英文干扰，只保留中文内容
                lines = block.split('\n')
                cn_lines = []
                for line in lines:
                    line = line.strip()
                    if not line: continue
                    cn = len(re.findall(r'[\u4e00-\u9fff]', line))
                    en = len(re.findall(r'[a-zA-Z]', line))
                    if cn > 30 and cn > en * 2:
                        clean = re.sub(r'[a-zA-Z0-9\'\"\s,;:!?.]+', '', line)
                        cn_lines.append(clean)
                if cn_lines:
                    return "。".join(cn_lines[:3])
    return None


def extract_employee_count(full_text):
    """从年报提取员工总数 - 取最大匹配值（年报通常多处提及）"""
    counts = set()
    patterns = [
        r'we had a total of\s*([\d,]+)\s*employees',
        r'total of\s*([\d,]+)\s*employees',
        r'截至[^。]{0,30}(?:共有|合計)\s*([\d,]+)\s*名\s*(?:僱員|員工)',
        r'(\d{4,5})\s*employees',
    ]
    for p in patterns:
        for m in re.finditer(p, full_text, re.IGNORECASE):
            try:
                counts.add(int(m.group(1).replace(",", "")))
            except:
                pass
    if counts:
        return max(counts)  # 取最大 = 总员工数 (其他可能只是分部)
    return None


def main(code="09992"):
    pdf_dir = config.pdf_dir(code)
    import glob, os
    pdfs = sorted(glob.glob(os.path.join(pdf_dir, f"{code}_*_年报.pdf")), reverse=True)
    if not pdfs:
        print(f"  [WARN] 未找到年报PDF: {code}")
        return

    pdf_path = pdfs[0]
    print(f"  PDF: {os.path.basename(pdf_path)}")
    pdf = pdfplumber.open(pdf_path)

    pages_text = []
    full_text = ""
    for i, page in enumerate(pdf.pages):
        t = page.extract_text()
        if t:
            pages_text.append((i + 1, t))
            full_text += t + "\n"
    pdf.close()

    # 提取业务描述
    business_desc = extract_business_desc_by_page(pages_text)
    if not business_desc:
        print("  [WARN] 自动提取失败，使用手动整理描述")
        business_desc = BUSINESS_DESC_FALLBACK

    # 提取员工人数
    employee_count = extract_employee_count(full_text)

    # 存入SQLite
    db_path = config.db_path(code)
    conn = sqlite3.connect(db_path)
    conn.execute("CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT)")

    conn.execute("INSERT OR REPLACE INTO meta VALUES (?,?)",
                 ("business_desc", business_desc))
    print(f"  business_desc: {business_desc[:80]}...")

    if employee_count:
        conn.execute("INSERT OR REPLACE INTO meta VALUES (?,?)",
                     ("employee_count", str(employee_count)))
        conn.execute("INSERT OR REPLACE INTO meta VALUES (?,?)",
                     ("employee_year", "2025"))
        print(f"  employee_count: {employee_count}")
    else:
        print("  [WARN] 未提取到员工人数")

    conn.commit()
    conn.close()


if __name__ == "__main__":
    code = sys.argv[1] if len(sys.argv) > 1 else "09992"
    print(f"提取PDF元数据: {code}")
    main(code)
    print("完成")
