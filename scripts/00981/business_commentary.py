# -*- coding: utf-8 -*-
"""中芯国际 00981 — VL 标准 Business + AI Commentary (5段)"""

def build(stock, metrics, revenue_structure, years, cagr, spot):
    latest_yr = years[-1] if years else "2025"
    ly = metrics.get(latest_yr, {})
    py = metrics.get(years[-2], {}) if len(years) >= 2 else {}

    def _chg(c, p): return (c/p-1)*100 if c and p and c>0 and p>0 else None
    def _dir(c,p): d=_chg(c,p); return "增长" if d and d>0 else ("下降" if d and d<0 else "持平")
    def _pct(v): return f"{v:+.1f}%" if v is not None else "-"

    rev, np_v = ly.get("OPERATE_INCOME"), ly.get("HOLDER_PROFIT")
    eps, gm, npm, roe = ly.get("BASIC_EPS"), ly.get("GROSS_MARGIN"), ly.get("NET_PROFIT_RATIO"), ly.get("ROE")
    rev_c, np_c = _chg(rev, py.get("OPERATE_INCOME")), _chg(np_v, py.get("HOLDER_PROFIT"))
    per_cf, per_capex, dps = ly.get("PER_NETCASH"), ly.get("CAPEX_PS") or 0, ly.get("DPS") or 0
    bps = ly.get("BPS")
    shares = ly.get("TOTAL_SHARES")

    # ── Business 描述 ──
    business = (
        f"中芯国际是中国大陆规模最大、技术最先进的晶圆代工企业，"
        f"提供0.35μm至FinFET全工艺节点的集成电路制造服务。"
        f"核心产品包括逻辑、射频、CIS、PMIC、BCD、NOR Flash等工艺平台。"
        f"全球晶圆代工排名第五、中国大陆第一，12英寸晶圆产能持续扩张。"
        f"CEO: 刘训峰。A+H双上市（港股00981 / 科创板688981）。"
    )

    # ── 段1: 年度业绩概述 ──
    p1 = (f"2026年6月8日 — 中芯国际{latest_yr}年营收约{rev:.0f}亿元"
          + (f"（{_dir(rev, py.get('OPERATE_INCOME'))}{abs(rev_c):.1f}%）" if rev_c else "")
          + f"，归母净利润约{np_v:.0f}亿元"
          + (f"（{_dir(np_v, py.get('HOLDER_PROFIT'))}{abs(np_c):.1f}%）" if np_c else "")
          + f"。"
          + f"晶圆出货量创新高，12英寸晶圆占比持续提升。"
          + f"FinFET/28nm先进制程收入占比持续扩大，40/55nm仍为最大营收来源。"
          + f"受益于中国半导体自主可控政策，稼动率回升至90%+。"
          + (f"利润增速{abs(np_c):.0f}%超营收{abs(rev_c):.0f}%，规模效应+稼动率提升驱动利润率改善。" if np_c and rev_c and np_c > rev_c*1.3 else ""))

    # ── 段2: 每股资金流向 ──
    tax_rate = (ly.get("TAX_EBT", 12) or 12) / 100
    op_eps = round(ly.get("PER_OI", 0) * (ly.get("OP_MARGIN", 0) / 100) * (1 - tax_rate), 2) if ly.get("PER_OI") and ly.get("OP_MARGIN") else None
    nonop_eps = round(eps - op_eps, 2) if eps and op_eps else None
    op_pct = round(op_eps / eps * 100) if eps and op_eps and eps != 0 else 0
    net_ps = round(per_cf - per_capex - dps, 2) if per_cf else None

    if eps and per_cf:
        p2_parts = [
            f"每股收益¥{eps:.2f}中，主业经营贡献¥{op_eps:.2f}（{op_pct}%），"
            f"非经营性贡献¥{nonop_eps:.2f}（{100-op_pct}%）。"
            if op_eps else "",
            f"每股现金流¥{per_cf:.2f}，三大流向：",
            f"① 资本支出¥{per_capex:.2f}/股（晶圆厂建设，年支出超300亿元）——重资产行业必然；",
        ]
        p2_parts.append(f"② 现金分红¥{dps:.2f}/股（支付率{ly.get('PAYOUT_RATIO', 0):.0f}%）；")
        p2_parts.append(
            f"③ 净留存¥{net_ps:.2f}/股。"
            f"自由现金流(CF-CapEx)长期为负是半导体制造常态，"
            f"但每股净资产¥{bps:.2f}为真实价值锚点。"
            if bps else ""
        )
        p2 = "".join(p2_parts)
    else:
        p2 = "每股资金流向：数据待补充。"

    # ── 段3: 竞争壁垒 ──
    p3 = (f"毛利率{_pct(gm)}、净利率{_pct(npm)}、ROE {_pct(roe)}。"
          f"竞争壁垒："
          f"① 政策护城河——中国大陆最大晶圆代工企业，国家半导体自主可控战略核心载体，"
          f"享有设备采购优先权和政策补贴；"
          f"② 技术平台广——从0.35μm成熟制程到14nm FinFET全覆盖，"
          f"BCD、CIS、PMIC等特色工艺国内领先；"
          f"③ 客户粘性——服务全球600+客户，芯片设计→流片→量产周期长，转换成本高。"
          f"风险：美国设备禁令（无法获取EUV/先进DUV）、中美科技脱钩、"
          f"成熟制程竞争加剧（华虹/台积电南京/联电）、行业周期性波动。")

    # ── 段4: 估值分析 ──
    pe, pb = spot.get("pe", 0) or 0, spot.get("pb", 0) or 0
    median_pe = spot.get("median_pe")
    div_y = spot.get("div_yield", 0) or 0
    eps_1yr = cagr.get("eps", {}).get("1yr")

    p4 = (f"当前PE约{pe:.1f}倍"
          + (f"（周期高位），PB约{pb:.1f}倍处于历史高位（3年91%分位）。" if pb > 3 else f"。PB约{pb:.1f}倍。")
          + f"ROE仅{_pct(roe)}，理论上PB应接近1x，当前高溢价来自半导体自主可控主题和A股联动效应。"
          + f"PB=1x为保守估值目标（对标全球成熟制程代工厂UMC），对应目标价约¥{bps:.1f}（每股净资产）。"
          + f"关注稼动率、28nm产能爬坡及政策支持力度——估值催化剂。")

    # ── 段5: 未来展望 ──
    p5 = (f"核心跟踪指标：① 28nm及以上先进制程收入占比（当前~17%，目标25%+）；"
          f"② 12英寸晶圆月产能（当前约18万片，北京/上海/深圳/天津四地扩建中）；"
          f"③ 稼动率（当前90%+，持续改善则利润率提升）。"
          f"半导体周期处于AI驱动上行阶段，中国自主可控需求确定性强。"
          + (f"EPS增速{eps_1yr:+.1f}%，若先进制程放量+稼动率维持高位，业绩弹性可观。" if eps_1yr else "")
          + f"PB=1x为绝对价值底部，随着ROE改善和产能释放，PB存在重估空间。")

    return {"business": business, "commentary": [p1, p2, p3, p4, p5]}
