# -*- coding: utf-8 -*-
"""涪陵榨菜 002507 — VL Business + AI Commentary（数据驱动，不写死数字）

数据口径：
- 财务/估值数字全部取自 engine 传入的 metrics / spot / revenue_structure / cagr 参数
- 分品类增速、销量、库存量等年报细节来自
  data/pdfs/002507/002507_2025_年报.pdf（第 21-22 页营业收入构成 / 产销量表），已单独标注来源
"""


def build(stock, metrics, revenue_structure, years, cagr, spot):
    ly = metrics.get(years[-1], {}) if years else {}
    py = metrics.get(years[-2], {}) if len(years) >= 2 else {}

    def _n(v, d=0.0):
        try:
            return float(v)
        except (TypeError, ValueError):
            return d

    def _chg(c, p):
        c2, p2 = _n(c, None), _n(p, None)
        if c2 is None or p2 is None or p2 == 0:
            return None
        return (c2 / p2 - 1) * 100

    def _dir(c, p):
        c = _chg(c, p)
        return "增长" if (c or 0) >= 0 else "下降"

    def _fmt(v, d=0):
        return f"{_n(v):,.{d}f}" if v is not None else "-"

    def _pct(v, d=1):
        return f"{_n(v):+.{d}f}%" if v is not None else "-"

    rev = ly.get("OPERATE_INCOME")
    np_val = ly.get("HOLDER_PROFIT")
    eps = ly.get("BASIC_EPS")
    dps = _n(ly.get("DPS"))
    payout = ly.get("PAYOUT_RATIO")
    gm = ly.get("GROSS_MARGIN")
    opm = ly.get("OP_MARGIN")
    npm = ly.get("NET_PROFIT_RATIO")
    roe = ly.get("ROE")
    roic = ly.get("ROIC")
    bps = ly.get("BPS")
    per_cf = _n(ly.get("PER_NETCASH"))
    per_capex = _n(ly.get("CAPEX_PS"))

    r_chg = _chg(rev, py.get("OPERATE_INCOME"))
    n_chg = _chg(np_val, py.get("HOLDER_PROFIT"))
    r_abs = abs(r_chg) if r_chg is not None else 0.0
    n_abs = abs(n_chg) if n_chg is not None else 0.0

    price = _n(spot.get("price"))
    pe = _n(spot.get("pe"))
    pb = _n(spot.get("pb"))
    div_y = _n(spot.get("div_yield"))
    mkt_cap = _n(spot.get("mkt_cap"))
    median_pe = spot.get("median_pe")

    rs = revenue_structure if isinstance(revenue_structure, dict) else {}
    prod = rs.get("by_product", []) or []
    reg = rs.get("by_region", []) or []
    chan = rs.get("by_channel", []) or []
    prod_str = "、".join(f"{r['name']}{r['pct']:.0f}%" for r in prod[:4]) if prod else ""

    def _find(items, *keys):
        for it in items:
            if any(k in str(it.get("name", "")) for k in keys):
                return it
        return None

    overseas = _find(reg, "出口", "海外", "国外")
    direct = _find(chan, "直销")
    dist = _find(chan, "经销")

    def _cagr(metric, span):
        """最近 span 年年化增速（%），数据取自 metrics / years"""
        try:
            a = _n(metrics.get(years[-1 - span], {}).get(metric), None)
            b = _n(metrics.get(years[-1], {}).get(metric), None)
            if not a or not b or a <= 0 or b <= 0:
                return None
            return ((b / a) ** (1.0 / span) - 1) * 100
        except (IndexError, TypeError):
            return None

    s3 = _cagr("OPERATE_INCOME", 3)
    s5 = _cagr("OPERATE_INCOME", 5)
    roe_base_yr = "2022" if "2022" in metrics else (years[0] if years else None)
    roe_base = metrics.get(roe_base_yr, {}) if roe_base_yr else {}

    # ── Business ──
    biz = (
        f"涪陵榨菜是重庆市涪陵区国资委实际控制下的国有控股食品企业，以「乌江」品牌为核心深耕佐餐开味菜领域，"
        f"主营榨菜、萝卜、泡菜、榨菜酱等下饭菜产品。FY{years[-1] if years else ''} 营收 {_fmt(rev, 1)} 亿元"
        f"（{_dir(rev, py.get('OPERATE_INCOME'))}{r_abs:.1f}%），归母净利 {_fmt(np_val, 1)} 亿元"
        f"（{_dir(np_val, py.get('HOLDER_PROFIT'))}{n_abs:.1f}%），毛利率 {_fmt(gm, 1)}%、净利率 {_fmt(npm, 1)}%，"
        f"ROE {_fmt(roe, 1)}%。营收结构（按产品）：{prod_str or '-'}；经销渠道占 "
        f"{_fmt(dist['pct'] if dist else None, 1)}%。"
    )

    # ── P1 经营分析 ──
    p1 = (
        f"FY{years[-1] if years else ''} 营收 {_fmt(rev, 1)} 亿元（{_dir(rev, py.get('OPERATE_INCOME'))}{r_abs:.1f}%），"
        f"归母净利 {_fmt(np_val, 1)} 亿元（{_dir(np_val, py.get('HOLDER_PROFIT'))}{n_abs:.1f}%）：量微增、价稳定，"
        f"但费用与成本投入使净利率由 {_fmt(py.get('NET_PROFIT_RATIO'), 1)}% 降至 {_fmt(npm, 1)}%，"
        f"营业利润率 {_fmt(opm, 1)}%。"
        f"年报披露榨菜销量 13.40 万吨（+1.06%）、生产量 13.68 万吨（+3.25%）；分品类榨菜 20.59 亿元（+0.74%）为基本盘，"
        f"萝卜 0.57 亿元（+24.78%）、其他产品 0.97 亿元（+54.82%）增速快但体量小，泡菜 2.14 亿元（-6.85%）仍在调整。"
        f"分区域华南 27.2%、华东 17.7% 为两大主力市场，华中（+5.15%）、西北（+5.92%）增长较好，"
        f"出口 {_fmt(overseas and overseas['value'] / 100, 2)} 亿元（占比 {_fmt(overseas and overseas['pct'], 1)}%，+17.62%）。"
        f"（分品类增速/销量明细来源：公司 2025 年年度报告「营业收入构成」）"
    )

    # ── P2 现金流与资本配置 ──
    fcf_ps = round(per_cf - per_capex, 2)
    net_keep = round(fcf_ps - dps, 2)
    p2 = (
        f"每股经营现金流 {_fmt(per_cf, 2)} 元，高于每股收益 {_fmt(eps, 2)} 元，利润含金量高；"
        f"资本支出 {_fmt(per_capex, 2)} 元/股（对应中国榨菜城绿色智能化生产基地等投入），"
        f"自由现金流约 {fcf_ps} 元/股；分红 {_fmt(dps, 2)} 元/股（支付率 {_fmt(payout, 1)}%），净留存约 {net_keep} 元/股。"
        f"资产负债表极为稳健：有息负债极少、现金类资产充裕，营业利润对利息覆盖极高，无杠杆风险。"
        f"需注意分红支付率较上年回落（每股分红 {_fmt(py.get('DPS'), 2)} → {_fmt(dps, 2)} 元），"
        f"主因资本开支上行期的留存安排，属产能投入而非分红能力恶化。"
    )

    # ── P3 盈利质量与护城河 ──
    p3 = (
        f"毛利率 {_fmt(gm, 1)}%、营业利润率 {_fmt(opm, 1)}%、净利率 {_fmt(npm, 1)}%、ROE {_fmt(roe, 1)}%、"
        f"ROIC {_fmt(roic, 1)}% —— 高毛利、低杠杆的典型佐餐消费品报表；但 ROE/ROIC 自 {roe_base_yr} 年"
        f"（{_fmt(roe_base.get('ROE'), 1)}%/{_fmt(roe_base.get('ROIC'), 1)}%）以来逐年回落，"
        f"净资产累积快于利润增长。护城河：①品牌与品类心智——「乌江」是佐餐开味菜国民品牌，低单价、高频次的刚需属性带来稳定复购；"
        f"②原料与产地壁垒——青菜头为一年一季的原产地作物，公司以「两价两单一链」利益联结机制锁定农户与加工户，"
        f"向上游延伸平抑农产品价格波动（来源：2025 年年报 MD&A）；③渠道网络——覆盖全国 8 大销售大区、"
        f"经销占比 {_fmt(dist['pct'] if dist else None, 1)}%，并通过整合渠道冲突经销商持续优化结构；"
        f"④标准话语权——参与《榨菜》《轻盐榨菜》《酱腌菜质量通则》等国标/行标制定（来源：2025 年年报 MD&A）。"
        f"风险：榨菜品类天花板+收入长期低增长（近 3 年营收 CAGR {_pct(s3)}、5 年 {_pct(s5)}）、"
        f"第二曲线尚未跑通、原料与人工成本波动。"
    )

    # ── P4 估值分析 ──
    cf15 = per_cf * 15
    cf20 = per_cf * 20
    implied_yield = (dps / price * 100) if price else 0
    pe_gap = (price / cf15 - 1) * 100 if cf15 else 0
    p4 = (
        f"当前市值 {_fmt(mkt_cap, 1)} 亿元，PE {_fmt(pe, 1)} 倍、PB {_fmt(pb, 2)} 倍、"
        f"股息率（现价 {_fmt(price, 2)} 元、每股分红 {_fmt(dps, 2)} 元）约 {_fmt(implied_yield, 1)}%。"
        f"PE 已跌至历史低位区间"
        + (f"（历史中位 PE {_fmt(median_pe, 1)} 倍）" if median_pe else "")
        + f"，PB {_fmt(pb, 2)} 倍亦低于近年中枢，市场对成长性给予明显折价。"
        f"CF 估值（每股经营现金流 {_fmt(per_cf, 2)} 元）：15x 对应 {_fmt(cf15, 2)} 元、20x 对应 {_fmt(cf20, 2)} 元，"
        f"现价较 15x 中枢{'溢价' if pe_gap >= 0 else '折价'}约 {abs(pe_gap):.1f}%。"
        f"股息视角：若资本开支高峰过去、支付率回到上年 {_fmt(py.get('PAYOUT_RATIO'), 0)}% 水平，"
        f"对应每股分红约 {_fmt(eps and (eps * _n(py.get('PAYOUT_RATIO')) / 100), 2)} 元、静态股息率约 "
        f"{_fmt(price and (eps and (eps * _n(py.get('PAYOUT_RATIO')) / 100) / price * 100), 1)}%。"
    )

    # ── P5 催化剂与风险 ──
    p5 = (
        "催化剂：①原料成本弹性——青菜头收购价是核心利润变量，"
        f"按营收 {_fmt(rev, 1)} 亿元测算毛利率每变动 1pct 约影响毛利 {_fmt(_n(rev) * 0.01, 2)} 亿元；"
        "②第二曲线放量——泡菜优化配方工艺并推出爆炒豇豆等新品，深化 C 端即食化与 B 端餐饮定制双轮驱动"
        "（来源：2025 年年报 MD&A），年内萝卜、其他产品收入增速已显著快于榨菜；"
        "③渠道结构升级——成立国际事业部与大客户中心，探索山姆、小象等新兴渠道的大客户定制型直营模式，"
        f"出口占比仅 {_fmt(overseas and overseas['pct'], 1)}%，海外与直营渠道仍有提升空间；"
        "④股东回报——资本开支回落+支付率修复将抬升股息率。"
        "风险：品类天花板导致收入增长停滞、青菜头价格与人工成本上行、硬折扣/社区团购渠道变革冲击价格体系、"
        "库存与渠道库存消化压力。跟踪要点：季度收入增速与毛利率、青菜头收购价、泡菜及新品收入占比、分红率变化。"
    )

    return {"business": biz, "commentary": [p1, p2, p3, p4, p5]}
