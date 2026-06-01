"""
extract_mda.py — 生成管理层讨论与分析(MD&A)中文总结
策略: PDF文本提取 → 质量评分 → 低质量用财务数据动态生成
通用版本: 无硬编码公司信息, 兼容所有A股/港股年报
"""
import pdfplumber, re, sqlite3, sys, json, os
sys.path.insert(0, ".")
import config


def _numeric_ratio(text):
    """计算文本中数字/日期/货币字符的密度 (0~1)"""
    if not text:
        return 0
    numeric = len(re.findall(r'[\d.%%万亿千百港元美人民币亿兆]', text))
    return numeric / max(len(text), 1)


def _is_narrative(s, max_ratio=0.22):
    """判断句子是否为叙事性文本 (非财务数据句)"""
    # 财务数据句特征: 高数字密度 + 增长率/同比/环比等关键词
    finance_terms = ["增长", "下降", "同比", "环比", "增加", "减少",
                     "上升", "下跌", "扩大", "收缩", "变动", "波动"]
    num_ratio = _numeric_ratio(s)
    if num_ratio > max_ratio:
        return False
    # 含>=2个财务术语 + 高数字密度 → 数据句
    fin_count = sum(1 for t in finance_terms if t in s)
    if fin_count >= 2 and num_ratio > 0.12:
        return False
    return True


def extract_chinese_sentences(text):
    """从PDF文本中提取叙事性中文句子（>20中文字符，过滤财务数据句）"""
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
        if len(p) <= 25:
            continue
        # 过滤财务数据句 (通用, 不绑定公司)
        if not _is_narrative(p):
            continue
        results.append(p)
    return results


def _score_sentence(s, keywords):
    """给句子对某分类的匹配度打分 (通用关键词)"""
    score = 0
    for kw in keywords:
        if kw in s:
            score += 1
    # 长句更可能是完整叙事
    if len(s) > 50:
        score += 0.5
    # 惩罚高数字密度
    nr = _numeric_ratio(s)
    if nr > 0.15:
        score -= 1
    if nr > 0.10:
        score -= 0.5
    return score


def classify_sentences(sentences):
    """打分分类: 每句归入得分最高的类别 (通用关键词, 不绑定公司)"""
    categories = {
        "overview": ["业务", "经营", "公司", "本集团", "市场地位"],
        "product":  ["产品", "服務", "服务", "IP", "品类", "品牌", "平台", "内容"],
        "channel":  ["渠道", "门店", "线上", "零售", "会员", "用户", "流量", "活跃"],
        "region":   ["中国", "海外", "国际", "亚太", "美洲", "欧洲", "全球", "地区", "境内", "境外"],
        "cost":     ["成本", "费用", "效率", "研发", "技术", "创新", "人才", "组织"],
        "outlook":  ["展望", "未来", "战略", "布局", "目标", "计划", "方向", "愿景", "使命"],
    }

    sections = {k: [] for k in categories}
    quality = {k: 0 for k in categories}  # 每个类别匹配的句数

    for s in sentences:
        best_cat, best_score = None, -99
        for cat, kws in categories.items():
            sc = _score_sentence(s, kws)
            if sc > best_score:
                best_score = sc
                best_cat = cat
        if best_cat and best_score >= 0.5:
            sections[best_cat].append(s)
            quality[best_cat] += 1

    return sections, quality


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
    quality_ok = False

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
        print(f"  提取叙事句: {len(extracted)}")

        sections, quality = classify_sentences(extracted)
        total = sum(quality.values())
        print(f"  分类: {quality} (共{total}句)")

        # 质量评分: 覆盖≥3个类别 + 总句数≥10 + overview不能一家独大
        categories_covered = sum(1 for v in quality.values() if v > 0)
        overview_pct = quality.get("overview", 0) / max(total, 1)
        quality_ok = (categories_covered >= 3 and total >= 10
                      and overview_pct < 0.70)  # overview >70% → 分类太偏

        if quality_ok:
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

    # Fallback: PDF提取不足 → 从数据动态生成
    if not mda_text or len(mda_text) < 300:
        print("  -> PDF提取不足(或过短)，使用财务数据动态生成")
        fallback = build_mda_from_data(code)
        if fallback:
            mda_text = fallback
            quality_ok = False
        else:
            # report_data.json 不存在 (Step 3 在 engine 之前运行)
            print("  -> 动态生成也失败(report_data.json不存在)，保留PDF提取并标记低质量")
            quality_ok = False

    if not mda_text:
        print("  [ERROR] 无法生成MD&A文本")
        return

    db_path = config.db_path(code)
    conn = sqlite3.connect(db_path)
    conn.execute("CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT)")
    conn.execute("INSERT OR REPLACE INTO meta VALUES (?,?)", ("mda_text", mda_text))
    conn.execute("INSERT OR REPLACE INTO meta VALUES (?,?)", ("mda_quality", "1" if quality_ok else "0"))
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
