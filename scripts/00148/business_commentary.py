# -*- coding: utf-8 -*-
"""建滔集团 00148 — VL Business + AI Commentary（手动精写, 2026-08-06）"""
def build(stock, metrics, revenue_structure, years, cagr, spot):
    ly = metrics.get(years[-1], {}) if years else {}
    py = metrics.get(years[-2], {}) if len(years) >= 2 else {}
    def _chg(c, p):
        try:
            c2, p2 = float(c), float(p)
            if not c2 or not p2: return None
            if p2 > 0: return (c2 / p2 - 1) * 100
            if c2 < 0 and p2 < 0: return (c2 - p2) / abs(p2) * 100
            return (c2 / p2 - 1) * 100
        except: return None
    def _num(v):
        try: return float(v)
        except: return 0
    def _fmt(v, d=0):
        try: return f"{float(v):,.{d}f}"
        except: return "-"
    def _p(v):
        try: return f"{float(v):+.1f}%"
        except: return "-"

    name = stock.get("name", "建滔集团")
    rev = _num(ly.get("OPERATE_INCOME"))
    np_val = _num(ly.get("HOLDER_PROFIT"))
    eps = _num(ly.get("BASIC_EPS"))
    gm = _num(ly.get("GROSS_MARGIN"))
    npm = _num(ly.get("NET_PROFIT_RATIO"))
    roe = _num(ly.get("ROE"))
    roic = _num(ly.get("ROIC"))
    bps = _num(ly.get("BPS"))
    per_cf = _num(ly.get("PER_NETCASH"))
    per_capex = _num(ly.get("CAPEX_PS") or 0)
    dps = _num(ly.get("DPS") or 0)
    payout = _num(ly.get("PAYOUT_RATIO") or 0)
    dep = _num(ly.get("DEPRECIATION"))
    lt_debt = _num(ly.get("LT_DEBT"))
    total_eq = _num(ly.get("TOTAL_EQUITY"))
    shares = _num(ly.get("TOTAL_SHARES"))
    price = _num(spot.get("price", 0))
    pe = _num(spot.get("pe", 0)) or (round(price / eps, 1) if price and eps else 0)
    pb = _num(spot.get("pb", 0)) or (round(price / bps, 2) if price and bps else 0)
    div_y = _num(spot.get("div_yield", 0)) or (round(dps / price * 100, 1) if price and dps else 0)
    med_pe = spot.get("median_pe")

    rev_chg = _chg(rev, py.get("OPERATE_INCOME"))
    np_chg = _chg(np_val, py.get("HOLDER_PROFIT"))
    rev_dir = "增长" if (rev_chg or 0) > 0 else "下降"
    np_dir = "增长" if (np_chg or 0) > 0 else "下降"

    prod_data = revenue_structure.get("by_product", []) if isinstance(revenue_structure, dict) else []

    # ── Business ──
    biz = (
        f"建滔集团是全球覆铜面板行业绝对龙头，旗下建滔积层板（01888.HK）连续20年全球刚性覆铜板产销量第一。"
        f"集团构建了从上游铜箔/玻纤布/树脂→中游覆铜板→下游PCB的垂直一体化产业链，覆盖电子材料全价值环节。"
        f"2025年营收{_fmt(rev/1e8,0)}亿港元（同比{rev_dir}{abs(rev_chg):.1f}%），"
        f"持有人应占溢利{_fmt(np_val/1e8,0)}亿港元（同比{np_dir}{abs(np_chg):.1f}%）。"
        f"业务结构：覆铜面板37%、PCB 29%、化工产品28%、物业3%。"
    )

    # ── P1: 业绩快照与变化归因 ──
    p1 = (
        f"2026年8月 — 建滔集团2025年营收453.75亿港元（+5.3%），持有人应占溢利44.02亿港元（+170%）。"
        f"核心驱动力：①覆铜面板分部量价齐升，受益于AI服务器、数据中心对高端覆铜板（M6/M7级高速材料）需求爆发，"
        f"分部营收增长10%至207亿港元；②化工产品分部（铜箔/玻纤/树脂）作为上游物料同步受益，营收增长至135亿港元；"
        f"③房地产分部营收大降62%，但占比仅3%，拖累有限。基本纯利（剔除一次性项目）49.85亿港元（+207%），"
        f"反映核心主业盈利能力大幅修复。毛利率{_p(gm)}，净利率{_p(npm)}，净利润率修复至9.7%（2024年仅3.8%）。"
    )

    # ── P2: 每股资金流向与现金循环 ──
    p2 = (
        f"每股收益{_fmt(eps,2)}港元，每股经营现金流{_fmt(per_cf,2)}港元（现金流/净利润=1.08x，"
        f"差值约{_fmt(per_cf-eps,2)}港元≈折旧{_fmt(dep/shares*1e8,2)}港元，典型重资产特征）。"
        f"资本支出每股{_fmt(per_capex,2)}港元（维持性+扩产），自由现金流每股{_fmt(per_cf-per_capex,2)}港元。"
        f"分红每股{_fmt(dps,2)}港元（支付率{_fmt(payout,0)}%），分红慷慨但支付率偏高。"
        f"每股净资产{_fmt(bps,2)}港元，10年CAGR约+5.4%，内生价值稳步增长。"
        f"负债权益比15%，长期债务96.6亿港元，财务稳健。"
    )

    # ── P3: 业务质地与竞争壁垒 ──
    p3 = (
        f"ROIC {_p(roic)}，ROE {_p(roe)}，净利润率{_p(npm)}。建滔集团的护城河来自三层结构："
        f"①垂直一体化壁垒——从铜箔、玻纤布、树脂到覆铜板再到PCB，全链条自供，成本优势+供应安全双重护城河。"
        f"上游物料（电子级玻纤布/铜箔）自供率极高，周期底部时亏损分部少、抗风险能力强。"
        f"②规模与客户粘性——连续20年全球覆铜板销量第一，客户覆盖全球主要PCB厂商，转换成本高。"
        f"③高端化升级——AI服务器用高速覆铜板（M6/M7级）技术门槛高，公司是少数能量产的供应商之一。"
        f"风险：覆铜板行业周期性明显（2023-2024年低谷验证），铜价/树脂等原材料波动大；"
        f"房地产资产（账面约122亿待开发物业+260亿投资物业）流动性差，减值风险尚未完全释放；"
        f"大股东Hallgain Management近年减持带来估值压制。"
    )

    # ── P4: 估值锚定与安全边际 ──
    p4 = (
        f"当前PE约{_fmt(pe,1)}倍，历史PE中位数{_fmt(med_pe,0)}x（百分位110%，显著高于历史中枢）。"
        f"PB {_fmt(pb,2)}倍，低于每股净资产{_fmt(bps,2)}港元（破净），资产端提供一定安全边际。"
        f"股息率约{_fmt(div_y,1)}%。按PB估值框架：历史PB均值约0.46x，当前0.78x处于历史偏高区间。"
        f"资产净值（NAV）约647亿港元，市值489亿港元，折价24%。但NAV中含大量低流动性房地产资产，"
        f"实际可变现价值需打折扣。核心看点是：若覆铜板/PCB主业利润持续修复，"
        f"PB估值有望从0.5-0.8x向1.0x修复；反之若周期下行，PB可能回落至0.3-0.5x区间。"
    )

    # ── P5: 催化剂与待验证信号 ──
    p5 = (
        f"催化剂：①AI算力持续扩张→高端覆铜板（M6/M7级高速材料）需求结构性增长，公司产能爬坡直接受益；"
        f"②2026H1盈喜：预计纯利超27亿港元（+4%），覆铜面板分部利润大增200%+，周期上行趋势确认中；"
        f"③建滔积层板（01888）配售+大股东减持压力释放后，估值压制因素边际减弱；"
        f"④若房地产资产加速处置/变现，可释放隐藏价值并改善市场对公司治理的担忧。"
        f"风险：覆铜板周期下行（2026H2若AI需求不及预期）；大股东持续减持；房地产减值。"
        f"关注信号：每半年覆铜板ASP趋势、高端产品（M6+）占比、房地产处置进展。"
    )

    return {"business": biz, "commentary": [p1, p2, p3, p4, p5]}
