# Value Line Report — 样式参考

> 保存时间: 2026-05-28
> 当前标的: 09988.HK (阿里巴巴)
> 文件: generate_report.py → report.html

---

## 一、整体布局

```
┌─────────────────────────────────────────────┐
│ .container (grid: 275px + 1fr)              │
│ ┌──────────┬──────────────────────────────┐ │
│ │ 左栏     │ 中栏                         │ │
│ │ 275px    │ flex:1                       │ │
│ └──────────┴──────────────────────────────┘ │
└─────────────────────────────────────────────┘
```

- 页面宽度: `1280px`, 背景: `#fff`
- 字体: Arial/Helvetica, 基准 `10px`, line-height `1.25`

---

## 二、左栏 (275px)

| 区块 | 样式要点 |
|------|---------|
| `.left-col` | `padding:4px 5px; font-size:9px; border-right:1px solid #000` |
| `.sec-title` | `font-weight:700; font-size:9.5px; border-bottom:1px solid #000` |
| 表格 | `font-size:8.5px; border-collapse:collapse` |
| 对齐 | `.r` = `text-align:right`; `.b` = `font-weight:700` |

区块顺序:
1. Insider Decisions (占位)
2. Institutional Decisions (占位)
3. Business (数据驱动, 中文)
4. Capital Structure (2列网格)
5. Current Position (表格)
6. Annual Rates of Change (动态列: 10yr/5yr/3yr 或 5yr/3yr/1yr)
7. Quarterly Sales / EPS / Divs Paid

### Capital Structure 2列网格

```css
width:50%; display:inline-block; vertical-align:top;
font-size:8px; line-height:1.6
```

每项 flex: `justify-content:space-between`

---

## 三、中栏 (flex:1)

### 3.1 统一表格结构 (table-layout:fixed)

| Row | 内容 | 备注 |
|-----|------|------|
| 1 | Yearly High/Low 标题 | colspan 整行 |
| 2 | High 行 | 每年一列 |
| 3 | Low 行 | 每年一列 |
| 4 | LEGENDS + K线图 | 第一列110px + colspan=yrCount |
| 5 | Year 基准行 | 年份标签, 居中加粗 |
| 6+ | 23-line metrics | 分隔线: order 2,4,6,7,10 之后 |

### 3.2 表格样式

```css
table-layout: fixed; width: 100%; border-collapse: collapse; font-size: 8.5px
```

- 第一列宽: `110px`, `text-align:left; white-space:nowrap`
- 其余列: `text-align:right; border-right:1px solid #ddd; padding:2px 4px`
- 分隔线: `border-bottom:2px solid #000`
- DPS/PAYOUT_RATIO 行高亮: `background:#fffde7`

### 3.3 K线图区域

- 容器: `chart-box` `flex:1; height:150px`
- 左侧 LEGENDS: `width:110px; font-size:7px`
- ECharts 初始化延迟 `300ms`

### 3.4 ECharts 配置

```javascript
grid: {left:0, right:18, top:2, bottom:20}
xAxis: {
  type: 'category', data: dates, boundaryGap: false,
  axisLabel: {
    fontSize: 6.5, color: '#666', fontWeight: 700, margin: 2,
    formatter: v => v && v.endsWith('-01') ? v.slice(0,4) : '',
    interval: 0, showMinLabel: true, showMaxLabel: true
  },
  splitLine: {show: true, lineStyle: {color:'#ccc', width:0.5}},
  axisTick: {show: false}
}
yAxis: [
  {type: 'log', scale: true, axisLabel: {fontSize:6}, position: 'right'},
  {type: 'value', axisLabel: {fontSize:6}, position: 'right'}
]
series: [
  candlestick (红涨绿跌: #ef232a / #14b143),
  15x CF line (dashed, #1976D2),
  RS Stock line (#ef232a, right axis),
  RS Index line (#999, dotted, right axis)
]
```

### 3.5 K线颜色 (中国惯例)

- 涨 (上涨): `#ef232a` (红)
- 跌 (下跌): `#14b143` (绿)

### 3.6 年分隔线

```javascript
dates.forEach(function(d,i) {
  if(d.endsWith('-01')) yearLines.push({xAxis:i, lineStyle:{color:'#ccc',width:1,type:'solid'}});
});
series[0].markLine = {silent:true, animation:false, symbol:'none', data:yearLines, label:{show:false}};
```

### 3.7 年份对齐策略

- 指标表列数 = yearCount (最多10年)
- K线 `colspan=yearCount` 占满
- ECharts xAxis category 数据与指标列一一对应（不足年份需补null占位）
- Year 基准行 (Row 5) 硬编码年份居中显示

---

## 四、底部

- Business (中文, 数据驱动)
- MDA (从SQLite mda_text, 7板块)
- Footer: AKShare + Annual Report 校验汇总

---

## 五、数据单位约定

| 单位 | 显示 | 来源 |
|------|------|------|
| 营收/利润 | `亿` (人民币) | HOLDER_PROFIT, OPERATE_INCOME 等 |
| 每股 | `元` | EPS, BPS, DPS, CFPS 等 |
| 百分比 | `%` | ROE, 毛利率 等 |
| 股数 | `百万股` | Common Stock |
| 股息 | HKD (港股) | 手动补充 |

---

## 六、关键参数

| 参数 | 值 |
|------|-----|
| 页面宽度 | 1280px |
| 左栏宽度 | 275px |
| 第一列宽 | 110px |
| 图表高度 | 150px |
| grid.bottom | 20px |
| 最大年份数 | 10 |
| 季度表最近年数 | 5 |

---

## 七、生成流程

```
config.py → ACTIVE_STOCK
     │
     ▼
fetcher.py → AKShare API → SQLite (data/{code}.db)
     │         + PDF 营收结构提取
     │         + 股息手动补充
     ▼
engine.py  → SQLite → report_data.json
     │         (指标计算、交叉校验、估值定位)
     ▼
generate_report.py → report_data.json → report.html
                      (套用统一样式模板)
```

每次换股票只需改 `config.py` 的 `ACTIVE_STOCK`，重新跑三步。

### 文件清单

| 文件 | 作用 | 是否需修改 |
|------|------|-----------|
| `config.py` | 股票定义、指标列表、市场配置 | 换股票时改 ACTIVE_STOCK |
| `fetcher.py` | 从 AKShare 抓数据 + PDF 解析 | 不改 |
| `engine.py` | 计算 23 行指标 + 季度数据 + 估值 | 不改 |
| `generate_report.py` | 套模板生成单页 HTML | 不改 |
| `.workbuddy/style-reference.md` | 样式参考文档 | 只读 |
