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

### 1.5.1 BUSINESS 区域模板 (2026-06-02 — Pop Mart 风格固化)

BUSINESS 区域采用 **4段式** 结构，对标 Pop Mart(09992) 报告：

```
P1: {year}年营收{X}亿元(同比±{g}%)，归母净利润{Y}亿元(同比±{h}%)，
    毛利率{G}%，ROE {R}%。{一句话业务描述，含核心数据(规模/覆盖/触达)}。

P2: 产品：{by_product top3 name+pct}；
    行业：{by_industry top5 name+pct}
    (具体维度取决于 revenue_structure 可用数据: by_product/by_industry/
     by_channel/by_ip/by_region，按优先级全部渲染)

P3: 折旧率{D}%。员工{E}万人（{最新年份}）

P4: 首席执行官：{ceo}。注册地：{inc}。{website}
```

**数据源优先级：**

| 段 | 数据源 | fallback |
|----|--------|---------|
| P1 | `analyst.business` (手写) | config.business_desc |
| P2 | `revenue_structure` 表 | 空 (不显示) |
| P3 | 折旧率: `DEPRECIATION/OPERATE_INCOME`; 员工: `meta.employee_count` | 空 |
| P4 | `meta.ceo/inc/website` (来自 config.STOCKS) | 空 |

**关键约束：**
- P1 不截断 (generate_report.py 中 `bizP.push(desc)` 保留全文，禁用 `substring`)
- P2 支持全部维度: `by_ip/by_channel/by_region/by_product/by_industry`
- CEO/inc/website 在 config.py STOCKS 中配置，engine.py 自动传入 meta

### 1.5.2 AI Commentary 模板 (2026-06-02 — VL 原生叙事风格)

参考 VL 官方手册：*"The analyst discusses recent performance and expectations for the future, explains why the forecast is what it is, and is particularly useful when a change in trend is occurring."*

采用 **3 段叙事体**（总 300-400 字），无分节标题，连续散文：

```
P1: {日期} — {1-2句业绩快照，含同比变化}。{1-2句趋势判断：什么在变、为什么重要}。

P2: {2-3句深度分析：业务变化、竞争格局、财务质地}。
    {估值快照：PE/PB vs 历史中位数对比}。

P3: {催化剂+风险总结}。关注{1-2个未来验证信号}。
```

**关键原则：**
- ❌ 不罗列数据（不是仪表盘，是分析师观点）
- ✅ 解释"为什么"——why the numbers are what they are
- ✅ 指出"什么在变"——trend change is the most valuable insight
- ✅ 结尾给出验证信号——what to watch for next

示例（分众传媒）：
> 2026年6月2日 — 分众传媒2025年营收127.6亿元(+4.1%)，归母净利润29.5亿元(-42.8%)。利润下滑主因2024年一次性投资收益高基数，核心广告业务保持稳健。值得关注的是客户结构正在发生质变：日用消费品广告占比从2021年的42.7%跃升至61.9%，互联网客户从28.5%降至9.2%——收入底盘正从"烧钱换增长的互联网"转向"稳健投放的品牌消费品"，客户质量和抗周期能力大幅提升。
>
> 公司全面拥抱AI：营销智能体"众小智"覆盖创意生成到投放优化全链路，"千楼千面"实现分楼宇精准投放，传统户外广告正升级为"可精准、可归因、可互动、可优化"的数智化营销。毛利率70.5%、ROE 20.2%、负债率仅0.3%，财务质地优秀。当前PE 27.7倍，高于10年中位数19.1倍，但考虑到2025年低基数效应，前瞻估值更具参考意义。
>
> AI降本增效+消费品客户升级+海外拓展构成三重催化剂。关注2026年中报核心广告业务利润增速及AI工具实效数据——这是验证公司"第二增长曲线"叙事的关键节点。

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
