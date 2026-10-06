# -*- coding: utf-8 -*-
"""revenue_price_timeline_hk.py — 港股「营收 × 披露时点 × 股价」一图对照（单面板叠加）

与 .codebuddy/skills/revenue-price-timeline 的 A 股版同版式，差异在数据源与期别：

| | A 股版（skill） | 本脚本（港股） |
|---|---|---|
| 营收 | ak.stock_profit_sheet_by_report_em，TOTAL_OPERATE_INCOME | ak.stock_financial_hk_report_em，营业额 STD_ITEM_CODE=004001001 |
| 披露日 | 东财 NOTICE_DATE | 港交所披露易 titleSearchServlet（业绩公告刊发日 **精确到分钟**） |
| 行情 | ak.stock_zh_a_daily(qfq) | ak.stock_hk_daily(qfq)，单位港元 |
| 期别 | 一季报 / 中报 / 三季报 / 年报 四色 | 港股无强制季报 → **仅中报(H1) / 年报(FY) 两色** |
| 季度更新 | A 股 Q1/Q3 本身就是定期财报 | 另在 x 轴下方用**橙色三角**标记自愿性季度业务状况（Q1/Q3），只有时点、无营收 |

港股特有口径：
- 业绩公告有「午间休市刊发」与「收市后刊发」两类。前者的价格反应在**当日午后**，
  后者的反应在**次日**。故标注点统一取「披露后首个交易日」收盘价（hour<16 → 当日；
  hour>=16 → 下一交易日），口径为「市场首次完整消化该期业绩的收盘价」。
- 营收以**人民币**列示，股价为**港元**，两者不可直接相乘，仅作走势对照。
- 公司惯例每年自愿发布「第一/第三季度最新業務狀況」（首期 2021Q3，之后 Q1 在 4 月中下旬、
  Q3 在 10 月下旬）。这类公告**没有营业额数据**，不能画成营收柱，只留一条淡橙点线贯穿柱区，
  并在 x 轴刻度标签下方的「季度轨道」上给一个橙色三角 + 标签「YYQn」，用于把「定期财报节奏」
  与「季度经营披露节奏」放在同一条时间轴上对照。

用法：
    python scripts/09992/revenue_price_timeline_hk.py --code 09992 --name 泡泡玛特 \
        --extremes 2021:high,2022:low,2025:high,2026:low \
        --out research-wiki/research/消费/泡泡玛特/assets/revenue-price-timeline.png \
        --csv scripts/out/09992_revenue_vs_price.csv
"""
import argparse
import json
import os
import re
import sys
import time

import akshare as ak
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.font_manager as fm
from matplotlib.patches import Rectangle
import requests

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:                                            # noqa: BLE001
    pass

PRICE_C = "#2f6fd0"
GRID_C = "#e8eaee"
YEAR_C = "#c3ccd9"
NOTE_C = "#6b7280"
# 季度业务状况（公司自愿公告，非定期财报）：标记/竖线/文字
QNOTE_C = "#e08a4c"
QNOTE_LINE_C = "#f2c9a8"
QNOTE_TXT_C = "#a8552a"

REV_ITEM = "004001001"          # 「营业额」

# key, 报告期名称, 涵盖月份, 报告期末(MM-DD), 柱色, 描边色, 柱宽(天),
# 字号, zorder, 透明度, 标签上移(pt)
KINDS = [
    ("H1", "中报", 6, "06-30", "#63bda6", "#227a63", 30.0, 8.4, 3.9, 0.82, 8.0),
    ("FY", "年报", 12, "12-31", "#9b86c4", "#4f3d78", 46.0, 8.8, 3.0, 0.48, 8.0),
]
STYLE = {k[0]: dict(name=k[1], months=k[2], prev=k[3], color=k[4], deep=k[5],
                    width=k[6], fs=k[7], z=k[8], alpha=k[9], up=k[10])
         for k in KINDS}
DRAW_ORDER = ["FY", "H1"]

Z_LINE = 6.0
Z_LABEL = 8.0
Z_NOTE = 9.0
Z_EXTREME_MK = 10.0
Z_EXTREME_TX = 12.0

HDR = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}


