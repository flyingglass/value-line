# -*- coding: utf-8 -*-
"""revenue_price_timeline.py — A股「营收 × 披露时点 × 股价」一图对照（单面板叠加）

数据源：
- 营业收入 / 定期报告披露日：东方财富「利润表-按报告期」
  (ak.stock_profit_sheet_by_report_em)，NOTICE_DATE 即该期报告公开披露日
- 行情：新浪日线前复权 (ak.stock_zh_a_daily, adjust="qfq")

版式要点（勿随意改动，详见 skill 的 references/implementation-notes.md）：
- 单面板叠加：左轴股价（元）、右轴营收（亿元），共用同一时间轴
- 用 secondary_yaxis 做右轴刻度换算（不新建 axes），保证 zorder 分层有效
- 全部图元在同一 axes 内按 zorder 排序：柱 → 股价线 → 标注

用法示例：
    python revenue_price_timeline.py --code 002810 --name 山东赫达 \
        --extremes 2018:low,2021:high,2024:low,2026:high \
        --out research-wiki/research/白马/山东赫达/assets/revenue-price-timeline.png
"""
import argparse
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

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:                                            # noqa: BLE001
    pass

PRICE_C = "#2f6fd0"
GRID_C = "#e8eaee"
YEAR_C = "#c3ccd9"
NOTE_C = "#6b7280"

# key, 报告期名称关键字, 涵盖月份, 报告期末(MM-DD), 柱色, 描边/标签色,
# 柱宽(天), 标签字号, zorder, 透明度, 标签上移(pt)
KINDS = [
    ("Q1", "一季报", 3, "03-31", "#8fbde2", "#2f6a99", 22.0, 7.4, 4.2, 0.92, 18.0),
    ("H1", "中报", 6, "06-30", "#63bda6", "#227a63", 30.0, 8.0, 3.9, 0.82, 8.0),
    ("Q3", "三季报", 9, "09-30", "#f0ad4e", "#a9610d", 38.0, 7.4, 3.6, 0.75, 30.0),
    ("FY", "年报", 12, "12-31", "#9b86c4", "#4f3d78", 46.0, 8.6, 3.0, 0.48, 8.0),
]
STYLE = {k[0]: dict(name=k[1], months=k[2], prev=k[3], color=k[4], deep=k[5],
                    width=k[6], fs=k[7], z=k[8], alpha=k[9], up=k[10])
         for k in KINDS}
DRAW_ORDER = ["FY", "Q3", "H1", "Q1"]       # 先画粗口径，后画细口径

Z_LINE = 6.0          # 股价线：压在全部柱之上
Z_LABEL = 8.0         # 柱顶标签 / 柱底披露日期
Z_NOTE = 9.0          # 披露当日股价点
Z_EXTREME_MK = 10.0   # 高低点标记
Z_EXTREME_TX = 12.0   # 高低点文字


def setup_font():
    avail = {f.name for f in fm.fontManager.ttflist}
    for f in ("Microsoft YaHei", "SimHei", "Noto Sans CJK SC",
              "Source Han Sans SC", "Arial Unicode MS"):
        if f in avail:
            plt.rcParams["font.sans-serif"] = [f]
            return f
    return None


def market_of(code):
    """返回 (新浪行情前缀, 东财 symbol 前缀)。"""
    if code.startswith(("6", "9")):
        return "sh", "SH"
    if code.startswith(("4", "8")):
        return "bj", "BJ"
    return "sz", "SZ"


def _retry(fn, n=4, wait=2.0):
    last = None
    for i in range(n):
        try:
            return fn()
        except Exception as e:                                # noqa: BLE001
            last = e
            time.sleep(wait)
    raise last


def stock_name(code):
    """取股票简称：先试东财个股信息（快），失败退回全市场代码表（慢但稳）。"""
    try:
        info = _retry(lambda: ak.stock_individual_info_em(symbol=code),
                      n=2, wait=1.0)
        row = info[info["item"].astype(str).str.contains("简称")]
        if len(row):
            return str(row["value"].iloc[0]).strip()
    except Exception:                                         # noqa: BLE001
        pass
    try:
        tbl = _retry(lambda: ak.stock_info_a_code_name(), n=2, wait=1.0)
        hit = tbl[tbl["code"].astype(str) == code]
        if len(hit):
            return str(hit["name"].iloc[0]).strip()
    except Exception:                                         # noqa: BLE001
        pass
    return code


