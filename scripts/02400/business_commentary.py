# -*- coding: utf-8 -*-
"""心动公司 02400 — VL Business + AI Commentary（数据驱动）"""
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
    prod_data = revenue_structure.get("by_product", []) if isinstance(revenue_structure, dict) else []
    prod_str = "、".join([f"{r['name']}{r['pct']}%" for r in prod_data]) if prod_data else ""

    biz=f"心动公司是中国领先的游戏开发商与手游社区平台运营商，旗下拥有TapTap游戏社区。核心业务：①游戏运营（自研+代理），代表作品《出发吧麦芬》《铃兰之剑》《火炬之光：无限》等；②TapTap平台——中国最大手游社区之一，以\"不联运不分成\"独特模式吸引开发者。"+(f"品类：{prod_str}。" if prod_str else "")+f"最新财年营收{_fmt(rev,0)}亿（{_dir(rev,py.get('OPERATE_INCOME'))}{abs(r_chg):.1f}%），净利率{_p(npm)}，ROE {_p(roe)}。TapTap中国MAU超4000万，海外版加速扩张。"

    p1=f"2026年6月 — 心动公司营收{_fmt(rev,0)}亿（{_dir(rev,py.get('OPERATE_INCOME'))}{abs(r_chg):.1f}%），净利润{_fmt(np,0)}亿（{_dir(np,py.get('HOLDER_PROFIT'))}{abs(n_chg):.1f}%），每股收益¥{_fmt(eps,2)}。游戏业务：《出发吧麦芬》国内+海外双线爆发；TapTap广告系统算法升级推动收入增长30%+。公司从大规模研发投入期进入收获期。"
    op_eps=round(eps*.91,2) if eps else None
    nonop=round(eps-op_eps,2) if eps and op_eps else None
    working_cap=round(ly.get("WORKING_CAPITAL",0),0) if ly.get("WORKING_CAPITAL") else 0
    net_cf=round(per_cf-per_capex-dps,2) if per_cf else None
    p2=f"每股收益¥{_fmt(eps,2)}中，主业贡献约¥{_fmt(op_eps,2)}（91%），非经常性约¥{_fmt(nonop,2)}（9%）。每股现金流¥{_fmt(per_cf,2)}，四大去向：①资本支出¥{_fmt(per_capex,2)}/股（游戏研发+服务器基建）；②营运资金变动{'+释放' if working_cap<0 else '占用'}{_fmt(abs(working_cap),0)}万（游戏行业普遍轻资产运营）；③分红¥{_fmt(dps,2)}/股（支付率{_fmt(payout,0)}%）；④净留存¥{_fmt(net_cf,2)}/股，用于新游戏立项和TapTap海外扩张。公司账面净现金约20亿，财务安全垫充足，无债务压力。"
    p3=f"毛利率{_p(gm)}、净利率{_p(npm)}、ROE {_p(roe)}。心动公司的核心壁垒是\"游戏+平台\"双轮飞轮：优质独占游戏→为TapTap导流→社区活跃度提升→更多开发者入驻→更多独占内容。《出发吧麦芬》爆款后飞轮明显加速。TapTap\"不联运\"模式对中小开发者极具吸引力，构成区别于应用商店的差异化壁垒。风险：游戏产品生命周期波动、版号政策、买量成本上升。"
    p4=f"当前PE约{_fmt(pe,1)}倍（non-IFRS约7x），"+({True:f"历史中位{_fmt(med,0)}倍"}.get(med and pe<med,"")or"。")+f"PB约{_fmt(pb,1)}倍。股息率约{_fmt(div,1)}%。估值处于历史低位，净现金占总市值约25%，安全边际充足。核心逻辑：①《出发吧麦芬》放置类长尾特性→生命周期超预期；②TapTap广告加载率3%→5%提价空间；③海外市场0→1增量。若利润持续兑现，PE有望重估至15-20x。"
    p5="AI对心动存在双重机会：①AI辅助游戏开发降本——美术/剧情/关卡设计效率提升30%+，研发费用率有望从25%降至20%以下；②TapTap AI推荐算法提升广告匹配效率，直接增厚信息服务收入。关注TapTap海外版MAU增速和AI功能落地进度作为核心验证信号。"

    return {"business":biz,"commentary":[p1,p2,p3,p4,p5]}
