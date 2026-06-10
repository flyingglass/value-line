---
module: generate_index.py
category: 索引导航
depends_on: [config.py]
updated: 2026-06-09
---

# generate_index.py — 索引页生成

## 职责

从 `config.py` 的 STOCKS 字典自动生成 `report/index.html`，按行业分组展示所有标的卡片作为导航门户。

## 输出

`report/index.html` — 所有标的的索引页

## 涉及模块

[[config.py]] — STOCKS 配置

## 相关概念

无
