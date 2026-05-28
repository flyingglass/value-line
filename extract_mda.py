"""
extract_mda.py — 生成管理层讨论与分析(MD&A)中文总结
策略: PDF文本提取 → 失败则用财务数据+营收结构动态生成
通用版本: 无硬编码公司信息
"""
import pdfplumber, re, sqlite3, sys, json, os
sys.path.insert(0, ".")
import config


def extract_chinese_sentences(text):
    """从PDF文本中提取中文句子（>20中文字符，过滤表头/英文）"""
    parts = re.split(r'[。！？\n]', text)
    results = []
    for p in parts:
        p = p.strip()
        cn = len(re.findall(r'[\u4e00-\u9fff]', p))
        if cn < 20:
            continue
        # 过滤英文残留、表头
        p = re.sub(r'\b[a-zA-Z][a-zA-Z0-9\'.,;:!?\d\-/\s()（）\[\]]*\b', '', p)
        p = p.strip()
        if ';(' in p or '),(' in p or len(re.findall(r'[；;]', p)) > 2:
            continue
        if len(p) > 25:
            results.append(p)
    return results


def classify_sentences(sentences):
    """通用关键词分类（不绑定任何公司）"""
    sections = {
        "overview": [],
        "product": [],
        "channel": [],
        "region": [],
        "cost": [],
        "outlook": [],
    }
    for s in sentences:
        if any(k in s for k in ["展望", "未來", "布局", "戰略", "策略", "将", "將"]):
            sections["outlook"].append(s)
        elif any(k in s for k in ["渠道", "门店", "線上", "電商", "电商", "会员", "會員", "零售"]):
            sections["channel"].append(s)
        elif any(k in s for k in ["中國", "海外", "亞太", "美洲", "歐洲", "地区", "地區", "市場"]):
            sections["region"].append(s)
        elif any(k in s for k in ["产品", "產品", "品類", "品类", "品牌"]):
            sections["product"].append(s)
        elif any(k in s for k in ["成本", "開支", "毛利率", "費用", "效率", "运营", "運營"]):
            sections["cost"].append(s)
        else:
            sections["overview"].append(s)
    return sections


def build_mda_from_data(code):
    """基于财务数据+营收结构，动态生成通用MD&A文本"""
    rp = os.path.join(config.BASE_DIR, "report_data.json")
    if not os.path.exists(rp):
        return None

    with open(rp, encoding='utf-8') as f:
        d = json.load(f)

    stock = config.STOCKS.get(code, {})
    name = stock.get("name", "该公司")
    mt = d.get('data', {})
    rev = d.get('revenue_structure', {})
    yrs = sorted(mt.keys())

    if len(yrs) < 2:
        return None

    ly = yrs[-1]
    py = yrs[-2]
    lyd = mt[ly]
    pyd = mt[py]

    # 增长率
    rev_yoy = ((lyd.get('OPERATE_INCOME', 0) / pyd.get('OPERATE_INCOME', 1)) - 1) * 100 if pyd.get('OPERATE_INCOME') else 0
    np_yoy = ((lyd.get('HOLDER_PROFIT', 0) / pyd.get('HOLDER_PROFIT', 1)) - 1) * 100 if pyd.get('HOLDER_PROFIT') else 0
    eps_yoy = ((lyd.get('BASIC_EPS', 0) / pyd.get('BASIC_EPS', 1)) - 1) * 100 if pyd.get('BASIC_EPS') else 0
    yoy_dir = "增长" if rev_yoy >= 0 else "下降"

    parts = []

    # 1. 经营总览
    parts.append("【经营总览】")
    lines = [f"{ly}年{name}实现营收{lyd.get('OPERATE_INCOME', 0):.1f}亿元，同比{yoy_dir}{abs(rev_yoy):.1f}%"]
    if lyd.get('HOLDER_PROFIT'):
        lines.append(f"归母净利润{lyd['HOLDER_PROFIT']:.1f}亿元，同比{yoy_dir}{abs(np_yoy):.1f}%")
    if lyd.get('ROE_AVG'):
        lines.append(f"ROE达{lyd['ROE_AVG']:.1f}%")
    if lyd.get('BASIC_EPS'):
        lines.append(f"每股收益¥{lyd['BASIC_EPS']:.2f}")
    if lyd.get('OP_MARGIN'):
        lines.append(f"经营利润率{lyd['OP_MARGIN']:.1f}%")
    parts.append("，".join(lines) + "。")
    parts.append("")

    # 2. 产品/业务
    ip_data = rev.get('by_ip', [])
    ch_data = rev.get('by_channel', [])
    rg_data = rev.get('by_region', [])

    if ip_data:
        parts.append("【产品/业务结构】")
        top_items = ip_data[:3]
        ip_str = "、".join([f"{x['name']}({x['pct']}%)" for x in top_items])
        parts.append(f"核心业务来源：{ip_str}。")
        parts.append("")

    # 3. 渠道
    if ch_data:
        parts.append("【渠道发展】")
        ch_str = "、".join([f"{c['name']}({c['pct']}%)" for c in ch_data[:3]])
        parts.append(f"渠道结构：{ch_str}。")
        parts.append("")

    # 4. 分地区
    if rg_data:
        parts.append("【分地区表现】")
        rg_str = "，".join([f"{r['name']}占{r['pct']}%" for r in rg_data])
        parts.append(f"收入区域分布：{rg_str}。")
        overseas_total = sum(r['pct'] for r in rg_data if r['name'] != '中国')
        if overseas_total > 0:
            parts.append(f"海外市场收入占比{overseas_total:.1f}%。")
        parts.append("")

    # 5. 成本与效率
    parts.append("【成本与效率】")
    eff_lines = []
    if lyd.get('DEPRECIATION'):
        eff_lines.append(f"折旧摊销{lyd['DEPRECIATION']:.1f}亿元")
    if lyd.get('WORKING_CAPITAL'):
        eff_lines.append(f"营运资金{lyd['WORKING_CAPITAL']:.1f}亿元")
    if eff_lines:
        parts.append("，".join(eff_lines) + "。")

    # 员工信息
    db_path = config.db_path(code)
    conn = sqlite3.connect(db_path)
    emp = conn.execute("SELECT value FROM meta WHERE key='employee_count'").fetchone()
    conn.close()
    if emp:
        emp_n = int(emp[0])
        parts.append(f"员工规模{emp_n/10000:.1f}万人。")
    parts.append("")

    # 6. 未来展望
    parts.append("【未来展望】")
    parts.append(f"{name}将继续坚持核心战略，深化业务布局与运营效率提升。")
    parts.append("持续推动产品创新与市场拓展，把握行业发展趋势。")
    parts.append("致力于为股东创造长期可持续价值。")

    return "\n".join(parts)


