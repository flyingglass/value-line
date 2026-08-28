# -*- coding: utf-8 -*-
"""
古井贡B 200596 — VL Business + AI Commentary (数据驱动, 聚焦 A/B 折价)

B股与A股(000596)为同一法律主体、同一份财报、同一分红方案，仅交易场所与
计价货币不同（深市B股以港元计价）。因此本报告的财务指标与A股一致，
核心差异与投资要点集中在 **折价** 上。

折价数据全部实时计算: B股价(自身DB) vs A股价(000596.DB) + HKD/CNY汇率。
不硬编码任何价格或折价率。
"""
import os
import sqlite3

_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _get_fx(date_str=None):
    """1 HKD = ? CNY (fx_rates.db 存 100HKD=?CNY)"""
    db = os.path.join(_ROOT, "data", "fx_rates.db")
    if not os.path.exists(db):
        return None
    try:
        conn = sqlite3.connect(db)
        if date_str:
            row = conn.execute(
                "SELECT hkd_cny FROM daily_rates WHERE date<=? ORDER BY date DESC LIMIT 1",
                (date_str,)).fetchone()
        else:
            row = conn.execute(
                "SELECT hkd_cny FROM daily_rates ORDER BY date DESC LIMIT 1").fetchone()
        conn.close()
        return row[0] / 100.0 if row else None
    except Exception:
        return None


def _latest_close(code):
    """取该标的最新前复权收盘价"""
    db = os.path.join(_ROOT, "data", f"{code}.db")
    if not os.path.exists(db):
        return None, None
    try:
        conn = sqlite3.connect(db)
        row = conn.execute(
            "SELECT date, close FROM kline WHERE adjust='qfq' ORDER BY date DESC LIMIT 1"
        ).fetchone()
        conn.close()
        return (row[0], row[1]) if row else (None, None)
    except Exception:
        return None, None


def _yearly_avg_close(code):
    """按年聚合前复权月均价 → {年份: 年均价}"""
    db = os.path.join(_ROOT, "data", f"{code}.db")
    if not os.path.exists(db):
        return {}
    try:
        from collections import defaultdict
        conn = sqlite3.connect(db)
        rows = conn.execute(
            "SELECT date, close FROM kline WHERE adjust='qfq' ORDER BY date").fetchall()
        conn.close()
        monthly = defaultdict(list)
        for d, c in rows:
            monthly[d[:7]].append(c)
        yr = defaultdict(list)
        for m, cs in monthly.items():
            yr[m[:4]].append(sum(cs) / len(cs))
        return {y: sum(v) / len(v) for y, v in yr.items() if v}
    except Exception:
        return {}


