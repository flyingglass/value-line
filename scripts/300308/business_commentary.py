# -*- coding: utf-8 -*-
"""中际旭创 300308 — VL Business + AI Commentary (数据驱动)"""
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
    per_cf,per_capex=ly.get("PER_NETCASH"),ly.get("CAPEX_PS")or 0
    pe,pb=spot.get("pe",0)or 0,spot.get("pb",0)or 0; div=spot.get("div_yield",0)or 0
    biz=f"中际旭创是全球领先的光模块提供商，AI算力基础设施核心供应商。800G/1.6T光模块全球份额第一（约30%），深度绑定北美云厂商。营收{_fmt(rev,0)}亿（{_dir(rev,py.get('OPERATE_INCOME'))}{abs(r_chg):.1f}%），净利率{_p(npm)}，ROE {_p(roe)}。"
    p1=f"2026年6月 — 中际旭创营收{_fmt(rev,0)}亿（{_dir(rev,py.get('OPERATE_INCOME'))}{abs(r_chg):.1f}%），净利润{_fmt(np,0)}亿（{_dir(np,py.get('HOLDER_PROFIT'))}{abs(n_chg):.1f}%）。800G出货全球第一，1.6T量产。AI驱动高速光模块需求指数增长。"
    p2=f"每股收益{_fmt(eps,2)}元，每股现金流{_fmt(per_cf,2)}元，每股资本支出{_fmt(per_capex,2)}元。产能全球最大，单位成本持续下降。"
    p3=f"毛利率{_p(gm)}、净利率{_p(npm)}、ROE {_p(roe)}。壁垒：①先发优势——最早量产800G，1.6T领先竞品6-12月；②客户粘性——深度参与北美云厂商光模块设计验证；③规模效应——产能全球最大。风险：AI资本开支周期性、价格年降压力、中美贸易限制。"
    p4=f"当前PE约{_fmt(pe,1)}倍，PB约{_fmt(pb,1)}倍。PEG约{_fmt(pe/(r_chg or 1),1)}x。关注每季度800G/1.6T出货量及北美云厂商Capex。"
    p5="催化剂：AI算力投资持续超预期+1.6T渗透率提升。若每季度出货量保持环比增长，估值有显著重估空间。关注英伟达GPU出货量指引及北美云厂商Capex指引。"
    return {"business":biz,"commentary":[p1,p2,p3,p4,p5]}
