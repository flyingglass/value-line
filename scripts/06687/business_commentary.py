# -*- coding: utf-8 -*-
"""聚水潭 06687 — VL Business + AI Commentary（个股定制，数据驱动）

为什么必须手写：build.py step_4_5 自动生成的脚本会引用未定义变量 name、把
P4 写死成 CF 倍数套话，且对「GAAP 巨亏但经营层面已转正」这类标的完全不成立。

数据分层（严格区分）:
  A. 来自入参 metrics / revenue_structure / cagr / spot —— 全部动态取，不硬编码。
  B. 年报/公告原文中 DB 没有的运营与口径数字 —— 集中在下方常量区，逐条标注出处，
     属「引用原文」，不是推断。
  C. 推算值 —— 仅在文中显式标 🟡 并交代算法，不做结论级断言。

出处:
  - 2025年报 p8 财务概要 / p10 收入明细 / p11-12 核心业务表现与费用 / p14 优先股亏损
    / p17 现金与合约获取成本 / p19 僱員及薪酬
  - 2026 中期业绩公告 p1 财务概要 / p8 收入拆分 / p19-20 收入明细与核心指标 / p22 每股盈利
  - 招股章程 p8 收入按产品类别及 SaaS 按收费模式拆分 / p317 收入明细
"""

# ── B 类：年报/公告原文数字（DB 中不存在，引用时逐条带出处）──
FY25 = {
    "rev_yoy": 25.6,          # 2025年报 p11
    "gross_margin": 73.6,     # 2025年报 p12（2024: 68.5）
    "cost_yoy": 5.1,          # 2025年报 p12
    "sales_yoy": 7.0,         # 2025年报 p12
    "rd_yoy": 1.4,            # 2025年报 p13
    "op_income": 51.597,      # 百万元，2025年报 p10 全年业绩公告「經營收入」；2024 为 -62.093
    "op_income_py": -62.093,
    "gaap_holder": -1655.025, # 百万元，2025全年业绩公告「本公司權益擁有人應佔虧損」
    "adj_np": 230.868,        # 百万元，2025全年业绩公告 / 年报 p8（2024: 60.412）
    "adj_np_py": 60.412,
    "pref_loss": 1769.644,    # 百万元，2025年报 p14 可转换可赎回优先股公允价值亏损
    "ocf": 404.758,           # 百万元，2025全年业绩公告「經營活動所得現金淨額」
    "cash": 3052.581,         # 百万元，2025年报 p17 现金及现金等价物
    "contract_liab": 2257.450,  # 百万元，2026中期业绩公告 p9（2025-12-31 合约负债总额）
    "cac": 416.740,           # 百万元，2026中期业绩公告 p9 合约获取成本
    "customers_k": 113.0,     # 千名，2025年报 p12（2024: 88.4）
    "customers_py_k": 88.4,
    "orders_bn": 38.8,        # 十亿笔，2025年报 p12（2024: 33.0）
    "rev_per_order": 0.0285,  # 元/笔，2025年报 p12（2024: 0.0266）
    "sea_rev": 21.9,          # 百万元，2025年报 p11 东南亚（2024: 10.0）
    "sea_rev_py": 10.0,
    "collab_yoy": 65.3,       # %，2025年报 p10 协同产品收入增速
    "employees": 2552,        # 人，2025年报 p19（2024: 2758）
}
H1_26 = {
    "rev": 615.015,           # 百万元，2026中期业绩公告 p1（2025H1: 523.642）
    "rev_yoy": 17.4,
    "gross_margin": 76.4,     # %，p20（2025H1: 71.8）
    "holder_profit": 101.368, # 百万元，p1（2025H1: -41.146）
    "adj_np": 185.018,        # 百万元，p1（2025H1: 51.784）
    "collab_yoy": 43.4,       # %，p19 协同产品
    "orders_bn": 20.2,        # 十亿笔，p20（2025H1: 18.2）
    "rev_per_order": 0.030,   # 元/笔，p20
    "eps": 0.23,              # 元，p22
}
# 招股章程 p8：SaaS 收入按收费模式，订阅占比 51.5%(2022) → 62.1%(2024)
SUB_MIX_2022, SUB_MIX_2024 = 51.5, 62.1


