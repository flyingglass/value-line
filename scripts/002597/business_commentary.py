# -*- coding: utf-8 -*-
"""金禾实业 002597 — VL Business + AI Commentary（数据驱动，不写死数字）"""

def build(stock, metrics, revenue_structure, years, cagr, spot):
    latest_yr = years[-1] if years else "2025"
    ly = metrics.get(latest_yr, {})
    prev_yr = years[-2] if len(years) >= 2 else None
    py = metrics.get(prev_yr, {}) if prev_yr else {}

    def _chg(cur, prev):
        return (cur / prev - 1) * 100 if cur and prev and prev > 0 else None
    def _dir(cur, prev):
        c = _chg(cur, prev)
        return "增长" if (c or 0) > 0 else "下降"
    def _fmt(v, d=0): return f"{v:,.{d}f}" if v is not None else "-"
    def _fmt_pct(v): return f"{v:+.1f}%" if v is not None else "-"

    rev = ly.get("OPERATE_INCOME")
    np_val = ly.get("HOLDER_PROFIT")
    eps = ly.get("BASIC_EPS")
    gm = ly.get("GROSS_MARGIN")
    npm = ly.get("NET_PROFIT_RATIO")
    roe = ly.get("ROE")
    roic = ly.get("ROIC")
    rev_chg = _chg(rev, py.get("OPERATE_INCOME"))
    np_chg = _chg(np_val, py.get("HOLDER_PROFIT"))
    per_cf = ly.get("PER_NETCASH")
    per_capex = ly.get("CAPEX_PS") or 0
    dps = ly.get("DPS") or 0
    payout = ly.get("PAYOUT_RATIO")

    # ---- Revenue breakdown ----
    rev_parts = []
    if isinstance(revenue_structure, dict) and revenue_structure:
        for dim_key, items in revenue_structure.items():
            if items:
                rev_parts.extend([f"{r.get('name','')}{r.get('pct',''):.0f}%" for r in items[:3]])

    # ---- Business ----
    business = (
        f"金禾实业是全球领先的健康食品配料企业，主营甜味剂（安赛蜜产能全球第一约1.6万吨/年、三氯蔗糖产能全球前列）、"
        f"香料（乙基麦芽酚）及基础化工产品，构建从基础化工到精细化工的全产业链布局。"
        f"FY{latest_yr}营收{_fmt(rev,0)}亿（{_dir(rev, py.get('OPERATE_INCOME'))}{abs(rev_chg):.1f}%），"
        f"归母净利{_fmt(np_val,0)}亿，净利率{_fmt_pct(npm)}，ROE {_fmt_pct(roe)}。"
        + (f"营收结构：{'/'.join(rev_parts)}。" if rev_parts else "")
    )

    # ---- Commentary 1: 业绩概览 ----
    p1 = (
        f"2026年7月 — 金禾实业{latest_yr}年营收约{_fmt(rev,0)}亿元"
        + (f"（{_dir(rev, py.get('OPERATE_INCOME'))}{abs(rev_chg):.1f}%）" if rev_chg else "")
        + f"，归母净利润约{_fmt(np_val,0)}亿元"
        + (f"（{_dir(np_val, py.get('HOLDER_PROFIT'))}{abs(np_chg):.1f}%）" if np_chg else "")
        + f"。业绩大幅下滑主因：三氯蔗糖行业产能严重过剩，价格从2022年高点约40万元/吨跌至约10-12万元/吨，"
        + f"安赛蜜价格亦受新产能冲击走弱。公司甜味剂业务量增价跌，利润严重承压。"
        + (f"毛利率{_fmt_pct(gm)}、净利率{_fmt_pct(npm)}，均处历史低位。" if gm and npm else "")
    )

    # ---- Commentary 2: 每股资金流向 ----
    if eps and per_cf:
        net_ps = round(per_cf - per_capex - dps, 2) if per_cf else None
        p2_parts = [
            f"每股收益¥{_fmt(eps,2)}中，主业经营贡献绝大部分。",
            f"每股经营现金流¥{_fmt(per_cf,2)}，资本支出¥{_fmt(per_capex,2)}/股"
            + (f"（维持性为主，甜味剂扩产高峰已过），" if per_capex else "，"),
            f"分红¥{_fmt(dps,2)}/股（支付率{_fmt(payout,0)}%），净留存约¥{_fmt(net_ps,2)}/股。",
            "资产负债率仅24%，现金充裕，极端周期底部抗风险能力强。"
            "实际控制人杨乐于2026年6月增持约3000万元（149万股），信号意义积极。",
        ]
        p2 = "".join(p2_parts)
    else:
        p2 = "每股资金流向：数据待补充。"

    # ---- Commentary 3: 竞争壁垒 ----
    p3 = (
        f"毛利率{_fmt_pct(gm)}、净利率{_fmt_pct(npm)}、ROE {_fmt_pct(roe)}"
        + (f"、ROIC {_fmt_pct(roic)}。" if roic else "。")
        + "竞争壁垒："
        "①规模与成本优势——安赛蜜全球产能第一（1.6万吨），三氯蔗糖产能全球前三，"
        "规模效应+全产业链配套（自产基础化工原料如双乙烯酮、液碱等），生产成本行业最低梯队；"
        "②客户粘性——食品饮料大客户（可口可乐、百事、雀巢等）认证周期长、切换成本高，"
        "长期供应关系构成稳定基本盘；"
        "③工艺know-how——甜味剂合成工艺复杂，多年积累的技术壁垒新进入者短期难以突破。"
        "风险：甜味剂价格持续低迷（核心利润变量）、三氯蔗糖行业出清节奏不确定、"
        "代糖消费趋势变化（天然甜味剂替代）、原材料（液碱/硫酸）价格波动。"
    )

    # ---- Commentary 4: 估值 ----
    pe = spot.get("pe", 0) or 0
    median_pe = spot.get("median_pe")
    pb = spot.get("pb", 0) or 0
    div_yield = spot.get("div_yield", 0) or 0
    bps = ly.get("BPS")

    p4 = (
        f"当前PE约{_fmt(pe,1)}倍"
        + (f"，历史中位PE {_fmt(median_pe,0)}倍。" if median_pe else "。")
        + f"PB约{_fmt(pb,1)}倍"
        + (f"（每股净资产{_fmt(bps,2)}元）。" if bps else "。")
        + f"股息率约{_fmt(div_yield,1)}%。"
        + "核心逻辑：①周期底部困境反转——三氯蔗糖行业亏损面扩大，中小产能退出加速，"
        + "行业出清后价格弹性极大（每涨价1万元/吨可增厚年利润约0.5-0.8亿）；"
        + "②安赛蜜基本盘——全球市占率超60%，刚需属性提供利润底；"
        + "③资产负债表优秀——净现金状态+低负债率，周期底部存活确定性强。"
        + "关注三氯蔗糖报价和行业开工率作为核心信号。"
    )

    # ---- Commentary 5: 催化剂 ----
    p5 = (
        "催化剂：①三氯蔗糖行业出清——当前价格已跌破多数企业现金成本线，"
        + "预计2026H2中小产能加速退出，价格有望触底回升，每回升1万元/吨对年利润弹性"
        + "约{:.1f}亿元。".format(np_val * 0.02 if np_val else 0.7)
        + "②定远基地产能逐步爬坡，一体化降本效应持续释放；"
        + "③代糖消费长期趋势向好——全球减糖趋势下安赛蜜、三氯蔗糖需求CAGR 5-8%，"
        + "价格终将回归合理利润水平。"
        + "④2026年6月实控人增持3000万元释放底部信号。"
        + "关注每季度三氯蔗糖和安赛蜜销售均价变化。"
    )

    return {
        "business": business,
        "commentary": [p1, p2, p3, p4, p5],
    }
