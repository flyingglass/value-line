---
name: value-line-report
description: >-
  This skill should be used when the user wants to generate, update, or modify
  a Value Line-style investment research single-page report for any stock
  (A-share or HK). It covers the full pipeline: SQLite-driven data fetching from
  AKShare, PDF parsing for revenue structure, engine computation of 23-line
  metrics/CAGR/PE, and HTML generation with the classic 2-column layout.
  Market config in config.py drives all market-specific behavior (HSI/CSI300,
  currency, PE estimates) — no hardcoded market logic.
  Triggers: "生成价值线报告", "Value Line report", "更新报告",
  "generate report for <ticker>", "value line for <stock>".
agent_created: true
---

# Value Line Report Generator

## Overview

Generate a self-contained HTML Value Line-style investment research report.
Project at `C:/LY/Repo/llm/value-line/`. All data flows through SQLite —
market-specific settings driven by config.py MARKET_CONFIG.

## Two-Column Layout

```
┌──────────────┬──────────────────────────────────────┐
│  LEFT 275px  │          CENTER (flex)                 │
├──────────────┼───────────────────────────────────────┤
│ Insider      │ HEADER: Stock Name / Price / PE        │
│ Decisions    │ Timeliness / Safety / Industry         │
│ Institutional├───────────────────────────────────────┤
│ Decisions    │ Yearly High / Low (表格)               │
│ Capital      │ MONTHLY PRICE RANGES (Log Scale)      │
│ Structure    │ Candlestick + CF×15 + RS + %Return    │
│ (2列网格)    ├───────────────────────────────────────┤
│ Current      │ 23-LINE STATISTICAL ARRAY             │
│ Position     │ (9 years × 23 metrics, 含%单位后缀)    │
│ Annual Rates ├───────────────────────────────────────┤
│ Quarterly    │ BUSINESS (中文, 渠道/IP/地区/员工)     │
│ Sales/EPS    ├───────────────────────────────────────┤
│ / Dividends  │ Management Discussion & Analysis      │
│              │ (7板块中文总结, 紧凑排版)              │
└──────────────┴───────────────────────────────────────┘
```

## Data Pipeline

```
fetcher.py  ────→  SQLite (data/{code}.db)  ────→  engine.py  ────→  report_data.json  ────→  generate_report.py  ────→  report.html
insert_revenue.py ──┘                           (computation)          (self-contained JSON)        (2-column HTML)
```

## Key Files

| File | Role |
|------|------|
| `config.py` | Stock definitions, 23-line metric specs, MARKET_CONFIG (market index/PE/currency) |
| `fetcher.py` | Fetch ALL AKShare data → SQLite: spot, K-line, financials (annual+semi-annual), indicators, dividends |
| `engine.py` | Read SQLite → compute metrics, CAGR, semi-annual, position, validation → report_data.json. Shares computed dynamically from OI/PER_OI, not hardcoded. |
| `generate_report.py` | Read report_data.json → self-contained 2-column HTML. Uses meta.index_name for RS line label (not hardcoded HSI). |
| `pdf_downloader.py` | Download annual/semi-annual report PDFs |
| `insert_revenue.py` | Insert revenue structure data from PDF into SQLite |

## Config: MARKET_CONFIG

```python
MARKET_CONFIG = {
    "hk": {"currency": "HKD", "index_name": "HSI", "pe_estimate": {...}},
    "cn": {"currency": "CNY", "index_name": "CSI300", "pe_estimate": {...}},
    "us": {"currency": "USD", "index_name": "SPX", "pe_estimate": {}},
}
```
Adding a new market = adding one dict entry.

## SQLite Schema (data/{code}.db)

```
income       — report_date, item_name, amount, item_code (annual + semi-annual)
balance      — report_date, item_name, amount, item_code
cashflow     — report_date, item_name, amount, item_code
indicators   — report_date, item_name, amount (annual analysis indicators)
dividend     — report_year, cash_dps, special_dps, ex_date, pay_date, total_amount
revenue_structure — code, year, dim_type, dim_name, amount, pct
spot         — current price/PE/PB/etc.
kline        — daily OHLCV
```

## Adding a New Stock

1. Add stock definition to `config.py` STOCKS dict:
```python
"NEW_CODE": {
    "name": "名称", "name_en": "NAME", "market": "hk",  # or "cn" / "us"
    "currency": "CNY", "org_id": "...",
    # "shares": 1234567890  ← 可选fallback, 默认动态计算
}
```
2. Run `python fetcher.py NEW_CODE` — pulls all AKShare data  
3. Run `python engine.py` (update ACTIVE_STOCK) — computes metrics  
4. Manually insert revenue structure into SQLite via `insert_revenue.py`  
5. Run `python generate_report.py` — generates HTML  
6. Preview `report.html`

## Important Item Codes (income table)

| STD_ITEM_CODE | Meaning | Use |
|---------------|---------|-----|
| 004001001 | 营业总收入 | H1 revenue |
| 004025002 | 归母净利润 | H1 net profit |
| 004027002 | 基本每股收益 | H1 EPS |

## Cross-Validation

engine.py automatically checks H1+H2 = Annual for all available years.
Results and data source list shown in report footer.

## Recent Changes (2026-05-27)

- **数据层**
  - 股数: 完全动态化(OI/PER_OI), 去掉所有config硬编码
  - 市场配置: 新增 MARKET_CONFIG, 驱动 index/currency/PE基准
  - PDF元数据: 新增 extract_pdf_metadata.py, business_desc+employee_count→SQLite
  - MD&A: 新增 extract_mda.py, 7板块中文管理层讨论与分析
  - 营收结构: "中国内地"→"中国", 与PDF原文一致

- **样式层**
  - 布局: Business+MDA→中栏堆叠, 左栏仅 Capital/Current Position/Annual Rates/Quarterly
  - Capital Structure: 2列网格布局(参考原版Value Line)
  - 单位: B/¥B→(亿)统一, 动态检测(万亿/亿/万)
  - 移除: Revenue Structure饼图, ★BelowMin, Est 3-5yr TBD列
  - Business: 全中文, 含渠道/IP/地区/员工数
  - MDA: 全中文7板块, 紧凑排版

- **核心文件**
  - engine.py: market参数化, 动态单位检测, _detect_unit()
  - generate_report.py: 布局重排, 中文业务简介, 2列Capital Structure
  - config.py: 新增 MARKET_CONFIG, currency/index/pe_estimate
  - 新增: extract_pdf_metadata.py, extract_mda.py

