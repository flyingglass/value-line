# Value Line 报告 — 数据口径 & 样式规范（2026-06-01 终版）

> 复刻目标：美国 Value Line Investment Survey 单页报告格式
> 对标标的：泡泡玛特(09992.HK) / 腾讯(00700.HK)
> 原则：股价 HKD，数据 CNY。HKD 值必标单位。
> **年份标准**：engine 默认 15 年，indicators 不足时自动回退 raw 表计算。

---

## 一、数据口径

### 1.1 Header（顶部栏）

| 指标 | VL 公式 | 我们公式 | 数据源 | POP MART 值 | 状态 |
|------|---------|---------|--------|------------|------|
| Price | 最新收盘价 | `spot.price` | AKShare stock_hk_spot | 173.40 HKD | ✅ |
| P/E RATIO | 价÷(6M实+6M预) | 价÷TTM_EPS(HKD) | `_compute_ttm_eps` | 16.3 | ⚠️缺预测 |
| Trailing P/E | 价÷TTM实EPS | 同PE | — | 16.3 | ✅ |
| Median P/E | 10年PE中位+调整 | IQR(1.5×)中位数 | `_median_pe_iqr` | 44.8 | ⚠️VL调整未公开 |
| RELATIVE P/E | PE÷VL~1700中位 | PE_AVG÷HSI PE | config pe_estimate | 2.36 | ⚠️对标 |
| DIV'D YLD | 预估12M÷价 | DPS_HKD÷price×100 | dividend+fx | 1.52% | ⚠️缺预测 |

### 1.2 Price Chart (K线图)

| 元素 | VL 数据 | 我们数据 | 数据源 | 状态 |
|------|---------|---------|--------|------|
| OHLC月K线 | 月OHLC | 前复权(qfq) HKD | AKShare kline | ✅ |
| Cash Flow线 | 15×CF/Sh (实+虚) | 15×PER_NETCASH÷fx HKD | engine cf_line | ❌缺预测 |
| RS线 | (价/基)÷VL基准 | (价/基)÷(HSI/基)×100 | K线+index_kline | ⚠️对标 |
| Volume% | 月量÷总股本% | 月vol÷TOTAL_SHARES×100 | Kline vol+shares | ✅ |
| Yearly H/L | 年最高/最低 | K线按年聚合 | kline | ✅ |
| % HIST.RETURN | 1/3/5yr含息总回报 | (末价+累息)÷初价 | kline+dividend | ✅ |

### 1.2.1 年份覆盖机制（2026-06-01 固化）

| 场景 | indicators 表 | engine 行为 | 典型年份数 |
|------|--------------|-----------|-----------|
| 港股老股 (腾讯) | 2017-2025 (9年) | 2011-2016 回退 raw 表计算 | 15年 |
| 港股新股 (泡泡玛特) | 2017-2025 (9年) | 全量 9年 (无更早数据) | 9年 |
| A股 | 全量 | 标准路径 | 15年 |

回退计算公式:
- **税率**: `item_code 004012001(税项) / 004011999(除税前利润)`
- **BPS**: `总权益 / shares`
- **shares**: `share_count(rd) → total_shares(carry-forward) → config.STOCKS.shares`
- **DIV_YIELD**: DPS=0 → 0.0 (不分红年份股息率=0%)

### 1.3 Statistical Array (24行)

| # | VL 名称 | VL 公式 | 我们公式 | 2025值 | 单位 | 状态 |
|---|---------|---------|---------|--------|------|------|
| 1 | Revenues per sh | Rev÷Sh | `OPERATE_INCOME/shares` | 27.64 | 元 | ✅ |
| 2 | Cash Flow per sh | (NP+Dep)÷Sh | `(adj_np+dep)/shares` | 10.43 | 元 | ✅ |
| 3 | Earnings per sh | **扣非稀释EPS** | `adj_np/shares` | 9.60 | 元 | ✅ |
| 4 | Div'ds Decl'd | DPS | dividend表 | 2.38 | 元 | ✅ |
| 5 | Cap'l Spending | (Fixed+Acq)÷Sh | `(capex_fixed+mna)/sh` | 0.73 | 元 | ✅ |
| 6 | Book Value per sh | BV÷Sh | BPS(AKShare) | 16.61 | 元 | ✅ |
| 7 | Common Shs | 在外股数 | `oi/psi`(API优先) | 1,341 | Mill. | ✅ |
| 8 | Avg P/E Ratio | AvgPx÷EPS | `avg_px_cny/eps` | 18.9 | 倍 | ✅ |
| 9 | Relative P/E | PE÷MktPE | `PE_AVG/HSI_PE` | 2.36 | 倍 | ⚠️ |
| 10 | Avg Div Yield | DPS÷AvgPx | `dps/avg_px_cny%` | 1.3 | % | ✅ |
| 11 | Revenues(亿) | 总营收 | `OPERATE_INCOME/1e8` | 371.2 | 亿 | ✅ |
| 12 | Gross Margin | GP÷Rev | `(rev-cogs)/rev%` | 72.1 | % | ✅ |
| 13 | Operating Margin | OpInc÷Rev | `op_profit/rev%` | 48.5 | % | ✅ |
| 14 | Depreciation(亿) | Dep+Amort | cashflow | 11.2 | 亿 | ✅ |
| 15 | Net Profit(亿) | 归母净利 | `HOLDER_PROFIT/1e8` | 128.9 | 亿 | ✅ |
| 16 | Income Tax Rate | Tax÷EBT | TAX_EBT | 23.6 | % | ✅ |
| 17 | Net Profit Mgn | NP÷Rev | `adj_np/rev%` | 34.7 | % | ✅ |
| 18 | Working Cap(亿) | CA-CL | `(ca-cl)/1e8` | 177.5 | 亿 | ✅ |
| 19 | LT Debt(亿) | NCL | balance | 22.8 | 亿 | ✅ |
| 20 | Shr. Equity(亿) | Total Eq | `TOTAL_EQUITY/1e8` | 226.5 | 亿 | ✅ |
| 21 | Return on Capital | EBIT÷IC | `ebit/(lt_debt+eq)%` | 68.1 | % | ✅ |
| 22 | Return on Equity | NP÷Eq | ROE(AKShare) | 56.9 | % | ✅ |
| 23 | Retained to Eq | Retained÷ComEq | `retained/com_eq%` | 43.5 | % | ✅ |
| 24 | Payout Ratio | Div÷NP | `div_total/adj_np%` | 24.8 | % | ✅ |