def setup_font():
    avail = {f.name for f in fm.fontManager.ttflist}
    for f in ("Microsoft YaHei", "SimHei", "Noto Sans CJK SC",
              "Source Han Sans SC", "Arial Unicode MS"):
        if f in avail:
            plt.rcParams["font.sans-serif"] = [f]
            return f
    return None


def _retry(fn, n=4, wait=2.0):
    last = None
    for _ in range(n):
        try:
            return fn()
        except Exception as e:                                # noqa: BLE001
            last = e
            time.sleep(wait)
    raise last


# ----------------------------------------------------------------- 港交所披露易
def hkex_stock_id(code):
    """港交所披露易的内部 stockId（与证券代码不同）。"""
    u = ("https://www1.hkexnews.hk/search/prefix.do?"
         "callback=cb&lang=ZH&type=A&name=%s&market=SEHK" % code)
    t = requests.get(u, headers=HDR, timeout=30).text
    m = re.search(r'"stockId"\s*:\s*(\d+)', t)
    if not m:
        raise RuntimeError("未取得港交所 stockId：%s" % code)
    return m.group(1)


def hkex_announcements(code, y0=2019, y1=None):
    """拉取港交所公告列表（逐年分片），返回 DataFrame。"""
    sid = hkex_stock_id(code)
    y1 = y1 or pd.Timestamp.today().year
    rows = []
    for y in range(y0, y1 + 1):
        u = ("https://www1.hkexnews.hk/search/titleSearchServlet.do?"
             "sortDir=0&sortByOptions=DateTime&category=0&market=SEHK&stockId=%s"
             "&documentType=-1&fromDate=%d0101&toDate=%d1231&title=&searchType=1"
             "&t1code=-2&t2Gcode=-2&t2code=-2&rowRange=400&lang=ZH" % (sid, y, y))
        r = _retry(lambda: requests.get(u, headers=HDR, timeout=45).json(),
                   n=3, wait=2.0)
        res = r.get("result")
        if isinstance(res, str):
            res = json.loads(res)
        rows += (res or [])
        time.sleep(0.4)
    df = pd.DataFrame(rows)
    df["dt"] = pd.to_datetime(df["DATE_TIME"], format="%d/%m/%Y %H:%M",
                              errors="coerce")
    return df.dropna(subset=["dt"]).sort_values("dt").reset_index(drop=True)


RESULT_RE = re.compile(
    r"截至\s*(\d{4})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*日止\s*"
    r"(年度|六個月|六个月|三個月|三个月)")

CN_DIG = {"零": 0, "一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6,
          "七": 7, "八": 8, "九": 9}
RESULT_RE_CN = re.compile(r"截至\s*([零一二三四五六七八九〇]{4})年"
                          r"([零一二三四五六七八九]{1,3})月"
                          r"([零一二三四五六七八九]{1,3})日止\s*"
                          r"(年度|六個月|六个月)")


def _cn2int(s):
    """中文数字 → int（覆盖 1-31 的常见写法）。"""
    if s in ("十",):
        return 10
    if s.startswith("十"):
        return 10 + CN_DIG.get(s[1:], 0)
    if "十" in s:
        a, b = s.split("十")
        return CN_DIG.get(a, 0) * 10 + (CN_DIG.get(b, 0) if b else 0)
    return int("".join(str(CN_DIG.get(c, "")) for c in s) or 0)


def parse_result_announcements(ann):
    """从公告列表里挑出定期业绩公告，解析出报告期末与刊发时点。"""
    out = []
    for _, r in ann.iterrows():
        title = str(r["TITLE"])
        if ("業績" not in title) and ("业绩" not in title):
            continue
        m = RESULT_RE.search(title)
        if m:
            y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
        else:
            m = RESULT_RE_CN.search(title)
            if not m:
                continue
            y = int("".join(str(CN_DIG.get(c, 0)) for c in m.group(1)))
            mo, d = _cn2int(m.group(2)), _cn2int(m.group(3))
        period_end = pd.Timestamp("%04d-%02d-%02d" % (y, mo, d))
        if period_end.strftime("%m-%d") == "06-30":
            kind = "H1"
        elif period_end.strftime("%m-%d") == "12-31":
            kind = "FY"
        else:
            continue                                # 一季报/三季度业务状况：非定期财报
        out.append(dict(kind=kind, period_end=period_end,
                        notice=r["dt"], title=title))
    return sorted(out, key=lambda x: x["notice"])


