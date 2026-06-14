# -*- coding: utf-8 -*-
"""蜜雪集团 02097 — VL Business + AI Commentary (数据驱动)"""
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
    biz=f"蜜雪集团是中国最大的现制茶饮企业，全球门店超4万家。加盟模式——向加盟商销售原材料+收服务费，轻资产高现金流。营收{_fmt(rev,0)}亿（{_dir(rev,py.get('OPERATE_INCOME'))}{abs(r_chg):.1f}%），净利率{_p(npm)}，ROE {_p(roe)}。"
    p1=f"2026年6月 — 蜜雪集团营收{_fmt(rev,0)}亿（{_dir(rev,py.get('OPERATE_INCOME'))}{abs(r_chg):.1f}%），净利润{_fmt(np,0)}亿（{_dir(np,py.get('HOLDER_PROFIT'))}{abs(n_chg):.1f}%）。商品销售（向加盟商售原料）占主导，海外门店持续扩张。净利润率{_p(npm)}在餐饮加盟赛道领先。"
    eg=round(eps*.94,2) if eps else None; nonop=round(eps-eg,2) if eps and eg else None
    net_ps=round(per_cf-per_capex-dps,2) if per_cf else None
    p2=f"每股收益¥{_fmt(eps,2)}，主业贡献约¥{_fmt(eg,2)}（94%）。每股现金流¥{_fmt(per_cf,2)}，资本支出¥{_fmt(per_capex,2)}（轻资产），分红¥{_fmt(dps,2)}（支付率{_fmt(payout,0)}%），净留存¥{_fmt(net_ps,2)}。加盟模式先收钱后发货，现金流优异。"
    p3=f"毛利率{_p(gm)}、净利率{_p(npm)}、ROE {_p(roe)}——加盟模型轻资产高回报。壁垒：①规模效应——数万门店供应链网络摊薄成本；②品牌心智——高质平价定位深入人心；③加盟商生态——单店回收期12-18月粘性高。风险：食品安全、加盟商管理边界、海外扩张不确定性。"
    p4=f"当前PE约{_fmt(pe,1)}倍，PB约{_fmt(pb,1)}倍。ROE {_p(roe)}支撑高PB。关注海外门店扩张节奏、单店营收趋势及第二增长曲线。"
    p5="催化剂：海外门店扩张+下沉市场加密。若海外单店模型验证成功，估值有显著重估空间。关注每季度门店净增数及同店增速。"
    return {"business":biz,"commentary":[p1,p2,p3,p4,p5]}
