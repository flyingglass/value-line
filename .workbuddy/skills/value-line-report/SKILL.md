---
name: value-line-report
description: >-
  This skill should be used when the user wants to generate, update, or modify
  a Value Line-style investment research single-page report for any stock
  (A-share or HK). It covers the full pipeline: SQLite-driven data fetching from
  AKShare, PDF parsing for revenue structure, engine computation of 23-line
  metrics/CAGR/PE, and HTML generation with the classic 3-column layout.
  Triggers: "生成价值线报告", "Value Line report", "更新报告",
  "generate report for <ticker>", "value line for <stock>".
agent_created: true
---

# Value Line Report Generator

## Overview

Generate a self-contained HTML Value Line-style investment research report.
Project at `C:/LY/Repo/llm/value-line/`. All data flows through SQLite —
no hardcoded values in engine or report generator.

## Three-Column Layout (Classic Value Line Format)

```
┌──────────────┬───────────────────────────┬──────────────┐
│  LEFT 270px  │      CENTER (flex)        │  RIGHT 255px │
├──────────────┼───────────────────────────┼──────────────┤
│ Insider      │ HEADER: Name/Ticker       │ Per Share    │
│ Decisions    │ Price / PE / 52-Wk Range  │  Data        │
│ Institutional│ Timeliness/Safety/Tech    │              │
│ Decisions    │ Beta / Industry           │ Key Ratios   │
│ Business     ├───────────────────────────┤              │
│ Description  │ CHART (Log Scale)         │ Valuation    │
│              │ Candlestick + RS + CF×15  │  Summary     │
│ Capital      │ % Total Return sidebar    │              │
│ Structure    ├───────────────────────────┤              │
│ Current      │ 23-LINE STATISTICAL ARRAY │              │
│ Position     │ (9 years × 23 metrics)   │              │
│ Annual Rates ├───────────────────────────┤              │
│ Quarterly    │ ANALYST COMMENTARY         │              │
│ Sales / EPS  ├───────────────────────────┤              │
│ / Dividends  │ REVENUE STRUCTURE (3 charts)│             │
│              │ Channel / IP / Region      │              │
└──────────────┴───────────────────────────┴──────────────┘
```

## Data Pipeline

```
fetcher.py  ────→  SQLite (data/{code}.db)  ────→  engine.py  ────→  report_data.json  ────→  generate_report.py  ────→  report.html
insert_revenue.py ──┘                           (computation)          (self-contained JSON)        (3-column HTML)
```

## Key Files

| File | Role |
|------|------|
| `config.py` | Stock definitions, 23-line metric specs, AKShare parameters |
| `fetcher.py` | Fetch ALL AKShare data → SQLite: spot, K-line, financials (annual+semi-annual), indicators, dividends |
| `engine.py` | Read SQLite → compute metrics, CAGR, semi-annual, position, validation → report_data.json |
| `generate_report.py` | Read report_data.json → self-contained 3-column HTML |
| `pdf_downloader.py` | Download annual/semi-annual report PDFs |
| `insert_revenue.py` | Insert revenue structure data from PDF into SQLite |

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
    "name": "名称", "name_en": "NAME", "market": "hk",
    "currency": "HKD", "org_id": "...",
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

## Constraints

- HK stocks: no quarterly reports, use H1/H2 instead
- PE_AVG computed from monthly K-line average price ÷ EPS
- PE_RELATIVE = PE_AVG ÷ HSI PE (HSI PE is approximate reference)
- DPS supplemented manually (AKShare HK dividend often returns 0)
- Revenue structure: inserted from PDF → SQLite (no AKShare source for HK)
- Insider/Institutional data: N/A for HK stocks
