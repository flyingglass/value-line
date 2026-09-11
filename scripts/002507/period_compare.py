# -*- coding: utf-8 -*-
"""period_compare.py — 涪陵榨菜(002507) 日K / 周K 对照图

用途：判断一张复盘截图用的是「日K」还是「周K」。
方法：同一时间区间分别按 日 / 周 聚合画 K 线，并给出「K 线根数」与「每根占多少像素」，
      与截图对比即可判定周期。

数据口径：data/002507.db kline 表（前复权 qfq）。
          图中「名义价 56.24」= 前复权 2020-09-03 最高 38.21（不复权口径）。

输出：research-wiki/research/疯狂的里海/assets/kline-002507-period-compare.png

用法：.venv\\Scripts\\python scripts\\002507\\period_compare.py
"""
import os
import sqlite3
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
plt.rcParams["font.sans-serif"] = ["Microsoft YaHei"]
plt.rcParams["axes.unicode_minus"] = False

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB = os.path.join(BASE, "data", "002507.db")
OUT_DIR = os.path.join(BASE, "research-wiki", "research", "疯狂的里海", "assets")
OUT_PNG = os.path.join(OUT_DIR, "kline-002507-period-compare.png")

UP, DOWN = "#d93a34", "#1f9e63"        # A 股惯例：涨红跌绿
MA_A, MA_B = "#e08a1e", "#2f6fd0"

FIG_W_IN, DPI = 20.0, 150
AX_PX = 1300.0                          # 单面板轴宽估算（像素），用于算「每根 K 线占几 px」

# 关键点位（前复权价，DB 客观极值）
MARKS = [
    dict(d="2015-09-15", px=3.86, tag="①", txt="① 3.86 全期最低（2015 股灾底）"),
    dict(d="2018-08-01", px=20.54, tag="②", txt="② 20.54 第一波顶"),
    dict(d="2019-07-31", px=13.68, tag="③", txt="③ 13.68 中报暴雷后低点"),
    dict(d="2020-09-03", px=38.21, tag="④", txt="④ 38.21 全期最高（名义价 56.24）"),
    dict(d="2021-02-19", px=36.82, tag="⑤", txt="⑤ 36.82 M 头确认"),
]

# (频率, 起始, 结束, 标题)
PANELS = [
    ("day", "2015-09-01", "2021-06-30", "日K · 2015-09 ~ 2021-06（全区间）"),
    ("week", "2015-09-01", "2021-06-30", "周K · 2015-09 ~ 2021-06（全区间）"),
    ("day", "2020-01-01", "2021-06-30", "日K · 2020-01 ~ 2021-06（放大段）"),
    ("week", "2020-01-01", "2021-06-30", "周K · 2020-01 ~ 2021-06（放大段）"),
]


def load_kline():
    c = sqlite3.connect(DB)
    df = pd.read_sql("select date,open,high,low,close from kline "
                     "where date>='2015-08-01' order by date", c)
    c.close()
    df["date"] = pd.to_datetime(df["date"])
    return df


def to_week(df):
    w = (df.set_index("date")
           .resample("W-FRI")
           .agg({"open": "first", "high": "max", "low": "min", "close": "last"})
           .dropna()
           .reset_index())
    return w


def draw_candles(ax, df, freq):
    x = mdates.date2num(df["date"])
    o, h, l, c = (df[k].to_numpy(dtype=float) for k in ("open", "high", "low", "close"))
    col = np.where(c >= o, UP, DOWN)
    ax.vlines(x, l, h, color=col, lw=0.55 if freq == "day" else 0.85, zorder=2)
    rng = h.max() - l.min()
    hgt = np.maximum(np.abs(c - o), rng * 0.0015)
    ax.bar(x, hgt, bottom=np.minimum(o, c), width=0.62 if freq == "day" else 4.3,
           color=col, edgecolor="none", zorder=3)
    pairs = ((20, MA_A), (60, MA_B)) if freq == "day" else ((10, MA_A), (30, MA_B))
    for n, c_ in pairs:
        ax.plot(x, df["close"].rolling(n).mean().to_numpy(), color=c_, lw=0.9,
                alpha=0.9, zorder=4)


