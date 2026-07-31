# -*- coding: utf-8 -*-
"""中国平安 601318 — VL Business + AI Commentary"""
def build(stock, metrics, revenue_structure, years, cagr, spot):
    ly = metrics.get(years[-1], {}) if years else {}
    py = metrics.get(years[-2], {}) if len(years) >= 2 else {}
    def _f(v,d=0): return f"{v:,.{d}f}" if v is not None else "-"
    def _p(v): return f"{v:+.1f}%" if v is not None else "-"
    eps = ly.get("BASIC_EPS"); bps = ly.get("BPS"); roe = ly.get("ROE")
    biz = f"中国平安是中国最大的综合金融集团，主营保险（寿险/产险）、银行、资产管理及科技。寿险代理人规模行业第一。FY{years[-1]}归母净利{_f(ly.get('HOLDER_PROFIT'),0)}亿，ROE {_p(roe)}。"
    p1 = f"2026年7月 — 中国平安归母净利润{_f(ly.get('HOLDER_PROFIT'),0)}亿，每股收益{_f(eps,2)}。寿险新业务价值（NBV）是核心观察指标，反映代理人渠道的质量改善趋势。综合金融+科技（平安好医生/陆金所/壹账通）双轮驱动。"
    p2 = f"每股收益¥{_f(eps,2)}，每股净资产{_f(bps,2)}。内含价值（EV）是保险股的核心估值锚，当前PEV（市值/内含价值）处于历史低位。2025年分红每股约¥{_f(ly.get('DPS'),2)}，股息率吸引。金融壹账通和平安好医生等科技板块价值未被充分定价。"
    p3 = f"ROE {_p(roe)}。壁垒：①品牌+渠道——1.5亿个人客户+6.3亿互联网用户，交叉销售率行业最高；②综合金融——保险+银行+资管一站式服务，客户迁移成本高；③科技投入——年研发投入150亿+，AI赋能代理人培训和理赔效率。风险：长端利率下行压缩利差、地产敞口减值、寿险需求疲软。"
    pe, pb = spot.get("pe",0), spot.get("pb",0)
    p4 = f"PE约{_f(pe,1)}倍，PB{_f(pb,1)}倍，PEV约0.6x（历史低位）。核心逻辑：①寿险改革（代理人提质增效）效果逐步显现→NBV恢复增长；②利率企稳+权益市场回暖→投资收益率改善；③科技子公司分拆上市（陆金所/好医生/壹账通）释放价值。当前估值处于10年低位，防御性突出。"
    p5 = "催化剂：①寿险NBV增速转正（代理人产能提升+产品结构优化）；②长端利率触底反弹→利差损担忧缓解；③平安银行零售转型成效释放；④地产风险出清+权益市场回暖→投资端弹性。关注每季度NBV增速和代理人数量/产能趋势。"
    return {"business": biz, "commentary": [p1,p2,p3,p4,p5]}
