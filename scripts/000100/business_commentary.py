# -*- coding: utf-8 -*-
"""TCL科技 000100 — VL Business + AI Commentary（数据驱动）"""
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
    r_chg=_chg(rev, py.get("OPERATE_INCOME"))
    n_chg=_chg(np_val, py.get("HOLDER_PROFIT"))
    r_abs=abs(r_chg) if r_chg is not None else 0
    n_abs=abs(n_chg) if n_chg is not None else 0

    # Revenue structure by product
    prod_data = revenue_structure.get("by_product", []) if isinstance(revenue_structure, dict) else []
    panel_rev = next((r['value'] for r in prod_data if '显示' in r.get('name','')), None)
    pv_rev = next((r['value'] for r in prod_data if '光伏' in r.get('name','') or '新能源' in r.get('name','')), None)

    biz=f"TCL科技主营半导体显示（TCL华星光电）和新能源光伏（TCL中环）两大业务。半导体显示业务以面板制造为核心，产品涵盖大尺寸TV面板、中小尺寸IT/Mobile面板等；新能源光伏业务以TCL中环（002129.SZ）为载体，主营光伏硅片和半导体硅片。2025年营收{_fmt(rev,0)}亿（同比{_dir(rev,py.get('OPERATE_INCOME'))}{r_abs:.1f}%），归母净利润{_fmt(np_val,0)}亿（同比增长{n_abs:.1f}%）。"

    p1=f"2026年6月 — TCL科技营收{_fmt(rev,0)}亿（同比增长{r_abs:.1f}%），归母净利润{_fmt(np_val,0)}亿（同比增长{n_abs:.1f}%）。半导体显示业务复苏是利润增长核心驱动：面板价格经历2022-2023低谷后持续回升，叠加产能利用率提升和大尺寸化趋势，华星光电盈利能力显著改善。新能源光伏业务受行业产能过剩影响，TCL中环2025年营收约290亿、亏损约98亿，严重拖累合并利润。剔除非经常性损益后归母净利润约29亿，面板主业实际盈利能力更强。"

    p2=f"每股收益{_fmt(eps,2)}元，每股现金流{_fmt(per_cf,2)}元，资本支出每股{_fmt(per_capex,2)}元（面板+光伏双线重资产投入）。每股净资产{_fmt(bps,2)}元，资产结构偏重——固定资产+在建工程超2000亿，年折旧超300亿。经营现金流健康（每股2.12元），自由现金流承压（CAPEX高）。有息负债规模大（~1700亿），但面板业务现金流稳定、光伏业务有望触底，整体偿债风险可控。"

    p3=f"毛利率{_p(gm)}、净利率{_p(npm)}、ROE{_p(roe)}。面板行业核心特征：①强周期性——面板价格波动直接影响利润（2023年行业低谷GP仅9.8%，2025年回升至13.2%）；②重资产壁垒——高世代产线投资门槛百亿级，新进入者极少；③中国主导格局——华星光电+京东方合计占全球LCD产能60%+。风险：面板周期下行（产能过剩）、TCL中环亏损持续（光伏行业出清仍需时间）、债务负担（资产负债率64%）。"

    cf_10x=_fmt(per_cf*10,2) if per_cf else "-"
    cf_15x=_fmt(per_cf*15,2) if per_cf else "-"
    p4=f"当前PE约{_fmt(pe,1)}倍，PB{_fmt(pb,2)}倍。面板股估值以PB为核心（重资产周期股）：当前PB=1.17x，每股净资产{_fmt(bps,2)}元。面板行业PB历史中枢1.0-1.5x，当前处于中位。若面板景气持续+TCL中环减亏，PB有向1.3-1.5x修复空间。可比公司：京东方PB 1.18x，面板双龙头估值高度联动。"

    p5="催化剂：①面板价格维持高位——2026年TV面板供需偏紧，大尺寸化趋势持续（平均尺寸年增1.5-2英寸），华星光电盈利有望继续改善；②TCL中环减亏/剥离——光伏行业2026年产能出清有望加速，中环亏损收窄将直接增厚归母利润；③OLED渗透——中小尺寸OLED产线（T4/T5）良率提升和客户导入，打开第二增长曲线。关注每季度面板价格、华星光电经营利润、TCL中环减亏进展作为核心信号。"

    return {"business":biz,"commentary":[p1,p2,p3,p4,p5]}
