---
entity: 数据源-通达信TDX
type: 数据源 / 外部服务
url: https://txmcp.tdx.com.cn:3001/txmcp
protocol: MCP streamable-http
created: 2026-06-11
updated: 2026-06-13
---

# 数据源：通达信 TDX MCP

## 概述

通达信官方 MCP 服务，通过 CodeBuddy 自定义连接器接入。提供 A 股 + 港股三大财务报表（利润表/资产负债表/现金流量表），数据深度港股可达 2001 年。

**状态：已接入。** 港股三大表通过 `tdx_client.py` 直连 TDX HTTP API 拉取，替换原 AKShare 东方财富接口。
**指标 (indicators) 与分红仍由 AKShare 负责**，采用 INSERT OR IGNORE 保护历史数据。

## 接入方式

```python
# tdx_client.py — HTTP POST 直连 (非 MCP 代理)
POST http://tdxhub.icfqs.com:7615/TQLEX?Entry=TdxSharePCCW.skef10_hk_cwfx
Body: {"Params": [fixedTag, code]}  # fixedTag: 1=损益表, 2=资产负债表, 3=现金流量表
Header: token=<TDX_TOKEN>
```

## 关键属性

| 属性 | 值 |
|------|-----|
| 市场覆盖 | A 股、港股、美股（有限） |
| 港股深度 | **2001-2026**（25年, ~90期季报） |
| 数据粒度 | 原始财务报表（非预计算指标） |
| 港股货币 | 万元（已由 fetcher 转为元） |
| 字段名 | 英文短名 (TAssets, SHProfit, TurnOver...) |

## 与东方财富(EM)对比

| 维度 | TDX 港股 | EM 港股 |
|------|:---:|:---:|
| 最早年份 | **2001** (25y) | 2017 (9y) |
| 引擎兼容 | item_name 中文映射 | item_code + item_name |
| 替换策略 | **✅ 三大表已替换** | indicators/分红保留 |

## 涉及模块

[[tdx_client.py]] — HTTP 直连封装, 字段映射, 单位转换
[[fetcher.py]] — 调用 tdx_client, 写入 SQLite
[[engine.py]] — 双路径消费 (code or name 双重回退)

## 相关概念

[[三市场数据适配]]
[[数据源-AKShare]]
[[vl/log.md]] · [[vl/index.md]]
[[vl/entities/工具-IMA知识库.md]] · [[vl/index.md]]
