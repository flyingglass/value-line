# -*- coding: utf-8 -*-
"""批量生成 business_commentary.py + metric_adjustment.py + extract_business.py"""
import os, sys
sys.path.insert(0, '.')
import config

# 只处理仅含 insert_revenue.py 的标的
SCRIPT_DIR = 'scripts'
targets = []

for code in sorted(config.STOCKS):
    d = os.path.join(SCRIPT_DIR, code)
    if not os.path.isdir(d): continue
    files = [f for f in os.listdir(d) if f.endswith('.py') and not f.startswith('__')]
    if files == ['insert_revenue.py']:
        targets.append(code)

print(f"目标: {len(targets)} 只")

BC = """# -*- coding: utf-8 -*-
\"\"\"{} {} — VL Business + AI Commentary (数据驱动)\"\"\"
def build(stock, metrics, revenue_structure, years, cagr, spot):
    latest_yr = years[-1] if years else "2025"
    ly = metrics.get(latest_yr, {{}})
    prev_yr = years[-2] if len(years) >= 2 else None
    py = metrics.get(prev_yr, {{}}) if prev_yr else {{}}

    def _dir(cur, prev):
        if not cur or not prev or prev <= 0: return ""
        c = (cur / prev - 1) * 100
        return "增长" if c > 0 else ("下降" if c < 0 else "持平")

    rev = ly.get("OPERATE_INCOME"); np_val = ly.get("HOLDER_PROFIT")
    eps = ly.get("BASIC_EPS"); gm = ly.get("GROSS_MARGIN")
    npm = ly.get("NET_PROFIT_RATIO"); roe = ly.get("ROE")
    roce = ly.get("ROIC"); per_cf = ly.get("PER_NETCASH")
    dps = ly.get("DPS") or 0; payout = ly.get("PAYOUT_RATIO")
    per_capex = ly.get("CAPEX_PS") or 0
    rev_prev = py.get("OPERATE_INCOME")
    rev_chg = (rev / rev_prev - 1) * 100 if rev and rev_prev and rev_prev > 0 else None

    desc = stock.get("business_desc", "")
    biz = f"{{desc}} {{latest_yr}}年营收{{rev:.0f}}亿" + (f"（{{_dir(rev, rev_prev)}}{{abs(rev_chg):.1f}}%）" if rev_chg else "") + f"，净利率{{npm:.1f}}%，ROE {{roe:.1f}}%。" if desc else f"{{latest_yr}}年营收{{rev:.0f}}亿，净利率{{npm:.1f}}%，ROE {{roe:.1f}}%。"

    np_prev = py.get("HOLDER_PROFIT")
    np_chg = (np_val / np_prev - 1) * 100 if np_val and np_prev and np_prev > 0 else None

    p1 = f"{{latest_yr}}年营收约{{rev:.0f}}亿元" + (f"（{{_dir(rev, rev_prev)}}{{abs(rev_chg):.1f}}%）" if rev_chg else "") + f"，扣非净利润约{{np_val:.1f}}亿元" + (f"（{{_dir(np_val, np_prev)}}{{abs(np_chg):.1f}}%）" if np_chg else "") + f"。毛利率{{gm:.1f}}%，净利率{{npm:.1f}}%。"

    net_ps = round(per_cf - per_capex - dps, 2) if per_cf else None
    p2 = f"每股收益\\u00a5{{eps:.2f}}。每股现金流\\u00a5{{per_cf:.2f}}，资本支出\\u00a5{{per_capex:.2f}}，现金分红\\u00a5{{dps:.2f}}" + (f"（支付率{{payout:.0f}}%）" if payout else "") + (f"，净留存\\u00a5{{net_ps:.2f}}/股" if net_ps else "") + "。"

    p3 = f"毛利率{{gm:.1f}}%、净利率{{npm:.1f}}%、ROE {{roe:.1f}}%。" + (f"ROIC {{roce:.1f}}%。" if roce else "") + "关注行业竞争格局与成本端变化。"

    pe = spot.get("pe", 0) or 0; pb = spot.get("pb", 0) or 0
    div_yield = spot.get("div_yield", 0) or 0
    p4 = f"当前PE约{{pe:.1f}}倍，PB约{{pb:.1f}}倍，股息率约{{div_yield:.2f}}%。关注盈利增长与估值匹配度。"

    p5 = f"关注{{latest_yr}}年报及次年季报趋势作为验证信号。"

    return {{"business": biz, "commentary": [p1, p2, p3, p4, p5]}}
"""

