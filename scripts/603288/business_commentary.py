# -*- coding: utf-8 -*-
"""海天味业 603288 — VL Business + AI Commentary"""
def build(stock, metrics, revenue_structure, years, cagr, spot):
    ly = metrics.get(years[-1], {}) if years else {}
    py = metrics.get(years[-2], {}) if len(years) >= 2 else {}
    def _chg(c,p): return (c/p-1)*100 if c and p and p>0 else None
    def _d(c,p): return "增长" if (_chg(c,p) or 0)>0 else "下降"
    def _f(v,d=0): return f"{v:,.{d}f}" if v is not None else "-"
    def _p(v): return f"{v:+.1f}%" if v is not None else "-"
    rev, npv, eps = ly.get("OPERATE_INCOME"), ly.get("HOLDER_PROFIT"), ly.get("BASIC_EPS")
    gm, npm, roe, roic = ly.get("GROSS_MARGIN"), ly.get("NET_PROFIT_RATIO"), ly.get("ROE"), ly.get("ROIC")
    rc, nc = _chg(rev, py.get("OPERATE_INCOME")), _chg(npv, py.get("HOLDER_PROFIT"))
    per_cf, dps = ly.get("PER_NETCASH"), ly.get("DPS") or 0
    rp = []; 
    if isinstance(revenue_structure, dict):
        for dk, items in revenue_structure.items():
            if items: rp.extend([f"{r.get('name','')}{r.get('pct',''):.0f}%" for r in items[:3]])
    biz = f"海天味业是中国调味品行业绝对龙头，酱油市占率约20%，主营酱油、蚝油、调味酱。品牌+渠道壁垒深厚。FY{years[-1]}营收{_f(rev,0)}亿（{_d(rev, py.get('OPERATE_INCOME'))}{abs(rc):.1f}%），归母净利{_f(npv,0)}亿，净利率{_p(npm)}，ROE {_p(roe)}。" + (f"营收结构：{'/'.join(rp)}。" if rp else "")
    p1 = f"2026年7月 — 海天味业营收{_f(rev,0)}亿（{_d(rev, py.get('OPERATE_INCOME'))}{abs(rc):.1f}%），归母净利{_f(npv,0)}亿（{_d(npv, py.get('HOLDER_PROFIT'))}{abs(nc):.1f}%）。毛利率{_p(gm)}、净利率{_p(npm)}。酱油为现金牛，蚝油/复合调味料为增长引擎。经营现金流77.46亿（+13.2%），分红每股0.80元。A+H双上市平台拓宽融资渠道。"
    p2 = f"每股收益¥{_f(eps,2)}，经营现金流¥{_f(per_cf,2)}，分红¥{_f(dps,2)}/股。5.85亿渠道终端+品牌认知形成深厚护城河，几乎无有息负债，财务极度稳健。2025年H股上市募集约96.6亿港元，为海外并购和产能扩张储备弹药。"
    p3 = f"毛利率{_p(gm)}、净利率{_p(npm)}、ROE {_p(roe)}" + (f"、ROIC {_p(roic)}。" if roic else "。") + "壁垒：①品牌——中华老字号+酱油品类第一联想，消费者切换成本高；②渠道——覆盖300万+餐饮终端，经销商体系20年深耕；③规模——年产300万吨+，单位成本行业最低。风险：餐饮渠道占比高（受经济周期影响）、复合调味料竞争加剧、酱油品类增长天花板。"
    pe, pb, dy = spot.get("pe",0), spot.get("pb",0), spot.get("div_yield",0)
    med = spot.get("median_pe"); bps = ly.get("BPS")
    p4 = f"PE约{_f(pe,1)}倍"+(f"，历史中位{_f(med,0)}x。" if med else "。")+f"PB{_f(pb,1)}倍（BPS{_f(bps,2)}元）。股息率{_f(dy,1)}%。核心逻辑：①调味品刚需消费品，经济下行期防御性强；②渠道下沉+品类扩张双轮驱动低双位数增长；③H股上市后海外并购（东南亚调味品品牌）期权价值。关注酱油销量增速和餐饮渠道恢复。"
    p5 = "催化剂：①餐饮渠道复苏+外卖渗透率提升→酱油/蚝油量增；②复合调味料+预制菜调料包打开第二增长曲线；③H股募集资金并购海外调味品品牌（东南亚/日本）；④46.77亿分红（分红率67%）彰显现金牛属性。关注每季度酱油销量和吨价变化。"
    return {"business": biz, "commentary": [p1,p2,p3,p4,p5]}
