---
module: fetcher.py
category: 数据获取
depends_on: [config.py]
updated: 2026-06-09
---

# fetcher.py — 数据获取

## 职责

从 AKShare API 拉取股标财务/行情数据，写入 SQLite 数据库。
支持 A 股（同花顺/巨潮）、港股（东方财富）、美股（东方财富+SEC）三市场。

## 拉取内容

| 表 | 内容 | 来源 |
|----|------|------|
| `spot` | 实时行情快照 | stock_hk_spot / stock_zh_a_spot |
| `kline` | 前复权日线 | stock_hk_daily / stock_zh_a_daily |
| `indicators` | 分析指标（EPS/BPS/ROE 等） | analysis_indicator_em |
| `income` | 利润表 | financial_report_em |
| `balance` | 资产负债表 | financial_report_em |
| `cashflow` | 现金流量表 | financial_report_em |
| `dividend` | 股息数据 | dividend |
| `revenue_structure` | 营收结构 | 由 insert_revenue.py 写入 |

## 市场适配

| 市场 | API 前缀 | 字段体系 |
|------|---------|---------|
| 港股 hk | 东方财富 EM | 中文 item_name（营业额/经营溢利等） |
| A 股 cn | 同花顺 THS + 巨潮 | THS 中文 → 英文 map（THS_INDICATOR_MAP） |
| 美股 us | 东方财富 EM | 英文字段名 |

## 港股关键字段映射

| AKShare item_name | VL 用途 |
|-------------------|--------|
| 营业额 | Revenues |
| 销售成本 | COGS |
| 经营溢利 | Operating Profit |
| 股东应占利润 | Net Profit |
| 折旧及摊销 | Depreciation |

## 涉及模块

[[config.py]] — ACTIVE_STOCK、STOCKS
[[build.py]] — Step 1 调用

## 相关概念

[[三市场数据适配]]
