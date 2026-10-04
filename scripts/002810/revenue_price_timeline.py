# -*- coding: utf-8 -*-
"""revenue_price_timeline.py — 山东赫达（002810）营收 × 披露时点 × 股价 一图对照

数据：
- 营业收入 / 定期报告披露日：东方财富「利润表-按报告期」(ak.stock_profit_sheet_by_report_em)
  字段 NOTICE_DATE 即该期报告的公开披露日期；涵盖一季报 / 中报 / 三季报 / 年报。
- 行情：新浪日线前复权 (ak.stock_zh_a_daily, adjust="qfq")

读法：
- 单面板叠加：股价线（左轴）与营收柱（右轴）共用同一绘图区与时间轴。
- 全部图元绘制在同一个 axes 内并按 zorder 分层：柱 → 股价线 → 标注，
  因此股价线与各类标注始终位于柱之上，不被遮挡。
- 营收柱的横向位置 = 该期报告的披露日期（非报告期末）。
- 柱宽随涵盖月份递增（Q1=3个月 → FY=12个月），颜色同色系由浅到深。
- 柱高为按报告期口径的累计营业总收入，不同期长度之间不可直接比高低；
  柱顶百分比为「同口径上年同期」的同比。

用法：.venv\\Scripts\\python scripts/002810/revenue_price_timeline.py
"""
import os
import sys
import time

import akshare as ak
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
plt.rcParams["font.sans-serif"] = ["Microsoft YaHei"]
plt.rcParams["axes.unicode_minus"] = False

CODE = "002810"
NAME = "山东赫达"
START = pd.Timestamp("2016-08-26")   # 上市日
END = pd.Timestamp("2026-09-30")

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT_DIR = os.path.join(BASE, "research-wiki", "research", "白马", CODE, "assets")
CSV_DIR = os.path.join(BASE, "scripts", "out")

PRICE_C = "#2f6fd0"
GRID_C = "#e8eaee"
YEAR_C = "#c3ccd9"

# key, 报告期名称关键字, 涵盖月份, 上年同期报告期末(MM-DD), 柱色, 描边/标签色,
# 柱宽(天), 标签字号, zorder, 透明度, 标签上移(pt)
KINDS = [
    # 四类报告期各用一个色相：一季报蓝 / 中报青绿 / 三季报橙 / 年报紫
    ("Q1", "一季报", 3, "03-31", "#8fbde2", "#2f6a99", 22.0, 7.4, 4.2, 0.92, 18.0),
    ("H1", "中报", 6, "06-30", "#63bda6", "#227a63", 30.0, 8.0, 3.9, 0.82, 8.0),
    ("Q3", "三季报", 9, "09-30", "#f0ad4e", "#a9610d", 38.0, 7.4, 3.6, 0.75, 30.0),
    ("FY", "年报", 12, "12-31", "#9b86c4", "#4f3d78", 46.0, 8.6, 3.0, 0.48, 8.0),
]
STYLE = {k[0]: dict(name=k[1], months=k[2], prev=k[3], color=k[4], deep=k[5],
                    width=k[6], fs=k[7], z=k[8], alpha=k[9], up=k[10])
         for k in KINDS}
NOTE_C = "#6b7280"          # 披露日股价点（中性色，避免与柱色混淆）
DRAW_ORDER = ["FY", "Q3", "H1", "Q1"]

# 图层顺序（同一个 axes 内 zorder 从小到大依次压盖）
Z_BAR = None                # 柱：沿用 KINDS 中的 z（3.0~4.2）
Z_LINE = 6.0                # 股价线：压在全部柱之上
Z_LABEL = 8.0               # 营收柱标签：压在股价线之上
Z_NOTE = 9.0                # 披露当日股价点
Z_EXTREME_MK = 10.0         # 关键高低点标记
Z_EXTREME_TX = 12.0         # 关键高低点文字


def _retry(fn, n=4, wait=2.0):
    last = None
    for i in range(n):
        try:
            return fn()
        except Exception as e:                       # noqa: BLE001
            last = e
            time.sleep(wait)
    raise last


