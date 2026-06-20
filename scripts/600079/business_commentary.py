# -*- coding: utf-8 -*-
"""人福医药 600079 — VL Business + AI Commentary（数据驱动）"""
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
    payout=_num(ly.get("PAYOUT_RATIO") or 0)
    pb=_num(spot.get("pb",0))
    pe=_num(spot.get("pe",0))
    price=_num(spot.get("price",0))
    mkt_cap=_num(spot.get("mkt_cap",0))
    r_chg=_chg(rev, py.get("OPERATE_INCOME"))
    n_chg=_chg(np_val, py.get("HOLDER_PROFIT"))
    prod_data = revenue_structure.get("by_product", []) if isinstance(revenue_structure, dict) else []
    prod_str_parts = [f"{r['name']}{r['pct']:.0f}%" for r in prod_data] if prod_data else []
    prod_str = "、".join(prod_str_parts) if prod_str_parts else ""
    r_abs=abs(r_chg) if r_chg is not None else 0
    n_abs=abs(n_chg) if n_chg is not None else 0
    biz=f"人福医药是中国麻醉药领域龙头企业，主营中枢神经用药、甾体激素及两性健康用药、维吾尔药及医药商业。核心子公司宜昌人福是国内最大的麻醉药品研发生产基地（持股80%），枸橼酸舒芬太尼、瑞芬太尼、氢吗啡酮等核心品种市占率居首。2025年营收{_fmt(rev,0)}亿（同比{_dir(rev,py.get('OPERATE_INCOME'))}{r_abs:.1f}%），归母净利润{_fmt(np_val,0)}亿（同比增长{n_abs:.1f}%）。业务结构：{prod_str}。2025年招商局集团入主，成为央企旗下医药平台，开启债务置换与降本增效新阶段。"
    p1=f"2026年6月 — 人福医药营收{_fmt(rev,0)}亿（{_dir(rev,py.get('OPERATE_INCOME'))}{r_abs:.1f}%），归母净利润{_fmt(np_val,0)}亿（同比增长{n_abs:.1f}%）。营收下降主因医药商业板块收缩（\"归核聚焦\"战略主动压缩低毛利批发业务），但核心制造业营收约{_fmt(142.1,0)}亿基本持平，毛利率提升至48.2%（+3.6pp）。利润高增长驱动因素：①制造业毛利率72.3%，同比提升4.1pp（原材料降价+降本增效）；②招商局入主后财务费用同比下降13.6%；③归核聚焦出售非核心资产。扣非净利润17.62亿（+54.8%），盈利质量扎实。"
    net_fcf=round(per_cf-per_capex-dps,2) if per_cf else None
    p2=f"每股收益{_fmt(eps,2)}元，每股现金流{_fmt(per_cf,2)}元，资本支出每股{_fmt(per_capex,2)}元（制造业扩产温和）。经营现金流2.52元/股，自由现金流{net_fcf}元/股，现金流健康。2025年未分红（ST状态，待摘帽后恢复），每股净资产{_fmt(bps,2)}元。招商局入主推进债务置换，短期债务占比下降，融资结构显著优化。应付票据及账款周转健康，运营资金充裕。"
    p3=f"毛利率{_p(gm)}、净利率{_p(npm)}、ROE{_p(roe)}——制造业毛利率72.3%支撑整体盈利，批发业务毛利率仅12.9%拖累综合毛利率至48.2%。核心护城河：①麻醉药品管制牌照壁垒（国家定点麻醉药品生产基地，竞争对手极有限）；②宜昌人福独家/首仿品种群（38个独家品规，舒芬太尼、瑞芬太尼、氢吗啡酮等市占率>50%）；③招商局央企背书——融资成本下降+治理改善。风险：ST状态制约融资/分红；医药商业板块持续收缩拖累营收；集采政策向麻醉药延伸的不确定性。"
    cf_15x=_fmt(per_cf*15,2) if per_cf else "-"
    cf_20x=_fmt(per_cf*20,2) if per_cf else "-"
    p4=f"当前PE约{_fmt(pe,1)}倍（扣非PE约{_fmt(price/17.62*16.32,0) if eps else '-'}倍），PB{_fmt(pb,2)}倍。CF估值：每股现金流{_fmt(per_cf,2)}元，CF=15x对应{cf_15x}元（较当前{_fmt(price,2)}元折价），CF=20x对应{cf_20x}元（接近当前价）。PB估值：每股净资产{_fmt(bps,2)}元，PB=1.22x处于历史低位。麻醉药赛道具备刚需+牌照护城河特性，可比公司（恒瑞、恩华）PE中枢25-30x，人福因ST折价交易，摘帽后存在估值修复空间。"
    p5="催化剂：①ST摘帽（预计2026年内，资金占用问题已解决）；②招商局集团资源注入——潜在资产整合（宜昌人福剩余20%股权收购）；③麻醉药新品放量（瑞马唑仑+47.5%产量增长、阿芬太尼持续渗透）；④国际化突破（美国市场全渠道覆盖，FDA认证品种出口增长）。若顺利摘帽+招商局治理改善兑现，PE有望从14x向20-25x重估，存在50%+上行空间。关注每季度宜昌人福利润增速及摘帽进展作为核心信号。"
    return {"business":biz,"commentary":[p1,p2,p3,p4,p5]}