def build(stock, metrics, revenue_structure, years, cagr, spot):
    ly = metrics.get(years[-1], {}) if years else {}
    py = metrics.get(years[-2], {}) if len(years) >= 2 else {}

    def _num(v):
        try:
            return float(v)
        except (TypeError, ValueError):
            return 0.0

    def _chg(c, p):
        try:
            c2, p2 = float(c), float(p)
            return (c2 / p2 - 1) * 100 if p2 else None
        except (TypeError, ValueError, ZeroDivisionError):
            return None

    def _dir(c, p):
        v = _chg(c, p)
        if v is None:
            return "变动"
        return "增长" if v > 0 else ("下降" if v < 0 else "持平")

    def _fmt(v, d=0):
        try:
            return f"{float(v):,.{d}f}"
        except (TypeError, ValueError):
            return "-"

    def _p(v, d=1):
        try:
            return f"{float(v):.{d}f}%"
        except (TypeError, ValueError):
            return "-"

    rev = _num(ly.get("OPERATE_INCOME"))
    rev_p = _num(py.get("OPERATE_INCOME"))
    np_val = _num(ly.get("HOLDER_PROFIT"))
    np_p = _num(py.get("HOLDER_PROFIT"))
    eps = _num(ly.get("BASIC_EPS"))
    gm = _num(ly.get("GROSS_MARGIN"))
    npm = _num(ly.get("NET_PROFIT_RATIO"))
    roe = _num(ly.get("ROE"))
    bps = _num(ly.get("BPS"))
    per_cf = _num(ly.get("PER_NETCASH"))
    dps = _num(ly.get("DPS"))
    payout = _num(ly.get("PAYOUT_RATIO"))

    r_chg, n_chg = _chg(rev, rev_p), _chg(np_val, np_p)

    pe = _num(spot.get("pe"))
    pb = _num(spot.get("pb"))
    div = _num(spot.get("div_yield"))

    # ══════════ A/B 折价测算 (全部实时计算) ══════════
    a_code = (stock or {}).get("a_share_code", "000596")
    b_px_hkd = _num(spot.get("price"))                 # B股价 (HKD)
    fx = _get_fx()
    _, a_px = _latest_close(a_code)                    # A股价 (CNY)
    a_px = _num(a_px)
    b_px_cny = b_px_hkd * fx if (b_px_hkd and fx) else 0.0

    disc = None          # B股相对A股折价率
    a_div_yield = None   # A股股息率
    b_div_yield = None   # B股股息率(同DPS, 更低价格 → 更高股息率)
    if b_px_cny > 0 and a_px > 0:
        disc = (1 - b_px_cny / a_px) * 100
    if dps > 0 and a_px > 0:
        a_div_yield = dps / a_px * 100
    if dps > 0 and b_px_cny > 0:
        b_div_yield = dps / b_px_cny * 100

    # 历史折价区间 (按年均价)
    hist_disc = []
    if fx:
        a_yr = _yearly_avg_close(a_code)
        b_yr = _yearly_avg_close("200596")   # 本模块专属标的
        for y in sorted(set(a_yr) & set(b_yr)):
            if a_yr[y] <= 0:
                continue
            f = _get_fx(f"{y}-12-31") or fx
            bd = (1 - b_yr[y] * f / a_yr[y]) * 100
            hist_disc.append((y, bd))

    # ── 营收结构
    rs = revenue_structure if isinstance(revenue_structure, dict) else {}

    def _pct(dim, *keys):
        for r in rs.get(dim, []):
            if any(k in r.get("name", "") for k in keys):
                return _num(r.get("pct"))
        return None

    baijiu_pct = _pct("by_product", "白酒")
    central_pct = _pct("by_region", "华中")

    # ══════════ Business ══════════
    biz = (
        "古井贡B是古井贡酒在深交所上市的B股（A股000596.SZ），与A股同股同权，"
        "共享同一份财务报表、同一分红方案，唯一差异是以港元计价交易且投资者准入受限。"
        + (f"白酒业务占营收{_p(baijiu_pct)}" if baijiu_pct else "")
        + (f"，华中大本营市场占{_p(central_pct)}" if central_pct else "")
        + f"。最新年度营收{_fmt(rev, 1)}亿、归母净利润{_fmt(np_val, 1)}亿、"
        f"毛利率{_p(gm)}、ROE {_p(roe)}。"
    )
    if disc is not None:
        biz += (
            f"当前B股{_fmt(b_px_hkd, 2)}港元（≈{_fmt(b_px_cny, 2)}元人民币）"
            f"，A股{_fmt(a_px, 2)}元人民币，**B股折价{_p(disc)}**——"
            "同样的股权、同样的分红，价格只有A股的一半左右。"
        )

    # ══════════ P1 经营分析 ══════════
    yr_label = years[-1] if years else "最新年度"
    p1 = f"基本面与A股完全一致（同一法律主体）。{yr_label}年营收{_fmt(rev, 1)}亿"
    if r_chg is not None:
        p1 += f"（{_dir(rev, rev_p)}{abs(r_chg):.1f}%）"
    if n_chg is not None:
        p1 += f"，归母净利润{_fmt(np_val, 1)}亿（{_dir(np_val, np_p)}{abs(n_chg):.1f}%）"
    else:
        p1 += f"，归母净利润{_fmt(np_val, 1)}亿"
    p1 += "。白酒行业自2024年起进入深度调整期，需求疲软叠加渠道去库存，次高端价格带承压，公司主动控货去化以修复渠道。"
    if yr_label == "2025":
        p1 += "当年对黄鹤楼酒业计提约3.15亿元商誉减值，是第四季度单季利润转负的直接原因之一（来源：2025年年度报告、长江证券点评）。"

    # ══════════ P2 现金流与资本配置 (折价核心) ══════════
    p2 = f"每股收益¥{_fmt(eps, 2)}，每股经营现金流¥{_fmt(per_cf, 2)}，每股分红¥{_fmt(dps, 2)}"
    if payout:
        p2 += f"（支付率{_fmt(payout, 0)}%）"
    p2 += "。"
    if a_div_yield and b_div_yield:
        p2 += (
            f"**折价直接体现在股息率上：同一笔每股¥{_fmt(dps, 2)}的分红，"
            f"A股股东股息率{a_div_yield:.2f}%，B股股东{b_div_yield:.2f}%，"
            f"B股为A股的{b_div_yield / a_div_yield:.2f}倍。**"
        )
    p2 += "分红以人民币宣告、按派息时汇率折算为港元派发，B股股东承担的汇率波动仅限于派息时点，不改变其人民币收益权的本质。"

    # ══════════ P3 盈利质量与护城河 ══════════
    p3 = f"毛利率{_p(gm)}、净利率{_p(npm)}、ROE {_p(roe)}、每股净资产¥{_fmt(bps, 2)}。"
    p3 += (
        "公司层面壁垒：①老八大名酒品牌背书，「年份原浆」在安徽及华中市场心智稳固；"
        "②古井镇老窖池资源与酿造工艺积淀；③省内深度分销网络。"
    )
    p3 += (
        "**但B股投资者需额外认清：折价不是公司质地折让，而是股权之外的问题**——"
        "B股市场自2001年对境内个人开放后再无增量制度供给，流动性长期枯竭、"
        "再融资功能丧失，折价反映的是流动性与制度性因素，而非基本面的额外风险。"
    )
    p3 += "公司层面的真实风险仍是：全国化推进不及预期、次高端竞争加剧、白酒消费受宏观景气度影响。"

    # ══════════ P4 估值 ══════════
    p4 = f"当前PE约{_fmt(pe, 1)}倍，PB约{_fmt(pb, 2)}倍，股息率约{_fmt(div, 2)}%。"
    if disc is not None:
        p4 += f"**相对A股折价{_p(disc)}（B股{_fmt(b_px_hkd, 2)}港元≈¥{_fmt(b_px_cny, 2)} vs A股¥{_fmt(a_px, 2)}）。**"
    if hist_disc:
        ds = [d for _, d in hist_disc]
        y0, y1 = hist_disc[0][0], hist_disc[-1][0]
        p4 += (
            f"历史折价区间（{y0}-{y1}年均价口径）：最窄{min(ds):.1f}%、最宽{max(ds):.1f}%、"
            f"均值{sum(ds) / len(ds):.1f}%。"
        )
        if disc is not None:
            if disc <= min(ds):
                p4 += "当前处于历史最窄水平，折价修复空间已大幅收窄。"
            elif disc >= max(ds):
                p4 += "当前处于历史最宽水平。"
            else:
                p4 += f"当前处于历史均值{'之下' if disc < sum(ds) / len(ds) else '之上'}。"
    p4 += "B股的定价锚应是A股：折价收敛是主要回报来源，但收敛时点不可预测。"

    # ══════════ P5 催化剂 ══════════
    p5 = (
        "催化剂：①B股市场制度改革（B转A、B转H、回购注销等先例曾带来折价快速收敛）；"
        "②公司层面回购或大股东增持B股；③A股估值修复带动B股联动；"
        "④股息率优势吸引长期资金——当前B股股息率显著高于A股，"
        "对以收息为目的的资金具备吸引力。"
        "跟踪信号：A/B折价率变化、B股日均成交额（流动性是否改善）、"
        "公司分红方案（B股绝对股息是否维持）、B股市场政策动向。"
        "**风险提示：折价可以长期存在甚至进一步扩大；B股流动性极差，"
        "大额资金进出困难，且需承担港元/人民币汇率波动。**"
    )

    return {"business": biz, "commentary": [p1, p2, p3, p4, p5]}
