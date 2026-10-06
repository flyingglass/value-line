# -*- coding: utf-8 -*-
"""山东赫达 002810 — VL Business + AI Commentary（个股定制, 数据驱动）

为什么不用通用模板 / 年报原文:
  - 通用模板会产出「主营产品96%、自营产品95%」这类跨年份重复的占位文本；
  - 年报 PDF 按排版行切句会产生「…等优良特」「药」这种半截残句。
  本脚本只取 DB 中的真实财务与营收结构数据，文字针对纤维素醚 / 植物胶囊业务定制。

事实来源:
  - 业务口径: 2025年报「释义」(HPMC/HEC/纤维素醚/HPMC植物胶囊)、「第二节 公司简介」
  - 结构占比: revenue_structure (akshare 东财主营构成, 2025-12-31 年报口径)
  - 财务: metrics (DB indicators / 三大报表)
"""


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
    """取某个维度，按名称去重(同名保留占比最大的一条)，按占比降序。"""
    raw = rs.get(key, []) if isinstance(rs, dict) else []
    acc = {}
    for r in raw:
        name = str(r.get("name", "")).strip()
        if not name:
            continue
        pct = _num(r.get("pct"))
        amount = _num(r.get("value") or r.get("amount"))
        if name not in acc or pct > acc[name]["pct"]:
            acc[name] = {"name": name, "pct": pct, "amount": amount}
    return sorted(acc.values(), key=lambda x: -x["pct"])


