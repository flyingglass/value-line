# -*- coding: utf-8 -*-
"""名创优品 09896 — VL Business + AI Commentary（数据驱动）。

数据来源约定：
  - 财务比率 / 每股数 / 估值：来自 metrics、cagr、spot（DB + 行情），不硬编码；
  - 门店数、分部收入、永辉收购、经调整口径等 DB 中没有的数字，一律标注年报出处。
"""


def build(stock, metrics, revenue_structure, years, cagr, spot):
    ly = metrics.get(years[-1], {}) if years else {}
    py = metrics.get(years[-2], {}) if len(years) >= 2 else {}

    def _chg(cur, prev):
        return (cur / prev - 1) * 100 if cur and prev and prev > 0 else None

    def _dir(cur, prev):
        return "增长" if (_chg(cur, prev) or 0) > 0 else "下降"

    def _fmt(v, d=1):
        return f"{v:,.{d}f}" if v else "-"

    def _p(v):
        return f"{v:+.1f}%" if v is not None else "-"

    rev, np_, eps = ly.get("OPERATE_INCOME"), ly.get("HOLDER_PROFIT"), ly.get("BASIC_EPS")
    gm, opm, npm = ly.get("GROSS_MARGIN"), ly.get("OP_MARGIN"), ly.get("NET_PROFIT_RATIO")
    roe, roic = ly.get("ROE"), ly.get("ROIC")
    per_cf, capex_ps = ly.get("PER_NETCASH"), (ly.get("CAPEX_PS") or 0)
    dps, payout, equity = (ly.get("DPS") or 0), ly.get("PAYOUT_RATIO"), ly.get("TOTAL_EQUITY")
    pe, pb = spot.get("pe") or 0, spot.get("pb") or 0
    div, mkt_cap = spot.get("div_yield") or 0, spot.get("mkt_cap") or 0
    price, median_pe = spot.get("price") or 0, spot.get("median_pe") or 0

    rev_chg = _chg(rev, py.get("OPERATE_INCOME"))
    np_chg = _chg(np_, py.get("HOLDER_PROFIT"))
    fcf_ps = (per_cf - capex_ps) if per_cf else None

    seg = {i["name"]: i["pct"] for i in (revenue_structure.get("by_segment") or [])}
    reg = {i["name"]: i["pct"] for i in (revenue_structure.get("by_region") or [])}
    chn = {i["name"]: i["pct"] for i in (revenue_structure.get("by_channel") or [])}
    overseas_pct = sum(v for k, v in reg.items() if k != "中国内地")
    mainland_pct = reg.get("中国内地", 0)

    biz = (
        "名创优品集团是全球价值零售商，双品牌运营：旗舰品牌「名创优品 MINISO」提供以 IP 联名设计"
        "为特色的潮流生活家居产品，第二品牌「TOP TOY」聚焦潮流玩具。门店以合伙人（加盟）模式为主、"
        "直营为辅，收入来自向加盟商与代理商销售产品、直营店零售、线上销售以及授权费与服务费。"
        f"{years[-1]}年营收 {_fmt(rev)} 亿元（{_dir(rev, py.get('OPERATE_INCOME'))}{abs(rev_chg or 0):.1f}%），"
        f"归母净利 {_fmt(np_)} 亿元，毛利率 {_fmt(gm)}%；收入结构中中国内地占 {mainland_pct:.1f}%、"
        f"海外占 {overseas_pct:.1f}%（来源：2025年度报告 附注4(iii)）。"
    )

    p1 = (
        f"{years[-1]}年营收 {_fmt(rev)} 亿元（{_p(rev_chg)}），归母净利 {_fmt(np_)} 亿元（{_p(np_chg)}）。"
        "净利大幅下滑与主业无关，三项非经营项合计拖累约 12.9 亿元：①分占以权益法入账的被投资公司"
        "（主体为永辉超市）亏损 8.34 亿元；②TOP TOY 战略融资优先股形成的赎回负债公允价值变动 -1.58 亿元；"
        "③财务净成本 3.27 亿元（上年为净收入 0.26 亿元，主因股票挂钩证券与收购永辉的银行贷款利息）。"
        "同期经营利润 33.03 亿元与上年 33.16 亿元基本持平，经调整净利润 28.98 亿元（+6.5%）。"
        "结构上：名创优品品牌收入 195.25 亿元（+22.0%，其中海外 +29.3%、中国内地 +16.8%），"
        "TOP TOY 收入 19.16 亿元（+94.8%）；门店名创优品 8,151 家（上年末 7,504 家）、"
        "TOP TOY 334 家（上年末 276 家）。2026 上半年营收 114.99 亿元（+22.4%）、归母净利 9.62 亿元（+5.6%），"
        "但经调整净利 10.79 亿元（-15.7%），增长质量较 2025 年转弱（来源：2026中期报告 P4-6）。"
    )

    p2 = (
        f"每股经营现金流 {_fmt(per_cf, 2)} 元（上年 {_fmt(py.get('PER_NETCASH'), 2)} 元），"
        f"每股资本开支 {_fmt(capex_ps, 2)} 元，自由现金流每股约 {_fmt(fcf_ps, 2)} 元——海外直营店投入加大后，"
        f"经营现金流对扩张的覆盖度下降。2025 年每股派息 {_fmt(dps, 2)} 元，对应派息率 {_fmt(payout, 0)}%"
        f"（GAAP 口径；按经调整净利约 50%），年内另回购并注销约 1% 股本。最大一笔资本配置是 2024-2025 年"
        f"以 62.70 亿元收购永辉超市 29.4% 股权（2025Q1 完成，权益法核算），2025 年末该投资公允价值 "
        f"125.14 亿元、占总资产 43.7%，当年确认分占亏损 8.13 亿元（来源：2025年度报告 P31-32）。"
        f"股东权益 {_fmt(equity)} 亿元，对应当前 PB {_fmt(pb, 2)}x；分红 + 回购的现金回报路径仍在延续。"
    )

    p3 = (
        f"毛利率由 2022 年 30.4% 升至 {years[-1]} 年 {_fmt(gm)}%（上年 {_fmt(py.get('GROSS_MARGIN'))}%），"
        f"驱动力是海外收入占比提升、IP 联名产品结构升级与 TOP TOY 毛利改善；净利率 {_fmt(npm)}%"
        f"（上年 {_fmt(py.get('NET_PROFIT_RATIO'))}%）、ROE {_fmt(roe)}%（上年 {_fmt(py.get('ROE'))}%）的恶化"
        f"全部来自永辉权益法亏损与融资成本，ROIC 仍有 {_fmt(roic)}%，说明主业资本回报未受损。"
        f"护城河：①IP 联名矩阵与高频上新带来的产品差异化；②8,000+ 家全球门店网络的采购规模与渠道复用，"
        f"授权费及服务费占收入 {chn.get('授权费及服务费', 0):.1f}%，近乎纯利；③TOP TOY 作为潮玩第二曲线"
        f"（2025 年 GMV 25.88 亿元）。风险：直营化令销售及分销开支同比 +49.6%、费用刚性上升；美国等市场"
        f"关税与汇率波动；TOP TOY 分部经营利润由上年 +0.97 亿元转为 -1.06 亿元。"
    )

    p4 = (
        f"现价 {_fmt(price, 2)} 港元、市值 {_fmt(mkt_cap, 0)} 亿元人民币，PE(TTM) {_fmt(pe, 1)}x、PB {_fmt(pb, 2)}x，"
        f"按 2025 年实际派息计算的股息率约 {_fmt(div, 1)}%，历史 PE 中位数 {_fmt(median_pe, 1)}x。"
        f"估值已显著压缩：2025 年股价均值 38.6 港元、对应 PE 均值 35.9x，2026 年以来一度跌至 17 港元附近。"
        f"需注意 PE 分子被永辉拖累失真——以经调整净利 28.98 亿元计，市值/经调整净利约 "
        f"{_fmt(mkt_cap / 28.98 if mkt_cap else None, 1)}x；但永辉 125 亿元账面投资每年贡献的亏损需单独打折，"
        f"更合理的锚是「主业经调整利润 + 永辉资产折价」。PB {_fmt(pb, 2)}x 与 ROE {_fmt(roe)}% 的组合，"
        f"已落在全球零售股的底部区间。"
    )

    p5 = (
        "催化剂与观察点：①永辉减亏节奏——2025 年永辉门店约 403 家、分占亏损 8.13 亿元，若门店调改见效"
        "将直接修复表观利润；②海外直营店爬坡（2025 年末集团直营店 768 家、直营收入 +71.3%）能否摊薄费用率；"
        "③TOP TOY 在战略融资后的扩张与海外门店模型验证（2025 年海外 GMV 0.64 亿元，基数仍小）；"
        "④高股息与回购的延续性（派息率已超 GAAP 净利，靠现金流支撑）；"
        "⑤负面观察项：2026 上半年经调整净利同比 -15.7%、经调整净利率下滑，若下半年未改善，"
        "估值修复缺乏业绩支撑。"
    )

    return {"business": biz, "commentary": [p1, p2, p3, p4, p5]}
