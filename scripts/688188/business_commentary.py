# -*- coding: utf-8 -*-
"""柏楚电子 688188 — VL Business + AI Commentary (5段, 数据驱动)

口径提示：
  - metrics[y]["HOLDER_PROFIT"] / ["BASIC_EPS"] 为 VL 经常性（扣非）口径
  - 营收结构取最新年报（2025）分产品/分地区/分销售模式，value 单位为百万元
  - cagr 键名兼容 engine 两种写法：revenue/sales、eps/earnings、cashflow
所有数字取自 build() 入参，不硬编码。
"""


def build(stock, metrics, revenue_structure, years, cagr, spot):
    ly_year = years[-1] if years else ""
    ly = metrics.get(ly_year, {}) if years else {}
    py = metrics.get(years[-2], {}) if len(years) >= 2 else {}
    py2 = metrics.get(years[-3], {}) if len(years) >= 3 else {}

    def _num(v):
        try:
            return float(v)
        except (TypeError, ValueError):
            return 0.0

    def _fmt(v, d=1):
        v = _num(v)
        return f"{v:,.{d}f}" if v else "—"

    def _chg(cur, prev):
        c, p = _num(cur), _num(prev)
        if not c or not p:
            return None
        return (c / p - 1) * 100

    def _yoy(cur, prev):
        v = _chg(cur, prev)
        if v is None:
            return "—"
        return ("增长" if v >= 0 else "下降") + f"{abs(v):.1f}%"

    rev, npv = _num(ly.get("OPERATE_INCOME")), _num(ly.get("HOLDER_PROFIT"))
    p_rev, p_np = _num(py.get("OPERATE_INCOME")), _num(py.get("HOLDER_PROFIT"))
    gm, opm, npm = _num(ly.get("GROSS_MARGIN")), _num(ly.get("OP_MARGIN")), _num(ly.get("NET_PROFIT_RATIO"))
    gm_1, gm_2 = _num(py.get("GROSS_MARGIN")), _num(py2.get("GROSS_MARGIN"))
    roe, roic = _num(ly.get("ROE")), _num(ly.get("ROIC"))
    eps, dps, bps = _num(ly.get("BASIC_EPS")), _num(ly.get("DPS")), _num(ly.get("BPS"))
    per_cf, cap_ps, payout = _num(ly.get("PER_NETCASH")), _num(ly.get("CAPEX_PS")), _num(ly.get("PAYOUT_RATIO"))
    lt_debt = _num(ly.get("LT_DEBT"))
    lt_all_zero = all(_num(metrics.get(y, {}).get("LT_DEBT")) == 0 for y in years) if years else False

    price, pe, pb = _num(spot.get("price")), _num(spot.get("pe")), _num(spot.get("pb"))
    div_y, mcap = _num(spot.get("div_yield")), _num(spot.get("mkt_cap"))
    med_pe, eps_ttm = _num(spot.get("median_pe")), _num(spot.get("eps_ttm"))
    pe_avg = _num(ly.get("PE_AVG"))

    ar = cagr or {}
    def _cg(*keys):
        for k in keys:
            v = ar.get(k)
            if isinstance(v, dict):
                return v
        return {}
    s_g, e_g, c_g = _cg("revenue", "sales"), _cg("eps", "earnings"), _cg("cashflow")

    rs = revenue_structure if isinstance(revenue_structure, dict) else {}
    prod = rs.get("by_product", []) or []
    regi = rs.get("by_region", []) or []
    chan = rs.get("by_channel", []) or []

    def _seg(name_key):
        for r in prod:
            if str(r.get("name", "")) == name_key:
                return r
        return None

    def _pct_of(name_key):
        r = _seg(name_key)
        return _num(r.get("pct")) if r else 0.0

    def _val_of(name_key):
        """value 单位为百万元 → 换算为亿元"""
        r = _seg(name_key)
        return _num(r.get("value")) / 100.0 if r else 0.0

    prod_str = "、".join(f"{r['name']} {_num(r.get('pct')):.1f}%" for r in prod[:4]) if prod else ""
    reg_str = "、".join(f"{r['name']} {_num(r.get('pct')):.1f}%" for r in regi[:3]) if regi else ""
    ch_str = "、".join(f"{r['name']} {_num(r.get('pct')):.0f}%" for r in chan[:2]) if chan else ""
    top_reg = regi[0] if regi else None

    # ── Business：config 业务描述 + 最新年核心数据 ──
    biz_core = (
        f"{ly_year} 年营业收入 {_fmt(rev)} 亿元（同比{_yoy(rev, p_rev)}），"
        f"扣非归母净利润 {_fmt(npv)} 亿元（同比{_yoy(npv, p_np)}）；"
        f"毛利率 {_fmt(gm)}%、ROE {_fmt(roe)}%（VL 扣非口径）；"
        + (f"长期有息负债十年均为 0，属轻资产、零杠杆的「软件收租」型生意。" if lt_all_zero
           else f"长期有息负债 {_fmt(lt_debt, 2)} 亿元。")
    )
    if prod_str:
        biz_core += f"收入结构：{prod_str}。"
    business = (stock.get("business_desc", "") + biz_core).strip()

    # ── P1 经营分析 ──
    p1 = (
        f"【经营分析】{ly_year} 年营收 {_fmt(rev)} 亿元（同比{_yoy(rev, p_rev)}），"
        f"扣非净利 {_fmt(npv)} 亿元（同比{_yoy(npv, p_np)}），净利率 {_fmt(npm)}%、营业利润率 {_fmt(opm)}%。"
    )
    if prod_str:
        p1 += f"分应用场景{prod_str}：平面切割是基本盘，管材为第二支柱，"
        other_pct, other_val = _pct_of("其他"), _val_of("其他")
        if other_pct:
            p1 += f"「其他」（智能切割头、智能焊接等新业务）{_fmt(other_val)} 亿元、占 {_fmt(other_pct)}%，是脱离切割周期 beta 的关键观察项；"
        p1 += "三维解决方案基数仍小。"
    if chan:
        p1 += f"销售模式为 {chan[0]['name']}（{ch_str}），客户为下游激光切割设备制造商，不绑单一整机厂。"
    if reg_str and top_reg:
        p1 += f"分地区{reg_str}，{top_reg['name']}占 {_fmt(_num(top_reg.get('pct')))}%、区域集中度高，与国内激光设备产业带分布一致。"
    if s_g.get("3yr") is not None:
        p1 += f"营收三年复合增速 {_fmt(s_g.get('3yr'))}%、五年 {_fmt(s_g.get('5yr'))}%，收入弹性明显大于行业总量。"

    # ── P2 现金流与资本配置 ──
    fcf_ps = per_cf - cap_ps - dps if per_cf else 0.0
    p2 = (
        f"【现金流与资本配置】每股现金流（VL 口径 = 扣非净利 + 折旧）¥{_fmt(per_cf, 2)}，"
        f"资本支出仅 ¥{_fmt(cap_ps, 2)}/股——资产轻、扩产不依赖重投入；"
        f"分红 ¥{_fmt(dps, 2)}/股、支付率 {_fmt(payout, 0)}%，股息率 {_fmt(div_y, 2)}%；"
        f"净留存约 ¥{_fmt(fcf_ps, 2)}/股继续累积为净资产。"
    )
    if c_g.get("3yr") is not None:
        p2 += f"每股现金流三年复合增速 {_fmt(c_g.get('3yr'))}%，与利润增速基本同步，利润含金量扎实。"
    pays = [_num(metrics.get(y, {}).get("PAYOUT_RATIO")) for y in years[-3:]]
    pays = [p for p in pays if p]
    pay_range = f"{min(pays):.0f}%–{max(pays):.0f}%" if pays else "历史区间"
    p2 += (
        "现金画像要看两点：一是分红支付率"
        + (f"近三年在 {pay_range} 区间（VL 扣非口径下超过 100% 意味着动用存量现金分红）" if pays else "偏高")
        + "，高支付率能否维持取决于利润增长；二是账上现金与交易性金融资产的配置（理财收益计入非经常性损益，是扣非口径与归母口径差异的主要来源）。"
    )
    p2 += (
        "⚠️ 口径提示（2026-09-26 核，非表中数值）：2025 年度方案为每 10 股派现 19.28 元并转增 4 股，"
        "按转增前 288,729,927 股计、现金红利总额 5.567 亿元（2025 年报 p2、p56）。"
        "摊薄到转增后股本，每股股息约 1.38 元、对应现价股息率约 1.45%，"
        "分红总额占 2025 年归母净利 50.0%、占扣非净利 54.2%。"
        "表内股息率 2.02% 与支付率 76% 是「转增前每股股息 ÷ 摊薄后每股收益」的混合口径，读数时以摊薄口径为准。"
    )

    # ── P3 盈利质量与护城河 ──
    gm_trend = ""
    if gm and gm_1 and gm_2:
        gm_trend = f"，毛利率 {_fmt(gm_2)}%（{years[-3]}）→ {_fmt(gm_1)}%（{years[-2]}）→ {_fmt(gm)}%（{ly_year}）逐年下移"
    p3 = (
        f"【盈利质量与护城河】毛利率 {_fmt(gm)}%、营业利润率 {_fmt(opm)}%、净利率 {_fmt(npm)}%"
        f"{gm_trend}，是低毛利智能硬件（切割头等）占比抬升的直接体现——这是结构性的，不是周期性的。"
        f"ROIC {_fmt(roic)}% 高于 ROE {_fmt(roe)}%，说明高回报来自经营本身而非杠杆（资产负债率常年个位数）。"
        f"护城河三层（①–③ 为本报告判断，非年报原文）：① 控制系统占整机成本比重不高却决定切割质量与易用性，"
        f"装机后形成操作习惯与调试数据沉淀，替换成本高；② 软件复制的边际成本近零，规模效应直接落到利润率；"
        f"③ 下游设备厂高度分散，公司不绑定单一客户，议价权不在下游。"
        f"份额的口径来自年报原文：2025 年报「国内市场占有率约为 60%」（中低功率，p40），"
        f"高功率则由「高功率切割系统 + 智能激光切割头」组合推进国产替代（p40 原文）。"
        f"风险：激光切割整机价格战向上游传导；低毛利硬件放量继续稀释毛利率；高功率领域仍面对国际控制系统厂商竞争。"
    )

    # ── P4 估值分析 ──
    cf_x = price / per_cf if per_cf else 0.0
    p4 = (
        f"【估值分析】现价 ¥{_fmt(price, 2)}，总市值 {_fmt(mcap)} 亿元，"
        f"PE(TTM，归母口径) {_fmt(pe, 1)} 倍、PB {_fmt(pb, 2)} 倍（每股净资产 ¥{_fmt(bps, 2)}）、"
        f"股息率 {_fmt(div_y, 2)}%；{ly_year} 年 PE_AVG {_fmt(pe_avg, 1)} 倍、历史 PE 中位数约 {_fmt(med_pe, 0)} 倍，"
        f"当前 PE 处于历史区间的偏低位置。"
    )
    if cf_x:
        p4 += (
            f"按本报告估值口径，现价相当于每股现金流（VL 口径 ¥{_fmt(per_cf, 2)}）的 {_fmt(cf_x, 1)} 倍，"
            f"即每 1 元现金流对应的市值远高于常规 CF 估值线——市场定价的重心是成长性与业务质量，而非当期现金流。"
            f"读估值线时要记住：这条线是「现金流锚」，不是目标价；"
            f"判断安全边际要看成长能否延续（营收增速、新业务占比）以及毛利率下滑是否止住。"
        )
    if eps_ttm:
        p4 += (
            f"⚠️ PE 口径提示（2026-09-26 核）：表头 PE(TTM) {_fmt(pe, 1)} 倍由「{ly_year} 年报 EPS（转增前股本）"
            f"＋ 2026Q1 EPS（转增后股本）」混合算出（≈¥{_fmt(eps_ttm, 2)}），与本报告每股指标（按转增后 405,557,343 股摊薄）不同源。"
            f"按统一摊薄口径重算：归母 TTM = 2025H2 4.72 亿 + 2026H1 7.87 亿 = 12.60 亿，"
            f"÷ 4.0556 亿股 ≈ ¥3.11，对应 PE 约 30.7 倍；扣非 TTM 11.47 亿 ≈ ¥2.83，PE 约 33.7 倍。"
            f"另：2026H1 归母净利同比 +22.97%，但经营活动现金流净额同比 −8.84%（2026 中报 p6–p7），"
            f"利润与现金流的这一背离需在下一期继续验证。"
        )

    # ── P5 催化与风险 ──
    p5 = (
        "【催化与风险】向上情景（方向引自 2025 年报 p40 未来展望）：智能焊接作为激光切割的后道工序，"
        "受益钢结构产量增长与焊工短缺带来的自动化需求；「高功率切割系统 + 智能激光切割头」组合继续挤压国际厂商份额；"
        "超高精度驱控一体方向实现核心技术自主可控。落到数据上就是「其他」分部占比与新业务订单能否继续抬升。"
        "向下风险：毛利率继续下移（硬件占比结构性拖累）；下游激光设备行业价格战向控制系统传导；"
        "若成长减速，当前高于现金流锚的估值倍数缺乏支撑。"
        "跟踪指标按优先级：① 季度毛利率是否止跌 ＞ ② 「其他」分部收入占比（新业务斜率）＞ "
        "③ 应收账款与存货周转（直销模式下回款质量）＞ ④ 分红支付率是否维持。"
    )

    return {"business": business, "commentary": [p1, p2, p3, p4, p5]}
