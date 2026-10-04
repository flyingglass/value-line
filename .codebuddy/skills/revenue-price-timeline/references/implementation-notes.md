# 实现笔记：营收 × 披露时点 × 股价 对照图

本文件给需要改造脚本的场景提供细节；日常出图只看 SKILL.md 即可。

## 1. 接口与字段

| 用途 | 接口 | 关键字段 |
|---|---|---|
| 营收与披露日 | `ak.stock_profit_sheet_by_report_em(symbol="SZ002810")` | `REPORT_DATE`（报告期末）、`REPORT_DATE_NAME`（如 `2025-12-31 年报`）、`NOTICE_DATE`（公开披露日）、`TOTAL_OPERATE_INCOME`（营业总收入，元） |
| 日线行情 | `ak.stock_zh_a_daily(symbol="sz002810", adjust="qfq")` | `date / open / high / low / close / volume`，`qfq` 为前复权 |
| 简称（快） | `ak.stock_individual_info_em(symbol="600519")` | `item="股票简称"` 行的 `value`，走东财 push2，偶发 `RemoteDisconnected` |
| 简称（稳） | `ak.stock_info_a_code_name()` | `code / name`，全市场表，约 6 秒，tqdm 进度条走 stderr |

`TOTAL_OPERATE_INCOME` 是营业总收入；若需营业收入口径，改用 `OPERATE_INCOME`。

## 2. 报告期的识别

`REPORT_DATE_NAME` 里含「一季报 / 中报 / 三季报 / 年报」关键字，同时要求报告期末的 `MM-DD` 等于 `03-31 / 06-30 / 09-30 / 12-31`，两个条件都满足才归入对应 `kind`。这样能挡掉「中报摘要」「业绩快报」这类同名字段错位。

同比基准用 `dict(报告期末 → 营收)` 查「上年同期末」，缺失或 0 时为 `None`，图上不显示百分比。

## 3. 双轴叠加的正确做法（踩坑记录）

最初用 `axp = subplot(...)` + `axr = axp.twinx()`，给柱 `zorder=3~4.2`、给股价线 `zorder=6`，但**股价线仍然被柱子盖住**。原因：`zorder` 只在同一个 axes 内部排序，axes 之间按添加顺序整体绘制，后添加的 `axr` 整体压在 `axp` 之上。

错误修法（治标）：`axr.set_zorder(0)` + `axp.set_zorder(1)` + `axp.patch.set_visible(False)`。可行但两套坐标系仍需人工对齐，且标签仍在另一 axes 里，无法与线比较层级。

正确做法（当前脚本）：

```python
price_top = hi * price_mult          # 左轴顶部
rev_top = max(rev_max * rev_mult, 1e-9)
scale = price_top / rev_top          # 亿元 → 左轴价格坐标

ax = fig.add_subplot(gs[0])
ax.set_ylim(0, price_top)
axr = ax.secondary_yaxis("right",
                         functions=(lambda v: v / scale, lambda v: v * scale))
# 柱：ax.bar(x, rev * scale, bottom=0.0, zorder=st["z"])
# 股价线：ax.plot(x, close, zorder=Z_LINE)
```

一个 axes 承载全部图元，`zorder` 严格生效：柱 → 线 → 标注。

## 4. zorder 常量表

```python
Z_LINE = 6.0         # 股价线：压在全部柱之上
Z_LABEL = 8.0        # 柱顶标签 / 柱底披露日期
Z_NOTE = 9.0         # 披露当日股价点
Z_EXTREME_MK = 10.0  # 高低点标记
Z_EXTREME_TX = 12.0  # 高低点文字
```

柱用 `KINDS` 里自带的 `z`（FY 3.0 / Q3 3.6 / H1 3.9 / Q1 4.2），并按 `DRAW_ORDER = ["FY","Q3","H1","Q1"]` 先画粗口径后画细口径——年报与一季报同日披露时，同年一小段 Q1 柱叠在 FY 柱之上。

年份分隔线 `zorder=1.0`、披露时点竖虚线 `zorder=1.2`、网格 `zorder=0` 且 `set_axisbelow(True)`。

## 5. 刻度自适应

```python
def nice_ticks(top, target=7):   # 期望约 7 段
    raw = top / float(target)
    mag = 10.0 ** np.floor(np.log10(raw))
    for m in (1.0, 2.0, 2.5, 5.0, 10.0):
        if raw <= m * mag:  step = m * mag; break
    return np.arange(0.0, top + step * 1e-9, step)
```

- 002810：`price_top≈65` → 步长 10（0~60）；`rev_top≈22` → 步长 5（0~20）
- 600519：`price_top≈2900` → 步长 500（0~2500）；营收步长 500（亿元）

硬编码步长会在茅台这种量程下把标签挤成竖排黑线。

## 6. 自动挑关键高低点

```python
def pick_extremes(px, n=4):
    med = np.nanmedian(closes); rng = max - min
    # 每年取年内最高/最低收盘各作候选，score = |val - med| / rng
    # 按 score 降序取 n 个，同年只取一个（先命中的那个）
```

不足 60 个交易日的年份（上市当年、截尾年）跳过，避免把上市首日异常价当极值。要精确复刻某只票的历史标注位置，用 `--extremes 2018:low,2021:high,...` 显式指定。

## 7. 其他细节

- 字体探测 `fm.fontManager.ttflist` 里的可用名，Windows 下 `Microsoft YaHei`，Linux 容器常见 `Noto Sans CJK SC`。
- `sys.stdout.reconfigure(encoding="utf-8", errors="replace")`，Windows 控制台打印中文表格不乱码。
- 画完后 `plt.close(fig)`，避免批量出图时内存累积。
- 输出目录用 `os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)`，传相对路径也不会因目录缺失失败。
- CSV 用 `utf-8-sig`，Excel 直接打开不乱码。

## 8. 可选扩展

| 需求 | 改法 |
|---|---|
| 真正的日 K 蜡烛 | 用行情表的 `open/high/low/close` 画 `ax.vlines` + `ax.bar` 组合（或 mplfinance），涨跌配色自定；注意蜡烛最小宽度按像素定，缩到 10 年跨度会糊 |
| 周 K / 月 K | 对 `close` 做 `resample("W-FRI")` / `resample("ME")` 后重画，柱状披露点位置不变 |
| 成交量副栏 | 再开一个 `fig.add_gridspec(2,1)` 的窄栏，用 `sharex=ax`，成交量柱 `zorder` 独立 |
| 单季同比 | 由累计口径做差分：`单季 = 本期累计 - 上期累计`（Q1 即累计），同比再比同单季 |
| 披露后 N 日涨跌 | `price_at(+N)` 减去 `price_at(notice)`，可加一栏热力条 |
| 匿名化/去标题 | 出图参数里加 `--no-title`、`--font-scale`，改 `draw()` 的 `ax.set_title` 与 `fig.text` |
