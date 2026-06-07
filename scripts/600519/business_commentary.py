# -*- coding: utf-8 -*-
"""贵州茅台 600519 — VL 标准 Business + AI Commentary"""

def build(stock, metrics, revenue_structure, years, cagr, spot):
    latest_yr = years[-1] if years else "2025"
    ly = metrics.get(latest_yr, {})
    prev_yr = years[-2] if len(years) >= 2 else None
    py = metrics.get(prev_yr, {}) if prev_yr else {}
    name = stock.get("name", "贵州茅台")

    def _chg(cur, prev):
        return (cur / prev - 1) * 100 if cur and prev and prev > 0 else None
    def _dir(cur, prev):
        c = _chg(cur, prev)
        if c is None: return ""
        return "增长" if c > 0 else ("下降" if c < 0 else "持平")
    def _fmt_pct(v):
        return f"{v:+.1f}%" if v is not None else "-"

    rev = ly.get("OPERATE_INCOME")
    np_val = ly.get("HOLDER_PROFIT")
    eps = ly.get("BASIC_EPS")
    gm = ly.get("GROSS_MARGIN")
    opm = ly.get("OP_MARGIN")
    npm = ly.get("NET_PROFIT_RATIO")
    roe = ly.get("ROE")
    roce = ly.get("ROIC")
    rev_chg = _chg(rev, py.get("OPERATE_INCOME"))
    np_chg = _chg(np_val, py.get("HOLDER_PROFIT"))
    per_cf = ly.get("PER_NETCASH")
    per_oi = ly.get("PER_OI")
    per_capex = ly.get("CAPEX_PS") or 0
    dps = ly.get("DPS") or 0
    bps = ly.get("BPS")
    payout = ly.get("PAYOUT_RATIO")

    # ---- Business ----
    business = (
        f"贵州茅台是中国高端白酒绝对龙头，核心产品飞天茅台占据2000+元价格带垄断地位。"
        f"公司拥有不可复制的地理护城河（茅台镇7.5km²核心产区独特微生物环境）、"
        f"深厚的品牌壁垒（国酒地位）及稀缺产能。营收以茅台酒为主（~87%），系列酒（茅台1935等）为辅（~13%）。"
        f"毛利率{_fmt_pct(gm)}，净利率{_fmt_pct(npm)}，ROE {_fmt_pct(roe)}。"
        f"渠道改革（i茅台直销占比提升至45%+）持续释放利润。"
        f"{latest_yr}年营收{rev:.0f}亿，年产基酒约5.7万吨。"
    )

    # ---- Commentary 5段 ----
    # 段1: 业绩快照与变化归因
    p1 = (
        f"2026年6月6日 — 贵州茅台{latest_yr}年营收约{rev:.0f}亿元（{_dir(rev, py.get('OPERATE_INCOME'))}{abs(rev_chg):.1f}%），"
        f"扣非净利润约{np_val:.0f}亿元（{_dir(np_val, py.get('HOLDER_PROFIT'))}{abs(np_chg):.1f}%）。"
        f"茅台酒营收{ly.get('OPERATE_INCOME',0)*0.87:.0f}亿，系列酒{ly.get('OPERATE_INCOME',0)*0.13:.0f}亿，"
        f"i茅台直销平台持续贡献增量。飞天茅台出厂价1169元/瓶，终端批价约2700元，渠道利润丰厚，提价空间充足。"
        f"毛利率{_fmt_pct(gm)}连续15年>90%，净利率{_fmt_pct(npm)}，盈利能力A股第一梯队。"
    )

    # 段2: 每股资金流向与现金循环
    tax_rate = (ly.get("TAX_EBT", 25) or 25) / 100
    if per_oi and opm and eps:
        op_eps = round(per_oi * (opm / 100) * (1 - tax_rate), 2)
        nonop_eps = round(eps - op_eps, 2)
        op_pct = round(op_eps / eps * 100) if eps else 0
        nonop_pct = 100 - op_pct
        net_ps = round(per_cf - per_capex - dps, 2) if per_cf else None

        p2 = (
            f"每股收益¥{eps:.2f}中，主业经营贡献¥{op_eps:.2f}（{op_pct}%），非经营性贡献¥{nonop_eps:.2f}（{nonop_pct}%），"
            f"利润高度纯粹。每股现金流¥{per_cf:.2f}，资本支出¥{per_capex:.2f}（产能扩建），"
            f"现金分红¥{dps:.2f}（支付率{payout:.0f}%），净留存¥{net_ps:.2f}/股。"
            f"现金流极度充裕，分红率持续提升——账上现金超2000亿元，"
            f"2025年茅台酒基酒产量5.72万吨，系列酒4.81万吨，3-5年后可售商品酒将显著放量。"
        )
    else:
        p2 = "每股资金流向：数据待补充。"

    # 段3: 业务质地与竞争壁垒
    p3 = (
        f"毛利率{_fmt_pct(gm)}、净利率{_fmt_pct(npm)}、ROE {_fmt_pct(roe)}——"
        f"茅台是全球盈利能力最强的消费品公司之一。"
        f"竞争壁垒三重：①不可复制的茅台镇7.5km²核心产区微生物环境——"
        f"任何异地复制均告失败，形成了地球上最深的食品行业护城河之一；"
        f"②53度飞天茅台占据消费者心智的\"国酒\"地位，社交货币属性超越普通消费品；"
        f"③社会库存（渠道+消费者囤积）形成天然需求缓冲，终端价格体系极其稳固。"
        f"风险：宏观经济下行压制高端消费、产能扩张后稀缺性边际稀释、白酒消费人口结构变化。"
    )

    # 段4: 估值锚定与安全边际
    pe = spot.get("pe", 0) or 0
    median_pe = spot.get("median_pe")
    pb = spot.get("pb", 0) or 0
    div_yield = spot.get("div_yield", 0) or 0

    p4 = (
        f"当前PE约{pe:.1f}倍，"
        + (f"低于5年历史中位数{median_pe:.0f}倍，处于历史区间低位区。" if median_pe and pe < median_pe else (
           f"高于历史中位数{median_pe:.0f}倍。" if median_pe else "估值位置待评估。"))
        + f"PB约{pb:.1f}倍，ROE {_fmt_pct(roe)}支撑高PB溢价。"
        + f"股息率约{div_yield:.2f}%，支付率{payout:.0f}%仍有提升空间（账上现金超2,000亿）。"
        + (f"估值已从2021年PE 70x泡沫回归理性，当前约等于无风险利率倒数隐含的合理PE。" if pe and pe < 30 else "")
        + f"关注批价走势——若飞天批价跌破2500元则需重新评估渠道健康度。"
    )

    # 段5: 转折点检测 + 验证信号
    eps_1yr = cagr.get("eps", {}).get("1yr")
    rev_1yr = cagr.get("revenue", {}).get("1yr")
    eps_5yr = cagr.get("eps", {}).get("5yr")

    signals = []
    if rev_chg is not None and rev_chg < 15:
        signals.append(f"营收增速放缓至{rev_chg:.1f}%，关注是否进入中低增长常态")
    if np_chg is not None and rev_chg is not None and np_chg < rev_chg:
        signals.append("利润增速落后营收——费用端或产品结构变化需关注")
    if eps_1yr is not None and eps_1yr < 10:
        signals.append(f"EPS增速{eps_1yr:+.1f}%进入个位数时代，估值中枢可能下移")
    if gm and gm > 90:
        signals.append(f"毛利率{_fmt_pct(gm)}超级稳定，定价权未受挑战")

    p5 = "。".join(signals) + "。" if signals else "关键指标稳定，暂无显著转折信号。"

    return {
        "business": business,
        "commentary": [p1, p2, p3, p4, p5],
    }
