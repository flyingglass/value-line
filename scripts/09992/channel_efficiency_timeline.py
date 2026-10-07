# -*- coding: utf-8 -*-
"""channel_efficiency_timeline.py — 泡泡玛特「中国内地 / 海外」渠道单店·单台产出时间线

左右双面板：**左 = 中国内地，右 = 海外（含港澳台）**，两面板共享同一纵轴刻度便于对比，
各面板自带右轴画该区域的门店/机器人数（同一量纲，解释摊薄）。

每个面板内：**年报线与中报线分开连线**（不折算、不合并）
- 年报线 = 全年收入 ÷ 期末单位数；中报线 = 半年收入 ÷ 期末单位数。
- 二者口径不同，**不能纵向互相比较大小**；只能在各自序列内部看同比与趋势
  （中报对中报、年报对年报）。把中报 ×2 当"年化"是错的做法，这里不做。

其余口径：
1. **分子是渠道收入不是总营收**：零售店图只用零售店渠道收入，机器人图只用机器人渠道收入，
   线上、批发及其他全部剔除（交叉校验 26H1：中国零售店 60.90 + 海外 30.22 = 91.12 亿，
   与中报「全球零售店占总营收 53.1%」吻合）。
2. **海外 = 含港澳台，中国 = 中国内地**：门店/机器人数表是「港澳台及海外」合计，
   收入侧同步含港澳台；25H1 起中报把港澳台并入「中国业务」披露，本图按此回加，保持全期可比。
3. 公司**不披露同店销售（SSSG）**，且分母是期末时点数、分子是区间收入，
   故含新店/新机爬坡摊薄，是「上界方向」的读数而非纯需求读数。

数据来源（均在 research-wiki 沉淀 + 年报/中报原文核对）：
- 20H1-25A 渠道收入：`research-wiki/raw/research/泡泡玛特/2026-08-20-渠道跟踪表-用户提供.xlsx.md`
  Sheet「渠道-按区域」（海外含港澳台 = 亚太+美洲+欧洲+港澳台，与区域拆分表交叉核对一致）
- 24H1 中国内地零售店收入 17.24 亿：采用 2025 中报 Note 5 中国业务（内地）口径
  （用户表 Old 口径 14.71，见 `业绩/经营时间序列（2020-2026）.md` 〇）
- 25H1/26H1 机器人 + 26H1 零售店：`data/pdfs/泡泡玛特/09992_泡泡玛特_2026_中报.pdf`
  P9（Note 5 中国/海外业务）× P25（中国内地/港澳台地区 数量与收入）
- 25A 机器人：渠道跟踪表区域拆分（亚太+美洲+欧洲+港澳台）
- 门店/机器人数：`业绩/经营时间序列（2020-2026）.md` 三、门店网络（期末时点）

用法：
    python scripts/09992/channel_efficiency_timeline.py
    python scripts/09992/channel_efficiency_timeline.py --kind robot   # 只出机器人图
"""
import argparse
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.lines import Line2D

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:                                            # noqa: BLE001
    pass

CN_C = "#d1495b"        # 中国
OS_C = "#2f6fd0"        # 海外
GRID_C = "#e8eaee"
NOTE_C = "#6b7280"
NUM_C = "#b9bfc9"       # 数量轴（淡灰）
NUM_MK_C = "#7c848f"    # 数量轴数据点（加深，便于读端点）
LINE_LS = (0, (4, 2.4))  # 中报线：虚线

PERIODS = ["20H1", "20A", "21H1", "21A", "22H1", "22A", "23H1", "23A",
           "24H1", "24A", "25H1", "25A", "26H1"]
IS_ANNUAL = [False, True] * 6 + [False]

# ---- 零售店：收入（亿元）/ 店数（家）----
STORE_CN_REV = [3.13, 10.02, 6.75, 16.73, 8.92, 16.91, 11.79, 26.61,
                17.24, 38.28, 36.48, 85.02, 54.2744]
