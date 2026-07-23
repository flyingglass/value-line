# -*- coding: utf-8 -*-
"""药明康德 02359 — VL Business + AI Commentary（数据驱动）"""
def build(stock, metrics, revenue_structure, years, cagr, spot):
    ly=metrics.get(years[-1],{}) if years else {}
    py=metrics.get(years[-2],{}) if len(years)>=2 else {}
    def _chg(c,p):
        try:
            c2,p2=float(c),float(p)
            if not c2 or not p2: return None
            if p2>0: return (c2/p2-1)*100
            if c2<0 and p2<0: return (c2-p2)/abs(p2)*100
            return (c2/p2-1)*100
        except: return None
    def _dir(c,p): return "增长" if (_chg(c,p) or 0)>0 else "下降"
    def _num(v): return float(v) if v is not None else 0
    def _fmt(v,d=0):
        try: return f"{float(v):,.{d}f}"
        except: return "-"
    def _p(v):
        try: return f"{float(v):+.1f}%"
        except: return "-"
    rev=_num(ly.get("OPERATE_INCOME"))
    np_val=_num(ly.get("HOLDER_PROFIT"))
    eps=_num(ly.get("BASIC_EPS"))
    npm=_num(ly.get("NET_PROFIT_RATIO"))
    roe=_num(ly.get("ROE"))
    roic=_num(ly.get("ROIC"))
    bps=_num(ly.get("BPS"))
    per_cf=_num(ly.get("PER_NETCASH"))
    per_capex=_num(ly.get("CAPEX_PS") or 0)
    dps=_num(ly.get("DPS") or 0)
    pb=_num(spot.get("pb",0))
    pe=_num(spot.get("pe",0))
    price=_num(spot.get("price",0))
    shares=_num(ly.get("TOTAL_SHARES"))
    r_chg=_chg(rev, py.get("OPERATE_INCOME"))
    n_chg=_chg(np_val, py.get("HOLDER_PROFIT"))
    r_abs=abs(r_chg) if r_chg is not None else 0
    n_abs=abs(n_chg) if n_chg is not None else 0
    npm_prev=_num(py.get("NET_PROFIT_RATIO"))
    roe_prev=_num(py.get("ROE"))

    # Revenue structure
    prod_data = revenue_structure.get("by_product", []) if isinstance(revenue_structure, dict) else []
   化学 = next((r for r in prod_data if '化学' in r.get('name','')), None)
   测试 = next((r for r in prod_data if '测试' in r.get('name','')), None)
   生物 = next((r for r in prod_data if '生物' in r.get('name','')), None)

    total_eq=_num(ly.get("TOTAL_EQUITY"))
    lt_debt=_num(ly.get("LT_DEBT"))

    biz=f"药明康德是全球领先的医药研发外包服务(CRO/CDMO)企业，A+H双上市（603259.SH/02359.HK）。提供从药物发现、临床前测试到商业化生产的一体化CRDMO平台，服务全球6000+客户（含全球TOP20药企）。核心化学业务含小分子CDMO和多肽/寡核苷酸TIDES两大引擎，其中TIDES（GLP-1减肥药产业链）2025年收入同比接近翻倍。2025年营收{_fmt(rev,0)}亿（同比{_dir(rev,py.get('OPERATE_INCOME'))}{r_abs:.1f}%），归母净利润{_fmt(np_val,0)}亿（同比增长{n_abs:.1f}%，含投资收益），扣非净利约132亿（+32.6%），在手订单580亿。"

    rev_化学=_num(化学.get('value',0)) if 化学 else 0
    rev_测试=_num(测试.get('value',0)) if 测试 else 0

    p1=f"2025年营收{_fmt(rev,0)}亿（同比增长{r_abs:.1f}%），归母净利润{_fmt(np_val,0)}亿（同比增长{n_abs:.1f}%）。利润增速远超营收，主因出售药明合联等资产产生约59亿投资收益；扣非净利润132.41亿（+32.6%）更能反映主业增速。核心驱动：①化学业务收入{_fmt(rev_化学,0)}亿（+25.5%），其中TIDES多肽/寡核苷酸收入113.7亿（+96%），受益于GLP-1减肥药全球产能紧缺；②小分子D&M收入199.2亿（+11.4%），商业化项目持续增长。测试业务{_fmt(rev_测试,1)}亿（+4.7%）、生物学{_fmt(_num(生物.get('value',0)) if 生物 else 0,1)}亿（+5.2%）恢复正增长。净利率从{_p(npm_prev)}升至{_p(npm)}（扣非口径约29%），毛利率持续改善。"

    fcf_ps=_fmt(per_cf-per_capex-dps,2) if per_cf else "-"
    p2=f"每股收益{_fmt(eps,2)}元，每股经营现金流{_fmt(per_cf,2)}元，每股净资产{_fmt(bps,2)}元。资本支出{_fmt(per_capex,2)}元/股主要用于多肽产能扩张（固相合成反应釜从4.1万升扩至10万升+），资本开支处于爬坡期但经营现金流充沛。2025年派息约47亿元+回购注销20亿元，合计股东回报约67亿，分红率约35%（扣非口径约50%）。资产负债率低，现金充裕，无有息负债压力。总股本约29.84亿股（A+H），2025年持续回购注销。"

    p3=f"净利率{_p(npm)}、ROE{_p(roe)}。药明康德的护城河：①一站式CRDMO平台——覆盖R（药物发现）→D（临床前/临床开发）→M（商业化生产）全链条，客户从早期分子发现开始绑定，随项目推进收入放大（\"follow the molecule\"模式）；②多肽产能壁垒——GLP-1减肥药全球需求爆发，多肽固相合成产能建设周期2-3年+资本密集（单条产线数亿），先发者优势显著；③客户粘性——全球TOP20药企全覆盖，前10大客户收入占比约35%，转换成本极高（监管认证+工艺转移）；④中国工程师红利——相比欧美CRO/CDMO，人力成本优势+效率优势（7×24小时项目周转）。风险：①中美地缘政治——BIOSECURE法案阴影（虽2024年底被否决，但后续版本风险仍在），美国客户收入占比超60%；②新冠订单退潮——2023-2024年新冠商业化项目收入归零已反映，但提醒依赖单一大客户/品种的风险；③产能过剩——全行业CDMO产能扩张（韩国三星生物、国内凯莱英/博腾等），价格竞争加剧。"

    pe_calc=_fmt(price/eps,1) if eps and price else "-"
    pb_calc=_fmt(price/bps,2) if bps and price else "-"
    p4=f"当前股价约{_fmt(price,2)}港元，PE约{pe_calc}倍（扣非口径约{_fmt(price/(132.41/29.84),1) if price else '-'}倍），PB约{pb_calc}倍。CXO行业PE历史区间宽幅波动（20-100x），取决于行业景气度+地缘政治风险溢价。2026年业绩指引营收增长~18%至约530亿，扣非净利有望继续高增。CF=12x估值对应约{_fmt(per_cf*12,2)}元/股。核心变量：①TIDES订单增速——在手订单580亿中多肽占比持续提升；②美国政策风险溢价——BIOSECURE阴影消除则估值修复空间显著；③产能利用率——2025年化学业务经调整毛利率持续提升说明利用率改善。"

    p5=f"催化剂：①GLP-1产业链——多肽CDMO全球产能紧缺，药明康德TIDES在手订单同比+20.2%，2026年多肽产能继续扩张，减肥药长周期需求确定性强；②2026年指引——营收目标~530亿（+18%），扣非利润增速有望超营收；③地缘风险缓和——BIOSECURE法案2024年底被否决后，2025年未出现新版本，中美关系边际改善有利于估值修复；④在手订单转化——580亿在手订单（+47%），为2026-2027年收入提供高能见度；⑤回购+分红——2025年全年股东回报约67亿（分红47亿+回购20亿），管理层持续提升股东回报意愿。关注每季度TIDES收入增速、在手订单变化、美国政策动态。"

    return {"business":biz,"commentary":[p1,p2,p3,p4,p5]}
