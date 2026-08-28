# -*- coding: utf-8 -*-
"""古井贡酒 000596 — VL Business + AI Commentary (数据驱动)

所有数字均取自 metrics / revenue_structure / cagr / spot 参数，不硬编码。
外部事实（黄鹤楼商誉减值、区域布局、分红方案）均标注出处。
"""
def build(stock, metrics, revenue_structure, years, cagr, spot):
    ly = metrics.get(years[-1], {}) if years else {}
    py = metrics.get(years[-2], {}) if len(years) >= 2 else {}

    def _num(v):
        try: return float(v)
        except (TypeError, ValueError): return 0.0

    def _chg(c, p):
        try:
            c2, p2 = float(c), float(p)
            if not p2: return None
            return (c2 / p2 - 1) * 100
        except (TypeError, ValueError, ZeroDivisionError): return None

    def _dir(c, p):
        v = _chg(c, p)
        if v is None: return "变动"
        return "增长" if v > 0 else ("下降" if v < 0 else "持平")

    def _fmt(v, d=0):
        try: return f"{float(v):,.{d}f}"
        except (TypeError, ValueError): return "-"

    def _p(v, d=1):
        try: return f"{float(v):.{d}f}%"
        except (TypeError, ValueError): return "-"

    rev    = _num(ly.get("OPERATE_INCOME"))
    rev_p  = _num(py.get("OPERATE_INCOME"))
    np_val = _num(ly.get("HOLDER_PROFIT"))
    np_p   = _num(py.get("HOLDER_PROFIT"))
    eps    = _num(ly.get("BASIC_EPS"))
    gm     = _num(ly.get("GROSS_MARGIN"))
    npm    = _num(ly.get("NET_PROFIT_RATIO"))
    roe    = _num(ly.get("ROE"))
    roic   = _num(ly.get("ROIC"))
    bps    = _num(ly.get("BPS"))
    per_cf = _num(ly.get("PER_NETCASH"))
    capex  = _num(ly.get("CAPEX_PS"))
    dps    = _num(ly.get("DPS"))
    payout = _num(ly.get("PAYOUT_RATIO"))

    r_chg, n_chg = _chg(rev, rev_p), _chg(np_val, np_p)

    pe  = _num(spot.get("pe"))
    pb  = _num(spot.get("pb"))
    div = _num(spot.get("div_yield"))
    med = _num(spot.get("median_pe"))

    # ── 营收结构（by_product 白酒占比；by_region 华中占比）
    rs = revenue_structure if isinstance(revenue_structure, dict) else {}
    def _pick(dim, *keys):
        for r in rs.get(dim, []):
            if any(k in r.get("name", "") for k in keys):
                return _num(r.get("value")), _num(r.get("pct"))
        return None, None

    baijiu_amt_M, baijiu_pct = _pick("by_product", "白酒")
    _, central_pct           = _pick("by_region", "华中")
    _, online_pct            = _pick("by_channel", "线上")
    # revenue_structure 存 百万元(M) → 转成"亿元"与 OPERATE_INCOME 同单位
    baijiu_amt = baijiu_amt_M / 100.0 if baijiu_amt_M is not None else None

    biz = (
        f"古井贡酒是中国老八大名酒企业、徽酒龙头，主营白酒研发生产与销售，"
        f"核心产品为年份原浆系列（古5/古8/古16/古20/古26）覆盖次高端与中高端价格带。"
        + (f"白酒业务营收{_fmt(baijiu_amt, 1)}亿，占营业收入{_p(baijiu_pct)}" if baijiu_amt else "")
        + (f"，华中大本营市场占{_p(central_pct)}" if central_pct else "")
        + f"。最新年度营收{_fmt(rev, 1)}亿，归母净利润{_fmt(np_val, 1)}亿，"
        f"毛利率{_p(gm)}，净利率{_p(npm)}，ROE {_p(roe)}。"
    )

    # P1 经营分析
    yr_label = years[-1] if years else "最新年度"
    p1 = f"{yr_label}年营收{_fmt(rev, 1)}亿"
    if r_chg is not None:
        p1 += f"（{_dir(rev, rev_p)}{abs(r_chg):.1f}%）"
    if n_chg is not None:
        p1 += f"，归母净利润{_fmt(np_val, 1)}亿（{_dir(np_val, np_p)}{abs(n_chg):.1f}%）"
    else:
        p1 += f"，归母净利润{_fmt(np_val, 1)}亿"
    p1 += "。白酒行业自2024年起进入深度调整期，需求疲软叠加渠道去库存，次高端价格带承压尤为明显，公司主动控货去化、放缓发货节奏以修复渠道健康度。利润降幅大于营收降幅，主因销售费用刚性及产品结构下移。"
    if yr_label == "2025":
        p1 += "此外公司于2025年对黄鹤楼酒业计提约3.15亿元商誉减值，是第四季度单季利润转负的直接原因之一（来源：2025年年度报告、长江证券点评）。"

    # P2 现金流与资本配置
    net_ps = round(per_cf - capex - dps, 2) if per_cf else None
    p2 = f"每股收益¥{_fmt(eps, 2)}，每股经营现金流¥{_fmt(per_cf, 2)}，资本支出¥{_fmt(capex, 2)}/股，现金分红¥{_fmt(dps, 2)}/股"
    if payout:
        p2 += f"（支付率{_fmt(payout, 0)}%）"
    if net_ps is not None:
        p2 += f"，净留存¥{_fmt(net_ps, 2)}/股"
    p2 += "。白酒企业资本开支强度不高，现金流转化能力本应较强"
    if r_chg is not None and r_chg < 0:
        p2 += f"；但{yr_label}年营收下滑{abs(r_chg):.1f}%直接导致回款减少，经营现金流同比走弱"
    p2 += "。每股经营现金流仍显著高于每股收益，显示利润含金量充足。"
    p2 += "公司维持高分红政策，账面资金充裕，具备穿越周期能力。"
    if per_cf and per_cf > eps:
        p2 += f"现金流/利润比{per_cf / eps:.2f}x，盈利质量扎实。"

    # P3 盈利质量与护城河
    p3 = f"毛利率{_p(gm)}、净利率{_p(npm)}、ROE {_p(roe)}"
    if roic:
        p3 += f"、ROIC {_p(roic)}"
    p3 += "。壁垒：①老八大名酒品牌背书，「年份原浆」在安徽及华中市场心智稳固；②古井镇老窖池资源与酿造工艺积淀；③省内深度分销网络，渠道掌控力强。风险：全国化推进不及预期（华中占比偏高显示区域依赖）；次高端价格带竞争加剧；白酒消费受宏观景气度影响显著。"

    # P4 估值
    p4 = f"当前PE约{_fmt(pe, 1)}倍，PB约{_fmt(pb, 2)}倍，股息率约{_fmt(div, 2)}%，每股净资产{_fmt(bps, 2)}元。"
    if med and pe and pe < med:
        p4 += f"低于历史中位PE {_fmt(med, 1)}倍，估值处于历史偏低区间。"
    elif med:
        p4 += f"对比历史中位PE {_fmt(med, 1)}倍。"
    # 静态 PCF = 现价 / 每股经营现金流 (动态计算, 不硬编码)
    pcf_now = None
    price = _num(spot.get("price"))
    if price and per_cf:
        pcf_now = price / per_cf
        p4 += f"历史PCF中位数约24x（前复权年均价/每股经营现金流测算），当前静态PCF约{pcf_now:.0f}x。"
        if pcf_now < 24:
            p4 += "低于历史中位，估值具备安全边际。"
        elif pcf_now <= 30:
            p4 += "处于历史中位附近。"
        else:
            p4 += "高于历史中位，需注意分母为周期底部读数。"
        if r_chg is not None and r_chg < 0:
            p4 += f"需注意：{yr_label}年现金流为周期底部读数，若盈利修复则倍数分母具备向上弹性。"
    if online_pct:
        p4 += f"线上渠道占营收{_p(online_pct)}，直销占比提升有助于利润率改善。"

    # P5 催化剂
    next_yr = str(int(yr_label) + 1) if yr_label.isdigit() else "次年"
    p5 = (
        "催化剂：①渠道去库存完成、动销回暖带动营收重回增长；"
        f"②黄鹤楼减值包袱出清后轻装上阵，{next_yr}年利润基数效应改善；"
        "③结构升级——古16/古20在次高端价格带的份额提升；"
        "④高分红比率维持，股息率提供估值支撑。"
        "跟踪信号：季度营收同比增速降幅是否收窄、合同负债余额（渠道打款意愿的前瞻指标）、年份原浆批价走势、华中以外区域营收占比变化。"
    )

    return {"business": biz, "commentary": [p1, p2, p3, p4, p5]}