def main(code="09992"):
    pdf_dir = config.pdf_dir(code)
    stock = config.STOCKS.get(code, {})
    name = stock.get("name", code)

    import glob
    pdfs = sorted(glob.glob(os.path.join(pdf_dir, f"{code}_*_年报.pdf")), reverse=True)

    mda_text = None

    # 尝试从PDF提取
    if pdfs:
        pdf_path = pdfs[0]
        print(f"  PDF: {os.path.basename(pdf_path)}")
        pdf = pdfplumber.open(pdf_path)
        full_text = ""
        for pn in range(10, min(80, len(pdf.pages))):
            text = pdf.pages[pn].extract_text()
            if text:
                full_text += text + "\n"
        pdf.close()

        extracted = extract_chinese_sentences(full_text)
        print(f"  提取中文句: {len(extracted)}")

        sections = classify_sentences(extracted)
        total = sum(len(v) for v in sections.values())
        print(f"  分类: {dict((k, len(v)) for k, v in sections.items() if v)}")

        if total >= 6:
            titles = {
                "overview": "【经营总览】", "product": "【产品/业务结构】",
                "channel": "【渠道发展】", "region": "【分地区表现】",
                "cost": "【成本与效率】", "outlook": "【未来展望】"
            }
            parts = []
            for key in ["overview", "product", "channel", "region", "cost", "outlook"]:
                if sections[key]:
                    parts.append(titles[key])
                    parts.extend(sections[key][:5])
                    parts.append("")
            mda_text = "\n".join(parts)

    # Fallback: 从数据动态生成
    if not mda_text or len(mda_text) < 400:
        print("  -> PDF提取不足，使用财务数据动态生成")
        mda_text = build_mda_from_data(code)

    if not mda_text:
        print("  [ERROR] 无法生成MD&A文本")
        return

    db_path = config.db_path(code)
    conn = sqlite3.connect(db_path)
    conn.execute("CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT)")
    conn.execute("INSERT OR REPLACE INTO meta VALUES (?,?)", ("mda_text", mda_text))
    conn.commit()
    conn.close()

    print(f"\n=== MDA预览 ({len(mda_text)}字符) ===")
    print(mda_text[:400])
    print("...")
    print("完成")


if __name__ == "__main__":
    code = sys.argv[1] if len(sys.argv) > 1 else None
    if not code:
        code = config.ACTIVE_STOCK
    print(f"提取MD&A: {code} ({config.STOCKS.get(code, {}).get('name', '')})")
    main(code)
