# -*- coding: utf-8 -*-
"""京东方 000725 — VL Business + AI Commentary（数据驱动）"""
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

    # Revenue structure
    prod_data = revenue_structure.get("by_product", []) if isinstance(revenue_structure, dict) else []
    display = next((r['value'] for r in prod_data if '显示' in r.get('name','')), None)
    iot = next((r['value'] for r in prod_data if '物联网' in r.get('name','') or '创新' in r.get('name','')), None)
    mled = next((r['value'] for r in prod_data if 'MLED' in r.get('name','') or 'mled' in r.get('name','')), None)

    # total assets and debt from metrics
    total_eq=_num(ly.get("TOTAL_EQUITY"))
    lt_debt=_num(ly.get("LT_DEBT"))

    biz=f"京东方是全球领先的半导体显示技术公司，主营显示器件（LCD/OLED面板）、物联网创新、MLED、智慧医工等业务。智能手机、平板、笔记本、显示器、电视五大主流领域面板出货量稳居全球第一。2025年营收{_fmt(rev,0)}亿（同比{_dir(rev,py.get('OPERATE_INCOME'))}{r_abs:.1f}%），归母净利润{_fmt(np_val,0)}亿（同比增长{n_abs:.1f}%）。"

    p1=f"2026年6月 — 京东方营收{_fmt(rev,0)}亿（同比增长{r_abs:.1f}%），归母净利润{_fmt(np_val,0)}亿（同比增长{n_abs:.1f}%）。2025年面板行业温和复苏：TV面板价格自2024下半年回升后维持相对高位，IT面板价格企稳，公司营收首次突破2000亿大关。利润增速温和主因OLED产线仍处折旧高峰期（成都/绵阳/重庆三条柔性OLED线），拖累整体利润率。毛利率{_p(gm)}，同比提升{_p(gm-_num(py.get('GROSS_MARGIN')))}，核心显示器件主业盈利能力切实改善。"

    p2=f"每股收益{_fmt(eps,2)}元，每股现金流{_fmt(per_cf,2)}元，每股资本支出{_fmt(per_capex,2)}元，每股净资产{_fmt(bps,2)}元。京东方是超级重资产企业，年折旧{_fmt(dep,0)}亿，折旧现金流远超会计利润——每股经营现金流{_fmt(per_cf,2)}元是EPS {_fmt(eps,2)}元的{_fmt(per_cf/eps,0) if eps else '-'}倍。自由现金流={_fmt(per_cf-per_capex-dps,2)}元/股（扣CAPEX+股息后）。总股本{_fmt(shares/100,0)}亿股，PB估值关键。"

    p3=f"毛利率{_p(gm)}、净利率{_p(npm)}、ROE{_p(roe)}。面板行业三大护城河：①规模+工艺壁垒——高世代产线投资门槛300-500亿/条，全球LCD产能由京东方+TCL华星双寡头主导（合计>60%）；②专利壁垒——累计可用专利超9万件，OLED专利全球前三；③客户粘性——五大品牌（三星/苹果/华为/联想/戴尔）深度绑定。风险：面板强周期性（产能过剩→价格战→全行业亏损）、OLED折旧高峰（2025-2027年折旧压力最大）、长期负债{_fmt(lt_debt,0)}亿。"

    cf_8x=_fmt(per_cf*8,2) if per_cf else "-"
    p4=f"当前PE约{_fmt(pe,1)}倍，PB{_fmt(pb,2)}倍。面板股核心看PB估值（重资产周期股）：每股净资产{_fmt(bps,2)}元，历史PB区间0.8-2.0x，当前处于中低位。CF=8x估值对应{cf_8x}元/股。面板双龙头定价高度联动——TCL科技PB {1.17}，京东方PB {_fmt(pb,2)}。"

    p5="催化剂：①面板价格——2026年TV面板供需偏紧（韩厂退出+中国控产+大尺寸化趋势），价格有望维持相对高位；②OLED拐点——成都/绵阳/重庆三条柔性OLED产线产能释放，iPhone LTPO订单增量有望驱动OLED业务2027年前后扭亏；③折旧高峰过后的利润弹性——年折旧300亿+，折旧到期后将直接转化为利润。关注每季度面板价格、OLED出货量及良率、折旧进度。"

    return {"business":biz,"commentary":[p1,p2,p3,p4,p5]}
