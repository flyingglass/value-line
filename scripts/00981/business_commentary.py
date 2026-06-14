# -*- coding: utf-8 -*-
"""中芯国际 00981 — VL Business + AI Commentary (数据驱动, PB估值)"""
def build(stock, metrics, revenue_structure, years, cagr, spot):
    ly=metrics.get(years[-1],{}) if years else {}
    py=metrics.get(years[-2],{}) if len(years)>=2 else {}
    def _chg(c,p): return (c/p-1)*100 if c and p and p>0 else None
    def _dir(c,p): return "增长" if (_chg(c,p) or 0)>0 else "下降"
    def _fmt(v,d=0): return f"{v:,.{d}f}" if v else "-"
    def _p(v): return f"{v:+.1f}%" if v else "-"
    rev,np,bps=ly.get("OPERATE_INCOME"),ly.get("HOLDER_PROFIT"),ly.get("BPS")
    roe=ly.get("ROE")
    r_chg=_chg(rev,py.get("OPERATE_INCOME"))
    pb,pe,div=spot.get("pb",0)or 0,spot.get("pe",0)or 0,spot.get("div_yield",0)or 0
    per_cf=ly.get("PER_NETCASH"); per_capex=ly.get("CAPEX_PS")or 0
    biz=f"中芯国际是中国大陆最大、技术最先进的晶圆代工企业，提供0.35μm到FinFET工艺服务。A+H双上市。营收{_fmt(rev,0)}亿（{_dir(rev,py.get('OPERATE_INCOME'))}{abs(r_chg):.1f}%），每股净资产{_fmt(bps,2)}元。资本开支极重，PB估值比CF更合理。"
    p1=f"2026年6月 — 中芯国际营收{_fmt(rev,0)}亿（{_dir(rev,py.get('OPERATE_INCOME'))}{abs(r_chg):.1f}%），净利润{_fmt(np,0)}亿。12英寸晶圆占比持续提升，FinFET/28nm收入占比增长。受益于中国半导体自主可控政策。"
    p2=f"每股净资产{_fmt(bps,2)}元，PB={_fmt(pb,2)}x。每股资本支出{_fmt(per_capex,2)}元（年支出超{_fmt(per_capex*79.67,0)}亿建晶圆厂），自由现金流长期为负。"
    p3=f"ROE {_p(roe)}。壁垒：①大陆最大晶圆代工厂，技术领先；②政策壁垒——中国半导体自主可控战略核心标的；③客户粘性——全工艺平台覆盖。风险：美国制裁升级、技术差距（无法获取EUV）、行业周期波动。"
    p4=f"当前PB约{_fmt(pb,1)}x，PE={_fmt(pe,1)}。适合长期价值投资者，关注28nm产能爬坡、稼动率趋势及政策支持力度。"
    p5="催化剂：半导体上行周期+国产替代加速。若产能利用率持续提升+先进制程突破，PB有重估空间。关注每季度产能利用率及28nm收入占比。"
    return {"business":biz,"commentary":[p1,p2,p3,p4,p5]}
