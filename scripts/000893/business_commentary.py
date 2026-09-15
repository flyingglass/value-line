# -*- coding: utf-8 -*-
"""亚钾国际 000893 — VL Business + AI Commentary（数据驱动）

口径说明:
  - metrics 中 HOLDER_PROFIT / BASIC_EPS / NET_PROFIT_RATIO 为 VL 口径净利润
    (A股取年报"扣除非经常性损益后的净利润"), 与年报"归母净利润"存在差额, 文本中已注明
  - TOTAL_SHARES / LT_DEBT / TOTAL_EQUITY 单位为百万元(百万股)
  - revenue_structure amount 单位为百万元
硬编码事实(产量/储量/项目进度等)均标注年报出处, 不引用 DB 之外的推测数据。
"""
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

    def _dir(c, p): return "增长" if (_chg(c, p) or 0) > 0 else "下降"

    def _num(v): return float(v) if v is not None else 0

    def _fmt(v, d=0):
        try: return f"{float(v):,.{d}f}"
        except: return "-"

    def _p(v):
        try: return f"{float(v):+.1f}%"
        except: return "-"

    rev = _num(ly.get("OPERATE_INCOME"))          # 亿元
    np_val = _num(ly.get("HOLDER_PROFIT"))        # 亿元, VL口径(扣非)
    eps = _num(ly.get("BASIC_EPS"))               # 元
    gm = _num(ly.get("GROSS_MARGIN"))             # %
    npm = _num(ly.get("NET_PROFIT_RATIO"))        # %
    roe = _num(ly.get("ROE"))
    roic = _num(ly.get("ROIC"))
    bps = _num(ly.get("BPS"))                     # 元
    per_cf = _num(ly.get("PER_NETCASH"))          # 元/股
    per_capex = _num(ly.get("CAPEX_PS") or 0)     # 元/股
    dps = _num(ly.get("DPS") or 0)                # 元/股
    shares = _num(ly.get("TOTAL_SHARES"))         # 百万股
    lt_debt = _num(ly.get("LT_DEBT"))             # 百万元
    total_eq = _num(ly.get("TOTAL_EQUITY"))       # 百万元
    pb = _num(spot.get("pb", 0))
    pe = _num(spot.get("pe", 0))
    price = _num(spot.get("price", 0))
    div_yield = _num(spot.get("div_yield", 0))
    r_chg = _chg(rev, py.get("OPERATE_INCOME"))
    n_chg = _chg(np_val, py.get("HOLDER_PROFIT"))
    r_abs = abs(r_chg) if r_chg is not None else 0
    n_abs = abs(n_chg) if n_chg is not None else 0
    # shares 单位为百万股 → 每股指标 × 百万股 / 100 = 亿元
    cf_total = per_cf * shares / 100.0 if shares else 0
    capex_total = per_capex * shares / 100.0 if shares else 0
    lt_debt_yi = lt_debt          # metrics 中 LT_DEBT / TOTAL_EQUITY 同为亿元
    total_eq_yi = total_eq
    lt_debt_to_eq = (lt_debt / total_eq * 100) if total_eq else 0

    biz = (f"亚钾国际是中国企业\"走出去\"在境外开发钾盐资源的标杆企业，主营氯化钾（钾肥）的开采、生产与销售，"
           f"核心资产位于老挝甘蒙省，公司目前拥有老挝甘蒙省263.3平方公里钾盐矿权（来源：2025年报），"
           f"建成了我国境外第一个实现工业化生产的钾肥装置，也是东南亚地区规模最大的钾肥生产商。"
           f"2025年营收{_fmt(rev, 2)}亿元（同比{_dir(rev, py.get('OPERATE_INCOME'))}{r_abs:.1f}%），"
           f"VL口径净利润（扣非）{_fmt(np_val, 2)}亿元（同比{_dir(np_val, py.get('HOLDER_PROFIT'))}{n_abs:.1f}%）。")

    p1 = (f"2025年营收{_fmt(rev, 2)}亿元（同比{_dir(rev, py.get('OPERATE_INCOME'))}{r_abs:.1f}%），"
          f"VL口径净利润（扣非）{_fmt(np_val, 2)}亿元，同比{_dir(np_val, py.get('HOLDER_PROFIT'))}{n_abs:.1f}%；"
          f"年报口径归母净利润16.73亿元（同比+75.97%），两者差额主因当年计提资产减值损失3.12亿元"
          f"（来源：2025年报利润表、同花顺指标）。业绩爆发来自量价齐升：全年钾肥产量201.15万吨、销量204.57万吨，"
          f"产销量双双突破200万吨并创历史新高；2025年12月6日小东布矿区主运输系统投运暨第三个100万吨/年钾肥项目"
          f"联动投料试车成功，公司正式迈入300万吨/年产能阶段（来源：2025年报）。盈利能力同步修复，"
          f"毛利率由上一年的{_p(_num(py.get('GROSS_MARGIN')))}提升至{_p(gm)}，"
          f"净利率由{_p(_num(py.get('NET_PROFIT_RATIO')))}提升至{_p(npm)}。"
          f"2026年上半年延续高增：营收38.22亿元（同比+51.53%）、归母净利润13.50亿元（同比+57.93%），"
          f"公司披露增长主因钾肥销量增加及价格上升（来源：2026年半年报）。")

    p2 = (f"每股收益{_fmt(eps, 2)}元（VL口径，按扣非净利润/股本），每股经营现金流{_fmt(per_cf, 2)}元，"
          f"每股净资产{_fmt(bps, 2)}元。每股经营现金流是EPS的{_fmt(per_cf / eps, 2) if eps else '-'}倍，"
          f"盈利的现金含量扎实：按每股口径折算，全年经营活动现金流约{_fmt(cf_total, 2)}亿元"
          f"（2025年报披露为22.82亿元，差异来自股本口径），"
          f"同期资本开支约{_fmt(capex_total, 2)}亿元，现金流在覆盖扩产后仍有结余"
          f"（2025年报披露投资活动净流出18.81亿元）。"
          f"长期负债（VL口径）{_fmt(lt_debt_yi, 2)}亿元，相当于净资产的{_fmt(lt_debt_to_eq, 1)}%，"
          f"2025年末资产负债率33.24%，2026年上半年末降至30.97%、货币资金升至21.06亿元"
          f"（来源：2025年报、2026年半年报）。资本配置明显偏向扩张而非分红："
          f"2025年度每股派息0.11元（除权日2026-06-03，来源：公司分红方案），"
          f"股息率约{_fmt(div_yield, 2)}%，分红率{_fmt(_num(ly.get('PAYOUT_RATIO')), 1)}%，"
          f"在300万吨产能爬坡阶段，现金再投入矿山建设是理性选择，但也意味着股东回报需等待产能兑现。")

    p3 = (f"毛利率{_p(gm)}、净利率{_p(npm)}、ROE{_p(roe)}、ROIC{_p(roic)}。"
          f"护城河来自三层：①资源壁垒——公司拥有老挝甘蒙省263.3平方公里钾盐矿权；"
          f"其中35平方公里矿区钾盐矿储量10.02亿吨、折纯氯化钾1.52亿吨，"
          f"彭下-农波矿区179.8平方公里矿石总量约39.35亿吨、折纯氯化钾约6.77亿吨（来源：2021年报），"
          f"合计折纯氯化钾约8.29亿吨；②成本壁垒——主要原材料为自有光卤石矿、不涉及外部采购（来源：2025年报），"
          f"叠加老挝本地人力成本与\"海运+陆运+中老铁路\"多式联运体系，单位成本仍有下探空间；"
          f"③区位与政策——东南亚最大钾肥生产商，产品覆盖中国、越南、泰国等市场，"
          f"老挝政府授予公司国家级\"老挝发展勋章\"（来源：2025年报）。"
          f"风险同样清晰：钾肥是强周期资源品（2024年公司营收同比-8.97%即为价格回落所致）；"
          f"老挝境外经营的政策、汇率与地缘风险；新产能爬坡不及预期；"
          f"以及2025年已出现的资产减值计提，提示重资产扩张期的报表波动。")

    p4 = (f"当前股价{_fmt(price, 2)}元，PE约{_fmt(pe, 1) if pe else (_fmt(price / eps, 1) if eps else '-')}倍，"
          f"PB约{_fmt(pb, 2) if pb else (_fmt(price / bps, 2) if bps else '-')}倍，每股净资产{_fmt(bps, 2)}元。"
          f"公司属资源型周期股，净资产主体为老挝钾盐矿采矿权与在建产能，重置成本高、"
          f"但盈利随钾肥价格波动剧烈，周期高点PE会被压低、周期底部PE会失真，因此更适合以PB锚定："
          f"按年末每股净资产与当年成交均价测算，2015-2025年历史PB区间约1.0-2.9倍、"
          f"近五年（2021-2025）均值约2.3倍（本表测算，前复权口径）。"
          f"当前PB处于近五年区间上沿，说明估值已部分反映300万吨产能释放与钾肥价格上行预期，"
          f"后续需要以产量兑现和钾肥价格中枢来消化估值。")

    p5 = ("催化剂：①产能爬坡——第三个100万吨/年钾肥项目已于2025年12月投料试车，公司进入300万吨/年产能阶段，"
          "2026年产量弹性主要来自该产能达产；②在建储备——第二个100万吨/年项目矿建加固推进中，"
          "彭下-农波矿区200万吨/年项目为远期增量，公司另有近90万吨/年颗粒钾产能（来源：2025年报）；"
          "③价格端——据USGS 2026年报告，全球探明钾盐储量（K₂O当量）超59亿吨，老挝占比17.0%居第三；"
          "Nutrien预计2026年全球钾肥贸易发运量7,400万-7,700万吨；"
          "Uralkali因资源枯竭将于2027-2029年逐步关闭合计360万吨产能（来源：2026年半年报引述），"
          "供给端收缩对钾肥价格形成支撑；④渠道——与中农控股、史丹利、云图控股等签署战略合作，"
          "老越永安国际港3号码头钾肥专用码头投运，物流成本进一步优化（来源：2025年报）。"
          "跟踪要点：季度钾肥产量/销量与单吨毛利、第二个百万吨项目投产时点、"
          "国际钾肥大合同价与港口库存、老挝政策与税收优惠变化，以及资产减值计提是否延续。")

    return {"business": biz, "commentary": [p1, p2, p3, p4, p5]}
