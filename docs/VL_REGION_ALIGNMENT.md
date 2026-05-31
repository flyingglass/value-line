# Value Line 报告逐区域对齐分析

> **参考来源:**
> - VL 官方手册: `1503516_Reading_VL_Report_WEB_2.7.17.pdf` (15页, May 12, 2017)
> - 项目实现: `engine.py` / `generate_report.py` / `config.py` / `fetcher.py`
> - 现有文档: `docs/VL_INDICATORS_SPEC.md` / `docs/VL_REPORT_MANUAL_ZH.md`

---

## VL 报告总览: 16 个功能区域

以迪士尼 (NYSE: DIS) 样本报告为基准, Value Line 单页报告包含以下区域:

```
┌───────────────────┬──────────────────────┬─────────────┐
│  Ratings Box      │  Header (Price/PE/   │  Target     │
│  (1.排名+β值)     │   Yield/Relative PE)  │  Price      │
├───────────────────┤                      │  Range      │
│  Legends Box      │  Price Chart         │  (3-5年)    │
│  (2.现金流倍数)    │  (K线+CF线+RS线+Vol)  │             │
├───────────────────┼──────────────────────┤             │
│  Projections      │                      │             │
│  (3-5年预测)      ├──────────────────────┼─────────────┤
├───────────────────┤  STATISTICAL ARRAY   │  Ratings    │
│  Insider/         │  23行历史数据+预测     │  (Fin.Str,  │
│  Institutional    │  (17年历史)           │   Stability,│
│  Decisions        │                      │   etc.)     │
├───────────────────┼──────────────────────┤             │
│  Business         │  Analyst Commentary  │             │
│  Description      │  (300-400字)         │             │
├───────────────────┼──────────────────────┤             │
│  Capital          │  Footnotes           │             │
│  Structure        │  (脚注)              │             │
├───────────────────┤                      │             │
│  Current          │                      │             │
│  Position (3年)    │                      │             │
├───────────────────┤                      │             │
│  Annual Rates     │                      │             │
│  of Change        │                      │             │
├───────────────────┤                      │             │
│  Quarterly Data   │                      │             │
│  (Rev/EPS/Divs)   │                      │             │
└───────────────────┴──────────────────────┴─────────────┘
```

---

## 区域 1: Ratings Box (排名框)

**VL 原文位置:** 手册 P.4-5, 样本报告左上角 (item 1)

### VL 定义

| 指标 | VL 定义 | 范围/说明 |
|------|--------|----------|
| **Timeliness™** | 未来6-12个月预期价格表现排名 | 1(最高)~5(最低), 100/300/900/300/100分布 |
| **Safety™** | 总风险排名 = (Financial Strength + Price Stability)/2 | 1~5, 数量不限 |
| **Technical** | 短期(3-6月)相对价格变化预测 | 1~5, 10个价格趋势因子 |
| **Beta** | 相对市场波动率 | 1.00=市场同步 |
| **Price Growth Persistence** | 过去10年相对股价增长一致性 | 评级分 |
| **Earnings Predictability** | 盈利预测可靠性 | 百分制 |

### A/H 股实现状态

| 指标 | 实现状态 | 当前方案 | 差距 |
|------|---------|---------|------|
| Timeliness | ❌ 未实现 | — | 需要价格趋势模型 |
| Safety | ❌ 未实现 | — | 需要财务强度+价格稳定性模型 |
| Technical | ❌ 未实现 | — | 需要10因子价格趋势模型 |
| Beta | ❌ 未实现 | — | 可从日K线回归计算 |
| Price Growth Persistence | ❌ 未实现 | — | VL专有算法 |
| Earnings Predictability | ❌ 未实现 | — | VL专有算法 |

**VL原文 (P.4):**
> "Timeliness rank is Value Line's projection of the expected price performance of a stock for the coming six to 12 months relative to our approximately 1,700 stock universe."
> "The Safety rank is derived from two measurements (weighted equally)... a Company's Financial Strength and a Stock's Price Stability."

**建议优先级:** P3 (高级功能, 核心统计数组和业务描述优先)

---

## 区域 2: Legends Box (图例框)

**VL 原文位置:** 手册 P.14 Item 2, 样本报告图表左上

**VL 原文:**
> *"The Legends box contains the 'cash flow' multiple, the amounts and dates of recent stock splits, and an indication if options on the stock are traded."*

### 指标对比与含义

