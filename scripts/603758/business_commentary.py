# -*- coding: utf-8 -*-
"""秦安股份 603758 — VL Business + AI Commentary（数据驱动, 手工精调）
口径说明: VL 净利润/每股收益采用扣非口径 (2025 扣非归母 1.41 亿 / 每股 0.33 元),
年报披露归母口径 1.49 亿 / EPS 0.35 元 (2024 年扣非 2.01 亿 反而 > 归母 1.73 亿, 因股票公允价值变动为负)。
文内以扣非口径为主数字, 归母口径另行注明。最新财年(2025)同比增速用年报 PDF 精确披露值硬编码。
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
    def _dir(c, p):
        v = _chg(c, p)
        if v is None: return "持平"
        return "增长" if v > 0.05 else ("下降" if v < -0.05 else "基本持平")
    def _num(v):
        try: return float(v)
        except: return 0
    def _fmt(v, d=0):
        try: return f"{float(v):,.{d}f}"
        except: return "-"
    def _p(v):
        try: return f"{float(v):+.1f}%"
        except: return "-"

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
    price = _num(spot.get("price", 0))
    pe = _num(spot.get("pe", 0))
    pb = _num(spot.get("pb", 0))
    div_y = _num(spot.get("div_yield", 0))
    med_pe = spot.get("median_pe")
    r_chg = _chg(rev, py.get("OPERATE_INCOME"))
    n_chg = _chg(np_val, py.get("HOLDER_PROFIT"))
    r_abs = abs(r_chg) if r_chg is not None else 0
    n_abs = abs(n_chg) if n_chg is not None else 0
    r_dir = _dir(rev, py.get("OPERATE_INCOME"))
    n_dir = _dir(np_val, py.get("HOLDER_PROFIT"))

    # 营收结构 (value 单位: 百万元)
    prod_data = revenue_structure.get("by_product", []) if isinstance(revenue_structure, dict) else []
    prod_parts = [f"{r['name']}{r['pct']:.1f}%" for r in prod_data] if prod_data else []
    prod_str = "、".join(prod_parts)
    reg_data = revenue_structure.get("by_region", []) if isinstance(revenue_structure, dict) else []

    # ── Business 段 ──
    biz = (
        "秦安股份（重庆秦安机电，2017年上交所上市）是国内规模居前的汽车轻量化结构件专业供应商，"
        "铸造+机加一体化，主营汽车发动机核心零部件（缸盖、缸体、曲轴）与变速器关重零部件（箱体/壳体及混动变速器箱体），"
        "并延伸至增程式发动机缸盖缸体、纯电动车电机壳体，覆盖燃油/混动/纯电车型，采用订单式生产，"
        "主要客户为长安福特、理想汽车、中国一汽、吉利、长安、江铃等主流整车及动力平台企业；"
        "2024年直供北美福特发动机缸体，2025年持续稳定量产、出口收入实现翻倍。"
        "2025年12月完成对亦高光电99%股权收购，切入高端真空镀膜（超硬镀膜/AR镀膜/NCVM/电致变色玻璃），"
        "应用于手机、智能穿戴、车载屏与AR眼镜，形成汽车零部件+真空镀膜双主业布局。"
    )
    biz += f"2025年营收{_fmt(rev, 2)}亿元（同比-15.5%），净利润（扣非口径）1.41亿元（同比-29.7%，年报归母1.49亿元、-13.6%），毛利率{gm:.1f}%（同比降约3.3pp），ROE {roe:.1f}%。"
    if prod_str:
        biz += f"产品结构：{prod_str}。"
    if reg_data:
        reg_parts = [f"{r['name']}占{r['pct']:.1f}%" for r in reg_data]
        biz += "分地区：" + "，".join(reg_parts) + "。"

    # ── P1: 业绩快照 + 趋势 ──
    p1 = f"2026年9月 — 秦安股份2025年营收{_fmt(rev, 2)}亿元（同比-15.5%，年报口径-15.48%），扣非净利润1.41亿元（同比-29.7%，年报-29.66%），"
    p1 += f"归母净利润1.49亿元（-13.56%）；毛利率{gm:.1f}%（同比-3.3pp），净利率{npm:.1f}%，ROE {roe:.1f}%、ROIC {roic:.1f}%。"
    p1 += "这是业绩连续第二年回落：营收从2023年17.4亿元降至2025年13.5亿元，主因行业竞争加剧致部分产品降价、销量下滑（缸盖销量-20.9%、缸体-16.4%），"
    p1 += "叠加铝、铜等大宗原材料采购均价上涨（铝+3.8%、铜+7.9%）侵蚀毛利率。经营质量方面，经营现金流净额2.70亿元（-33.5%）仍大幅高于净利，财务结构稳健。"
    p1 += "2025年不分红，资金优先用于亦高光电收购整合与产能建设。"

    # ── P2: 现金流与资本配置 ──
    p2 = f"每股收益（扣非）{_fmt(eps, 2)}元，每股经营现金流{_fmt(per_cf, 2)}元，每股资本开支{_fmt(per_capex, 2)}元"
    if per_cf:
        p2 += f"（资本开支占经营现金流约{per_capex / per_cf * 100:.0f}%，含亦高光电并购与镀膜产线投入）"
    p2 += f"，每股净资产{_fmt(bps, 2)}元。2025年度不分红（2023-2024年曾连续分红、支付率曾超60%）。"
    p2 += "账面货币资金与交易性金融资产合计11.34亿元、现金比率138%，但因收购亦高光电引入并购贷款，"
    p2 += "资产负债率由2024年末17.35%升至2025年末33.96%，总资产38.98亿元；短期无偿债压力，长期资金主要投向双主业扩张。"

    # ── P3: 盈利质量与护城河 ──
    p3 = f"毛利率{gm:.1f}%在汽零行业属中等水平且呈下行通道（2023年27.5%→2024年23.9%→2025年20.7%），净利率{npm:.1f}%、ROE {roe:.1f}%、ROIC {roic:.1f}%。"
    p3 += "护城河：①客户认证与供货壁垒——发动机缸体/缸盖等安全件认证周期长，一旦定点供货生命周期可达8-10年，公司以长安福特、理想、一汽等核心客户为基本盘；"
    p3 += "②铸造+机加一体化——自制毛坯压缩成本、响应快，年交付百万件级规模；③出口突破——直供北美福特缸体并持续放量，打开全球配套空间。"
    p3 += "风险：燃油车产业链收缩（2025年产销双降、销量合计-19.8%）、产品降价与原材料上涨双重挤压毛利率、新业务整合存在不确定性。"

    # ── P4: 估值锚定 ──
    cf_15x = per_cf * 15 if per_cf else 0
    cf_20x = per_cf * 20 if per_cf else 0
    p4 = f"当前价{_fmt(price, 2)}元，PE（TTM）约{_fmt(pe, 1)}倍"
    if med_pe:
        p4 += f"，高于上市以来中位{_fmt(med_pe, 1)}倍" if pe and pe > med_pe else f"，低于上市以来中位{_fmt(med_pe, 0)}倍"
    p4 += f"，PB {_fmt(pb, 2)}倍，股息率{div_y:.1f}%（2025年度不分红）。"
    if per_cf and price:
        implied = price / per_cf if per_cf else 0
        p4 += f"CF估值法：每股经营现金流{_fmt(per_cf, 2)}元，CF=15x对应{_fmt(cf_15x, 1)}元、CF=20x对应{_fmt(cf_20x, 1)}元，当前股价隐含CF倍数约{implied:.0f}倍，略高于15x锚。"
        p4 += f"以扣非净利1.41亿、当前市值约{_fmt(spot.get('mkt_cap', 0), 1)}亿元衡量，静态估值不便宜，"
        p4 += "PE（TTM）显著高于上市以来中位，市场已部分定价真空镀膜第二曲线与北美出口预期，需业绩兑现消化。"

    # ── P5: 催化剂与风险 ──
    p5 = ("催化剂：①亦高光电并表——2025年12月完成99%股权收购，业绩承诺2025-2027累计净利润不低于2.4亿元，"
          "2026年起贡献并表利润与高端镀膜第二曲线（手机/车载/AR眼镜）；"
          "②海外放量——北美福特缸体稳定量产基础上，探索福特全球其他区域及新海外车企合作，出口占比有望继续提升；"
          "③新能源项目落地——混动驱动系统总成、电机壳体等新项目按计划推进，增程式/混动专用件对冲燃油车下滑；"
          "④新客户订单——东安动力等新客户落地，终端覆盖尊界、小鹏、岚图等。")
    p5 += "验证信号：跟踪季度营收同比是否止跌、综合毛利率能否企稳在20%以上、亦高光电单季收入与利润兑现、经营现金流回款节奏。风险：燃油车景气继续下行、价格战、铝铜成本上涨、并购整合与商誉减值、新业务投产爬坡不及预期。"

    return {"business": biz, "commentary": [p1, p2, p3, p4, p5]}
