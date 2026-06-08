# -*- coding: utf-8 -*-
"""腾讯控股 00700 — VL 标准 Business + AI Commentary (5段)"""

def build(stock, metrics, revenue_structure, years, cagr, spot):
    latest_yr = years[-1] if years else "2025"
    ly = metrics.get(latest_yr, {})
    prev_yr = years[-2] if len(years) >= 2 else None
    py = metrics.get(prev_yr, {}) if prev_yr else {}

    def _chg(cur, prev):
        return (cur / prev - 1) * 100 if cur and prev and prev > 0 else None
    def _dir(cur, prev):
        c = _chg(cur, prev)
        if c is None: return ""
        return "增长" if c > 0 else ("下降" if c < 0 else "持平")
    def _fmt_pct(v):
        return f"{v:+.1f}%" if v is not None else "-"

    rev = ly.get("OPERATE_INCOME")
    np_val = ly.get("HOLDER_PROFIT")
    eps = ly.get("BASIC_EPS")
    gm = ly.get("GROSS_MARGIN")
    opm = ly.get("OP_MARGIN")
    npm = ly.get("NET_PROFIT_RATIO")
    roe = ly.get("ROE")
    roce = ly.get("ROIC")
    rev_chg = _chg(rev, py.get("OPERATE_INCOME"))
    np_chg = _chg(np_val, py.get("HOLDER_PROFIT"))
    per_cf = ly.get("PER_NETCASH")
    per_oi = ly.get("PER_OI")
    per_capex = ly.get("CAPEX_PS") or 0
    dps = ly.get("DPS") or 0
    payout = ly.get("PAYOUT_RATIO")

    # ---- Business ----
    business = (
        f"腾讯控股是全球最大的互联网科技公司之一，核心业务涵盖"
        f"社交通信（微信/QQ，月活13亿+）、游戏（全球最大游戏公司）、"
        f"金融科技（微信支付/理财通）、云服务及企业服务。"
        f"营收{rev:.0f}亿（{_dir(rev, py.get('OPERATE_INCOME'))}{abs(rev_chg):.1f}%），"
        f"净利率{_fmt_pct(npm)}，ROE {_fmt_pct(roe)}。"
        f"2025年回购超1,000亿港元，每股价值持续增厚。"
        f"AI大模型混元已全面接入核心业务，视频号广告为增长新引擎。"
    )

    # ---- Commentary 5段 ----
    tax_rate = (ly.get("TAX_EBT", 15) or 15) / 100
    op_eps = round(per_oi * (opm / 100) * (1 - tax_rate), 2) if per_oi and opm else None
    nonop_eps = round(eps - op_eps, 2) if eps and op_eps else None
    op_pct = round(op_eps / eps * 100) if eps and op_eps and eps != 0 else 0
    net_ps = round(per_cf - per_capex - dps, 2) if per_cf else None

    # 段1
    p1 = (
        f"2026年6月6日 — 腾讯控股{latest_yr}年营收约{rev:.0f}亿元（{_dir(rev, py.get('OPERATE_INCOME'))}{abs(rev_chg):.1f}%），"
        f"扣非净利润约{np_val:.0f}亿元（{_dir(np_val, py.get('HOLDER_PROFIT'))}{abs(np_chg):.1f}%）。"
        f"游戏：国内《王者荣耀》《和平精英》《DNF手游》基本盘稳固，国际游戏收入占比突破30%+；"
        f"广告：视频号广告VV同比增长80%+，广告收入突破1,200亿元；"
        f"金融科技及企业服务：AI混元大模型全面接入，云业务毛利率大幅改善。"
        + (f"利润增速{abs(np_chg):.0f}%超营收{abs(rev_chg):.0f}%，降本增效+回购增厚EPS效果显著。" if np_chg and rev_chg and np_chg > rev_chg * 1.5 else "")
    )

    # 段2
    wc, wc_p = ly.get("WORKING_CAPITAL"), py.get("WORKING_CAPITAL")
    shares, shares_p = ly.get("TOTAL_SHARES"), py.get("TOTAL_SHARES")
    shr_chg = round((shares - shares_p) / shares_p * 100, 1) if shares and shares_p and shares_p > 0 else None
    if eps and op_eps and nonop_eps:
        p2_parts = [
            f"每股收益¥{eps:.2f}中，主业经营贡献¥{op_eps:.2f}（{op_pct}%），"
            f"投资及非经营性贡献¥{nonop_eps:.2f}（{100-op_pct}%）。",
            f"每股经营现金流¥{per_cf:.2f}（内生现金生成 = 净利润 + 折旧），四大去向：",
            f"① 资本支出¥{per_capex:.2f}/股（AI算力+云基础设施）；",
        ]
        if wc is not None and wc_p is not None:
            wc_chg = wc - wc_p
            p2_parts.append(f"② 营运资金{'占用 +' if wc_chg > 0 else '释放 '}{abs(wc_chg):.1f}亿；")
        p2_parts.append(f"③ 现金分红¥{dps:.2f}/股（支付率{payout:.0f}%）；")
        if shr_chg is not None and shr_chg < -0.3:
            p2_parts.append(f"④ 股份回购（股数{shr_chg:+.1f}%）— 增厚每股价值 ✅；")
        elif shr_chg is not None and shr_chg > 0:
            p2_parts.append(f"④ 股数持平/微扩；")
        p2_parts.append(
            f"净留存¥{net_ps:.2f}/股。"
            f"2025年回购超1,000亿港元，相当于总股本缩减~3%，每股价值持续增厚。"
            f"净现金状态（现金远超债务），财务极度稳健。"
        )
        p2 = "".join(p2_parts)
    else:
        p2 = "每股资金流向：数据待补充。"

    # 段3
    p3 = (
        f"毛利率{_fmt_pct(gm)}、净利率{_fmt_pct(npm)}、ROE {_fmt_pct(roe)}——"
        f"腾讯的竞争壁垒是全球互联网中最深之一："
        f"①社交流量黑洞——微信13亿MAU形成的网络效应是地球上最强的消费者互联网护城河，"
        f"任何竞争者都无法复制；"
        f"②游戏产业链垂直整合——从研发（天美/光子/Riot/Supercell）到发行到电竞的"
        f"全链条控制，全球游戏收入第一；"
        f"③金融+云生态——微信支付覆盖10亿用户，企业服务处于AI转型风口。"
        f"风险：监管政策不确定性、游戏版号周期、宏观经济影响广告预算、AI投入回报周期。"
    )

    # 段4
    pe = spot.get("pe", 0) or 0
    median_pe = spot.get("median_pe")
    pb = spot.get("pb", 0) or 0
    div_yield = spot.get("div_yield", 0) or 0
    eps_1yr = cagr.get("eps", {}).get("1yr")

    p4 = (
        f"当前PE约{pe:.1f}倍"
        + (f"（non-IFRS口径更低估），低于历史中位数{median_pe:.0f}倍。" if median_pe and pe < median_pe else
           f"。估值尚可。" if not median_pe else "。")
        + f"PB约{pb:.1f}倍。股息率约{div_yield:.2f}%"
        + f"（港股通扣税后），但回购收益率约4%，综合股东回报率约4.5%。"
        + f"净现金2,000亿+，安全边际充足。"
        + f"核心逻辑：视频号广告加载率从3%→6%带来增量收入千亿级；"
        + f"AI大模型对内降本对外增收——这是PE重估的关键驱动力。"
    )

    # 段5
    signals = [
        "腾讯正处于AI应用爆发的历史级催化剂中",
        "混元大模型已覆盖微信搜一搜、腾讯云、广告、游戏NPC等核心场景",
        "广告业务AI赋能实现精准投放效率大幅提升",
        f"{'游戏收入增速稳健，国际占比持续提升' if rev_chg and rev_chg > 5 else '营收增速放缓，关注AI商业化进展验证'}",
    ]
    p5 = "。".join(signals) + "。"
    p5 += "若AI将广告/云/企业服务收入带入加速增长通道，PE存在显著重估空间。"

    return {
        "business": business,
        "commentary": [p1, p2, p3, p4, p5],
    }
