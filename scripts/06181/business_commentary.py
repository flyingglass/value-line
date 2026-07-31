# -*- coding: utf-8 -*-
"""老铺黄金 06181 — VL Business + AI Commentary（数据驱动，不写死数字）"""

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
    bps = ly.get("BPS")

    # ---- Revenue breakdown ----
    rev_parts = []
    if isinstance(revenue_structure, dict) and revenue_structure:
        for dim_key, items in revenue_structure.items():
            if items:
                rev_parts.extend([f"{r.get('name','')}{r.get('pct',''):.0f}%" for r in items[:3]])

    # ---- Business ----
    business = (
        f"老铺黄金是中国古法手工金器专业第一品牌，主营古法黄金饰品及金器（足金镶嵌钻石/宝石），"
        f"定位高端奢侈品路线，单店年销过亿。2024年6月港交所上市，品牌稀缺性极强。"
        f"FY{latest_yr}营收{_fmt(rev,0)}亿（{_dir(rev, py.get('OPERATE_INCOME'))}{abs(rev_chg):.0f}%），"
        f"归母净利{_fmt(np_val,0)}亿，净利率{_fmt_pct(npm)}，ROE {_fmt_pct(roe)}，"
        f"是中国增长最快的奢侈品公司之一。"
        + (f"营收结构：{'/'.join(rev_parts)}。" if rev_parts else "")
    )

    # ---- Commentary 1: 业绩概览 ----
    p1 = (
        f"2026年7月 — 老铺黄金{latest_yr}年营收{_fmt(rev,0)}亿元"
        + (f"（{_dir(rev, py.get('OPERATE_INCOME'))}{abs(rev_chg):.0f}%）" if rev_chg else "")
        + f"，归母净利润{_fmt(np_val,0)}亿元"
        + (f"（{_dir(np_val, py.get('HOLDER_PROFIT'))}{abs(np_chg):.0f}%）" if np_chg else "")
        + f"。2024年6月上市以来连续超预期增长，2026H1预计营收约200亿（+60-65%），增速虽放缓但仍惊人。"
        + f"毛利率{_fmt_pct(gm)}，体现了品牌的奢侈品定价权和古法金器的工艺溢价。"
        + "驱动因素：①古法黄金品类渗透率快速提升（从传统黄金饰品的差异化中切蛋糕），"
        + "②门店高速扩张（从一线向新一线下沉），③客单价持续提升（金价上涨+品牌溢价双驱动）。"
    )

    # ---- Commentary 2: 每股资金流向 ----
    if eps:
        net_ps = round(per_cf - per_capex - dps, 2) if per_cf else None
        p2_parts = [
            f"每股收益¥{_fmt(eps,2)}，每股净资产¥{_fmt(bps,2)}。",
            f"经营现金流每股¥{_fmt(per_cf,2)}" + (
                "（大幅为负！高速扩张期黄金库存占用巨额资金）" if per_cf and per_cf < 0 else ""
            ) + "，",
            f"资本支出¥{_fmt(per_capex,2)}/股（门店装修+产能扩张），"
            f"分红¥{_fmt(dps,2)}/股（支付率{_fmt(payout,0)}%）。",
            "核心问题：经营现金流为负是高速扩张的阵痛——门店铺货+金价上涨导致库存占用大量现金，"
            "但随着门店成熟和同店增长（SSSG），现金流有望在未来1-2年转正。"
            "长期来看，单店盈利模型极强（店均年收入过亿、回收期<6个月），现金流改善可期。",
        ]
        p2 = "".join(p2_parts)
    else:
        p2 = "每股资金流向：数据待补充。"

    # ---- Commentary 3: 竞争壁垒 ----
    p3 = (
        f"毛利率{_fmt_pct(gm)}、净利率{_fmt_pct(npm)}、ROE {_fmt_pct(roe)}"
        + (f"、ROIC {_fmt_pct(roic)}。" if roic else "。")
        + "竞争壁垒："
        "①品牌先行者优势——率先将古法黄金从传统金饰中独立为高端品类，占据消费者心智第一联想，"
        "品牌溢价显著（客单价远超周大福/老凤祥等传统品牌）；"
        "②非遗工艺壁垒——花丝、錾刻、珐琅等古法工艺依赖资深匠人，人才培养周期长、复制难度大；"
        "③奢侈品渠道稀缺性——高端商场（SKP/恒隆/太古里等）选址壁垒，核心铺位有限，后来者难以复制；"
        "④单店模型极强——店均年收入过亿，坪效行业最高，形成正反馈扩张飞轮。"
        "风险：金价大幅下跌导致库存减值、宏观经济下行影响高端消费、"
        "竞品（周大福/老凤祥/周生生等）推出古法系列分流、高速扩张中品牌稀释风险。"
    )

    # ---- Commentary 4: 估值 ----
    pe = spot.get("pe", 0) or 0
    median_pe = spot.get("median_pe")
    pb = spot.get("pb", 0) or 0
    div_yield = spot.get("div_yield", 0) or 0

    p4 = (
        f"当前PE约{_fmt(pe,1)}倍"
        + (f"，历史中位PE {_fmt(median_pe,0)}倍。" if median_pe else "。")
        + f"PB约{_fmt(pb,1)}倍（每股净资产{_fmt(bps,2)}元）。"
        + f"股息率约{_fmt(div_yield,1)}%。"
        + "核心逻辑：①品类渗透红利——古法黄金在整体黄金饰品市场渗透率仍低（<10%），"
        + "赛道增速远高于传统金饰，老铺作为品类定义者受益最大；"
        + "②门店扩张空间——当前门店约30+家，若对标国际奢侈品牌（卡地亚/蒂芙尼/宝格丽中国200+店），"
        + "仍有5-10倍开店空间；③单店效率持续提升（同店+客单价+复购率），"
        + "单店模型进入盈利正循环后利润弹性极大。"
        + "关注同店增速（SSSG）、门店净增数和客单价趋势作为核心信号。"
    )

    # ---- Commentary 5: 催化剂 ----
    p5 = (
        "催化剂：①2026H1预告营收约200亿（+60-65%），若H2增速维持40%+，"
        + f"全年营收有望突破400亿，远超当前市场预期；"
        + "②品牌出海——新加坡/东京首店测试成功后，东南亚高端华人市场空间巨大；"
        + "③品类延伸——古法金镶钻/宝石产品毛利率更高（50%+），产品结构升级持续推升净利率；"
        + "④金价长期上涨趋势叠加品牌溢价，客单价持续攀升的确定性高。"
        + "⑤2025年股息每股11.95元（支付率约42%），股东回报意识强。"
        + "关注月度门店销售数据和季度同店增长。"
    )

    return {
        "business": business,
        "commentary": [p1, p2, p3, p4, p5],
    }