### 1.4 Capital Structure

| 指标 | 公式/源 | 当前值 | 单位 | 状态 |
|------|---------|--------|------|------|
| Total Assets | balance | 321.0 | 亿CNY | ✅ |
| Total Debt | balance | 94.5 | 亿CNY | ✅ |
| LT Debt | NCL+到期 | 22.8+5.9 | 亿CNY | ✅ |
| Interest Coverage | EBIT÷利息 | >25x | — | ✅ |
| LT Debt % | LTD÷TotalCap | 9.1 | % | ✅ |
| Market Cap | price_cny×sh | 2,103.3 | 亿CNY | ✅ |
| Common Stock | API(缓存) | 1,341,043,150 | shs. | ✅ |

### 1.5 其他区域

| 区域 | 数据 | 源 | 状态 |
|------|------|-----|------|
| Current Position | Cash/AR/Inv/AP 3年 | balance | ✅ |
| Annual Rates | per-share CAGR 1/3/5yr | per-share数据 | ✅ |
| Quarterly Rev | 半年度营收 | income+report_em | ✅ |
| Quarterly EPS | 半年度EPS(稀释) | income 004027003 | ✅ |
| Quarterly Div | 半年度股息 | dividend表 | ✅ |
| BUSINESS | 手动维护 | config.business_desc | ✅ → mda override |
| AI Commentary | 手动维护 | config.analyst.commentary | ✅ → mda override |

### 1.5.1 BUSINESS & Commentary 数据源 (2026-06-01)

| 优先级 | 来源 | 适用条件 | 内容 |
|--------|------|---------|------|
| **1** | PDF 年报提取 | quality=1 (分类均衡, ≥300chars) | 叙事性文本 |
| **2** | 财务数据自生成 | quality=0 (默认, 零配置) | 营收/利润/ROE/地域/业务/CAGR/PE |
| **3** | config.py fallback | 前两者均失败 | 手动维护 (可选) |

自生成公式:
- **BUSINESS**: `{year}年营收{X}亿元(+{g}%)。归母净利润{Y}亿元。ROE {R}%。业务: {segments}。`
- **Commentary P1**: 业绩概览 (营收/利润/EPS/毛利率同比)
- **Commentary P2**: 业务结构 + 地域分布
- **Commentary P3**: 财务健康 (ROE/负债率/PE)
- **Commentary P4**: 增长趋势 (CAGR) — 如果有5年数据

### 1.6 汇率转换

| 操作 | 方向 | 公式 | 例 |
|------|------|------|-----|
| EPS→HKD | CNY→HKD | 除fx | 9.61÷0.9032=10.64 |
| BPS→HKD | CNY→HKD | 除fx | 16.61÷0.9032=18.39 |
| DPS→HKD | CNY→HKD | 除fx | 2.38÷0.9032=2.64 |
| price→CNY | HKD→CNY | 乘fx | 173.40×0.9032=156.62 |
| avg_px→CNY | HKD→CNY | 乘fx | 200.86×0.9032=181.41 |
| CF Line→HKD | CNY→HKD | 除fx | 10.43×15÷0.9032=173.21 |
| PE/PB | — | 币种无关 | — |
| 股数 | — | 不涉及 | — |

---

## 二、页面样式

### 2.1 全局

| 属性 | 值 |
|------|-----|
| 字体族 | Arial, Helvetica, sans-serif |
| 基准字号 | body 10px, line-height 1.25 |
| 页面宽度 | 1360px, margin:0 auto |
| 双栏布局 | grid-template: 245px + 1fr |
| 色彩 | 黑 #000, 涨红 #ef232a, 跌绿 #14b143, HKD 蓝 #1976D2 |
| iOS 适配 | `-webkit-text-size-adjust:100%` |
| 页脚 | 8px #666, "股价: HKD | 财报数据: CNY | YYYY-MM-DD" |

