---
entity: 数据源-通达信TDX
type: 数据源 / 外部服务
url: https://txmcp.tdx.com.cn:3001/txmcp
protocol: MCP streamable-http
created: 2026-06-11
---

# 数据源：通达信 TDX MCP

## 概述

通达信官方 MCP 服务，通过 CodeBuddy 自定义连接器接入。提供 A 股 + 港股三大财务报表（利润表/资产负债表/现金流量表），数据深度港股可达 2001 年。

**无需 API Key**（当前阶段开放），通过 OAuth 2.0 Bearer Token 认证。

## 关键属性

| 属性 | 值 |
|------|-----|
| 市场覆盖 | A 股、港股、美股（有限） |
| 港股深度 | **2001-2026**（90期季报） |
| A 股深度 | 2020-2026（25期季报） |
| 数据粒度 | 原始财务报表（非预计算指标） |
| 港股货币 | 万元（人民币/港币/美元） |
| A 股货币 | 元（人民币） |

## 接入配置

```json
// ~/.codebuddy/mcp.json
"tdx-connector": {
  "type": "streamable-http",
  "url": "https://txmcp.tdx.com.cn:3001/txmcp",
  "timeout": 30000,
  "headers": {
    "Authorization": "Bearer <TDX_TOKEN>"
  }
}
```

Token 存储在项目 `.env` 的 `TDX_TOKEN` + `TDX_REFRESH_TOKEN`。

## 关键工具

| 工具 | 用途 |
|------|------|
| `tdx_api_data` | 调用内部财务接口（利润表/资产负债表/现金流量表） |
| `tdx_lookup_stock` | 按中文名查代码 |
| `tdx_kline` | K线数据 |
| `tdx_quotes` | 实时行情 |
| `tdx_indicator_select` | A股最新指标快照 |

## 与东方财富(EM)对比

| 维度 | TDX 港股 | EM 港股 | TDX A股 | EM A股 |
|------|:---:|:---:|:---:|:---:|
| 最早年份 | **2001** (25y) | 2017 (9y) | 2020 (6y) | **2011** (15y) |
| 数据一致性 | 0.0% 偏差 | - | 0.0% 偏差 | - |
| 替换策略 | **✅ 全替换** | 被替换 | ❌ 保留EM | **保留** |

## 涉及模块

[[fetcher.py]] — 拟接入 TDX 替换港股 EM 数据拉取
[[engine.py]] — 消费原始报表数据计算 24 项指标

## 相关概念

[[三市场数据适配]]
[[数据源-AKShare]]

## 参考文档

- raw/tdx-reference/tdx-mcp-api.md — 完整数据字典
