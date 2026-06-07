# -*- coding: utf-8 -*-
"""华晨中国 (01114) — 自定义 Business 描述 + AI Commentary

engine.py 优先调用本脚本 build()。返回 None 的字段回退到 engine 内置逻辑。
"""


def build(stock, metrics, rev_struct, years, cagr, spot):
    """返回 {"business": str|None, "commentary": [段1,段2,段3,段4] | None}"""
    name = stock.get("name", "华晨中国")
    if not years:
        return {"business": None, "commentary": None}

    ly = metrics.get(years[-1], {})
    py = metrics.get(years[-2], {}) if len(years) >= 2 else {}
    yr3 = metrics.get(years[-4], {}) if len(years) >= 4 else {}

    # ── 辅助 ──
    def _chg(cur, prev):
        return (cur / prev - 1) * 100 if cur and prev and prev > 0 else None

    def _dir_pct(cur, prev, label=""):
        c = _chg(cur, prev)
        return f"{label}增长{abs(c):.1f}%" if c and c > 0 else f"{label}下降{abs(c):.1f}%" if c and c < 0 else ""

    # ── Business ──
    business_txt = (
        "华晨中国是华晨汽车集团控股的香港上市公司，核心资产为持有华晨宝马25%股权"
        "（联营公司，不并表），自身并表业务涵盖轻型客车/MPV制造及汽车金融服务。"
        "2022年完成华晨宝马股权转让后，营收由联营公司投资收益驱动，"
        "并表营收规模约11亿元但利润率波动大，真实盈利能力需看联营贡献。"
    )

    # ── 关键数据 ──
    rev, rev_p = ly.get("OPERATE_INCOME"), py.get("OPERATE_INCOME")
    np_v, np_p = ly.get("HOLDER_PROFIT"), py.get("HOLDER_PROFIT")
    eps, eps_p = ly.get("BASIC_EPS"), py.get("BASIC_EPS")
    per_oi = ly.get("PER_OI")  # 每股营收
    per_cf = ly.get("PER_NETCASH")  # 每股现金流
    per_capex = ly.get("CAPEX_PS")  # 每股资本支出
    dps = ly.get("DPS", 0) or 0
    op_margin = ly.get("OP_MARGIN")  # 营业利润率
    gm, gm_p = ly.get("GROSS_MARGIN"), py.get("GROSS_MARGIN")
    roe, roe_p = ly.get("ROE"), py.get("ROE")
    pe = spot.get("pe", 0)
    pb = spot.get("pb", 0)
    div_y = spot.get("div_yield", 0)

    latest_yr = years[-1]

    # ── 每股资金流向计算 ──
    op_eps = round(per_oi * (op_margin / 100), 2) if per_oi and op_margin else None
    nonop_eps = round(eps - op_eps, 2) if eps and op_eps else None
    net_ps = round(per_cf - (per_capex or 0) - dps, 2) if per_cf is not None else None

    op_pct = round(op_eps / eps * 100) if eps and op_eps and eps != 0 else None
    nonop_pct = round(nonop_eps / eps * 100) if eps and nonop_eps and eps != 0 else None
    capex_pct = round(per_capex / per_cf * 100) if per_cf and per_capex and per_cf != 0 else None
    dps_pct = round(dps / per_cf * 100) if per_cf and dps and per_cf != 0 else None

    # ── 转折点检测 ──
    triggers = []

    # 营收反转: 1yr增速>0 AND 过去多年持续下降
    rev_1yr = cagr.get("revenue", {}).get("1yr")
    rev_3yr = cagr.get("revenue", {}).get("3yr")
    rev_5yr = cagr.get("revenue", {}).get("5yr")
    if rev_1yr is not None and rev_1yr > 0 and rev_3yr is not None and rev_3yr < -5:
        triggers.append("🔄 营收增速反转：多年下行后重获正增长，关注持续性")

    # 利润率反转: 毛利率 1yr 改善 AND 3yr 整体走低
    if gm and gm_p and gm > gm_p:
        gm_vals = [metrics.get(str(y), {}).get("GROSS_MARGIN") for y in years[-3:]]
        gm_vals = [v for v in gm_vals if v is not None]
        if len(gm_vals) >= 2 and gm_vals[-1] > gm_vals[0]:
            triggers.append("🔄 毛利率止跌回升，盈利质量边际改善")

    # 现金流方向反转
    if net_ps is not None:
        py_per_cf = py.get("PER_NETCASH")
        py_capex = py.get("CAPEX_PS") or 0
        py_dps = py.get("DPS", 0) or 0
        if py_per_cf is not None:
            py_net = round(py_per_cf - py_capex - py_dps, 2)
            if (net_ps > 0 > py_net):
                triggers.append("🔄 每股净留存由负转正，现金流状况改善")
            elif (net_ps < 0 < py_net):
                triggers.append("⚠️ 每股净留存由正转负，现金流承压")

    # ROE 反转
    roe_vals = [metrics.get(str(y), {}).get("ROE") for y in years]
    roe_vals = [v for v in roe_vals if v is not None]
    if len(roe_vals) >= 3:
        avg_before = sum(roe_vals[-4:-1]) / 3 if len(roe_vals) >= 4 else sum(roe_vals[:-1]) / (len(roe_vals)-1)
        if roe_vals[-1] > avg_before * 1.1:
            triggers.append("🔄 ROE 触底反弹：盈利能力较近年均值大幅改善")

    # ── 段1: 业绩快照 ──
    p1 = f"{name}{latest_yr}年营收{rev:.1f}亿元({_dir_pct(rev,rev_p)})" if rev else ""
    if np_v is not None:
        p1 += f"，扣非净利润{np_v:.1f}亿元({_dir_pct(np_v,np_p)})"
    if eps:
        p1 += f"，每股收益¥{eps:.2f}"
    if gm:
        p1 += f"，毛利率{gm:.1f}%"
    if roe:
        p1 += f"，ROE {roe:.1f}%"
    # 解释变化原因
    rev_c = _chg(rev, rev_p)
    np_c = _chg(np_v, np_p)
    if np_c is not None and rev_c is not None and abs(np_c - rev_c) > 10:
        if np_c > rev_c:
            p1 += f"。联营公司华晨宝马贡献了利润的大部分，是盈利波动的核心变量"
        else:
            p1 += f"。并表业务利润增速落后营收，关注成本端及联营投资贡献"
    p1 += "。"

    # ── 段2: 每股资金流向 (全新) ──
    p2 = ""
    if eps and op_eps is not None and nonop_eps is not None:
        p2 = (f"每股收益¥{eps:.2f}中，主业贡献¥{op_eps:.2f}（{op_pct}%），"
              f"非经营性贡献¥{nonop_eps:.2f}（{nonop_pct}%）。")
        if per_cf is not None and net_ps is not None:
            p2 += (f"每股现金流¥{per_cf:.2f}中，资本支出¥{per_capex or 0:.2f}占{capex_pct or 0}%，"
                   f"现金分红¥{dps:.2f}占{dps_pct or 0}%，净留存¥{net_ps:.2f}/股")
            if net_ps > 0:
                p2 += "，现金流充裕。"
            else:
                p2 += "，入不敷出，消耗存量现金储备。"
    else:
        p2 = f"财报数据不足以计算每股资金流向分解。"

    # ── 段3: 业务质地 + 估值 ──
    p3_parts = []
    p3_parts.append("核心资产华晨宝马25%股权为联营公司，贡献大部分利润但不并表")
    p3_parts.append("自身轻型客车/MPV业务体量小（年销约2万辆），利润微薄")

    # 估值
    if pe:
        pe_str = f"当前PE {pe:.1f}倍"
        if pe < 0:
            pe_str += "（利润为负，PE无参考意义）"
        p3_parts.append(pe_str)
    if pb is not None:
        p3_parts.append(f"PB {pb:.2f}倍")
    if div_y and div_y > 0:
        p3_parts.append(f"股息率{div_y:.1f}%")
    if roe is not None:
        roe_str = f"ROE {roe:.1f}%"
        if roe_p and roe > roe_p:
            roe_str += "（同比提升）"
        p3_parts.append(roe_str)

    p3 = "。".join(p3_parts) + "。"

    # ── 段4: 趋势判断 + 转折点检测 + 验证信号 ──
    p4_parts = []

    if rev_1yr is not None and rev_3yr is not None:
        if rev_1yr > rev_3yr:
            p4_parts.append(f"营收增速加速（1年{rev_1yr:+.1f}% vs 3年{rev_3yr:+.1f}%）")
        elif rev_1yr < rev_3yr and rev_1yr > 0:
            p4_parts.append(f"营收增速放缓（1年{rev_1yr:+.1f}% vs 3年{rev_3yr:+.1f}%）")

    # 插入转折点信号
    for t in triggers:
        p4_parts.append(t)

    # 验证信号
    watch = []
    if net_ps is not None and net_ps < 0:
        watch.append(f"关注{int(latest_yr)+1}年中报净留存是否回升至正值")
    else:
        watch.append(f"关注{int(latest_yr)+1}年华晨宝马销量与单车利润变化")

    if watch:
        p4_parts.append("验证信号：" + "；".join(watch))

    p4 = "。".join(p4_parts) + "。"

    commentary = [p1, p2, p3, p4]

    return {
        "business": business_txt,
        "commentary": commentary,
    }
