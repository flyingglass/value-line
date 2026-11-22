# -*- coding: utf-8 -*-
"""润贝航科 001316 — VL Business + AI Commentary（手动精写, 2026-11-22）

口径（宪法）:
  - build() 返回 {"business": ..., "commentary": [p1..p5]}。
  - 所有数字均取自入参 metrics / revenue_structure / cagr / spot，不硬编码。
  - 定性描述仅取自已核实原文：公司官网「集团介绍」、2025 年报 p20/p21/p36，
    不含可比公司估值中枢、行业规模、市占率等 DB 中不存在的数字。
  - 营收结构原始出处：data/pdfs/润贝航科/001316_润贝航科_2025_年报.pdf p21
    「（1）营业收入构成」，由 scripts/001316/insert_revenue.py 入库。
"""


def build(stock, metrics, revenue_structure, years, cagr, spot):
    ly = metrics.get(years[-1], {}) if years else {}
    py = metrics.get(years[-2], {}) if len(years) >= 2 else {}
    yr = str(years[-1]) if years else "最新"

    def _chg(c, p):
        try:
            c2, p2 = float(c), float(p)
            if not c2 or not p2:
                return None
            return (c2 / p2 - 1) * 100
        except (ValueError, TypeError, ZeroDivisionError):
            return None

    def _num(v):
        try:
            return float(v)
        except (ValueError, TypeError):
            return 0.0

    def _fmt(v, d=0):
        try:
            return f"{float(v):,.{d}f}"
        except (ValueError, TypeError):
            return "-"

    def _p(v):
        try:
            return f"{float(v):+.1f}%"
        except (ValueError, TypeError):
            return "-"

    name = stock.get("name", "润贝航科")
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
    lt_debt = _num(ly.get("LT_DEBT"))
    total_eq = _num(ly.get("TOTAL_EQUITY"))
    shares = _num(ly.get("TOTAL_SHARES"))
    price = _num(spot.get("price", 0))
    pe = _num(spot.get("pe", 0)) or (round(price / eps, 1) if price and eps else 0)
    pb = _num(spot.get("pb", 0)) or (round(price / bps, 2) if price and bps else 0)
    div_y = _num(spot.get("div_yield", 0)) or (round(dps / price * 100, 1) if price and dps else 0)

    rev_chg = _chg(rev, py.get("OPERATE_INCOME"))
    np_chg = _chg(np_val, py.get("HOLDER_PROFIT"))
    rev_dir = "增长" if (rev_chg or 0) > 0 else "下降"
    np_dir = "增长" if (np_chg or 0) > 0 else "下降"
    rev_abs = abs(rev_chg) if rev_chg is not None else 0.0
    np_abs = abs(np_chg) if np_chg is not None else 0.0

    rs = revenue_structure if isinstance(revenue_structure, dict) else {}

    # engine 的 cagr 形如 {"revenue": {"1yr":..,"5yr":..}, "equity": {...}, "eps": {...}}
    def _cagr(key, span="5yr"):
        if not isinstance(cagr, dict):
            return None
        v = cagr.get(key, {})
        return _num(v.get(span)) if isinstance(v, dict) else None

    bv_cagr = _cagr("equity")
    rev_cagr = _cagr("revenue")
    eps_cagr = _cagr("eps")
    cagr_parts = []
    if rev_cagr:
        cagr_parts.append(f"营收5年复合增速{_p(rev_cagr)}")
    if eps_cagr:
        cagr_parts.append(f"每股盈利5年复合增速{_p(eps_cagr)}")
    cagr_note = "、".join(cagr_parts) + "。" if cagr_parts else ""

    def _join(dim):
        rows = rs.get(dim, []) or []
        return "、".join(f"{r.get('name', '')}{_num(r.get('pct')):.0f}%" for r in rows)

    prod_str = _join("by_product")
    region_str = _join("by_region")
    channel_str = _join("by_channel")
    struct_note = "（来源：2025年报 p21「营业收入构成」）"

    # ── Business：1 段公司概述 + 最新年核心数据 ──
    biz = (
        f"润贝航空科技股份有限公司（LUBAIR，001316.SZ）是集研发、生产、销售于一体的航空器材"
        f"解决方案综合服务商，坚持「航材分销+航材国产化」双轮驱动：分销民用航空油料、航空原材料、"
        f"航空化学品等航材，同时研发国产化 PMA 零部件、高分子复合材料、胶带胶膜及精细化工类产品，"
        f"2022-06-24 于深交所主板上市（来源：公司官网 lubair.com「集团介绍」、2025 年报"
        f"「第三节 管理层讨论与分析」、AKShare stock_info_sz_name_code 深交所 A 股列表）。"
        f"{yr}年营业收入{_fmt(rev / 1e8, 2)}亿元（同比{rev_dir}{rev_abs:.1f}%），"
        f"归母净利润{_fmt(np_val / 1e8, 2)}亿元（同比{np_dir}{np_abs:.1f}%）。"
        + (f"业务结构：{prod_str}{struct_note}。" if prod_str else "")
    )

    # ── P1：经营分析 ──
    p1 = (
        f"{yr}年{name}营业收入{_fmt(rev / 1e8, 2)}亿元（同比{rev_dir}{rev_abs:.1f}%），"
        f"归母净利润{_fmt(np_val / 1e8, 2)}亿元（同比{np_dir}{np_abs:.1f}%），"
        f"毛利率{_p(gm)}、净利率{_p(npm)}。"
        + (f"按产品拆分：{prod_str}；" if prod_str else "")
        + (f"按地区拆分：{region_str}；" if region_str else "")
        + (f"按销售模式拆分：{channel_str}。" if channel_str else "")
        + f"三项拆分各自对应同期营业收入合计{struct_note}。"
        f"2025 年报将增长归因于国产化自研业务与分销业务规模同步扩张，并披露自研产品毛利率高于分销产品"
        f"（来源：2025 年报 p20「主营业务分析」、p21「占公司营业收入或营业利润10%以上的行业、产品、地区」）。"
    )

    # ── P2：现金流与资本配置 ──
    free_cf = per_cf - per_capex - dps
    debt_note = (
        f"长期债务{_fmt(lt_debt / 1e8, 2)}亿元、股东权益{_fmt(total_eq / 1e8, 2)}亿元，"
        if lt_debt or total_eq else ""
    )
    p2 = (
        f"每股收益{_fmt(eps, 2)}元，每股经营现金流{_fmt(per_cf, 2)}元，"
        f"每股资本支出{_fmt(per_capex, 2)}元，扣除分红后的每股自由现金流{_fmt(free_cf, 2)}元；"
        f"分红{_fmt(dps, 2)}元/股（支付率{_fmt(payout, 0)}%，股息率约{_fmt(div_y, 1)}%），"
        f"每股净资产{_fmt(bps, 2)}元。{debt_note}"
        f"公司上市以来连续现金分红（来源：data/db/001316.db dividend 表，巨潮分红数据）。"
        + (f"账面价值5年复合增速{_p(bv_cagr)}。" if bv_cagr else "")
    )

    # ── P3：盈利质量与护城河 ──
    p3 = (
        f"ROE {_p(roe)}，ROIC {_p(roic)}，毛利率{_p(gm)}、净利率{_p(npm)}。"
        f"护城河的可核验来源集中在资质与渠道，而非规模假设：①公司是较早取得油料适航批准书及"
        f"航材分销商证书的企业，航材分销需适航与质量体系认证，准入本身构成门槛；"
        f"②常备航材料号众多、具备一站式采购与仓储物流/信息系统管理能力，客户覆盖航空公司、"
        f"维修企业与制造商，切换供应商涉及适航重新验证；③国产化自研业务已形成从选型、开发、"
        f"取证、上机测试到销售售后的全流程能力，自研产品需逐件号取得民航局适航批准"
        f"（来源：公司官网「集团介绍」、2025 年报 p20、p36）。"
        f"风险：上游供应商涨价与供应链波动、存货跌价与仓储物流管理、人才流失、"
        f"国产化产品市场导入节奏（来源：2025 年报 p36「运营风险」及「非主营业务分析」中的存货跌价准备）。"
    )

    # ── P4：估值分析（PB 框架，按用户确认倍数动态锚定） ──
    pb_mult = stock.get("pb")
    pb_line = ""
    if pb_mult and bps:
        target = bps * _num(pb_mult)
        rel = (target / price - 1) * 100 if price else 0
        pb_line = (
            f"按用户确认的 PB {_fmt(pb_mult, 2)}x 估值线，对应{_fmt(target, 2)}元/股，"
            f"较现价{_fmt(price, 2)}元{'溢价' if rel > 0 else '折价'}{_fmt(abs(rel), 1)}%。"
        )
    p4 = (
        f"当前股价{_fmt(price, 2)}元，PE约{_fmt(pe, 1)}倍，PB {_fmt(pb, 2)}倍"
        f"（每股净资产{_fmt(bps, 2)}元），股息率约{_fmt(div_y, 1)}%。{pb_line}"
        f"本标的采用 PB 法估值：资产端以每股净资产为锚，估值线的合理性取决于净资产的可变现质量与"
        f"ROE 能否维持，需结合存货（航材备货）与应收账款的周转情况判断账面价值含金量"
        f"（来源：data/db/001316.db 三大报表与 spot；估值方法由用户确认）。"
        + cagr_note
    )

    # ── P5：催化剂与风险 ──
    p5 = (
        f"催化剂：①航材国产化替代——自研产品适航取证件号持续增加、纳入商飞工艺材料产品目录，"
        f"高毛利自研业务占比若提升将改善整体利润率；②数智化工具落地——AI 航检眼镜解决方案与"
        f"RPA 流程应用提升服务附加值与运营效率；③下游民航维修与机队需求回暖带动航材采购量"
        f"（来源：2025 年报 p20「主营业务分析」、p36「公司未来发展的展望」）。"
        f"风险：上游涨价无法向下游传导、供应链与国际物流波动、存货跌价、国产化产品验证与"
        f"市场导入慢于预期。跟踪信号：分产品收入中自研产品占比与毛利率、存货与应收账款周转、"
        f"适航取证件号增量（来源：2025 年报 p21、p36；DB 中无件号与市占率数据，不作量化预测）。"
    )

    return {"business": biz, "commentary": [p1, p2, p3, p4, p5]}
