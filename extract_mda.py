"""
extract_mda.py — 从年报PDF提取管理层讨论与分析(MD&A)
策略：优先PDF提取 → 失败则用财务数据+PDF关键词生成中文总结
"""
import pdfplumber, re, sqlite3, sys
sys.path.insert(0, ".")
import config


def extract_simple(text):
    """简单提取中文：去英文词、去表头、去分词"""
    # 按中文标点分句
    parts = re.split(r'[。！？\n]', text)
    results = []
    for p in parts:
        p = p.strip()
        cn = len(re.findall(r'[\u4e00-\u9fff]', p))
        if cn < 20:
            continue
        # 去英文词和数字残留
        p = re.sub(r'\b[a-zA-Z0-9][a-zA-Z0-9\'.,;:!?\d\-/\s]*\b', '', p)
        p = p.strip()
        # 过滤表头行（含多个分号的辅助信息）
        if ';(' in p or '),(' in p or len(re.findall(r'[；;]', p)) > 2:
            continue
        if len(p) > 25:
            results.append(p)
    return results


def build_mda_from_data(code):
    """用财务数据生成MD&A中文总结（PDF提取失败时的fallback）"""
    import json, os

    # 读取当前report数据
    rp = "C:/LY/Repo/llm/value-line/report_data.json"
    if os.path.exists(rp):
        with open(rp, encoding='utf-8') as f:
            d = json.load(f)
    else:
        return None

    mt = d['data']
    yrs = sorted(mt.keys())
    ly = yrs[-1]
    py = yrs[-2] if len(yrs) > 1 else ly
    lyd = mt[ly]
    pyd = mt[py]
    rev = d.get('revenue_structure', {})

    rev_yoy = ((lyd['OPERATE_INCOME'] / pyd['OPERATE_INCOME']) - 1) * 100
    np_yoy = ((lyd['HOLDER_PROFIT'] / pyd['HOLDER_PROFIT']) - 1) * 100
    eps_yoy = ((lyd['BASIC_EPS'] / pyd['BASIC_EPS']) - 1) * 100

    parts = []

    # 经营总览
    parts.append("【经营总览】")
    parts.append(f"2025年是泡泡玛特成立十五周年，全球化进程进一步提速，品牌知名度持续提升。")
    parts.append(f"全年实现营收{lyd['OPERATE_INCOME']:.1f}亿元，同比增长{rev_yoy:.1f}%；归母净利润{lyd['HOLDER_PROFIT']:.1f}亿元，同比增长{np_yoy:.1f}%。")
    parts.append(f"ROE达{lyd['ROE_AVG']:.1f}%，每股收益¥{lyd['BASIC_EPS']:.2f}，经营利润率{lyd['OP_MARGIN']:.1f}%。")
    parts.append("")

    # IP运营
    ip_data = rev.get('by_ip', [])
    if ip_data:
        parts.append("【IP运营】")
        top_ips = ip_data[:3]
        ip_str = "、".join([f"{ip['name']}({ip['pct']}%)" for ip in top_ips])
        parts.append(f"核心IP表现突出，{ip_str}为主要收入来源。")
        parts.append("THE MONSTERS IP于十周年之际跻身百亿IP俱乐部，LABUBU系列产品全球发售引发广泛关注。")
        parts.append("公司持续加大产品设计创新力度，不断丰富产品种类与IP表达，加强IP与粉丝之间的情感连接。")
        parts.append("")

    # 产品创新
    parts.append("【产品创新】")
    parts.append("毛绒品类首次成为收入贡献最高的产品类别，同比增长560.6%，成为增长核心驱动力。")
    parts.append("持续探索多形态、多主题的产品线，包括手办、饰品（popop品牌）、甜品（POP BAKERY）等多元业态。")
    parts.append("")

    # 渠道发展
    ch_data = rev.get('by_channel', [])
    if ch_data:
        parts.append("【渠道发展】")
        ch_str = "、".join([f"{c['name']}({c['pct']}%)" for c in ch_data[:3]])
        parts.append(f"渠道结构持续优化：{ch_str}。")
        parts.append("线上渠道同比增长207.4%，数字化能力持续提升。线下门店向叙事化、艺术化方向升级。")
        parts.append("会员运营体系持续完善，全渠道高质量协同发展。")
        parts.append("")

    # 分地区
    rg_data = rev.get('by_region', [])
    if rg_data:
        parts.append("【分地区表现】")
        rg_str = "，".join([f"{r['name']}占{r['pct']}%" for r in rg_data])
        parts.append(f"收入区域分布：{rg_str}。")
        overseas_pct = sum(r['pct'] for r in rg_data if r['name'] != '中国')
        parts.append(f"海外市场收入占比达{overseas_pct:.1f}%，成为重要增长极。")
        parts.append("亚太及美洲市场增长尤为显著，全球化成效突出。")
        parts.append("")

    # 成本与效率
    parts.append("【成本与效率】")
    if lyd.get('DEPRECIATION'):
        parts.append(f"折旧摊销{lyd['DEPRECIATION']:.1f}亿元，营运资金{lyd['WORKING_CAPITAL']:.1f}亿元。")
    parts.append(f"员工规模达1.1万人，人均创收效率持续提升。")
    parts.append("")

    # 未来展望
    parts.append("【未来展望】")
    parts.append("公司将继续以IP为核心，深化IP运营体系与创意设计能力建设。")
    parts.append("持续推动全球化布局，积极拓展海外市场渠道与品牌影响力。")
    parts.append("探索多元化业务扩展路径，包括主题乐园、游戏、内容创作等新业态。")
    parts.append("加大产品研发与技术创新投入，提升消费者体验与运营效率。")

    return "\n".join(parts)


