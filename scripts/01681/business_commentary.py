# -*- coding: utf-8 -*-
"""康臣药业 01681 — VL Business + AI Commentary（数据驱动）"""

def build(stock, metrics, revenue_structure, years, cagr, spot):
    latest_yr = years[-1] if years else "2025"
    ly = metrics.get(latest_yr, {})
    prev_yr = years[-2] if len(years) >= 2 else None
    py = metrics.get(prev_yr, {}) if prev_yr else {}

    def _chg(cur, prev):
        return (cur / prev - 1) * 100 if cur and prev and prev > 0 else None
    def _dir(cur, prev):
        c = _chg(cur, prev)
        return "增长" if (c or 0) > 0 else "下降"
    def _fmt(v, d=0): return f"{v:,.{d}f}" if v is not None else "-"
    def _fmt_pct(v): return f"{v:+.1f}%" if v is not None else "-"

    rev = ly.get("OPERATE_INCOME")
    np_val = ly.get("HOLDER_PROFIT")
    eps = ly.get("BASIC_EPS")
    gm = ly.get("GROSS_MARGIN")
    npm = ly.get("NET_PROFIT_RATIO")
    roe = ly.get("ROE")
    roic = ly.get("ROIC")
    rev_chg = _chg(rev, py.get("OPERATE_INCOME"))
    np_chg = _chg(np_val, py.get("HOLDER_PROFIT"))
    per_cf = ly.get("PER_NETCASH")
    per_capex = ly.get("CAPEX_PS") or 0
    dps = ly.get("DPS") or 0
    payout = ly.get("PAYOUT_RATIO")

    # ---- Revenue breakdown ----
    rev_parts = []
    if isinstance(revenue_structure, dict) and revenue_structure:
        for dim_key, items in revenue_structure.items():
            if items:
                rev_parts.extend([f"{r.get('name','')}{r.get('pct',''):.0f}%" for r in items[:3]])

    # ---- Business ----
    business = (
        f"康臣药业是现代化中成药及医用成像对比剂企业，1997年创立，2013年港交所上市。"
        f"核心产品尿毒清颗粒为肾病口服中成药龙头（市占率第一），"
        f"旗下玉林制药（正骨水、湿毒清）为中华老字号品牌。"
        f"FY{latest_yr}营收{_fmt(rev,0)}亿（{_dir(rev, py.get('OPERATE_INCOME'))}{abs(rev_chg):.1f}%），"
        f"归母净利{_fmt(np_val,0)}亿，净利率{_fmt_pct(npm)}，ROE {_fmt_pct(roe)}。"
        + (f"营收结构：{'/'.join(rev_parts)}。" if rev_parts else "")
    )

    # ---- Commentary 1: 业绩概览 ----
    p1 = (
        f"2026年7月 — 康臣药业{latest_yr}年营收{_fmt(rev,0)}亿"
        + (f"（{_dir(rev, py.get('OPERATE_INCOME'))}{abs(rev_chg):.1f}%）" if rev_chg else "")
        + f"，归母净利润{_fmt(np_val,0)}亿"
        + (f"（{_dir(np_val, py.get('HOLDER_PROFIT'))}{abs(np_chg):.1f}%）" if np_chg else "")
        + f"。肾科药物（尿毒清颗粒为主）收入24.02亿（+20.3%），为绝对主力。"
        + f"毛利率{_fmt_pct(gm)}、净利率{_fmt_pct(npm)}，"
        + "核心品种尿毒清颗粒在慢性肾病中成药市场地位稳固，集采扩面后持续放量。"
        + "中国CKD 3-4期存量患者超2000万，当前尿毒清市场渗透率仅约2%，长期增长空间巨大。"
    )

    # ---- Commentary 2: 每股资金流向 ----
    net_ps = round(per_cf - per_capex - dps, 2) if per_cf else None
    if eps and per_cf:
        p2 = (
            f"每股收益¥{_fmt(eps,2)}，每股经营现金流¥{_fmt(per_cf,2)}（现金流充沛，远超EPS），"
            f"资本支出每股¥{_fmt(per_capex,2)}（轻资产模式，无需大量资本投入），"
            f"分红每股约¥{_fmt(dps,2)}（支付率{_fmt(payout,0)}%），净留存约¥{_fmt(net_ps,2)}/股。"
            "公司是典型的高分红医药股：上市以来累计派息约30亿港元，"
            "FY2025末期息0.40港元+中期息0.33港元，持续回报股东。"
            "资产负债率仅24.5%，几乎无有息负债，财务极度稳健。"
        )
    else:
        p2 = "每股资金流向：数据待补充。"

    # ---- Commentary 3: 竞争壁垒 ----
    p3 = (
        f"毛利率{_fmt_pct(gm)}、净利率{_fmt_pct(npm)}、ROE {_fmt_pct(roe)}"
        + (f"、ROIC {_fmt_pct(roic)}。" if roic else "。")
        + "竞争壁垒："
        "①品种壁垒——尿毒清颗粒为独家品种（中药保护），循证证据充分（多项RCT研究），"
        "疗效确切+品牌认知深厚，竞品替代难度极高；"
        "②渠道壁垒——覆盖5万+终端医疗机构和30万+零售药店，渠道深度远超同行；"
        "③玉林制药中华老字号品牌——正骨水、湿毒清等OTC品种品牌忠诚度高，"
        "构建第二增长曲线（FY2025收入4.73亿，+6.8%）；"
        "④高现金流+高分红模式——轻资产、高毛利、低资本开支，自由现金流充裕，"
        "具备持续高分红和并购能力。"
        "风险：尿毒清颗粒集采降价压力、中药注射剂/化药竞品替代、原材料（中药材）价格波动、"
        "研发投入偏低（4.4%），产品线集中度高。"
    )

    # ---- Commentary 4: 估值 ----
    pe = spot.get("pe", 0) or 0
    median_pe = spot.get("median_pe")
    pb = spot.get("pb", 0) or 0
    div_yield = spot.get("div_yield", 0) or 0
    bps = ly.get("BPS")

    p4 = (
        f"当前PE约{_fmt(pe,1)}倍"
        + (f"，历史中位PE {_fmt(median_pe,0)}倍。" if median_pe else "。")
        + f"PB约{_fmt(pb,1)}倍（每股净资产{_fmt(bps,2)}元）。"
        + f"股息率约{_fmt(div_yield,1)}%。"
        + "核心逻辑：①估值极低——PE不到10倍，而ROE 25%、营收/净利CAGR 14%/17%（2020-2025），"
        + "PEG约0.5-0.6，显著低估于港股医药板块均值（PE 20x+）；"
        + "②集采放量——尿毒清颗粒纳入集采后以价换量，2025年销量增速显著高于收入增速，"
        + "基层医疗渗透率提升驱动长期增长；"
        + "③高股息安全垫——股息率约5-6%，为港股医药股中最高之一，提供绝对收益保底。"
        + "关注尿毒清颗粒季度销量和集采续约价格作为核心信号。"
    )

    # ---- Commentary 5: 催化剂 ----
    p5 = (
        "催化剂：①尿毒清颗粒海外拓展——已成功登陆印尼市场，东南亚慢性肾病高发区市场潜力巨大；"
        + "②罗沙司他胶囊、恩格列净片2025年获批上市，肾科产品线从单品种→组合拳，"
        + "渠道协同效应逐步释放；③玉林制药品牌重塑+OTC渠道扩张，正骨水/湿毒清等老字号品种"
        + "有望通过品牌年轻化+线上渠道实现增速拐点；"
        + "④公司账面净现金充裕，具备并购整合中小药企的能力，外延增长期权值得关注。"
        + "关注每季度尿毒清颗粒销量和基层医疗机构覆盖数。"
    )

    return {
        "business": business,
        "commentary": [p1, p2, p3, p4, p5],
    }