def fetch_reports():
    df = _retry(lambda: ak.stock_profit_sheet_by_report_em(symbol="SZ" + CODE))
    cols = ["REPORT_DATE", "REPORT_DATE_NAME", "NOTICE_DATE",
            "TOTAL_OPERATE_INCOME"]
    df = df[cols].copy()
    df["REPORT_DATE"] = pd.to_datetime(df["REPORT_DATE"])
    df["NOTICE_DATE"] = pd.to_datetime(df["NOTICE_DATE"])
    df["rev"] = df["TOTAL_OPERATE_INCOME"] / 1e8
    # 保留 2015 及以前报告期，仅作为同比基准；上市前披露/上市前报告期的条目不画
    df = df[df["REPORT_DATE"] >= "2015-01-01"]
    return df.sort_values("REPORT_DATE").reset_index(drop=True)


def fetch_price():
    d = _retry(lambda: ak.stock_zh_a_daily(symbol="sz" + CODE, adjust="qfq"))
    d["date"] = pd.to_datetime(d["date"])
    d = d[(d["date"] >= START) & (d["date"] <= END)]
    return d.reset_index(drop=True)


def build_frames(rep):
    """返回定期报告列表：一季报 / 中报 / 三季报 / 年报。"""
    rev_of = dict(zip(rep["REPORT_DATE"].dt.strftime("%Y-%m-%d"), rep["rev"]))
    items = []
    for _, r in rep.iterrows():
        if r["NOTICE_DATE"] < START or r["REPORT_DATE"] < START:
            continue                      # 上市前披露或报告期在上市前，不进时间轴
        for key, kw, months, prev_md, *_ in KINDS:
            if kw not in r["REPORT_DATE_NAME"]:
                continue
            y = r["REPORT_DATE"].year
            if r["REPORT_DATE"].strftime("%m-%d") != prev_md:
                continue
            prev = rev_of.get("%d-%s" % (y - 1, prev_md))
            yoy = None if prev is None or not np.isfinite(prev) else \
                (r["rev"] / prev - 1.0) * 100.0
            items.append(dict(kind=key, year=y, rev=float(r["rev"]), yoy=yoy,
                              notice=r["NOTICE_DATE"],
                              period_end=r["REPORT_DATE"],
                              label=("FY%d" % y) if key == "FY"
                              else ("%d%s" % (y, key))))
            break
    return sorted(items, key=lambda it: it["notice"])


def price_at(px, ts):
    seg = px[px["date"] <= ts]
    if len(seg):
        return float(seg["close"].iloc[-1])
    return float(px["close"].iloc[0])