def main():
    df = load_kline()
    wk = to_week(df)

    fig = plt.figure(figsize=(FIG_W_IN, 12.0), dpi=DPI)
    fig.patch.set_facecolor("#ffffff")
    gs = fig.add_gridspec(2, 2, left=0.047, right=0.985, top=0.885, bottom=0.135,
                          hspace=0.30, wspace=0.13)

    for k, (freq, s, e, title) in enumerate(PANELS):
        ax = fig.add_subplot(gs[k // 2, k % 2])
        seg = (df if freq == "day" else wk)
        seg = seg[(seg["date"] >= pd.Timestamp(s)) & (seg["date"] <= pd.Timestamp(e))]
        seg = seg.reset_index(drop=True)
        n = len(seg)
        ax.set_facecolor("#f8fafc" if k % 2 == 0 else "#fdfaf5")
        draw_candles(ax, seg, freq)

        lo, hi = seg["low"].min(), seg["high"].max()
        rng = hi - lo
        ax.set_ylim(lo - rng * 0.10, hi + rng * 0.20)
        ax.set_xlim(pd.Timestamp(s) - pd.Timedelta(days=10),
                    pd.Timestamp(e) + pd.Timedelta(days=10))
        ax.grid(axis="y", color="#e8eaee", lw=0.6, zorder=0)
        ax.set_axisbelow(True)
        for sp in ("top", "right"):
            ax.spines[sp].set_visible(False)
        ax.spines["left"].set_color("#c8ccd4")
        ax.spines["bottom"].set_color("#c8ccd4")
        ax.tick_params(labelsize=8, colors="#4a5058")
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=6 if k < 2 else 3))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%y-%m"))
        for lb in ax.get_xticklabels():
            lb.set_fontsize(8)

        # 关键点位竖线 + 编号
        for m in MARKS:
            t = pd.Timestamp(m["d"])
            if not (pd.Timestamp(s) <= t <= pd.Timestamp(e)):
                continue
            ax.axvline(t, color="#9aa2ae", lw=0.8, ls=":", alpha=0.9, zorder=1.5)
            ax.plot([t], [m["px"]], marker="o", ms=5, mfc="white", mec="#2b3138",
                    mew=1.1, zorder=12)
            ax.annotate(m["tag"], (t, m["px"]), xytext=(0, 11), textcoords="offset points",
                        ha="center", fontsize=10, fontweight="bold", color="#2b3138",
                        zorder=13, clip_on=False)

        ax.set_title("%s\n共 %d 根　｜　每根平均 %.2f px（面板轴宽约 %.0f px）"
                     % (title, n, AX_PX / n, AX_PX),
                     fontsize=11.5, fontweight="bold", color="#1a1d22", loc="left", pad=8)
        ax.set_ylabel("前复权价（元）", fontsize=9, color="#4a5058")

    fig.suptitle("涪陵榨菜（002507）日K / 周K 对照 —— 判断复盘截图的周期\n"
                 "区间约 2015-09 ~ 2021-06（对应你截图中「2015 年低点 → 56.24 次高点」的位置）",
                 fontsize=15, fontweight="bold", color="#1a1d22", x=0.047, ha="left", y=0.975)

    handles = [
        Line2D([], [], color=UP, lw=7, label="阳线"),
        Line2D([], [], color=DOWN, lw=7, label="阴线"),
        Line2D([], [], color=MA_A, lw=1.5, label="均线 A（日K MA20 / 周K MA10）"),
        Line2D([], [], color=MA_B, lw=1.5, label="均线 B（日K MA60 / 周K MA30）"),
        Line2D([], [], marker="o", color="none", mfc="white", mec="#2b3138", ms=7,
               label="关键顶 / 底（前复权）"),
    ]
    fig.legend(handles=handles, loc="lower center", ncol=5, fontsize=9, frameon=False,
               bbox_to_anchor=(0.5, 0.095), handletextpad=0.6, columnspacing=2.4)

    fig.text(0.047, 0.012,
             "关键点位：" + " · ".join(m["txt"] for m in MARKS) + "\n"
             "判据：在约 560 px 宽的截图里，若 2015-09→2020-09 这段的蜡烛能逐根分辨，说明这段约 260 根 → 周K；"
             "若糊成一整条色带、只有价格轮廓，说明约 1210 根 → 日K。\n"
             "口径：本图价格为前复权（qfq，已还原除权除息，供跨期比较）；你截图上的 56.24 是不复权名义价，"
             "同一天（2020-09-03）前复权最高为 38.21。两者不可直接混用。\n"
             "数据：data/002507.db kline 表。",
             fontsize=8.4, color="#5a6068", va="bottom", linespacing=1.7)

    os.makedirs(OUT_DIR, exist_ok=True)
    fig.savefig(OUT_PNG, facecolor="#ffffff")
    plt.close(fig)

    print("已输出 %s" % OUT_PNG)
    for freq, s, e, _ in PANELS:
        seg = df if freq == "day" else wk
        seg = seg[(seg["date"] >= pd.Timestamp(s)) & (seg["date"] <= pd.Timestamp(e))]
        print("%-4s %s ~ %s : %4d 根" % (freq, s, e, len(seg)))


if __name__ == "__main__":
    main()
