# -*- coding: utf-8 -*-
"""分众传媒 002027 — VL 标准 Business + AI Commentary (5段)"""

def build(stock, metrics, revenue_structure, years, cagr, spot):
    latest_yr = years[-1] if years else "2025"
    ly = metrics.get(latest_yr, {})
    py = metrics.get(years[-2], {}) if len(years) >= 2 else {}

    def _chg(c, p): return (c/p-1)*100 if c and p and p>0 else None
    def _dir(c,p): d=_chg(c,p); return "增长" if d and d>0 else ("下降" if d and d<0 else "持平")
    def _pct(v): return f"{v:+.1f}%" if v is not None else "-"

    rev, np_v = ly.get("OPERATE_INCOME"), ly.get("HOLDER_PROFIT")
    eps, gm, npm, roe, roce = ly.get("BASIC_EPS"), ly.get("GROSS_MARGIN"), ly.get("NET_PROFIT_RATIO"), ly.get("ROE"), ly.get("ROIC")
    rev_c, np_c = _chg(rev, py.get("OPERATE_INCOME")), _chg(np_v, py.get("HOLDER_PROFIT"))
    per_cf, per_capex, dps = ly.get("PER_NETCASH"), ly.get("CAPEX_PS") or 0, ly.get("DPS") or 0
    pay, pe, med_pe = ly.get("PAYOUT_RATIO"), spot.get("pe",0), spot.get("median_pe")

    business = (
        f"分众传媒是中国最大的生活圈媒体平台，核心业务为电梯电视和电梯海报广告，"
        f"覆盖全国约300个城市超280万电梯点位，触达4亿城市主流消费人群。"
        f"营收{rev:.0f}亿（{_dir(rev, py.get('OPERATE_INCOME'))}{abs(rev_c):.1f}%），"
        f"净利率{_pct(npm)}，ROE {_pct(roe)}。AI赋能广告投放降本增效，高分红现金牛。"
    )

    p1 = (f"2026年6月6日 — 分众传媒{latest_yr}年营收约{rev:.0f}亿元（{_dir(rev, py.get('OPERATE_INCOME'))}{abs(rev_c):.1f}%），"
          f"VL经常性净利润约{np_v:.0f}亿元（{_dir(np_v, py.get('HOLDER_PROFIT'))}{abs(np_c):.1f}%）。"
          + (f"（报表归母29.5亿，加回数禾科技一次性减值21.5亿+权益法亏损3.8亿后，"
             f"主业经常性利润≈52.4亿，数禾已于2026年1月清仓。）" if latest_yr == "2025" else "")
          + f"消费品牌客户占比持续提升，互联网客户投放趋于稳定。"
          f"AI赋能——AI创作广告素材、智能排播系统提升运营效率。"
          f"成本端点位租金趋于稳定，毛利率维持高位。")

    net_ps = round(per_cf - per_capex - dps, 2) if per_cf else None
    p2 = (f"每股收益¥{eps:.2f}，收入随广告投放周期波动。"
          f"每股现金流¥{per_cf:.2f}，资本支出¥{per_capex:.2f}（点位维护），"
          f"现金分红¥{dps:.2f}（支付率{pay:.0f}%），净留存¥{net_ps:.2f}/股。"
          f"高分红+高现金流特征——典型现金牛标的，股东回报优先。")

    p3 = (f"毛利率{_pct(gm)}、净利率{_pct(npm)}、ROE {_pct(roe)}。"
          f"护城河：①点位垄断——280万+电梯点位覆盖核心城市，后来者难以复制规模；"
          f"②品牌广告的不可替代——电梯场景具有强制观看属性，互联网广告无法替代；"
          f"③客户粘性——消费品牌长期投放关系，切换成本高。"
          f"风险：宏观经济下行广告预算收缩、梯媒竞争（新潮传媒）、数字化转型节奏。")

    pb, div_y = spot.get("pb",0), spot.get("div_yield",0) or 0
    p4 = (f"当前PE约{pe:.1f}倍"
          + (f"，低于历史中位数{med_pe:.0f}倍。" if med_pe and pe<med_pe else "。")
          + f"PB约{pb:.1f}倍，股息率约{div_y:.2f}%。支付率{pay:.0f}%处高位——"
          + f"市场给予的是「增长停滞的广告渠道」估值，但忽视了消费复苏带来的弹性。"
          + f"若消费品牌广告投放恢复+AI降本增效兑现，PE有修复空间。")

    rev1 = cagr.get("revenue",{}).get("1yr")
    p5 = (f"关注消费品客户广告投放周期及季度环比改善节奏。"
          + (f"当前营收增速{rev1:+.1f}%，核心驱动力是消费品牌客户占比提升+AI降本效果。" if rev1 else ""))

    return {"business": business, "commentary": [p1, p2, p3, p4, p5]}
