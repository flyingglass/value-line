# -*- coding: utf-8 -*-
"""阿里巴巴 09988 — VL 标准 Business + AI Commentary (5段)"""

def build(stock, metrics, revenue_structure, years, cagr, spot):
    latest_yr = years[-1] if years else "FY2026"
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
        f"阿里巴巴集团是全球领先的电商及科技公司，核心业务：中国商业（淘宝/天猫/1688）、"
        f"国际商业（AliExpress/Lazada/Trendyol）、阿里云（中国第一）、本地生活、菜鸟物流。"
        f"FY{latest_yr}营收{rev:.0f}亿（{_dir(rev, py.get('OPERATE_INCOME'))}{abs(rev_c):.1f}%），"
        f"云业务AI驱动加速增长，国际电商+菜鸟为第二增长曲线。持续大规模股份回购。CEO: 吴泳铭。"
    )

    p1 = (f"2026年6月6日 — 阿里巴巴FY{latest_yr}营收约{rev:.0f}亿元（{_dir(rev, py.get('OPERATE_INCOME'))}{abs(rev_c):.1f}%），"
          f"扣非净利润约{np_v:.0f}亿元（{_dir(np_v, py.get('HOLDER_PROFIT'))}{abs(np_c):.1f}%）。"
          f"核心电商在拼多多/抖音竞争下维持份额，88VIP会员持续高增长。"
          f"阿里云AI相关收入连续多季度三位数增长，云业务从「基础设施」转向「AI平台」，利润率大幅改善。"
          f"国际电商AIDC保持30%+增速，菜鸟全球化物流网络完善。")

    net_ps = round(per_cf - per_capex - dps, 2) if per_cf else None
    p2 = (f"每股收益¥{eps:.2f}，云业务+国际电商贡献增量。"
          f"每股现金流¥{per_cf:.2f}，资本支出¥{per_capex:.2f}（AI算力投资加大），"
          f"现金分红¥{dps:.2f}（支付率{pay:.0f}%），净留存¥{net_ps:.2f}/股。"
          f"净现金超2,000亿，股份回购持续——FY2025约650亿美元等值，每股价值增厚显著。")

    p3 = (f"毛利率{_pct(gm)}、净利率{_pct(npm)}、ROE {_pct(roe)}。"
          f"护城河：①中国电商最大双边网络——10亿消费者+千万商家；"
          f"②阿里云——中国市场份额第一，AI转型领先（通义大模型、AI推理服务）；"
          f"③全球化基础设施——菜鸟+Lazada+AliExpress覆盖全球物流网络。"
          f"风险：电商份额被拼多多/抖音蚕食、云业务竞争（华为/腾讯）、监管、消费疲软。")

    pb, div_y = spot.get("pb",0), spot.get("div_yield",0) or 0
    p4 = (f"当前PE约{pe:.1f}倍"
          + (f"，低于历史中位数{med_pe:.0f}倍。" if med_pe and pe<med_pe else "。")
          + f"PB约{pb:.1f}倍接近净资产，安全边际较高。股息率约{div_y:.2f}%。"
          + f"当前市场给予阿里的是「衰退中的电商」估值，但忽视了云业务AI重估潜力。"
          + f"若阿里云AI收入占比突破20%+国际电商盈利拐点确认，PE存在从15x向20x+重估的空间。")

    eps1 = cagr.get("eps",{}).get("1yr")
    p5 = (f"核心验证：阿里云AI收入增速+国际电商亏损缩窄节奏——这是PE重估的双引擎。"
          + (f"当前EPS增速{eps1:+.1f}%，若AI带动云业务加速增长，业绩弹性可观。" if eps1 else ""))

    return {"business": business, "commentary": [p1, p2, p3, p4, p5]}
