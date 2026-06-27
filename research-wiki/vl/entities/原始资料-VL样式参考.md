---
entity: 原始资料-VL样式参考
type: 外部服务
source: .workbuddy/style-reference.md (已迁移至 raw/vl-reference/)
created: 2026-06-10
---

# VL 报告样式参考

## 概述

generate_report.py 的 HTML 样式规范参考文档，记录布局尺寸、ECharts 配置、颜色约定、数据单位等细节。

## 状态

- **文件**: `raw/vl-reference/style-reference.md`
- **来源**: `.workbuddy/style-reference.md`（已迁移至 raw 层）

## 内容概要

- 整体布局：1280px 宽，左栏 275px + 中栏 flex
- ECharts K 线图配置：candlestick 红涨绿跌，log 轴，年分隔线
- 表格样式：table-layout:fixed，第一列 110px
- 数据单位：营收/利润 → 亿，每股 → 元，百分比 → %
- 生成流程图 + 生成后必查清单

## 关联

- [[数据口径与样式规范]] — 概念页，Header/K 线/24 行数据口径
- [[generate_report.py]] — 核心 HTML 生成模块
