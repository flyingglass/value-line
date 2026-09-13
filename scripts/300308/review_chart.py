# -*- coding: utf-8 -*-
"""review_chart.py — 中际旭创(300308) 行情复盘图（周K）

样式对齐 research-wiki/research/疯狂的里海/assets/kline-*-review.png。
"""
import os
import sqlite3
import sys

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
plt.rcParams["font.sans-serif"] = ["Microsoft YaHei"]
plt.rcParams["axes.unicode_minus"] = False

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB = os.path.join(BASE, "data", "300308.db")
ASSETS = os.path.join(BASE, "research-wiki", "research", "疯狂的里海", "assets")

UP, DOWN = "#d93a34", "#1f9e63"
PHASE_EC = "#2f6fd0"
YEAR_C, MID_C = "#c3ccd9", "#b9c3d1"
LEVEL_C = "#b3261e"
PHASE_BG = ["#f4f7fb", "#fbf7f0"]

SPEC = dict(
    name="中际旭创", start="2018-01-01",
    title=("中际旭创（300308）行情复盘 · 周K（前复权）· 2018-2026",
           "数据驱动复盘；本图不含「里海买卖点」——中际旭创不是里海案例标的"),
    footnote=("数据：data/300308.db（kline 前复权 qfq，按周 W-FRI 聚合成周K）\n"
              "口径：前复权连续价；顶底由脚本自动定位年份最高/最低周，未手填。"),
    phases=[
        ("2018-01-01", "2019-12-31", "阶段一 · 区间震荡\n2018-2019"),
        ("2020-01-01", "2022-12-31", "阶段二 · 冲高回落\n2020-2022"),
        ("2023-01-01", "2023-12-31", "阶段三 · 主升启动\n2023"),
        ("2024-01-01", "2026-12-31", "阶段四 · 加速主升\n2024-2026"),
    ],
    trades=[],
    hilo=[
        ("2022", "L", "2022 低点：启动前夜"),
        ("2023", "H", "2023 高点：主升元年"),
        ("2025", "H", "2025 高点"),
        ("2026", "H", "2026 高点"),
    ],
    levels=[
        (121.06, "2023 高点 121.06", LEVEL_C),
        (658.02, "2025 高点 658.02", "#5a6473"),
    ],
)


def load_kline(code, start):
    c = sqlite3.connect(DB)
    df = pd.read_sql("select date,open,high,low,close,volume from kline "
                     "where date>=? order by date", c, params=(start,))
    c.close()
    df["date"] = pd.to_datetime(df["date"])
    return df


def to_week(df):
    return (df.set_index("date").resample("W-FRI")
              .agg({"open": "first", "high": "max", "low": "min",
                    "close": "last", "volume": "sum"})
              .dropna().reset_index())


def week_pos(wi, t):
    t = pd.Timestamp(t)
    return int(np.clip(np.searchsorted(wi, t.to_datetime64(), side="right") - 1,
                       0, len(wi) - 1))


def year_extreme(w, year, kind):
    seg = w[w["date"].dt.year == int(year)]
    if seg.empty:
        return None
    i = seg["high"].idxmax() if kind == "H" else seg["low"].idxmin()
    return int(w.index.get_loc(i)), float(w.loc[i, "high" if kind == "H" else "low"])



def draw_candles(ax, seg, idx, lw=0.55, width=0.82):
    o, h, l, cl = (seg[k].to_numpy(dtype=float)
                   for k in ("open", "high", "low", "close"))
    colors = np.where(cl >= o, UP, DOWN)
    ax.add_collection(LineCollection(
        [[(i, lo), (i, hi)] for i, lo, hi in zip(idx, l, h)],
        colors=colors, linewidths=lw, zorder=2))
    rng = h.max() - l.min()
    bot = np.minimum(o, cl)
    hgt = np.maximum(np.abs(cl - o), rng * 0.0016)
    ax.bar(idx, hgt, bottom=bot, width=width, color=colors,
           edgecolor="none", zorder=3)


