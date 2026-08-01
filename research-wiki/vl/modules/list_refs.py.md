---
module: list_refs.py
category: 只读工具
depends_on: [config.py]
updated: 2026-06-09
---

# list_refs.py — 历史估值参考

## 职责

只读工具，批量列出所有股票的 PE/PB 历史均值，辅助估值决策。不修改任何数据。

## 输出

控制台输出各标的的历史 PE/PB 参考值。

## 涉及模块

[[config.py]] — STOCKS 配置

## 相关概念

[[VL 估值方法论]]
[[vl/index.md]]
[[vl/index.md]]