def fetch_reports(code):
    _, prefix = market_of(code)
    df = _retry(lambda: ak.stock_profit_sheet_by_report_em(symbol=prefix + code))
    cols = ["REPORT_DATE", "REPORT_DATE_NAME", "NOTICE_DATE",
            "TOTAL_OPERATE_INCOME"]
    df = df[cols].copy()
    df["REPORT_DATE"] = pd.to_datetime(df["REPORT_DATE"])
    df["NOTICE_DATE"] = pd.to_datetime(df["NOTICE_DATE"])
    df["rev"] = pd.to_numeric(df["TOTAL_OPERATE_INCOME"], errors="coerce") / 1e8
    # 多保留若干历史年度，仅作同比基准；上市前的报告期在 build_frames 中剔除
    return df.sort_values("REPORT_DATE").reset_index(drop=True)


def fetch_price(code, start=None, end=None):
    sina, _ = market_of(code)
    d = _retry(lambda: ak.stock_zh_a_daily(symbol=sina + code, adjust="qfq"))
    d["date"] = pd.to_datetime(d["date"])
    if start is not None:
        d = d[d["date"] >= start]
    if end is not None:
        d = d[d["date"] <= end]
    return d.reset_index(drop=True)


def build_frames(rep, start):
    """返回定期报告列表（一季报 / 中报 / 三季报 / 年报），按披露日排序。"""
    rev_of = dict(zip(rep["REPORT_DATE"].dt.strftime("%Y-%m-%d"), rep["rev"]))
    items = []
    for _, r in rep.iterrows():
        if r["NOTICE_DATE"] < start or r["REPORT_DATE"] < start:
            continue                      # 上市前披露或报告期在上市前，不入图
        if not np.isfinite(r["rev"]):
            continue
        for key, kw, months, prev_md, *_ in KINDS:
            if kw not in str(r["REPORT_DATE_NAME"]):
                continue
            y = r["REPORT_DATE"].year
            if r["REPORT_DATE"].strftime("%m-%d") != prev_md:
                continue
            prev = rev_of.get("%d-%s" % (y - 1, prev_md))
            yoy = None if prev is None or not np.isfinite(prev) or prev == 0 \
                else (r["rev"] / prev - 1.0) * 100.0
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


def pick_extremes(px, n=4):
    """自动挑选 n 个关键高低点：每年取年内极值按偏离度排序，同年只取一个。"""
    closes = px["close"].to_numpy(dtype=float)
    med = float(np.nanmedian(closes))
    rng = float(np.nanmax(closes) - np.nanmin(closes)) or 1.0
    cand = []
    for y, seg in px.groupby(px["date"].dt.year):
        if len(seg) < 60:                       # 不足一年的片段（上市/截尾年）跳过
            continue
        for kind, i in (("high", seg["close"].idxmax()),
                        ("low", seg["close"].idxmin())):
            val = float(seg.loc[i, "close"])
            cand.append(dict(year=int(y), kind=kind, val=val,
                             date=seg.loc[i, "date"],
                             score=abs(val - med) / rng))
    cand.sort(key=lambda c: -c["score"])
    out, used = [], set()
    for c in cand:
        if c["year"] in used:
            continue
        used.add(c["year"])
        out.append(c)
        if len(out) >= n:
            break
    return sorted(out, key=lambda c: c["date"])


def nice_ticks(top, target=7):
    """按量程自动挑一个「整数、约 target 段」的刻度步长，避免出现 17.5 这类读数。"""
    top = float(top)
    if top <= 0:
        return np.array([0.0])
    raw = top / float(target)
    mag = 10.0 ** np.floor(np.log10(raw))
    step = 10.0 * mag
    for m in (1.0, 2.0, 2.5, 5.0, 10.0):
        if raw <= m * mag:
            step = m * mag
            break
    return np.arange(0.0, top + step * 1e-9, step)


def parse_extremes(s, px):
    """解析 '2018:low,2021:high' 形式的显式指定。"""
    out = []
    for part in [p for p in s.split(",") if p.strip()]:
        m = re.match(r"\s*(\d{4})\s*(?::\s*(high|low|高|低))?\s*$", part)
        if not m:
            raise ValueError("--extremes 格式应为 2018:low,2021:high，收到：%s"
                             % part)
        y = int(m.group(1))
        kind = (m.group(2) or "high")
        kind = {"高": "high", "低": "low"}.get(kind, kind)
        seg = px[px["date"].dt.year == y]
        if seg.empty:
            continue
        i = seg["close"].idxmax() if kind == "high" else seg["close"].idxmin()
        out.append(dict(year=y, kind=kind, val=float(seg.loc[i, "close"]),
                        date=seg.loc[i, "date"], score=0.0))
    return out


