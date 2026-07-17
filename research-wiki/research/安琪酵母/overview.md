---
topic: 安琪酵母 (600298)
category: 投研-数据目录
created: 2026-06-23
updated: 2026-06-23
sources:
  - report/reading/600298.md
  - scripts/600298/insert_revenue.py
  - scripts/600298/business_commentary.py
  - report_data.json
---

# 600298 安琪酵母 — 数据目录

## DB 表

数据库文件: `data/600298.db`，共 9 张表（定义见 `fetcher.py:_init_tables`）。

## `revenue_structure` 表

| 列 | 类型 | 说明 |
|----|------|------|
| code | TEXT (PK) | 股票代码 |
| year | TEXT (PK) | 财年 |
| dim_type | TEXT (PK) | 拆分维度 |
| dim_name | TEXT (PK) | 维度下的条目名 |
| amount | REAL | 金额（百万元） |
| pct | REAL | 占比（%） |

**联合主键 = (code, year, dim_type, dim_name)**

### 已存在的维度

| dim_type | 条数 | 年份 | 说明 |
|----------|------|------|------|
| by_product | 5 | 2025 | 产品拆分（酵母/食品原料/制糖/包装/其他） |
| by_region | 2 | 2025 | 地区拆分（国内/国外） |
| by_channel | 2 | 2025 | 渠道拆分（线上/线下） |

### 查询示例

```sql
-- 查 2025 年全产品拆分
SELECT dim_name, amount, pct
FROM revenue_structure
WHERE code = '600298' AND year = '2025' AND dim_type = 'by_product'
ORDER BY amount DESC;

-- 查地区毛利率（需结合年报原文）
SELECT dim_name, amount, pct
FROM revenue_structure
WHERE code = '600298' AND year = '2025' AND dim_type = 'by_region';
```

### 产品结构速查 FY2025

| 产品线 | 营收（百万元） | 占比 |
|--------|:---------:|:----:|
| 酵母及深加工产品 | 11,949 | 71.4% |
| 食品原料 | 2,218 | 13.3% |
| 制糖 | 1,339 | 8.0% |
| 其他（营养健康等） | 789 | 4.7% |
| 包装 | 360 | 2.2% |
| **合计** | **16,655** | **100%** |

> 来源：2025年年报 → `scripts/600298/insert_revenue.py` 手动录入

### 地域分布 FY2025

| 地区 | 营收（百万元） | 占比 | 毛利率 |
|------|:---------:|:----:|:----:|
| 国内 | 9,805 | 58.6% | 19.7% |
| 国外 | 6,848 | 40.9% | 32.1% |

> 海外毛利率 32.1% vs 国内 19.7%，全球化布局成效显著。
> 毛利率数据来源：`scripts/600298/business_commentary.py`（硬编码，原始出处为年报分地区毛利率表）

## 核心财务 FY2025

| 指标 | 数值 | 同比 | 来源 |
|------|------|------|------|
| 总营收 | 167.3 亿 | +10.1% | AKShare → indicators 表 |
| 归母净利润（扣非） | 13.6 亿 | +16.3% | AKShare → indicators 表 |
| 毛利率 | 24.7% | +1.2pp | AKShare → indicators 表 |
| ROE | 10.5% | +0.2pp | AKShare → indicators 表 |
| ROIC | 13.7% | +1.2pp | AKShare → indicators 表 |
| 每股收益 | 1.57 元 | +16.3% | AKShare → indicators 表 |
| 每股现金流 | 2.61 元 | +13.5% | AKShare → indicators 表 |
| 每股账面价值 | 14.86 元 | +13.8% | 计算：权益/股数 |
| 资产负债率 | 49.3% | — | AKShare → indicators 表 |

### 毛利率趋势 2017-2025

| 2017 | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 |
|:----:|:----:|:----:|:----:|:----:|:----:|:----:|:----:|:----:|
| 37.6% | 36.3% | 35.0% | 34.0% | 27.3% | 24.8% | 24.2% | 23.5% | **24.7%** |

> 2021 年毛利率断崖式下跌（糖蜜暴涨），2025 年首次企稳回升。

## 年报 PDF

92 个 PDF 文件存放于 `data/pdfs/600298/`（2014-2026 年报/半年报/季报）。

## 估值

VL 报告采用 **CF=15.0x**（必需消费股），PB 备用 1.0x。见 `report/安琪酵母.html`。

## 数据来源汇总

| 数据类型 | 一级来源 | 二级来源 |
|---------|---------|---------|
| 财务指标 | AKShare `stock_financial_abstract_new_ths`（同花顺） | engine.py 交叉验证 |
| 三大报表 | AKShare 同花顺 `benefit/debt/cash_ths` | engine.py 内部一致性 |
| 营收结构 | **年报 PDF 手动录入** | `insert_revenue.py` |
| MD&A | 年报 PDF (pdfplumber 自动) | meta.mda_text |
| 行情估值 | AKShare 东方财富 + 新浪 | K 线 + 财报联合计算 |
| 竞争格局/产能 | 年报 + 研报 → `business_commentary.py` | 硬编码（非自动更新） |
| 分红 | AKShare `stock_dividend_cninfo`（巨潮） | dividend 表 |

## 相关页面

- [[安琪酵母/industry-chain]] — 产业链全景
- [[安琪酵母/thesis]] — 投资 Thesis