QUARTER_RE = re.compile(
    r"二零([〇一二三四五六七八九]{2})年第([一二三])季度最新業務狀況")


def parse_quarterly_updates(ann):
    """挑出公司自愿发布的「季度业务状况」公告（每年 Q1 / Q3 两期）。

    港股没有强制季报，这类公告也不是定期财报（东财利润表里没有对应期次的营业额），
    因此不进营收柱，只作为信息披露时点在图上标记。
    """
    out = []
    for _, r in ann.iterrows():
        m = QUARTER_RE.search(str(r["TITLE"]))
        if not m:
            continue
        year = 2000 + _cn2int(m.group(1))
        q = _cn2int(m.group(2))
        if q not in (1, 3):
            continue
        out.append(dict(year=year, q=q, notice=r["dt"], title=str(r["TITLE"])))
    return sorted(out, key=lambda x: x["notice"])


# ----------------------------------------------------------------- 营收 / 行情
def fetch_revenue(code):
    """东财港股利润表「营业额」（按报告期累计），单位：亿元。"""
    df = _retry(lambda: ak.stock_financial_hk_report_em(
        stock=code, symbol="利润表", indicator="报告期"))
    df = df[df["STD_ITEM_CODE"].astype(str) == REV_ITEM].copy()
    df["period_end"] = pd.to_datetime(df["REPORT_DATE"])
    df["rev"] = pd.to_numeric(df["AMOUNT"], errors="coerce") / 1e8
    df = df.dropna(subset=["rev"])
    # 同一报告期若返回多行，保留最后一条
    df = (df.sort_values("period_end")
            .drop_duplicates("period_end", keep="last"))
    return df[["period_end", "rev"]].reset_index(drop=True)


def fetch_price(code, start=None, end=None, ipo=None):
    d = _retry(lambda: ak.stock_hk_daily(symbol=code, adjust="qfq"))
    d["date"] = pd.to_datetime(d["date"])
    if ipo is not None:
        # 可选：按上市日截断。数据源若给出上市日之前的行（试盘报价/不同源兜底），
        # 图上会多出一段「上市前」的股价线，给 --ipo 即截掉。
        # 不给此参数时，图的左端就是数据源给出的首个交易日。
        # 注意：绘图区左右还会被 matplotlib autoscale 再加约 5% 留白，属正常，
        # 别据此以为行情数据起点比 set_xlim 的左端更早（二者不是一回事）。
        d = d[d["date"] >= pd.Timestamp(ipo)]
    if start is not None:
        d = d[d["date"] >= start]
    if end is not None:
        d = d[d["date"] <= end]
    return d.sort_values("date").reset_index(drop=True)


def build_frames(ann_items, rev, px_start):
    """把公告与营收对起来，剔除行情起点前披露的期次。"""
    rev_of = dict(zip(rev["period_end"].dt.strftime("%Y-%m-%d"), rev["rev"]))
    items = []
    for a in ann_items:
        if a["notice"] < px_start or a["period_end"] < px_start:
            continue
        r = rev_of.get(a["period_end"].strftime("%Y-%m-%d"))
        if r is None or not np.isfinite(r):
            continue
        y = a["period_end"].year
        md = a["period_end"].strftime("%m-%d")
        prev = rev_of.get("%d-%s" % (y - 1, md))
        yoy = None if prev is None or not np.isfinite(prev) or prev == 0 \
            else (r / prev - 1.0) * 100.0
        items.append(dict(kind=a["kind"], year=y, rev=float(r), yoy=yoy,
                          notice=a["notice"], period_end=a["period_end"],
                          title=a["title"],
                          label=("FY%d" % y) if a["kind"] == "FY"
                          else ("%dH1" % y)))
    return sorted(items, key=lambda it: it["notice"])


def first_reaction_close(px, ts):
    """披露后首个交易日收盘价：刊发时刻 <16:00（午间/盘中）算当日，否则顺延。"""
    if ts.hour >= 16:
        seg = px[px["date"] > ts.normalize()]
    else:
        seg = px[px["date"] >= ts.normalize()]
    if len(seg):
        return float(seg["close"].iloc[0]), seg["date"].iloc[0]
    return float(px["close"].iloc[-1]), px["date"].iloc[-1]