| # | VL 原版指标 | VL 公式 / 含义 | 当前实现 | 数据来源 | 样式 | 差距 |
|---|---|---|---|---|---|---|
| 1 | **CF Multiple** | 分析师选定倍数 × 每股现金流(盈利+折旧-优先股息)，使 CF 线对齐 3-5 年目标价。倍数不固定，股价偏离线太远会调整 | `cf_line = PER_NETCASH × 15`，硬编码 15 倍 | `engine.py` → ECharts | `━━━` 蓝实线 (#1976D2) → K线图 CF 线 `solid` | ⚠️ 硬编码15，非动态 |
| 2 | **Rel Price Strength** | 个股价格 ÷ VL 全样本(~1700只)算术平均。线上涨=跑赢大市，线下跌=跑输 | RS 线=个股(基期100) ÷ 恒指/CSI300(基期100) 双线对比 | `index_kline` + `kline` → ECharts | `···` 红虚线 (#ef232a) → K线图 RS 个股线 `dotted` | ⚠️ 对标从 VL 全样本→市场指数 |
| 3 | **Options** | 该股是否有对应期权产品在交易所交易 | `meta.options` (No/Yes) | `config.py` 手动配置 | 纯文本，无图例 | ✅ A/H 股多数为 No |
| 4 | **Stock Splits** | 历史拆股/送股的日期和比例。无拆分显示 None | `meta.splits` (None/具体) | `config.py` 手动配置 | 纯文本，无图例 | ✅ |
| 5 | **Shaded area** | 图表灰色阴影=美国 NBER 衰退期 | 无 | — | — | ❌ A/H 不适用 |

### 非 LEGENDS 指标 (在 VL 报告中位于 LEGENDS 下方独立区域)

| 指标 | VL 实际位置 | 含义 |
|---|---|---|
| **% Total Return** (1yr/3yr/5yr) | 图表左下角独立 | 股价涨跌 + 股息 = 总回报，与 VL 算术平均指数对比 |
| **P/E P/B Yld** | LEGENDS 下方 | 当前估值快照 |
| **PE H/L/Avg** | LEGENDS 下方 | 年度 PE 历史区间 |

### 最终样式规格

```
LEGENDS                         ← 8.5px 粗体
────── 实线 1px #000
━━━  (蓝色实线, 10px, #1976D2)    ← 图例标记
15.0 x "Cash Flow" p sh          ← 指标名 (8px)
      ← 空白间隔 4px
······ (红色点, 10px, #ef232a, 6个·) ← 图例标记
Relative Price Strength          ← 指标名 (8px)
      ← 空白间隔 3px
Splits: None / Options: No       ← 补充信息 (8px)
      ← 空白间隔 15px
% TOT. RETURN                    ← 8.5px 粗体
────── 实线 1px #000
THIS (bold)  STOCK (bold)  HSI   ← 8.5px 表格
1 yr.        -30.3%       8.1%
3 yr.        812.2%       38.1%
5 yr.        129.3%       -13.6%
```

**布局:** 左侧列 flex 容器 height:290px，LEGENDS+% TOT. RETURN 在上部，Percent/shares/traded 用 margin-top:auto 沉底。

## 区域 2B: % Total Return (总回报)

**VL 原文位置:** 图表左下角，LEGENDS 下方独立区域

**VL 公式 (Item 19):**
> *"Annual Total Return (percent including dividends)"*

`% Total Return = (期末价 - 期初价 + 累计股息) / 期初价 × 100`

- 累计回报，非年化
- 包含股息
- 双列对比：THIS STOCK vs VL Arithmetic Index

### 当前实现

| 指标 | VL 原版 | 当前实现 | 数据来源 | 差距 |
|---|---|---|---|---|
| **公式** | (期末-期初+股息)/期初 ×100 | 同公式，含年度DPS | `engine.py:_calc_return()` | ✅ |
| **期间** | 1yr / 3yr / 5yr | 最近 12/36/60 个月 | K线月线 close | ✅ |
| **个股** | THIS STOCK | 含股息累计回报 | kline + dividend DPS | ✅ |
| **对比基准** | VL Arithmetic Index (~1700只) | HSI (港股) / CSI300 (A股) | `index_kline` 月线 close | ⚠️ 对标改为市场指数 |
| **格式** | 双列表格 (THIS | VL ARITH.) | 双列表格 (THIS | HSI/CSI300) | ✅ |

### 最终样式

```
                    ← 15px 空白
% TOT. RETURN       ← 8.5px 粗体
────── 实线 1px #000
          THIS   STOCK   HSI/CSI300  ← 8.5px 表格, THIS/STOCK/指数名 bold
  1 yr.  -30.3%         8.1%
  3 yr.  812.2%        38.1%
  5 yr.  129.3%       -13.6%
```

**数据来源:**
- `engine.py:_calc_return()` — 含股息累计回报
- K线月线 `close` 最近 12/36/60 个月
- 个股价差 + 累计 `DPS`
- 指数不含股息 (仅价差)
- 表格字号 8.5px, line-height 1.35

---

## 区域 3: Header (顶部报价区)

**VL 原文位置:** 手册 P.4-5, 样本报告顶部 (items 5-9)

### VL 定义

| 指标 | VL 公式 | VL 原文 |
|------|--------|--------|
| **RECENT PRICE** | 最新交易日收盘价 | "Price as of the date listed..." |
| **P/E RATIO** | 最新价 ÷ (过去6个月实际EPS + 未来6个月预估EPS) | "recent price divided by the latest six months' earnings per share plus earnings estimated for the next six months" |
| **Trailing P/E** | 最新价 ÷ 过去4个季度实际EPS | "recent price divided by the sum of reported earnings for the past four reported quarters" |
| **Median P/E** | 过去10年年度PE的统计调整中位数 | "average annual P/E ratio... over the past 10 years, with certain statistical adjustments made for unusually low or high ratios" |
| **RELATIVE P/E** | 当前P/E ÷ VL 全样本(~1700)的预估PE中位数 | "stock's current P/E divided by the median P/E for the approximately 1,700 stocks under Value Line review" |
| **DIV'D YLD** | 未来12个月预估股息 ÷ 最新价 | "cash dividends estimated to be declared in the next 12 months divided by the recent price" |

### A/H 股实现状态 (2026-05-30 最终确认)

| 指标 | VL原始口径 | 当前口径 | 计算代码 | 差距说明 |
|------|-----------|---------|---------|---------|
| **RECENT PRICE** | 最新交易日收盘价 | `spot.price` (AKShare实时价) | `fetcher.py` → spot表 | ✅ 一致 |
| **P/E RATIO** | Price ÷ (6M实际+6M预估EPS) | Price ÷ TTM EPS | `engine.py:_compute_ttm_eps()` | ⚠️ VL=Forward PE, 当前=TTM (标注TTM) |
| **Trailing P/E** | Price ÷ 过去4Q实际EPS | Price ÷ TTM EPS (同上) | 同 P/E RATIO | ✅ 与P/E同源,TTM=Trailing |
| **Median P/E** | 10年PE中位数(统计调整) | IQR(1.5×)过滤+中位数,≤10年 | `engine.py:_median_pe_iqr()` | ✅ IQR替代VL统计调整 |
| **RELATIVE P/E** | Stock PE ÷ VL~1700股票PE中位数 | Stock PE_AVG ÷ 市场指数PE(HSI/CSI300) | `engine.py:_compute_pe_metrics()` | ⚠️ 对标VL universe→市场指数 |
| **DIV'D YLD** | 预估未来12M股息 ÷ 最新价 | 最近年度DPS ÷ 最新价 | `spot.div_yield` | ⚠️ VL=Forward, 当前=TTM |

### 详细计算公式

**TTM EPS** (`_compute_ttm_eps(reader, latest_yr)`):
```
if 半年报可用: TTM_EPS = 最新H1_EPS + (上年FY_EPS - 上年H1_EPS)
else: 回退为最新年报EPS
```
数据来源: `income` 表 STD_ITEM_CODE 004027002 (基本每股收益)

**Median P/E** (`_median_pe_iqr(pe_values, years=10)`):
```
1. 取最近≤10年年度PE值 (年均价÷年EPS)
2. 计算 IQR = Q3 - Q1, 排除 [Q1-1.5*IQR, Q3+1.5*IQR] 外的异常值
3. 剩余值取中位数
```

**RELATIVE P/E**:
```
个股年PE = 月均价均值 ÷ 年EPS
相对PE = 个股年PE ÷ 参考PE
港股参考: HSI PE, A股参考: CSI300 PE
```

**DIV'D YLD**:
```
股息率 = 最近年度每股分红 ÷ spot.price × 100
港股来源: stock_hk_dividend_payout_em (常有0值, 需手动补充)
A股来源: 同花顺分红数据
```

### Header 最终样式 (已确认)

HTML `<table>` 2行布局:

```
POP MART 09992.HK │ RECENT │ 153.60 │ P/E │ 30.1 │ (Trailing:30.1) │ RELATIVE │ 0.97 │ DIV'D │ 1.4%
                  │ PRICE  │        │RATIO│      │ (Median:50.0)  │P/E RATIO │      │ YLD   │
```

| 元素 | 字号 | 粗体 | 说明 |
|---|---|---|---|
| POP MART | 18px | 700 | 公司名 |
| 09992.HK | 9px | 700 | 代码,同行右侧 |
| RECENT/PRICE等标签 | 9px | 700 | #000 |
| 价格值 | 18px | 700 | rowspan=2居中 |
| 其他值 | 17px | 700 | P/E, REL, DIV, rowspan=2居中 |
| 括号区 | 9px | 700 | (Trailing:xx)+(Median:xx),每行独立括号 |
| 分隔线 | border-right:1px solid #999 | | 公司名|价格|括号|相对PE 后 |

---

## 区域 4: Price Chart (价格图表)

**VL 原文位置:** 手册 P.7-8, 样本报告中上部 (items 3, 4, 10, 11)

### VL 定义

| 元素 | VL 说明 |
|------|--------|
| **Monthly Price Bars** | 月线高低价竖线 (前复权, 含拆分/送股调整) |
| **"Cash Flow" Line** | 实线: 历史现金流×倍数; 虚线: 预测现金流×倍数 |
| **Relative Price Strength** | 细虚线: 个股 vs VL全样本(算术平均)相对强弱 |
| **Monthly Volume %** | 月成交量÷总股本, 图表底部柱状图 |
| **Yearly High/Low** | 年度最高/最低价, 图表上方表格 |
| **Target Price Range** | 图表右侧: 3-5年预测价格区间 |
| **Recession Shading** | 灰色区域表示经济衰退期 |

### A/H 股实现状态

| 元素 | 实现状态 | 当前方案 | 与VL的差距 |
|------|---------|---------|-----------|
| Monthly Price Bars | ✅ | ECharts candlestick (红涨绿跌) | ✅ 符合中国惯例 |
| Cash Flow Line | ✅ | 15×CF per sh (实线+虚线) | ⚠️ 无预测部分虚线 |
| Relative Price Strength | ⚠️ 替代 | 个股vs HSI/CSI300 指数线 | VL对~1700只美股, 当前对市场指数 |
| Monthly Volume % | ✅ | 成交量÷股本×100% | ✅ |
| Yearly High/Low | ✅ | 从月K线聚合 | ✅ |
| Target Price Range | ❌ | — | 需3-5年预测EPS+PE |
| Recession Shading | ❌ | — | 美股经济周期标注 |

**VL原文 (P.7-8, items 3, 4, 11):**
> "The price chart at the top... contains, among other things, a monthly price history for the stock (the vertical bars) overlaid by a solid line that we call the 'cash flow' line... The dashed line from mid-2016 to mid-2018... is Value Line's projection."
> "Relative Price Strength line... shows the relative performance of Disney stock versus the entire universe of Value Line stocks."
> "At the very bottom of the chart, we show monthly trading volume (item 11) as a percentage of total shares outstanding."

**🔴 关键差异:**
1. **RS线对标对象** — VL对VL全样本, 当前对HSI/CSI300。这是结构差异(VL universe是股票池, 非指数)。
2. **预测虚线段** — "Cash Flow"线的虚线延伸部分是VL分析师预测。当前无预测, 硬停在实际数据末尾。
3. **Target Price Range 缺失** — 需要预测EPS+PE才能绘制。

### 图表技术实现

#### Y轴: Ratio Scale (对数刻度)

VL 使用 Ratio Scale (比例/对数刻度)，而非线性刻度。手册 P.9:
> "The price chart uses a 'ratio scale'... equal percentage changes are represented by equal vertical distances."

**实现方案:**

| 项 | 值 |
|---|---|
| 图表库 | ECharts 5.5.0 |
| 数据变换 | `Math.log(price)` — 自然对数 |
| Y轴类型 | `type:'value'` — log空间中线性轴 |
| 刻度生成 | 种子序列 `[1, 1.6, 2.4, 4, 6]` × 10^k + 4%缓冲区 |
| 范围计算 | `yMin=ln(pMin)-4%， yMax=ln(pMax)+4%` |
| 标签还原 | `Math.exp(v)` — exp反变换为真实价格 |
| tooltip | `Math.exp(v).toFixed(2)` |
| 图表高度 | chart-box: 260px, volume: 30px |
| Grid | `left:0, right:28, top:4, bottom:24` |
| K线颜色 | 红涨绿跌 (#ef232a / #14b143) — 中国惯例 |

**种子序列说明:**
```javascript
seeds = [1, 1.6, 2.4, 4, 6]
// log空间间距 ≈ 0.2, 视觉均匀
// 示例: 10, 16, 24, 40, 60, 100, 160, 240, 400, ...
```

**CF 线:**
- 固态 `#1976D2`, 宽度 1.2px
- 数据同样做 log 变换
- 按年度映射(非月度), 全年统一值

**Relative Price Strength 线:**
- 个股: 红色虚线 `#ef232a`, `dotted`, yAxisIndex:1 (右侧线性轴)
- 指数(HSI): 灰色虚线 `#999`, `dotted`, yAxisIndex:1
- 基期100, 百分比值, 独立线性Y轴

**Volume % (Percent shares traded) 图:**

VL Item 11 — 月换手率柱状图，位于K线图下方volume区域。

**数据计算:**
```
月换手率(%) = 月成交股数(k.volume) ÷ (当年TOTAL_SHARES × 10^6) × 100
```
- 分母按年份匹配股本 `MT[y].TOTAL_SHARES`，历史月份用当时股本(非最新)
- fallback: `showYears`最后一年
- 数据通过 `.toFixed(2)` 保留两位，前缀 `+` 转为数字(避免JS字符串比较Bug)

**Y轴刻度算法 (自适应):**
```javascript
vMax     = volData 数值最大值
maxVol   = vMax × 1.2                         // 20% 比例缓冲
interval = maxVol≤5 ? 1 : maxVol≤50 ? 5 : 10 // 自适应刻度间距
ceilVol  = ceil(maxVol/interval) × interval   // 向上取整到nice number
step     = ceilVol / 3                        // 三等分
```
| vMax范围 | interval | 示例 |
|---------|----------|------|
| ≤4.2% | 1 | max=3 → ceilVol=4 → 刻度 4,3,1 |
| ≤41.7% | 5 | max=35 → ceilVol=45 → 刻度 45,30,15 |
| >41.7% | 10 | max=50 → ceilVol=60 → 刻度 60,40,20 |

**样式参数:**

| 参数 | 值 |
|------|----|
| 图表高度 | 30px |
| grid | left:0, right:0, top:0, bottom:0 |
| 柱颜色(普通月) | `#1976D2` (蓝色) |
| 柱颜色(1月) | `#ff6600` (橙色) |
| barWidth | 60% |
| Y轴刻度 | 隐藏 (axisLabel: false) |
| splitLine | 关闭，改用 markLine 手动绘制 |

**网格线 (markLine):**
| 位置 | 线型 | 宽度 | 颜色 |
|------|------|------|------|
| 顶线 (ceilVol) | 实线 solid | **3.0px** 加粗 | #000 |
| 中线 (step×2) | 实线 solid | 0.5px | #000 |
| 底线 (step) | 实线 solid | 0.5px | #000 |
| 0线 | 不绘制 | — | — |

**左侧标签:**
- 表格3行: `Percent | 刻度值` / `shares | 刻度值` / `traded | 刻度值`
- 字体 8.5px bold, 右对齐
- 刻度值由 JS 动态更新 (`document.getElementById('vs1'/'vs2'/'vs3')`)
- 位于 LEGENDS 列 flex 容器底部 (margin-top:auto, height:290px)

**年度 High/Low 表格:**
- 位于 K线图上方, 每列对应一年
- 从月K线按年聚合最高/最低价

---

## 区域 5: Statistical Array (统计数组) — 项目核心

**VL 原文位置:** 手册 P.8-10, 样本报告中下部 (items 12, 18)

### VL 定义 (23行, 历史17年 + 当前年 + 未来3-5年预测)

VL 手册 P.8-10 逐行定义了23个指标(本项目增加毛利率为24行):

```
┌──────────────────────────────────────────────────┐
│                    LEFT SIDE           RIGHT SIDE│
│  Historical Data (Regular Type)     Estimates    │
│  up to 17 years                   (Bold Italics) │
│                                                  │
│  2006 2007 ... 2016              2017 2018 20-22│
│  ───────────────────────────────────────────────│
│  1  Revenues per sh              ○○○ → ○○○ ○○   │
│  2  "Cash Flow" per sh           ○○○ → ○○○ ○○   │
│  3  Earnings per sh              ○○○ → ○○○ ○○   │
│  4  Div'ds Decl'd per sh         ○○○ → ○○○ ○○   │
│  5  Cap'l Spending per sh        ○○○ → ○○○ ○○   │
│  6  Book Value per sh            ○○○ → ○○○ ○○   │
│  ── 分隔线 ──                                   │
│  7  Common Shs Outst'g (mil)     ○○○ → ○○○ ○○   │
│  8  Avg Ann'l P/E Ratio          ○○○ → ○○○ ○○   │
│  9  Relative P/E Ratio           ○○○ → ○○○ ○○   │
│  10 Avg Ann'l Div'd Yield        ○○○ → ○○○ ○○   │
│  ── 分隔线 ──                                   │
│  11 Revenues ($mill)             ○○○ → ○○○ ○○   │
│  12 Operating Margin             ○○○ → ○○○ ○○   │
│  13 Depreciation ($mill)         ○○○ → ○○○ ○○   │
│  14 Net Profit ($mill)           ○○○ → ○○○ ○○   │
│  15 Income Tax Rate              ○○○ → ○○○ ○○   │
│  16 Net Profit Margin            ○○○ → ○○○ ○○   │
│  ── 分隔线 ──                                   │
│  17 Working Cap'l ($mill)        ○○○ → ○○○ ○○   │
│  18 Long-Term Debt ($mill)       ○○○ → ○○○ ○○   │
│  19 Shr. Equity ($mill)          ○○○ → ○○○ ○○   │
│  ── 分隔线 ──                                   │
│  20 Return on Total Cap'l        ○○○ → ○○○ ○○   │
│  21 Return on Shr. Equity        ○○○ → ○○○ ○○   │
│  22 Retained to Com Eq           ○○○ → ○○○ ○○   │
│  23 All Div'ds to Net Prof       ○○○ → ○○○ ○○   │
└──────────────────────────────────────────────────┘
```

> **注意:** 本项目增加 Gross Margin (毛利率) 在第11行Revenues和第12行Operating Margin之间, 形成24行。VL原版无此行。

### 当前实现 vs VL 逐行对照

每行的详细计算和A/H映射已在 `docs/VL_INDICATORS_SPEC.md` 中记录。以下是关键结构性差异:

| 维度 | VL 定义 | 本项目 | 差距等级 |
|------|--------|--------|---------|
| **历史列数** | 最多17年 | 最多10年 (allY[-10:]) | 🟡 P2 |
| **预测列** | 当前年+次年+3-5年(粗斜体) | ❌ 无预测列 | 🔴 P0 |
| **单位** | 百万美元 ($mill) | 亿元 (÷1e8) | 🟡 P2 |
| **EPS口径** | 稀释EPS, 排除非经常性 | 基本EPS, 含非经常性 | 🟡 P1 |
| **Cash Flow** | NetIncome + D&A - PreferredDiv | 当前未减优先股股息 | 🟢 P3 |
| **毛利率行** | VL原版无 | 本项目新增(行12) | ✅ 设计决策 |
| **行号对应** | VL 23行 = 项目 24行(因新增毛利率) | 项目行12=VL行12(Op Margin) | 注意偏移 |

**VL原文 (P.8-10):**
> "When available, our historical array includes per-share data dating back up to 17 years."
> "We also project statistical data for the current fiscal year, next fiscal year, as well as three to five years into the future. These projections are presented in bold italics."

**🔴 最大差距: 无预测列。**
VL报告的核心价值之一是分析师预测(未来3-5年)。当前项目仅展示历史数据, 缺失"右侧粗斜体预测列"。这是本项目与VL原版最本质的功能差距。

### 当前实现样式规格

```
Year                           2017   2018   2019   ...    ← 8.5px bold #000, border-top/bottom #ccc
Revenues per sh      每股营收   27.64  9.71   4.67   ...    ← 英文名: 9px bold, 中文名: 7.5px #666
"Cash Flow" per sh   每股现金流  10.43  2.99   1.30   ...
Earnings per sh      每股收益     9.58   2.35   0.81   ...
────────────────────  分区线 (2px solid #000)  ──────────
Common Shs Outst'g   发行在外股数  ...
Avg Ann'l P/E Ratio  平均年化PE   ...
...
```

**样式参数:**
| 参数 | 值 |
|------|----|
| 英文指标名 | 9px, bold, #000 |
| 中文指标名 | 7.5px, normal, #666 |
| 数据值 | 8.5px, right-align |
| 年份行 | 8.5px, bold, border-top/bottom: 1px solid #ccc |
| 分区线 | 2px solid #000 (每6/4/7/3/4行一组) |
| 列分隔 | 1px solid #ddd |
| 空值 | "—" |

**数据口径:**
- EPS: DILUTED_EPS, AKShare
- 净利: adj_np = 归母净利 - 非经常性项目(税后)
- ROE: adj_np ÷ 期末总权益
- 全链使用 adj_np: PER_NETCASH, ROE, RETAINED, PAYOUT, NET_PROFIT_MARGIN

---

## 区域 6: Business Description (业务描述)

**VL 原文位置:** 手册 P.10, 样本报告左下

### VL 定义

> VL将业务描述放在 Statistical Array 和 Capital Structure 之间, 格式为紧排的一段文字。以迪士尼为例:
> "BUSINESS: The Walt Disney Company operates Media Networks, incl. ABC and ESPN (43% of '16 revs.); Parks and Resorts..."

内容通常包括:
- 主要业务板块及营收占比
- 重要收购/剥离事件
- 折旧率、员工人数
- 高管持股、注册地
- 公司地址/电话/网址

### A/H 股实现状态

| 内容 | 实现状态 | 数据来源 | 差距 |
|------|---------|---------|------|
| 业务板块+营收占比 | ⚠️ 部分 | `revenue_structure`表 + `extract_pdf_metadata.py` | 质量依赖PDF提取效果 |
| 员工人数 | ⚠️ 部分 | `extract_pdf_metadata.py` 正则提取 | 成功率约70% |
| 收购/剥离事件 | ❌ | — | 需手动录入或AI提取 |
| 折旧率 | ❌ | — | 未见实现 |
| 高管/地址 | ❌ | — | 低优先级, config可补充 |
| 注册地 | ❌ | — | config中无此字段 |

**当前实现 (generate_report.py L.125-167):**
- 从 SQLite meta 表读取 `business_desc` 和 `employee_count`
- 如果缺失, 从 config + report_data.json 动态生成简化版
- 营收结构从 `revenue_structure` 表读取

**VL原文 (P.10, Footnote):**
> "'16 depr. rate: 4.7%. Employs 195,000. Off. and dir., less than 1% of common stock; Vanguard, 5.5% (1/17 proxy). Chairman/CEO: Robert A. Iger. Inc.: DE."

**🔴 差距:** VL的Business是一个高度信息密度的文本块, 包含收购历史、折旧率、高管、注册地等。当前主要靠PDF提取, 质量不稳定。

---

## 区域 7: Capital Structure (资本结构)

**VL 原文位置:** 手册 P.10, 样本报告左栏中部 (迪士尼样本 P.13)

### VL 定义 (迪士尼样本)

```
CAPITAL STRUCTURE as of 12/31/16
Total Debt $20,490 mill.    Due in 5 Yrs $11,275 mill.
LT Debt $14,792 mill.       LT Interest $600 mill.
(Total interest coverage: NMF)
(24% of Cap'l)
Leases, Uncapitalized Annual rentals 477.0 mill.
Pension Assets-10/16 $10.41 bill.  Oblig. $14.48 bill.
Pfd Stock None
Common Stock 1,581,248,242 shs.  as of 2/1/17

MARKET CAP: $182 billion (Large Cap)
```

### A/H 股实现状态

| VL行 | 含义 | 实现状态 | 数据来源 | 差距 |
|------|------|---------|---------|------|
| Total Debt | 总负债 | ✅ | balance.总负债 | ✅ |
| Due in 5 Yrs | 5年内到期 | ⚠️ 近似 | 融资租赁(流)+短期贷款+长期应付款 | 需确认VL口径 |
| LT Debt | 长期债务 | ✅ | 融资租赁(非流) → 长期贷款 | ✅ |
| LT Interest | 长期利息 | ⚠️ 近似 | income.融资成本 | ✅ 近似 |
| Coverage | 利息覆盖倍数 | ✅ | 经营溢利÷利息支出 | ✅ |
| % of Capital | LT Debt占比 | ✅ | LT_Debt÷(LT_Debt+Equity) | ✅ |
| Leases | 未资本化租赁 | ❌ | 不在中国准则常见披露中 | 中美准则差异 |
| Pension | 养老金资产/义务 | ❌ | 中美差异, 不适用 | 可能不适用 |
| Pfd Stock | 优先股 | ⚠️ 占位 | "None" | A/H股基本无优先股 |
| Common Stock | 普通股股数 | ✅ | config.shares/动态计算 | ✅ |
| MARKET CAP | 市值 | ✅ | price×shares | ✅ |

**当前实现:** `_build_capital_structure()` 在 engine.py L.606-709, 自动检测单位(万亿/亿/万)

**🔴 关键差异:**
1. **Leases** — VL专门列出未资本化经营租赁。中国准则下经营租赁也已上表(新租赁准则), 差异缩小。
2. **Pension** — 美国的DB养老金计划披露, 中国通常为DC计划, 不适用。
3. **% of Capital** — VL展示为 `(24% of Cap'l)`, 指 LT Debt ÷ (LT Debt + Equity)。已实现。

---

## 区域 8: Current Position (短期资产负债)

**VL 原文位置:** 手册 P.10, 样本报告左栏 (3年对比)

### VL 定义 (迪士尼样本)

```
CURRENT POSITION      2015   2016  12/31/16
($MILL.)
Cash Assets           4269   4610    3736
Receivables           8019   9065    9878
Inventory(AvgCst)     1575   1562    1390
Other Current Assets  895    729    1661
Current Assets       16758  16966   16665
Accounts Payable      7844   9130    9979
Debt Due              4563   3687    5698
Other Current Liab    3927   4025    3640
Current Liabilities  16334  16842   19317
```

### A/H 股实现状态

| 行 | 实现状态 | 数据来源 | 差距 |
|---|---------|---------|------|
| Cash Assets | ✅ | balance.现金及等价物 | ✅ |
| Receivables | ✅ | balance.应收帐款 | ✅ |
| Inventory | ✅ | balance.存货 | ✅ VL标记AvgCst (平均成本法) |
| Other CA | ✅ | 流动资产合计 - (现金+应收+存货) | ✅ |
| Current Assets | ✅ | balance.流动资产合计 | ✅ |
| Accounts Payable | ✅ | balance.应付帐款 | ⚠️ 字段名是否需要映射确认 |
| Debt Due | ⚠️ 近似 | balance.融资租赁负债(流动) | VL的Debt Due=一年内到期长期债务 |
| Other CL | ✅ | 流动负债合计 - (应付+DebtDue) | ✅ |
| Current Liabilities | ✅ | balance.流动负债合计 | ✅ |

**当前实现:** `_build_current_position()` engine.py L.712-750, 最近3年

**🔴 关键差异:**
1. **Debt Due 口径** — VL是"一年内到期的长期债务", 当前使用"融资租赁负债(流动)"。应包含: 一年内到期长期借款 + 一年内到期应付债券 + 融资租赁负债(流动)。
2. **Inventory 标记 Average Cost** — VL标注存货计价方法, 本项目无此标注。

---

## 区域 9: Annual Rates of Change (复合增长率)

**VL 原文位置:** 手册 P.7, 样本报告左栏 (items 17)

### VL 定义 (迪士尼样本)

```
ANNUAL RATES          Past     Past    Est'd
of change (per sh)   10 Yrs.  5 Yrs.  '14-'16 to '20-'22
Revenues              7.5%     9.5%    6.0%
"Cash Flow"           12.5%    15.0%   4.0%
Earnings              14.0%    18.5%   7.5%
Dividends             19.0%    30.0%   7.5%
Book Value            7.0%     6.5%    7.0%
```

### A/H 股实现状态

| 指标 | 实现状态 | 计算方式 | 预测列 |
|------|---------|---------|--------|
| Revenues (per sh) | ✅ | OPERATE_INCOME CAGR | ❌ |
| "Cash Flow" (per sh) | ✅ | PER_NETCASH CAGR | ❌ |
| Earnings (per sh) | ✅ | BASIC_EPS CAGR | ❌ |
| Dividends (per sh) | ✅ | DPS CAGR | ❌ |
| Book Value (per sh) | ✅ | BPS CAGR | ❌ |

**当前实现:** `_build_annual_rates()` engine.py L.753-791
- 有10年数据→显示 10yr/5yr/3yr
- 不足10年→显示 5yr/3yr/1yr
- **预测列未实现** — VL有 "Est'd '14-'16 to '20-'22" 列

**VL原文 (P.7):**
> "The Annual Rates box (item 17) shows the compound annual growth percentages for sales, cash flow, and other items for the past 5 and 10 years and also Value Line's projections of growth for each item for the coming 3 to 5 years."

**🔴 差距:** VL的Annual Rates包含3列 (Past 10 Yrs / Past 5 Yrs / Estimated 3-5yr), 当前只有历史无预测。

---

## 区域 10: Quarterly Data (季度数据)

**VL 原文位置:** 手册 P.10-11, 样本报告左栏底部 (items 16)

### VL 定义 (迪士尼样本)

VL左栏底部有三个季度表:

1. **QUARTERLY REVENUES ($mill.)** — 按财年季度 (Mar/Jun/Sep/Dec) + Full Year
2. **EARNINGS PER SHARE** — 季度EPS (含预估, 粗体)
3. **QUARTERLY DIVIDENDS PAID** — 实际支付股息 (按日历年)

> VL原文 (P.14, item 16):
> "Quarterly Sales are shown on a gross basis. Quarterly earnings on a per-share basis (estimates in bold type). Quarterly Dividends Paid are actual payments. The total of dividends paid in four quarters may not equal the figure shown in the annual series on dividends declared... (Sometimes a dividend declared at the end of the year will be paid in the first quarter of the following year.)"

### A/H 股实现状态

| 季度表 | 实现状态 | 数据来源 | 差距 |
|--------|---------|---------|------|
| Quarterly Revenues | ⚠️ 半年度 | income表 STD_ITEM_CODE | VL为4季度, 港股仅2半年 |
| Quarterly EPS | ⚠️ 半年度 | income表 STD_ITEM_CODE | 同上 |
| Quarterly Dividends | ⚠️ 年度 | dividend表 | VL有季度拆分, 当前仅年度总额 |

**当前实现:** `build_semi_annual()` engine.py L.387-499
- 有季报(Q1/Q2/Q3/Q4) → 4季度+全年
- 仅半年报 → H1/H2/Full Yr (港股标准)
- 股息: 仅显示年度DPS (无季度拆分)

**VL Quarterly Sales 说明 (P.14, item 16):**
> "Quarterly Sales are shown on a gross basis. Quarterly earnings on a per-share basis (estimates in bold type)."

**🔴 关键差异:**
1. **季度 vs 半年度** — VL原版是4季度报告, A股理论支持, 港股仅半年。
2. **预测列缺失** — VL的季度EPS表有粗体预测, 当前全为历史。
3. **股息表结构差异** — VL有实际支付日期(日历拆分), 当前仅年度总额。
4. **Dividends Declared vs Paid** — VL区分宣告股息(行4)和支付股息(季度表), 当前两者都读同一数据源。

---

## 区域 11: Analyst Commentary (分析师点评)

**VL 原文位置:** 手册 P.5, 样本报告中下 (item 13)

### VL 定义

> VL原文 (P.5):
> "Many readers think our commentary (item 13) is the most important section of the page."
> "A 300–400 word report on recent developments and prospects—issued every three months."

内容结构 (以迪士尼为例):
- 近期业绩表现归因
- 业务板块表现拆解
- 战略投资方向
- 未来展望和风险
- 估值观点及投资建议

### A/H 股实现状态

| 内容 | 实现状态 | 当前方案 | 差距 |
|------|---------|---------|------|
| 近期业绩 | ⚠️ 自动生成 | MDA从PDF提取或财务数据动态生成 | 无分析师观点, 仅是数据陈述 |
| 业务分拆 | ⚠️ 部分 | 营收结构表自动生成 | 无深度分析 |
| 战略分析 | ❌ | 通用模板文本 | 无公司定制 |
| 未来展望 | ❌ | 通用模板 | 无预测 |
| 估值观点 | ❌ | — | 无 |

**当前实现:**
- `extract_mda.py` — 从PDF提取中英文句子, 按6类分类(overview/product/channel/region/cost/outlook)
- PDF提取失败时 `build_mda_from_data()` 用财务数据动态生成

**VL原文 (P.5):**
> "The analyst uses the commentary to explain the forecast. The commentary is also particularly useful when a trend is shifting, or a change is about to occur."

**🔴 差距:** VL的Analyst Commentary是分析师手写的300-400字深度分析, 包含预测逻辑和投资观点。当前实现仅是PDF关键字提取或数据陈述, 本质上是 "摘要" 而非 "分析"。

---

## 区域 12: Footnotes (脚注)

**VL 原文位置:** 手册 P.10, 样本报告底部 (item 15)

### VL 定义

VL脚注 (item 15) 包含:
- EPS计算方式 (Basic vs Diluted)
- 非经常性项目剔除明细
- 股息支付历史日期
- 财报年结日
- 无形资产明细
- 每股账面价值中的商誉

### A/H 股实现状态

| 内容 | 实现状态 |
|------|---------|
| EPS口径说明 | ❌ |
| 非经常性明细 | ❌ |
| 股息历史日期 | ⚠️ dividend表有日期字段 |
| 财年结束日 | ✅ config.fiscal_yr_end |
| 无形资产/商誉 | ❌ |

**当前实现:** generate_report.py Footer仅显示校验结果和数据来源, 非VL脚注。

---

## 区域 13: Projections Box (预测框)

**VL 原文位置:** 手册 P.7, 样本报告左栏 (item 19)

### VL 定义

```
2020-22 PROJECTIONS
              Price   Gain   Ann'l Total Return
High      135 (+15%)         6%
Low       110  (-5%)         1%
```

**VL公式 (P.7):**
- Target Price = 预估EPS × 预估PE
- Range宽度取决于Safety rank
- Annual Total Return = 价格涨幅 + 股息再投资

### A/H 股实现状态: ❌ 完全未实现

需要3-5年EPS预测和PE预测才能生成。

---

## 区域 14: Target Price Range (目标价区间)

**VL 原文位置:** 显示在图表右上和Projections Box

### VL 公式 (P.7):
> "The range is based on our earnings projection for that period, multiplied by the estimated price/earnings ratio in the Statistical Array. The width of the high-low range depends on the stock's Safety rank."

### A/H 股实现状态: ❌ 完全未实现

---

## 区域 15: Insider/Institutional Decisions

**VL 原文位置:** 样本报告左栏上方

### VL 定义

```
Insider Decisions
          to Buy  to Sell
Jan       0       0
Feb       0       0
...
Options   0       3

Institutional Decisions
          to Buy  to Sell
Q1 '17    93      87
Q2 '17    82      90
...
```

### A/H 股实现状态: ⚠️ 占位符 ("N/A")

A股有高管增减持数据 (巨潮), 港股有披露权益数据 (港交所), 但当前未接入。

---

## 区域 16: Financial Strength / Price Stability 等评级

**VL 原文位置:** 手册 P.4-5, 样本报告右下 (item 14)

### VL 定义

| 指标 | 范围 |
|------|------|
| Financial Strength | A++ ~ C |
| Price Stability | 100 ~ 5 (递增5) |
| Price Growth Persistence | 评级分 |
| Earnings Predictability | 0 ~ 100 |

### A/H 股实现状态: ❌ 完全未实现

---

## 总结: 差距矩阵 (按优先级)

| 优先级 | 区域 | 差距描述 | 价值 |
|--------|------|---------|------|
| **🔴 P0** | Statistical Array | **无预测列** (当前年/次年/3-5年粗斜体) | VL40%价值在此 |
| **🔴 P0** | Quarterly Data | **无预测** (季度粗体预测) | 短期预测参考 |
| **🔴 P0** | Annual Rates | **无Est'd 3-5yr列** | CAGR预测 |
| **🔴 P0** | Analyst Commentary | **无分析师观点**, 仅数据摘要 | VL最受欢迎的区域 |
| **🟡 P1** | Header PE | P/E公式差异 (历史 vs Forward) | 估值锚定 |
| **🟡 P1** | Header Relative PE | 对标错误 (HSI vs VL universe) | 相对估值 |
| **🟡 P1** | RS Line | 对标错误 (HSI vs VL universe) | 相对强弱 |
| **🟡 P1** | Target Price Range | **完全缺失** | 投资决策直接参考 |
| **🟡 P1** | Projections Box | **完全缺失** | 投资总回报预期 |
| **🟡 P1** | Footnotes | **缺失** (EPS口径/非经常性等) | 数据可靠性 |
| **🟢 P2** | Business | 信息密度不足 | 公司认知 |
| **🟢 P2** | Legends | CF Multiple硬编码15.0 | VL是分析师动态选择 |
| **🟢 P2** | Current Position | Debt Due口径偏差 | 流动性分析 |
| **🟢 P3** | Ratings Box | 排名体系完全缺失 | 高价值但极复杂 |
| **🟢 P3** | Insider/Institutional | 占位N/A | A/H有数据源可接入 |
| **🟢 P3** | Fin Strength/Stability | 完全缺失 | 风险评估 |

### 核心洞察

**VL 报告的 40% 价值来自预测 (粗斜体列)，30% 来自分析师点评，30% 来自历史数据。**
当前项目只覆盖了历史数据部分，缺失了预测和分析这两个最核心的价值区域。

**建议还原路径:**
1. 先完成历史数据的准确性 (P0数据缺陷)
2. 再补充预测框架 (P0预测列)
3. 最后实现分析师点评和排名体系

---

## 附录: A股 vs H股数据可及性对照

| 数据需求 | A股(巨潮/同花顺/新浪) | H股(东方财富/港交所/新浪) |
|---------|----------------------|-------------------------|
| 季报数据 | ✅ 一季报/中报/三季报/年报 | ⚠️ 仅年报+中报 (部分公司自愿Q1/Q3) |
| 稀释EPS | ⚠️ THS抽象指标可能提供 | ⚠️ EM接口基本EPS |
| 扣非净利润 | ✅ THS支持扣非 | ⚠️ Non-IFRS需手动获取 |
| 高管增减持 | ✅ 巨潮披露 | ⚠️ 港交所披露权益(SDI) |
| 机构持股 | ✅ 有 | ⚠️ 港交所CCASS |
| 历史年份数 | THS约10-15年 | EM约5-10年 |
| 股息 | ✅ 巨潮分红 | ⚠️ EM大量0值 |
| 货币 | 固定CNY | CNY/HKD混合 |
