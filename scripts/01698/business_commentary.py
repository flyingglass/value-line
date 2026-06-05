# -*- coding: utf-8 -*-
"""腾讯音乐 (01698) — 自定义 Business 描述 + AI Commentary

engine.py 优先调用本脚本 build()。返回 None 的字段回退到 engine 内置逻辑。
"""


def build(stock, metrics, rev_struct, years, cagr, spot):
    """返回 {"business": str|None, "commentary": [段1,段2,段3,段4] | None}"""
    name = stock.get("name", "腾讯音乐")
    if not years:
        return {"business": None, "commentary": None}

    ly = metrics.get(years[-1], {})
    py = metrics.get(years[-2], {}) if len(years) >= 2 else {}
    yr3 = metrics.get(years[-4], {}) if len(years) >= 4 else {}

    def _chg(cur, prev):
        return (cur / prev - 1) * 100 if cur and prev and prev > 0 else None

    def _dir_str(cur, prev):
        c = _chg(cur, prev)
        return f"增长{abs(c):.1f}%" if c and c > 0 else f"下降{abs(c):.1f}%" if c and c < 0 else "持平"

    # ── Business ──
    business_txt = (
        "腾讯音乐娱乐集团是中国最大的在线音乐娱乐平台，运营QQ音乐、酷狗音乐、"
        "酷我音乐和全民K歌四大产品矩阵。业务分为在线音乐服务（订阅+广告+数字专辑销售，"
        "占营收约80%）和社交娱乐服务（直播+K歌打赏，占营收约20%）。"
        "公司背靠腾讯生态获取流量，依托海量独家版权和AI推荐算法构建竞争壁垒，"
        "2024年以来在线音乐付费率持续提升，带动利润率结构性上行。"
    )

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
    pe = spot.get("pe", 0)
    pb = spot.get("pb", 0)
    div_y = spot.get("div_yield", 0)
    median_pe = spot.get("median_pe")
    latest_yr = years[-1]

    # ── 每股资金流向 ──
    op_eps = round(per_oi * (op_margin / 100), 2) if per_oi and op_margin else None
    nonop_eps = round(eps - op_eps, 2) if eps and op_eps else None
    net_ps = round(per_cf - per_capex - dps, 2) if per_cf is not None else None
    op_pct = round(op_eps / eps * 100) if eps and op_eps and eps != 0 else None
    nonop_pct = round(nonop_eps / eps * 100) if eps and nonop_eps and eps != 0 else None
    capex_pct = round(per_capex / per_cf * 100) if per_cf and per_capex and per_cf != 0 else None
    dps_pct = round(dps / per_cf * 100) if per_cf and dps and per_cf != 0 else None

    # ── 段1: 业绩快照 ──
    p1 = f"{name}{latest_yr}年营收{rev:.1f}亿元({_dir_str(rev, rev_p)})"
    if np_v is not None:
        p1 += f"，归母净利润{np_v:.1f}亿元({_dir_str(np_v, np_p)})"
    if eps:
        p1 += f"，每股收益¥{eps:.2f}"
    if gm:
        p1 += f"，毛利率{gm:.1f}%（同比{_dir_str(gm, gm_p)}）"
    if roe:
        p1 += f"，ROE {roe:.1f}%"
    rev_c = _chg(rev, rev_p)
    np_c = _chg(np_v, np_p)
    if np_c is not None and rev_c is not None and np_c > rev_c + 10:
        p1 += f"。利润增速远超营收，在线音乐付费率提升+成本管控驱动利润率大幅改善。"
    p1 += "。"

    # ── 段2: 每股资金流向 ──
    p2 = ""
    if eps and op_eps is not None and nonop_eps is not None:
        p2 = (f"每股收益¥{eps:.2f}中，主业贡献¥{op_eps:.2f}（{op_pct}%），"
              f"非经营性贡献¥{nonop_eps:.2f}（{nonop_pct}%）。")
        if per_cf is not None and net_ps is not None:
            p2 += (f"每股现金流¥{per_cf:.2f}中，资本支出¥{per_capex:.2f}占{capex_pct}%，"
                   f"现金分红¥{dps:.2f}占{dps_pct}%，净留存¥{net_ps:.2f}/股，"
                   f"现金流极为充裕。")

    # ── 段3: 业务质地 + 估值 ──
    p3_parts = [
        "以在线音乐订阅为核心（营收占比超80%），社交娱乐业务持续收缩但仍贡献现金流",
        f"当前PE {pe:.1f}倍"
    ]
    if median_pe:
        p3_parts[-1] += f"（远低于历史中位数{median_pe:.1f}倍）"
    if pb:
        p3_parts.append(f"PB {pb:.2f}倍")
    if div_y and div_y > 0:
        p3_parts.append(f"股息率{div_y:.1f}%")
    if roe is not None:
        roe_str = f"ROE {roe:.1f}%"
        if roe_p and roe > roe_p:
            roe_str += "（同比大幅提升）"
        p3_parts.append(roe_str)
    p3 = "。".join(p3_parts) + "。"

    # ── 段4: 趋势判断 + 验证信号 ──
    rev_1yr = cagr.get("revenue", {}).get("1yr")
    rev_3yr = cagr.get("revenue", {}).get("3yr")
    eps_1yr = cagr.get("earnings", {}).get("1yr")

    p4_parts = []
    if rev_1yr is not None and rev_3yr is not None:
        if rev_1yr > rev_3yr * 2:
            p4_parts.append(f"营收增速显著加速（1年+{rev_1yr:.1f}% vs 3年+{rev_3yr:.1f}%），付费用户渗透率提升驱动增长")
        elif rev_1yr > rev_3yr:
            p4_parts.append(f"营收增速加速（1年+{rev_1yr:.1f}% vs 3年+{rev_3yr:.1f}%）")

    if eps_1yr is not None and eps_1yr > 30:
        p4_parts.append(f"利润高速增长（EPS CAGR 1年+{eps_1yr:.1f}%），利润率扩张趋势明确")

    watch = [f"关注{int(latest_yr)+1}年中报付费用户数增速能否持续"]
    p4_parts.append("验证信号：" + "；".join(watch))
    p4 = "。".join(p4_parts) + "。"

    return {
        "business": business_txt,
        "commentary": [p1, p2, p3, p4],
    }