def price_at(px, d):
    seg = px[px["date"] <= d]
    return float(seg["close"].iloc[-1]) if len(seg) else float(px["close"].iloc[0])


def parse_extremes(s, px):
    out = []
    for part in [p for p in s.split(",") if p.strip()]:
        m = re.match(r"\s*(\d{4})\s*(?::\s*(high|low|高|低))?\s*$", part)
        if not m:
            raise ValueError("--extremes 格式应为 2021:high,2022:low，收到：%s" % part)
        y = int(m.group(1))
        kind = {"高": "high", "低": "low"}.get(m.group(2) or "high",
                                            m.group(2) or "high")
        seg = px[px["date"].dt.year == y]
        if seg.empty:
            continue
        i = seg["close"].idxmax() if kind == "high" else seg["close"].idxmin()
        out.append(dict(year=y, kind=kind, val=float(seg.loc[i, "close"]),
                        date=seg.loc[i, "date"], score=0.0))
    return out


def nice_ticks(top, target=7):
    top = float(top)
    if top <= 0:
        return np.array([0.0])
    raw = top / float(target)
    mag = 10.0 ** np.floor(np.log10(raw))
    step = 10.0 * mag
    for mm in (1.0, 2.0, 2.5, 5.0, 10.0):
        if raw <= mm * mag:
            step = mm * mag
            break
    return np.arange(0.0, top + step * 1e-9, step)


