---
module: engine.py
category: 核心计算引擎
depends_on: [config.py]
lines: ~2500
updated: 2026-06-09
---

# engine.py — 核心计算引擎

## 职责

从 SQLite 读取原始数据，计算全部 Value Line 指标，输出 `report_data.json`。
纯数据驱动，零硬编码。

## 关键功能

### 1. 24 项指标计算

- 每股指标：PER_OI, PER_NETCASH, EPS, DPS, CAPEX_PS, BPS
- 估值指标：TOTAL_SHARES, PE_AVG, PE_RELATIVE, DIV_YIELD
- 利润表：OPERATE_INCOME, GROSS_MARGIN, OP_MARGIN, DEPRECIATION, HOLDER_PROFIT, TAX_EBT, NET_PROFIT_RATIO
- 资产：WORKING_CAPITAL, LT_DEBT, TOTAL_EQUITY
- 回报率：ROIC, ROE, RETAINED_RATIO, PAYOUT_RATIO

### 2. 估值线生成

- CF 线：CF 乘数 × 每股现金流（CNY → HKD 汇率换算）
- PB 线：PB 乘数 × 每股净资产
- 图表渲染用 HKD，数组用 CNY

### 3. 交叉验证（7 项）

AKShare ↔ income ↔ balance ↔ PDF 三源交叉，TOTAL_SHARES 三路径反推。

### 4. BUSINESS & Commentary 生成

- 优先从 `_parse_mda_text()` 解析 PDF 提取的 mda_text
- 失败则 `_build_business_from_data()` + `_build_commentary_from_data()` 自生成
- 自生成从财务数据动态构建（营收/利润/ROE/地域/业务拆分/CAGR/PE）

### 5. 早年回退计算

港股 indicators 仅 2017+ 的 9 年数据。更早年份 engine 自动从 income/balance/cashflow 当面计算：
- 税率：item_code 004012001/004011999
- BPS：总权益 / shares
- shares：share_count → total_shares carry-forward → config fallback

## 数据流

```
SQLite (data/<code>.db) → engine.py
    ↓ 读取 indicators / income / balance / cashflow / dividend / meta
    ↓ 计算 24 项指标 + 估值线 + 验证
    ↓ 生成 BUSINESS + Commentary
    ↓
report_data.json → generate_report.py → HTML
```

## 涉及模块

[[config.py]] — ACTIVE_STOCK、VL_METRICS、MARKET_CONFIG
[[build.py]] — 估值参数写入 DB meta 表 → engine 读取

## 相关概念

[[24 行统计阵列]]
[[VL 估值方法论]]
[[多源交叉验证]]
[[BUSINESS 生成链路]]
[[三市场数据适配]]
