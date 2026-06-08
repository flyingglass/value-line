# -*- coding: utf-8 -*-
"""腾讯音乐 01698 — VL 标准 Business + AI Commentary (5段)"""

def build(stock, metrics, revenue_structure, years, cagr, spot):
    latest_yr = years[-1] if years else "2025"
    ly = metrics.get(latest_yr, {})
    prev_yr = years[-2] if len(years) >= 2 else None
    py = metrics.get(prev_yr, {}) if prev_yr else {}

    def _chg(c, p):
        return (c / p - 1) * 100 if c and p and p > 0 else None
    def _dir(c, p):
        d = _chg(c, p)
        return "增长" if d and d > 0 else ("下降" if d and d < 0 else "持平")
    def _pct(v):
        return f"{v:+.1f}%" if v is not None else "-"

    rev, np_v = ly.get("OPERATE_INCOME"), ly.get("HOLDER_PROFIT")
    eps, gm, npm, roe = ly.get("BASIC_EPS"), ly.get("GROSS_MARGIN"), ly.get("NET_PROFIT_RATIO"), ly.get("ROE")
    rev_c, np_c = _chg(rev, py.get("OPERATE_INCOME")), _chg(np_v, py.get("HOLDER_PROFIT"))
    per_cf, per_capex, dps = ly.get("PER_NETCASH"), ly.get("CAPEX_PS") or 0, ly.get("DPS") or 0
    pay, pe, med_pe = ly.get("PAYOUT_RATIO"), spot.get("pe", 0), spot.get("median_pe")

    business = (
        f"腾讯音乐娱乐集团是中国领先的在线音乐平台，运营QQ音乐、酷狗音乐、酷我音乐及全民K歌。"
        f"通过在线音乐订阅（会员付费）和社交娱乐服务双轮变现，付费用户破1.2亿。"
        f"营收{rev:.0f}亿（{_dir(rev, py.get('OPERATE_INCOME'))}{abs(rev_c):.1f}%），"
        f"净利率{_pct(npm)}，ROE {_pct(roe)}。AI音乐创作与推荐驱动创新。"
    )

    # 段1
    p1 = (f"2026年6月6日 — 腾讯音乐{latest_yr}年营收约{rev:.0f}亿元（{_dir(rev, py.get('OPERATE_INCOME'))}{abs(rev_c):.1f}%），"
          f"扣非净利润约{np_v:.0f}亿元（{_dir(np_v, py.get('HOLDER_PROFIT'))}{abs(np_c):.1f}%）。"
          f"在线音乐付费用户持续增长，订阅ARPPU稳步提升，在线音乐服务收入占比超60%。"
          f"社交娱乐板块（直播）受短视频冲击持续收缩，但占比降至30%以下影响递减。"
          + (f"利润增速超营收，成本端版权占比下降释放利润率。" if np_c and rev_c and np_c > rev_c else ""))

    # 段2
    wc, wc_p = ly.get("WORKING_CAPITAL"), py.get("WORKING_CAPITAL")
    shares, shares_p = ly.get("TOTAL_SHARES"), py.get("TOTAL_SHARES")
    shr_chg = round((shares - shares_p) / shares_p * 100, 1) if shares and shares_p and shares_p > 0 else None
    net_ps = round(per_cf - per_capex - dps, 2) if per_cf else None
    op_eps = round(eps * 0.85, 2) if eps else None  # approx operating
    p2_parts = [
        f"每股收益¥{eps:.2f}，音乐订阅为主业核心驱动力（约85%+）。"
        f"每股现金流¥{per_cf:.2f}（内生现金生成 = 净利润 + 折旧），四大去向：",
        f"① 资本支出¥{per_capex:.2f}/股（轻资产，版权为主）；",
    ]
    if wc is not None and wc_p is not None:
        wc_chg = wc - wc_p
        p2_parts.append(f"② 营运资金{'占用 +' if wc_chg > 0 else '释放 '}{abs(wc_chg):.1f}亿；")
    p2_parts.append(f"③ 现金分红¥{dps:.2f}/股（支付率{pay:.0f}%）；")
    if shr_chg is not None and shr_chg < -0.3:
        p2_parts.append(f"④ 股份回购（股数{shr_chg:+.1f}%）— 增厚每股价值 ✅；")
    elif shr_chg is not None and shr_chg > 0:
        p2_parts.append(f"④ 股数持平/微扩；")
    p2_parts.append(f"净留存¥{net_ps:.2f}/股，净现金状态，现金流充沛，版权成本占比持续下降。")
    p2 = "".join(p2_parts)

    # 段3
    p3 = (f"毛利率{_pct(gm)}、净利率{_pct(npm)}、ROE {_pct(roe)}。"
          f"竞争壁垒：①双平台（QQ音乐+酷狗）覆盖年轻+下沉用户全域人群，MAU超6亿；"
          f"②版权壁垒——与环球/索尼/华纳三大唱片长期独家/优先合作；"
          f"③付费率提升路径清晰（<20% vs Spotify 45%+），ARPPU提升空间大。"
          f"风险：短视频平台音乐分流、直播业务持续萎缩、付费率爬坡不及预期。")

    # 段4
    pb, div_y = spot.get("pb", 0), spot.get("div_yield", 0) or 0
    p4 = (f"当前PE约{pe:.1f}倍"
          + (f"，低于历史中位数{med_pe:.0f}倍。" if med_pe and pe < med_pe else "。")
          + f"PB约{pb:.1f}倍，股息率约{div_y:.2f}%。"
          + f"对标Spotify（PE 80x+），腾讯音乐估值折价显著——"
          + f"市场给予的是「衰退中的直播公司」估值，而非「付费率爬坡中的音乐平台」估值。"
          + f"若付费率突破25%，估值逻辑可能重估。")

    # 段5
    eps1 = cagr.get("eps", {}).get("1yr")
    p5 = (f"关注付费率何时突破25%（对标Spotify）及AI音乐商业化落地。"
          + (f"当前EPS增速{eps1:+.1f}%支撑当前估值，向上弹性取决于付费率加速。" if eps1 else ""))

    return {"business": business, "commentary": [p1, p2, p3, p4, p5]}
