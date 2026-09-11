# -*- coding: utf-8 -*-
"""review_chart.py — 涪陵榨菜(002507) 战略股复盘图（周K）

四件事：
  1) 周K 主图：2015-2026 全景 + 关键顶底 + 里海买卖点 + 时间轴
  2) 主图标注业绩快报 / 业绩预告披露时点（13 条：每年 2 月披露 → 次年业绩先声）
  3) 标注关键顶部、底部（价格 + 日期）；关键水平位（阻力 / 新低）
  4) 标注里海（疯狂的里海）买点 / 卖点（日期 + 当时名义价）

数据口径：
  · 价格 = data/002507.db kline 表（前复权 qfq），为连续可比价
  · 公告日 = data/disclosure/002507_disclosure.json（巨潮资讯 cninfo 实际披露日）
  · 买卖点价位 = 案例原文的「当时实际成交价（名义价）」，与前复权价不同口径：
    图上按日期定位、以文字标注名义价，脚注已说明
  · 买卖点 / 事件出处见 research-wiki/research/疯狂的里海/案例/里海案例-涪陵榨菜.md

输出：research-wiki/research/疯狂的里海/assets/kline-002507-review.png

用法：.venv\\Scripts\\python scripts\\002507\\review_chart.py
"""
import io
import json
import os
import re
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
DB = os.path.join(BASE, "data", "002507.db")
DISC_JSON = os.path.join(BASE, "data", "disclosure", "002507_disclosure.json")
OUT_DIR = os.path.join(BASE, "research-wiki", "research", "疯狂的里海", "assets")
OUT_PNG = os.path.join(OUT_DIR, "kline-002507-review.png")

UP, DOWN = "#d93a34", "#1f9e63"          # A 股惯例：涨红跌绿
MAS = (5, 10, 20, 30, 60)                # 均线周期（周）
MA5_C, MA10_C, MA20_C = "#d9a209", "#e08a1e", "#d2569b"
MA30_C, MA60_C = "#2f6fd0", "#8a63c9"
REPORT_C, QUICK_C = "#5a6473", "#c2570c"
BUY_C, SELL_C, ANCHOR_C = "#c62828", "#0b7a4b", "#1f5fb0"
PHASE_BG = ["#f4f7fb", "#fbf7f0"]

# ---------------------------------------------------------------------------
# 一、里海买卖点（出处：里海案例-涪陵榨菜.md；价位为原文「当时实际价」）
# ---------------------------------------------------------------------------
TRADES = [
    dict(date="2019-04-26", side="S", tag="S1",
         text="S1 2019-04-26 卖出大半 ≈30 元\n（底仓 +200%、加仓 +80%）",
         short="S1 2019-04-26 减仓 ≈30 元", prefer="up", off=(0, -34)),
    dict(date="2019-11-18", side="B", tag="B2",
         text="B2 2019-11-18 买回：坏财报砸不动 = 业绩底",
         short="B2 2019-11-18 买回", prefer="down", off=(-62, -30)),
    dict(date="2020-01-07", side="B", tag="B3",
         text="B3 2020-01-07 示范账户建仓 3800 股 @25.10",
         short="B3 2020-01-07 建仓 @25.10", prefer="down", off=(62, 30)),
    dict(date="2020-04-23", side="S", tag="S2",
         text="S2 2020-04-23 卖 1200 股 @36（换再升）",
         short="S2 2020-04-23 减仓 @36", prefer="up", off=(-62, 32)),
    dict(date="2020-09-04", side="S", tag="S3",
         text="S3 2020-09-04 清仓 2600 股 @49.2\n10 天后 9.29 切鲁西 8.95",
         short="S3 2020-09-04 清仓 @49.2", prefer="up", off=(0, 95)),
    dict(date="2022-11-07", side="B", tag="观察",
         text="买 100 股弱跟踪", short="2022-11-07 买 100 股（观察）",
         prefer="down", off=(0, -28)),
    dict(date="2025-09-24", side="B", tag="观察",
         text="再买 100 股弱跟踪", short="2025-09-24 买 100 股（观察）",
         prefer="down", off=(-52, 28)),
]

# 区间建仓（案例只给年份，未披露具体日期 → 用区间带表示，不臆造日期）
BANDS = [
    dict(start="2016-01-01", end="2016-12-31", label="2016 年内建仓：账户全部资金（不到 10 万）\n"
                                                   "市值 30 多亿、预估净利冲 2 亿（案例只给年份）"),
]

# 中性锚点（非买卖点）
ANCHORS = [
    dict(date="2017-01-03", text="主仓复盘起算 8.44 元\n（2019.9.11 统计口径）"),
]

