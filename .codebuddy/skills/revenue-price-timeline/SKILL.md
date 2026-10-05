---
name: revenue-price-timeline
description: 生成 A 股个股「营收 × 定期报告披露时点 × 股价」的单面板叠加对照图：左轴为新浪日线前复权收盘价折线，右轴为按报告期累计的营业总收入柱，每根柱的横向位置是该公司该期报告的实际披露日（NOTICE_DATE），一季报/中报/三季报/年报四色区分，柱顶标营收与同口径同比，柱底标披露日期，另有披露当日股价点与关键高低点标注。数据取自 akshare 东方财富「利润表-按报告期」+ 新浪日线前复权，脚本参数化任意 A 股代码。当用户要求「把 XX 的营收、营收公告时间和股价画在一张图上」「营收 vs 披露时点 vs 股价」「财报披露后股价怎么走」「季报/年报披露节奏对照股价」时使用。
agent_created: true
---

# 营收 × 披露时点 × 股价 一图对照

## 目的

把「某只 A 股的历史营收（按报告期累计口径）」与「这些报告的实际披露日期」和「同期股价」压到同一张图里，用于观察：披露节奏、披露时点前后的股价位置、营收同比拐点与股价拐点的时间关系。

产出：1 张 PNG（单面板叠加，左轴股价、右轴营收）+ 1 份明细 CSV（每期报告的 `period_end / notice_date / rev_yi / yoy_pct / px_on_notice`）。

## 快速使用

```bash
# 在仓库根目录执行（Windows：.venv\Scripts\python）
.venv/Scripts/python .codebuddy/skills/revenue-price-timeline/scripts/revenue_price_timeline.py \
  --code 002810 --name 山东赫达 --end 2026-09-30 \
  --extremes 2018:low,2021:high,2024:low,2026:high \
  --out research-wiki/research/白马/山东赫达/assets/revenue-price-timeline.png
```

最小用法（其余全部自动）：

```bash
.venv/Scripts/python .codebuddy/skills/revenue-price-timeline/scripts/revenue_price_timeline.py --code 600519 --start 2016-01-01
```

## 参数

| 参数 | 说明 |
|---|---|
| `--code` | 必填，6 位代码；沪 `6`/`9`、北 `4`/`8`、其余深市，前缀自动判断 |
| `--name` | 股票简称，缺省自动查询（东财个股信息 → 全市场代码表兜底） |
| `--start` / `--end` | 起止日，缺省分别取「行情首日」与「今天」；`--start` 不传时图上就是全部上市历史 |
| `--out` | PNG 路径，缺省 `./out/<code>-revenue-price-timeline.png` |
| `--csv` / `--no-csv` | 明细 CSV 路径，缺省与 PNG 同目录同名；`--no-csv` 不导出 |
| `--extremes` | 关键高低点，形如 `2018:low,2021:high,2024:low,2026:high`；缺省自动挑 4 个（每年取年内极值、按偏离中位数程度排序、同年只取一个） |
| `--price-mult` / `--rev-mult` | 左轴/右轴顶部余量系数，默认 1.14；柱顶标签被裁或柱显得太矮时调它 |

## 数据来源与口径（硬约束）

- **营收与披露日**：`ak.stock_profit_sheet_by_report_em(symbol="SH/SZ/BJ"+code)` 的 `REPORT_DATE / REPORT_DATE_NAME / NOTICE_DATE / TOTAL_OPERATE_INCOME`。`NOTICE_DATE` 即该期报告的公开披露日，柱的横坐标用它，**不是报告期末**。
- **股价**：`ak.stock_zh_a_daily(symbol="sh/sz/bj"+code, adjust="qfq")` 日线前复权收盘价。
- **同比**：与「上年同一报告期末」的累计口径相比（Q1 vs 上年 Q1、H1 vs 上年 H1……），不是单季同比。
- **柱高不可跨口径比高低**：Q1=3 个月、H1=6 个月、Q3=9 个月、FY=12 个月，累计口径长度不同。
- 上市前披露的报告期一律不画；行情起点早于上市日的以行情为准，脚注里写明「行情起点为 YYYY-MM-DD，此前披露的报告期未入图」。

## 版式硬约束（改前先读 references/implementation-notes.md）

