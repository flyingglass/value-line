# -*- coding: utf-8 -*-
"""TCL中环 002129 — VL Business + AI Commentary（数据驱动）"""
def build(stock, metrics, revenue_structure, years, cagr, spot):
    ly=metrics.get(years[-1],{}) if years else {}
    py=metrics.get(years[-2],{}) if len(years)>=2 else {}
    def _chg(c,p):
        try:
            c2,p2=float(c),float(p)
            if not c2 or not p2: return None
            if p2>0: return (c2/p2-1)*100
            # 两期均为负: 减亏率 = (亏损收窄额) / |上期亏损|
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
    rev=np_val=eps=gm=npm=roe=roic=bps=0
    rev=_num(ly.get("OPERATE_INCOME"))
    np_val=_num(ly.get("HOLDER_PROFIT"))
    eps=_num(ly.get("BASIC_EPS"))
    gm=_num(ly.get("GROSS_MARGIN"))
    npm=_num(ly.get("NET_PROFIT_RATIO"))
    roe=_num(ly.get("ROE"))
    roic=_num(ly.get("ROIC"))
    bps=_num(ly.get("BPS"))
    r_chg=_chg(rev, py.get("OPERATE_INCOME"))
    n_chg=_chg(np_val, py.get("HOLDER_PROFIT"))
    per_cf=_num(ly.get("PER_NETCASH"))
    per_capex=_num(ly.get("CAPEX_PS") or 0)
    dps=_num(ly.get("DPS") or 0)
    payout=_num(ly.get("PAYOUT_RATIO"))
    pb=_num(spot.get("pb",0))
    div=_num(spot.get("div_yield",0))
    price=_num(spot.get("price",0))
    prod_data = revenue_structure.get("by_product", []) if isinstance(revenue_structure, dict) else []
    prod_str_parts = [f"{r['name']}{r['pct']}%" for r in prod_data] if prod_data else []
    prod_str = "、".join(prod_str_parts) if prod_str_parts else ""
    r_abs=abs(r_chg) if r_chg is not None else 0
    n_abs=abs(n_chg) if n_chg is not None else 0
    biz=f"TCL中环是全球光伏硅片龙头+国内最大半导体硅片供应商之一，主营光伏单晶硅片、光伏电池组件、半导体硅片的研发生产。2025年营收{_fmt(rev,0)}亿（同比{_dir(rev,py.get('OPERATE_INCOME'))}{r_abs:.1f}%），归母净利润{_fmt(np_val,0)}亿（同比减亏{n_abs:.1f}%）。产品结构：{prod_str}。半导体材料收入57.07亿（+21.8%），毛利率18.9%，成为第二增长极。"
    p1=f"2026年6月 — TCL中环营收{_fmt(rev,0)}亿（{_dir(rev,py.get('OPERATE_INCOME'))}{r_abs:.1f}%），归母净利润{_fmt(np_val,0)}亿（同比减亏{n_abs:.1f}%）。光伏硅片市占率保持全球第一，G12大尺寸硅片出货同比+40.8%。光伏行业供需失衡导致全产业链价格暴跌，光伏硅片毛利率-20.5%深度亏损，但半导体材料业务逆势增长，营收57亿（+21.8%）、毛利率18.9%，有效对冲光伏亏损。"
    net_ps=round(per_cf-per_capex-dps,2) if per_cf else None
    p2=f"每股收益{_fmt(eps,2)}元（亏损），每股现金流{_fmt(per_cf,2)}元（负值），资本支出每股{_fmt(per_capex,2)}元，分红{_fmt(dps,2)}元（支付率{_fmt(payout,0)}%）。现金流全赛道承压：经营现金流为负反映行业寒冬，但资本开支不减反增（半导体12英寸硅片扩产），无分红。每股净资产{_fmt(bps,2)}元，PB={_fmt(pb,2)}倍，净资产提供估值锚。"
    p3=f"毛利率{_p(gm)}、净利率{_p(npm)}、ROE{_p(roe)}、ROIC{_p(roic)}——光伏周期底部，盈利能力严重受损。但护城河仍在：①光伏硅片全球市占率第一（23.5%），210mm大尺寸技术领先；②半导体硅片国内龙头（4-12英寸全覆盖），通过台积电/英飞凌认证；③工业4.0柔性制造带来成本优势。风险：光伏产能过剩持续、硅片价格战、Maxeon持股拖累、高资本开支下现金流压力。"
    bps_1x=_fmt(bps,2)
    bps_15x=_fmt(bps*1.5,2) if bps else "-"
    p4=f"PE无意义（亏损）。当前PB约{_fmt(pb,2)}倍，每股净资产{_fmt(bps,2)}元对应股价{_fmt(price,2)}元。用PB估值：保守PB=1.0x对应{bps_1x}元（与当前股价基本持平），中性PB=1.5x对应{bps_15x}元。半导体业务单独估值可达300-400亿，光伏业务按净资产估值，分部加总显示当前市值或已反映悲观预期。关注光伏减亏拐点+半导体增长斜率作为核心信号。"
    p5="催化剂：①光伏行业产能出清→硅片价格企稳回升；②半导体12英寸大硅片放量（中环领先IPO预期）；③海外建厂（沙特10GW晶体晶片项目）。若光伏行业触底+半导体业务估值重估，存在显著向上弹性。关注每季度光伏硅片毛利率修复进度及半导体营收增速。"
    return {"business":biz,"commentary":[p1,p2,p3,p4,p5]}