def build(stock, metrics, revenue_structure, years, cagr, spot):
    ly = metrics.get(years[-1], {}) if years else {}
    py = metrics.get(years[-2], {}) if len(years) >= 2 else {}
    yr = years[-1] if years else ""

    rev = _num(ly.get("OPERATE_INCOME"))
    np_val = _num(ly.get("HOLDER_PROFIT"))
    eps = _num(ly.get("BASIC_EPS"))
    gm = _num(ly.get("GROSS_MARGIN"))
    npm = _num(ly.get("NET_PROFIT_RATIO"))
    opm = _num(ly.get("OP_MARGIN"))
    roe = _num(ly.get("ROE"))
    bps = _num(ly.get("BPS"))
    per_cf = _num(ly.get("PER_NETCASH"))
    per_capex = _num(ly.get("CAPEX_PS"))
    dps = _num(ly.get("DPS"))
    payout = _num(ly.get("PAYOUT_RATIO"))
    dep = _num(ly.get("DEPRECIATION"))
    price = _num(spot.get("price", 0))
    pe = _num(spot.get("pe", 0)) or (round(price / eps, 1) if price and eps else 0)
    pb = _num(spot.get("pb", 0)) or (round(price / bps, 2) if price and bps else 0)
    med_pe = _num(spot.get("median_pe", 0))
    div_y = _num(spot.get("div_yield", 0)) or (round(dps / price * 100, 1) if price and dps else 0)

    prods = _dim(revenue_structure, "by_product")
    regs = _dim(revenue_structure, "by_region")

    def _join(items, n=4):
        return "、".join(f"{i['name']} {_pct(i['pct'], 1)}" for i in items[:n])

    prod_str = _join(prods)
    reg_str = _join(regs, 2)
    overseas = next((r for r in regs if "海外" in r["name"] or "国外" in r["name"] or "境外" in r["name"]), None)

    # ── Business: 先讲清生意是什么，再给结构与最新数据 ──
    biz = (
        f"山东赫达（002810.SZ，山东淄博周村）以天然纤维素经醚化反应生产纤维素醚："
        f"主要品种为 HPMC（羟丙基甲基纤维素）与 HEC（羟乙基纤维素），"
        f"因用量小、作用大被称为「工业味精」，下游覆盖建材干混砂浆/瓷砖胶、医药辅料、食品添加剂与日化；"
        f"公司同时向下游延伸至 HPMC 植物空心胶囊（子公司山东赫尔希胶囊），并经营石墨产品等副业。"
    )
    if prod_str:
        biz += f"{yr}年营收{_fmt(rev, 2)}亿元，产品结构：{prod_str}。"
    if reg_str:
        biz += f"地区结构：{reg_str}"
        if overseas:
            biz += f"，海外为第一大市场"
        biz += "。"
    # 注: metrics 的 HOLDER_PROFIT 为 VL 口径扣非净利润(2025: 归母1.42亿 / 扣非1.60亿),
    #     文案统一写「扣非净利润」，避免与年报归母口径混淆
    if np_val:
        biz += f"扣非净利润{_fmt(np_val, 2)}亿元，毛利率{_pct(gm)}、净利率{_pct(npm)}。"

    # ── P1 业绩快照 ──
    r_chg = _chg(rev, py.get("OPERATE_INCOME"))
    n_chg = _chg(np_val, py.get("HOLDER_PROFIT"))
    p1 = f"{yr}年营收{_fmt(rev, 2)}亿元"
    if r_chg is not None:
        p1 += f"（同比{r_chg:+.1f}%）"
    p1 += f"，扣非净利润{_fmt(np_val, 2)}亿元"
    if n_chg is not None:
        p1 += f"（同比{n_chg:+.1f}%）"
    p1 += f"，毛利率{_pct(gm)}、经营利润率{_pct(opm)}、ROE {_pct(roe)}。"
    if r_chg is not None and n_chg is not None:
        if n_chg < r_chg:
            p1 += "利润增速慢于营收，说明毛利或费用端承压（增收不增利）。"
        elif n_chg > r_chg:
            p1 += "利润增速快于营收，费用率改善或产品结构上移。"

    # ── P2 每股与现金流 ──
    net_fcf = round(per_cf - per_capex - dps, 2)
    p2 = (
        f"每股收益{_fmt(eps, 2)}元，每股经营现金流{_fmt(per_cf, 2)}元，"
        f"每股资本开支{_fmt(per_capex, 2)}元，每股分红{_fmt(dps, 2)}元（支付率{_fmt(payout, 0)}%），"
        f"每股净资产{_fmt(bps, 2)}元。"
    )
    if per_cf:
        p2 += f"扣除资本开支与分红后自由现金流{_fmt(net_fcf, 2)}元/股"
        p2 += "（为负，扩产期靠借款/存量现金支撑）" if net_fcf < 0 else "（为正，内生现金可覆盖扩张）"
        p2 += "。"
    if dep:
        p2 += f"折旧摊销{_fmt(dep, 2)}亿元，占营收{_pct(dep / rev * 100) if rev else '-'}，属重资产制造口径。"

    # ── P3 业务质地 ──
    p3 = (
        f"生意质地：纤维素醚是建材与药用辅料的添加剂，单价低但粘性强、认证门槛高，"
        f"因此客户切换成本构成主要护城河；医药级、食品级纤维素醚的生产技术与附加值高于建材级，"
        f"植物胶囊是纤维素醚的下游延伸（子公司赫尔希胶囊），附加值更高。"
        f"当前毛利率{_pct(gm)}、净利率{_pct(npm)}、ROE {_pct(roe)}，"
        f"盈利能力处于化工制造的中等水平。"
    )
    if overseas:
        p3 += (
            f"海外收入占比{_pct(overseas['pct'])}，是第一大市场，"
            f"带来汇率与贸易政策（关税/认证）的额外变量。"
        )

    # ── P4 估值锚定 ──
    cf15 = per_cf * 15
    cf20 = per_cf * 20
    p4 = f"当前股价{_fmt(price, 2)}元，PE(TTM) {_fmt(pe, 1)}x"
    if med_pe:
        p4 += f"，历史中位 PE {_fmt(med_pe, 0)}x（{'高于' if pe > med_pe else '低于'}中枢）"
    p4 += f"，PB {_fmt(pb, 2)}x，股息率{_pct(div_y)}。"
    if per_cf:
        p4 += (
            f"CF 估值：每股现金流{_fmt(per_cf, 2)}元 → CF=15x 对应{_fmt(cf15, 2)}元、"
            f"CF=20x 对应{_fmt(cf20, 2)}元，现价相对 15x "
            f"{'溢价' if price > cf15 else '折价'}{_pct(abs(price / cf15 - 1) * 100) if cf15 else '-'}。"
        )

    # ── P5 观察点与风险 ──
    p5 = (
        "后续看点：①医药级/食品级纤维素醚与植物胶囊的产能爬坡与占比提升（结构升级带动毛利率）；"
        "②海外客户认证与订单延续（海外为第一大市场）；"
        + ("③折旧与资本开支见顶后自由现金流能否转正。" if net_fcf < 0
           else "③自由现金流能否在扩产期维持为正并覆盖后续产能投入。")
        + "主要风险：建材级需求与地产/基建景气度相关、原材料与能源价格波动、"
        "海外占比高带来的汇率与关税扰动、新增产能投放后的价格竞争。"
        "跟踪信号：季度毛利率、海外收入增速、植物胶囊收入占比、经营性现金流/净利润比值。"
    )

    return {"business": biz, "commentary": [p1, p2, p3, p4, p5]}
