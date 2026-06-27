# -*- coding: utf-8 -*-
"""
generate_business_commentary.py — 自动生成个股专属 business_commentary.py
读取 config + DB 数据, 输出数据驱动的 5 段 Commentary 模板。
moat (P3) 和 catalysts (P5) 按行业提供初稿, 可后续手动精调。

用法:
    python generate_business_commentary.py 600298
    python generate_business_commentary.py 01579
"""
import os, sys, sqlite3, json

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config

# ── 行业专属 moat 模板 (P3 段) ──
INDUSTRY_MOAT = {
    "Consumer Staples": (
        "消费品核心壁垒：①品牌心智占位——多年积累的消费者认知形成复购惯性；"
        "②渠道网络密度——深度分销覆盖终端, 竞品短期难以复制；"
        "③规模效应——采购议价力+固定成本摊薄构成成本护城河。"
        "风险：原材料价格波动、消费降级趋势、新渠道分流。"
    ),
    "Consumer": (
        "消费品核心壁垒：①品牌IP与用户粘性——粉丝经济驱动复购；"
        "②全球化渠道——直营+经销覆盖多国, 本地化运营降低风险；"
        "③供应链效率——柔性生产+快反补货。"
        "风险：IP生命周期衰减、海外政策风险、竞争加剧。"
    ),
    "Technology": (
        "科技行业核心壁垒：①技术领先与研发投入——持续高研发构建专利护城河；"
        "②生态锁定——平台/云服务的高迁移成本；"
        "③数据网络效应——用户规模越大产品越好。"
        "风险：技术迭代风险、地缘政治制裁、估值波动。"
    ),
    "Energy": (
        "能源行业核心壁垒：①资源禀赋——低成本储量/产能不可复制；"
        "②规模优势——全球布局摊薄开采成本；"
        "③政策牌照——上游勘探开采权构成准入壁垒。"
        "风险：油价/气价周期波动、能源转型政策、地缘政治。"
    ),
    "Metals & Mining": (
        "金属矿业核心壁垒：①资源储量与品位——优质矿权稀缺且不可再生；"
        "②一体化成本优势——采选冶+电力自给降低完全成本；"
        "③产能规模——大规模冶炼摊薄固定成本。"
        "风险：大宗商品价格周期、环保限产、电价上涨。"
    ),
    "Media": (
        "传媒行业核心壁垒：①点位/流量垄断——高密度覆盖构建渠道网络效应；"
        "②品牌客户粘性——大客户长期合约+数据投放能力；"
        "③轻资产高现金流——资本支出少、现金流转化率高。"
        "风险：宏观经济下行广告预算削减、新媒体分流、监管政策。"
    ),
    "Semiconductor": (
        "半导体行业核心壁垒：①制程工艺+专利墙——先进制程需十年以上积累；"
        "②资本密度——单厂投资百亿美元级别, 新进入者门槛极高；"
        "③客户认证——车规/工规认证周期长达2-3年。"
        "风险：地缘政治制裁、行业周期下行、技术路线切换。"
    ),
    "Packaging": (
        "包装行业核心壁垒：①客户粘性——食品/日化大客户长期合作, 转换成本高；"
        "②就近配套——属地化产能降低物流成本, 形成区域壁垒；"
        "③技术工艺——多层共挤/高阻隔等专有技术。"
        "风险：原材料价格波动、下游需求疲软、环保法规趋严。"
    ),
    "Automotive": (
        "汽车行业核心壁垒：①品牌+渠道——经销商网络深度和品牌认知；"
        "②规模效应——百万级销量摊薄研发和模具成本；"
        "③技术迭代——电动化/智能化领先者享受先发优势。"
        "风险：价格战、技术路线不确定性、海外贸易壁垒。"
    ),
    "Home Appliances": (
        "家电行业核心壁垒：①品牌+渠道——全渠道覆盖和售后网络；"
        "②智能制造——自动化产线降低人工成本；"
        "③全球化——海外建厂规避关税壁垒。"
        "风险：房地产周期、原材料涨价、海外需求波动。"
    ),
    "Pharmaceuticals": (
        "医药行业核心壁垒：①研发管线+专利保护——创新药专利期内垄断定价；"
        "②临床数据+审批壁垒——新药上市周期长达8-12年；"
        "③医保准入+渠道覆盖——进入医保目录意味着确定性的量。"
        "风险：集采降价、研发失败、专利到期。"
    ),
    "Healthcare": (
        "医疗健康核心壁垒：①牌照/认证——医疗器械注册证、医院牌照稀缺；"
        "②医生/患者习惯——医疗器械和药品的处方惯性；"
        "③技术壁垒——精密制造和临床数据积累。"
        "风险：集采政策、医保控费、产品召回。"
    ),
    "Building Materials": (
        "建材行业核心壁垒：①资源禀赋——优质矿山/石灰石资源不可再生；"
        "②运输半径——水泥/商混等受运距限制, 属地化产能形成自然垄断；"
        "③规模成本——大规模产线单位成本更低。"
        "风险：房地产/基建需求下行、环保限产、煤炭/电力涨价。"
    ),
    "Insurance": (
        "保险行业核心壁垒：①牌照稀缺——金融牌照审批严格；"
        "②代理人/银保渠道——大规模销售队伍难以短期复制；"
        "③精算+投资能力——长期资产负债匹配管理经验。"
        "风险：利率下行压缩利差、保费增速放缓、巨灾赔付。"
    ),
    "Financial Services": (
        "金融服务核心壁垒：①牌照与监管准入——金融牌照审批严格；"
        "②客户信任+资金规模——规模越大资金成本越低；"
        "③风控体系——长期积累的信用评估模型。"
        "风险：信用风险暴露、利差收窄、监管政策收紧。"
    ),
    "Utilities": (
        "公用事业核心壁垒：①垄断经营权——区域特许经营不可替代；"
        "②重资产壁垒——电网/管网/水库投资巨大；"
        "③稳定现金流——刚需+政府定价保障收入确定性。"
        "风险：电价/水价调整滞后、新能源替代、资本开支压力。"
    ),
}

