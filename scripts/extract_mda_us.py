# -*- coding: utf-8 -*-
"""
extract_mda_us.py — SEC 10-K HTML → MD&A 文本提取
从 SEC EDGAR 下载的 10-K HTML 年报中提取 Item 7 (MD&A) 和 Item 1 (Business)。

输出:
  - meta.mda_text: MD&A 全文 (Item 7)
  - meta.business_text: 业务描述 (Item 1)
  - meta.mda_extracted_year: 提取年份

用法: python scripts/extract_mda_us.py GOOGL
"""
import html, os, re, sqlite3, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config


def _html_to_text(html_content: str) -> str:
    """10-K HTML → 纯文本 (去除标签、实体解码、压缩空白)"""
    # 移除 script / style 标签
    text = re.sub(r'<(script|style)[^>]*>.*?</\1>', '', html_content, flags=re.S | re.I)
    # 移除 HTML 标签
    text = re.sub(r'<[^>]+>', ' ', text)
    # HTML 实体解码
    text = html.unescape(text)
    # 替换 &nbsp; 等
    text = text.replace('\xa0', ' ').replace('&nbsp;', ' ')
    # 压缩多余空白
    text = re.sub(r'\s+', ' ', text)
    # 按常见句子结束符分行
    text = re.sub(r'([.?!])\s+', r'\1\n', text)
    return text.strip()


def _extract_section(text: str, start_pattern: str, end_pattern: str = None) -> str:
    """从纯文本中提取指定章节"""
    m_start = re.search(start_pattern, text, re.I)
    if not m_start:
        return ""
    start_pos = m_start.start()

    if end_pattern:
        m_end = re.search(end_pattern, text[start_pos:], re.I)
        if m_end:
            return text[start_pos:start_pos + m_end.start()].strip()
    return text[start_pos:].strip()


def extract_10k_mda(html_path: str) -> dict:
    """从单个 10-K HTML 文件中提取 MD&A 和 Business 章节
    返回 {"item1": "...", "item7": "...", "year": "2025"}
    """
    with open(html_path, "r", encoding="utf-8", errors="replace") as f:
        raw = f.read()

    text = _html_to_text(raw)

    # 提取年份 (从文件名或内容)
    year_match = re.search(r'(\d{4})[-/]\d{2}[-/]\d{2}', os.path.basename(html_path))
    year = year_match.group(1) if year_match else ""

    # Item 1: Business description
    item1 = _extract_section(text,
        r'ITEM\s+1[\.\s].*?BUSINESS',
        r'ITEM\s+1A[\.\s].*?RISK\s*FACTORS')

    # Item 7: MD&A
    item7 = _extract_section(text,
        r'ITEM\s+7[\.\s].*?(?:MANAGEMENT.S?\s*DISCUSSION|MD\s*&?\s*A)',
        r'ITEM\s+7A[\.\s].*?(?:QUANTITATIVE|MARKET\s*RISK)')

    # 截断过长文本 (引擎只需要 ~5000-10000 chars)
    if item1 and len(item1) > 10000:
        item1 = item1[:10000]
    if item7 and len(item7) > 15000:
        item7 = item7[:15000]

    return {"item1": item1, "item7": item7, "year": year}


def main(code="GOOGL"):
    stock = config.STOCKS.get(code, {})
    if stock.get("market") != "us":
        print(f"{code} 不是美股")
        return

    pdf_dir = config.pdf_dir(code)
    db_path = config.db_path(code)

    # 找最新的 10-K 文件
    k10_files = sorted(
        [f for f in os.listdir(pdf_dir) if "10K" in f and f.endswith(".htm")],
        reverse=True)
    if not k10_files:
        print("未找到 10-K 文件")
        return

    latest = k10_files[0]
    html_path = os.path.join(pdf_dir, latest)
    print(f"  提取 {latest} ...")

    result = extract_10k_mda(html_path)

    if not result["item7"] and not result["item1"]:
        print(f"  警告: 未能提取到 MD&A 或 Business 章节")
        return

    conn = sqlite3.connect(db_path)
    conn.execute("CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT)")

    # 保存 MD&A (Item 7)
    if result["item7"]:
        conn.execute("INSERT OR REPLACE INTO meta VALUES (?,?)",
                     ("mda_text", result["item7"]))
        print(f"  mda_text: {len(result['item7'])} chars")

    # 保存 Business (Item 1)
    if result["item1"]:
        conn.execute("INSERT OR REPLACE INTO meta VALUES (?,?)",
                     ("business_text", result["item1"]))
        print(f"  business_text: {len(result['item1'])} chars")

    # 保存提取年份
    conn.execute("INSERT OR REPLACE INTO meta VALUES (?,?)",
                 ("mda_extracted_year", result["year"]))
    conn.commit()
    conn.close()
    print(f"  OK (FY{result['year']})")


if __name__ == "__main__":
    code = sys.argv[1] if len(sys.argv) > 1 else "GOOGL"
    main(code)
