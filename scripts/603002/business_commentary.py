# -*- coding: utf-8 -*-
"""宏昌电子 603002 — VL Business + AI Commentary（数据驱动）

数据源原则：定量指标一律取 build.py 传入的 metrics / revenue_structure / cagr / spot；
经营事实（产能项目、产销、行业口径）取自 2026 年半年度报告原文（已在文中标注）。
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
    r_chg = _chg(rev, py.get("OPERATE_INCOME"))
    n_chg = _chg(np_val, py.get("HOLDER_PROFIT"))
    r_abs = abs(r_chg) if r_chg is not None else 0
    n_abs = abs(n_chg) if n_chg is not None else 0
    r_dir = _dir(rev, py.get("OPERATE_INCOME"))
    n_dir = _dir(np_val, py.get("HOLDER_PROFIT"))

    prod_data = revenue_structure.get("by_product", []) if isinstance(revenue_structure, dict) else []
    prod_str = "、".join([f"{r['name']}{r['pct']:.1f}%" for r in prod_data]) if prod_data else ""
    reg_data = revenue_structure.get("by_region", []) if isinstance(revenue_structure, dict) else []
    dom = next((r for r in reg_data if "境内" in str(r.get("name", ""))), None)
    ovs = next((r for r in reg_data if "境外" in str(r.get("name", ""))), None)

    # ── Business 段 ──
    biz = (
        "宏昌电子材料股份有限公司（上交所603002，广州黄埔）从事电子级环氧树脂、覆铜板（CCL）两大类产品的生产和销售，"
        "所属证监会行业为计算机、通信和其他电子设备制造业（C39）。环氧树脂为覆铜板基材、电子封装（电容/LED/半导体环氧塑封料）、"
        "重防腐涂料、风电叶片与复合材料提供材料；覆铜板及半固化片（PP）是印制电路板（PCB）的核心基材，"
        "下游为消费电子、通讯设备、服务器、车载工控、基站等。生产基地包括珠海宏昌（环氧树脂）、无锡宏仁（覆铜板）、"
        "珠海宏仁（高阶覆铜板电子材料），另有香港宏昌；2012年5月上交所上市（2026年中报原文）。"
    )
    biz += f"最新年度营收{_fmt(rev, 2)}亿元（同比{r_dir}{r_abs:.1f}%），净利润（扣非口径）{_fmt(np_val, 2)}亿元（{n_dir}），毛利率{gm:.1f}%，ROE {roe:.1f}%。"
    if prod_str:
        biz += f"业务结构：{prod_str}。"
    if dom and ovs:
        biz += f"境内营收占{dom['pct']:.1f}%，境外占{ovs['pct']:.1f}%。"

    # ── P1: 业绩快照 ──
    p1 = f"最新年度营收{_fmt(rev, 2)}亿元（同比{r_dir}{r_abs:.1f}%），净利润（扣非口径）{_fmt(np_val, 2)}亿元（{n_dir}），毛利率{gm:.1f}%，净利率{npm:.1f}%，ROE {roe:.1f}%。"
    p1 += "公司属典型“加工型材料”生意：毛利率与净利率薄（个位数），利润对销量、产能利用率与产品价格高度敏感，"
    p1 += "营收放量的年份利润弹性大，反之在行业产能过剩、价格下行时利润会被迅速压缩。"
    p1 += "2026年上半年已是这一弹性的体现：营收21.86亿元（同比+64.83%）、归母净利润3,939.15万元（同比+141.15%），"
    p1 += "其中环氧树脂业务净利519.73万元、覆铜板及半固化片业务净利3,419.42万元——利润主要来自覆铜板端（2026年中报原文）。"

    # ── P2: 现金流与资本配置 ──
    net_fcf = round(per_cf - per_capex - dps, 2) if per_cf else None
    p2 = f"每股收益（扣非）{_fmt(eps, 2)}元，每股经营现金流{_fmt(per_cf, 2)}元，每股资本开支{_fmt(per_capex, 2)}元"
    if per_cf:
        p2 += f"（资本开支占经营现金流约{per_capex / per_cf * 100:.0f}%，处于产能集中投放期）"
    p2 += f"，自由现金流{net_fcf}元/股，每股净资产{_fmt(bps, 2)}元。"
    if dps > 0:
        p2 += f"当期每股股息{_fmt(dps, 2)}元（支付率约{payout:.0f}%，股息率{div_y:.2f}%）。"
    else:
        p2 += "当期未分红，现金主要用于产能建设。"
    p2 += ("资本配置的核心是三个募投项目的连续投产：珠海宏昌二期“年产14万吨液态环氧树脂”（总投资7.79亿元，2025年5月建成投产）、"
           "珠海宏昌三期“年产8万吨电子级功能性环氧树脂”（总投资4.21亿元，含年产500吨高频高速树脂，2026年1月试生产、2026年8月21日取得安全生产许可证后正式生产）、"
           "珠海宏仁“功能性高阶覆铜板电子材料项目”（总投资5.01亿元，达产后年产高阶覆铜板720万张、半固化片1,440万米，2025年12月31日建成投产）——"
           "以上均为2026年中报原文。资本开支高峰已过，但新增产能能否达产并实现预期收益仍取决于下游需求与认证进度。")

    # ── P3: 盈利质量与护城河 ──
    p3 = f"毛利率{gm:.1f}%、净利率{npm:.1f}%、ROE {roe:.1f}%、ROIC {roic:.1f}%，是薄利加工型材料企业的典型特征："
    p3 += ("盈利能力受两头挤压——上游原料（环氧树脂端为双酚A、环氧氯丙烷、四溴双酚A；覆铜板端为铜箔、玻纤布、树脂）价格随行就市，"
           "下游面对PCB与电子电气客户的成本加成定价。护城河来源：①电子级+特种定位——公司产品主要应用于电子级和特种用途，"
           "属精细型，而多数竞争对手面向涂料级泛用型（2026年中报原文）；②高端树脂研发储备——围绕5G/超5G高频高速场景开发低介电聚醚（PPO）树脂、"
           "含磷阻燃聚醚、新型BT树脂等，多项已获专利授权或处于客户认证阶段（2026年中报原文）；③客户认证壁垒——高频高速材料需经下游覆铜板厂与终端客户"
           "长时间评估认证，切换成本高；④一体化协同——自有环氧树脂可直接配套覆铜板生产。"
           "主要约束：公司缺乏上游原料自产（需外购），而部分竞争对手具备完整产业链（2026年中报原文），成本端抗波动能力弱于对手。")

    # ── P4: 估值锚定 ──
    p4 = f"当前价{_fmt(price, 2)}元，PE（TTM）约{_fmt(pe, 1)}倍，PB {_fmt(pb, 2)}倍，股息率{div_y:.2f}%。"
    p4 += ("本标的为周期加工型材料股，利润波动大（行业景气时净利可翻倍、低迷时大幅回落），PE 在利润低基数年份会严重失真，"
           "因此以 PB 为主要估值锚：")
    if bps and price:
        implied_pb = price / bps if bps else 0
        p4 += f"每股净资产{_fmt(bps, 2)}元，当前价隐含PB约{implied_pb:.1f}倍；"
        for m in (1.5, 2.0, 2.5):
            p4 += f"PB={m}x对应{_fmt(bps * m, 2)}元，"
        p4 += "可作为资产口径的参考区间。"
    if per_cf and price:
        implied_cf = price / per_cf if per_cf else 0
        p4 += f"现金流口径参考：每股经营现金流{_fmt(per_cf, 2)}元，当前价隐含CF倍数约{implied_cf:.0f}倍。"
    p4 += ("需要注意：估值的前提是新增产能（珠海三期8万吨、宏仁高阶覆铜板720万张+半固化片1,440万米）能否转化为稳定销量与毛利，"
           "若产能去化不及预期，账面净资产扩张反而会摊薄ROE，构成“资产变重但回报不升”的风险。")

    # ── P5: 催化剂与风险 ──
    p5 = ("催化剂：①珠海宏昌三期（含500吨高频高速树脂）2026年8月正式投产后产能爬坡；②珠海宏仁高阶覆铜板项目产能释放并导入华南客户；"
          "③AI算力与数据中心建设带动高频高速、低损耗覆铜板需求，公司超5G/低介电树脂在下游客户处的认证与量产导入进展；"
          "④环氧树脂行业供给出清——2025年中国环氧树脂总产能422.8万吨/年、产量258万吨、行业平均开工率仅61%，"
          "若落后产能退出、开工率回升，产品价格与毛利有修复空间（数据来源：北京国化新材料技术研究院统计，转引自2026年中报）。")
    p5 += ("验证信号：季度营收增速与毛利率能否延续、覆铜板与半固化片产销增速、高频高速树脂认证与量产落地公告、应收账款与存货周转变化。"
           "风险：新增产能从投产到完全达产需时间且取决于下游需求波动与认证进度；环氧树脂行业产能持续释放、竞争加剧压制盈利；"
           "上游原料价格大幅波动；AI/算力需求若放缓，高端材料溢价与产能利用率同步回落。")

    return {"business": biz, "commentary": [p1, p2, p3, p4, p5]}