STORE_CN_N = [136, 187, 215, 288, 308, 329, 340, 363, 374, 401, 409, 410, 419]
# 20H1/20A 海外零售店收入未披露（当年海外仅 1 家店）→ None
STORE_OS_REV = [None, None, 0.03, 0.03, 0.35, 1.36, 1.65, 5.83,
                8.94, 29.38, 32.5906, 87.52, 36.8454]
STORE_OS_N = [1, 1, 2, 7, 11, 28, 38, 70, 83, 120, 162, 220, 257]

# ---- 机器人商店：收入（亿元）/ 台数 ----
# 26H1 内地 757,958 千元 / 2436 台（中报 P25），港澳台 20,995 / 46 计入海外侧
ROBOT_CN_REV = [1.05, 3.29, 2.27, 4.68, 2.04, 3.79, 2.71, 5.53,
                3.15, 6.98, 6.4344, 12.86, 7.57958]
ROBOT_CN_N = [1001, 1351, 1477, 1855, 1916, 2067, 2185, 2190,
              2189, 2300, 2396, 2350, 2436]
ROBOT_OS_REV = [None, None, 0.00, 0.02, 0.04, 0.15, 0.25, 0.57,
                0.53, 1.33, 1.77293, 4.04, 1.92567]
# 25H1/26H1 海外台数 = 中报披露的全球 − 中国内地（2597−2396=201；2827−2436=391）
ROBOT_OS_N = [0, 1, 7, 15, 20, 57, 106, 99, 143, 172, 201, 287, 391]

ASSET_DIR = os.path.join("research-wiki", "research", "消费", "泡泡玛特", "assets")

# ann: (期间, 面板 cn/os, 线型 annual/half, 文本, 框左下角位置)
CFG = {
    "store": dict(
        title_ch="零售店", unit="百万元 / 店 / 期", unit_cn="家", u="店",
        rev_cn=STORE_CN_REV, n_cn=STORE_CN_N,
        rev_os=STORE_OS_REV, n_os=STORE_OS_N,
        scale=100.0, ylim=(0, 45), y_num_max=700, none_label="未披露",
        out="store-efficiency-timeline.png",
        csv="09992_store_efficiency.csv",
        ann=[("25A", "os", "annual", "海外年报峰值 39.8（25A）\nLabubu 全球爆火 + 门店 220 家",
              (2.0, 33.0)),
             ("26H1", "os", "half", "26H1 海外 14.3：中报同比 -28.7%\n（25H1 20.1 → 26H1 14.3）",
              (8.6, 5.0)),
             ("26H1", "cn", "half", "中国 26H1 13.0：中报同比 +45.2%\n与海外中报差距由 2.3 倍收窄至 1.1 倍\n"
                                    "内地店数近 3 年几乎不动 401→419",
              (0.4, 24.0))],
    ),
    "robot": dict(
        title_ch="机器人商店", unit="万元 / 台 / 期", unit_cn="台", u="台",
        rev_cn=ROBOT_CN_REV, n_cn=ROBOT_CN_N,
        rev_os=ROBOT_OS_REV, n_os=ROBOT_OS_N,
        scale=10000.0, ylim=(0, 150), y_num_max=2600, none_label="无（0 台）",
        out="robot-efficiency-timeline.png",
        csv="09992_robot_efficiency.csv",
        ann=[             ("25A", "os", "annual", "海外年报峰值 140.8（25A）\n当年机器人数 172→287 台仍在扩张",
              (0.3, 100.0)),
             ("26H1", "os", "half", "26H1 海外 49.3：中报同比 -44.2%\n（25H1 88.2 → 26H1 49.3）",
              (7.2, 12.0)),
             ("26H1", "cn", "half", "中国 26H1 31.1：中报同比 +15.9%，中报序列新高\n"
                                    "台数近 3 年零增长 2190→2436，靠单台提效\n"
                                    "与海外中报差距 3.3 倍 → 1.6 倍",
              (0.5, 72.0))],
    ),
}


def setup_font():
    avail = {f.name for f in fm.fontManager.ttflist}
    for f in ("Microsoft YaHei", "SimHei", "Noto Sans CJK SC",
              "Source Han Sans SC", "Arial Unicode MS"):
        if f in avail:
            plt.rcParams["font.sans-serif"] = [f]
            return f
    return None


