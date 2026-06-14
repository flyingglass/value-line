# -*- coding: utf-8 -*-
"""分众传媒 002027 — VL Business + AI Commentary (数据驱动)"""
def build(stock, metrics, revenue_structure, years, cagr, spot):
    ly=metrics.get(years[-1],{}) if years else {}
    py=metrics.get(years[-2],{}) if len(years)>=2 else {}
    def _chg(c,p): return (c/p-1)*100 if c and p and p>0 else None
    def _dir(c,p): return "增长" if (_chg(c,p) or 0)>0 else "下降"
    def _fmt(v,d=0): return f"{v:,.{d}f}" if v else "-"
    def _p(v): return f"{v:+.1f}%" if v else "-"
    rev,np,eps=ly.get("OPERATE_INCOME"),ly.get("HOLDER_PROFIT"),ly.get("BASIC_EPS")
    npm,roe=ly.get("NET_PROFIT_RATIO"),ly.get("ROE")
    r_chg,n_chg=_chg(rev,py.get("OPERATE_INCOME")),_chg(np,py.get("HOLDER_PROFIT"))
    per_cf,dps=ly.get("PER_NETCASH"),ly.get("DPS")or 0; payout=ly.get("PAYOUT_RATIO")
    pe,pb,div=spot.get("pe",0)or 0,spot.get("pb",0)or 0,spot.get("div_yield",0)or 0
    biz=f"分众传媒是中国最大的生活圈媒体平台，电梯电视+海报覆盖300城市4亿主流人群。营收{_fmt(rev,0)}亿（{_dir(rev,py.get('OPERATE_INCOME'))}{abs(r_chg):.1f}%），净利率{_p(npm)}，ROE {_p(roe)}。媒体资源壁垒深厚。"
    p1=f"2026年6月 — 分众传媒营收{_fmt(rev,0)}亿（{_dir(rev,py.get('OPERATE_INCOME'))}{abs(r_chg):.1f}%），净利润{_fmt(np,0)}亿（{_dir(np,py.get('HOLDER_PROFIT'))}{abs(n_chg):.1f}%）。消费品客户占比持续提升，AI赋能广告创作与智能排播提升运营效率。"
    p2=f"每股收益{_fmt(eps,2)}元，每股现金流{_fmt(per_cf,2)}元。分红{_fmt(dps,2)}元/股（支付率{_fmt(payout,0)}%），现金流充裕。点位租金趋于稳定，利润率改善空间大。"
    p3=f"净利率{_p(npm)}、ROE {_p(roe)}。壁垒：①280万电梯点位形成的规模优势难以复制；②品牌广告主粘性——消费品、互联网巨头首选投放渠道；③电梯场景独占性——封闭空间的强注意力。风险：宏观经济下行影响广告预算、新媒体分流、点位扩张边际递减。"
    p4=f"当前PE约{_fmt(pe,1)}倍，PB约{_fmt(pb,1)}倍，股息率约{_fmt(div,1)}%。关注消费品广告投放恢复及AI降本增效。"
    p5="催化剂：消费复苏驱动品牌广告预算回归+AI智能排播提升点位利用率。若Q2广告收入加速增长，估值修复空间显著。关注季度广告收入增速及刊挂率。"
    return {"business":biz,"commentary":[p1,p2,p3,p4,p5]}
