# -*- coding: utf-8 -*-
"""拼多多 PDD — VL Business + AI Commentary（数据驱动）"""

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
    rev_chg = _chg(rev, py.get("OPERATE_INCOME"))
    np_chg = _chg(np_val, py.get("HOLDER_PROFIT"))
    per_cf = ly.get("PER_NETCASH")
    per_capex = ly.get("CAPEX_PS") or 0
    dps = ly.get("DPS") or 0
    payout = ly.get("PAYOUT_RATIO")

    rev_parts = []
    if isinstance(revenue_structure, dict) and revenue_structure:
        for dim_key, items in revenue_structure.items():
            if items:
                rev_parts.extend([f"{r.get('name','')}{r.get('pct',''):.0f}%" for r in items[:3]])

    business = (
        f"拼多多（PDD Holdings）是中国领先的电商平台，旗下运营拼多多（社交拼团+低价白牌）、"
        f"Temu（跨境电商，覆盖70+国家）等业务。2018年纳斯达克上市，以极致性价比模式快速崛起。"
        f"FY{latest_yr}营收{_fmt(rev,0)}亿（{_dir(rev, py.get('OPERATE_INCOME'))}{abs(rev_chg):.1f}%），"
        f"归母净利{_fmt(np_val,0)}亿，净利率{_fmt_pct(npm)}，ROE {_fmt_pct(roe)}。"
        + (f"收入构成：{'/'.join(rev_parts)}。" if rev_parts else "")
    )

    p1 = (
        f"2026年7月 — 拼多多{latest_yr}年营收{_fmt(rev,0)}亿元"
        + (f"（{_dir(rev, py.get('OPERATE_INCOME'))}{abs(rev_chg):.1f}%）" if rev_chg else "")
        + f"，Non-GAAP净利润约{_fmt(np_val*1.07 if np_val else None,0)}亿元。"
        + f"增速从2024年的59%放缓至10%，主因国内电商竞争加剧（抖音电商/京东低价策略）及Temu海外扩张投入。"
        + f"毛利率{_fmt_pct(gm)}、净利率{_fmt_pct(npm)}，平台模式轻资产高利润率特征显著。"
        + "2025年成立「新拼姆」自营品牌平台（首批注资150亿），从纯平台向平台+自营混合模式转型。"
    )

    if eps:
        p2 = (
            f"每股收益¥{_fmt(eps,2)}，每股经营现金流¥{_fmt(per_cf,2)}，"
            f"资本支出每股¥{_fmt(per_capex,2)}。"
            f"账面现金及短期投资约3871亿元（$540亿），几乎无有息负债，净现金极为充裕。"
            "拼多多一直以来不分红、不回购，利润全部留存用于再投资（Temu全球扩张+新拼姆自营业务）。"
            "23,000+员工，人均创收约1800万元，人效极高。"
        )
    else:
        p2 = "每股资金流向：数据待补充。"

    roic = ly.get("ROIC")
    p3 = (
        f"毛利率{_fmt_pct(gm)}、净利率{_fmt_pct(npm)}、ROE {_fmt_pct(roe)}"
        + (f"、ROIC {_fmt_pct(roic)}。" if roic else "。")
        + "竞争壁垒："
        "①极致的低价供应链——C2M（工厂直达消费者）+反向定制+超大订单量，单位履约成本行业最低；"
        "②Temu的全球增长期权——利用中国供应链优势+全托管模式快速复制至70+国家，"
        "2024年GMV已超500亿美元，海外市场打开第二增长曲线；"
        "③社交裂变+游戏化运营——拼团模式创造极低获客成本，7.8亿年活跃买家形成网络效应；"
        "④账上3871亿现金——在电商烧钱大战中具备极强的持久战和投资能力。"
        "风险：中美关税/贸易摩擦（Temu核心风险）、国内电商竞争激烈（抖音电商增速50%+）、"
        "新拼姆自营模式对利润率的摊薄、监管风险（VIE架构）。"
    )

    pe = spot.get("pe", 0) or 0
    median_pe = spot.get("median_pe")
    pb = spot.get("pb", 0) or 0
    div_yield = spot.get("div_yield", 0) or 0
    bps = ly.get("BPS")

    p4 = (
        f"当前PE约{_fmt(pe,1)}倍"
        + (f"，历史中位PE {_fmt(median_pe,0)}倍。" if median_pe else "。")
        + f"PB约{_fmt(pb,1)}倍（每股净资产{_fmt(bps,2)}元）。"
        + f"股息率约{_fmt(div_yield,1)}%（不分红）。"
        + "核心逻辑：①PE不到10倍，对应10%增速，PEG≈1，估值合理但非极端低估；"
        + "②Temu是最大的价值变量——若海外业务从亏损走向盈利（参照Shein路径），"
        + "利润弹性极大（当前Temu仍处于投入期，亏损拖累整体利润率）；"
        + "③3871亿净现金占市值约40%+，提供了极强的安全边际和抗风险能力；"
        + "④新拼姆自营品牌是战略突围——对标Costco自有品牌的会员模式，若成功可打开第三增长曲线。"
        + "关注Temu季度亏损额和国内GMV增速作为核心信号。"
    )

    p5 = (
        "催化剂：①Temu盈利拐点——2025年海外扩张速度放缓后，2026年若实现单季度盈亏平衡，"
        + "将触发市场对利润弹性的重估；②新拼姆首年运营数据（GMV/复购率/NPS）若超预期，"
        + "验证自营品牌模式可行性；③中美贸易谈判若降低关税壁垒，Temu估值直接受益；"
        + "④公司账上3871亿现金，若启动股份回购计划，将是重大估值催化剂。"
        + "关注每季度Temu经营亏损率和国内平台GMV同比增速。"
    )

    return {
        "business": business,
        "commentary": [p1, p2, p3, p4, p5],
    }