def draw(spec):
    w = to_week(load_kline("300308", spec["start"]))
    wi = w["date"].to_numpy()
    n = len(w)

    fig = plt.figure(figsize=(21, 9.6), dpi=150)
    fig.patch.set_facecolor("#ffffff")
    gs = fig.add_gridspec(2, 1, height_ratios=[4.0, 0.72],
                          left=0.052, right=0.984, top=0.885, bottom=0.155,
                          hspace=0.205)
    ax_m = fig.add_subplot(gs[0])
    ax_v = fig.add_subplot(gs[1], sharex=ax_m)
    idx_all = np.arange(n)
    draw_candles(ax_m, w, idx_all)

    lo, hi = w["low"].min(), w["high"].max()
    rng = hi - lo
    y0, y1 = lo - rng * 0.10, hi + rng * 0.20
    ax_m.set_ylim(y0, y1)
    ax_m.set_xlim(-6, n + 6)
    ax_m.grid(axis="y", color="#e8eaee", lw=0.6, zorder=0)
    ax_m.set_axisbelow(True)
    for s in ("top", "right"):
        ax_m.spines[s].set_visible(False)
    ax_m.spines["left"].set_color("#c8ccd4")
    ax_m.spines["bottom"].set_color("#c8ccd4")
    ax_m.tick_params(labelsize=9, colors="#4a5058", length=3, axis="y")
    ax_m.set_ylabel("前复权价（元）· 周K", fontsize=10, color="#4a5058")

    for i, ph in enumerate(spec["phases"]):
        p0, p1 = week_pos(wi, ph[0]), week_pos(wi, ph[1])
        ax_m.add_patch(Rectangle((p0 - 0.5, y0), (p1 - p0 + 1), (y1 - y0),
                                 fc=PHASE_BG[i % 2], ec=PHASE_EC, lw=1.2,
                                 ls=(0, (5, 3)), alpha=0.5, zorder=1.1))
        ax_m.annotate(ph[2].replace("\n", "　"),
                      ((p0 + p1) / 2.0, y1 - (y1 - y0) * 0.05),
                      ha="center", va="center", fontsize=9.6, fontweight="bold",
                      color="#2b3138", zorder=6,
                      bbox=dict(boxstyle="round,pad=0.42", fc="#ffffff",
                                ec="#9aa2ae", lw=1.0, alpha=0.94))

    for px, txt, col in spec["levels"]:
        ax_m.axhline(px, color=col, lw=1.1, ls=(0, (6, 4)), alpha=0.55,
                     zorder=1.5)
        ax_m.annotate(txt, (2, px), xytext=(0, 3), textcoords="offset points",
                      ha="left", va="bottom", fontsize=8.6, fontweight="bold",
                      color=col, zorder=22,
                      bbox=dict(boxstyle="round,pad=0.28", fc="#ffffff",
                                ec=col, lw=0.7, alpha=0.92))

    for item in spec["hilo"]:
        got = year_extreme(w, item[0], item[1])
        if got is None:
            continue
        p, px = got
        up = item[1] == "H"
        ax_m.plot([p], [px], marker="o", ms=6, mfc="white", mec="#2b3138",
                  mew=1.2, zorder=12)
        ax_m.annotate("%s-%s · %.2f %s"
                      % (item[0], w.loc[p, "date"].strftime("%m-%d"), px, item[2]),
                      (p, px), xytext=(6 if p > n * 0.86 else 0, 14 if up else -16),
                      textcoords="offset points",
                      ha="right" if p > n * 0.86 else "center",
                      va="bottom" if up else "top",
                      fontsize=8.6, fontweight="bold",
                      color="#2b3138", zorder=26,
                      bbox=dict(boxstyle="round,pad=0.30", fc="#ffffff",
                                ec="#c1c8d2", lw=0.8))

    yrs = pd.Series(wi).dt.year
    ypos = [int(i) for i in yrs.ne(yrs.shift()).to_numpy().nonzero()[0]]
    ypos = [p for p in ypos if p < n]
    for p in ypos:
        ax_m.axvline(p, color=YEAR_C, lw=1.1, zorder=1.25)
        ax_v.axvline(p, color=YEAR_C, lw=1.1, zorder=0.6)

    jul = pd.Series(wi).dt.month.eq(7)
    for i in jul.ne(jul.shift()).to_numpy().nonzero()[0]:
        if not jul.iloc[i]:
            continue
        ax_m.axvline(int(i), color=MID_C, lw=0.95, ls=(0, (4, 3)), zorder=1.24)
        ax_v.axvline(int(i), color=MID_C, lw=0.95, ls=(0, (4, 3)), zorder=0.6)

    ax_m.set_xticks(ypos)
    ax_m.set_xticklabels([])
    ax_m.tick_params(axis="x", length=0)

    ax_m.set_title((spec["title"][0] + "\n" + spec["title"][1]),
                   fontsize=13.2, fontweight="bold", color="#1a1d22",
                   loc="left", pad=16)

    vcol = np.where(w["close"].to_numpy() >= w["open"].to_numpy(), UP, DOWN)
    ax_v.bar(idx_all, w["volume"].to_numpy() / 1e8, width=0.82, color=vcol,
             edgecolor="none", zorder=3)
    ax_v.set_ylim(0, w["volume"].max() / 1e8 * 1.28)
    ax_v.set_ylabel("周成交量（亿股）", fontsize=9, color="#6a7280")
    ax_v.grid(axis="y", color="#eef0f3", lw=0.6, zorder=0)
    ax_v.set_axisbelow(True)
    for s in ("top", "right"):
        ax_v.spines[s].set_visible(False)
    ax_v.spines["left"].set_color("#c8ccd4")
    ax_v.spines["bottom"].set_color("#c8ccd4")
    ax_v.tick_params(labelsize=9, colors="#4a5058", length=3)
    ax_v.set_xticks(ypos)
    ax_v.set_xticklabels([str(y) for y in sorted(set(yrs))][:len(ypos)],
                         fontsize=10, color="#3a4048", fontweight="bold")
    ax_v.tick_params(axis="x", length=0, pad=6)

    for x in (0.052, 0.984):
        fig.add_artist(Line2D([x, x], [0.155, 0.885], transform=fig.transFigure,
                              color="#e3e6ea", lw=0.9, zorder=0.5))

    fig.text(0.052, 0.118, spec["footnote"], fontsize=8.6, color="#7a828d",
             ha="left", va="top", linespacing=1.7)

    os.makedirs(ASSETS, exist_ok=True)
    out = os.path.join(ASSETS, "kline-300308-review.png")
    fig.savefig(out, facecolor="#ffffff")
    plt.close(fig)
    return out


def main():
    print("OK", draw(SPEC))


if __name__ == "__main__":
    main()