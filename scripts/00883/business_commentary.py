# -*- coding: utf-8 -*-
"""中海油 00883 — VL Business + AI Commentary (数据驱动)"""
def build(stock, metrics, revenue_structure, years, cagr, spot):
    ly=metrics.get(years[-1],{}) if years else {}
    py=metrics.get(years[-2],{}) if len(years)>=2 else {}
    def _chg(c,p): return (c/p-1)*100 if c and p and p>0 else None
    def _dir(c,p): return "增长" if (_chg(c,p) or 0)>0 else "下降"
    def _fmt(v,d=0): return f"{v:,.{d}f}" if v else "-"
    def _p(v): return f"{v:+.1f}%" if v else "-"
    rev,np,eps=ly.get("OPERATE_INCOME"),ly.get("HOLDER_PROFIT"),ly.get("BASIC_EPS")
    gm,roe=ly.get("GROSS_MARGIN"),ly.get("ROE")
    r_chg,n_chg=_chg(rev,py.get("OPERATE_INCOME")),_chg(np,py.get("HOLDER_PROFIT"))
    per_cf,dps=ly.get("PER_NETCASH"),ly.get("DPS")or 0; payout=ly.get("PAYOUT_RATIO")
    pe,pb,div=spot.get("pe",0)or 0,spot.get("pb",0)or 0,spot.get("div_yield",0)or 0
    biz=f"中国海洋石油是中国最大的海上原油及天然气生产商，全球最大独立E&P企业之一。营收{_fmt(rev,0)}亿（{_dir(rev,py.get('OPERATE_INCOME'))}{abs(r_chg):.1f}%），净利率{_p(ly.get('NET_PROFIT_RATIO'))}，ROE {_p(roe)}。桶油成本持续下降。"
    p1=f"2026年6月 — 中海油营收{_fmt(rev,0)}亿（{_dir(rev,py.get('OPERATE_INCOME'))}{abs(r_chg):.1f}%），净利润{_fmt(np,0)}亿（{_dir(np,py.get('HOLDER_PROFIT'))}{abs(n_chg):.1f}%）。产量持续增长，勘探成功率行业领先。"
    p2=f"每股收益{_fmt(eps,2)}元，每股现金流{_fmt(per_cf,2)}元，分红{_fmt(dps,2)}元/股（支付率{_fmt(payout,0)}%）。资本支出控制在收入合理比例，自由现金流充裕，分红率承诺45%+。"
    p3=f"毛利率{_p(gm)}、净利率{_p(ly.get('NET_PROFIT_RATIO'))}。壁垒：①中国海上油气垄断经营权；②极低的桶油成本（全球第一梯队）；③海外资产组合分散地缘风险。风险：油价大幅波动、OPEC+产量政策、全球能源转型。"
    p4=f"当前PE约{_fmt(pe,1)}倍，PB约{_fmt(pb,1)}倍，股息率约{_fmt(div,1)}%。港股高股息板块核心标的。关注油价走势及OPEC+政策。"
    p5="催化剂：油价中枢维持70-80美元/桶即保障高盈利。若分红率持续提升或产量超预期，估值有上行空间。关注季度产量数据及桶油成本趋势。"
    return {"business":biz,"commentary":[p1,p2,p3,p4,p5]}
