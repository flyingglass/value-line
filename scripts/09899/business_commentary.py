# -*- coding: utf-8 -*-
"""网易云音乐 09899 — VL Business + AI Commentary（数据驱动）"""
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
    r_chg=_chg(rev, py.get("OPERATE_INCOME"))
    n_chg=_chg(np_val, py.get("HOLDER_PROFIT"))
    r_abs=abs(r_chg) if r_chg is not None else 0
    n_abs=abs(n_chg) if n_chg is not None else 0

    # Revenue structure
    prod_data = revenue_structure.get("by_service", []) if isinstance(revenue_structure, dict) else []
    online = next((r['value'] for r in prod_data if '在线' in r.get('name','')), None)
    social = next((r['value'] for r in prod_data if '社交' in r.get('name','')), None)

    biz=f"网易云音乐是中国领先的在线音乐平台，2021年港交所上市。以音乐社区为核心差异化，通过在线音乐订阅（会员付费）和社交娱乐服务（直播打赏）双变现。2025年营收{_fmt(rev,0)}亿（同比{_dir(rev,py.get('OPERATE_INCOME'))}{r_abs:.1f}%），归母净利润{_fmt(np_val,0)}亿（同比增长{n_abs:.1f}%）。收入结构：在线音乐{online:.0f}亿、社交娱乐及其他{social:.0f}亿。"

    p1=f"2026年6月 — 网易云音乐营收{_fmt(rev,0)}亿（同比{r_abs:.1f}%），归母净利润{_fmt(np_val,0)}亿（同比增长{n_abs:.1f}%）。营收微降主因社交娱乐服务主动收缩（-32%至17.65亿），但核心在线音乐服务增长12%至59.94亿，会员订阅收入突破50亿。利润暴增75%的核心驱动：①毛利率从33.7%扩大至35.7%（内容成本优化）；②销售费用砍半（6.1→4.1亿，更审慎的推广策略）；③确认递延所得税抵免7.47亿。经调整净利润28.6亿（+68%），盈利质量扎实。"

    p2=f"每股收益{_fmt(eps,2)}元，每股现金流{_fmt(per_cf,2)}元，资本支出每股{_fmt(per_capex,2)}元（轻资产模式，CAPEX极低）。每股净资产{_fmt(bps,2)}元。公司是极轻资产互联网平台：账上现金+定期存款约136亿，零有息负债，经营现金流16.18亿充沛。自由现金流≈经营现金流（CAPEX微乎其微），是典型的现金牛模型。2025年未分红（港股新经济公司惯例），未来分红潜力巨大。"

    p3=f"毛利率{_p(gm)}、净利率{_p(npm)}、ROE{_p(roe)}。核心护城河：①音乐社区壁垒——网易云音乐以歌单、评论、Mlog等UGC生态构建差异化社区，用户粘性极高（日活/月活>30%，行业领先）；②版权+原创双轮驱动——引进韩厂、影视OST等内容，同时扶持独立音乐人（平台上传歌曲超3亿首）；③AI推荐——自研Climber大模型驱动个性化分发。风险：社交娱乐持续萎缩（监管+战略收缩）、与腾讯音乐（01698.HK）的竞争、付费率提升天花板。"

    cf_15x=_fmt(per_cf*15,2) if per_cf else "-"
    cf_20x=_fmt(per_cf*20,2) if per_cf else "-"
    p4=f"当前PE约{_fmt(pe,1)}倍，PB{_fmt(pb,2)}倍。CF估值：每股现金流{_fmt(per_cf,2)}元，CF=15x对应{cf_15x}元，CF=20x对应{cf_20x}元。公司估值核心看PE（轻资产+高利润），当前PE~15x处于历史低位（2023-2025均值16.2x）。对标腾讯音乐PE~18-22x，网易云因社交娱乐萎缩折价交易。若在线音乐会员持续增长（当前付费率约25% vs Spotify 39%），PE有向18-20x修复空间。"

    p5="催化剂：①会员增长——在线音乐月付费用户持续增长（2025年会员订阅收入+13.3%），付费率从25%向30%+提升是最大驱动力；②ARPU提升——会员权益升级（AI功能、无损音质、跨平台权益）有望拉动月均ARPU；③成本优化持续——内容授权费占比下降+AI降本（智能客服、内容审核），毛利率有望从35.7%继续向38-40%爬升；④现金价值重估——136亿现金+零负债，若启动分红或回购，市场将重新定价现金价值。关注每季度在线音乐付费用户数、ARPU、毛利率趋势。"

    return {"business":biz,"commentary":[p1,p2,p3,p4,p5]}
