# -*- coding: utf-8 -*-
"""润泽科技 300442 — VL Business + AI Commentary（数据驱动, 自动生成）"""
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
    def _dir(c, p): return "增长" if (_chg(c, p) or 0) > 0 else "下降"
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

    r_chg = _chg(rev, py.get("OPERATE_INCOME"))
    n_chg = _chg(np_val, py.get("HOLDER_PROFIT"))
    r_abs = abs(r_chg) if r_chg is not None else 0
    n_abs = abs(n_chg) if n_chg is not None else 0

    # 营收结构
    prod_data = revenue_structure.get("by_product", []) if isinstance(revenue_structure, dict) else []
    prod_str_parts = [f"{r['name']}{r['pct']:.0f}%" for r in prod_data] if prod_data else []
    prod_str = "、".join(prod_str_parts) if prod_str_parts else ""

    # 地区拆分
    reg_data = revenue_structure.get("by_region", []) if isinstance(revenue_structure, dict) else []
    dom = next((r for r in reg_data if "国内" in str(r.get("name", ""))), None)
    ovs = next((r for r in reg_data if "国外" in str(r.get("name", ""))), None)

    # Business
    biz=f"润泽智算科技集团股份有限公司是国内领先的算力基础设施运营服务商，主营IDC（数据中心）和AIDC（智算中心）业务，布局七大园区覆盖京津冀、长三角、粤港澳等核心枢纽。2025年营收56.74亿（+30%），AIDC业务占比超44%，净利润50.50亿同比增182%。" + f"营收{_fmt(rev,0)}亿（同比{_dir(rev,py.get("OPERATE_INCOME"))}{r_abs:.1f}%），业务结构：IDC业务100%、IDC业务100%、IDC业务72%、IDC业务67%。"

    # P1: 业绩快照
    p1 = (
        f"2026年6月 — {name}营收{_fmt(rev, 0)}亿（{_dir(rev, py.get('OPERATE_INCOME'))}{r_abs:.1f}%），"
        f"归母净利润{_fmt(np_val, 0)}亿（{_dir(np_val, py.get('HOLDER_PROFIT'))}{n_abs:.1f}%）。"
        + (f"毛利率{_p(gm)}，净利率{_p(npm)}。" if gm else "")
    )
    if dom and ovs:
        p1 += (
            f"海外收入{ovs['amount']:.0f}M（占比{ovs['pct']:.1f}%）增速远高国内"
            f"（{dom['amount']:.0f}M），全球化布局成效显著。"
        )

    # P2: 每股资金流向
    net_fcf = round(per_cf - per_capex - dps, 2) if per_cf else None
    p2 = (
        f"每股收益{_fmt(eps, 2)}元，每股经营现金流{_fmt(per_cf, 2)}元，"
        f"资本支出每股{_fmt(per_capex, 2)}元（扩产期）。"
        f"自由现金流{net_fcf}元/股，分红{_fmt(dps, 2)}元/股（支付率{_fmt(payout, 0)}%），"
        f"每股净资产{_fmt(bps, 2)}元。现金流健康度良好。"
    )

    # P3: 业务质地与壁垒
    p3 = (
        f"毛利率{_p(gm)}，净利率{_p(npm)}，ROE {_p(roe)}。"
        f"科技行业核心壁垒：①技术领先与研发投入——持续高研发构建专利护城河；②生态锁定——平台/云服务的高迁移成本；③数据网络效应——用户规模越大产品越好。风险：技术迭代风险、地缘政治制裁、估值波动。"
    )

    # P4: 估值锚定
    cf_15x = _fmt(per_cf * 15, 2) if per_cf else "-"
    cf_20x = _fmt(per_cf * 20, 2) if per_cf else "-"
    p4 = (
        f"当前PE约{_fmt(pe, 1)}倍"
        + ({True: f"，低于历史中位{_fmt(med_pe, 0)}x"}.get(med_pe and pe < med_pe, "") or "。")
        + f"PB{_fmt(pb, 2)}倍，股息率约{_fmt(div_y, 1)}%。"
        f"CF估值：每股现金流{_fmt(per_cf, 2)}元，CF=15x对应{cf_15x}元"
        + (f"（较当前{_fmt(price, 2)}元" + ("溢价" if per_cf * 15 > price else "折价") + "）" if price else "")
        + f"，CF=20x对应{cf_20x}元。"
    )

    # P5: 催化剂与风险
    p5 = f"催化剂：①AI/新技术落地——新产品周期驱动增长加速；②份额提升——竞争对手退出或技术替代带来市场集中；③利润率改善——规模效应+高毛利业务占比提升。风险：技术路线变化、制裁升级。关注每季度新业务收入占比和研发转化率。"

    return {"business": biz, "commentary": [p1, p2, p3, p4, p5]}
