# -*- coding: utf-8 -*-
"""润泽科技 300442 — VL Business + AI Commentary（数据驱动）"""
def build(stock, metrics, revenue_structure, years, cagr, spot):
    ly = metrics.get(years[-1], {}) if years else {}
    py = metrics.get(years[-2], {}) if len(years) >= 2 else {}
    def _chg(c, p):
        try:
            c2, p2 = float(c), float(p)
            if not c2 or not p2: return None
            if p2 > 0: return (c2 / p2 - 1) * 100
            if c2 < 0 and p2 < 0: return (c2 - p2) / abs(p2) * 100
            return (c2 / p2 - 1) * 100
        except: return None
    def _dir(c, p):
        chg = _chg(c, p)
        return "增长" if (chg or 0) >= 0 else "下降"
    def _num(v):
        try: return float(v)
        except: return 0
    def _fmt(v, d=0):
        try: return f"{float(v):,.{d}f}"
        except: return "-"
    def _p(v):
        try: return f"{float(v):+.1f}%"
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
    pe = _num(spot.get("pe", 0)) or (round(price / eps, 1) if price and eps else 0)
    pb = _num(spot.get("pb", 0)) or (round(price / bps, 2) if price and bps else 0)
    div_y = _num(spot.get("div_yield", 0)) or (round(dps / price * 100, 1) if price and dps else 0)
    med_pe = spot.get("median_pe")

    rev_prev = _num(py.get("OPERATE_INCOME"))
    np_prev = _num(py.get("HOLDER_PROFIT"))
    r_chg = _chg(rev, rev_prev)
    n_chg = _chg(np_val, np_prev)
    r_abs = abs(r_chg) if r_chg is not None else 0
    n_abs = abs(n_chg) if n_chg is not None else 0

    name = stock.get("name", "润泽科技")

    # 营收结构
    prod_data = revenue_structure.get("by_product", []) if isinstance(revenue_structure, dict) else []
    prod_str_parts = [f'{r["name"]}{r["pct"]:.0f}%' for r in prod_data] if prod_data else []
    prod_str = "、".join(prod_str_parts) if prod_str_parts else ""

    # Business 描述
    biz = (
        f'润泽科技是国内领先的算力基础设施运营服务商，主营IDC（数据中心）和AIDC（智算中心）业务，'
        f'布局京津冀、长三角、粤港澳、成渝、甘肃、海南等九大园区，规划算力规模约6GW。'
        f'营收{_fmt(rev, 0)}亿（同比{_dir(rev, rev_prev)}{r_abs:.1f}%），'
        f'归母净利{_fmt(np_val, 0)}亿（同比{_dir(np_val, np_prev)}{n_abs:.1f}%），'
        f'净利率{_p(npm)}，ROE {_p(roe)}。'
        + (f'营收结构：{prod_str}。' if prod_str else '')
    )

    # P1: 业绩快照
    p1 = (
        f'{name}营收{_fmt(rev, 0)}亿（同比{_dir(rev, rev_prev)}{r_abs:.1f}%），'
        f'归母净利润{_fmt(np_val, 0)}亿（同比{_dir(np_val, np_prev)}{n_abs:.1f}%）。'
        f'毛利率{_p(gm)}，净利率{_p(npm)}。'
    )

    # P2: 每股资金流向
    net_fcf = round(per_cf - per_capex - dps, 2) if per_cf else None
    p2 = (
        f'每股收益{_fmt(eps, 2)}元，每股经营现金流{_fmt(per_cf, 2)}元，'
        f'资本支出每股{_fmt(per_capex, 2)}元（重资产扩张期）。'
        + (f'自由现金流{net_fcf}元/股，' if net_fcf is not None else '')
        + f'分红{_fmt(dps, 2)}元/股（支付率{_fmt(payout, 0)}%），'
        + f'每股净资产{_fmt(bps, 2)}元。'
    )

    # P3: 业务质地与壁垒
    p3 = (
        f'毛利率{_p(gm)}，净利率{_p(npm)}，ROE {_p(roe)}。'
        f'AIDC龙头核心壁垒：①资源卡位——九大园区布局核心枢纽城市，'
        f'土地+能耗指标稀缺性构成进入壁垒；'
        f'②客户锁定——深度绑定头部互联网和云厂商，签约锁定率极高；'
        f'③先发规模——规划6GW算力规模国内领先，单位成本持续下降。'
        f'风险：重资产高负债、客户集中度高、AI算力需求周期性波动、电费成本上行。'
    )

    # P4: 估值锚定
    cf_15x_val = per_cf * 15 if per_cf else 0
    cf_20x_val = per_cf * 20 if per_cf else 0
    vs_price = '溢价' if cf_15x_val > price else '折价'
    p4 = (
        f'当前PE{_fmt(pe, 1)}倍'
        + (f'，低于历史中位{_fmt(med_pe, 0)}x' if med_pe and pe < med_pe else '')
        + f'。PB{_fmt(pb, 2)}倍，股息率{_fmt(div_y, 1)}%。'
        f'CF估值：每股现金流{_fmt(per_cf, 2)}元，CF=15x对应{_fmt(cf_15x_val, 2)}元'
        + (f'（较当前{_fmt(price, 2)}元{vs_price}）' if price else '')
        + f'。'
    )

    # P5: 催化剂与风险
    p5 = (
        f'催化剂：①AI算力超级周期——大模型训练+推理需求爆发驱动AIDC上架率持续提升；'
        f'②液冷技术领先——PUE低至1.09，能耗效率行业标杆，碳中和政策利好；'
        f'③海外扩张——自建+收购并举拓展东南亚/中东市场。'
        f'风险：算力需求不及预期、电费成本上行、客户集中度风险。'
        f'关注每季AIDC上架率、新签客户和海外项目落地进展。'
    )

    return {"business": biz, "commentary": [p1, p2, p3, p4, p5]}