# ── 行业专属 catalyst 模板 (P5 段) ──
INDUSTRY_CATALYST = {
    "Consumer Staples": (
        "催化剂：①提价+产品结构升级——高端化/功能化产品占比提升驱动毛利率改善；"
        "②产能释放——新建产能投产带来量的增长；"
        "③渠道下沉/出海——空白市场覆盖带来增量空间。"
        "风险：原材料成本若大幅上涨将压缩毛利；消费疲软导致销量不及预期。"
        "关注每季度毛利率趋势和分品类收入增速作为核心信号。"
    ),
    "Consumer": (
        "催化剂：①新产品/新IP放量——爆款产品周期驱动业绩弹性；"
        "②海外扩张——新兴市场渠道铺设带来增量；"
        "③品牌升级——提价+高端线提升利润中枢。"
        "风险：IP热度消退、海外政策风险。关注每季度同店增速和新品贡献率。"
    ),
    "Technology": (
        "催化剂：①AI/新技术落地——新产品周期驱动增长加速；"
        "②份额提升——竞争对手退出或技术替代带来市场集中；"
        "③利润率改善——规模效应+高毛利业务占比提升。"
        "风险：技术路线变化、制裁升级。关注每季度新业务收入占比和研发转化率。"
    ),
    "Energy": (
        "催化剂：①产量增长+新油田投产——产能释放驱动量的增长；"
        "②成本下降——技术优化降低桶油成本；"
        "③分红/回购——高现金流向股东回馈。"
        "风险：油价大幅下跌、资源国政策变化。关注每季度桶油成本和产量指引。"
    ),
    "Metals & Mining": (
        "催化剂：①商品价格上行——供需缺口驱动价格上涨；"
        "②产能扩张——新建项目投产带来产量增长；"
        "③成本优化——电力/原材料自给率提升。"
        "风险：商品价格周期下行、环保限产。关注每季度完全成本和产量。"
    ),
    "Media": (
        "催化剂：①点位扩张——新城市/新场景覆盖带来广告库存增长；"
        "②刊例价提升——品牌广告主预算回流线下媒体；"
        "③海外拓展——东南亚/中东等新兴市场复制模式。"
        "风险：宏观经济下行广告主削减预算。关注每季度单屏收入和点位利用率。"
    ),
    "Semiconductor": (
        "催化剂：①新产线投产——产能扩张驱动量的增长；"
        "②国产替代——地缘政治加速国产芯片渗透率提升；"
        "③ASP提升——先进制程/高端产品占比提高。"
        "风险：行业周期下行、制裁升级。关注每季度产能利用率和ASP趋势。"
    ),
    "Packaging": (
        "催化剂：①新产品/新客户导入——头部品牌客户订单放量；"
        "②原材料降价——塑料粒子价格下行利好毛利；"
        "③产能利用率提升——需求回暖驱动开工率上升。"
        "风险：原材料价格反弹、下游需求疲软。关注每季度毛利率和新客户导入进度。"
    ),
    "Pharmaceuticals": (
        "催化剂：①新药获批/放量——重磅品种上市驱动业绩拐点；"
        "②集采中标——以量补价, 市场份额快速提升；"
        "③国际化——ANDA/FDA获批打开海外市场。"
        "风险：集采降价超预期、研发失败、专利到期。关注每季度核心品种增速。"
    ),
}

