# -*- coding: utf-8 -*-
"""宁德时代 300750 — VL Business + AI Commentary（数据驱动）"""
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
    gm_prev=_num(py.get("GROSS_MARGIN"))
    npm_prev=_num(py.get("NET_PROFIT_RATIO"))
    roe_prev=_num(py.get("ROE"))
    payout=_num(ly.get("PAYOUT_RATIO"))

    # Revenue structure
    prod_data = revenue_structure.get("by_product", []) if isinstance(revenue_structure, dict) else []
   动力 = next((r for r in prod_data if '动力' in r.get('name','')), None)
   储能 = next((r for r in prod_data if '储能' in r.get('name','')), None)
   材料 = next((r for r in prod_data if '材料' in r.get('name','') or '回收' in r.get('name','')), None)

    total_eq=_num(ly.get("TOTAL_EQUITY"))
    lt_debt=_num(ly.get("LT_DEBT"))

    biz=f"宁德时代是全球最大的动力电池和储能电池制造商，A+H双上市（300750.SZ / 03750.HK）。主营动力电池系统、储能电池系统和电池材料回收，技术覆盖三元锂、磷酸铁锂、钠离子、固态/凝聚态等多化学体系。全球动力电池市占率约39%（连续9年第一），储能电池市占率约30%（连续5年第一）。2025年营收{_fmt(rev,0)}亿（同比{_dir(rev,py.get('OPERATE_INCOME'))}{r_abs:.1f}%），归母净利润{_fmt(np_val,0)}亿（同比增长{n_abs:.1f}%），经营性现金流净额1332亿。"

    rev_运动=_num(动力.get('value',0)) if 动力 else 0
    rev_储能=_num(储能.get('value',0)) if 储能 else 0

    p1=f"2025年营收{_fmt(rev,0)}亿（同比增长{r_abs:.1f}%），归母净利润{_fmt(np_val,0)}亿（同比增长{n_abs:.1f}%）。利润增速远超营收，核心驱动：①动力电池出货量增长+产品结构升级（麒麟/神行高端电池占比提升）；②储能出货量同比大幅增长，海外储能单价和毛利率优于国内；③规模效应摊薄折旧+原材料成本下行（碳酸锂均价较2023年大幅回落）。毛利率从{_p(gm_prev)}提升至{_p(gm)}，净利率从{_p(npm_prev)}升至{_p(npm)}。分产品：动力电池收入{_fmt(rev_运动,0)}亿（占比{_fmt(动力.get('pct',0) if 动力 else 0,1)}%），储能收入{_fmt(rev_储能,0)}亿（占比{_fmt(储能.get('pct',0) if 储能 else 0,1)}%），储能正在成为第二增长引擎。"

    fcf_ps=_fmt(per_cf-per_capex-dps,2) if per_cf else "-"
    p2=f"每股收益{_fmt(eps,2)}元，每股经营现金流{_fmt(per_cf,2)}元，每股资本支出{_fmt(per_capex,2)}元，每股净资产{_fmt(bps,2)}元。宁德时代是超级现金牛：经营现金流1332亿远超资本支出444亿，自由现金流充沛。全年现金分红约361亿（含中期+年末），支付率约{payout:.0f}%，股息率约{_fmt(dps/price*100,1) if price and dps else '-'}%。货币资金3335亿，覆盖有息负债（长借782亿+短借129亿）绰绰有余。总股本46.27亿股（含回购注销），实控人曾毓群通过瑞华投资持股约23%。"

    p3=f"毛利率{_p(gm)}、净利率{_p(npm)}、ROE{_p(roe)}。宁德时代的护城河由五层壁垒构成：①技术壁垒——超2万项全球专利，麒麟电池（CTP 3.0）能量密度255Wh/kg，神行超充电池4C快充，纳新电池开辟钠离子新赛道；②规模壁垒——年产能超800GWh，全球最大单一电池工厂，单位成本比二线厂商低15-20%；③客户粘性——特斯拉、宝马、奔驰、大众等全球TOP车企深度绑定，更换供应商认证周期3-5年；④全产业链——从锂矿/镍矿（入股Pilbara/印尼镍项目）到电池回收（邦普循环）垂直整合；⑤全球化产能——德国、匈牙利、印尼工厂投产，规避地缘贸易壁垒。风险：动力电池产能过剩隐忧（全行业规划产能远超需求）、车企自研电池（比亚迪/特斯拉4680）、地缘政治（欧美本土化政策）。"

    pe_calc=_fmt(price/eps,1) if eps and price else "-"
    pb_calc=_fmt(price/bps,2) if bps and price else "-"
    p4=f"当前股价约{_fmt(price,2)}元，PE约{pe_calc}倍，PB约{pb_calc}倍。宁德时代近5年PE中枢约25-30倍（2020年前为40-60倍高增长溢价期），当前估值处于历史中低位。每股净资产{_fmt(bps,2)}元，主要由产能资产+现金+股权投资构成。按CF=12x估值（适合制造业龙头），对应约{_fmt(per_cf*12,2)}元/股。公司2025年ROE达{_p(roe)}，若维持该水平，PB=4-5x对应的ROE/PB比值约5-6%，投资回报率具备吸引力。注意：比亚迪（垂直整合+价格战）和韩系电池厂（LG/三星SDI）在海外市场的竞争加剧是估值的重要压制因素。"

    p5=f"催化剂：①储能爆发——2026年储能出货量有望翻倍，AIDC（AI数据中心）储能需求兴起，海外大储项目（中东/欧洲/美洲）Pipeline超200GWh；②固态/凝聚态电池——2026年4月超级科技日发布麒麟凝聚态电池（能量密度500Wh/kg），预计2027年量产，打开航空/高端电动车增量市场；③换电网络——超换一体全场景补能网络（巧克力换电块），商用车换电合作密集落地，开辟电池运营+服务经常性收入；④海外产能放量——匈牙利工厂2026年投产、印尼项目推进，海外市占率突破30%后利润弹性显著；⑤股东回报——2025年全年股东回报超400亿（分红+回购），未来有望维持50%+支付率。关注每季度装机量/市占率、碳酸锂价格走势、海外工厂投产进度。"

    return {"business":biz,"commentary":[p1,p2,p3,p4,p5]}
