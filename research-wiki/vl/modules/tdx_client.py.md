---
module: tdx_client.py
category: 数据获取
depends_on: []
updated: 2026-06-13
---

# tdx_client.py — TDX HTTP API 客户端

## 职责

HTTP 直连通达信 TDX 后端（非 MCP 代理），拉取港股三大财报，返回标准行列表供 `fetcher.py` 写入 SQLite。

## 关键函数

- `fetch_hk_income(code)` → income 表行列表
- `fetch_hk_balance(code)` → balance 表行列表 (含自动计算 `总权益`)
- `fetch_hk_cashflow(code)` → cashflow 表行列表

## API 格式

```
POST http://tdxhub.icfqs.com:7615/TQLEX?Entry=TdxSharePCCW.skef10_hk_cwfx
Body: {"Params": ["1", "00700"]}
Header: token=Bearer <TDX_TOKEN>
```

## 字段映射

TDX 返回英文短名 (`TurnOver`, `SHProfit`, `TAssets` 等)，`_transform_rows()` 映射到引擎期望的中文名 (`营业额`, `股东应占溢利` 等)。

## 单位处理

- 金额类: TDX 万元 ×10000 → 元
- 每股类 (EPSBasic/EPSDiluted): 已是元，不转换

## 涉及模块

[[fetcher.py]] — 调用 fetch_hk_income/balance/cashflow

## 相关概念

[[数据源-通达信TDX]]
[[vl/log.md]] · [[vl/index.md]]
[[vl/log.md]] · [[vl/modules/engine.py.md]]