# ---------------------------------------------------------------------------
# 二、关键顶底（前复权周K 客观极值 + 当时事件）
# ---------------------------------------------------------------------------
HILO = [
    dict(date="2015-09-15", kind="L", px=3.86, tag="①", text="① 2015-09-15 · 3.86 全期最低（2015 股灾底）", prefer="down"),
    dict(date="2016-02-29", kind="L", px=3.91, tag="②", text="② 2016-02-29 · 3.91 二次探底", prefer="down", dx=60),
    dict(date="2017-11-22", kind="H", px=12.69, tag="③", text="③ 2017-11-22 · 12.69 新高（《庆涪陵榨菜新高》）", prefer="up"),
    dict(date="2018-08-01", kind="H", px=20.54, tag="④", text="④ 2018-08-01 · 20.54 第一波顶（年报预收/现金流走弱）", prefer="up"),
    dict(date="2019-04-01", kind="H", px=21.38, tag="⑤", text="⑤ 2019-04-01 · 21.38 前高未破（双顶）", prefer="up", dx=60),
    dict(date="2019-07-31", kind="L", px=13.68, tag="", text="2019-07-31 · 13.68 中报暴雷后低点", prefer="down"),
    dict(date="2020-09-03", kind="H", px=38.21, tag="⑥", text="⑥ 2020-09-03 · 38.21 全期最高（当时名义价 ≈56）", prefer="up"),
    dict(date="2021-02-19", kind="H", px=36.82, tag="⑦", text="⑦ 2021-02-19 · 36.82 M 头右肩", prefer="up"),
    dict(date="2022-10-31", kind="L", px=15.33, tag="⑧", text="⑧ 2022-10-31 · 15.33（三剑客收官 -25.54%）", prefer="down"),
    dict(date="2023-12-27", kind="L", px=12.57, tag="", text="2023-12-27 · 12.57", prefer="down"),
    dict(date="2024-10-08", kind="H", px=16.11, tag="⑨", text="⑨ 2024-10-08 · 16.11（924 行情脉冲高点）", prefer="up"),
    dict(date="2026-06-29", kind="L", px=10.61, tag="⑩", text="⑩ 2026-06-29 · 10.61 十一年新低：净利 7 亿一分没跌，股价跌回 2016 起点", prefer="down"),
]

# ---------------------------------------------------------------------------
# 三、重要事件（有原文出处）
# ---------------------------------------------------------------------------
NOTES = [
    dict(date="2016-10-31", text="2016.11-2017.1 作者复盘「最佳切入点」\n（提价 8-12%、销量不降）", prefer="up"),
    dict(date="2017-01-23", text="2017.1.23 业绩预告修正\n→ 跳空启动", prefer="up"),
    dict(date="2019-07-30", text="2019.7.30 中报前预警「暴雷可预判」\n次日中报：Q2 净利 -16.18%", prefer="up"),
    dict(date="2021-01-01", text="2021.1.1 定位降级为「白马股杀业绩」", prefer="up"),
    dict(date="2026-06-29", text="2026.6.9「股价跌 80%，业绩 7 亿一分没跌」", prefer="down"),
]

# 阶段划分（主图区间框 + 分阶段面板）
PHASES = [
    dict(s="2015-01-01", e="2016-12-31", tag="阶段一", name="底部孕育",
         short="阶段一 · 底部孕育\n2015-2016",
         full="阶段一 · 底部孕育（股灾底 → 二次探底 → 起涨前夜）"),
    dict(s="2017-01-01", e="2018-12-31", tag="阶段二", name="提价周期主升",
         short="阶段二 · 提价主升\n2017-2018",
         full="阶段二 · 提价周期主升（业绩预告跳空启动）"),
    dict(s="2019-01-01", e="2020-12-31", tag="阶段三", name="暴雷洗盘 → 第二波爆炒",
         short="阶段三 · 暴雷洗盘 → 第二波爆炒\n2019-2020",
         full="阶段三 · 暴雷洗盘 → 第二波爆炒（见历史大顶）"),
    dict(s="2021-01-01", e="2022-12-31", tag="阶段四", name="杀估值元年",
         short="阶段四 · 杀估值元年（M 头）\n2021-2022",
         full="阶段四 · 杀估值元年（M 头确认）"),
    dict(s="2023-01-01", e="2024-12-31", tag="阶段五", name="成长停滞后横盘阴跌",
         short="阶段五 · 成长停滞阴跌\n2023-2024",
         full="阶段五 · 成长停滞后横盘阴跌"),
    dict(s="2025-01-01", e="2026-12-31", tag="阶段六", name="债券分红股化",
         short="阶段六 · 债券分红股化\n2025-2026",
         full="阶段六 · 债券分红股化（十一年新低）"),
]


# ---------------------------------------------------------------------------
# 数据加载
# ---------------------------------------------------------------------------
def load_kline():
    c = sqlite3.connect(DB)
    df = pd.read_sql("select date,open,high,low,close,volume from kline "
                     "where date>='2015-01-01' order by date", c)
    c.close()
    df["date"] = pd.to_datetime(df["date"])
    return df


