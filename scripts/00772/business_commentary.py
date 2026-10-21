# -*- coding: utf-8 -*-
"""阅文集团 00772 — VL Business + AI Commentary（数据驱动）

财务数值取自 metrics（DB 计算），业务细节取自 2025 年报（人民币千元口径换算），
外部不可核算数字均在文中标注「2025年报」。
"""
def build(stock, metrics, revenue_structure, years, cagr, spot):
    ly = metrics.get(years[-1], {}) if years else {}
    py = metrics.get(years[-2], {}) if len(years) >= 2 else {}

    def _chg(c, p):
        return (c / p - 1) * 100 if c and p and p > 0 else None

    def _dir(c, p):
        ch = _chg(c, p)
        return "增长" if (ch or 0) > 0 else "下降"

    def _fmt(v, d=0):
        return f"{v:,.{d}f}" if v else "-"

    def _p(v):
        return f"{v:+.1f}%" if v else "-"

    rev = ly.get("OPERATE_INCOME")
    np_ = ly.get("HOLDER_PROFIT")
    eps = ly.get("BASIC_EPS")
    gm = ly.get("GROSS_MARGIN")
    roe = ly.get("ROE")
    per_cf = ly.get("PER_NETCASH")
    capex_ps = ly.get("CAPEX_PS") or 0
    rev_chg = _chg(rev, py.get("OPERATE_INCOME"))
    np_chg = _chg(np_, py.get("HOLDER_PROFIT"))

    pe = spot.get("pe") or 0
    pb = spot.get("pb") or 0
    med = spot.get("median_pe")
    price = spot.get("price") or 0

    seg = revenue_structure.get("by_segment", []) if isinstance(revenue_structure, dict) else []
    prod = revenue_structure.get("by_product", []) if isinstance(revenue_structure, dict) else []
    seg_str = "、".join(f"{r['name']}{r['pct']}%" for r in seg) if seg else ""
    prod_str = "、".join(f"{r['name']}{r['pct']}%" for r in prod) if prod else ""

    biz = (
        "阅文集团是中国最大的网络文学平台与IP运营公司：上游以起点中文网、QQ阅读等自有平台"
        "沉淀作者与作品库，中游通过版权运营对外授权，下游经新丽传媒制作影视剧、并延伸至动漫、"
        "短剧、AI漫剧与IP衍生品。腾讯控股持股56.55%（2025年报），是控股股东与分发渠道。"
        + (f"收入结构（2025年报）：{seg_str}；细分：{prod_str}。" if seg_str and prod_str else "")
        + f"最新财年营收{_fmt(rev,1)}亿元（{_dir(rev, py.get('OPERATE_INCOME'))}{abs(rev_chg or 0):.1f}%），"
        f"归母净利{_fmt(np_,1)}亿元，毛利率{_fmt(gm,1)}%。"
    )

    py_np = py.get("HOLDER_PROFIT")
    if np_ and py_np and (np_ < 0 or py_np < 0):
        np_txt = f"归母净利{_fmt(np_,1)}亿元（上年{_fmt(py_np,1)}亿元）"
    else:
        np_txt = (f"归母净利{_fmt(np_,1)}亿元（{_dir(np_, py_np)}"
                  f"{abs(np_chg or 0):.1f}%）")

    p1 = (
        f"{years[-1] if years else ''}年营收{_fmt(rev,1)}亿元（{_dir(rev, py.get('OPERATE_INCOME'))}"
        f"{abs(rev_chg or 0):.1f}%），{np_txt}。收入双引擎分化：在线阅读守住基本盘（2025年报：40.47亿元，+0.4%，"
        "占比54.9%，其中自有平台35.62亿元+0.9%），版权运营及其他则明显回落（33.19亿元，-18.9%，"
        "主因影视剧排播延期、上线项目减少）。用户端承压：自有平台及腾讯自营渠道平均MAU 1.378亿"
        "（-17.3%），其中自有平台1.041亿基本走平、腾讯自营渠道3,370万（-46.3%，主动收缩免费阅读分发）；"
        "月付费用户900万（-1.1%），ARPU 32.9元（+2.8%）。量减价升，说明增长已从拉新转向存量变现。"
    )

    op_cf = ly.get("PER_NETCASH")
    p2 = (
        f"每股现金流（净利+折旧摊销，VL口径）{_fmt(op_cf,2)}元，资本开支{_fmt(capex_ps,2)}元/股。2025年报：经营活动现金净流出"
        "2.765亿元，自由现金流-4.373亿元，主因营运资金变动（影视项目回款节奏）。资产端是这家公司最扎实的"
        "部分——现金净额（现金及等价物+定期存款及其他-借款）94.36亿元，总借款为零、杠杆率为零，"
        "未动用银行融资17.2亿元，流动资产/流动负债=321.3%。资本配置偏向股东回报与内容投入：2025年"
        "回购633.88万股、耗资1.580亿港元并全部注销（2025年报），上市以来从未派息。"
    )

    p3 = (
        f"毛利率{_fmt(gm,1)}%、ROE {_p(roe)}。2025年账面亏损主要来自一次性项目：其他亏损净额12.46亿元，"
        "其中新丽传媒商誉减值约18亿元；剔除股份酬金、投资及收购亏损净额、无形资产摊销与税盾后，"
        "非国际财务报告准则（non-IFRS）归母盈利8.59亿元、non-IFRS基本EPS 0.84元，经调整EBITDA 6.14亿元"
        "（同比下降33.5%，经调整EBITDA率8.3%）。护城河在于：①中国最大的原创文学内容库与作者生态，"
        "IP储备是影视/动漫/游戏的源头供给；②腾讯生态的分发与影视工业化能力（新丽传媒）；"
        "③IP衍生品2025年GMV超11亿元、较2024年5亿元增长逾两倍，AI漫剧2025下半年收入超1亿元，"
        "第二曲线开始有收入验证。风险在于：影视业务利润高度依赖排播节奏与爆款率，商誉已两度减值，"
        "在线阅读MAU仍在收缩，IP长周期开发投入回报不确定。"
    )

    bps = ly.get("BPS")
    pe_txt = f"当前PE约{_fmt(pe,1)}倍" if pe and pe > 0 else "IFRS口径亏损，PE不适用"
    p4 = (
        f"{pe_txt}，PB约{_fmt(pb,2)}倍（每股净资产{_fmt(bps,2)}元），股价{_fmt(price,2)}港元。"
        "以2025年报现金净额94.36亿元计，净现金约占当前市值近半；扣除净现金后的隐含企业价值约107亿元，"
        "对应公司披露的non-IFRS归母盈利8.59亿元约12.5倍。估值的关键分歧不在贵贱，而在："
        "在线阅读的现金流能否止跌，以及版权运营能否从「靠项目排播的影视公司」转型为「靠IP长尾变现的平台」。"
    )

    p5 = (
        "催化剂：①新丽传媒影视项目储备在2026年集中排播，版权运营收入恢复增长；②IP衍生品延续"
        "「GMV从5亿到11亿」的翻倍节奏，且从授权走向自营、提升变现率；③AI漫剧/短剧以低成本产能"
        "放大IP库存价值，2025下半年已录得超1亿元收入，2026年看能否规模化；④账上94.36亿元净现金"
        "提供回购与并购弹药，回购若能常态化将托底每股价值。跟踪信号：半年报的MAU/MPU是否止跌、"
        "版权运营收入增速、IP衍生品GMV与AI漫剧收入体量、商誉余额是否需再度减值。"
    )

    return {"business": biz, "commentary": [p1, p2, p3, p4, p5]}
