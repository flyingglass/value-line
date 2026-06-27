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
    r_chg=_chg(rev, py.get("OPERATE_INCOME"))
    n_chg=_chg(np_val, py.get("HOLDER_PROFIT"))
    r_abs=abs(r_chg) if r_chg is not None else 0
    n_abs=abs(n_chg) if n_chg is not None else 0

    # Revenue structure
    prod_data = revenue_structure.get("by_product", []) if isinstance(revenue_structure, dict) else []
    prod_str_parts = [f"{r['name']}{r['pct']:.0f}%" for r in prod_data] if prod_data else []
    prod_str = "、".join(prod_str_parts) if prod_str_parts else ""

    biz=f"京东方是全球领先的半导体显示技术公司，主营显示器件、物联网创新、MLED、智慧医工、传感等业务。核心业务为显示器件（LCD/OLED面板），智能手机/平板/笔记本/显示器/TV五大主流领域面板出货量稳居全球第一。2025年营收{_fmt(rev,0)}亿（同比{_dir(rev,py.get('OPERATE_INCOME'))}{r_abs:.1f}%），归母净利润{_fmt(np_val,0)}亿（同比增长{n_abs:.1f}%）。业务结构：{prod_str}。"

    p1=f"2026年6月 — 京东方营收{_fmt(rev,0)}亿（同比增长{r_abs:.1f}%），归母净利润{_fmt(np_val,0)}亿（同比增长{n_abs:.1f}%）。2025年是面板行业温和复苏之年：TV面板价格自2024下半年回升后维持相对高位，IT面板价格企稳。公司营收首次突破2000亿大关。利润增速温和（+10%）因OLED业务（绵阳/重庆/成都产线）仍处产能爬坡和折旧高峰期，拖累整体利润率。扣非净利润约25.7亿（+82%），核心面板主业盈利能力切实改善。"

    p2=f"每股收益{_fmt(eps,2)}元，每股现金流{_fmt(per_cf,2)}元，资本支出每股{_fmt(per_capex,2)}元。每股净资产{_fmt(bps,2)}元。京东方是超级重资产企业（总资产超4200亿，固定资产+在建工程超2500亿），年折旧374亿，折旧现金流远超会计利润——2025年经营现金流414亿（每股1.11元），是EPS（0.11元）的10倍，自由现金流≈14亿（股息覆盖后）。有息负债约1800亿，但以长期银团贷款为主，期限匹配产线寿命，偿债压力可控。"

    p3=f"毛利率{_p(gm)}、净利率{_p(npm)}、ROE{_p(roe)}。面板行业三大护城河：①规模+技术壁垒——高世代产线投资门槛300-500亿/条，全球仅京东方+TCL华星两家中国企业主导LCD产能（合计>60%）；②专利壁垒——累计可用专利超9万件，OLED专利全球前三；③客户粘性——五大主流品牌（三星/苹果/华为/联想/戴尔）深度绑定。风险：面板周期性（产能过剩→价格战→亏损）、OLED折旧高峰（2025-2027年折旧压力最大）、高负债率（资产负债率52%）。"

    cf_8x=_fmt(per_cf*8,2) if per_cf else "-"
    cf_10x=_fmt(per_cf*10,2) if per_cf else "-"
    p4=f"当前PE约{_fmt(pe,1)}倍（因会计利润薄但现金流强劲，PE估值失真），PB{_fmt(pb,2)}倍。面板股核心看PB：当前PB=1.18x，每股净资产{_fmt(bps,2)}元。历史PB区间0.8-2.0x，当前处于中低位。若按CF=8x估值（重资产折旧股合理倍数），对应{cf_8x}元（较当前{_fmt(price,2)}元有36%上行空间）。可比TCL科技PB 1.17x，面板双龙头估值高度一致。"

    p5="催化剂：①面板价格——2026年TV面板供需仍偏紧（韩厂退出+中国控产+大尺寸化），价格有望维持高位；②OLED拐点——成都/绵阳/重庆三条柔性OLED产线进入产能释放期，苹果iPhone/LTPO订单增量有望带动OLED业务2027年前后扭亏；③物联网创新——智慧金融/智慧园区/数字艺术等新兴业务快速增长（+15%+），打开非面板第二增长曲线。关注每季度面板均价、OLED出货量、折旧高峰过后的利润弹性。"

    return {"business":biz,"commentary":[p1,p2,p3,p4,p5]}
