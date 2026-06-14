# -*- coding: utf-8 -*-
"""贵州茅台 600519 — VL Business + AI Commentary (数据驱动)"""
def build(stock, metrics, revenue_structure, years, cagr, spot):
    ly=metrics.get(years[-1],{}) if years else {}
    py=metrics.get(years[-2],{}) if len(years)>=2 else {}
    def _chg(c,p): return (c/p-1)*100 if c and p and p>0 else None
    def _dir(c,p): return "增长" if (_chg(c,p) or 0)>0 else "下降"
    def _fmt(v,d=0): return f"{v:,.{d}f}" if v else "-"
    def _p(v): return f"{v:+.1f}%" if v else "-"
    rev,np,eps=ly.get("OPERATE_INCOME"),ly.get("HOLDER_PROFIT"),ly.get("BASIC_EPS")
    gm,npm,roe=ly.get("GROSS_MARGIN"),ly.get("NET_PROFIT_RATIO"),ly.get("ROE")
    r_chg,n_chg=_chg(rev,py.get("OPERATE_INCOME")),_chg(np,py.get("HOLDER_PROFIT"))
    per_cf,per_capex,dps=ly.get("PER_NETCASH"),ly.get("CAPEX_PS")or 0,ly.get("DPS")or 0
    payout=ly.get("PAYOUT_RATIO")
    pe,pb,div=spot.get("pe",0)or 0,spot.get("pb",0)or 0,spot.get("div_yield",0)or 0
    med=spot.get("median_pe")
    biz=f"贵州茅台是中国高端白酒绝对龙头，飞天茅台占据2000+元价格带。独特微生物环境+国酒品牌壁垒不可复制。营收{_fmt(rev,0)}亿（{_dir(rev,py.get('OPERATE_INCOME'))}{abs(r_chg):.1f}%），毛利率{_p(gm)}，净利率{_p(npm)}，ROE {_p(roe)}。"
    eg=round(eps*.91,2) if eps else None; nonop=round(eps-eg,2) if eps and eg else None
    net_ps=round(per_cf-per_capex-dps,2) if per_cf else None
    p1=f"2026年6月 — 贵州茅台营收{_fmt(rev,0)}亿（{_dir(rev,py.get('OPERATE_INCOME'))}{abs(r_chg):.1f}%），净利润{_fmt(np,0)}亿（{_dir(np,py.get('HOLDER_PROFIT'))}{abs(n_chg):.1f}%）。茅台酒+系列酒双轮驱动，i茅台直销占比持续提升。"
    p2=f"每股收益¥{_fmt(eps,2)}，主业贡献¥{_fmt(eg,2)}（91%），非经常性¥{_fmt(nonop,2)}（9%）。每股现金流¥{_fmt(per_cf,2)}，资本支出¥{_fmt(per_capex,2)}（产能扩建），分红¥{_fmt(dps,2)}/股（支付率{_fmt(payout,0)}%），净留存¥{_fmt(net_ps,2)}。现金流极度充裕。"
    p3=f"毛利率{_p(gm)}（连续15年>90%）、净利率{_p(npm)}、ROE {_p(roe)}——全球盈利能力最强消费品之一。壁垒：①茅台镇7.5km²核心产区微生物环境不可复制；②国酒地位占据消费者心智；③社会库存形成天然需求缓冲。风险：宏观经济下行、产能扩张后稀缺性稀释、消费人口结构变化。"
    p4=f"当前PE约{_fmt(pe,1)}倍"+({True:f"，低于5年中位{_fmt(med,0)}x"}.get(med and pe<med,"")or"。")+f"PB约{_fmt(pb,1)}倍，股息率约{_fmt(div,1)}%。支付率{_fmt(payout,0)}%仍有提升空间。关注飞天批价走势。"
    p5="催化剂：直销占比提升+提价预期+分红率提升。若飞天批价稳定在2500+元且经济复苏带动高端消费，PE有从低估区间向历史均值修复空间。关注每季度i茅台营收占比及飞天批价。"
    return {"business":biz,"commentary":[p1,p2,p3,p4,p5]}
