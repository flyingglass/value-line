# -*- coding: utf-8 -*-
"""阿里健康 00241.HK — VL Business + AI Commentary（手写定制）"""
def build(stock, metrics, revenue_structure, years, cagr, spot):
    ly = metrics.get(years[-1], {}) if years else {}
    py = metrics.get(years[-2], {}) if len(years) >= 2 else {}
    def _chg(c, p):
        try:
            c2, p2 = float(c), float(p)
            if not c2 or not p2: return None
            return (c2 / p2 - 1) * 100 if p2 > 0 else None
        except: return None
    def _num(v):
        try: return float(v)
        except: return 0
    def _fmt(v, d=0):
        try: return f"{float(v):,.{d}f}"
        except: return "-"

    rev = _num(ly.get("OPERATE_INCOME"))
    np_val = _num(ly.get("HOLDER_PROFIT"))
    eps = _num(ly.get("BASIC_EPS"))
    gm = _num(ly.get("GROSS_MARGIN"))
    npm = _num(ly.get("NET_PROFIT_RATIO"))
    roe = _num(ly.get("ROE"))
    bps = _num(ly.get("BPS"))
    per_cf = _num(ly.get("PER_NETCASH"))
    per_capex = _num(ly.get("CAPEX_PS") or 0)
    dps = _num(ly.get("DPS") or 0)
    payout = _num(ly.get("PAYOUT_RATIO") or 0)
    price = _num(spot.get("price", 0))
    pe = _num(spot.get("pe", 0))
    pb = _num(spot.get("pb", 0))
    div_y = _num(spot.get("div_yield", 0))
    med_pe = spot.get("median_pe")

    rev_prev = _num(py.get("OPERATE_INCOME"))
    np_prev = _num(py.get("HOLDER_PROFIT"))
    r_chg = _chg(rev, rev_prev) or 0
    n_chg = _chg(np_val, np_prev) or 0

    name = "阿里健康"

    # 营收结构
    prod_data = revenue_structure.get("by_product", []) if isinstance(revenue_structure, dict) else []
    parts = []
    for r in prod_data:
        parts.append(f'{r["name"]}{r["pct"]:.0f}%')
    rev_breakdown = "、".join(parts) if parts else ""

    # Business
    biz = (
        f'阿里健康是阿里巴巴集团在大健康领域的旗舰平台，FY2025营收{_fmt(rev, 0)}亿'
        f'（同比+{r_chg:.1f}%），归母净利{_fmt(np_val, 0)}亿'
        f'（同比+{n_chg:.1f}%），净利率{_fmt(npm, 1)}%，毛利率{_fmt(gm, 1)}%。'
        f'三大业务：{rev_breakdown}。'
        f'核心逻辑：医药电商规模效应兑现→利润率持续改善；'
        f'医疗健康服务为第二增长曲线；阿里生态协同提供流量+技术+数据壁垒。'
    )

    # P1: 业绩快照
    p1 = (
        f'FY2025（截至2025年3月），{name}营收{_fmt(rev, 0)}亿'
        f'（同比+{r_chg:.1f}%），归母净利{_fmt(np_val, 0)}亿'
        f'（同比+{n_chg:.1f}%），调整后净利约19.5亿（+35.6%）。'
        f'毛利率{_fmt(gm, 1)}%，同比提升2.5pp；净利率{_fmt(npm, 1)}%。'
    )

    # P2: 每股资金流向
    net_fcf = per_cf - per_capex - dps if per_cf else 0
    p2 = (
        f'每股收益{_fmt(eps, 3)}港元，每股经营现金流{_fmt(per_cf, 3)}港元。'
        f'资本支出{_fmt(per_capex, 3)}港元/股（轻资产平台模式），'
        f'自由现金流{_fmt(net_fcf, 3)}港元/股，'
        f'每股分红{_fmt(dps, 3)}港元（支付率{_fmt(payout, 0)}%），'
        f'每股净资产{_fmt(bps, 3)}港元。'
        + (f'现金流充裕，内生增长无需大量资本投入。' if net_fcf > 0 else f'现金流偏紧，关注应收账款和存货周转。')
    )

    # P3: 壁垒
    p3 = (
        f'毛利率{_fmt(gm, 1)}%，净利率{_fmt(npm, 1)}%，ROE {_fmt(roe, 1)}%。'
        f'阿里健康的核心壁垒：'
        f'①阿里生态流量——淘宝/天猫8亿+活跃用户导流，获客成本行业最低；'
        f'②供应链规模——国内最大医药电商平台，SKU和履约效率领先；'
        f'③数据和品牌信任——超3亿年度活跃消费者，品牌认知度无可替代；'
        f'④平台网络效应——买家多→商家多→品类多→买家更多（阿瑟式正反馈）。'
        f'风险：医药电商监管政策变化、行业竞争加剧（京东健康/美团买药）、对阿里生态依赖。'
    )

    # P4: 估值
    cf_15x_val = per_cf * 15
    cf_20x_val = per_cf * 20
    p4 = (
        f'当前PE{_fmt(pe, 1)}倍'
        + (f'，低于历史中位{_fmt(med_pe, 0)}x。' if med_pe and pe < med_pe else f'。')
        + f'PB{_fmt(pb, 2)}倍，股息率{_fmt(div_y, 1)}%。'
        f'每股现金流{_fmt(per_cf, 3)}港元，CF=15x对应{_fmt(cf_15x_val, 2)}港元'
        + (f'（较{_fmt(price, 2)}港元折价）' if cf_15x_val < price else f'（较{_fmt(price, 2)}港元溢价）')
        + f'。核心驱动：利润率持续改善+医药电商渗透率提升。'
    )

    # P5: 催化剂
    p5 = (
        f'催化剂：'
        f'①处方药外流——政策推动医院处方流向零售药店和医药电商，TAM持续扩大；'
        f'②AI+医疗——大模型赋能在线问诊、智能用药推荐，提升用户粘性和ARPU；'
        f'③利润率拐点——规模效应持续兑现，调整后净利率从5.3%→6.4%，目标8-10%。'
        f'风险：药品集采扩面影响自营毛利率、监管政策收紧。'
        f'关注每季活跃买家数、自营GMV增速和调整后净利率趋势。'
    )

    return {"business": biz, "commentary": [p1, p2, p3, p4, p5]}