def draw(items, px):
    x_px = mdates.date2num(px["date"])
    y_px = px["close"].to_numpy(dtype=float)

    x0, x1 = mdates.date2num(START) - 45, mdates.date2num(END) + 45
    lo, hi = float(np.nanmin(y_px)), float(np.nanmax(y_px))
    rev_max = max(it["rev"] for it in items)

    # 单一绘图区：左轴 = 股价（元），右轴 = 营收（亿元），两者共用同一时间轴。
    # 用 secondary_yaxis 只做右侧刻度换算，不新建 axes，因此柱 / 股价线 / 标注
    # 都在同一图层栈里，zorder 可以严格排序。
    price_top = hi * 1.14
    rev_top = rev_max * 1.14
    scale = price_top / rev_top          # 亿元 → 左轴价格坐标

    fig = plt.figure(figsize=(29.0, 12.4), dpi=150)
    fig.patch.set_facecolor("#ffffff")
    gs = fig.add_gridspec(1, 1, left=0.040, right=0.962, top=0.856, bottom=0.152)
    ax = fig.add_subplot(gs[0])
    ax.set_facecolor("#fafbfc")
    ax.set_ylim(0, price_top)
    ax.set_xlim(x0, x1)
    axr = ax.secondary_yaxis("right",
                             functions=(lambda v: v / scale, lambda v: v * scale))

    # ---- 年份分隔 + 披露时点竖虚线 ----
    for y in range(2017, 2027):
        ax.axvline(mdates.date2num(pd.Timestamp("%d-01-01" % y)),
                   color=YEAR_C, lw=1.0, zorder=1.0)
    for ts in sorted({it["notice"] for it in items}):
        ax.axvline(mdates.date2num(ts), color="#e6e9ef", lw=0.85,
                   ls=(0, (3, 3)), zorder=1.2)

    # ================= 营收柱（按披露日定位，位于最底层）=================
    for key in DRAW_ORDER:
        st = STYLE[key]
        for it in [i for i in items if i["kind"] == key]:
            xv = mdates.date2num(it["notice"])
            ax.bar(xv, it["rev"] * scale, width=st["width"], bottom=0.0,
                   color=st["color"], alpha=st["alpha"], edgecolor=st["deep"],
                   linewidth=0.85, hatch=("" if key == "FY" else "///"),
                   zorder=st["z"])
            if key in ("FY", "H1"):
                txt = "%s  %.2f亿" % (it["label"], it["rev"])
                if it["yoy"] is not None:
                    txt += "\n%+.1f%%" % it["yoy"]
            else:
                txt = "%s %.2f亿" % (it["label"][2:], it["rev"])   # 17Q1 1.37亿
                if it["yoy"] is not None:
                    txt += " %+.1f%%" % it["yoy"]
            ax.annotate(txt, (xv, it["rev"] * scale), xytext=(0, st["up"]),
                        textcoords="offset points", ha="center", va="bottom",
                        fontsize=st["fs"], fontweight="bold",
                        color=st["deep"], zorder=Z_LABEL + st["z"] * 0.1,
                        linespacing=1.32)
            # 年报/中报/三季报在柱底标注披露日期；一季报多与年报同日披露，省略以免重叠
            if key in ("FY", "H1", "Q3"):
                ax.annotate(it["notice"].strftime("%m-%d"), (xv, 0),
                            xytext=(0, -13), textcoords="offset points",
                            ha="center", va="top", fontsize=7.0,
                            color="#8b939e", zorder=Z_LABEL + st["z"] * 0.1)

    # ================= 股价线：压在全部柱之上 =================
    ax.plot(x_px, y_px, color=PRICE_C, lw=1.2, zorder=Z_LINE)

    # ================= 标注：位于最上层 =================
    # 披露当日股价标记
    for key in DRAW_ORDER:
        for it in [i for i in items if i["kind"] == key]:
            xv = mdates.date2num(it["notice"])
            ax.plot([xv], [price_at(px, it["notice"])], marker="o",
                    ms=5.4 if key == "FY" else 4.6, mfc="#ffffff",
                    mec=NOTE_C, mew=1.25, zorder=Z_NOTE)

    # ---- 关键高低点 ----
    for yr in (2018, 2021, 2024, 2026):
        seg = px[px["date"].dt.year == yr]
        if seg.empty:
            continue
        if yr in (2021, 2026):
            i = seg["close"].idxmax()
            val = float(seg.loc[i, "close"])
            off, va = (0, 10), "bottom"
        else:
            i = seg["close"].idxmin()
            val = float(seg.loc[i, "close"])
            off, va = (0, -12), "top"
        xv = mdates.date2num(seg.loc[i, "date"])
        ax.plot([xv], [val], marker="o", ms=5.5, mfc="#ffffff",
                mec="#2b3138", mew=1.3, zorder=Z_EXTREME_MK)
        ax.annotate("%d %s %.2f" % (yr, "高" if yr in (2021, 2026) else "低",
                                    val),
                    (xv, val), xytext=off, textcoords="offset points",
                    ha="center", va=va, fontsize=8.4, fontweight="bold",
                    color="#2b3138", zorder=Z_EXTREME_TX,
                    bbox=dict(boxstyle="round,pad=0.28", fc="#ffffff",
                              ec="#c1c8d2", lw=0.8))

    # ---- 坐标轴外观 ----
    ax.set_ylabel("收盘价（元 · 前复权）", fontsize=10.5, color="#4a5058")
    ax.tick_params(axis="y", labelsize=9.5, colors="#4a5058", length=3)
    ax.grid(axis="y", color=GRID_C, lw=0.6, zorder=0)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["left"].set_color("#c8ccd4")
    ax.spines["bottom"].set_color("#c8ccd4")
    ax.spines["right"].set_color("#c8ccd4")

    axr.set_ylabel("营业总收入（亿元 · 按报告期累计口径）", fontsize=10.5,
                   color="#5c626b")
    axr.tick_params(axis="y", labelsize=9.5, colors="#5c626b", length=3)
    # 两侧都用整数刻度，避免出现 17.5 / 12.5 这类读数
    ax.set_yticks(np.arange(0.0, price_top + 1e-9, 10.0))
    axr.set_yticks(np.arange(0.0, rev_top + 1e-9, 5.0))

    # ---- X 轴：年份刻度 ----
    ticks = [mdates.date2num(pd.Timestamp("%d-07-01" % y))
             for y in range(2016, 2027)]
    ax.set_xticks(ticks)
    ax.set_xticklabels([str(y) for y in range(2016, 2027)],
                       fontsize=10.5, color="#3a4048", fontweight="bold")
    ax.tick_params(axis="x", length=0, pad=6)

    # ---- 图例 ----
    handles = [plt.Line2D([], [], color=PRICE_C, lw=1.6,
                          label="收盘价（前复权）")]
    for key in ("FY", "Q3", "H1", "Q1"):
        st = STYLE[key]
        handles.append(Rectangle(
            (0, 0), 1, 1, fc=st["color"], alpha=min(st["alpha"] + 0.15, 1.0),
            ec=st["deep"], lw=0.85,
            hatch=("" if key == "FY" else "///"),
            label="%s营收（%s，累计%d个月）"
                  % (st["name"], key, st["months"])))
    handles.append(plt.Line2D([], [], marker="o", mfc="#ffffff",
                              mec=NOTE_C, mew=1.3, ls="none", ms=5.5,
                              label="定期报告披露当日股价"))
    handles.append(plt.Line2D([], [], color="#e6e9ef", lw=1.2,
                              ls=(0, (3, 3)), label="定期报告披露时点"))
    ax.legend(handles=handles, loc="upper left", fontsize=9.0,
              frameon=True, framealpha=0.94, ncol=7, columnspacing=1.4,
              bbox_to_anchor=(0.0, 1.076), borderaxespad=0.0)

    ax.set_title("%s（%s）股价 · 营收 · 披露时点对照图　2016-2026（含季报）"
                 % (NAME, CODE),
                 fontsize=15.0, fontweight="bold", color="#1a1d22",
                 loc="left", pad=46)
    fig.text(0.040, 0.115,
             "数据：营业收入与定期报告披露日取自东方财富「利润表-按报告期」（NOTICE_DATE 为该期报告公开披露日）；"
             "股价为新浪日线前复权收盘价。\n"
             "读法：股价线（左轴）与营收柱（右轴）共用同一时间轴并叠加于同一绘图区；"
             "每根营收柱的横向位置 = 该期报告的披露日期（非报告期末），"
             "竖虚线标示披露时点，与虚线对应的灰色空心点即披露当日收盘价。\n"
             "图层顺序：营收柱 → 股价线 → 各类标注（柱顶标签、披露日股价点、高低点），"
             "标注与股价线始终压在柱之上。\n"
             "四类报告期用四种颜色区分（一季报蓝 / 中报青绿 / 三季报橙 / 年报紫），柱宽随涵盖月份递增（3→12个月）。\n"
             "口径：柱高为按报告期累计的营业总收入（Q1=3个月、H1=6个月、Q3=9个月、FY=12个月），"
             "不同期长度之间不可直接比高低；柱顶百分比为同口径上年同期同比，单位为亿元。",
             fontsize=8.8, color="#7a828d", ha="left", va="top",
             linespacing=1.75)

    os.makedirs(OUT_DIR, exist_ok=True)
    out = os.path.join(OUT_DIR, "revenue-price-timeline.png")
    fig.savefig(out, facecolor="#ffffff")
    plt.close(fig)
    return out


def dump_csv(items, px):
    os.makedirs(CSV_DIR, exist_ok=True)
    rows = [dict(kind=it["kind"], label=it["label"], rev_yi=it["rev"],
                 yoy_pct=it["yoy"],
                 period_end=it["period_end"].strftime("%Y-%m-%d"),
                 notice_date=it["notice"].strftime("%Y-%m-%d"),
                 px_on_notice=round(price_at(px, it["notice"]), 2))
            for it in items]
    df = pd.DataFrame(rows).sort_values(["notice_date", "kind"])
    p = os.path.join(CSV_DIR, "002810_revenue_vs_price.csv")
    df.to_csv(p, index=False, encoding="utf-8-sig")
    return p, df


def main():
    rep = fetch_reports()
    px = fetch_price()
    items = build_frames(rep)
    csv_path, df = dump_csv(items, px)
    print(df.to_string(index=False))
    print("\nCSV ->", csv_path)
    print("PNG ->", draw(items, px))


if __name__ == "__main__":
    main()
