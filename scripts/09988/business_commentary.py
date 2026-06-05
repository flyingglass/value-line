# -*- coding: utf-8 -*-
"""阿里巴巴 (09988) — 自定义 Business 描述 + AI Commentary

engine.py 优先调用本脚本 build()。返回 None 的字段回退到 engine 内置逻辑。
"""


def build(stock, metrics, rev_struct, years, cagr, spot):
    """返回 {"business": str|None, "commentary": [段1,段2,段3,段4] | None}"""
    name = stock.get("name", "阿里巴巴")
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
        "阿里巴巴集团是中国最大的电商和云计算公司，业务涵盖淘天集团（淘宝天猫，占营收约44%）、"
        "云智能集团（阿里云，约11%）、国际数字商业（约10%）、菜鸟物流（约10%）、"
        "本地生活（饿了么高德，约6%）和大文娱（优酷等，约5%）七大板块。"
        "以平台模式运营，轻资产高毛利，近年加码AI大模型（通义千问Qwen）和全球化扩张，"
        "中国大陆营收约74%、国际市场约26%。"
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
    latest_yr = years[-1]
    pe_avg_hist = ly.get("PE_AVG")
    pe_range_min = None
    pe_range_max = None
    pe_all = [(v.get("PE_AVG"), k) for k, v in metrics.items() if v.get("PE_AVG")]
    if pe_all:
        pe_vals = [p[0] for p in pe_all]
        pe_range_min = min(pe_vals)
        pe_range_max = max(pe_vals)

    # ── 每股资金流向 ──
    op_eps = round(per_oi * (op_margin / 100), 2) if per_oi and op_margin else None
    nonop_eps = round(eps - op_eps, 2) if eps and op_eps else None
    net_ps = round(per_cf - per_capex - dps, 2) if per_cf is not None else None
    op_pct = round(op_eps / eps * 100) if eps and op_eps and eps != 0 else None
    nonop_pct = round(nonop_eps / eps * 100) if eps and nonop_eps and eps != 0 else None
    capex_pct = round(per_capex / per_cf * 100) if per_cf and per_capex and per_cf != 0 else None
    dps_pct = round(dps / per_cf * 100) if per_cf and dps and per_cf != 0 else None

    # ── 段1: 业绩快照 ──
    p1 = f"{name}{latest_yr}财年营收{rev:.1f}亿元({_dir_str(rev, rev_p)})"
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
    if np_c is not None and rev_c is not None and np_c < rev_c - 15:
        p1 += f"。利润下滑主因云智能及国际业务持续投入，以及非经常性投资收益波动。"
    p1 += "。"

    # ── 段2: 每股资金流向 ──
    p2 = ""
    if eps and op_eps is not None and nonop_eps is not None:
        p2 = (f"每股收益¥{eps:.2f}中，主业贡献¥{op_eps:.2f}（{op_pct}%），"
              f"非经营性贡献¥{nonop_eps:.2f}（{nonop_pct}%）。")
        if per_cf is not None and net_ps is not None:
            p2 += (f"每股现金流¥{per_cf:.2f}中，资本支出¥{per_capex:.2f}占{capex_pct}%，"
                   f"现金分红¥{dps:.2f}占{dps_pct}%，净留存¥{net_ps:.2f}/股。")

    # ── 段3: 业务质地 + 估值 ──
    p3_parts = [
        "以淘天集团电商为核心（营收占比超40%），云智能+国际业务为第二增长曲线",
        f"当前PE {pe:.1f}倍"
    ]
    if pe_range_min and pe_range_max:
        p3_parts[-1] += f"（历史区间{pe_range_min:.1f}-{pe_range_max:.1f}倍，低于均值）"
    if pb:
        p3_parts.append(f"PB {pb:.2f}倍")
    if div_y and div_y > 0:
        p3_parts.append(f"股息率{div_y:.1f}%")
    if roe is not None:
        p3_parts.append(f"ROE {roe:.1f}%（投资回报率偏低，资本配置效率待提升）")
    p3 = "。".join(p3_parts) + "。"

    # ── 段4: 趋势判断 + 验证信号 ──
    rev_1yr = cagr.get("revenue", {}).get("1yr")
    rev_3yr = cagr.get("revenue", {}).get("3yr")
    rev_5yr = cagr.get("revenue", {}).get("5yr")
    eps_1yr = cagr.get("earnings", {}).get("1yr")
    eps_3yr = cagr.get("earnings", {}).get("3yr")

    p4_parts = []
    if rev_1yr is not None:
        if rev_1yr < 5:
            p4_parts.append(f"营收低速增长（1年+{rev_1yr:.1f}%），电商主业增速见顶，增长依赖云和国际化")
        else:
            p4_parts.append(f"营收增速{rev_1yr:+.1f}%（1年）")

    if eps_1yr is not None and eps_1yr < 0 and eps_3yr is not None and eps_3yr > 0:
        p4_parts.append(f"⚠️ 利润增速由正转负（1年{eps_1yr:+.1f}% vs 3年{eps_3yr:+.1f}%），注意投资支出对利润的侵蚀")

    watch = [f"关注{int(latest_yr)+1}财年云业务利润率是否改善", "关注国际电商减亏进度"]
    p4_parts.append("验证信号：" + "；".join(watch))
    p4 = "。".join(p4_parts) + "。"

    return {
        "business": business_txt,
        "commentary": [p1, p2, p3, p4],
    }
