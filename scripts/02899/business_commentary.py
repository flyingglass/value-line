# -*- coding: utf-8 -*-
"""紫金矿业 (02899) — 自定义 Business 描述 + AI Commentary

engine.py 优先调用本脚本 build()。返回 None 的字段回退到 engine 内置逻辑。
"""


def build(stock, metrics, rev_struct, years, cagr, spot):
    """返回 {"business": str|None, "commentary": [段1,段2,段3,段4] | None}"""
    name = stock.get("name", "紫金矿业")
    if not years:
        return {"business": None, "commentary": None}

    ly = metrics.get(years[-1], {})
    py = metrics.get(years[-2], {}) if len(years) >= 2 else {}

    # ── 辅助 ──
    def _chg(cur, prev):
        return (cur / prev - 1) * 100 if cur and prev and prev > 0 else None

    def _dir_pct(cur, prev, label=""):
        c = _chg(cur, prev)
        return f"{label}+{abs(c):.1f}%" if c and c > 0 else f"{label}{c:.1f}%" if c and c < 0 else ""

    # ── Business ──
    business_txt = (
        "紫金矿业是全球领先的大型跨国矿业集团，主营金、铜、锌等金属矿产资源的勘查、开采和冶炼，"
        "在中国、非洲、南美等地拥有多个世界级矿山。2025年营收3,491亿元(+15.0%)，归母净利润466亿元(+65.1%)，"
        "金铜价格上行驱动利润爆发式增长。旗下卡莫阿-卡库拉铜矿（刚果金）、巨龙铜矿（西藏）等世界级矿山持续放量，"
        "铜产量突破100万吨跻身全球前五，黄金产量约68吨。"
    )

    # ── 关键数据 ──
    rev, rev_p = ly.get("OPERATE_INCOME"), py.get("OPERATE_INCOME")
    np_v, np_p = ly.get("HOLDER_PROFIT"), py.get("HOLDER_PROFIT")
    eps = ly.get("BASIC_EPS")
    per_oi = ly.get("PER_OI")
    per_cf = ly.get("PER_NETCASH")
    per_capex = ly.get("CAPEX_PS") or 0
    dps = ly.get("DPS", 0) or 0
    gm, gm_p = ly.get("GROSS_MARGIN"), py.get("GROSS_MARGIN")
    op_margin = ly.get("OP_MARGIN")
    roe, roe_p = ly.get("ROE"), py.get("ROE")
    roic = ly.get("ROIC")
    npm = ly.get("NET_PROFIT_RATIO")
    wc, wc_p = ly.get("WORKING_CAPITAL"), py.get("WORKING_CAPITAL")
    lt_debt = ly.get("LT_DEBT")
    equity = ly.get("TOTAL_EQUITY")
    bps = ly.get("BPS")
    shares = ly.get("TOTAL_SHARES")
    pe = spot.get("pe", 0)
    pb = spot.get("pb", 0)
    div_y = spot.get("div_yield", 0)

    latest_yr = years[-1]

    # ── 每股资金流向计算 ──
    op_eps = round(per_oi * (op_margin / 100), 2) if per_oi and op_margin else None
    nonop_eps = round(eps - op_eps, 2) if eps and op_eps else None
    net_ps = round(per_cf - per_capex - dps, 2) if per_cf is not None else None

    op_pct = round(op_eps / eps * 100) if eps and op_eps and eps != 0 else None
    capex_pct = round(per_capex / per_cf * 100) if per_cf and per_capex and per_cf != 0 else None
    dps_pct = round(dps / per_cf * 100) if per_cf and dps and per_cf != 0 else None

    # ── 段1: 业绩快照 ──
    p1 = f"{name}{latest_yr}年营收{rev:.1f}亿元({_dir_pct(rev,rev_p)})"
    if np_v is not None:
        nc = _chg(np_v, np_p)
        nc_str = f"+{nc:.1f}%" if nc is not None and nc > 0 else f"{nc:.1f}%" if nc is not None else ""
        p1 += f"，归母净利润{np_v:.1f}亿元({nc_str})" if nc_str else f"，归母净利润{np_v:.1f}亿元"
    if eps:
        p1 += f"，每股收益¥{eps:.2f}"
    p1 += f"。受益于金铜价格中枢上移及矿山产能释放，利润弹性充分释放。"
    if gm and gm_p:
        gm_chg = gm - gm_p
        p1 += f"毛利率{gm:.1f}%（同比{gm_chg:+.1f}ppt），矿产品量价齐升推动盈利质量大幅改善。"
    if roe and roe_p:
        roe_chg = roe - roe_p
        p1 += f"ROE {roe:.1f}%（同比{roe_chg:+.1f}ppt）。"

    # ── 段2: 每股资金流向 ──
    p2 = ""
    if eps and op_eps is not None:
        p2_parts = [
            f"每股收益¥{eps:.2f}中，主业经营贡献¥{op_eps:.2f}（{op_pct}%），"
        ]
        if nonop_eps is not None and abs(nonop_eps) > 0.05:
            p2_parts.append(f"非经常性贡献¥{nonop_eps:.2f}。")
        if per_cf is not None and net_ps is not None:
            p2_parts.append(
                f"每股经营现金流¥{per_cf:.2f}，四大去向："
                f"①资本支出¥{per_capex:.2f}/股（占现金流{capex_pct}%，矿山扩建持续投入）；"
            )
            if wc is not None and wc_p is not None and shares:
                wc_chg = wc - wc_p
                wc_ps = abs(wc_chg * 100 / shares) if shares > 0 else 0
                p2_parts.append(f"②营运资金{'增加 ' if wc_chg > 0 else '释放 '}{abs(wc_chg):.0f}亿（约¥{wc_ps:.2f}/股）；")
            p2_parts.append(f"③现金分红¥{dps:.2f}/股（占现金流{dps_pct}%）；")
            p2_parts.append(f"④净留存¥{net_ps:.2f}/股")
            if net_ps < 0:
                p2_parts.append("，高强度资本开支下自由现金流为负，依赖外部融资。")
            else:
                p2_parts.append("。")
        p2 = "".join(p2_parts)

    # ── 段3: 业务质地 + 估值 ──
    p3_parts = []
    p3_parts.append("紫金矿业是全球增长最快的大型矿企")
    p3_parts.append(f"2025年铜产量突破100万吨，黄金产量约68吨")
    p3_parts.append("核心矿山：卡莫阿-卡库拉（刚果金，全球品位最高铜矿之一）、巨龙铜矿（西藏）、Timok（塞尔维亚）持续扩产")

    # 估值
    if pe:
        p3_parts.append(f"当前PE {pe:.1f}倍（低于历史中枢，受益于利润高增长）")
    if pb is not None:
        bps_str = f"¥{bps:.2f}" if bps else "N/A"
        p3_parts.append(f"PB {pb:.2f}倍，每股净资产{bps_str}，PB=1.0x目标价约{bps_str}")
    if div_y and div_y > 0:
        p3_parts.append(f"股息率{div_y:.1f}%")
    if roe is not None:
        p3_parts.append(f"ROE {roe:.1f}%")
    if lt_debt and equity:
        debt_ratio = lt_debt / equity * 100
        p3_parts.append(f"资产负债率{debt_ratio:.0f}%（矿业正常水平）")

    p3 = "。".join(p3_parts) + "。"

    # ── 段4: 趋势判断 + 验证信号 ──
    rev_1yr = cagr.get("revenue", {}).get("1yr")
    rev_5yr = cagr.get("revenue", {}).get("5yr")
    ear_1yr = cagr.get("earnings", {}).get("1yr")
    ear_5yr = cagr.get("earnings", {}).get("5yr")

    p4_parts = []
    p4_parts.append("金铜价格是核心变量——2025年金价突破历史新高，铜价受新能源+AI基建需求支撑维持高位")
    p4_parts.append("产能扩张管线充沛：卡莫阿三期、巨龙二期、西藏朱诺铜矿等在建项目将推动未来3-5年铜金产量持续增长")
    p4_parts.append("风险：金铜价格周期性回落、海外矿山地缘政治风险（刚果金/南美）、高资本开支下融资压力、环保政策趋严")
    p4_parts.append(f"验证信号：关注每季度金铜均价走势及矿山产量指引达成率——这是估值能否修复的核心驱动力")

    p4 = "。".join(p4_parts) + "。"

    commentary = [p1, p2, p3, p4]

    return {
        "business": business_txt,
        "commentary": commentary,
    }