1. **单 axes + `secondary_yaxis`**，禁止用 `twinx` 叠第二个 axes：matplotlib 按 axes 顺序整体绘制，后加的 axes 会盖住前一个，`zorder` 无法跨 axes 生效，结果是柱子压住股价线。
2. 柱的 y 值先换算到左轴坐标：`scale = price_top / rev_top`，柱高画 `rev * scale`；右轴刻度用 `functions=(v/scale, v*scale)` 换算回来。
3. **zorder 分层**：年份线/披露虚线 1.0~1.2 → 营收柱 3.0~4.2 → 股价线 6.0 → 柱顶标签与柱底日期 8.0+ → 披露日股价点 9.0 → 高低点标记 10.0 → 高低点文字 12.0。用户要求「线/标注压在所有柱之上」时就是这套。
4. 两侧刻度用 `nice_ticks(top)` 自适应整数步长（默认期望约 7 段），避免出现 17.5 / 12.5 这类读数。
5. 柱宽随涵盖月份递增：Q1 22 天 / H1 30 天 / Q3 38 天 / FY 46 天；年报半透明（alpha 0.48）以便与同年一季报同日披露时叠放可见。
6. 字体按可用性探测：Microsoft YaHei → SimHei → Noto Sans CJK SC → Source Han Sans SC → Arial Unicode MS。
7. 画布 29×12.4 inch @150dpi，标题左对齐、图例一行 7 项在标题下方，脚注 5 行说明数据来源/读法/图层顺序/颜色口径/口径与行情起点。
8. **标题与图例必须按 inch 拉开，别凭感觉给 pad**：图例用 `loc="lower left"` + `bbox_to_anchor=(0.0, 1.032)`（悬在绘图区上沿之上 ≈0.032×axes高），标题用 `loc="left"` + `pad=78`（≈1.08 inch）。
   实测坑：早期写的「图例 `1.076` + 标题 `pad=46`」在 8.73 inch 高的绘图区上分别落在 ≈0.66 / 0.64 inch，**同一高度 → 标题与图例字压字**。
   复核公式：图例锚点偏移(inch) = 0.032 × axes 高度；标题 pad(pt)/72 必须 > 锚点偏移 + 图例高度(≈0.3 inch)，留 0.4 inch 以上净空。

## 落盘约定（本仓库）

- 图：`research-wiki/research/<分类>/<中文名>/assets/revenue-price-timeline.png`
- 明细：`scripts/out/<code>_revenue_vs_price.csv`（脚本与明细仍按 6 位代码命名，与 `scripts/<code>/` 一致）。
  **注意**：脚本缺省把 CSV 写在 PNG 同目录同名，要按本仓库约定落盘得显式加 `--csv scripts/out/<code>_revenue_vs_price.csv`，否则会在 assets/ 里多出一份副本。
- **Windows cmd 传中文 `--out`**：先 `set "PYTHONUTF8=1"`（必须带引号；写成 `set PYTHONUTF8=1 &&` 会带上尾随空格 → `invalid PYTHONUTF8 environment variable value`）。不设置则 argv 里的中文会 mojibake，报 `OSError: [Errno 22] Invalid argument: 'research-wiki/research/????/…'`。
- **目录名一律用股票简称中文名，不用 6 位代码**（如 `白马/山东赫达`、`白马/贵州茅台`），与同级已有目录的命名风格保持一致；中文名取图上所用简称（`--name`，缺省时由接口自动查询得到）。
- 新标的先确认「分类目录 + 中文名」再写，勿自建分类；已建页标的沿用其既有目录。
- **目录改名时**（如把代码目录换成中文名）必须连带同步，否则 wiki 链接会断：
  1. `git mv` 重命名目录（保留 git 历史）；
  2. 改 `research/index.md` 里的 `[[分类/旧名/文章]]` wikilink（含「最后更新」摘要里的那些）；
  3. 改页面正文里复现命令的 `--out` 路径、以及本 SKILL.md 与脚本 docstring 的示例路径；
  4. 跑 `.venv/Scripts/python scripts/generate_wiki_index.py` 重建视图，再用 `git rm -r research-wiki/view/stocks/<旧名>` 删掉旧视图目录。

## 已验证样例

- **688188 柏楚电子 · 2019-08-08 ~ 2026-09-30**（2026-10-05，落 `AI软件/柏楚电子/`）：科创板也走 SH 前缀，28 期报告入图（FY/H1/Q1/Q3 各 7 期）；显式 `--extremes 2019:low,2021:high,2022:low,2026:high`，页面要点引用的高低点数字与图完全一致（`parse_extremes` 取年内收盘极值，可先用 `stock_zh_a_daily` 自行算一遍再传）。
- **002810 山东赫达 · 2016-08-26 ~ 2026-09-30**（2026-10-04）：共 40 期报告入图（FY/H1/Q1/Q3 各 10 期）。2021 年内收盘高点 57.06 元（前复权，不复权约 85.58 元），而 FY2021 营收 15.60 亿 +19.2% 要到 2022-04-26 才披露（当日收盘 32.94 元）；2024 年内收盘低点 9.78 元；三季报披露集中在 10-19 ~ 10-31，年报集中在 04-26 ~ 04-28。
  复现命令即上面的「快速使用」；`--extremes` 用显式指定可复刻四色标注位置（自动挑选会在个别年份给出不同结果）。
- **600519 贵州茅台 · 2016-01-01 起**（2026-10-04）：验证沪市前缀、简称自动获取（东财个股信息接口被拒时由全市场代码表兜底）、大额量程下刻度步长自适应（左轴 0~2500 元 / 步长 500）。

## 常见问题

- **东财 push2 接口偶发被拒**（`RemoteDisconnected`）：脚本内已对财务表与行情做 4 次重试；简称查询失败会退回 `ak.stock_info_a_code_name()`（约 6 秒，带 tqdm 进度条，输出在 stderr）。
- **年报与次年一季报同日披露**：较矮的 Q1 柱叠在 FY 柱内部，属正常现象，图例与脚注已说明。
- **某期营收缺失**（接口返回 NaN）：该期直接跳过，不补 0、不估算。
- 需要真正的 K 线蜡烛 / 周月线 / 成交量副栏时：见 references/implementation-notes.md 的「可选扩展」，按要求改造后再出图。