def draw(items, px, name, code, extremes, out_path,
         price_mult=1.14, rev_mult=1.14):
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
    scale = price_top / rev_top              # 亿元 → 左轴价格坐标

    fig = plt.figure(figsize=(29.0, 12.4), dpi=150)
    fig.patch.set_facecolor("#ffffff")
    gs = fig.add_gridspec(1, 1, left=0.040, right=0.962, top=0.856, bottom=0.152)
    ax = fig.add_subplot(gs[0])
    ax.set_facecolor("#fafbfc")
    ax.set_ylim(0, price_top)
    ax.set_xlim(x0, x1)
    axr = ax.secondary_yaxis(
        "right", functions=(lambda v: v / scale, lambda v: v * scale))

    # ---- 年份分隔 + 披露时点竖虚线 ----
    for y in range(start.year + 1, end.year + 1):
        ax.axvline(mdates.date2num(pd.Timestamp("%d-01-01" % y)),
                   color=YEAR_C, lw=1.0, zorder=1.0)
    for ts in sorted({it["notice"] for it in items}):
        ax.axvline(mdates.date2num(ts), color="#e6e9ef", lw=0.85,
                   ls=(0, (3, 3)), zorder=1.2)

    # ================= 营收柱（最底层，按披露日定位）=================
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

    # ================= 标注：最上层 =================
    for key in DRAW_ORDER:
        for it in [i for i in items if i["kind"] == key]:
            xv = mdates.date2num(it["notice"])
            ax.plot([xv], [price_at(px, it["notice"])], marker="o",
                    ms=5.4 if key == "FY" else 4.6, mfc="#ffffff",
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

    # ---- 坐标轴外观 ----
    ax.set_ylabel("收盘价（元 · 前复权）", fontsize=10.5, color="#4a5058")
    ax.tick_params(axis="y", labelsize=9.5, colors="#4a5058", length=3)
    ax.grid(axis="y", color=GRID_C, lw=0.6, zorder=0)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    for s in ("left", "bottom", "right"):
        ax.spines[s].set_color("#c8ccd4")

    axr.set_ylabel("营业总收入（亿元 · 按报告期累计口径）", fontsize=10.5,
                   color="#5c626b")
    axr.tick_params(axis="y", labelsize=9.5, colors="#5c626b", length=3)
    # 两侧都用整数刻度（步长随量程自适应），避免出现 17.5 / 12.5 这类读数
    ax.set_yticks(nice_ticks(price_top))
    axr.set_yticks(nice_ticks(rev_top))

    # ---- X 轴：年份刻度 ----
    years = list(range(start.year, end.year + 1))
    ax.set_xticks([mdates.date2num(pd.Timestamp("%d-07-01" % y)) for y in years])
    ax.set_xticklabels([str(y) for y in years], fontsize=10.5,
                       color="#3a4048", fontweight="bold")
    ax.tick_params(axis="x", length=0, pad=6)

    # ---- 图例 ----
    handles = [plt.Line2D([], [], color=PRICE_C, lw=1.6, label="收盘价（前复权）")]
    for key in ("FY", "Q3", "H1", "Q1"):
        st = STYLE[key]
        handles.append(Rectangle(
            (0, 0), 1, 1, fc=st["color"], alpha=min(st["alpha"] + 0.15, 1.0),
            ec=st["deep"], lw=0.85, hatch=("" if key == "FY" else "///"),
            label="%s营收（%s，累计%d个月）"
                  % (st["name"], key, st["months"])))
    handles.append(plt.Line2D([], [], marker="o", mfc="#ffffff", mec=NOTE_C,
                              mew=1.3, ls="none", ms=5.5,
                              label="定期报告披露当日股价"))
    handles.append(plt.Line2D([], [], color="#e6e9ef", lw=1.2, ls=(0, (3, 3)),
                              label="定期报告披露时点"))
    ax.legend(handles=handles, loc="upper left", fontsize=9.0, frameon=True,
              framealpha=0.94, ncol=7, columnspacing=1.4,
              bbox_to_anchor=(0.0, 1.076), borderaxespad=0.0)

    ax.set_title("%s（%s）股价 · 营收 · 披露时点对照图　%d-%d（含季报）"
                 % (name, code, start.year, end.year),
                 fontsize=15.0, fontweight="bold", color="#1a1d22",
                 loc="left", pad=46)
    fig.text(0.040, 0.115,
             "数据：营业收入与定期报告披露日取自东方财富「利润表-按报告期」（NOTICE_DATE 为该期报告公开披露日）；"
             "股价为新浪日线前复权收盘价（数据截至 %s）。\n"
             "读法：股价线（左轴）与营收柱（右轴）共用同一时间轴并叠加于同一绘图区；"
             "每根营收柱的横向位置 = 该期报告的披露日期（非报告期末），"
             "竖虚线标示披露时点，与虚线对应的灰色空心点即披露当日收盘价。\n"
             "图层顺序：营收柱 → 股价线 → 各类标注（柱顶标签、披露日股价点、高低点），"
             "标注与股价线始终压在柱之上。\n"
             "四类报告期用四种颜色区分（一季报蓝 / 中报青绿 / 三季报橙 / 年报紫），柱宽随涵盖月份递增（3→12个月）。\n"
             "口径：柱高为按报告期累计的营业总收入（Q1=3个月、H1=6个月、Q3=9个月、FY=12个月），"
             "不同期长度之间不可直接比高低；柱顶百分比为同口径上年同期同比，单位为亿元；"
             "行情起点为 %s，此前披露的报告期未入图。"
             % (end.strftime("%Y-%m-%d"), start.strftime("%Y-%m-%d")),
             fontsize=8.8, color="#7a828d", ha="left", va="top",
             linespacing=1.75)

    os.makedirs(os.path.dirname(os.path.abspath(out_path)) or ".", exist_ok=True)
    fig.savefig(out_path, facecolor="#ffffff")
    plt.close(fig)
    return out_path


def dump_csv(items, px, csv_path):
    os.makedirs(os.path.dirname(os.path.abspath(csv_path)) or ".", exist_ok=True)
    rows = [dict(kind=it["kind"], label=it["label"], rev_yi=it["rev"],
                 yoy_pct=it["yoy"],
                 period_end=it["period_end"].strftime("%Y-%m-%d"),
                 notice_date=it["notice"].strftime("%Y-%m-%d"),
                 px_on_notice=round(price_at(px, it["notice"]), 2))
            for it in items]
    df = pd.DataFrame(rows).sort_values(["notice_date", "kind"])
    df.to_csv(csv_path, index=False, encoding="utf-8-sig")
    return csv_path, df


def main():
    ap = argparse.ArgumentParser(
        description="A股「营收 × 披露时点 × 股价」一图对照（单面板叠加）")
    ap.add_argument("--code", required=True, help="6位股票代码，如 002810")
    ap.add_argument("--name", default=None, help="股票简称，缺省自动查询")
    ap.add_argument("--start", default=None, help="起始日 YYYY-MM-DD，缺省取行情首日")
    ap.add_argument("--end", default=None, help="截止日 YYYY-MM-DD，缺省取今天")
    ap.add_argument("--out", default=None,
                    help="输出 PNG 路径，缺省 ./out/<code>-revenue-price-timeline.png")
    ap.add_argument("--csv", default=None, help="明细 CSV 路径，缺省与 PNG 同目录")
    ap.add_argument("--no-csv", action="store_true", help="不导出 CSV")
    ap.add_argument("--extremes", default=None,
                    help="关键高低点年份，如 2018:low,2021:high,2024:low,2026:high；"
                         "缺省自动挑选 4 个")
    ap.add_argument("--price-mult", type=float, default=1.14,
                    help="左轴（股价）顶部余量系数，默认 1.14")
    ap.add_argument("--rev-mult", type=float, default=1.14,
                    help="右轴（营收）顶部余量系数，默认 1.14")
    args = ap.parse_args()

    setup_font()

    code = args.code.strip()
    start = pd.Timestamp(args.start) if args.start else None
    end = pd.Timestamp(args.end) if args.end else None

    px = fetch_price(code, start, end)
    if px.empty:
        raise SystemExit("未取到行情：%s" % code)
    name = args.name or stock_name(code)

    rep = fetch_reports(code)
    items = build_frames(rep, px["date"].min())
    if not items:
        raise SystemExit("未取到定期报告营收数据：%s" % code)

    extremes = (parse_extremes(args.extremes, px) if args.extremes
                else pick_extremes(px, 4))

    out = args.out or os.path.join("out", "%s-revenue-price-timeline.png" % code)
    draw(items, px, name, code, extremes, out,
         price_mult=args.price_mult, rev_mult=args.rev_mult)
    print("PNG ->", os.path.abspath(out))

    if not args.no_csv:
        csv_path = args.csv or os.path.join(
            os.path.dirname(out) or ".", "%s_revenue_vs_price.csv" % code)
        p, df = dump_csv(items, px, csv_path)
        print(df.to_string(index=False))
        print("CSV ->", os.path.abspath(p))


if __name__ == "__main__":
    main()
