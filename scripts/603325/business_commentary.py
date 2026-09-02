# -*- coding: utf-8 -*-
"""博隆技术 603325 — VL Business + AI Commentary（数据驱动, 手工精调）
口径说明: VL 净利润/每股收益采用扣非口径 (2025 扣非归母 3.71 亿 / 每股 4.64 元),
年报披露归母口径 4.10 亿 / EPS 5.13。文内以扣非口径为主数字, 归母口径另行注明。
"""
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
        v = _chg(c, p)
        if v is None: return "持平"
        return "增长" if v > 0.05 else ("下降" if v < -0.05 else "基本持平")
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
    roic = _num(ly.get("ROIC"))
    bps = _num(ly.get("BPS"))
    per_cf = _num(ly.get("PER_NETCASH"))
    per_capex = _num(ly.get("CAPEX_PS") or 0)
    dps = _num(ly.get("DPS") or 0)
    payout = _num(ly.get("PAYOUT_RATIO") or 0)
    price = _num(spot.get("price", 0))
    pe = _num(spot.get("pe", 0))
    pb = _num(spot.get("pb", 0))
    div_y = _num(spot.get("div_yield", 0))
    med_pe = spot.get("median_pe")
    r_chg = _chg(rev, py.get("OPERATE_INCOME"))
    n_chg = _chg(np_val, py.get("HOLDER_PROFIT"))
    r_abs = abs(r_chg) if r_chg is not None else 0
    n_abs = abs(n_chg) if n_chg is not None else 0
    r_dir = _dir(rev, py.get("OPERATE_INCOME"))
    n_dir = _dir(np_val, py.get("HOLDER_PROFIT"))

    # 营收结构
    prod_data = revenue_structure.get("by_product", []) if isinstance(revenue_structure, dict) else []
    prod_parts = [f"{r['name']}{r['pct']:.1f}%" for r in prod_data] if prod_data else []
    prod_str = "、".join(prod_parts)
    reg_data = revenue_structure.get("by_region", []) if isinstance(revenue_structure, dict) else []
    dom = next((r for r in reg_data if "境内" in str(r.get("name", ""))), None)
    ovs = next((r for r in reg_data if "境外" in str(r.get("name", ""))), None)

    # ── Business 段 ──
    biz = (
        "博隆技术（上海博隆装备，2024年1月上交所主板上市）是国内气力输送粉粒体物料处理系统解决方案龙头，"
        "为石油化工、煤化工、新材料、食品、医药等行业客户提供方案设计、关键设备制造、自动化控制与系统集成一体化服务，"
        "核心产品为成套系统（大型气力输送系统交钥匙工程）、单一功能系统（料仓、配混料系统等）及部件备件与服务，"
        "下游以合成树脂（聚烯烃）、煤化工为主。公司以内资龙头身份打破外资垄断，据公司披露在合成树脂领域合计市占率30%以上、"
        "煤制聚烯烃细分市占率近80%，并设有意大利子公司拓展海外。"
    )
    biz += f"2025年营收{_fmt(rev, 2)}亿元（同比+17.0%），净利润（扣非口径）{_fmt(np_val, 2)}亿元（同比+41.3%，年报归母4.10亿元、+38.1%），毛利率{gm:.1f}%，ROE {roe:.1f}%。"
    if prod_str:
        biz += f"产品结构：{prod_str}。"
    if dom and ovs:
        biz += f"境内占{dom['pct']:.1f}%，境外占{ovs['pct']:.1f}%（2025年境外收入+220%，海外料仓项目集中验收）。"

    # ── P1: 业绩快照 + 趋势 ──
    p1 = f"2026年9月 — 博隆技术2025年营收{_fmt(rev, 2)}亿元（同比+17.0%），扣非净利润{_fmt(np_val, 2)}亿元（同比+41.3%），"
    p1 += f"归母净利润4.10亿元（+38.1%）；毛利率{gm:.1f}%（+4.7pp），净利率{npm:.1f}%，ROE {roe:.1f}%。"
    p1 += "盈利弹性来自结构而非规模：当年交付验收大项目数量与单体规模增加，单一功能系统收入+56.4%且毛利率大幅升至31.5%（境外高复杂度料仓项目），"
    if ovs:
        p1 += f"境外收入{ovs['value'] / 100:.2f}亿元、同比+220%，海外项目普遍具备更高技术标准与毛利，是利润率上台阶的主引擎。"
    p1 += "2024年上市募资后净资产翻倍摊薄了ROE（2023年24.3%→2025年13.5%），但ROIC仍达17.4%，主业真实回报能力依然强劲。"

    # ── P2: 现金流与资本配置 ──
    net_fcf = round(per_cf - per_capex - dps, 2) if per_cf else None
    p2 = f"每股收益（扣非）{_fmt(eps, 2)}元，每股经营现金流{_fmt(per_cf, 2)}元，每股资本开支{_fmt(per_capex, 2)}元"
    if per_cf:
        p2 += f"（资本开支占经营现金流约{per_capex / per_cf * 100:.0f}%，其中含理财及产能投入）"
    p2 += f"，自由现金流{net_fcf}元/股。"
    p2 += f"2025年度每股股息{_fmt(dps, 2)}元（支付率约{payout:.0f}%，股息率{div_y:.1f}%），每股净资产{_fmt(bps, 2)}元。"
    p2 += "经营现金流2025年2.46亿元、同比下降45%，主因项目预收款节奏变化及采购存货付款增加，属项目制企业的正常波动而非恶化；"
    p2 += "账上类现金与理财充裕（含IPO募集），无有息负债压力，分红与扩产均有充足资金支撑。"

    # ── P3: 盈利质量与护城河 ──
    p3 = f"毛利率{gm:.1f}%在装备制造中显著偏高，净利率{npm:.1f}%更接近软件/设计型企业的水平——这是公司以方案设计+核心设备+系统集成为交付模式的体现，"
    p3 += f"ROE {roe:.1f}%、ROIC {roic:.1f}%。护城河：①know-how与业绩壁垒——气力输送系统需深度理解下游工艺，大型项目业绩记录（含6.6亿元在手海外大单）构成投标门槛；"
    p3 += "②国产替代卡位——合成树脂领域长期被外资垄断，公司凭性价比+本土服务在内资中居首，煤制聚烯烃细分市占率近80%；"
    p3 += "③定制化+直销模式——终端直销、深度绑定大型石化/煤化工客户，项目经验复利积累。风险：项目制收入确认波动大（2024年营收即下滑5.5%），大客户资本开支周期影响明显。"

    # ── P4: 估值锚定 ──
    cf_15x = per_cf * 15 if per_cf else 0
    cf_20x = per_cf * 20 if per_cf else 0
    p4 = f"当前价{_fmt(price, 2)}元，PE（TTM）约{_fmt(pe, 1)}倍"
    if med_pe:
        p4 += f"，低于上市以来中位{_fmt(med_pe, 1)}倍" if pe and pe < med_pe else f"，高于上市以来中位{_fmt(med_pe, 0)}倍"
    p4 += f"，PB {_fmt(pb, 2)}倍，股息率{div_y:.1f}%。"
    if per_cf and price:
        implied = price / per_cf if per_cf else 0
        p4 += f"CF估值法：每股经营现金流{_fmt(per_cf, 2)}元，CF=15x对应{_fmt(cf_15x, 1)}元、CF=20x对应{_fmt(cf_20x, 1)}元，当前股价隐含CF倍数约{implied:.0f}倍，低于15x锚。"
        p4 += f"以扣非净利3.71亿与扣非PE约{price / max(eps, 0.01):.0f}倍衡量，估值处于成长型装备股合理偏低区间；"
        if pe and med_pe and pe < med_pe:
            p4 += "上市以来PE中位16.6倍，当前13倍附近具备安全边际，若高毛利海外订单持续兑现存在盈利与估值双击空间。"

    # ── P5: 催化剂与风险 ──
    p5 = ("催化剂：①海外大单验收——6.6亿元海外气力输送系统合同进入交付期，2026年起逐期确认收入并抬升毛利率；"
          "②煤化工与新材料资本开支回暖——下游大型项目招标恢复带来新签订单增长；"
          "③产品结构升级——单一功能系统（料仓/配混料）高毛利放量，部件备件及服务后市场收入占比提升；"
          "④海外营销网络扩张——依托意大利子公司接轨国际标准，拓展东南亚、中东等市场。")
    p5 += "验证信号：跟踪新签订单金额、境外收入占比、单季毛利率（是否站稳37%+）、经营现金流回款节奏。风险：项目验收时点不确定导致业绩波动、下游化工资本开支放缓、海外执行与汇率风险。"

    return {"business": biz, "commentary": [p1, p2, p3, p4, p5]}