# ----------------------------------------------------------------- 绘图
def draw(items, px, name, code, extremes, out_path,
         price_mult=1.14, rev_mult=1.14, footer_extra="", q_items=None):
    x_px = mdates.date2num(px["date"])
    y_px = px["close"].to_numpy(dtype=float)

    start = px["date"].min()
    end = px["date"].max()
    x0 = mdates.date2num(start) - 45
    x1 = mdates.date2num(end) + 45
    hi = float(np.nanmax(y_px))
    rev_max = max(it["rev"] for it in items)

    price_top = hi * price_mult
    rev_top = max(rev_max * rev_mult, 1e-9)
    scale = price_top / rev_top

    fig = plt.figure(figsize=(29.0, 12.4), dpi=150)
    fig.patch.set_facecolor("#ffffff")
    # bottom 抬高到 0.175（原 0.152）：给 x 轴下方留一条「季度轨道」，
    # 顺序自上而下＝柱的 MM-DD(-4~-13pt) / 年份刻度标签(-6~-19pt，横向错开) /
    # 季度三角与标签(-23~-33pt) / 脚注(约 -36pt 起)，四层不互压
    gs = fig.add_gridspec(1, 1, left=0.040, right=0.962, top=0.856,
                          bottom=0.175)
    ax = fig.add_subplot(gs[0])
    ax.set_facecolor("#fafbfc")
    ax.set_ylim(0, price_top)
    ax.set_xlim(x0, x1)
    axr = ax.secondary_yaxis(
        "right", functions=(lambda v: v / scale, lambda v: v * scale))

    for y in range(start.year + 1, end.year + 1):
        ax.axvline(mdates.date2num(pd.Timestamp("%d-01-01" % y)),
                   color=YEAR_C, lw=1.0, zorder=1.0)
    for ts in sorted({it["notice"] for it in items}):
        ax.axvline(mdates.date2num(ts), color="#e6e9ef", lw=0.85,
                   ls=(0, (3, 3)), zorder=1.2)

    # ---- 季度业务状况（自愿公告）：淡橙点线贯穿柱区 + x 轴下方「季度轨道」标记 ----
    #      三角与期次标签统一压到 x 轴刻度标签下方的轨道上（Q_Y，约轴下 28pt），
    #      既不压 stock 曲线也不抢营收柱；标签横排在三角右侧，
    #      相邻两期相隔约半年（≈300px），不会互相挤
    q_used = [q for q in (q_items or [])
              if px["date"].min() <= q["notice"] <= end]
    if q_used:
        q_note = ("x 轴下方橙色三角＝公司自愿发布的季度业务状况公告（每年 Q1 / Q3 两期，"
                  "港股无强制季报故无对应营业额数据，只作信息披露时点）：图上共 %d 期，"
                  "最早 %s、最新 %s。"
                  % (len(q_used), q_used[0]["notice"].strftime("%Y-%m-%d"),
                     q_used[-1]["notice"].strftime("%Y-%m-%d")))
    else:
        q_note = ""
    q_track = ax.get_xaxis_transform()      # x=date2num 数据坐标，y=axes fraction
    Q_Y = -0.046                            # ≈ 轴下方 28pt
    for q in q_used:
        xv = mdates.date2num(q["notice"])
        ax.plot([xv, xv], [0, price_top * 0.96], color=QNOTE_LINE_C, lw=0.9,
                ls=(0, (2, 4)), zorder=1.15)
        ax.plot([xv], [Q_Y], marker="^", ms=5.0, color=QNOTE_C, mec="none",
                transform=q_track, clip_on=False, zorder=Z_LABEL)
        ax.annotate("%02dQ%d" % (q["year"] % 100, q["q"]), (xv, Q_Y),
                    xycoords=q_track, textcoords="offset points",
                    xytext=(5, 0), ha="left", va="center",
                    fontsize=7.0, color=QNOTE_TXT_C, zorder=Z_LABEL)

    for key in DRAW_ORDER:
        st = STYLE[key]
        for it in [i for i in items if i["kind"] == key]:
            xv = mdates.date2num(it["notice"])
            ax.bar(xv, it["rev"] * scale, width=st["width"], bottom=0.0,
                   color=st["color"], alpha=st["alpha"], edgecolor=st["deep"],
                   linewidth=0.85, hatch=("" if key == "FY" else "///"),
                   zorder=st["z"])
            txt = "%s  %.1f亿" % (it["label"], it["rev"])
            if it["yoy"] is not None:
                txt += "\n%+.1f%%" % it["yoy"]
            ax.annotate(txt, (xv, it["rev"] * scale), xytext=(0, st["up"]),
                        textcoords="offset points", ha="center", va="bottom",
                        fontsize=st["fs"], fontweight="bold",
                        color=st["deep"], zorder=Z_LABEL + st["z"] * 0.1,
                        linespacing=1.32)
            ax.annotate(it["notice"].strftime("%m-%d"), (xv, 0),
                        xytext=(0, -13), textcoords="offset points",
                        ha="center", va="top", fontsize=7.2,
                        color="#8b939e", zorder=Z_LABEL + st["z"] * 0.1)

    ax.plot(x_px, y_px, color=PRICE_C, lw=1.2, zorder=Z_LINE)

    pat = []
    for it in items:
        pxv, real = first_reaction_close(px, it["notice"])
        pat.append(dict(label=it["label"], kind=it["kind"],
                        notice=it["notice"].strftime("%Y-%m-%d %H:%M"),
                        reaction_date=real.strftime("%Y-%m-%d"),
                        reaction_close=round(pxv, 2),
                        rev=round(it["rev"], 2),
                        yoy=None if it["yoy"] is None else round(it["yoy"], 1)))
        ax.plot([mdates.date2num(real)], [pxv], marker="o",
                ms=5.4 if it["kind"] == "FY" else 4.6, mfc="#ffffff",
                mec=NOTE_C, mew=1.25, zorder=Z_NOTE)

    for ex in extremes:
        xv = mdates.date2num(ex["date"])
        val = ex["val"]
        off, va = ((0, 10), "bottom") if ex["kind"] == "high" else ((0, -12), "top")
        ax.plot([xv], [val], marker="o", ms=5.5, mfc="#ffffff",
                mec="#2b3138", mew=1.3, zorder=Z_EXTREME_MK)
        ax.annotate("%d %s %.2f" % (ex["year"],
                                    "高" if ex["kind"] == "high" else "低", val),
                    (xv, val), xytext=off, textcoords="offset points",
                    ha="center", va=va, fontsize=8.4, fontweight="bold",
                    color="#2b3138", zorder=Z_EXTREME_TX,
                    bbox=dict(boxstyle="round,pad=0.28", fc="#ffffff",
                              ec="#c1c8d2", lw=0.8))

    ax.set_ylabel("收盘价（港元 · 前复权）", fontsize=10.5, color="#4a5058")
    ax.tick_params(axis="y", labelsize=9.5, colors="#4a5058", length=3)
    ax.grid(axis="y", color=GRID_C, lw=0.6, zorder=0)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    for s in ("left", "bottom", "right"):
        ax.spines[s].set_color("#c8ccd4")

    axr.set_ylabel("营业额（亿元人民币 · 按报告期累计口径）", fontsize=10.5,
                   color="#5c626b")
    axr.tick_params(axis="y", labelsize=9.5, colors="#5c626b", length=3)
    ax.set_yticks(nice_ticks(price_top))
    axr.set_yticks(nice_ticks(rev_top))

    years = list(range(start.year, end.year + 1))
    ax.set_xticks([mdates.date2num(pd.Timestamp("%d-07-01" % y)) for y in years])
    ax.set_xticklabels([str(y) for y in years], fontsize=10.5,
                       color="#3a4048", fontweight="bold")
    ax.tick_params(axis="x", length=0, pad=6)

    handles = [plt.Line2D([], [], color=PRICE_C, lw=1.6,
                          label="收盘价（前复权，港元）")]
    for key in ("FY", "H1"):
        st = STYLE[key]
        handles.append(Rectangle(
            (0, 0), 1, 1, fc=st["color"], alpha=min(st["alpha"] + 0.15, 1.0),
            ec=st["deep"], lw=0.85, hatch=("" if key == "FY" else "///"),
            label="%s营业额（%s，累计%d个月）" % (st["name"], key, st["months"])))
    handles.append(plt.Line2D([], [], marker="o", mfc="#ffffff", mec=NOTE_C,
                              mew=1.3, ls="none", ms=5.5,
                              label="业绩公告后首个交易日股价"))
    handles.append(plt.Line2D([], [], color="#e6e9ef", lw=1.2, ls=(0, (3, 3)),
                              label="业绩公告刊发时点"))
    if q_used:
        handles.append(plt.Line2D([], [], color=QNOTE_C, lw=1.4, ls=(0, (2, 4)),
                                  marker="^", ms=5.0, mec="none",
                                  label="季度业务状况公告（自愿，无营收数据）"))
    ax.legend(handles=handles, loc="lower left", fontsize=9.6, frameon=True,
              framealpha=0.94, ncol=6, columnspacing=1.6,
              bbox_to_anchor=(0.0, 1.032), borderaxespad=0.0)

    ax.set_title("%s（%s.HK）股价 · 营业额 · 披露时点对照图　%d-%d（年报 + 中报）"
                 % (name, code, start.year, end.year),
                 fontsize=15.0, fontweight="bold", color="#1a1d22",
                 loc="left", pad=78)
    fig.text(0.040, 0.115,
             "数据：营业额取自东方财富港股「利润表-按报告期」（项目「营业额」，以人民币列示）；"
             "披露时点取自港交所披露易（业绩公告的实际刊发日期与时间）；"
             "股价为港股日线前复权收盘价（港元，数据截至 %s）。\n"
             "读法：每根柱的横向位置 = 该期业绩公告的刊发日（非报告期末）；"
             "竖虚线为刊发时点，对应的灰色空心点为「公告后首个交易日」收盘价。\n"
             "港股无强制季报，定期财报仅年报（累计12个月）与中报（累计6个月）两类，柱宽随涵盖月份递增；"
             "柱高为累计口径，FY 与 H1 之间不可直接比高低。\n"
             "披露时刻口径：业绩公告分「午间休市刊发」（12:00 前后，当日午后即有反应，取当日收盘）"
             "与「收市后刊发」（16:30-18:00，反应在次日，取次日收盘）两类，图上标注点统一取披露后首个交易日收盘价。\n"
             "币种提示：营业额为人民币、股价为港元，两者量纲不同，本图仅作走势与位置对照，不可相除；"
             "行情起点为 %s，此前披露的报告期未入图。%s\n%s"
             % (end.strftime("%Y-%m-%d"), start.strftime("%Y-%m-%d"),
                footer_extra, q_note),
             fontsize=8.8, color="#7a828d", ha="left", va="top",
             linespacing=1.75)

    os.makedirs(os.path.dirname(os.path.abspath(out_path)) or ".", exist_ok=True)
    fig.savefig(out_path, facecolor="#ffffff")
    plt.close(fig)
    return out_path, pat