def to_week(df):
    """日K → 周K（W-FRI），索引为周五日期。"""
    w = (df.set_index("date")
           .resample("W-FRI")
           .agg({"open": "first", "high": "max", "low": "min",
                 "close": "last", "volume": "sum"})
           .dropna()
           .reset_index())
    for n in MAS:
        w["ma%d" % n] = w["close"].rolling(n).mean()
    return w


PERIOD_PAT = [
    (re.compile(r"^(\d{4})年年度报告$"), "年报"),
    (re.compile(r"^(\d{4})年半年度报告$"), "中报"),
    (re.compile(r"^(\d{4})年(?:第一|一)季度报告(?:全文|正文)?$"), "Q1"),
    (re.compile(r"^(\d{4})年(?:第三|三)季度报告(?:全文|正文)?$"), "Q3"),
    (re.compile(r"^(\d{4})年度业绩快报"), "快报"),
    (re.compile(r"^(\d{4})年度业绩预告"), "预告"),
]
# 底部短线标签：两位年份 + 报告期缩写（A=年报 / H1=中报 / Q1 / Q3；快=业绩快报 / 预=业绩预告）
LABEL_FMT = {"年报": "%sA", "中报": "%sH1", "Q1": "%sQ1",
             "Q3": "%sQ3", "快报": "%s快", "预告": "%s预"}


def load_disclosures():
    """→ [{date, kind, label}]，同一天同一报告期去重。"""
    raw = json.load(io.open(DISC_JSON, encoding="utf-8"))["disclosures"]
    out, seen = [], set()
    for d in raw:
        t = d["title"]
        if "已取消" in t:
            continue
        for rx, kind in PERIOD_PAT:
            m = rx.match(t)
            if not m:
                continue
            year = m.group(1)
            key = (d["date"], year, kind)
            if key in seen:
                break
            seen.add(key)
            out.append(dict(date=pd.Timestamp(d["date"]), kind=kind,
                            label=LABEL_FMT[kind] % year[2:]))
            break
    return sorted(out, key=lambda x: x["date"])


# ---------------------------------------------------------------------------
# 标注自动避让
# ---------------------------------------------------------------------------
class Placer:
    """在轴内自动避让地放置带底框的文字标注。"""

    def __init__(self, fig, ax, top_ratio=1.0):
        self.fig, self.ax = fig, ax
        self.r = fig.canvas.get_renderer()
        self.ax_bb = ax.get_window_extent(self.r)
        y0, y1 = ax.get_ylim()
        self.top_limit = y1 - (y1 - y0) * (1.0 - top_ratio)
        self.used = []

    def place(self, x, y, text, prefer="up", fontsize=8.0, color="#333a42",
              fc="#ffffff", ec="#c9cfd8", pad=0.30, weight="bold"):
        offsets = [(0, 14), (0, -14), (34, 14), (-34, 14), (34, -14), (-34, -14),
                   (0, 28), (0, -28), (58, 22), (-58, 22), (58, -22), (-58, -22),
                   (0, 44), (0, -44), (84, 34), (-84, 34), (84, -34), (-84, -34)]
        order = offsets if prefer == "up" else [(dx, -dy) for dx, dy in offsets]
        fallback = None
        for dx, dy in order:
            ha = "center" if dx == 0 else ("left" if dx > 0 else "right")
            va = "bottom" if dy > 0 else "top"
            an = self.ax.annotate(text, (x, y), xytext=(dx, dy),
                                  textcoords="offset points", ha=ha, va=va,
                                  fontsize=fontsize, color=color, fontweight=weight,
                                  zorder=25,
                                  bbox=dict(boxstyle="round,pad=%.2f" % pad,
                                            fc=fc, ec=ec, lw=0.8))
            bb = an.get_window_extent(self.r)
            fallback = (an, bb)
            ok_box = (bb.x0 >= self.ax_bb.x0 + 2 and bb.x1 <= self.ax_bb.x1 - 2
                      and bb.y0 >= self.ax_bb.y0 + 2 and bb.y1 <= self.top_limit
                      and bb.y1 <= self.ax_bb.y1 - 2)
            if ok_box and not any(bb.expanded(1.05, 1.10).overlaps(u) for u in self.used):
                self.used.append(bb)
                return an
            an.remove()
        an, bb = fallback
        if an.axes is None:
            self.ax.add_artist(an)
        self.used.append(bb)
        return an


# ---------------------------------------------------------------------------
# 绘图工具
# ---------------------------------------------------------------------------
def draw_candles(ax, seg, idx, lw=0.55, width=0.68):
    o, h, l, cl = (seg[k].to_numpy(dtype=float) for k in ("open", "high", "low", "close"))
    colors = np.where(cl >= o, UP, DOWN)
    ax.add_collection(LineCollection(
        [[(i, lo), (i, hi)] for i, lo, hi in zip(idx, l, h)],
        colors=colors, linewidths=lw, zorder=2))
    rng = h.max() - l.min()
    bot = np.minimum(o, cl)
    hgt = np.maximum(np.abs(cl - o), rng * 0.0016)
    ax.bar(idx, hgt, bottom=bot, width=width, color=colors, edgecolor="none", zorder=3)


