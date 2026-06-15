---
module: fetcher.py
category: 数据获取
depends_on: [config.py, tdx_client.py]
updated: 2026-06-15
---

# fetcher.py — 数据获取

## 职责

从 AKShare API + TDX API 双源拉取股票财务/行情数据，写入 SQLite 数据库。
支持 A 股（同花顺/巨潮）、港股（TDX 三大表 + AKShare 指标/分红）、美股（东方财富+SEC）三市场。

## 拉取内容

| 表 | 内容 | 港股来源 | A股来源 | 美股来源 |
|----|------|---------|--------|--------|
| `spot` | 实时行情快照 | AKShare stock_hk_spot | AKShare stock_zh_a_spot | AKShare stock_us_spot |
| `kline` | 前复权日线 | AKShare stock_hk_daily | AKShare stock_zh_a_daily | AKShare stock_us_daily |
| `income` | 利润表 | **TDX** (2001+) → fallback AKShare | AKShare THS | AKShare EM |
| `balance` | 资产负债表 | **TDX** (2001+) → fallback AKShare | AKShare THS | AKShare EM |
| `cashflow` | 现金流量表 | **TDX** (2001+) → fallback AKShare | AKShare THS | AKShare EM |
| `indicators` | 分析指标 | AKShare (INSERT OR IGNORE) | AKShare THS | AKShare EM |
| `dividend` | 股息数据 | AKShare | AKShare | income 表提取 |

## 港股 TDX 改造 (2026-06-13)

### 三大表：TDX 替换 AKShare
- `tdx_client.py` 直连 TDX HTTP API (Entry: `TdxSharePCCW.skef10_hk_cwfx`)
- 损益表: fixedTag=1, 资产负债表: fixedTag=2, 现金流量表: fixedTag=3
- 字段名映射：TDX 英文 ColName → 引擎期望的中文 item_name
- 单位转换：万元 ×10000 → 元（每股类不乘）
- 失败自动 fallback 原 AKShare 接口

### indicators：保留 AKShare，INSERT OR IGNORE
- 一旦拉取成功，永不覆盖 → 保障历史数据稳定
- 如需强制刷新某年：手动 `DELETE FROM indicators WHERE report_date='年份-12-31'`

## 涉及模块

[[config.py]] — ACTIVE_STOCK、STOCKS
[[tdx_client.py]] — TDX HTTP API 封装
[[build.py]] — Step 1 调用

## 已知问题

**2026-06-15**：末尾打印 `FETCH_OK`（ASCII 标记），因 Windows 子进程输出中文 `"拉取完成"` 可能出现编码乱码，导致 build.py 的 `_run()` 误判为失败。

## 相关概念

[[三市场数据适配]]
[[数据源-AKShare]]
[[数据源-通达信TDX]]