# ── 通用默认模板 ──
DEFAULT_MOAT = (
    "核心壁垒：①规模与成本优势——行业领先产能带来的采购议价力和固定成本摊薄；"
    "②渠道/客户粘性——长期合作和转换成本构成护城河；"
    "③技术/品牌积累——多年研发/品牌建设形成先发优势。"
    "风险：行业竞争加剧、原材料价格波动、宏观经济下行。"
)
DEFAULT_CATALYST = (
    "催化剂：①产能释放——新建项目投产带来增量；"
    "②需求回暖——下游景气度回升驱动量价齐升；"
    "③利润率改善——降本增效+产品结构优化。"
    "风险：需求不及预期、成本上升、行业竞争加剧。"
    "关注每季度收入增速和毛利率趋势作为核心信号。"
)


def generate(code):
    """生成 scripts/<code>/business_commentary.py"""
    stock = config.STOCKS.get(code)
    if not stock:
        print(f"[ERROR] {code} 不在 config.STOCKS 中")
        return False

    name = stock.get("name", code)
    industry = stock.get("industry", "")
    business_desc = stock.get("business_desc", "").strip()

    out_dir = os.path.join(BASE, "scripts", code)
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "business_commentary.py")

    if os.path.exists(out_path):
        print(f"[SKIP] {out_path} 已存在, 不覆盖")
        return True

    # ── 营收结构摘要 ──
    db_path = os.path.join(BASE, "data", f"{code}.db")
    prod_summary = ""
    reg_summary = ""
    if os.path.exists(db_path):
        try:
            conn = sqlite3.connect(db_path)
            rows = conn.execute(
                "SELECT dim_name, pct FROM revenue_structure WHERE code=? AND dim_type='by_product' ORDER BY pct DESC",
                (code,)
            ).fetchall()
            if rows:
                parts = [f"{r[0]}{r[1]:.0f}%" for r in rows[:4]]
                prod_summary = "、".join(parts)
            rows2 = conn.execute(
                "SELECT dim_name, pct FROM revenue_structure WHERE code=? AND dim_type='by_region' ORDER BY pct DESC",
                (code,)
            ).fetchall()
            if rows2:
                parts2 = [f"{r[0]}{r[1]:.0f}%" for r in rows2]
                reg_summary = "、".join(parts2)
            conn.close()
        except:
            pass

    # ── 业务描述 ──
    if business_desc:
        # 取前两句作为 business 核心叙事
        biz_lines = business_desc.split("。")
        biz_core = "。".join(biz_lines[:2]) + "。"
        if len(biz_core) < 50 and len(biz_lines) >= 3:
            biz_core = "。".join(biz_lines[:3]) + "。"
        biz = (
            f"biz=f\"{biz_core}\""
            f" + " + (f'f"营收{{_fmt(rev,0)}}亿（同比{{_dir(rev,py.get(\"OPERATE_INCOME\"))}}{{r_abs:.1f}}%），'
                      f'业务结构：{prod_summary}。"' if prod_summary else 'f"营收{_fmt(rev,0)}亿。"')
        )
    else:
        biz = (
            f'biz=f"{name}。"'
            + (f' + f"营收{{_fmt(rev,0)}}亿，业务结构：{prod_summary}。"' if prod_summary else "")
        )

    # ── moat (P3) ──
    moat = INDUSTRY_MOAT.get(industry, DEFAULT_MOAT)
    # ── catalyst (P5) ──
    catalyst = INDUSTRY_CATALYST.get(industry, DEFAULT_CATALYST)

    # ── 生成脚本内容 ──
    script = f'''# -*- coding: utf-8 -*-
"""{name} {code} — VL Business + AI Commentary（数据驱动, 自动生成）"""
def build(stock, metrics, revenue_structure, years, cagr, spot):
    ly = metrics.get(years[-1], {{}}) if years else {{}}
    py = metrics.get(years[-2], {{}}) if len(years) >= 2 else {{}}
    def _chg(c, p):
        try:
            c2, p2 = float(c), float(p)
            if not c2 or not p2: return None
            if p2 > 0: return (c2 / p2 - 1) * 100
            if c2 < 0 and p2 < 0: return (c2 - p2) / abs(p2) * 100
            return (c2 / p2 - 1) * 100
        except: return None
    def _dir(c, p): return "增长" if (_chg(c, p) or 0) > 0 else "下降"
    def _num(v):
        try: return float(v)
        except: return 0
    def _fmt(v, d=0):
        try: return f"{{float(v):,.{{d}}f}}"
        except: return "-"
    def _p(v):
        try: return f"{{float(v):+.1f}}%"
        except: return "-"

    rev = _num(ly.get("OPERATE_INCOME"))
    np_val = _num(ly.get("HOLDER_PROFIT"))
    eps = _num(ly.get("BASIC_EPS"))
    gm = _num(ly.get("GROSS_MARGIN"))
    npm = _num(ly.get("NET_PROFIT_RATIO"))
    roe = _num(ly.get("ROE"))
    bps = _num(ly.get("BPS"))
    per_cf = _num(ly.get("PER_NETCASH"))
    per_capex = _num(ly.get("CAPEX_PS") or 0)
    dps = _num(ly.get("DPS") or 0)
    payout = _num(ly.get("PAYOUT_RATIO") or 0)
    price = _num(spot.get("price", 0))
    pe = _num(spot.get("pe", 0)) or (round(price / eps, 1) if price and eps else 0)
    pb = _num(spot.get("pb", 0)) or (round(price / bps, 2) if price and bps else 0)
    div_y = _num(spot.get("div_yield", 0)) or (round(dps / price * 100, 1) if price and dps else 0)
    med_pe = spot.get("median_pe")

    r_chg = _chg(rev, py.get("OPERATE_INCOME"))
    n_chg = _chg(np_val, py.get("HOLDER_PROFIT"))
    r_abs = abs(r_chg) if r_chg is not None else 0
    n_abs = abs(n_chg) if n_chg is not None else 0

    # 营收结构
    prod_data = revenue_structure.get("by_product", []) if isinstance(revenue_structure, dict) else []
    prod_str_parts = [f"{{r['name']}}{{r['pct']:.0f}}%" for r in prod_data] if prod_data else []
    prod_str = "、".join(prod_str_parts) if prod_str_parts else ""

    # 地区拆分
    reg_data = revenue_structure.get("by_region", []) if isinstance(revenue_structure, dict) else []
    dom = next((r for r in reg_data if "国内" in str(r.get("name", ""))), None)
    ovs = next((r for r in reg_data if "国外" in str(r.get("name", ""))), None)

    # Business
    {biz}

    # P1: 业绩快照
    p1 = (
        f"2026年6月 — {{name}}营收{{_fmt(rev, 0)}}亿（{{_dir(rev, py.get('OPERATE_INCOME'))}}{{r_abs:.1f}}%），"
        f"归母净利润{{_fmt(np_val, 0)}}亿（{{_dir(np_val, py.get('HOLDER_PROFIT'))}}{{n_abs:.1f}}%）。"
        + (f"毛利率{{_p(gm)}}，净利率{{_p(npm)}}。" if gm else "")
    )
    if dom and ovs:
        p1 += (
            f"海外收入{{ovs['amount']:.0f}}M（占比{{ovs['pct']:.1f}}%）增速远高国内"
            f"（{{dom['amount']:.0f}}M），全球化布局成效显著。"
        )

    # P2: 每股资金流向
    net_fcf = round(per_cf - per_capex - dps, 2) if per_cf else None
    p2 = (
        f"每股收益{{_fmt(eps, 2)}}元，每股经营现金流{{_fmt(per_cf, 2)}}元，"
        f"资本支出每股{{_fmt(per_capex, 2)}}元（扩产期）。"
        f"自由现金流{{net_fcf}}元/股，分红{{_fmt(dps, 2)}}元/股（支付率{{_fmt(payout, 0)}}%），"
        f"每股净资产{{_fmt(bps, 2)}}元。现金流健康度良好。"
    )

    # P3: 业务质地与壁垒
    p3 = (
        f"毛利率{{_p(gm)}}，净利率{{_p(npm)}}，ROE {{_p(roe)}}。"
        f"{moat}"
    )

    # P4: 估值锚定
    cf_15x = _fmt(per_cf * 15, 2) if per_cf else "-"
    cf_20x = _fmt(per_cf * 20, 2) if per_cf else "-"
    p4 = (
        f"当前PE约{{_fmt(pe, 1)}}倍"
        + ({{True: f"，低于历史中位{{_fmt(med_pe, 0)}}x"}}.get(med_pe and pe < med_pe, "") or "。")
        + f"PB{{_fmt(pb, 2)}}倍，股息率约{{_fmt(div_y, 1)}}%。"
        f"CF估值：每股现金流{{_fmt(per_cf, 2)}}元，CF=15x对应{{cf_15x}}元"
        + (f"（较当前{{_fmt(price, 2)}}元" + ("溢价" if per_cf * 15 > price else "折价") + "）" if price else "")
        + f"，CF=20x对应{{cf_20x}}元。"
    )

    # P5: 催化剂与风险
    p5 = f"{catalyst}"

    return {{"business": biz, "commentary": [p1, p2, p3, p4, p5]}}
'''

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(script)

    print(f"[OK] {out_path} (industry={industry})")
    return True


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="自动生成个股 business_commentary.py")
    parser.add_argument("code", help="股票代码")
    args = parser.parse_args()
    generate(args.code)
