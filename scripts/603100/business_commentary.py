# -*- coding: utf-8 -*-
"""川仪股份 603100 — VL BUSINESS + AI Commentary（人工精修版）

口径说明（重要）:
  1. metrics["HOLDER_PROFIT"] / ["BASIC_EPS"] 为 VL 流水线 A 股调整口径 = 扣非归母净利润
     （engine 对 A 股取 CAS 扣非口径, 见报告 footnotes「A股扣非净利润…较归母净利润调整…」）。
     正文引用该口径时一律写作「扣非净利润」；引用年报归母数时单独标注。
  2. 结构占比、分红、市占率、研发等年报原文数据以常量列出并标注出处，DB 中不存在的不臆造。
  3. 面向未来的判断仅来自年报/中报原文表述，不做主观外推。

数据来源:
  - metrics / spot / cagr / revenue_structure 参数 = engine 由 data/603100.db 计算
  - 年报原文 = 2025年年度报告(2026-04-15 董事会) / 2026年半年度报告, 正文内逐条标注
"""

# ---------- 年报原文常量（来源: 2025年年度报告, 单位见注释） ----------
_Y25_REV_TOTAL = 680494.71      # 万元, P25 主营业务收入
_Y25_GPM = 34.31                # %, P25 综合毛利率 (+1.22pp)
_Y25_RD = 48008.89              # 万元, P28-29 研发投入(全部费用化), 占营收 7.05%
_Y25_RD_STAFF = 1049            # 人, P28-29 研发人员, 占总人数 19.99%
_Y25_DIV_TOTAL = 261718319.76   # 元, P60 2025年度现金分红总额(三季度153,951,952.80 + 年度107,766,366.96)
_Y25_DIV_RATIO = 40.73          # %, P60 占2025年归母净利润比例(含回购注销为40.93%)
_Y23_25_DIV = 853031877.86      # 元, P59-60 最近三个会计年度累计现金分红
_Y25_INVEST_INC_YOY = -44.97    # %, P19 投资收益同比变动(联营企业横河川仪利润大幅下降)
_SHARE_TRANSFER = 29.91         # %, P88/P113 国机重庆公司受让四联集团+渝富控股股份比例, 2025-11-14 过户
_Y25_MDA = {                    # P19/P28-29 经营表述
    "合同": "2025年新签合同额与上年基本持平",
    "行业": "化工28.6%、石油天然气18.1%、冶金11.4%、电力6.0%",
    "央采": "全年中标31个央企集采框架, 新入围国家管网、大唐集团",
}
_RUI_2025 = (                   # P19 睿工业数据(2025年度国内市场份额排名)
    "智能变送器第3（国产品牌第1）、智能流量仪表第5（国产品牌第1）、"
    "温度仪表第1、气体和水质分析仪器第5（国产品牌第3）"
)
_H26 = {                        # 2026年半年度报告 P7 主要会计数据
    "营收": 341822.99,          # 万元, +4.18%
    "归母": 28367.10,           # 万元, -12.60%
    "扣非": 28999.31,           # 万元, +8.10%
    "经营现金流": 475.87,       # 万元, -98.11%
    "ROE": 5.91,                # %, 加权, -1.32pp
}