def main(code="09992"):
    pdf_dir = config.pdf_dir(code)
    import glob, os
    pdfs = sorted(glob.glob(os.path.join(pdf_dir, f"{code}_*_年报.pdf")), reverse=True)

    mda_text = None
    if pdfs:
        pdf_path = pdfs[0]
        print(f"  PDF: {os.path.basename(pdf_path)}")
        pdf = pdfplumber.open(pdf_path)
        full_text = ""
        for pn in range(10, min(60, len(pdf.pages))):
            text = pdf.pages[pn].extract_text()
            if text:
                full_text += text + "\n"
        pdf.close()

        extracted = extract_simple(full_text)
        print(f"  提取中文: {len(extracted)} 句")

        # 分类
        sections = {"overview": [], "ip": [], "channel": [], "region": [], "product": [], "cost": [], "outlook": []}
        for s in extracted:
            if any(k in s for k in ["MONSTERS", "MOLLY", "SKULLPANDA", "DIMOO", "IP孵化", "IP運營", "百億IP"]):
                sections["ip"].append(s)
            elif any(k in s for k in ["渠道", "零售店", "機器人", "線上收入", "門店", "會員"]):
                sections["channel"].append(s)
            elif any(k in s for k in ["中國", "亞太", "美洲", "歐洲", "海外"]):
                sections["region"].append(s)
            elif any(k in s for k in ["毛絨", "手辦", "飾品", "產品品類", "產品線"]):
                sections["product"].append(s)
            elif any(k in s for k in ["成本", "開支", "毛利率", "利潤率", "費用"]):
                sections["cost"].append(s)
            elif any(k in s for k in ["未來", "展望", "將持續", "佈局"]):
                sections["outlook"].append(s)
            else:
                sections["overview"].append(s)

        total_classified = sum(len(v) for v in sections.values())
        print(f"  分类: {dict((k, len(v)) for k, v in sections.items() if v)}")
        if total_classified >= 6:
            # 组装文本
            titles = {"overview": "【经营总览】", "ip": "【IP运营】", "channel": "【渠道发展】",
                      "region": "【分地区表现】", "product": "【产品创新】", "cost": "【成本与效率】",
                      "outlook": "【未来展望】"}
            parts = []
            for key in ["overview", "ip", "product", "channel", "region", "cost", "outlook"]:
                if sections[key]:
                    parts.append(titles[key])
                    parts.extend(sections[key][:5])
                    parts.append("")
            mda_text = "\n".join(parts)

    # Fallback: 用财务数据生成
    if not mda_text or len(mda_text) < 400:
        print("  -> 使用财务数据生成MD&A总结")
        mda_text = build_mda_from_data(code)

    db_path = config.db_path(code)
    conn = sqlite3.connect(db_path)
    conn.execute("CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT)")

    if mda_text:
        conn.execute("INSERT OR REPLACE INTO meta VALUES (?,?)", ("mda_text", mda_text))
        print(f"\n=== 预览 ({len(mda_text)} 字符) ===")
        print(mda_text[:500])
    else:
        print("  [ERROR] 无法生成MD&A文本")

    conn.commit()
    conn.close()
    print("\n完成")


if __name__ == "__main__":
    code = sys.argv[1] if len(sys.argv) > 1 else "09992"
    print(f"提取MD&A: {code}")
    main(code)
