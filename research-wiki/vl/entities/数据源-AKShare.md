---
entity: 数据源-AKShare
type: 数据源
url: https://github.com/akfamily/akshare
doc: https://github.com/akfamily/akshare/blob/main/docs/data/stock/stock.md
created: 2026-06-09
---

# 数据源：AKShare

## 概述

开源金融数据接口库，本项目主力数据源。所有接口通过 `import akshare as ak` 调用，返回 `pandas.DataFrame`。

## 本项目使用的接口

### 港股 (东方财富 EM)

| 接口 | 用途 | 写入表 |
|------|------|--------|
| `stock_hk_spot_em` | 实时行情快照 | `spot` |
| `stock_hk_daily` | 日K线（前复权 qfq） | `kline` |
| `stock_financial_hk_analysis_indicator_em` | 分析指标（EPS/BPS/ROE） | `indicators` |
| `stock_financial_hk_report_em` | 三大报表（利润/资产/现金） | `income/balance/cashflow` |

### A 股 (同花顺 THS + 巨潮)

| 接口 | 用途 | 写入表 |
|------|------|--------|
| `stock_zh_a_spot_em` | 实时行情 | `spot` |
| `stock_zh_a_hist` | 日K线（qfq 前复权） | `kline` |
| THS 分析指标 | EPS/BPS/ROE 等 | `indicators` |
| THS 财务报告 | 三大报表（长表 EAV 格式） | `income/balance/cashflow` |

### 美股 (东方财富 EM)

| 接口 | 用途 | 写入表 |
|------|------|--------|
| `stock_us_spot_em` | 实时行情 | `spot` |
| `stock_us_hist` | 日K线 | `kline` |
| EM 财报接口 | 三大报表 | `income/balance/cashflow` |

## 关键限制

- **港股 indicators 仅 2017+ 的 9 年数据** — 拟用 TDX MCP 替换（2001-2025），A 股保留 EM
- **A 股 THS 保留** — TDX A 股仅 6 年，不如 THS 15 年
- 频率限制：每分钟/每日有请求上限
- A 股 THS 字段为长表 EAV 格式（item_name + amount），需 `THS_INDICATOR_MAP` 映射
- 港股报表为元单位，A 股报表为万元单位

## 复权方式

`qfq` 前复权（本项目默认）、`hfq` 后复权、`""` 不复权。

## 涉及模块

[[fetcher.py]] — 调用所有 AKShare 接口（港股拟迁出至 [[数据源-通达信TDX]]）
[[engine.py]] — 消费 SQLite 数据，早年回退计算

## 相关概念

[[三市场数据适配]]
[[多源交叉验证]]
[[数据源-通达信TDX]]

## 外部文档

- 完整 API: https://github.com/akfamily/akshare/blob/main/docs/data/stock/stock.md
- 官方仓库: https://github.com/akfamily/akshare
[[vl/index.md]] · [[vl/overview.md]]
[[vl/overview.md]] · [[vl/modules/fetcher.py.md]]