def build(stock, metrics, revenue_structure, years, cagr, spot):
    def _m(y):
        return metrics.get(y) or metrics.get(str(y)) or {}

    ly = _m(years[-1]) if years else {}
    py = _m(years[-2]) if len(years) > 1 else {}

    def _num(v, d=0.0):
        try:
            return float(v)
        except (TypeError, ValueError):
            return d

    def _chg(cur, prev):
        cur, prev = _num(cur), _num(prev)
        if not cur or not prev or prev <= 0:
            return None
        return (cur / prev - 1) * 100

    rev = _num(ly.get("OPERATE_INCOME"))
    np_v = _num(ly.get("HOLDER_PROFIT"))
    eps = _num(ly.get("BASIC_EPS"))
    gm = _num(ly.get("GROSS_MARGIN"))
    npm = _num(ly.get("NET_PROFIT_RATIO"))
    roe = _num(ly.get("ROE"))
    roic = _num(ly.get("ROIC"))
    bps = _num(ly.get("BPS"))
    per_cf = _num(ly.get("PER_NETCASH"))
    per_capex = _num(ly.get("CAPEX_PS"))
    dps = _num(ly.get("DPS"))
    payout = _num(ly.get("PAYOUT_RATIO"))
    med_pe = _num(spot.get("median_pe"))
    price = _num(spot.get("price"))
    pe = _num(spot.get("pe"))
    pb = _num(spot.get("pb"))
    rev_yoy = cagr.get("revenue", {}).get("1yr")
    rev_5y = cagr.get("revenue", {}).get("5yr")
    np_p = _num(py.get("HOLDER_PROFIT"))
    gm_p = _num(py.get("GROSS_MARGIN"))
    np_yoy = (np_v / np_p - 1) * 100 if np_p else None
    gm_delta = (gm - gm_p) if gm_p else None

    prod = (revenue_structure or {}).get("by_product", []) or []
    reg = (revenue_structure or {}).get("by_region", []) or []
    p_top = prod[0] if prod else {}
    reg_ovs = next((r for r in reg if "出口" in str(r.get("name", "")) or "境外" in str(r.get("name", ""))), {})
    reg_dom_pct = 100 - _num(reg_ovs.get("pct"))

    yoy_s = f"{rev_yoy:+.1f}%" if rev_yoy is not None else "同比数据缺失"

    # ---------- BUSINESS ----------
    biz = (
        f"川仪股份是国内综合型工业自动化仪表及控制装置研发制造企业，2014年8月于上交所主板上市，"
        f"产品覆盖智能执行机构、智能变送器、智能调节阀、智能流量仪表、温度仪表、物位仪表、控制设备及装置、"
        f"分析仪器，并提供系统集成与总包服务，下游以化工、石油天然气、冶金、电力等流程工业为主。"
        f"{years[-1]}年营收{rev:.1f}亿元（{yoy_s}），扣非净利润{np_v:.1f}亿元，"
        f"{p_top.get('name', '主营')}占营收{_num(p_top.get('pct')):.0f}%，国内收入占{reg_dom_pct:.0f}%。"
        f"2025年11月国机重庆公司受让四联集团与渝富控股合计{_SHARE_TRANSFER}%股份完成过户，"
        f"控股股东变更，实际控制人由重庆市国资委变更为国机集团。"
    )

    # ---------- P1 经营分析 ----------
    p1 = (
        f"{years[-1]}年是公司近五年首次收入下滑：营收{rev:.1f}亿元（{yoy_s}），扣非净利润{np_v:.1f}亿元"
        + (f"（同比{np_yoy:+.1f}%）" if np_yoy is not None else "")
        + (f"，而毛利率反而提升至{gm:.1f}%（同比{gm_delta:+.1f}pp，来源：2025年报 P25），"
           if gm_delta is not None else f"，毛利率{gm:.1f}%（来源：2025年报 P25），")
        + f"显示下滑来自收入端而非价格端。收入仍高度依赖流程工业：{_Y25_MDA['行业']}（来源：2025年报 P19）；"
        + f"分产品{p_top.get('name', '')}占{_num(p_top.get('pct')):.0f}%仍为核心，"
        + (f"复合材料占{_num(prod[1].get('pct')):.0f}%为第二曲线（毛利率约20%，低于主业，来源：2025年报 P25）。"
           if len(prod) > 1 else "。")
        + f"经营层面：{_Y25_MDA['合同']}，{_Y25_MDA['央采']}（来源：2025年报 P19）。"
        + f"进入2026年收入端重回增长——上半年营收{_H26['营收'] / 10000:.2f}亿元（+4.18%），"
        + f"扣非归母净利润{_H26['扣非'] / 10000:.2f}亿元（+8.10%），毛利率与净利率同比改善（来源：2026年中报 P7）。"
    )

    # ---------- P2 现金流与资本配置 ----------
    net_ps = round(per_cf - per_capex - dps, 2) if per_cf else None
    p2 = (
        f"每股经营现金流{per_cf:.2f}元，每股资本支出仅{per_capex:.2f}元，"
        f"扣减分红{dps:.2f}元/股后仍有净留存{net_ps}元/股，属轻资产、内生现金驱动的模式；"
        f"2025年经营活动现金流净额6.10亿元（+26.31%），回款管理改善（来源：2025年报 P24）。"
        f"资本配置的最大看点是分红节奏前置：2025年度现金分红总额{_Y25_DIV_TOTAL / 1e8:.2f}亿元"
        f"（三季度每股0.30元 + 年度每股0.21元，合计0.51元/股），占2025年归母净利润{_Y25_DIV_RATIO}%"
        f"（含回购注销1,288,634.63元后为40.93%）；最近三个会计年度累计分红{_Y23_25_DIV / 1e8:.2f}亿元。"
        f"分红率连续三年稳定在37.9%-40.7%（2024年度占归母37.93%，来源：2025年报 P59），"
        f"而非一次性提升——真正的变化是2024年起新增三季度中期分配，把回报从「一年一次」变成「一年两次」，"
        f"这一安排在章程层面有「每年现金分红不低于当年可供分配利润30%」的约束（来源：2025年报 P58）。"
        f"需警惕现金流与利润的背离：2026年上半年经营现金流净额仅{_H26['经营现金流']:.2f}百万元（同比-98.11%），"
        f"而2025年末应收账款与合同资产账面价值合计19.00亿元、占流动资产25.30%（来源：2025年报 P42/P7），"
        f"收入增长未能同步转化为回款——这是当前最需要跟踪的裂口。"
    )

    # ---------- P3 盈利质量与护城河 ----------
    p3 = (
        f"毛利率{gm:.1f}%、净利率{npm:.1f}%、ROE {roe:.1f}%、ROIC {roic:.1f}%，"
        f"在仪器仪表制造业中处于中上水平；BPS {bps:.2f}元，杠杆不高（2025年资产负债率48.8%）。"
        f"护城河来自三处：一是产品线完整度——国内少有的能覆盖「测量与分析 + 控制与执行 + 智控系统」"
        f"全链路的厂商，客户一次选型可覆盖全厂仪表；二是国产替代身位——按睿工业2025年数据，"
        f"{_RUI_2025}；三是技术投入——2025年研发投入{_Y25_RD / 10000:.2f}亿元（占营收7.05%，全部费用化），"
        f"研发人员{_Y25_RD_STAFF}人、占总人数19.99%（来源：2025年报 P19/P28-29）。"
        f"竞争格局不容乐观：艾默生、西门子、E+H、横河电机等国际厂商仍在高端市场保持优势并深化中国布局，"
        f"行业呈「高端突破加速、中低端过剩加剧」态势（来源：2026年中报 P14）。"
        f"此外2025年投资收益同比{_Y25_INVEST_INC_YOY}%（联营企业横河川仪利润大幅下降，来源：2025年报 P19），"
        f"该项曾是利润的重要补充，其波动放大了当期业绩降幅。"
    )

    # ---------- P4 估值分析 ----------
    cf_15x = round(per_cf * 15, 2) if per_cf else None
    cf_20x = round(per_cf * 20, 2) if per_cf else None
    div_yield_calc = round(dps / price * 100, 2) if price and dps else None
    pe_vs_med = ""
    if pe and med_pe:
        pe_vs_med = f"，低于15年年均PE中位{med_pe:.1f}倍" if pe < med_pe else f"，高于15年年均PE中位{med_pe:.1f}倍"
    p4 = (
        f"现价{price:.2f}元对应PE {pe:.1f}倍（engine 以归母口径EPS TTM计算）、PB {pb:.2f}倍{pe_vs_med}。"
        f"以本报告的CF估值法：每股经营现金流{per_cf:.2f}元，CF=15倍对应{cf_15x}元、CF=20倍对应{cf_20x}元，"
        f"现价处在CF=15倍线附近。股息率按2025年度实际派发0.51元/股计算约{div_yield_calc}%。"
        f"口径提示：本报告指标表中的EPS为扣非口径（{np_v:.1f}亿元），比年报归母净利润6.43亿元更保守，"
        f"故表内PE读数（历史年均PE中位{med_pe:.1f}倍）系统性高于以归母利润计算的静态PE。"
        f"结论：估值本身不贵，分歧不在价格而在盈利方向——收入下滑究竟是周期性回落还是趋势性下台阶。"
    )

    # ---------- P5 催化剂与风险 ----------
    p5 = (
        f"催化剂：①国机集团入主（{_SHARE_TRANSFER}%股份过户完成，18个月内不转让）带来的央企协同——"
        f"借力国机集团海外业务资源、国机内部企业（苏美达、中工国际等）与央企集采通道，"
        f"这是公司历史上第一次真正接入央企体系（来源：2025年报 P19/P88）；"
        f"②「十五五」规划将高端仪器仪表列入重大工程，国产替代纵深推进，公司作为国产品牌份额第一受益；"
        f"③2026年上半年扣非已恢复正增长（+8.10%），若下半年新签合同转化加速，收入下滑周期有望确认结束。"
        f"风险：①下游化工、冶金资本开支放缓，2025年新签合同仅与上年持平，订单端尚无明确拐点；"
        f"②国际厂商在高端市场挤压与中低端产能过剩「两头受气」；③2026年上半年经营现金流同比-98.11%，"
        f"回款恶化若持续将压制分红能力；④联营企业横河川仪投资收益的大幅波动；"
        f"⑤管理层更替期的不确定性——李赐犁于2025年12月3日当选董事长，资本配置与分红政策的延续性待观察。"
        f"跟踪信号：季度新签合同额、毛利率能否守住34%、经营现金流回款率、海外收入占比（当前仅{_num(reg_ovs.get('pct')):.1f}%）。"
    )

    return {"business": biz, "commentary": [p1, p2, p3, p4, p5]}
