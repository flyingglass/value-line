"""
extract_pdf_metadata.py — 从年报PDF提取业务描述+员工人数，存入SQLite
通用版本: 无硬编码公司信息，全部从 config 和 PDF 自动提取
"""
import pdfplumber, sqlite3, re, sys, json, os
sys.path.insert(0, ".")
import config


def extract_business_desc_from_pdf(pages_text):
    """从PDF逐页搜索业务相关段落，返回首段>50个中文字符的文本"""
    # 多种搜索模式: 港版繁体、简体、英文
    patterns = [
        (u"業務回顧", 5),     # 港版年报常用
        (u"业务回顾", 5),     # 简体版
        (u"Management Discussion", 0),
        (u"管理层讨论", 5),
        (u"主席報告", 5),
        (u"董事长致辞", 5),
        (u"Chairman", 0),
    ]
    for keyword, offset in patterns:
        for pnum, text in pages_text:
            idx = text.find(keyword)
            if idx < 0:
                continue
            after = text[idx + len(keyword):]
            blocks = after.split('\n\n')
            for block in blocks:
                cn_chars = len(re.findall(r'[\u4e00-\u9fff]', block))
                if cn_chars < 50:
                    continue
                # 清理: 去英文、保留中文
                lines = block.split('\n')
                cn_lines = []
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    cn = len(re.findall(r'[\u4e00-\u9fff]', line))
                    en = len(re.findall(r'[a-zA-Z]', line))
                    if cn > 20 and cn > en:
                        clean = re.sub(r'[a-zA-Z0-9\'\"\s,;:!?.()（）\[\]]+', '', line)
                        clean = clean.strip()
                        if len(clean) > 15:
                            cn_lines.append(clean)
                if cn_lines:
                    return "。".join(cn_lines[:4])
    return None


def extract_employee_count(full_text):
    """从年报提取员工总数，取最大值（年报多处提及）"""
    counts = set()
    patterns = [
        r'(?:共有|合計|共计|约|擁有|拥有)\s*([\d,]+)\s*(?:名|位|人)?\s*(?:僱員|員工|雇员|员工)',
        r'(?:僱員|員工|雇员|员工)\s*(?:人數|人数|總數|总数|规模|規模)[^0-9]*([\d,]+)',
        r'(?:had|have|has)\s+(?:a\s+)?(?:total\s+(?:of\s+)?)?([\d,]+)\s+employees',
        r'total\s+(?:of\s+)?([\d,]+)\s+employees',
        r'(\d{4,6})\s*(?:名|位|人)\s*(?:僱員|員工|雇员|员工)',
        r'([\d,]+)\s+employees',
    ]
    for p in patterns:
        for m in re.finditer(p, full_text, re.IGNORECASE):
            try:
                count = int(m.group(1).replace(",", ""))
                if 100 < count < 2000000:  # 合理范围
                    counts.add(count)
            except:
                pass
    return max(counts) if counts else None


def build_fallback_desc(code):
    """PDF提取失败时，用config数据生成业务描述"""
    stock = config.STOCKS.get(code, {})
    name = stock.get("name", "该公司")
    industry = stock.get("industry", "")
    currency = stock.get("currency", "CNY")

    # 尝试从report_data.json获取基本财务数据
    rp = os.path.join(config.BASE_DIR, "report_data.json")
    desc = f"{name}"
    if industry:
        desc += f"是一家{industry}行业公司"
    desc += "。详情请参阅最新年报。"

    if os.path.exists(rp):
        try:
            with open(rp, encoding='utf-8') as f:
                d = json.load(f)
            yrs = sorted(d.get('data', {}).keys())
            if yrs:
                ly = d['data'][yrs[-1]]
                rev = ly.get('OPERATE_INCOME')
                profit = ly.get('HOLDER_PROFIT')
                roe = ly.get('ROE_AVG')
                parts = [f"{name}"]
                if industry:
                    parts.append(f"是{industry}行业企业")
                if rev:
                    parts.append(f"{yrs[-1]}年营收{rev:.1f}亿元")
                if profit:
                    parts.append(f"归母净利润{profit:.1f}亿元")
                if roe:
                    parts.append(f"ROE {roe:.1f}%")
                desc = "，".join(parts[:-1]) + "，" + parts[-1] + "。"
        except:
            pass
    return desc


def main(code="09992"):
    pdf_dir = config.pdf_dir(code)
    stock = config.STOCKS.get(code, {})
    stock_name = stock.get("name", code)

    import glob
    pdfs = sorted(glob.glob(os.path.join(pdf_dir, f"{code}_*_年报.pdf")), reverse=True)
    if not pdfs:
        print(f"  [WARN] 未找到年报PDF: {code}")
        return

    pdf_path = pdfs[0]
    yr_match = re.search(r'_(\d{4})_年报', os.path.basename(pdf_path))
    fy = yr_match.group(1) if yr_match else "2025"

    print(f"  PDF: {os.path.basename(pdf_path)} (FY{fy})")
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
    business_desc = extract_business_desc_from_pdf(pages_text)
    if not business_desc:
        print("  -> PDF业务描述提取失败，使用数据生成")
        business_desc = build_fallback_desc(code)

    # 提取员工人数
    employee_count = extract_employee_count(full_text)

    # 存入SQLite
    db_path = config.db_path(code)
    conn = sqlite3.connect(db_path)
    conn.execute("CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT)")

    conn.execute("INSERT OR REPLACE INTO meta VALUES (?,?)",
                 ("business_desc", business_desc))
    print(f"  business_desc: {business_desc[:100]}...")

    if employee_count:
        conn.execute("INSERT OR REPLACE INTO meta VALUES (?,?)",
                     ("employee_count", str(employee_count)))
        conn.execute("INSERT OR REPLACE INTO meta VALUES (?,?)",
                     ("employee_year", fy))
        print(f"  employee_count: {employee_count} (FY{fy})")
    else:
        print("  [WARN] 未提取到员工人数")

    conn.commit()
    conn.close()


if __name__ == "__main__":
    code = sys.argv[1] if len(sys.argv) > 1 else None
    if not code:
        code = config.ACTIVE_STOCK
    print(f"提取PDF元数据: {code} ({config.STOCKS.get(code, {}).get('name', '')})")
    main(code)
    print("完成")
