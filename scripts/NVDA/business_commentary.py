# -*- coding: utf-8 -*-
"""英伟达 NVDA — VL Business + AI Commentary (数据驱动)"""
def build(stock, metrics, revenue_structure, years, cagr, spot):
    latest_yr = years[-1] if years else "2025"
    ly = metrics.get(latest_yr, {})
    prev_yr = years[-2] if len(years) >= 2 else None
    py = metrics.get(prev_yr, {}) if prev_yr else {}

    def _dir(cur, prev):
        if not cur or not prev or prev <= 0: return ""
        c = (cur / prev - 1) * 100
        return "增长" if c > 0 else ("下降" if c < 0 else "持平")

    rev = ly.get("OPERATE_INCOME"); np_val = ly.get("HOLDER_PROFIT")
    eps = ly.get("BASIC_EPS"); gm = ly.get("GROSS_MARGIN")
    npm = ly.get("NET_PROFIT_RATIO"); roe = ly.get("ROE")
    roce = ly.get("ROIC"); per_cf = ly.get("PER_NETCASH")
    dps = ly.get("DPS") or 0; payout = ly.get("PAYOUT_RATIO")
    per_capex = ly.get("CAPEX_PS") or 0
    rev_prev = py.get("OPERATE_INCOME")
    rev_chg = (rev / rev_prev - 1) * 100 if rev and rev_prev and rev_prev > 0 else None

    business = f"英伟达(NVIDIA)是全球AI算力芯片领导者，GPU市占率超80%。{latest_yr}年营收${rev:.0f}亿" + (f"（{_dir(rev, rev_prev)}{abs(rev_chg):.1f}%）" if rev_chg else "") + f"，净利率{npm:.1f}%，ROE {roe:.1f}%。数据中心业务为最大收入来源，AI大模型训练推理需求驱动高速增长。"

    np_prev = py.get("HOLDER_PROFIT")
    np_chg = (np_val / np_prev - 1) * 100 if np_val and np_prev and np_prev > 0 else None

    p1 = f"{latest_yr}财年营收约${rev:.0f}亿" + (f"（{_dir(rev, rev_prev)}{abs(rev_chg):.1f}%）" if rev_chg else "") + f"，净利润约${np_val:.1f}亿" + (f"（{_dir(np_val, np_prev)}{abs(np_chg):.1f}%）" if np_chg else "") + f"。毛利率{gm:.1f}%，净利率{npm:.1f}%。数据中心GPU需求持续爆发。"

    net_ps = round(per_cf - per_capex - dps, 2) if per_cf else None
    p2 = f"每股收益${eps:.2f}。每股现金流${per_cf:.2f}，资本支出${per_capex:.2f}，现金分红${dps:.2f}" + (f"（支付率{payout:.0f}%）" if payout else "") + (f"，净留存${net_ps:.2f}/股" if net_ps else "") + "。"

    p3 = f"毛利率{gm:.1f}%、净利率{npm:.1f}%、ROE {roe:.1f}%。" + (f"ROIC {roce:.1f}%。" if roce else "") + "竞争壁垒：①CUDA生态锁定全球AI开发者；②每年一代GPU架构迭代速度碾压竞品；③与台积电深度绑定先进制程产能。风险：AI资本开支周期性、出口管制、竞争加剧。"

    pe = spot.get("pe", 0) or 0; pb = spot.get("pb", 0) or 0
    div_yield = spot.get("div_yield", 0) or 0
    p4 = f"当前PE约{pe:.1f}倍，PB约{pb:.1f}倍，股息率约{div_yield:.2f}%。关注AI Capex趋势及Blackwell/下一代GPU出货节奏。"

    p5 = f"关注{latest_yr}年报及下季度指引作为验证信号。AI算力需求未见天花板，GPU迭代速度决定估值天花板。"

    return {"business": business, "commentary": [p1, p2, p3, p4, p5]}