def main():
    ap = argparse.ArgumentParser(
        description="港股「营收 × 披露时点 × 股价」一图对照（单面板叠加）")
    ap.add_argument("--code", required=True, help="港股代码，如 09992")
    ap.add_argument("--name", default=None, help="股票简称，缺省用代码")
    ap.add_argument("--start", default=None, help="起始日 YYYY-MM-DD，缺省取行情首日")
    ap.add_argument("--ipo", default=None,
                    help="上市日 YYYY-MM-DD；接口偶发返回上市前的行，给此值即截断")
    ap.add_argument("--end", default=None, help="截止日 YYYY-MM-DD，缺省取今天")
    ap.add_argument("--out", default=None, help="输出 PNG 路径")
    ap.add_argument("--csv", default=None, help="明细 CSV 路径")
    ap.add_argument("--no-csv", action="store_true", help="不导出 CSV")
    ap.add_argument("--extremes", default=None,
                    help="关键高低点，如 2021:high,2022:low,2025:high,2026:low")
    ap.add_argument("--price-mult", type=float, default=1.14)
    ap.add_argument("--rev-mult", type=float, default=1.14)
    ap.add_argument("--json", default=None, help="可选：导出对账 JSON")
    args = ap.parse_args()

    setup_font()
    code = args.code.strip()
    start = pd.Timestamp(args.start) if args.start else None
    end = pd.Timestamp(args.end) if args.end else None

    px = fetch_price(code, start, end, ipo=args.ipo)
    if px.empty:
        raise SystemExit("未取到行情：%s" % code)
    print("行情 %s ~ %s（%d 个交易日%s）"
          % (px["date"].min().date(), px["date"].max().date(), len(px),
             "，已按 --ipo 截断" if args.ipo else ""))
    name = args.name or code

    rev = fetch_revenue(code)
    ann = hkex_announcements(code, y0=2019)
    ann_items = parse_result_announcements(ann)
    print("港交所业绩公告 %d 条：" % len(ann_items))
    for a in ann_items:
        print("   ", a["notice"], "%s %s" % (a["kind"],
              a["period_end"].date()), a["title"][:52])

    q_ann = parse_quarterly_updates(ann)
    print("\n季度业务状况公告（自愿，非定期财报）%d 条：" % len(q_ann))
    for q in q_ann:
        print("   ", q["notice"], "%dQ%d" % (q["year"], q["q"]),
              q["title"][:44])

    items = build_frames(ann_items, rev, px["date"].min())
    if not items:
        raise SystemExit("未取到定期业绩数据：%s" % code)

    extremes = (parse_extremes(args.extremes, px) if args.extremes
                else parse_extremes(
                    ",".join("%d:%s" % (y, k) for y, k in
                             [(2021, "high"), (2022, "low"),
                              (2025, "high"), (2026, "low")]), px))

    out = args.out or os.path.join(
        "out", "%s-revenue-price-timeline.png" % code)
    out, pat = draw(items, px, name, code,
                    [ex for ex in extremes
                     if px["date"].min().year <= ex["year"] <= px["date"].max().year],
                    out, price_mult=args.price_mult, rev_mult=args.rev_mult,
                    q_items=q_ann)
    print("\nPNG ->", os.path.abspath(out))

    for p in pat:
        print("  %-8s 公告 %s  反应日 %s  收 %7.2f  营收 %8.2f 亿  %s"
              % (p["label"], p["notice"], p["reaction_date"],
                 p["reaction_close"], p["rev"],
                 ("%+.1f%%" % p["yoy"]) if p["yoy"] is not None else "—"))

    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump(dict(code=code, name=name, periods=pat,
                           quarterly=[dict(label="%dQ%d" % (q["year"], q["q"]),
                                           notice=q["notice"].strftime(
                                               "%Y-%m-%d %H:%M"),
                                           title=q["title"]) for q in q_ann],
                           price_start=str(px["date"].min().date()),
                           price_end=str(px["date"].max().date()),
                           last_close=round(float(px["close"].iloc[-1]), 2)),
                      f, ensure_ascii=False, indent=2)
        print("JSON ->", os.path.abspath(args.json))

    if not args.no_csv:
        csv_path = args.csv or os.path.join(
            os.path.dirname(out) or ".", "%s_revenue_vs_price.csv" % code)
        os.makedirs(os.path.dirname(os.path.abspath(csv_path)) or ".", exist_ok=True)
        pd.DataFrame(pat).to_csv(csv_path, index=False, encoding="utf-8-sig")
        print("CSV ->", os.path.abspath(csv_path))


if __name__ == "__main__":
    main()
