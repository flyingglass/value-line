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
| 15. Footnotes | EPS 调整项明细表，每项一行 |

## BUSINESS 渲染（2026-06-14 重构）

**内容由 `business_commentary.py` 全权控制**，模板不再自动拼接 IP/渠道/地域/产品。

模板仅附加通用信息：折旧率、员工数、CEO、注册地、网站。

## Footnotes 渲染（2026-06-14 重构）

## Footnotes 渲染（2026-06-14 重构）

引擎输出 `{"year": "2025", "adj": "127.8亿", "diff": "0.08", "src": "GS 1.50 FV -1.60"}` 结构化字段。

**布局**：
- 标题 `Footnotes`，字体与 CURRENT POSITION 统一 (10px)
- 年份列 8.5px，数据列 8px
- 每项调整独立一行（政府补贴 / 公允价值变动 / ...），无数据列留空 `—`
- 合计行 `adj.NP` 位于底部，上方黑色实线分隔
- 垂直分割线 `border-right:1px solid #ddd`

**数据规则**：
- 正数无 `+`，负数括号 `(0.08)`，两位小数（百万级）
- diff < 0.005 亿显示 `—`
- diff = 归母NP - VL经常性NP；正数 = 非经常收益，负数 = 非经常损失

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
