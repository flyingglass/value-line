# -*- coding: utf-8 -*-
"""宝信软件 600845 — VL Business + AI Commentary（手工精修版）

数据来源约定（CODEBUDDY.md「投研数据」）：
  - metrics / revenue_structure / cagr / spot 全部来自 report_data.json（DB）
  - DB 中不存在的数字（关联销售占比、分部毛利率、在建工程等）一律标注一手来源
    （2025 年报 / 2026 中报），不做估算
口径提醒：
  - metrics.HOLDER_PROFIT 为 A 股**扣非**口径（2025 = 12.1 亿，年报归母 13.05 亿）
  - metrics.PER_NETCASH 为 VL 口径「扣非净利 + 折旧」，**不是**现金流量表经营现金流
    （2025 年报经营现金流净额 21.47 亿，须分开表述）
"""


def build(stock, metrics, revenue_structure, years, cagr, spot):
    name = stock.get("name", "宝信软件")
    ly = metrics.get(years[-1], {}) if years else {}
    py = metrics.get(years[-2], {}) if len(years) >= 2 else {}

    def _n(v, d=0.0):
        try:
            return float(v)
        except (TypeError, ValueError):
            return d

    def _f(v, d=1):
        try:
            return f"{float(v):,.{d}f}"
        except (TypeError, ValueError):
            return "-"

    def _pct(v, d=1):
        try:
            return f"{float(v):+.{d}f}%"
        except (TypeError, ValueError):
            return "-"

    def _cg(key, span):
        try:
            return cagr.get(key, {}).get(span)
        except AttributeError:
            return None

    rev = _n(ly.get("OPERATE_INCOME"))
    npd = _n(ly.get("HOLDER_PROFIT"))          # 扣非口径
    gm = _n(ly.get("GROSS_MARGIN"))
    npm = _n(ly.get("NET_PROFIT_RATIO"))
    roe = _n(ly.get("ROE"))
    roic = _n(ly.get("ROIC"))
    dps = _n(ly.get("DPS"))
    payout = _n(ly.get("PAYOUT_RATIO"))
    bps = _n(ly.get("BPS"))
    per_cf = _n(ly.get("PER_NETCASH"))
    capex_ps = _n(ly.get("CAPEX_PS"))
    capex_py = _n(py.get("CAPEX_PS"))
    lt_debt = _n(ly.get("LT_DEBT"))
    tot_eq = _n(ly.get("TOTAL_EQUITY"))

    price = _n(spot.get("price"))
    pe = _n(spot.get("pe"))
    pb = _n(spot.get("pb"))
    div_y = _n(spot.get("div_yield"))
    med_pe = _n(spot.get("median_pe"))
    mkt_cap = _n(spot.get("mkt_cap"))

    r1 = _cg("revenue", "1yr")
    r5 = _cg("revenue", "5yr")
    e1 = _cg("eps", "1yr")
    cf5 = _cg("cashflow", "5yr")

    prod = (revenue_structure or {}).get("by_product", []) or []
    prod_txt = "、".join(f"{r['name']} {r['pct']:.1f}%" for r in prod) if prod else "—"
    prod_lead = f"{prod[0]['pct']:.1f}%" if prod else "约三分之二"

    cf15 = per_cf * 15
    cf20 = per_cf * 20
    implied = (price / per_cf) if per_cf else 0

    # ── Business：公司概述 + 最新年核心数据 ──
    business = (
        f"{name}是中国宝武钢铁集团旗下的信息高科技公司，实际控制人为中国宝武，"
        f"控股股东宝钢股份持股 49.34%。业务按披露口径分三类：软件开发及工程服务（钢铁及流程行业数智化解决方案）、"
        f"服务外包（信息系统运维、云计算与宝之云 IDC 运营）、系统集成（硬件销售）。"
        f"2025 年营业收入 {_f(rev)} 亿元（{_pct(r1)}），毛利率 {_f(gm)}%，ROE {_f(roe)}%，"
        f"扣非归母净利润 {_f(npd)} 亿元（{_pct(e1)}）；营收结构为 {prod_txt}。"
        f"公司正从信息化服务商向工业智能与算力运营商转型：2025 年末在建工程约 17.6 亿元、"
        f"其中宝之云系占九成（来源：2025 年报）。"
    )

    # ── P1 经营分析 ──
    p1 = (
        f"2025 年营收 {_f(rev)} 亿、同比 {_pct(r1)}，为近十五年最大年度降幅（次深的 2015 年仅 -3.2%，"
        f"来源：DB 年度序列 2011-2025），营收 5 年复合增速降至 {_f(r5)}%。降幅高度集中在项目型业务："
        f"年报披露「软件开发及工程服务」收入 -27.7%，而「服务外包」仍 +3.0%（来源：2025 年报 p11）。"
        f"两块业务性质完全不同——前者是工程交付（集团统一编码／MES／ERP 等一次性统建），"
        f"后者是运维与 IDC 的按年收费。"
        f"客户侧印证同一结论：宝武系关联销售 2022 年见顶 74.5 亿后连跌三年至 2025 年 61.2 亿（-17.9%）、"
        f"占营业收入 55.75%；其中马钢系从 2021 年 12.4 亿落到 2.7 亿、太钢系从 2023 年 7.4 亿落到 1.9 亿，"
        f"是典型的「统建做完即止」（来源：2019-2025 年报附注十四）。"
        f"2026 上半年营收回升 +19.5%、归母 +22.97%（来源：2026 中报），但同期山钢日照关联销售已同比 -39%，"
        f"新一批整合红利的持续性仍需观察。"
    )

    # ── P2 现金流与资本配置 ──
    p2 = (
        f"2025 年经营现金流净额 21.47 亿元、同比 +28.5%（来源：2025 年报）；但收现端已在收缩——"
        f"2026 上半年销售商品提供劳务收到的现金 57.67 亿元、同比 -7.3%，收现比降至 1.02，"
        f"合同负债 28.65 亿元、同比 -9.3%（来源：2026 中报），说明收入增长在消耗既有预收。"
        f"VL 口径每股现金流（扣非净利＋折旧）{_f(per_cf, 2)} 元、5 年复合增速 {_f(cf5)}%，"
        f"与经营现金流不是同一口径，两者须分开看。资本配置正转向重资产：每股资本开支从 2024 年 "
        f"{_f(capex_py, 2)} 元升至 2025 年 {_f(capex_ps, 2)} 元（约 3 倍），当年在建工程新增 7.16 亿元、"
        f"主要投向宝之云华北基地（来源：2025 年报 p11-12）。分红方面，2025 年度每 10 股派 2.30 元、"
        f"合计 6.60 亿元、占归母净利 50.60%（来源：2025 年报），对应股息率 {_f(div_y, 2)}%、"
        f"分红率 {_f(payout)}%；每股分红 {_f(dps, 2)} 元（DB 口径，2023／2024 年度为 1.00／0.60 元）。"
        f"杠杆极轻：长期借款 {_f(lt_debt, 1)} 亿元、归母权益 {_f(tot_eq, 1)} 亿元，扩张主要靠自身现金流。"
    )

    # ── P3 盈利质量与护城河 ──
    p3 = (
        f"毛利率 {_f(gm)}%、净利率 {_f(npm)}%、ROE {_f(roe)}%、ROIC {_f(roic)}%，盈利水平在软件同业中偏低，"
        f"根因是收入结构：项目工程占 {prod_lead}，而该分部毛利率仅 25.78%；真正高毛利的「服务外包」"
        f"（含 IDC 与运维）毛利率 42.96%（来源：2025 年报 p11）。护城河有三层：①制度性——中国宝武与宝钢股份"
        f"2013 年出具、无固定期限的承诺函，体系内新增 IT 需求优先给予公司（触发条件为宝钢集团持股不低于 30%，"
        f"现为 49.34%；来源：2026 中报「承诺事项」）；②网络性——87 个行业、8 万余家客户与全国 200 多个城市的"
        f"本地化服务能力（来源：2026 中报）；"
        f"③技术性——全栈国产化控制系统（天行 PLC）、宝联登工业互联网平台与钢铁行业大模型。"
        f"风险同样明确：宝武系贡献过半收入，其资本开支周期直接决定公司收入节奏；关联交易定价为「市场价或协议价」，"
        f"客户盈利收窄会向公司传导——2025 年软件开发及工程服务毛利率下滑 5.36 个百分点即是显影。"
    )

    # ── P4 估值分析 ──
    p4 = (
        f"当前市值 {_f(mkt_cap)} 亿元、PE {_f(pe)} 倍、PB {_f(pb, 2)} 倍、股息率 {_f(div_y, 2)}%，"
        f"PE 高于历史中位 {_f(med_pe)} 倍。按 VL 的 CF 口径：每股现金流 {_f(per_cf, 2)} 元，"
        f"CF=15x 对应 {_f(cf15, 2)} 元、CF=20x 对应 {_f(cf20, 2)} 元，均显著低于现价 {_f(price, 2)} 元——"
        f"现价隐含 CF 倍数约 {_f(implied)} 倍。这个结果本身值得警惕：CF 口径的分子是「扣非净利＋折旧」，"
        f"2025 年扣非净利 -44.8% 使分子处于周期低点，而公司同时进入资本开支高峰期（每股资本开支 0.15→0.46 元），"
        f"折旧将逐年抬升、对应收入要等宝之云转固上架后才释放。因此在盈利低点用 CF 15x 会系统性低估，"
        f"而按当前盈利水平看估值又不便宜——估值锚落在「服务外包能否放量」这一个变量上。"
        f"PB {_f(pb, 2)} 倍对应每股净资产 {_f(bps, 2)} 元，可作为重资产化阶段的对照口径。"
    )

    # ── P5 催化剂与风险 ──
    p5 = (
        f"催化剂：①宝之云 IDC 转固放量——2025 年末在建工程约 17.6 亿元（宝之云系占九成），"
        f"华北基地 A4/A5/A6 楼等进入交付期，若上架率提升将直接抬升服务外包收入与毛利；"
        f"②集团整合红利延续——山钢、新余钢铁 2025 年关联销售分别升至 4.57 亿、4.27 亿，仍在上升段"
        f"（来源：2025 年报附注十四）；③AI 落地——宝武「2526」工程、钢铁行业大模型与 AI 场景铺开。"
        f"风险：①宝武系资本开支收缩——2025 年营收 -19.6% 已经发生，且体系外收缩更快（非关联收入 -27.8%）；"
        f"②项目毛利率继续下探（工程与集成竞争加剧）；③折旧刚性——资本开支高峰对应的折旧将先于收入体现。"
        f"跟踪三个读数：服务外包收入增速（现 +3.0%／2026H1 +6.7%）、软件开发及工程服务毛利率（现 25.78%）、"
        f"以及关联销售占营业收入比重（现 55.75%）。"
    )

    return {"business": business, "commentary": [p1, p2, p3, p4, p5]}
