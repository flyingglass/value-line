# -*- coding: utf-8 -*-
"""中航信 00696 — VL 标准 Business + AI Commentary (5段)"""

def build(stock, metrics, revenue_structure, years, cagr, spot):
    latest_yr = years[-1] if years else "2025"
    ly = metrics.get(latest_yr, {})
    py = metrics.get(years[-2], {}) if len(years) >= 2 else {}

    def _chg(c, p): return (c/p-1)*100 if c and p and p>0 else None
    def _dir(c,p): d=_chg(c,p); return "增长" if d and d>0 else ("下降" if d and d<0 else "持平")
    def _pct(v): return f"{v:+.1f}%" if v is not None else "-"

    rev, np_v = ly.get("OPERATE_INCOME"), ly.get("HOLDER_PROFIT")
    eps, gm, opm, npm, roe, roce = ly.get("BASIC_EPS"), ly.get("GROSS_MARGIN"), ly.get("OP_MARGIN"), ly.get("NET_PROFIT_RATIO"), ly.get("ROE"), ly.get("ROIC")
    rev_c, np_c = _chg(rev, py.get("OPERATE_INCOME")), _chg(np_v, py.get("HOLDER_PROFIT"))
    per_cf, per_capex, dps = ly.get("PER_NETCASH"), ly.get("CAPEX_PS") or 0, ly.get("DPS") or 0
    pay, pe, med_pe = ly.get("PAYOUT_RATIO"), spot.get("pe",0), spot.get("median_pe")

    business = (
        f"中国民航信息网络（TravelSky）是中国GDS（全球分销系统）垄断运营商，"
        f"处理中国90%+机票预订量，核心业务包括航空信息技术服务（按机票量收费）、"
        f"结算清算、机场IT及数据网络。营收{rev:.0f}亿（{_dir(rev, py.get('OPERATE_INCOME'))}{abs(rev_c):.1f}%），"
        f"利润率{_pct(opm)}，ROE {_pct(roe)}。垄断+政策壁垒确保定价权，受益航空出行量增长。"
    )

    p1 = (f"2026年6月6日 — TravelSky {latest_yr}年营收约{rev:.0f}亿元（{_dir(rev, py.get('OPERATE_INCOME'))}{abs(rev_c):.1f}%），"
          f"扣非净利润约{np_v:.0f}亿元（{_dir(np_v, py.get('HOLDER_PROFIT'))}{abs(np_c):.1f}%）。"
          f"订座处理量随航空出行复苏稳步增长，国际航线恢复为主要增量。"
          f"核心AIT业务按每张机票收费，与民航客运量高度相关，属于「出行基础设施」型收租模式。")

    wc, wc_p = ly.get("WORKING_CAPITAL"), py.get("WORKING_CAPITAL")
    shares, shares_p = ly.get("TOTAL_SHARES"), py.get("TOTAL_SHARES")
    shr_chg = round((shares - shares_p) / shares_p * 100, 1) if shares and shares_p and shares_p > 0 else None
    net_ps = round(per_cf - per_capex - dps, 2) if per_cf else None
    p2_parts = [
        f"每股收益¥{eps:.2f}，高度依赖航空出行量。"
        f"每股现金流¥{per_cf:.2f}（内生现金生成 = 净利润 + 折旧），四大去向：",
        f"① 资本支出¥{per_capex:.2f}/股（IT系统维护+升级）；",
    ]
    if wc is not None and wc_p is not None:
        wc_chg = wc - wc_p
        wc_chg_ps = f"折合¥{abs(wc_chg * 100 / shares):.2f}/股" if shares and shares > 0 else ""
        p2_parts.append(f"② 营运资金{'占用 +' if wc_chg > 0 else '释放 '}{abs(wc_chg):.1f}亿（{wc_chg_ps}）；")
    p2_parts.append(f"③ 现金分红¥{dps:.2f}/股（支付率{pay:.0f}%）；")
    if shr_chg is not None and shr_chg < -0.3:
        p2_parts.append(f"④ 股份回购（股数{shr_chg:+.1f}%）— 增厚每股价值 ✅；")
    elif shr_chg is not None and shr_chg > 0:
        p2_parts.append(f"④ 股数持平/微扩；")
    p2_parts.append(f"净留存¥{net_ps:.2f}/股，低资本支出+高现金流——垄断基础设施属性。")
    p2 = "".join(p2_parts)

    p3 = (f"营业利润率{_pct(opm)}、净利率{_pct(npm)}、ROE {_pct(roe)}。"
          f"护城河极深：①中国民航GDS法定垄断——政策+技术双重壁垒，无竞争对手；"
          f"②网络效应——航司接入越多，平台价值越大；③转换成本极高——航司/机场更换GDS系统不可行。"
          f"风险：航空出行周期性波动、高铁分流短途航线、新兴技术（NDC直连）长期威胁。")

    pb, div_y = spot.get("pb",0), spot.get("div_yield",0) or 0
    p4 = (f"当前PE约{pe:.1f}倍"
          + (f"，低于历史中位数{med_pe:.0f}倍。" if med_pe and pe<med_pe else "。")
          + f"PB约{pb:.1f}倍，股息率约{div_y:.2f}%。"
          + f"TravelSky属于「优质垄断基础设施」——确定性高、增长平稳、分红稳定。"
          + f"适合追求稳健收益+适度成长的投资者，下行有限上行依赖航空出行超预期。")

    rev1 = cagr.get("revenue",{}).get("1yr")
    p5 = (f"关注国际航线恢复进度（当前约疫情前80-90%）及民航客运量增速。"
          + (f"当前营收增速{rev1:+.1f}%，若国际航线全面恢复+国内出行增长加速，业绩弹性可观。" if rev1 else ""))

    return {"business": business, "commentary": [p1, p2, p3, p4, p5]}
