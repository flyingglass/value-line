# -*- coding: utf-8 -*-
"""盐湖股份 000792 — VL Business + AI Commentary（数据驱动）"""
def build(stock, metrics, revenue_structure, years, cagr, spot):
    ly=metrics.get(years[-1],{}) if years else {}
    py=metrics.get(years[-2],{}) if len(years)>=2 else {}
    def _chg(c,p):
        try:
            c2,p2=float(c),float(p)
            if not c2 or not p2: return None
            if p2>0: return (c2/p2-1)*100
            if c2<0 and p2<0: return (c2-p2)/abs(p2)*100
            return (c2/p2-1)*100
        except: return None
    def _dir(c,p): return "增长" if (_chg(c,p) or 0)>0 else "下降"
    def _num(v): return float(v) if v is not None else 0
    def _fmt(v,d=0):
        try: return f"{float(v):,.{d}f}"
        except: return "-"
    def _p(v):
        try: return f"{float(v):+.1f}%"
        except: return "-"
    rev=_num(ly.get("OPERATE_INCOME"))
    np_val=_num(ly.get("HOLDER_PROFIT"))
    eps=_num(ly.get("BASIC_EPS"))
    gm=_num(ly.get("GROSS_MARGIN"))
    npm=_num(ly.get("NET_PROFIT_RATIO"))
    roe=_num(ly.get("ROE"))
    roic=_num(ly.get("ROIC"))
    bps=_num(ly.get("BPS"))
    per_cf=_num(ly.get("PER_NETCASH"))
    per_capex=_num(ly.get("CAPEX_PS") or 0)
    dps=_num(ly.get("DPS") or 0)
    pb=_num(spot.get("pb",0))
    pe=_num(spot.get("pe",0))
    price=_num(spot.get("price",0))
    shares=_num(ly.get("TOTAL_SHARES"))
    dep=_num(ly.get("DEPRECIATION"))
    r_chg=_chg(rev, py.get("OPERATE_INCOME"))
    n_chg=_chg(np_val, py.get("HOLDER_PROFIT"))
    r_abs=abs(r_chg) if r_chg is not None else 0
    n_abs=abs(n_chg) if n_chg is not None else 0

    # Revenue structure from metrics
    prod_data = revenue_structure.get("by_product", []) if isinstance(revenue_structure, dict) else []

    # total equity and debt
    total_eq=_num(ly.get("TOTAL_EQUITY"))
    lt_debt=_num(ly.get("LT_DEBT"))
    debt_ratio=_num(ly.get("DEBT_ASSET_RATIO"))

    biz=f"盐湖股份是中国最大的钾肥和盐湖提锂企业，实控人为中国五矿集团。主营氯化钾（钾肥）和碳酸锂的生产与销售，拥有察尔汗盐湖（世界级锂钾资源）和一里坪盐湖双资源基地。钾肥产能500万吨/年，国内市占率超60%；碳酸锂产能约6万吨/年。2025年营收{_fmt(rev,0)}亿（同比{_dir(rev,py.get('OPERATE_INCOME'))}{r_abs:.1f}%），归母净利润{_fmt(np_val,0)}亿（同比增长{n_abs:.1f}%）。"

    p1=f"2025年营收{_fmt(rev,0)}亿（同比增长{r_abs:.1f}%），归母净利润{_fmt(np_val,0)}亿（同比增长{n_abs:.1f}%）。利润增速远超营收，主因碳酸锂价格触底回升——2025年碳酸锂均价较2024年显著上涨，叠加钾肥价格持稳，公司毛利率从{_p(_num(py.get('GROSS_MARGIN')))}提升至{_p(gm)}，净利率从{_p(_num(py.get('NET_PROFIT_RATIO')))}跃升至{_p(npm)}。全年生产氯化钾490.02万吨、碳酸锂4.65万吨，2025年12月收购五矿盐湖51%股权（一里坪盐湖），2026年1月并表，\"察尔汗+一里坪\"双盐湖布局成型。"

    p2=f"每股收益{_fmt(eps,2)}元，每股经营现金流{_fmt(per_cf,2)}元，每股净资产{_fmt(bps,2)}元。公司是典型的资源型现金牛：资产负债率仅{_fmt(debt_ratio,1)}%，长期借款{_fmt(lt_debt,0)}亿几乎为零，经营现金流{_fmt(per_cf*shares/100000000,0)}亿远超资本支出{_fmt(per_capex*shares/100000000,0)}亿。每股经营现金流{_fmt(per_cf,2)}元是EPS的{_fmt(per_cf/eps,1) if eps else '-'}倍，自由现金流充沛。总股本52.92亿股，2025年实控人中国五矿增持2.48亿股（占总股本4.69%），彰显信心。"

    p3=f"毛利率{_p(gm)}、净利率{_p(npm)}、ROE{_p(roe)}。盐湖提锂是中国最具成本优势的锂资源开发路径——察尔汗盐湖卤水提锂成本3-5万元/吨，远低于锂辉石（6-8万）和锂云母（8-10万）。三大护城河：①资源壁垒——察尔汗盐湖氯化锂储量世界级，中国盐湖资源集中在青海西藏，准入极难；②成本壁垒——盐湖提锂是全球成本最低的锂资源路线，钾肥联产摊薄固定成本；③央企背书——五矿集团入主后资源整合+融资优势。风险：碳酸锂价格周期波动剧烈（2022年高点近60万/吨→2024年低点7万/吨）、钾肥受国际粮价和大合同价影响。"

    pb_1_5x=_fmt(bps*1.5,2) if bps else "-"
    pb_2x=_fmt(bps*2.0,2) if bps else "-"
    p4=f"当前股价{_fmt(price,2)}元，PE约{_fmt(price/eps,1) if eps else '-'}倍，PB{_fmt(price/bps,2) if bps else '-'}倍。盐湖股份适合PB估值（资源型周期股）：每股净资产{_fmt(bps,2)}元，净资产主要构成为盐湖采矿权+钾锂产能资产，重置成本极高。历史PB区间约1.0-4.0x，PB=1.5-2.0x对应{_fmt(bps*1.5,2)}-{_fmt(bps*2.0,2)}元/股。当前PB在历史中位水平，需关注碳酸锂价格走势对盈利和净资产的边际影响。"

    p5="催化剂：①碳酸锂价格——2026年上半年碳酸锂价格呈上涨趋势，公司H1预增131%-155%（归母净利>60亿），钾肥量价齐升+锂盐产销两旺；②五矿盐湖并表——2026年1月完成交割，新增一里坪盐湖资源（氯化锂164.59万吨、氯化钾1,463.11万吨），远期碳酸锂产能有望翻倍；③钾肥景气——全球粮食安全+俄乌冲突持续扰动国际钾肥供给，钾肥价格维持高位；④央企改革——\"三步走战略\"下资源整合预期（中国盐湖集团平台）。关注季度碳酸锂产量/销量、钾肥大合同价、产能扩建进度。"

    return {"business":biz,"commentary":[p1,p2,p3,p4,p5]}
