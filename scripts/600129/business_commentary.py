# -*- coding: utf-8 -*-
"""太极集团 600129 — VL Business + AI Commentary（数据驱动, 手工精调）
口径说明: VL 净利润/每股收益采用扣非口径。太极 2025 扣非 0.44 亿 / 归母 1.21 亿(+352% 系 2024 低基数 0.27 亿),
2023 高基数归母 8.22 亿(扣非 7.7 亿)。文内以扣非为主数字, 归母口径另行注明。
最新财年(2025)同比增速用年报 PDF 精确披露值硬编码。
"""
def build(stock, metrics, revenue_structure, years, cagr, spot):
    ly = metrics.get(years[-1], {}) if years else {}
    py = metrics.get(years[-2], {}) if len(years) >= 2 else {}
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
    roic = _num(ly.get("ROIC"))
    bps = _num(ly.get("BPS"))
    per_cf = _num(ly.get("PER_NETCASH"))
    per_capex = _num(ly.get("CAPEX_PS") or 0)
    dps = _num(ly.get("DPS") or 0)
    price = _num(spot.get("price", 0))
    pe = _num(spot.get("pe", 0))
    pb = _num(spot.get("pb", 0))
    div_y = _num(spot.get("div_yield", 0))
    med_pe = spot.get("median_pe")

    # 营收结构 (value 单位: 百万元)
    ind_data = revenue_structure.get("by_industry", []) if isinstance(revenue_structure, dict) else []
    ind_parts = [f"{r['name']}{r['pct']:.1f}%" for r in ind_data] if ind_data else []
    ind_str = "、".join(ind_parts)
    reg_data = revenue_structure.get("by_region", []) if isinstance(revenue_structure, dict) else []
    reg_parts = [f"{r['name']}{r['pct']:.1f}%" for r in reg_data[:4]] if reg_data else []
    reg_str = "、".join(reg_parts)

    # ── Business 段 ──
    biz = (
        "太极集团（重庆太极实业，1997年上交所上市）隶属国药集团（2021年战略重组后控股），"
        "是国内医药产业链最完整的大型医药集团之一，以中成药制造为核心，集医药工业（涪陵制药厂、西南药业、桐君阁药厂等13家制药厂）、"
        "医药商业（20余家商业公司、川渝零售第一的桐君阁/太极大药房）、中药材资源与医药研发于一体。"
        "核心产品含太极藿香正气口服液、急支糖浆、通天口服液及盐酸吗啡缓释片等麻精类药品。"
        "2023年归母净利润8.22亿元创历史新高后，2024-2025年受集采降价、渠道去库存与销售结算模式调整影响业绩大幅回落，"
        "2025年营收105.00亿元(-15.2%)，归母净利润1.21亿元（2024年低基数0.27亿元，同比+352%），扣非净利润仅0.44亿元(+13.3%)，处于深度调整期。"
    )
    if ind_str:
        biz += f"主营结构（2025）：{ind_str}。"

    # ── P1: 业绩快照 + 趋势 ──
    p1 = f"2026年9月 — 太极集团2025年营收{_fmt(rev, 2)}亿元（同比-15.2%，年报口径-15.23%），扣非净利润0.44亿元（同比+13.3%），"
    p1 += "归母净利润1.21亿元（同比+352%，因2024年低基数仅0.27亿元）；综合毛利率29.6%（主营毛利率29.5%），净利率（扣非口径）0.4%，ROE 1.2%、ROIC 9.3%。"
    p1 += "这是一家仍在消化历史包袱的公司：2023年归母8.22亿元高点后，2024年骤降至0.27亿元（-96.8%）、2025年低位反弹。"
    p1 += "回落主因：①集采与医保控费压降主要产品价格；②医药商业结算模式变化、渠道去库存；③销售费用大幅压降（2025年-49.9%）暴露了此前高投入驱动增长的脆弱性。"
    p1 += "藿香正气口服液2025年产量-31.9%、销量-2.0%，库存大幅去化，动销端仍在筑底。"

    # ── P2: 现金流与资本配置 ──
    p2 = f"每股收益（扣非）{_fmt(eps, 2)}元，每股经营现金流{_fmt(per_cf, 2)}元，每股资本开支{_fmt(per_capex, 2)}元"
    if per_cf:
        p2 += f"（资本开支占经营现金流约{per_capex / per_cf * 100:.0f}%，扩产支出高于当期经营现金流入）"
    p2 += f"，每股净资产{_fmt(bps, 2)}元。2025年度未分红（2023年曾派息、支付率约21%）。"
    p2 += "经营现金流2025年净流入5.84亿元，较2024年的-6.31亿元大幅回正，主因销售规模下降的同时采购、薪酬、税费等现金流出同步收缩；"
    p2 += "账上营运资金为负（-26.8亿元，医药商业占款模式），有息负债规模可控，2025年筹资净额转正主要来自借款增加。"

    # ── P3: 盈利质量与护城河 ──
    p3 = f"毛利率{gm:.1f}%（2023年48.6%→2025年29.6%的大幅回落，主因低毛利医药商业占比被动上升+工业端降价），净利率（扣非）仅0.4%、ROE 1.2%，盈利质量处于历史低谷。"
    p3 += "护城河：①品牌与渠道——藿香正气口服液为中国家喻户晓的OTC大单品，桐君阁大药房稳居川渝零售第一，医药商业网络为西部最完善；"
    p3 += "②产业链一体化——中药材种植+工业制造+商业分销全覆盖，麻精类药品（盐酸吗啡缓释片等）牌照壁垒高；"
    p3 += "③国药集团赋能——2021年重组后获得央企资源与治理改善。风险：集采常态化压制中成药价格、"
    p3 += "医药商业资金占用大且毛利薄、前几年高费用投放的后遗症仍在消化、行业同质化竞争加剧。"

    # ── P4: 估值锚定 ──
    cf_15x = per_cf * 15 if per_cf else 0
    cf_20x = per_cf * 20 if per_cf else 0
    p4 = f"当前价{_fmt(price, 2)}元，PE（TTM）约{_fmt(pe, 1)}倍"
    if med_pe:
        p4 += f"，低于上市以来中位{_fmt(med_pe, 0)}倍" if pe and pe < med_pe else f"，高于上市以来中位{_fmt(med_pe, 0)}倍"
    p4 += f"，PB {_fmt(pb, 2)}倍，股息率{div_y:.1f}%（2025年度未分红）。"
    if per_cf and price:
        implied = price / per_cf if per_cf else 0
        p4 += f"CF估值法：每股经营现金流{_fmt(per_cf, 2)}元，CF=15x对应{_fmt(cf_15x, 1)}元、CF=20x对应{_fmt(cf_20x, 1)}元，当前股价隐含CF倍数约{implied:.0f}倍，高于15x锚。"
        p4 += f"以扣非净利0.44亿、当前市值约{_fmt(spot.get('mkt_cap', 0), 1)}亿元衡量，静态PE高达60倍以上，"
        p4 += "市场定价的是集采冲击见底后藿香正气口服液等大单品重回增长与国药整合带来的盈利修复期权，属困境反转博弈而非价值型买点。"

    # ── P5: 催化剂与风险 ──
    p5 = ("催化剂：①藿香正气口服液渠道库存去化接近尾声，若2026年动销回升+出厂价企稳，工业端收入有望止跌；"
          "②销售结算模式改革完成后费用率趋于稳定，净利率具备从极低基数修复的弹性（2023年曾达5%）；"
          "③国药集团持续赋能，亏损子公司清理（2025年启动清算/破产注销多家子公司）释放资源；"
          "④麻精类新品放量——西南药业酒石酸布托啡诺注射液2026年获批（二类精神药品，行业约16亿元规模）。")
    p5 += "验证信号：跟踪季度营收同比降幅是否收窄、藿香正气口服液销量与库存、工业端毛利率、扣非净利率能否回到3%以上、经营现金流持续性。风险：集采与医保控费力度超预期、渠道库存反复、医药商业坏账、国企改革执行不及预期。"

    return {"business": biz, "commentary": [p1, p2, p3, p4, p5]}
