---
module: config.py
category: 配置中心
lines: 873
updated: 2026-06-09
---

# config.py — 标的管理配置

## 职责

系统配置中心，定义所有股票标的、市场参数、24 行指标、财报分类码。
纯数据文件，被所有其他模块引用。

## 关键结构

| 结构 | 内容 |
|------|------|
| `STOCKS` | 30+ 只股票定义字典（代码 → 元数据） |
| `MARKET_CONFIG` | 3 个市场配置（hk/cn/us）含指数代码、PE 估计 |
| `VL_METRICS` | 24 行指标定义（行号/中文名/英文名/字段/单位/来源表） |
| `HK_PDF_URLS` | 港股年报 PDF 直链（手动维护） |
| `HKEX_CATEGORIES` / `CNINFO_CATEGORIES` | 交易所财报分类码 |
| `ACTIVE_STOCK` | 当前活跃标的（build.py 通过正则替换切换） |

## STOCKS 字段

| 字段 | 必填 | 说明 |
|------|:--:|------|
| name / name_en | ✅ | 中英文名 |
| market | ✅ | hk / cn / us |
| currency | ✅ | CNY / HKD / USD |
| shares | ✅ | 总股本（股数） |
| industry | — | 行业分类 |
| ceo / inc / website | — | 公司元数据 |
| fiscal_yr_end | — | 财年结束月（默认 12-31） |
| valuation_method | — | cf / pb，默认 cf |
| business_desc | — | fallback 业务描述 |
| analyst.commentary | — | fallback 分析师评论（List[str]） |
| pfx | — | 数据前缀（hk/sh/sz/us） |
| org_id | — | 巨潮内部 ID（A 股） |
| hkex_stock_id | — | 港交所 stockId |
| cik | — | SEC CIK（美股） |

## 市场配置

| 市场 | 指数 | PE 估计表 |
|------|------|----------|
| hk | 恒生指数 HSI | 2013-2025（手动维护） |
| cn | 沪深 300 CSI300 | 2013-2025（手动维护） |
| us | 标普 500 SPX | 2013-2025（手动维护） |

## VL_METRICS：24 行指标定义

按 5 组组织（每股 1-6/估值 7-10/利润 11-17/资产 18-20/回报 21-24），每组间以分隔线标记。

每行定义：(行号, 中文名, 英文名, 数据字段, 单位, 来源表)

## 设计决策

- 纯配置，零业务逻辑
- 估值参数不写死在此文件，由 build.py 动态管理（DB meta 表）
- business_desc / analyst.commentary 仅为 fallback，优先 PDF 提取

## 相关模块

[[build.py]] — 读取 ACTIVE_STOCK、STOCKS
[[engine.py]] — 读取 VL_METRICS、MARKET_CONFIG
[[fetcher.py]] — 读取 STOCKS 拉取数据

## 相关概念

[[24 行统计阵列]]
[[VL 估值方法论]]
