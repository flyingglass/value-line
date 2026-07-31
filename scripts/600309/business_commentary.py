# -*- coding: utf-8 -*-
"""万华化学 600309 — VL Business + AI Commentary"""
def build(stock, metrics, revenue_structure, years, cagr, spot):
    ly = metrics.get(years[-1], {}) if years else {}
    py = metrics.get(years[-2], {}) if len(years) >= 2 else {}
    def _c(c,p): return (c/p-1)*100 if c and p and p>0 else None
    def _f(v,d=0): return f"{v:,.{d}f}" if v is not None else "-"
    def _p(v): return f"{v:+.1f}%" if v is not None else "-"
    rev, npv, eps = ly.get("OPERATE_INCOME"), ly.get("HOLDER_PROFIT"), ly.get("BASIC_EPS")
    gm, npm, roe = ly.get("GROSS_MARGIN"), ly.get("NET_PROFIT_RATIO"), ly.get("ROE")
    rc, nc = _c(rev, py.get("OPERATE_INCOME")), _c(npv, py.get("HOLDER_PROFIT"))
    per_cf = ly.get("PER_NETCASH"); bps = ly.get("BPS")
    biz = f"万华化学是全球MDI龙头，MDI产能全球第一（约310万吨/年），主营聚氨酯、石化、精细化学品。技术壁垒极高（全球仅5家掌握MDI核心技术）。FY{years[-1]}营收{_f(rev,0)}亿，净利{_f(npv,0)}亿，净利率{_p(npm)}，ROE {_p(roe)}。"
    p1 = f"2026年7月 — 万华化学营收{_f(rev,0)}亿，归母净利{_f(npv,0)}亿。毛利率{_p(gm)}、净利率{_p(npm)}。MDI价格周期波动是最大利润变量，2025年MDI价差有所改善。全球MDI新增产能有限，公司市占率有望进一步提升。"
    p2 = f"每股收益¥{_f(eps,2)}，每股净资产{_f(bps,2)}，经营现金流¥{_f(per_cf,2)}。全球唯一掌握MDI全产业链技术的中国企业，持续高研发投入（年50亿+），在ADI、TPU、PC等新材料领域不断突破。资本开支大（年均数百亿），但MDI超高ROIC确保资本配置效率。"
    p3 = f"毛利率{_p(gm)}、净利率{_p(npm)}、ROE {_p(roe)}。壁垒：①MDI技术垄断——全球仅万华/巴斯夫/科思创/亨斯迈/陶氏5家，技术封锁极严；②一体化园区——烟台/宁波/匈牙利三大基地，园区化生产极致降本；③新材料管线——尼龙12、柠檬醛等突破卡脖子技术。风险：MDI价格周期性、全球宏观经济下行、海外反倾销。"
    pe, pb = spot.get("pe",0), spot.get("pb",0)
    p4 = f"PE约{_f(pe,1)}倍，PB{_f(pb,1)}倍。核心逻辑：①MDI行业供给刚性（全球年增量仅3-4%），需求增长（建筑保温+汽车轻量化）支撑长期量价；②化工新材料转型（POE/尼龙12/碳纤维）打开估值天花板；③周期底部布局——MDI价差处于历史低位，盈利弹性极大。关注每月MDI挂牌价。"
    p5 = f"催化剂：①MDI价差触底回升——全球地产+汽车/家电需求回暖；②POE粒子国产替代（光伏胶膜核心材料），千亿市场空间；③匈牙利基地扩产验证全球化能力；④柠檬醛/尼龙12等高壁垒新材料量产，打破海外垄断。关注MDI-纯苯价差季度走势。"
    return {"business": biz, "commentary": [p1,p2,p3,p4,p5]}