def month_ticks(w_index, n_target=12, month_step=None, label_fmt="%y-%m"):
    """按周索引给出「月初附近」的刻度位置与标签。

    month_step 给定时按 N 个月一格（6 = 半年一格，12 = 一年一格），否则按 n_target 等分。
    """
    months = pd.Series(w_index).dt.to_period("M")
    first = months.ne(months.shift()).to_numpy().nonzero()[0]
    if month_step:
        sel = [i for i in first if (int(months.iloc[i].month) - 1) % month_step == 0]
    else:
        step = max(1, len(first) // n_target)
        sel = first[::step]
    pos, lab = [], []
    for i in sel:
        pos.append(int(i))
        lab.append(pd.Timestamp(w_index[i]).strftime(label_fmt))
    return pos, lab


def week_pos(w_index, t):
    t = pd.Timestamp(t)
    return int(np.clip(np.searchsorted(w_index, t.to_datetime64(), side="right") - 1,
                       0, len(w_index) - 1))


def style_axis(ax, w_index, seg, n_target=12, tick_labelsize=8):
    lo, hi = seg["low"].min(), seg["high"].max()
    rng = max(hi - lo, 1e-6)
    ax.set_ylim(lo - rng * 0.14, hi + rng * 0.30)
    ax.set_xlim(-4, len(seg) + 4)
    ax.grid(axis="y", color="#e8eaee", lw=0.6, zorder=0)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.spines["left"].set_color("#c8ccd4")
    ax.spines["bottom"].set_color("#c8ccd4")
    ax.tick_params(labelsize=tick_labelsize, colors="#4a5058", length=3)
    pos, lab = month_ticks(w_index, n_target)
    pos = [p for p in pos if p < len(seg)]
    ax.set_xticks(pos)
    ax.set_xticklabels(lab[:len(pos)], fontsize=tick_labelsize)


# ---------------------------------------------------------------------------
# 主流程
# ---------------------------------------------------------------------------
def main():
    df = load_kline()
    w = to_week(df)
    wi = w["date"].to_numpy()
    disc = load_disclosures()

    fig = plt.figure(figsize=(21, 11.8), dpi=150)
    fig.patch.set_facecolor("#ffffff")
    # 只有两块面板：周K 主图 + 周成交量，紧贴（hspace 极小），上下共用同一时间轴
    ratios = [3.85, 0.40, 0.78]
    gs = fig.add_gridspec(3, 1, height_ratios=ratios,
                          left=0.048, right=0.985, top=0.940, bottom=0.118, hspace=0.058)

    # ================= 主图：周K 全景 =================
    ax_m = fig.add_subplot(gs[0])
    ax_d = fig.add_subplot(gs[1], sharex=ax_m)   # 披露带：主图之下，不占 K 线空间
    ax_v = fig.add_subplot(gs[2], sharex=ax_m)

    idx_all = np.arange(len(w))
    draw_candles(ax_m, w, idx_all, lw=0.5, width=0.82)

    lo, hi = w["low"].min(), w["high"].max()
    rng = hi - lo
    y0, y1 = lo - rng * 0.10, hi + rng * 0.20
    ax_m.set_ylim(y0, y1)
    ax_m.set_xlim(-6, len(w) + 6)
    ax_m.grid(axis="y", color="#e8eaee", lw=0.6, zorder=0)
    ax_m.set_axisbelow(True)
    for s in ("top", "right"):
        ax_m.spines[s].set_visible(False)
    ax_m.spines["left"].set_color("#c8ccd4")
    ax_m.spines["bottom"].set_color("#c8ccd4")
    ax_m.tick_params(labelsize=9, colors="#4a5058", length=3)
    ax_m.tick_params(axis="x", length=0)   # x 刻度标签显示在最底部，此处不再留刻度线
    ax_m.set_ylabel("前复权价（元）· 周K", fontsize=10, color="#4a5058")
    ax_m.tick_params(labelbottom=False)

    # 阶段区间框（编号 / 名称 / 时间范围）：虚线框 + 框顶带底标签
    for i, ph in enumerate(PHASES):
        p0, p1 = week_pos(wi, ph["s"]), week_pos(wi, ph["e"])
        ax_m.add_patch(Rectangle((p0 - 0.5, y0), (p1 - p0 + 1), (y1 - y0),
                                 fc=PHASE_BG[i % 2], ec="#2f6fd0", lw=1.2,
                                 ls=(0, (5, 3)), alpha=0.55, zorder=1.1))
        ax_m.annotate(ph["short"].replace("\n", "　"),
                      ((p0 + p1) / 2.0, y1 - (y1 - y0) * 0.050),
                      xytext=(0, 0), textcoords="offset points",
                      ha="center", va="center", fontsize=9.6, fontweight="bold",
                      color="#2b3138", zorder=6,
                      bbox=dict(boxstyle="round,pad=0.42", fc="#ffffff",
                                ec="#9aa2ae", lw=1.0, alpha=0.94))

    # 顶底（价格 + 日期）；dx 用于同价位相邻顶底的左右错开
    for m in HILO:
        p = week_pos(wi, m["date"])
        dx = m.get("dx", 0)
        ax_m.plot([p], [m["px"]], marker="o", ms=6, mfc="white", mec="#2b3138",
                  mew=1.2, zorder=12)
        ax_m.annotate(m["text"].split("（")[0], (p, m["px"]),
                      xytext=(dx, 12 if m["kind"] == "H" else -14),
                      textcoords="offset points",
                      ha="center" if dx == 0 else ("left" if dx > 0 else "right"),
                      va="bottom" if m["kind"] == "H" else "top",
                      fontsize=8.6, fontweight="bold", color="#2b3138", zorder=26,
                      bbox=dict(boxstyle="round,pad=0.30", fc="#ffffff",
                                ec="#c1c8d2", lw=0.8))

    # 里海买卖点（单行短标签 + 白底框；位置由 TRADES.off 逐个指定，避开 19-20 年密集区）
    for tr in TRADES:
        p = week_pos(wi, tr["date"])
        is_buy = tr["side"] == "B"
        col = BUY_C if is_buy else SELL_C
        ax_m.plot([p], [w["close"].iloc[p]],
                  marker="^" if is_buy else "v", ms=10,
                  mfc=col, mec="white", mew=1.2, zorder=14)
        dx, dy = tr.get("off", (0, 16 if is_buy else -18))
        ax_m.annotate(tr["short"], (p, w["close"].iloc[p]),
                      xytext=(dx, dy), textcoords="offset points",
                      ha="center" if dx == 0 else ("left" if dx > 0 else "right"),
                      va="bottom" if dy > 0 else "top",
                      fontsize=8.2, fontweight="bold", color=col, zorder=27,
                      bbox=dict(boxstyle="round,pad=0.26", fc="#ffffff",
                                ec=col, lw=0.8, alpha=0.94),
                      arrowprops=dict(arrowstyle="-", color=col, lw=0.8,
                                      alpha=0.55, shrinkA=2, shrinkB=4))

    # 2016 建仓区间带
    for b in BANDS:
        p0, p1 = week_pos(wi, b["start"]), week_pos(wi, b["end"])
        ax_m.add_patch(Rectangle((p0 - 0.5, y0), (p1 - p0 + 1), (y1 - y0) * 0.36,
                                 fc="#f4b9b4", ec="#d99b96", lw=0.8, alpha=0.30, zorder=1.05))
        ax_m.annotate("2016 年内全仓建仓（区间，案例只给年份）",
                      ((p0 + p1) / 2.0, y0 + (y1 - y0) * 0.36),
                      xytext=(0, -4), textcoords="offset points", ha="center", va="top",
                      fontsize=8.6, fontweight="bold", color="#8c2f28", zorder=28)

    # 业绩公告披露日：统一画成贴底短线（不挡 K 线），上方标报告期缩写
    # 标签一律竖排（rotation=90），横向只占一个字宽 —— 快报与一季报只差 2 个月，
    # 横排时任何分行组合都躲不开重叠；竖排天然不撞，且所有标签顶端对齐
    # 竖排标签横向只占约 10 px（≈2 周）：两根短线靠得太近时给「标签」加轴向微移，
    # 而不是合并文字 —— 合并会把「16预」「16快」拼成读不通的长标签
    items, used = [], []
    for d in disc:
        p = week_pos(wi, d["date"])
        p_lab = p
        for cand in (0.0, -2.0, 2.0, -4.0, 4.0):
            if all(abs(p + cand - u) >= 1.9 for u in used):
                p_lab = p + cand
                break
        used.append(p_lab)
        items.append(dict(p=p, p_lab=p_lab, label=d["label"],
                          quick=d["kind"] in ("快报", "预告")))
    # 披露带本体：无边框无刻度；短线自主图一侧向下垂，三行标签挂在短线下方
    ax_d.set_ylim(0, 1)
    ax_d.set_yticks([])
    ax_d.tick_params(length=0, labelbottom=False)
    for s in ("top", "right", "left", "bottom"):
        ax_d.spines[s].set_visible(False)
    for it in items:
        col = QUICK_C if it["quick"] else REPORT_C
        ax_d.vlines(it["p"], 1.04, 0.72, color=col,
                    lw=1.6 if it["quick"] else 1.2,
                    alpha=0.90 if it["quick"] else 0.50, clip_on=False)
        ax_d.annotate(it["label"], (it["p_lab"], 0.68),
                      rotation=90, ha="right", va="center",
                      fontsize=7.0, fontweight="bold", color=col,
                      alpha=1.0 if it["quick"] else 0.90)

    # 关键水平位（阻力 / 新低）
    LEVELS = [
        (21.38, "关键阻力位 21.38（2018.8 / 2019.4 双顶）", "#b3261e"),
        (10.61, "十一年新低 10.61（2026.6）", "#5a6473"),
    ]
    for px, txt, col in LEVELS:
        ax_m.axhline(px, color=col, lw=1.1, ls=(0, (6, 4)), alpha=0.55, zorder=1.5)
        ax_m.annotate(txt, (2, px), xytext=(0, 3), textcoords="offset points",
                      ha="left", va="bottom", fontsize=8.6, fontweight="bold",
                      color=col, zorder=22,
                      bbox=dict(boxstyle="round,pad=0.28", fc="#ffffff",
                                ec=col, lw=0.7, alpha=0.92))

    # 主图图例（右下空白区）
    ax_m.legend(
        handles=[
            Line2D([], [], color=QUICK_C, lw=1.5, ls="-", label="业绩快报 / 预告披露日"),
            Line2D([], [], color=REPORT_C, lw=1.1, ls="-", label="定期报告披露日（年报 / 中报 / Q1 / Q3）"),
            Line2D([], [], marker="^", color="none", mfc=BUY_C, mec="white", ms=10, label="里海买点"),
            Line2D([], [], marker="v", color="none", mfc=SELL_C, mec="white", ms=10, label="里海卖点"),
            Line2D([], [], marker="o", color="none", mfc="white", mec="#2b3138", ms=7,
                   label="关键顶 / 底（价格·日期）"),
            Line2D([], [], color="#b3261e", lw=1.1, ls=(0, (6, 4)), label="关键水平位（阻力 / 新低）"),
        ],
        loc="lower right", ncol=2, fontsize=9.2, frameon=True, facecolor="white",
        edgecolor="#d5dae2", framealpha=0.94, handlelength=1.5, columnspacing=1.2,
        handletextpad=0.5, borderaxespad=0.5).set_zorder(40)

    ax_m.set_title(
        "涪陵榨菜（002507）战略股复盘 · 周K（前复权）· 2015-2026　｜　关键顶底 × 里海买卖点 × 业绩披露时点 × 关键水平位\n"
        "一句话：戴维斯双击 5 年 10 倍（2016-2020）→ 净利零增长 6 年、股价腰斩再腰斩（2021-2026）。"
        "业绩没崩、估值崩 —— 预期定价的完整活教材",
        fontsize=15.0, fontweight="bold", color="#1a1d22", loc="left", pad=18)

    # ================= 周成交量（与主图共用同一时间轴，紧贴主图） =================
    vcol = np.where(w["close"].to_numpy() >= w["open"].to_numpy(), UP, DOWN)
    ax_v.bar(idx_all, w["volume"].to_numpy() / 1e8, width=0.82, color=vcol,
             edgecolor="none", zorder=3)
    ax_v.set_ylim(0, w["volume"].max() / 1e8 * 1.22)
    ax_v.grid(axis="y", color="#eef1f5", lw=0.6)
    ax_v.set_axisbelow(True)
    for s in ("top", "right"):
        ax_v.spines[s].set_visible(False)
    ax_v.tick_params(labelsize=9, colors="#4a5058", length=3)
    ax_v.set_ylabel("周成交量\n（亿股）", fontsize=9, color="#4a5058")
    vol_handles = [
        Line2D([], [], color=UP, lw=6, label="阳线量"),
        Line2D([], [], color=DOWN, lw=6, label="阴线量"),
    ]
    ax_v.legend(handles=vol_handles, loc="upper left", ncol=2, fontsize=9.2,
                frameon=True, facecolor="white", edgecolor="#d5dae2",
                framealpha=0.92, handlelength=1.5, columnspacing=1.6,
                handletextpad=0.5, borderaxespad=0.25)

    # 年份分割线 + x 轴年份刻度：取「每年第一个有数据的周」，两者共用同一组位置
    # （kline 表有三段真实缺口：2015-01~03、2016-04~06、2017-12~2018-03；
    #   若按「每年 1 月的周」取，2015 与 2018 会因那几周缺数据而整个漏标）
    yrs = pd.Series(wi).dt.year
    ypos = [int(i) for i in yrs.ne(yrs.shift()).to_numpy().nonzero()[0]]
    ypos = [p for p in ypos if p < len(w)]
    ylab = [str(pd.Timestamp(wi[p]).year) for p in ypos]
    for p in ypos:
        ax_m.axvline(p, color="#c3ccd9", lw=1.1, zorder=1.25)
        ax_d.axvline(p, color="#c3ccd9", lw=1.1, zorder=0.6)
        ax_v.axvline(p, color="#c3ccd9", lw=1.1, zorder=0.6)

    # 年中分割线：取每年 7 月首个数据周 —— 1 月→7 月与 7 月→次年 1 月各约 26 周，
    # 正好把年份对半分；取 6 月会偏前约 4 周，看着不居中
    jul = pd.Series(wi).dt.month.eq(7)
    for i in jul.ne(jul.shift()).to_numpy().nonzero()[0]:
        if not jul.iloc[i]:
            continue
        p = int(i)
        ax_m.axvline(p, color="#b9c3d1", lw=0.95, ls=(0, (4, 3)), zorder=1.24)
        ax_d.axvline(p, color="#b9c3d1", lw=0.95, ls=(0, (4, 3)), zorder=0.6)
        ax_v.axvline(p, color="#b9c3d1", lw=0.95, ls=(0, (4, 3)), zorder=0.6)

    # 时间轴：三块面板 sharex 共用同一套刻度，与上面的分割线严格对齐
    ax_m.set_xticks(ypos)
    ax_m.set_xticklabels(ylab, fontsize=10)
    ax_m.tick_params(axis="x", labelbottom=True, labelsize=10,
                     colors="#333a42", length=0, pad=4)
    ax_d.tick_params(axis="x", labelbottom=False)
    ax_v.tick_params(axis="x", labelbottom=True, labelsize=10,
                     colors="#333a42", length=4, pad=5)
    ax_v.set_xlabel("时间（主图 / 披露带 / 周成交量共用同一时间轴，每年一格）",
                    fontsize=10.2, color="#4a5058")

    # ================= 六个分阶段面板（周K + 时间轴） =================
    for k, ph in enumerate([]):
        s, e = pd.Timestamp(ph["s"]), pd.Timestamp(ph["e"])
        seg = w[(w["date"] >= s) & (w["date"] <= e)].reset_index(drop=True)
        if seg.empty:
            continue
        seg_last = seg["date"].iloc[-1]
        ax = fig.add_subplot(gs[k + 3])
        idx = np.arange(len(seg))
        seg_i = seg["date"].to_numpy()
        ax.set_facecolor(PHASE_BG[k % 2])
        draw_candles(ax, seg, idx, lw=0.6, width=0.70)
        for n, col in ((10, MA10_C), (30, MA30_C), (60, MA60_C)):
            ax.plot(idx, seg["ma%d" % n].to_numpy(), color=col, lw=0.9, alpha=0.9, zorder=4)
        style_axis(ax, seg_i, seg, n_target=12)
        ax.set_ylabel("周K", fontsize=9, color="#4a5058")
        ax.set_title("%s　｜　%s ~ %s　（%d 根周K）"
                     % (ph["full"], seg["date"].iloc[0].strftime("%Y-%m-%d"),
                        seg_last.strftime("%Y-%m-%d"), len(seg)),
                     fontsize=11.5, fontweight="bold", color="#1a1d22", loc="left", pad=7)

        def nearest_i(t):
            cand = seg.index[seg["date"] <= t]
            return int(cand[-1]) if len(cand) else None

        # --- 区间建仓带 ---
        for b in BANDS:
            i1 = nearest_i(pd.Timestamp(b["end"]))
            if nearest_i(pd.Timestamp(b["start"])) is None:
                continue
            i0 = nearest_i(pd.Timestamp(b["start"]))
            if pd.Timestamp(b["start"]) > seg_last:
                continue
            ax.axvspan(i0, i1, color="#f4b9b4", alpha=0.28, zorder=1.2)

        # --- 业绩公告竖线 ---
        ymin, ymax = ax.get_ylim()
        rng_i = ymax - ymin
        slot = 0
        for d in disc:
            i = nearest_i(d["date"])
            if i is None or d["date"] > seg_last:
                continue
            quick = d["kind"] in ("快报", "预告")
            col = QUICK_C if quick else REPORT_C
            ax.axvline(i, color=col, lw=0.9 if quick else 0.7,
                       ls="-" if quick else "--", alpha=0.55 if quick else 0.36, zorder=1.5)
            ax.annotate(d["label"], (i, ymax - rng_i * (0.020 + 0.040 * (slot % 3))),
                        ha="center", va="top", fontsize=7.2, color=col,
                        rotation=90, zorder=9)
            slot += 1

        pl = Placer(fig, ax, top_ratio=0.86)

        for nt in NOTES:
            t = pd.Timestamp(nt["date"])
            i = nearest_i(t)
            if i is None or t > seg_last:
                continue
            pl.place(i, seg.loc[i, "high"], nt["text"], nt["prefer"],
                     7.9, "#7a3300", "#fff4d6", "#e0b060", 0.30)

        for m in HILO:
            t = pd.Timestamp(m["date"])
            i = nearest_i(t)
            if i is None or t > seg_last:
                continue
            ax.plot([i], [m["px"]], marker="o", ms=5.0, mfc="white", mec="#2b3138",
                    mew=1.1, zorder=12)
            pl.place(i, m["px"], m["text"], m["prefer"], 7.9, "#2b3138",
                     "#ffffff", "#c1c8d2", 0.28)

        for b in BANDS:
            i = nearest_i(pd.Timestamp(b["start"]))
            if i is None or pd.Timestamp(b["start"]) > seg_last:
                continue
            pl.place(i, seg.loc[i, "low"], b["label"], "down", 8.0, "#8c2f28",
                     "#fdeceb", "#d99b96", 0.30)

        for a in ANCHORS:
            t = pd.Timestamp(a["date"])
            i = nearest_i(t)
            if i is None or t > seg_last:
                continue
            ax.plot([i], [seg.loc[i, "close"]], marker="D", ms=5, mfc="white",
                    mec=ANCHOR_C, mew=1.1, zorder=12)
            pl.place(i, seg.loc[i, "close"], a["text"], "up", 7.9, ANCHOR_C,
                     "#eef4fd", "#a8c2e6", 0.28)

        for tr in TRADES:
            t = pd.Timestamp(tr["date"])
            i = nearest_i(t)
            if i is None or t > seg_last:
                continue
            is_buy = tr["side"] == "B"
            y = seg.loc[i, "low"] if is_buy else seg.loc[i, "high"]
            ax.plot([i], [y], marker="^" if is_buy else "v", ms=12,
                    mfc=BUY_C if is_buy else SELL_C, mec="white", mew=1.3, zorder=14,
                    clip_on=False)
            pl.place(i, y, tr["text"], tr["prefer"], 8.4,
                     BUY_C if is_buy else SELL_C,
                     "#fdeceb" if is_buy else "#e8f6ef",
                     BUY_C if is_buy else SELL_C, 0.34)

    # ================= 脚注（图例已内置在两块面板内） =================
    fig.text(0.042, 0.004,
             "数据：data/002507.db（kline 前复权 qfq，全部按周（W-FRI）聚合成周K）· 巨潮资讯 cninfo 实际公告披露日 · "
             "里海买卖点与事件出处见 research-wiki/research/疯狂的里海/案例/里海案例-涪陵榨菜.md\n"
             "口径：图为前复权连续价（已还原除权除息，供跨期比较）；买卖点数值为原文「当时实际成交价（名义价）」，"
             "两者口径不同，故按日期定位、以文字标注名义价（如 2020-09-04 清仓 @49.2  /  前复权当日约 37 元；"
             "名义价最高 56.24  /  前复权最高 38.21，同为 2020-09-03）。\n"
             "时间标注：横轴 = 半年一格；主图 / 披露带 / 周成交量三块面板 sharex 共用同一时间轴、上下严格对齐；"
             "主图下方「披露带」中的短线 = 业绩公告披露日（共 58 条，均为巨潮 cninfo 实际披露日，自主图向下垂，不占 K 线空间）："
             "橙色 = 业绩快报 / 业绩预告（多在每年 2 月，次年业绩先声），灰色 = 年报 / 中报 / 一季报 / 三季报；"
             "短线标签 = 两位年份 + 报告期（21Q1 一季报 / 21H1 中报 / 21Q3 三季报 / 21A 年报 / 21快 业绩快报 / 21预 业绩预告），"
             "按披露月份自上而下分四行（快报·预告 / 年报 / 一季报·三季报 / 中报），避开 2-4 月的密集重叠；\n"
             "里海买卖点（图上标注为原文名义价）：S1 2019-04-26 减仓 ≈30 元 / B2 2019-11-18 买回 / B3 2020-01-07 建仓 @25.10 / "
             "S2 2020-04-23 减仓 @36 / S3 2020-09-04 清仓 @49.2；另 2022-11-07、2025-09-24 各买 100 股为观察仓。"
             "质量：两个主买点（2016 全仓 / 2019-11 买回）均落在业绩 + 估值双低区；卖点由「逻辑是否走完」触发、不由「涨了多少」触发，"
             "S3 清仓落在前复权高点 38.21 次日，此后 2020-2026 不再持有主仓位（原话「现在榨菜完全看不清」）。",
             fontsize=8.4, color="#5a6068", va="bottom", linespacing=1.65)

    os.makedirs(OUT_DIR, exist_ok=True)
    fig.savefig(OUT_PNG, facecolor="#ffffff")
    plt.close(fig)
    print("已输出 %s" % OUT_PNG)
    n_period = sum(d["kind"] not in ("快报", "预告") for d in disc)
    print("周K 根数 %d（%s ~ %s）| 主图公告竖线 %d 条（定期报告 %d / 快报·预告 %d）| 买卖点 %d | 顶底 %d | 事件 %d"
          % (len(w), w["date"].iloc[0].date(), w["date"].iloc[-1].date(),
             len(disc), n_period, len(disc) - n_period,
             len(TRADES), len(HILO), len(NOTES)))


if __name__ == "__main__":
    main()
