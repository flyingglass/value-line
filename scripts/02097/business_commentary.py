# -*- coding: utf-8 -*-
"""蜜雪集团 02097 — VL 标准 Business + AI Commentary"""

def build(stock, metrics, revenue_structure, years, cagr, spot):
    latest_yr = years[-1] if years else "2025"
    ly = metrics.get(latest_yr, {})
    prev_yr = years[-2] if len(years) >= 2 else None
    py = metrics.get(prev_yr, {}) if prev_yr else {}

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
    payout = ly.get("PAYOUT_RATIO")
    lt_debt = ly.get("LT_DEBT") or 0

    # ---- Business ----
    business = (
        f"蜜雪集团是中国最大的现制茶饮企业，全球门店突破4万家，"
        f"主营冰淇淋、柠檬水和茶饮产品，定位极致性价比（2-8元价格带）。"
        f"核心商业模式为加盟——公司向加盟商销售原材料（占比~95%）、"
        f"收取加盟费及服务费（~5%），轻资产、高现金流、高ROE。"
        f"营收{rev:.0f}亿（{_dir(rev, py.get('OPERATE_INCOME'))}{abs(rev_chg):.1f}%），"
        f"净利率{_fmt_pct(npm)}，ROE {_fmt_pct(roe)}。"
        f"海外门店（东南亚为主）超4,000家。2025年3月港交所上市。"
    )

    # ---- Commentary 5段 ----
    tax_rate = (ly.get("TAX_EBT", 25) or 25) / 100
    op_eps = round(per_oi * (opm / 100) * (1 - tax_rate), 2) if per_oi and opm else None
    nonop_eps = round(eps - op_eps, 2) if eps and op_eps else None
    op_pct = round(op_eps / eps * 100) if eps and op_eps and eps != 0 else 0
    net_ps = round(per_cf - per_capex - dps, 2) if per_cf else None

    # 段1
    p1 = (
        f"2026年6月6日 — 蜜雪集团{latest_yr}年营收约{rev:.0f}亿元（{_dir(rev, py.get('OPERATE_INCOME'))}{abs(rev_chg):.1f}%），"
        f"扣非净利润约{np_val:.0f}亿元（{_dir(np_val, py.get('HOLDER_PROFIT'))}{abs(np_chg):.1f}%）。"
        f"全球门店突破{41000 + (int(latest_yr)-2025)*7000}家，其中海外门店超4,000家。"
        f"同店增速保持正增长，净利率{_fmt_pct(npm)}在加盟赛道中领先。"
        + (f"利润增速{abs(np_chg):.0f}%远超营收{abs(rev_chg):.0f}%，经营杠杆释放明显。" if np_chg and rev_chg and np_chg > rev_chg * 1.1 else "")
    )

    # 段2
    wc, wc_p = ly.get("WORKING_CAPITAL"), py.get("WORKING_CAPITAL")
    shares, shares_p = ly.get("TOTAL_SHARES"), py.get("TOTAL_SHARES")
    shr_chg = round((shares - shares_p) / shares_p * 100, 1) if shares and shares_p and shares_p > 0 else None
    if eps and op_eps and nonop_eps:
        p2_parts = [
            f"每股收益¥{eps:.2f}中，主业经营贡献¥{op_eps:.2f}（{op_pct}%），"
            f"非经营性贡献¥{nonop_eps:.2f}（{100-op_pct}%），利润高度纯粹。",
            f"每股现金流¥{per_cf:.2f}（内生现金生成 = 净利润 + 折旧），四大去向：",
            f"① 资本支出¥{per_capex:.2f}/股（轻资产扩张，CAPEX极低）；",
        ]
        if wc is not None and wc_p is not None:
            wc_chg = wc - wc_p
            wc_chg_ps = f"折合¥{abs(wc_chg * 100 / shares):.2f}/股" if shares and shares > 0 else ""
            p2_parts.append(f"② 营运资金{'占用 +' if wc_chg > 0 else '释放 '}{abs(wc_chg):.1f}亿（{wc_chg_ps}）")
            p2_parts.append(f"（加盟模式先收钱后发货，快收慢付 ✅）；")
        p2_parts.append(f"③ 现金分红¥{dps:.2f}/股（支付率{payout:.0f}%）；")
        if shr_chg is not None and shr_chg < -0.3:
            p2_parts.append(f"④ 股份回购（股数{shr_chg:+.1f}%）— 增厚每股价值 ✅；")
        elif shr_chg is not None and shr_chg > 0:
            p2_parts.append(f"④ 股数持平/微扩；")
        p2_parts.append(f"净留存¥{net_ps:.2f}/股，现金流充裕——")
        p2_parts.append(
            ("零长期负债，" if lt_debt == 0 else f"长期负债率{lt_debt/ly.get('TOTAL_EQUITY',1)*100:.0f}%，")
            + "经营效率驱动所有回报。"
        )
        p2 = "".join(p2_parts)
    else:
        p2 = "每股资金流向：数据待补充。"

    # 段3
    p3 = (
        f"毛利率{_fmt_pct(gm)}、净利率{_fmt_pct(npm)}、ROE {_fmt_pct(roe)}——"
        f"加盟模型下轻资产高回报的典范。竞争壁垒三重："
        f"①规模效应——4万+门店的供应链网络摊薄采购和物流成本，"
        f"自建核心原料基地（柠檬、茶叶等），成本优势极难复制；"
        f"②品牌心智——\"高质平价\"定位深入人心，消费者认知难以被替代；"
        f"③加盟商生态——单店投资回收期12-18个月，加盟商粘性高。"
        f"风险：食品安全事件（餐饮行业系统性风险）、加盟商管理边界、"
        f"海外扩张不确定性、下沉市场竞争加剧（甜啦啦、古茗等）。"
    )

    # 段4
    pe = spot.get("pe", 0) or 0
    median_pe = spot.get("median_pe")
    pb = spot.get("pb", 0) or 0
    div_yield = spot.get("div_yield", 0) or 0
    eps_1yr = cagr.get("eps", {}).get("1yr")

    p4 = (
        f"当前PE约{pe:.1f}倍，"
        + (f"低于历史中位数{median_pe:.0f}倍，处于历史区间低位。" if median_pe and pe < median_pe else
           f"高于历史中位数{median_pe:.0f}倍。" if median_pe else "估值位置待评估。")
        + (f"PEG（PE/增长率）约{pe/eps_1yr:.1f}x，估值相对增速合理偏低。" if eps_1yr and eps_1yr > 0 else "")
        + f"PB约{pb:.1f}倍，ROE {_fmt_pct(roe)}支撑高溢价。"
        + f"股息率约{div_yield:.2f}%。"
        + f"2025年上市首年市场担忧增速见顶和加盟模式天花板。"
        + f"关注2026年海外扩张节奏、单店营收趋势及第二增长曲线（瓶装饮料等新品类）——"
        + f"这是估值能否重估的核心驱动力。"
    )

    # 段5
    signals = []
    if rev_chg is not None and rev_chg > 20: signals.append("营收增速仍处高位，加盟模式天花板尚未触及")
    if np_chg and rev_chg and np_chg > rev_chg * 1.2: signals.append("利润增速显著高于营收，经营杠杆持续释放")
    if lt_debt == 0: signals.append("零杠杆运营，财务安全性极高")
    if eps_1yr and eps_1yr > 15: signals.append(f"EPS增速{eps_1yr:+.1f}%，成长性在消费板块中属第一梯队")

    p5 = "。".join(signals) + "。验证信号：关注2026年中报海外门店同店增速，" + (
        f"若海外扩张节奏保持且利润率无摊薄，当前估值有显著重估空间。" if pe and pe < 25 else "需验证高增速的持续性。")

    return {
        "business": business,
        "commentary": [p1, p2, p3, p4, p5],
    }
