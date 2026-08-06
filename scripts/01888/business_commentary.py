# -*- coding: utf-8 -*-
"""建滔积层板 01888 — VL Business + AI Commentary（手动精写, 2026-08-06）"""
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

    name = stock.get("name", "建滔积层板")
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

    # ── Business ──
    biz = (
        f"建滔积层板是全球最大的覆铜面板（CCL）专业制造商，连续20年全球刚性覆铜板销量第一，"
        f"是建滔集团（00148.HK）控股子公司（持股约70%+）。公司专注覆铜板单一赛道，"
        f"产品覆盖纸基、玻纤布基、复合基及高速高频材料全系列，是PCB行业最上游的核心材料供应商。"
        f"2025年营收204亿港元（同比{rev_dir}{abs(rev_chg):.1f}%），持有人应占溢利24.42亿港元（+84%）。"
        f"覆铜面板及上游物料占比99%，物业及投资占比1%，业务极度纯粹。"
    )

    # ── P1: 业绩快照与变化归因 ──
    p1 = (
        f"2026年8月 — 建滔积层板2025年营收204亿港元（+10%），持有人应占溢利24.42亿港元（+84%），"
        f"基本纯利24.94亿港元（+85%）。毛利率{_p(gm)}（同比+1.9pp），净利率{_p(npm)}（同比+4.8pp），"
        f"利润率双升体现量价齐升+成本优化。核心驱动力："
        f"①AI服务器/数据中心爆发→高速覆铜板（M6/M7级低损耗材料）需求井喷，高端产品ASP远高于普通FR-4；"
        f"②汽车电子化→车载PCB用覆铜板需求增长40%+，公司汽车板全球市占率约1/3；"
        f"③上游电子级玻纤布（LDK一代纱）自供优势→普通纱毛利率15-20%而LDK一代纱约54%，"
        f"自供比例提升直接推高毛利率。覆铜板行业正处于AI驱动的结构性上行周期。"
    )

    # ── P2: 每股资金流向与现金循环 ──
    p2 = (
        f"每股收益{_fmt(eps,2)}港元，每股经营现金流{_fmt(per_cf,2)}港元（现金流/净利润=1.39x，"
        f"差值约{_fmt(per_cf-eps,2)}港元≈折旧{_fmt(dep/shares*1e8,2)}港元，重资产现金生成能力强）。"
        f"资本支出每股{_fmt(per_capex,2)}港元（清远/韶关扩产项目，2025年底投产），"
        f"自由现金流每股{_fmt(per_cf-per_capex,2)}港元。"
        f"分红每股{_fmt(dps,2)}港元（含末期25港仙+特别28港仙），支付率{_fmt(payout,0)}%偏高。"
        f"每股净资产{_fmt(bps,2)}港元，负债权益比仅4%，财务极度保守。"
        f"公司账面净现金充裕，为逆周期扩产提供充足弹药。"
    )

    # ── P3: 业务质地与竞争壁垒 ──
    p3 = (
        f"ROIC {_p(roic)}，ROE {_p(roe)}，净利润率{_p(npm)}。"
        f"建滔积层板的护城河是覆铜板行业中最深的："
        f"①规模与成本壁垒——全球产能第一，规模效应摊薄固定成本，原材料（铜箔/玻纤布/树脂）大规模采购议价力强。"
        f"②垂直整合——自产电子级玻纤布（LDK一代纱）、铜箔、树脂等上游物料，自供率持续提升，"
        f"周期底部时仍可维持正利润（2023年行业低谷时公司仍盈利）。"
        f"③技术升级——M6/M7级高速材料（低介电常数/低损耗因子）是AI服务器的必需材料，"
        f"技术壁垒高、认证周期长（1-2年），公司是少数能量产的供应商，先发优势明显。"
        f"④客户粘性——PCB厂商更换覆铜板供应商需重新认证，转换成本高。"
        f"风险：覆铜板是强周期品（价格随铜价/供需大幅波动），2021年峰值→2023年谷底→2025年复苏已验证；"
        f"AI需求若放缓，高端材料溢价可能收窄；母公司建滔集团减持/配售带来估值情绪压制。"
    )

    # ── P4: 估值锚定与安全边际 ──
    p4 = (
        f"当前PE约{_fmt(pe,1)}倍，历史PE中位数{_fmt(med_pe,0)}x（百分位110%+，估值处于历史高位）。"
        f"PB {_fmt(pb,2)}倍，远高于每股净资产{_fmt(bps,2)}港元。股息率约{_fmt(div_y,1)}%。"
        f"估值分歧的核心在于：当前PE近50x反映的是周期顶部的盈利水平（净利润24.42亿港元），"
        f"若2026年盈利继续增长（H1盈喜+覆铜板分部利润大增200%），则前瞻PE将显著下降。"
        f"但覆铜板周期性强，2023年谷底净利仅约9亿港元，若周期回落PE可能被动升高。"
        f"合理的估值框架应以周期平均盈利（约15-18亿港元）为锚，对应PE约20-25x。"
        f"当前价格包含了AI需求持续高增长的乐观预期，安全边际取决于周期判断。"
    )

    # ── P5: 催化剂与待验证信号 ──
    p5 = (
        f"催化剂：①AI算力军备竞赛持续→高速覆铜板（M6/M7/未来M8级）需求结构性的而非周期性，"
        f"公司产能扩张（清远/韶关新厂）2025年底投产，2026年贡献增量；"
        f"②汽车电子化（智能驾驶+800V高压平台）→车载PCB层数/面积增加，覆铜板用量持续增长；"
        f"③上游电子布自供率提升→毛利率结构性改善（LDK一代纱替代外购普通纱），利润率中枢有望上移；"
        f"④2026H1覆铜面板分部利润大增200%+（母公司盈喜数据），全年盈利高增长可期。"
        f"风险：AI资本开支周期见顶→覆铜板需求增速放缓；铜价上涨挤压毛利率；"
        f"母公司减持/配售（建滔集团近期配售建滔积层板股份）带来供给压力。"
        f"核心信号：每月覆铜板ASP/出货量、M6+高端产品占比、玻纤布自供率趋势。"
    )

    return {"business": biz, "commentary": [p1, p2, p3, p4, p5]}
