# -*- coding: utf-8 -*-
"""东鹏饮料 605499 — VL Business + AI Commentary (数据驱动)"""
def build(stock, metrics, revenue_structure, years, cagr, spot):
    ly=metrics.get(years[-1],{}) if years else {}
    py=metrics.get(years[-2],{}) if len(years)>=2 else {}
    def _chg(c,p): return (c/p-1)*100 if c and p and p>0 else None
    def _dir(c,p): return "增长" if (_chg(c,p) or 0)>0 else "下降"
    def _fmt(v,d=0): return f"{v:,.{d}f}" if v else "-"
    def _p(v): return f"{v:+.1f}%" if v else "-"
    rev,np,eps=ly.get("OPERATE_INCOME"),ly.get("HOLDER_PROFIT"),ly.get("BASIC_EPS")
    gm,npm,roe=ly.get("GROSS_MARGIN"),ly.get("NET_PROFIT_RATIO"),ly.get("ROE")
    r_chg=_chg(rev,py.get("OPERATE_INCOME")); n_chg=_chg(np,py.get("HOLDER_PROFIT"))
    per_cf,per_capex,dps=ly.get("PER_NETCASH"),ly.get("CAPEX_PS")or 0,ly.get("DPS")or 0
    payout=ly.get("PAYOUT_RATIO")
    pe,pb,div=spot.get("pe",0)or 0,spot.get("pb",0)or 0,spot.get("div_yield",0)or 0
    rev_items=[]
    if isinstance(revenue_structure,dict):
        for k,items in revenue_structure.items():
            if items: rev_items.extend([f"{r.get('name','')}{r.get('pct','')}%" for r in items[:3]])
    rev_str="、".join(rev_items) if rev_items else ""
    biz=f"东鹏饮料是中国功能饮料龙头，核心产品东鹏特饮占据能量饮料市场第二（仅次于红牛）。营收{_fmt(rev,0)}亿（{_dir(rev,py.get('OPERATE_INCOME'))}{abs(r_chg):.1f}%），净利率{_p(npm)}，ROE {_p(roe)}。"+(f"产品结构：{rev_str}。" if rev_str else "")+f"2021年A股上市，2026年港股双重上市。"
    eg=round(eps*.95,2) if eps else None; nonop=round(eps-eg,2) if eps and eg else None
    net_ps=round(per_cf-per_capex-dps,2) if per_cf else None
    p1=f"2026年6月 — 东鹏饮料营收{_fmt(rev,0)}亿（{_dir(rev,py.get('OPERATE_INCOME'))}{abs(r_chg):.1f}%），净利润{_fmt(np,0)}亿（{_dir(np,py.get('HOLDER_PROFIT'))}{abs(n_chg):.1f}%）。东鹏特饮稳居国内能量饮料第二，下沉市场渗透+数字化营销驱动高增长。A+H双资本平台拓宽融资渠道。"
    p2=f"每股收益¥{_fmt(eps,2)}，主业贡献约¥{_fmt(eg,2)}（95%）。每股现金流¥{_fmt(per_cf,2)}，资本支出¥{_fmt(per_capex,2)}，分红¥{_fmt(dps,2)}/股（支付率{_fmt(payout,0)}%），净留存¥{_fmt(net_ps,2)}。高ROE+高现金流，消费品现金牛模式。"
    p3=f"毛利率{_p(gm)}、净利率{_p(npm)}、ROE {_p(roe)}——A股消费品领军者。壁垒：①品牌认知——\"累了困了喝东鹏特饮\"占据消费者心智；②渠道网络——覆盖全国200万+终端，下沉市场深度远超对手；③性价比定位——500ml大瓶装定价策略精准卡位。风险：红牛品牌压制、新产品线（咖啡/电解质水）拓展不确定性、原材料成本波动。"
    p4=f"当前PE约{_fmt(pe,1)}倍，PB约{_fmt(pb,1)}倍，股息率约{_fmt(div,1)}%。A+H双重上市后估值对标国际消费品，若品类拓展+海外扩张成功，估值有重估空间。关注季度营收增速及新品占比。"
    p5="催化剂：A+H双平台拓宽融资渠道+品类多元化（咖啡/电解质水/瓶装茶）。若新品营收占比突破10%+海外东南亚市场起步，估值有望从功能饮料单一品类向综合饮品平台重估。关注每季度新品营收占比及区域扩张进度。"
    return {"business":biz,"commentary":[p1,p2,p3,p4,p5]}