def series(rev, num, scale):
    """单次报告期收入 ÷ 期末单位数。不折算：年报=全年口径，中报=半年口径。"""
    out = []
    for r, n in zip(rev, num):
        out.append(None if (r is None or not n) else r / n * scale)
    return out


def panel(ax, cfg, side, vals, nums, is_first):
    """画一个面板（side = 'cn' | 'os'）。"""
    color = CN_C if side == "cn" else OS_C
    region = "中国内地" if side == "cn" else "海外（含港澳台）"
    x = list(range(len(PERIODS)))
    ann = [v if IS_ANNUAL[i] else None for i, v in enumerate(vals)]
    hlf = [None if IS_ANNUAL[i] else v for i, v in enumerate(vals)]
    span = cfg["ylim"][1]

    # 数量轴（该面板自己twiny轴的右侧）
    axr = ax.twinx()
    axr.plot(x, nums, color=NUM_C, lw=1.4, ls=(0, (5, 3)), marker="o", ms=5.4,
             mfc=NUM_MK_C, mec="white", mew=1.0, zorder=3)
    what = "零售店数" if cfg["unit_cn"] == "家" else "机器人数"
    axr.set_ylabel("%s· %s（右轴）" % (region, what), fontsize=9.6,
                   color="#8b939e")
    axr.tick_params(axis="y", labelsize=9.0, colors="#8b939e", length=3)
    axr.set_ylim(0, cfg["y_num_max"])
    axr.grid(False)

    # 年报线 / 中报线
    for vs, ls, lw, mk in ((ann, "-", 2.1, "o"), (hlf, LINE_LS, 1.7, "D")):
        xs = [x[i] for i, v in enumerate(vs) if v is not None]
        ys = [v for v in vs if v is not None]
        ax.plot(xs, ys, color=color, lw=lw, ls=ls, marker=mk,
                ms=7.0 if mk == "o" else 6.0,
                mec="white" if mk == "o" else color,
                mfc=color if mk == "o" else "white",
                mew=1.0 if mk == "o" else 1.5, zorder=6)

    # 数值标签：年报朝上、中报朝下
    for i, v in enumerate(vals):
        if v is None:
            ax.annotate(cfg["none_label"], (x[i], span * 0.012), ha="center",
                        va="bottom", fontsize=7.6, color="#aeb6c0", zorder=7)
            continue
        up = IS_ANNUAL[i]
        if v < span * 0.08 and not up:
            ax.annotate("%.1f" % v, (x[i], v), xytext=(8, 3),
                        textcoords="offset points", ha="left", va="bottom",
                        fontsize=8.4, fontweight="bold", color=color, zorder=7)
        else:
            ax.annotate("%.1f" % v, (x[i], v),
                        xytext=(0, 7 if up else -11), textcoords="offset points",
                        ha="center", va="bottom" if up else "top",
                        fontsize=8.4, fontweight="bold", color=color, zorder=7)

    # 25H1 口径切换竖线
    i_cal = PERIODS.index("25H1")
    ax.axvline(x[i_cal] - 0.5, color="#d7dbe2", lw=1.0, ls=(0, (4, 3)), zorder=1)
    if is_first:
        ax.annotate("← 此前｜此后 →　25H1 起港澳台并入「中国」披露（已回加）",
                    (x[i_cal] - 0.5, span * 0.954), xytext=(4, 0),
                    textcoords="offset points", ha="left", va="center",
                    fontsize=7.6, color="#9aa2ad", zorder=8)

    # 面板内标注
    box = dict(boxstyle="round,pad=0.32", fc="#ffffff", ec=color, lw=0.8,
               alpha=0.96)
    arrow = dict(arrowstyle="-", color=color, lw=0.8, shrinkA=2, shrinkB=4,
                 alpha=0.7)
    for lb, sd, lt, text, xytext in cfg["ann"]:
        if sd != side:
            continue
        i = PERIODS.index(lb)
        val = vals[i]
        ax.annotate(text, xy=(x[i], val), xytext=xytext, ha="left", va="center",
                    fontsize=8.6, color=color, bbox=box, arrowprops=arrow,
                    zorder=8)

    ax.set_title("%s　%s产出" % (region, cfg["u"]), fontsize=11.6,
                 fontweight="bold", color=color, pad=9)
    ax.set_xticks(x)
    ax.set_xticklabels(PERIODS, fontsize=9.8, fontweight="bold")
    ax.tick_params(axis="x", length=0, pad=6)
    for i in range(len(PERIODS)):
        ax.get_xticklabels()[i].set_color("#8a5a2a" if IS_ANNUAL[i] else "#3a4048")
    ax.set_xlim(-0.5, len(PERIODS) - 0.5)
    ax.set_ylim(*cfg["ylim"])
    if is_first:
        ax.set_ylabel("单次报告期产出（%s）" % cfg["unit"], fontsize=10.6,
                      color="#4a5058")
    ax.tick_params(axis="y", labelsize=9.4, colors="#4a5058", length=3)
    ax.grid(axis="y", color=GRID_C, lw=0.6, zorder=0)
    ax.spines["top"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["bottom"].set_color("#c8ccd4")
    for s in ("top", "left", "right", "bottom"):
        axr.spines[s].set_visible(False)
    return axr


def draw(kind, cfg, csv_dir, outdir):
    cn = series(cfg["rev_cn"], cfg["n_cn"], cfg["scale"])
    os_ = series(cfg["rev_os"], cfg["n_os"], cfg["scale"])

    if csv_dir:
        os.makedirs(csv_dir, exist_ok=True)
        with open(os.path.join(csv_dir, cfg["csv"]), "w", encoding="utf-8") as fh:
            fh.write("期间,报告口径,中国内地%s,海外含港澳台%s,中国内地%s数,海外%s数\n"
                     % (cfg["unit"].replace(" ", ""), cfg["unit"].replace(" ", ""),
                        cfg["unit_cn"], cfg["unit_cn"]))
            for i, lb in enumerate(PERIODS):
                fh.write("%s,%s,%s,%s,%d,%d\n"
                         % (lb, "年报（全年）" if IS_ANNUAL[i] else "中报（半年）",
                            ("%.2f" % cn[i]) if cn[i] is not None else "",
                            ("%.2f" % os_[i]) if os_[i] is not None else "",
                            cfg["n_cn"][i], cfg["n_os"][i]))

    fig, (axl, axr) = plt.subplots(1, 2, figsize=(17.0, 8.6), dpi=150,
                                   sharey=True)
    fig.patch.set_facecolor("#ffffff")
    fig.subplots_adjust(left=0.052, right=0.952, top=0.845, bottom=0.255,
                        wspace=0.13)

    for ax, side, vals, nums, first in ((axl, "cn", cn, cfg["n_cn"], True),
                                        (axr, "os", os_, cfg["n_os"], False)):
        panel(ax, cfg, side, vals, nums, first)

    handles = [
        Line2D([], [], color="#8a5a2a", lw=2.1, marker="o", ms=7.0, mec="white",
               label="年报（全年收入 ÷ 期末%s数）" % cfg["unit_cn"]),
        Line2D([], [], color="#3a4048", lw=1.7, ls=LINE_LS, marker="D", ms=6.0,
               mfc="white", mec="#3a4048", mew=1.5,
               label="中报（半年收入 ÷ 期末%s数）" % cfg["unit_cn"]),
        Line2D([], [], color=NUM_C, lw=1.4, ls=(0, (5, 3)), marker="o", ms=5.4,
               mfc=NUM_MK_C, mec="white", mew=1.0,
               label="期末%s数（右轴，同一量纲）" % cfg["unit_cn"]),
    ]
    fig.legend(handles=handles, loc="lower left", fontsize=9.2, frameon=True,
               framealpha=0.94, ncol=3, columnspacing=2.2,
               bbox_to_anchor=(0.052, 0.878), borderaxespad=0.0)

    fig.text(0.052, 0.945,
             "泡泡玛特（09992.HK）%s单%s产出年报 vs 中报　2020H1 - 2026H1"
             "　（26H1 渠道收入：中国内地 %.2f 亿 / 海外 %.2f 亿）"
             % (cfg["title_ch"], cfg["u"], cfg["rev_cn"][-1], cfg["rev_os"][-1]),
             fontsize=14.0, fontweight="bold", color="#1a1d22",
             ha="left", va="center")

    fig.text(0.052, 0.215,
             "口径：① 年报与中报分别连线、不折算——年报点 = 全年收入 ÷ 期末%s数，中报点 = 半年收入 ÷ 期末%s数，二者口径不同，纵向不可直接比大小；"
             "只能在各自序列内部比同比（中报对中报、年报对年报）。年报普遍为中报的 1.8-2.3 倍，且倍率逐年变化，这正是不能混算的原因。\n"
             "② 分子是该渠道的收入（不是总营收）——零售店图剔除线上/机器人/批发，机器人图剔除零售店/线上/批发；"
             "交叉校验：26H1 中国零售店 60.90 + 海外 30.22 = 91.12 亿，与中报「零售店占全集团收入 53.1%%」吻合。"
             "③ 公司不披露同店销售（SSSG），分母为期末时点数、分子为区间收入，含新店/新机爬坡与装修期摊薄，是上界方向读数而非纯需求读数。\n"
             "④ 左面板 = 中国内地，右面板 = 港澳台及海外，两者相加 = 全球；25H1 起中报把港澳台并入「中国业务」披露，本图按此回加以保持全期可比。"
             "⑤ x 轴刻度颜色：橙色 = 年报、深色 = 中报。⑥ 24H1 中国内地零售店收入采用 2025 中报 Note 5 口径 17.24 亿（用户表 Old 口径 14.71 亿）；21H1 海外机器人收入披露为 0（当年仅 7 台）。\n"
             "数据源：raw/research/泡泡玛特/2026-08-20-渠道跟踪表-用户提供.xlsx.md（Sheet 渠道-按区域，20H1-25A）"
             "｜09992_泡泡玛特_2026_中报.pdf P9 Note 5 + P25 中国内地/港澳台地区分项"
             "\n⑦ 分母口径与来源（已回原文逐期核对）：中国内地数取各期年报/中报渠道章节原文（如 24A「截至2024年12月31日合計零售店401家／合計機器人商店2,300間」）；"
             "海外数 24A 及以前取同章节披露的「港澳台及海外」（不含合营/加盟，与渠道收入配套，如 24A 120 家／172 台）——年报业务概览章节另有含合营及加盟口径（24A 130 家／192 台），不采用，因合营/加盟收入不计入渠道收入。"
             "25H1/26H1 中报渠道章节不再披露海外分项，改用「全球 − 中国内地」倒推（全球取中报概览 571/2,597、676/2,827），这两期与前期可能存在含合营口径的小幅差异。\n"
             "数据源：raw/research/泡泡玛特/2026-08-20-渠道跟踪表-用户提供.xlsx.md（Sheet 渠道-按区域，20H1-25A）"
             "｜09992_泡泡玛特_2026_中报.pdf P9 Note 5 + P25 中国内地/港澳台地区分项"
             "｜各期年报/中报门店网络披露原文｜业绩/经营时间序列（2020-2026）.md（门店网络 3.1/3.2，期末时点）。"
             % (cfg["unit_cn"], cfg["unit_cn"]),
             fontsize=8.4, color=NOTE_C, ha="left", va="top", linespacing=1.72)

    out_path = os.path.join(outdir, cfg["out"])
    os.makedirs(os.path.dirname(os.path.abspath(out_path)) or ".", exist_ok=True)
    fig.savefig(out_path, facecolor="#ffffff")
    plt.close(fig)
    print("PNG ->", out_path)
    return out_path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--kind", default="all", choices=["store", "robot", "all"])
    ap.add_argument("--outdir", default=ASSET_DIR)
    ap.add_argument("--csv-dir", default="scripts/out")
    a = ap.parse_args()

    setup_font()
    kinds = ["store", "robot"] if a.kind == "all" else [a.kind]
    for k in kinds:
        draw(k, CFG[k], a.csv_dir, a.outdir)


if __name__ == "__main__":
    main()
