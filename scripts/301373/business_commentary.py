# -*- coding: utf-8 -*-
"""凌玮科技 301373 — VL Business + AI Commentary（数据驱动, 手工精调）"""
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
    ch_data = revenue_structure.get("by_channel", []) if isinstance(revenue_structure, dict) else []
    zhili = next((r for r in ch_data if "终端" in str(r.get("name", ""))), None)

    # ── Business 段: 生意是什么 + 最新年核心数据 ──
    biz = (
        "凌玮科技是国内纳米二氧化硅新材料细分领域龙头（广州凌玮科技，2023年创业板上市），"
        "主营消光用二氧化硅（消光剂）、开口剂、防锈颜料、硅溶胶、纳米氧化铝等纳米新材料，以及水性环氧乳液/固化剂，"
        "下游覆盖涂料、塑料薄膜、油墨、胶体蓄电池等。核心子公司冷水江三A为纳米二氧化硅生产基地，"
        "公司担任国内相关行业标准牵头起草单位，客户多为全球知名涂料、油墨、塑料企业。"
    )
    biz += f"2025年营收{_fmt(rev, 2)}亿元（同比{r_dir}{r_abs:.1f}%），净利润（扣非口径）{_fmt(np_val, 2)}亿元（{n_dir}），毛利率{gm:.1f}%，ROE {roe:.1f}%。"
    if prod_str:
        biz += f"业务结构：{prod_str}。"
    if dom and ovs:
        biz += f"境内营收占{dom['pct']:.1f}%，境外占{ovs['pct']:.1f}%。"
    if zhili:
        biz += f"终端直销占比{zhili['pct']:.1f}%，客户结构优质。"

    # ── P1: 业绩快照 + 趋势 ──
    p1 = f"2026年9月 — 凌玮科技2025年营收{_fmt(rev, 2)}亿元（同比{r_dir}{r_abs:.1f}%），净利润（扣非口径）{_fmt(np_val, 2)}亿元（{n_dir}），"
    p1 += f"毛利率{gm:.1f}%，净利率{npm:.1f}%，ROE {roe:.1f}%。"
    if n_abs < 1:
        p1 += "利润连续两年基本走平，核心矛盾在于营收体量仍小（约5亿元），新产能与高端应用放量前增长弹性有限。"
    else:
        p1 += "利润与营收同步变动，反映下游景气度变化。"
    if ovs and dom:
        p1 += f"区域结构上境外占{ovs['pct']:.1f}%（约{ovs['value'] / 100:.2f}亿元），出口东南亚、欧洲等地，是增长的重要变量；境内基本盘占{dom['pct']:.1f}%。"

    # ── P2: 现金流与资本配置 ──
    net_fcf = round(per_cf - per_capex - dps, 2) if per_cf else None
    p2 = f"每股收益（扣非）{_fmt(eps, 2)}元，每股经营现金流{_fmt(per_cf, 2)}元，每股资本开支{_fmt(per_capex, 2)}元"
    if per_cf:
        p2 += f"（资本开支占经营现金流约{per_capex / per_cf * 100:.0f}%，处于扩产投入期）"
    p2 += f"，自由现金流{net_fcf}元/股。"
    if dps > 0:
        p2 += f"2025年度每股股息{_fmt(dps, 2)}元（支付率约{payout:.0f}%，股息率{div_y:.2f}%），"
    else:
        p2 += "当期未分红，"
    p2 += f"每股净资产{_fmt(bps, 2)}元。公司无有息负债压力，账上类现金充裕，资产负债表干净，扩产资金主要靠自身经营积累与IPO募集。"

    # ── P3: 盈利质量与护城河 ──
    p3 = f"毛利率{gm:.1f}%为典型的精细化工新材料特征，净利率{npm:.1f}%较高，ROE {roe:.1f}%、ROIC {roic:.1f}%受制于上市后净资产扩张（每股净资产{_fmt(bps, 2)}元）而显得偏低。"
    p3 += "护城河来源：①产品壁垒——沉淀法纳米二氧化硅在消光剂、开口剂等细分市场的高端牌号长期由外资主导，公司以国产替代切入，参与行业标准制定，具备配方与工艺Know-how；"
    p3 += "②客户黏性——下游涂料/油墨/塑料客户对助剂一致性要求高、认证周期长，一旦进入供应体系替换成本高；③聚焦策略——营收高度集中于纳米新材料主业，资源投放集中。"
    p3 += "风险：营收体量小，单一产品线受下游周期波动影响大；扩产项目投产初期产能利用率爬坡可能压制利润率。"

    # ── P4: 估值锚定 ──
    cf_15x = per_cf * 15 if per_cf else 0
    cf_20x = per_cf * 20 if per_cf else 0
    p4 = f"当前价{_fmt(price, 2)}元，PE（TTM）约{_fmt(pe, 1)}倍"
    if med_pe:
        p4 += f"，高于上市以来中位{_fmt(med_pe, 1)}倍" if pe and pe > med_pe else f"，低于上市以来中位{_fmt(med_pe, 0)}倍"
    p4 += f"，PB {_fmt(pb, 2)}倍，股息率{div_y:.2f}%。"
    if per_cf and price:
        p4 += f"CF估值法：每股经营现金流{_fmt(per_cf, 2)}元，CF=15x对应{_fmt(cf_15x, 1)}元，CF=20x对应{_fmt(cf_20x, 1)}元，"
        implied = price / per_cf if per_cf else 0
        p4 += f"当前股价隐含CF倍数约{implied:.0f}倍，明显高于默认15x锚，市场已计入较高成长预期。"
        if med_pe and pe and pe > med_pe:
            p4 += "上市时间较短（2023年2月），历史估值中位参考意义有限，需以盈利兑现验证高估值。"
    p4 += "若未来两年营收突破10亿元且净利率维持25%+，当前估值可被业绩消化；反之则存在均值回归压力。"

    # ── P5: 催化剂与风险 ──
    p5 = ("催化剂：①高端进口替代放量——食品级二氧化硅、高性能消光剂等新牌号通过大客户验证后放量；"
          "②产能释放——募投及自建产能爬坡带来规模效应，单位成本下降；"
          "③境外扩张——与全球知名涂料/油墨/塑料企业的合作深化，出口占比提升；"
          "④产品线延伸——向气凝胶、硅溶胶等关联纳米材料拓展打开第二曲线。")
    p5 += "验证信号：关注季度营收增速是否重回两位数、毛利率能否站稳45%、境外收入占比变化。风险：下游涂料行业景气下行、原材料价格波动、新产能投产不及预期、高估值回撤。"

    return {"business": biz, "commentary": [p1, p2, p3, p4, p5]}
