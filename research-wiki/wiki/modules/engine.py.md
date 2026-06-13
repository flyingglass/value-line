---
module: engine.py
category: 核心计算引擎
depends_on: [config.py]
lines: ~2500
updated: 2026-06-13
---

# engine.py — 核心计算引擎

## 职责

从 SQLite 读取原始数据，计算全部 Value Line 指标，输出 `report_data.json`。
纯数据驱动，零硬编码。支持 AKShare + TDX 双数据源。

## 关键功能

### 1. 24 项指标计算 — 双路径 (2026-06-13 改造)

```python
if indicators 表有完整数据 (含 OPERATE_INCOME):
    → 标准路径: 从 indicators 取值, BPS 统一从 balance 计算
else:
    → 回退路径: 从 income/balance/cashflow 当面计算 (TDX 兼容)
```

- 每股指标：PER_OI, PER_NETCASH, EPS, DPS, CAPEX_PS, BPS
- 估值指标：TOTAL_SHARES, PE_AVG, PE_RELATIVE, DIV_YIELD
- 利润表：OPERATE_INCOME, GROSS_MARGIN, OP_MARGIN, DEPRECIATION, HOLDER_PROFIT, TAX_EBT, NET_PROFIT_RATIO
- 资产：WORKING_CAPITAL, LT_DEBT, TOTAL_EQUITY
- 回报率：ROIC, ROE, RETAINED_RATIO, PAYOUT_RATIO

### 2. 回退路径增强 (TDX 兼容)

| 改进 | 说明 |
|------|------|
| item_code + item_name 双重查询 | TDX 无 STD_ITEM_CODE, 回退到中文名查询 |
| EPS 反推加权股数 | `shares = NP / 每股基本盈利` → 年报加权股数 |
| BPS 统一公式 | `balance.总权益 ÷ shares` 替代 `indicators.BPS` 直读 |
| 折旧双源 | cashflow 优先, income.折旧及摊销 兜底 |
| 2017 年截断移除 | TDX 数据可追溯至 2001, 引擎不再限制起始年 |
| 季度/半年数据全链路 | H1/Q1 查询全面加 `or item_name` 回退 |
| 2026 前向季报 | 如有 Q1 数据则自动追加下一年到季度区域 |
| 数据源边界检测 | 自动发现 indicators 可用年份边界, 生成 `data_source_note` |

### 3. 估值线生成

- CF 线：CF 乘数 × 每股现金流
- PB 线：PB 乘数 × 每股净资产

### 4. 交叉验证（7 项）

AKShare ↔ income ↔ balance ↔ PDF 三源交叉，TOTAL_SHARES 三路径反推。

### 5. BUSINESS & Commentary 生成

- 优先从 `_parse_mda_text()` 解析 PDF 提取的 mda_text
- 失败则 `_build_business_from_data()` + `_build_commentary_from_data()` 自生成

### 6. 数据源标记 (report_data.json)

```json
{
  "data_source_note": "2017年起指标基于东方财富...2016年及以前基于TDX...",
  "bps_source": "归属母公司权益 ÷ 股数 (...)",
  "data": { "2017": { "BPS": 29.17, "BPS_FORMULA": "equity/shares" } }
}
```

仅当同时使用 AKShare + TDX 两种数据源时生成 `data_source_note`。

## 数据流

```
SQLite (data/<code>.db) → engine.py
    ↓ 双路径读取 (indicators 或 income/balance/cashflow)
    ↓ 计算 24 项指标 + 估值线 + 验证
    ↓ 动态检测数据源边界
    ↓ 生成 BUSINESS + Commentary
    ↓
report_data.json → generate_report.py → HTML
```

## 涉及模块

[[config.py]] — ACTIVE_STOCK、VL_METRICS、MARKET_CONFIG
[[build.py]] — 估值参数写入 DB meta 表 → engine 读取
[[tdx_client.py]] — TDX 数据写入 income/balance/cashflow

## 相关概念

[[24 行统计阵列]]
[[VL 估值方法论]]
[[多源交叉验证]]
[[BUSINESS 生成链路]]
[[三市场数据适配]]
[[数据源-通达信TDX]]