CN_ADJ = '''# -*- coding: utf-8 -*-
"""{name} {code} — A股EPS调整: CAS扣非已处理非经常项目"""
def adjust_metrics(reader, rd, np_val, tax_rate, stock_cfg):
    footnotes = []
    if np_val is None: return None, footnotes
    deducted = reader.financial_item("income", "*扣除非经常性损益后的净利润", rd)
    if deducted and abs(deducted - np_val) > 5e6:
        footnotes.append(f"EPS adj: CD {{deducted/1e8:.1f}} -> VL {{deducted/1e8:.1f}}亿 (归母{{np_val/1e8:.1f}}亿)")
        return deducted, footnotes
    return np_val, footnotes
'''

HK_ADJ = '''# -*- coding: utf-8 -*-
"""{name} {code} — VL EPS调整: 排除非经常项目 (港股IFRS)"""
def adjust_metrics(reader, rd, np_val, tax_rate, stock_cfg):
    footnotes = []
    if np_val is None: return None, footnotes
    items = [
        ("公允价值变动收益", "FV"), ("汇兑收益", "FX"), ("政府补助", "GS"),
        ("资产处置收益", "IM"), ("其他收益", "OG"),
    ]
    nonrecur = []
    for item_name, abbr in items:
        val = reader.financial_item("income", item_name, rd) or 0
        if abs(val) > 5e6: nonrecur.append((abbr, val))
    if nonrecur:
        adj_np = np_val
        for _, v in nonrecur: adj_np -= v * (1 - tax_rate)
        item_str = " ".join([f"{{a}} {{v/1e8:+.2f}}" for a, v in nonrecur])
        footnotes.append(f"EPS adj: {{item_str}} -> VL {{adj_np/1e8:.1f}}亿 (归母{{np_val/1e8:.1f}}亿)")
    else:
        adj_np = np_val
    return adj_np, footnotes
'''

EXTRACT = '''# -*- coding: utf-8 -*-
"""{name} {code} — PDF信息提取: 补充数据"""
import pdfplumber, os

code = "{code}"
pdf_dir = f"data/pdfs/{code}"
pdfs = sorted([f for f in os.listdir(pdf_dir) if f.endswith('.pdf')]) if os.path.isdir(pdf_dir) else []
if pdfs:
    latest = pdfs[-1]
    pdf = pdfplumber.open(os.path.join(pdf_dir, latest))
    print(f"PDF: {{latest}}, {{len(pdf.pages)}} pages")
    for i, page in enumerate(pdf.pages):
        text = page.extract_text()
        if not text: continue
        for kw in ["雇员", "员工", "人数"]:
            if kw in text:
                idx = text.find(kw)
                print(f"\\n--- Page {{i+1}}: [{{kw}}] ---")
                print(text[max(0,idx-50):idx+300])
                break
    pdf.close()
else:
    print(f"{{code}}: 无PDF文件")
'''

for code in targets:
    stock = config.STOCKS.get(code, {})
    name = stock.get("name", code)
    market = stock.get("market", "cn")
    d = os.path.join(SCRIPT_DIR, code)

    # business_commentary.py
    path = os.path.join(d, "business_commentary.py")
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            f.write(BC.format(code, name))
        print(f"  + {code} business_commentary.py")

    # metric_adjustment.py
    path = os.path.join(d, "metric_adjustment.py")
    if not os.path.exists(path):
        tpl = HK_ADJ if market == "hk" else CN_ADJ
        with open(path, "w", encoding="utf-8") as f:
            f.write(tpl.format(code=code, name=name))
        print(f"  + {code} metric_adjustment.py")

    # extract_business.py
    path = os.path.join(d, "extract_business.py")
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            f.write(EXTRACT.format(code=code, name=name))
        print(f"  + {code} extract_business.py")

print(f"\nDone. {len(targets)} stocks processed.")
