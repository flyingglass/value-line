---
module: generate_report.py
category: 前端渲染
depends_on: [engine.py, config.py]
updated: 2026-06-14
---

# generate_report.py — VL 单页 HTML 生成

## 职责

读取 `report_data.json`，生成自包含 VL 标准单页 HTML 报告。
内嵌所有 CSS/JS，单文件可离线查看。

## 渲染内容

| 区域 | 内容 |
|------|------|
| Header | 公司名/代码、PE/PB/股息率、最新股价 |
| K 线图 | ECharts candlestick，对数轴，CF/PB 线 + RS 线 |
| 成交量图 | 月量/流通股百分比 |
| 24 行统计阵列 | 5 组 × 15 年，左侧历史 + 右侧预测 |
| Capital Structure | 资产负债结构 + 市值 |
| Current Position | 3 年流动性对比 |
| Annual Rates | 1/3/5 年 CAGR |
| Quarterly Data | 半年度营收/EPS/股息 |
| BUSINESS | 4 段式（Pop Mart 风格） |
| AI Commentary | 3 段叙事体 |

## 技术栈

- ECharts：K 线图（candlestick）、成交量柱（bar）
- 自包含：CSS/JS 内嵌，无外部依赖
- 字体：Arial, Helvetica, sans-serif
- 色彩：涨红 #ef232a、跌绿 #14b143、HKD 蓝 #1976D2

### K 线 Tooltip 渲染

Hover 时显示：日期 → OHLC → 估值线价格 → RS → PST（月量/流通股%）。

估值线系列名：CF 模式 `"15.0x CF"`，PB 模式 `"0.67*BPS"`。
tooltip 对数价反转条件：`n.indexOf('x CF')>-1 || n.indexOf('*BPS')>-1` → `Math.exp(v).toFixed(2)`。

## BUSINESS 渲染优先级

```
analyst.business (手写) → mda_text 解析 → config.business_desc
```

## 涉及模块

[[engine.py]] — 输出 report_data.json
[[config.py]] — VL_METRICS 定义
[[generate_reading.py]] — 生成阅读报告 Markdown/HTML

## 相关概念

[[BUSINESS 生成链路]]
[[数据口径规范]]
