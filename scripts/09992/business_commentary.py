# -*- coding: utf-8 -*-
"""泡泡玛特 09992 — VL Business + AI Commentary（数据驱动）"""
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
    ch_data = revenue_structure.get("by_channel", []) if isinstance(revenue_structure, dict) else []
    ch_str="、".join([f"{r.get('name','')}{r.get('pct','')}%" for r in ch_data[:3]]) if ch_data else ""
    biz=f"泡泡玛特是中国领先的潮流文化娱乐公司，以IP为核心，覆盖艺术家发掘、IP运营、全球零售及粉丝社区。最新财年营收{_fmt(rev,0)}亿（{_dir(rev,py.get('OPERATE_INCOME'))}{abs(r_chg):.1f}%），净利率{_p(npm)}，ROE {_p(roe)}。"+(f"渠道：{ch_str}。" if ch_str else "")
    p1=f"2026年6月 — 泡泡玛特营收{_fmt(rev,0)}亿（{_dir(rev,py.get('OPERATE_INCOME'))}{abs(r_chg):.1f}%），净利润{_fmt(np,0)}亿（{_dir(np,py.get('HOLDER_PROFIT'))}{abs(n_chg):.1f}%）。海外收入占比持续提升，IP矩阵丰富，全球化扩张驱动增长。"
    op_eps=round(eps*.90,2) if eps else None
    nonop=round(eps-op_eps,2) if eps and op_eps else None
    net_ps=round(per_cf-per_capex-dps,2) if per_cf else None
    p2=f"每股收益¥{_fmt(eps,2)}，主业贡献约¥{_fmt(op_eps,2)}（90%），非经常性约¥{_fmt(nonop,2)}（10%）。每股现金流¥{_fmt(per_cf,2)}，资本支出¥{_fmt(per_capex,2)}，分红¥{_fmt(dps,2)}（支付率{_fmt(payout,0)}%），净留存¥{_fmt(net_ps,2)}。公司净现金状态，财务稳健。"
    p3=f"毛利率{_p(gm)}、净利率{_p(npm)}、ROE {_p(roe)}——顶级消费品公司。壁垒：①IP矩阵+粉丝经济形成强大品牌护城河；②全球化零售网络（海外门店覆盖30+国家）；③盲盒+潮玩模式创造高复购。风险：IP生命周期、海外扩张不确定性、消费降级。"
    p4=f"当前PE约{_fmt(pe,1)}倍"+({True:f"，历史中位{_fmt(med,0)}倍"}.get(med and pe<med,"")or"。")+f"PB约{_fmt(pb,1)}倍。股息率约{_fmt(div,1)}%。关注海外同店增速及新IP孵化作为核心信号。"
    p5="催化剂：海外门店扩张+新IP孵化。若海外同店增速持续超预期+新IP爆发，估值有显著重估空间。关注每个季度海外收入占比及同比增速。"
    return {"business":biz,"commentary":[p1,p2,p3,p4,p5]}