def _num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return 0.0


def _fmt(v, d=1):
    try:
        return f"{float(v):,.{d}f}"
    except (TypeError, ValueError):
        return "-"


def _pct(v, d=1):
    try:
        return f"{float(v):.{d}f}%"
    except (TypeError, ValueError):
        return "-"


def _chg(c, p):
    c2, p2 = _num(c), _num(p)
    if not c2 or not p2:
        return None
    return (c2 / p2 - 1) * 100


def _dim(rs, key):
    raw = rs.get(key, []) if isinstance(rs, dict) else []
    acc = {}
    for r in raw:
        name = str(r.get("name", "")).strip()
        if not name:
            continue
        p = _num(r.get("pct"))
        if name not in acc or p > acc[name]["pct"]:
            acc[name] = {"name": name, "pct": p,
                         "amount": _num(r.get("value") or r.get("amount"))}
    return sorted(acc.values(), key=lambda x: -x["pct"])


def build(stock, metrics, revenue_structure, years, cagr, spot):
    ly = metrics.get(years[-1], {}) if years else {}
    py = metrics.get(years[-2], {}) if len(years) >= 2 else {}
    yr = years[-1] if years else ""

    rev = _num(ly.get("OPERATE_INCOME"))
    holder = _num(ly.get("HOLDER_PROFIT"))
    eps = _num(ly.get("BASIC_EPS"))
    gm = _num(ly.get("GROSS_MARGIN")) or _num(ly.get("GROSS_PROFIT_RATIO"))
    npm = _num(ly.get("NET_PROFIT_RATIO"))
    roe = _num(ly.get("ROE")) or _num(ly.get("ROE_AVG"))
    bps = _num(ly.get("BPS"))
    per_cf = _num(ly.get("PER_NETCASH")) or _num(ly.get("PER_NETCASH_OPERATE"))
    dps = _num(ly.get("DPS"))
    price = _num(spot.get("price", 0))
    pb = _num(spot.get("pb", 0)) or (round(price / bps, 2) if price and bps else 0)
    div_y = _num(spot.get("div_yield", 0))

    prods = _dim(revenue_structure, "by_product")
    prod_str = "、".join(f"{i['name']} {_pct(i['pct'], 1)}" for i in prods[:4])

    # ── Business: 先把生意说清，再给最新年结构与关键数字 ──
    biz = (
        "聚水潭（06687.HK，JST Group）是中国电商 SaaS ERP 提供商，2025年10月21日于港交所主板上市。"
        "核心产品「聚水潭ERP」帮商家在各电商平台之间打通店铺、订单、库存、商品与财务数据；"
        "以 ERP 为入口再延伸至财务、客服、采购、分销等协同产品，收入以年度订阅与按处理订单量计费为主"
        "（来源：2026中期业绩公告 p17、招股章程 p8）。"
    )
    if prod_str:
        biz += f"{yr}年收入结构：{prod_str}（口径：2025年报 p10 / 招股章程 p317，占比按金额自算）。"
        biz += (
        f"{yr}年收入{_fmt(rev, 2)}亿元、同比{FY25['rev_yoy']:+.1f}%，"
        f"毛利率{FY25['gross_margin']:.1f}%，SaaS 客户{FY25['customers_k']:.1f}千家、"
        f"全年处理订单{FY25['orders_bn']:.1f}十亿笔（来源：2025年报 p11-12）。"
    )
    biz += (
        f"按国际财务报告准则的归母净利润为{FY25['gaap_holder'] / 100:.2f}亿元"
        f"（VL 统计表按调整口径列为 {_fmt(holder, 2)}亿元），"
        f"但该亏损主要来自上市时可转换可赎回优先股公允价值变动 {FY25['pref_loss'] / 100:.2f}亿元的非现金项目；"
        f"公司披露的经调整净利润为{FY25['adj_np'] / 100:.2f}亿元（来源：2025年报 p8、p14）。"
        f"期末员工{FY25['employees']:,}人（来源：2025年报 p19）。"
    )

    # ── P1 经营分析：这一轮变化是「收入增速远高于成本增速」的经营杠杆 ──
    p1 = (
        f"{yr}年收入{_fmt(rev, 2)}亿元（同比{FY25['rev_yoy']:+.1f}%）"
        + f"，而销售成本仅增{FY25['cost_yoy']:.1f}%、销售及营销开支增{FY25['sales_yoy']:.1f}%、"
        f"研发开支增{FY25['rd_yoy']:.1f}%，毛利率由 68.5% 升至{FY25['gross_margin']:.1f}%"
        "（来源：2025年报 p12-13）。"
    )
    p1 += (
        f"经营收入从 {FY25['op_income_py'] / 100:.2f}亿元转为 {FY25['op_income'] / 100:.2f}亿元，"
        f"经调整净利润从 {FY25['adj_np_py'] / 100:.2f}亿元升至 {FY25['adj_np'] / 100:.2f}亿元"
        "（来源：2025全年业绩公告、年报 p8）。"
    )
    p1 += (
        f"量的扩张与价的抬升同时发生：SaaS 客户数{FY25['customers_py_k']:.1f}千 → {FY25['customers_k']:.1f}千，"
        f"处理订单 {FY25['orders_bn']:.1f}十亿笔，每笔订单的 SaaS 收入 {FY25['rev_per_order']:.4f}元、同比 +7.1%"
        "（来源：2025年报 p12）。"
    )
    p1 += (
        f"2026 上半年收入 {H1_26['rev'] / 100:.2f}亿元（同比 +{H1_26['rev_yoy']:.1f}%）、"
        f"毛利率 {H1_26['gross_margin']:.1f}%、归母净利 {H1_26['holder_profit'] / 100:.2f}亿元，"
        f"说明上市后经营杠杆延续而非一次性（来源：2026中期业绩公告 p1、p20、p22）。"
    )

    # ── P2 现金流与资本配置：预收款 + 佣金资本化是这门生意的现金结构 ──
    p2 = (
        f"{yr}年经营活动所得现金净额 {FY25['ocf'] / 100:.2f}亿元，"
        f"是同期经调整净利润 {FY25['adj_np'] / 100:.2f}亿元的 {FY25['ocf'] / FY25['adj_np']:.1f} 倍"
        "（🟡 比值由两个披露数相除，来源：2025全年业绩公告）。"
    )
    p2 += (
        f"差额主要来自客户预付款：2025年末合约负债 {FY25['contract_liab'] / 100:.2f}亿元，"
        f"同时把支付给销售团队与代理商的佣金资本化为合约获取成本 {FY25['cac'] / 100:.2f}亿元，"
        "随收入确认分期摊销（来源：2026中期业绩公告 p9-10、2025年报 p17）。"
        "换言之，利润表上的收入确认滞后于现金流入，这是订阅制 SaaS 与项目制软件的根本差别。"
    )
    p2 += (
        f"上市募资后现金及现金等价物 {FY25['cash'] / 100:.2f}亿元，"
        f"2026 年中期宣派每股 0.17 元人民币（相当于 0.20 港元）股息"
        "（来源：2025年报 p17、2026中期业绩公告 p1）。"
        "公司上市仅一年，分红与回购尚未形成可验证的政策，资本配置仍待观察。"
    )

    # ── P3 盈利质量与护城河：GAAP 亏损不是经营亏损 ──
    p3 = (
        f"必须把两套口径分开：{yr}年 GAAP 归母净利 {FY25['gaap_holder'] / 100:.2f}亿元，"
        f"其中可转换可赎回优先股公允价值亏损 {FY25['pref_loss'] / 100:.2f}亿元，"
        "成因是上市后估值大幅上升，该工具已于上市时自动转为普通股，不产生现金流出"
        "（来源：2025年报 p14、2026中期业绩公告 p22）；"
        f"2026 上半年该项为零，归母净利随即转正为 {H1_26['holder_profit'] / 100:.2f}亿元。"
    )
    p3 += (
        "护城河不在单项功能，而在与 400 余家电商平台、800 余家物流服务商的对接和商家内部流程的沉淀："
        f"单笔订单的 SaaS 收入只有 {FY25['rev_per_order']:.4f}元，客户极度分散、单客户议价力弱，"
        "但 ERP 一旦承载订单与库存主数据，切换要重做流程与培训，迁移成本远高于年费"
        "（🟡 后半句为基于业务性质的推断，非年报原话）。"
    )
    p3 += (
        f"另一个被低估的变化是收入质量：招股章程披露 SaaS 收入中按年度订阅的占比由 2022 年 "
        f"{SUB_MIX_2022:.1f}% 升至 2024 年 {SUB_MIX_2024:.1f}%，按处理订单量计费的占比相应下降，"
        "收入对单量波动的敏感度在降低（来源：招股章程 p8）。"
    )

    # ── P4 估值：CF 15x 在本标的上不可用，必须说清而不是给个假锚 ──
    p4 = f"当前股价 {_fmt(price, 2)} 港元，每股净资产 {_fmt(bps, 2)} 元"
    if pb:
        p4 += f"，PB 约 {_fmt(pb, 2)}x"
    p4 += "。"
    if per_cf <= 0:
        p4 += (
            f"本报告按用户指定的 CF×15.0 口径绘制估值线，但 VL 的每股现金流取「扣非净利 + 折旧」，"
            f"{yr}年该值为 {_fmt(per_cf, 2)} 元/股（受前述优先股公允价值亏损污染），"
            "由此得到的 CF 估值线为负、不具估值含义，不应作为买卖参考；"
            "这是引擎既定口径，此处只标注不改写。"
        )
    else:
        p4 += (
            f"CF×15.0 对应每股 {_fmt(per_cf * 15.0, 2)} 元，"
            "但该口径的分母包含上市前一次性项目，仍需与经调整净利口径并列判断。"
        )
    p4 += (
        f"以年报经调整净利润 {FY25['adj_np'] / 100:.2f}亿元衡量经营盈利能力更贴近实际，"
        "但引擎的历史 PE / PE 均值样本仅覆盖上市后 13 个月，且 2025 年 GAAP 每股亏损使 TTM 滚动无有效输入，"
        "因此本页 P/E、EPS(TTM)、PE 均值与 PE 相对值留白属预期内的数据缺口，不是计算错误"
        "（🟡 依据引擎口径与 2025 年报 EPS -7.27 元）。"
    )
    if dps:
        p4 += f"每股分红 {_fmt(dps, 2)} 元、股息率 {_pct(div_y)}，均为 2026 中期单次派息，尚不能年化。"

    # ── P5 催化剂与风险 ──
    p5 = (
        f"后续看点：①协同产品 {yr}年收入增速 {FY25['collab_yoy']:.1f}%、2026 上半年 "
        f"{H1_26['collab_yoy']:.1f}%，是 ERP 之外的第二增长曲线（来源：2025年报 p10、2026中期业绩公告 p19）；"
        f"②东南亚收入 {FY25['sea_rev_py']:.1f} → {FY25['sea_rev']:.1f}百万元、同比 +119.0%，"
        "2026 上半年已设马来西亚、越南子公司（来源：2025年报 p11、2026中期业绩公告 p18）；"
        "③AI 智能体「水宝」与业财合规产品的商业化进度（来源：2026中期业绩公告 p18）。"
    )
    p5 += (
        "主要风险：电商行业流量红利消退会直接压低商家数量与订单量；客户高度分散虽降低集中度风险，"
        "但也意味着单客 ARPU 低、需要持续的地推与代理佣金投入；"
        "汇兑损益与政府补助在非经营项里波动明显（2026 上半年其他亏损 64.9 百万元，"
        "来源：2026中期业绩公告 p21）；此外上市仅 13 个月，历史财务与估值序列短，"
        "本页 15 年统计表的大量空白属客观数据边界。"
    )
    p5 += (
        "跟踪信号：SaaS 客户数与处理订单量的增速差、每笔订单 SaaS 收入、订阅收入占比、"
        "合约负债余额增速、经调整净利率与经营现金流的比值。"
    )

    return {"business": biz, "commentary": [p1, p2, p3, p4, p5]}