### 2.2 Header

| 元素 | 字号 | 粗细 | 对齐 | 间距/边框 |
|------|------|------|------|----------|
| 公司名 | 18px | 700 | left | pad 5px 10px |
| 代码 | 9px | 700 | left | 同上 |
| 标签(RECENT/PE/等) | 9px | 700 | bottom | pad 2px 8px |
| 价格数值 | 18px | 700 | center | rowspan=2, border-right:1px #999 |
| PE/PB/Div 值 | 17px | 700 | center | rowspan=2 |
| 括号(Trailing/Median) | 9px | 700 | top/bottom | pad 2px 8px, border-right:1px #999 |
| 底部线 | — | — | — | border-bottom:2px #000 |

### 2.3 K线图 & 成交量图

| 元素 | 样式 |
|------|------|
| K线高度/类型 | 240px candlestick, 涨红跌绿 |
| Y轴 | type:'log', 刻度种子[1,1.6,2.4,4,6]×10^k |
| 网格 | splitLine #ccc 0.5px |
| 年份标签 | 7px bold #333, x轴 |
| CF Line | 蓝实线 #1976D2 1.2px, symbol:none |
| RS Line | 红虚线 #ef232a 1.2px, symbol:none |
| LEGENDS/Yr 左列 | colgroup 130px (LEGENDS), 40px (Year) |
| LEGENDS 标题 | 10px bold |
| LEGENDS 内容 | 9px |
| % HIST.RETURN 标题 | 10px bold |
| % HIST.RETURN 表 | 9px table |
| 成交量高度 | 50px, margin-top:6px |
| 成交量柱色 | 蓝#1976D2(普通), 紫#7b1fa2(1月), 橙#ff6600(hover) |
| barWidth | 60% |
| Vol网格 | markLine: 顶线3px实线, 中/底线0.5px实线 #000 |
| Vol标签 | 10px bold, DOM+convertToPixel, left:-72px |
| K线裁剪 | kl.filter(>=showYears[0]), 与指标年份对齐 |

### 2.4 Tooltip（统一悬浮框）

```
2024-01 HKD
● POP MART
 open: 156.33  close: 173.40  low: 144.00  high: 181.00
● 15x CF: 173.21
● RS: 240.9
  ● PST: 11.30%
```

- 日期行 `<b>` bold + HKD
- OHLC 各一行, open/close/low/high
- CF/RS 各行带 ECharts marker
- PST 涨红跌绿圆点 + %
- 无 `$` 符号
- 成交量图 tooltip 关闭(show:false)

### 2.5 Statistical Array

| 属性 | 值 |
|------|-----|
| 字号 | 8px, line-height 1.3 |
| 表头 | font-weight:700, border-bottom:1px #000 |
| 分隔线 | border-top:0.5px #999 分组 |
| 数值对齐 | text-align:right |
| 列内边距 | td padding: 1px 4px |
| 第一列宽 | 130px（指标名英文+中文双语） |
| 对齐表第一列 | 130px |
| 年份数 | 最多15年, Y.slice(-15) |
| Q1列 | text-align:left + padding-left:3px |
| 共24行 | #1-6 每股 / #7-10 估值 / #11-17 利润 / #18-20 资产 / #21-24 回报率 |

### 2.6 其他区域

| 区域 | 字号 | 样式 |
|------|------|------|
| Cap Str 标题 | 10px bold | border-bottom:2px #000 |
| Cap Str 表 | 10px | text-align:right |
| Current Position | 10px | 3年对比, right-align |
| Annual Rates | 9px | compact table |
| Quarterly Data | 10px | line-height:1; padding-top:3px |
| Quarterly 标题 | 9.5px bold nowrap | colspan=4 centered, 防换行 |
| BUS/AI标题 | 12px bold / 9px bold | block / inline |
| Commentary 正文 | 9px | text-align:justify; line-height:1.35 |

### 2.7 数据来源标注

| 数据 | 标注 |
|------|------|
| HKD 价格 | 标注 "HKD"（Header / Tooltip 日期行） |
| CNY 数据 | 不标注（页脚统一声明） |
| 仅 AKShare 中报 | 中报数据标记 "仅AKShare" |

---

## 三、变更记录

| 日期 | 变更 |
|------|------|
| 2026-06-01 | 全链路稀释EPS(004027003→adj_np/sh) |
| 2026-06-01 | 总股本东方财富API直取+缓存 |
| 2026-06-01 | TTM EPS优先最新年报 |
| 2026-06-01 | 汇率全面审计:PE/PB币种无关,乘除方向修正 |
| 2026-06-01 | RS VL原生单线 |
| 2026-06-01 | 统一Tooltip(OHLC+CF+RS+PST) |
| 2026-06-01 | AI Commentary动态化(config驱动) |
| 2026-06-01 | HKD值标注单位, CNY移除 |
| 2026-06-01 | iOS适配, LEGENDS/volScale字体, Q1对齐 |
| 2026-05-31 | 初始版本 |
