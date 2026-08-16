---
topic: 贵州茅台 (600519) — 数据目录
category: 投研-数据目录
created: 2026-08-16
sources:
  - data/600519.db
---

# 贵州茅台 (600519) — 数据目录

> A股 · 白酒龙头。财务数据库 `data/600519.db`，9 表覆盖三大报表 + 指标 + 分红 + 行情 + 营收拆分。

## 一、数据库结构

| 表 | 行数 | 内容 |
|------|:---:|------|
| income | 3044 | 利润表（report_date / item_name / amount / item_code） |
| balance | 4674 | 资产负债表 |
| cashflow | 3631 | 现金流量表 |
| indicators | 1230 | 财务指标（如 sale_net_interest_ratio） |
| dividend | 25 | 分红（cash_dps / special_dps / ex_date / pay_date） |
| kline | 5939 | 行情（date / open / high / low / close / volume / adjust） |
| revenue_structure | 6 | 营收拆分（by_product / by_region / by_channel） |
| meta | 11 | 元数据（code / total_shares / valuation_method 等） |
| spot | 1 | 当前快照（price / pe / pb / div_yield / mkt_cap） |

## 二、关键元数据

| 项 | 值 |
|------|------|
| code | 600519 |
| market | cn |
| 总股本 | 1,250,081,601 股（12.50 亿股） |
| 员工数 | 33,000 |
| 估值方法 | cf（现金流折现，CF=15.0x） |
| 数据抓取 | 2026-06-14 |

## 三、营收拆分（2025 年度，百万元）

### by_product

| 产品 | 金额 | 占比 |
|------|------:|:---:|
| 茅台酒 | 146,499.9 | 86.8% |
| 其他系列酒 | 22,274.7 | 13.2% |

### by_region

| 地区 | 金额 | 占比 |
|------|------:|:---:|
| 国内 | 163,924.4 | 97.1% |
| 国外 | 4,850.1 | 2.9% |

### by_channel

| 渠道 | 金额 | 占比 |
|------|------:|:---:|
| 直销 | 84,543.0 | 50.1% |
| 批发代理 | 84,231.6 | 49.9% |

> 直销占比 2025 年首次过半（50.1%），是本 wiki 渠道改革跟踪的核心锚点，详见 [[operating-metrics]]。

## 四、SQL 查询示例

```sql
-- 营收拆分
SELECT * FROM revenue_structure WHERE year = '2025';

-- 分红历史
SELECT * FROM dividend ORDER BY report_year DESC;
```

## 参见

- [[thesis]] — 投资 Thesis
- [[industry-chain]] — 白酒产业链全景
- [[operating-metrics]] — 渠道改革与价格双轨制
- [[research-reports]] — 券商研报索引
[[research/index.md]]
