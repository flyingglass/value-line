# -*- coding: utf-8 -*-
"""安琪酵母 600298 — VL Business + AI Commentary（精调版）"""
def build(stock, metrics, revenue_structure, years, cagr, spot):
    ly = metrics.get(years[-1], {}) if years else {}
    py = metrics.get(years[-2], {}) if len(years) >= 2 else {}
    pp = metrics.get(years[-3], {}) if len(years) >= 3 else {}
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
    def _arrow(c, p):
        ch = _chg(c, p)
        if ch is None: return ""
        return "↗️" if ch > 0 else ("↘️" if ch < 0 else "➡️")

    rev = _num(ly.get("OPERATE_INCOME"))
    np_val = _num(ly.get("HOLDER_PROFIT"))
    eps = _num(ly.get("BASIC_EPS"))
    gm = _num(ly.get("GROSS_MARGIN"))
    npm = _num(ly.get("NET_PROFIT_RATIO"))
    roe = _num(ly.get("ROE"))
    roic = _num(ly.get("ROIC"))
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
    gm_chg = _chg(gm, py.get("GROSS_MARGIN"))
    r_abs = abs(r_chg) if r_chg is not None else 0
    n_abs = abs(n_chg) if n_chg is not None else 0

    # 营收结构
    prod_data = revenue_structure.get("by_product", []) if isinstance(revenue_structure, dict) else []
    yeast = next((r for r in prod_data if "酵母" in str(r.get("name", ""))), None)
    reg_data = revenue_structure.get("by_region", []) if isinstance(revenue_structure, dict) else []
    dom = next((r for r in reg_data if "国内" in str(r.get("name", ""))), None)
    ovs = next((r for r in reg_data if "国外" in str(r.get("name", ""))), None)

    # Business 描述
    biz = (
        f"安琪酵母是亚洲第一、全球第二的酵母公司（仅次于法国乐斯福），"
        f"主营酵母及深加工产品（面包酵母、酵母抽提物YE、酿酒酵母等），"
        f"产品出口170+个国家和地区，国内市占率55%遥遥领先。"
        f"2025年营收{_fmt(rev, 0)}亿（同比{_dir(rev, py.get('OPERATE_INCOME'))}{r_abs:.1f}%），"
        f"归母净利润{_fmt(np_val, 0)}亿（{_dir(np_val, py.get('HOLDER_PROFIT'))}{n_abs:.1f}%）。"
        + (f"酵母及深加工占比{yeast['pct']:.0f}%，发酵总产能49万吨。" if yeast else "")
    )

    # P1: 业绩快照
    p1 = (
        f"2026年6月 — 安琪酵母2025年营收{_fmt(rev, 0)}亿（{_dir(rev, py.get('OPERATE_INCOME'))}{r_abs:.1f}%），"
        f"归母净利润{_fmt(np_val, 0)}亿（{_dir(np_val, py.get('HOLDER_PROFIT'))}{n_abs:.1f}%）。"
        f"酵母及深加工收入119.5亿，销量46.8万吨（+15.8%），以量补价态势延续。"
        f"食品原料22.2亿（+54.4%）为增长最快板块，酵母蛋白新品类放量；"
        f"制糖13.4亿毛利率-4.9%拖累综合毛利。"
    )
    if dom and ovs:
        p1 += (
            f"海外收入{ovs['amount']:.0f}M（占比{ovs['pct']:.1f}%，+19.9%）增速远超国内"
            f"（{dom['amount']:.0f}M，+4.1%），海外毛利率32.1%远高于国内19.7%，"
            f"全球化布局成效显著。"
        )

    # P2: 每股资金流向
    net_fcf = round(per_cf - per_capex - dps, 2) if per_cf else None
    p2 = (
        f"每股收益{_fmt(eps, 2)}元，每股经营现金流{_fmt(per_cf, 2)}元，"
        f"资本支出每股{_fmt(per_capex, 2)}元（海外产能扩张期）。"
        f"自由现金流{net_fcf}元/股，分红{_fmt(dps, 2)}元/股（支付率{_fmt(payout, 0)}%），"
        f"每股净资产{_fmt(bps, 2)}元。"
        f"总资产256.6亿，资产负债率49.3%，有息负债占比可控。"
        f"经营现金流24.8亿覆盖资本开支20.0亿，海外建厂高峰期现金流偏紧但无断裂风险。"
    )

    # P3: 业务质地与壁垒
    p3 = (
        f"毛利率{_p(gm)}（{_arrow(gm, py.get('GROSS_MARGIN'))} +{_chg(gm, py.get('GROSS_MARGIN')):.1f}pp，"
        f"2021年以来首次企稳回升），净利率{_p(npm)}，ROE {_p(roe)}，ROIC {_p(roic)}%。"
        f"酵母行业核心壁垒："
        f"①规模与成本——全球第二大产能49万吨，糖蜜采购议价力强（最大买家），"
        f"规模效应摊薄固定成本；"
        f"②渠道网络——覆盖170+国，海外6个生产基地（埃及、俄罗斯等）本地化供应，"
        f"关税壁垒下竞争优势强化；"
        f"③技术壁垒——菌种选育+发酵工艺Know-how（四十年积累），"
        f"YE替代味精趋势明确，国内YE市占率60%+；"
        f"④品牌心智——安琪=中国酵母代名词，B端客户切换成本高。"
        f"风险：糖蜜价格波动（占成本40%+，2021年暴涨致毛利率断崖37.6%→27.3%）、"
        f"海外地缘政治（俄罗斯工厂）、制糖业务持续亏损。"
    )

    # P4: 估值锚定
    cf_15x = _fmt(per_cf * 15, 2) if per_cf else "-"
    cf_20x = _fmt(per_cf * 20, 2) if per_cf else "-"
    p4 = (
        f"当前PE约{_fmt(pe, 1)}倍"
        + ({True: f"，低于历史中位{_fmt(med_pe, 0)}x，处于历史低区（百分位-15%）"}.get(med_pe and pe < med_pe, "") or "。")
        + f"PB{_fmt(pb, 2)}倍，股息率约{_fmt(div_y, 1)}%。"
        f"CF估值：每股现金流{_fmt(per_cf, 2)}元，CF=15x对应{cf_15x}元"
        + (f"（较当前{_fmt(price, 2)}元" + ("溢价" if per_cf * 15 > price else "折价") + "）" if price else "")
        + f"，CF=20x对应{cf_20x}元。"
        f"历史PE区间23-47x，当前PE处于历史低位，具备安全边际。"
    )

    # P5: 催化剂与转折点
    p5 = (
        f"催化剂：①海外产能释放——埃及/俄罗斯工厂扩产，海外毛利率32%远高于国内，"
        f"海外收入占比从41%向50%提升将结构性改善盈利；"
        f"②酵母蛋白新品类——替代植物蛋白趋势，食品原料板块54%增速有望持续；"
        f"③YE渗透率提升——酵母抽提物替代味精空间大，YE毛利率高于传统酵母；"
        f"④毛利率企稳回升——2025年毛利率{_p(gm)}（+{_chg(gm, py.get('GROSS_MARGIN')):.1f}pp），"
        f"若糖蜜价格回归历史均值，毛利率可修复至30%+。"
        f"关注每季度海外收入增速及酵母主业毛利率作为核心信号。"
    )

    return {"business": biz, "commentary": [p1, p2, p3, p4, p5]}
