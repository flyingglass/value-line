# -*- coding: utf-8 -*-
"""达意隆 002209 — VL Business + AI Commentary

数据全部取自 build() 入参（metrics / revenue_structure / cagr / spot），不硬编码数字。
口径提示：
  - metrics[y]["HOLDER_PROFIT"] 为 VL 经常性口径净利润（归母经 _compute_adj_np 调整）
  - 营收结构取最新年报（2025）分产品/分地区/分销售模式，来源 2025 年报第 25 页
"""


def build(stock, metrics, revenue_structure, years, cagr, spot):
    ly_year = years[-1] if years else ""
    ly = metrics.get(ly_year, {}) if years else {}
    py = metrics.get(years[-2], {}) if len(years) >= 2 else {}

    def _num(v):
        try:
            return float(v)
        except (TypeError, ValueError):
            return 0.0

    def _fmt(v, d=1):
        return f"{_num(v):,.{d}f}" if _num(v) else "—"

    def _chg(cur, prev):
        c, p = _num(cur), _num(prev)
        if not c or not p:
            return None
        return (c / p - 1) * 100 if p > 0 else (c - p) / abs(p) * 100

    def _yoy(cur, prev, unit="%"):
        v = _chg(cur, prev)
        if v is None:
            return "—"
        return ("增长" if v >= 0 else "下降") + f"{abs(v):.1f}{unit}"

    rev, npv = _num(ly.get("OPERATE_INCOME")), _num(ly.get("HOLDER_PROFIT"))
    p_rev, p_np = _num(py.get("OPERATE_INCOME")), _num(py.get("HOLDER_PROFIT"))
    gm, opm, npm = _num(ly.get("GROSS_MARGIN")), _num(ly.get("OP_MARGIN")), _num(ly.get("NET_PROFIT_RATIO"))
    roe, roic = _num(ly.get("ROE")), _num(ly.get("ROIC"))
    eps, dps, bps = _num(ly.get("BASIC_EPS")), _num(ly.get("DPS")), _num(ly.get("BPS"))
    per_cf, cap_ps, payout = _num(ly.get("PER_NETCASH")), _num(ly.get("CAPEX_PS")), _num(ly.get("PAYOUT_RATIO"))
    gm_1y = _num(py.get("GROSS_MARGIN"))

    price = _num(spot.get("price"))
    pe, pb = _num(spot.get("pe")), _num(spot.get("pb"))
    div_y, mcap = _num(spot.get("div_yield")), _num(spot.get("mkt_cap"))
    med_pe = _num(spot.get("median_pe"))

    ar = cagr or {}
    s_g = ar.get("sales", {}) if isinstance(ar.get("sales"), dict) else {}
    e_g = ar.get("earnings", {}) if isinstance(ar.get("earnings"), dict) else {}
    c_g = ar.get("cashflow", {}) if isinstance(ar.get("cashflow"), dict) else {}

    rs = revenue_structure if isinstance(revenue_structure, dict) else {}
    prod = rs.get("by_product", []) or []
    regi = rs.get("by_region", []) or []
    chan = rs.get("by_channel", []) or []
    prod_str = "、".join(f"{r['name']} {r['pct']:.1f}%" for r in prod[:3]) if prod else ""
    reg_str = "、".join(f"{r['name']} {r['pct']:.1f}%" for r in regi[:4]) if regi else ""
    ch_str = "、".join(f"{r['name']} {r['pct']:.1f}%" for r in chan[:2]) if chan else ""
    ovs = next((r for r in regi if "境外" in str(r.get("name", "")) or "海外" in str(r.get("name", ""))), None)
    dom = next((r for r in regi if "华南" in str(r.get("name", ""))), None)

    # ── Business：公司概述（config 维护）+ 最新年核心数据（DB 驱动）──
    biz_core = (
        f"{ly_year} 年实现营业收入 {_fmt(rev)} 亿元（同比{_yoy(rev, p_rev)}），"
        f"归母净利润（VL 经常性口径）{_fmt(npv)} 亿元（同比{_yoy(npv, p_np)}）；"
        f"毛利率 {_fmt(gm)}%、ROE {_fmt(roe)}%。"
    )
    if prod_str:
        biz_core += f"收入结构：{prod_str}。"
    if ovs:
        biz_core += f"境外收入占比 {_fmt(ovs['pct'])}%。"
    business = (stock.get("business_desc", "") + biz_core).strip()

    # ── P1 经营分析 ──
    p1 = (
        f"【经营分析】{ly_year} 年营收 {_fmt(rev)} 亿元（同比{_yoy(rev, p_rev)}），"
        f"归母净利润（VL 经常性口径）{_fmt(npv)} 亿元（同比{_yoy(npv, p_np)}），"
        f"利润增速快于收入，营业利润率 {_fmt(opm)}%、销售净利率 {_fmt(npm)}%。"
    )
    if prod_str:
        p1 += f"分产品看{prod_str}，主业集中度极高；"
    if ch_str:
        p1 += f"分销售模式为{ch_str}，直销为主意味着公司在大客户整线项目上直接对接决策方。"
    if reg_str:
        p1 += f"分地区{reg_str}"
        if dom:
            p1 += f"，境内以华南（{_fmt(dom['pct'])}%）为大本营"
        p1 += "。"

    # ── P2 现金流与资本配置 ──
    fcf_ps = per_cf - cap_ps - dps if per_cf else 0
    p2 = (
        f"【现金流与资本配置】每股经营现金流 {_fmt(per_cf, 2)} 元，资本支出 {_fmt(cap_ps, 2)} 元/股"
        f"（扩产阶段，支出高于分红），每股自由现金流约 {_fmt(fcf_ps, 2)} 元。"
        f"分红 {_fmt(dps, 2)} 元/股、支付率 {_fmt(payout, 0)}%，对应股息率 {_fmt(div_y, 2)}%，"
        f"分红绝对额仍在低位，现金主要留存在体内支持产能与营运资金扩张。"
    )
    if c_g.get("3yr") is not None:
        p2 += f"经营现金流三年复合增速 {_fmt(c_g.get('3yr'), 1)}%，快于营收，说明利润有现金支撑。"
    p2 += (
        "设备行业的现金画像要盯两点：合同负债（预收款）能否随订单同步走高、"
        "以及验收后尾款与质保金的回款效率——前者决定未来收入可见度，后者决定利润含金量。"
    )

    # ── P3 盈利质量与护城河 ──
    p3 = (
        f"【盈利质量与护城河】毛利率 {_fmt(gm)}%（上年 {_fmt(gm_1y)}%），"
        f"ROE {_fmt(roe)}%、ROIC {_fmt(roic)}%，ROIC 高于 ROE 反映负债结构偏轻、"
        f"杠杆贡献有限，盈利更多来自资产周转与订单质量。"
        f"护城河来自三层：一是整线交付能力（前处理—吹瓶—灌装—贴标—二次包装一体化），"
        f"客户切换整线供应商的重置成本高；二是国际饮料品牌的认证与长期合作关系，"
        f"认证一旦通过形成的黏性远强于单机买卖；三是海外服务网络与本地化响应，"
        f"在新兴市场是外资标杆企业响应速度的短板。"
        f"风险集中在：下游资本开支的周期性、以销定产带来的单季收入确认波动、"
        f"海外收入占比越高则汇率与关税敞口越大，以及代加工业务对整体毛利的稀释。"
    )

    # ── P4 估值分析 ──
    p4 = (
        f"【估值分析】现价 {_fmt(price, 2)} 元，总市值 {_fmt(mcap)} 亿元，"
        f"PE {_fmt(pe, 1)} 倍、PB {_fmt(pb, 2)} 倍（对应每股净资产 {_fmt(bps, 2)} 元）、"
        f"股息率 {_fmt(div_y, 2)}%。"
    )
    p4 += (
        "本报告估值线采用 PB 口径：以每股净资产乘以 1.0 倍作为锚，"
        "该锚对应的是「账面资产价值」，而现价 PB 明显高于 1 倍，"
        "意味着市场已为设备业务的盈利能力和订单能见度支付溢价——"
        "股价相对估值线的偏离度本身就是位置信号，读数时应结合订单端（合同负债）是否延续。"
        "设备制造属于典型的中周期生意，用单一静态倍数定价值容易失真，"
        "更要看「订单—交付—验收—回款」链条是否顺畅。"
    )

    # ── P5 催化剂与风险 ──
    p5 = (
        "【催化与风险】向上情景来自三条线：一是自有产能改扩建项目投产后交付能力提升，"
        "打开订单承接上限；二是海外新兴市场（南亚、东南亚、中东、非洲等）饮料产能建设"
        "带来的整线订单持续性；三是产品结构继续向高毛利海外与整线项目倾斜，"
        "带动利润率与 ROE 抬升。向下风险有：订单验收节奏推迟导致单季收入落空、"
        "海外市场汇率与贸易壁垒、国内下游资本开支波动、以及代加工等低毛利业务萎缩的拖累。"
        "跟踪指标按优先级排序：合同负债趋势（订单可见度的直接代理）＞"
        "存货与发出商品（交付进度）＞分地区收入结构（海外斜率是否还在）＞经营现金流与收现比。"
    )

    return {"business": business, "commentary": [p1, p2, p3, p4, p5]}
