---
module: generate_reading.py
category: 深度分析报告
depends_on: [engine.py, config.py]
updated: 2026-06-09
---

# generate_reading.py — 深度阅读报告

## 职责

读取 `report_data.json`，生成深度阅读报告（Markdown + HTML），融合李录投资方法与 VL 分析体系。

## 输出

- `report/reading/<code>.md` — Markdown 阅读报告
- `report/reading/<code>.html` — HTML 阅读报告

## 8 模块内容

| 模块 | 内容 |
|------|------|
| 快速筛查 | 李录式 30 秒判断（PB/ROIC/资产质量） |
| 评级 | Timeliness/Safety/Technical 自动计算 |
| AI Commentary | 5 段业绩归因 + 资金循环 + 业务质地 + 估值锚定 |
| 24 行阵列 | 诊断窗（三层裂缝、ROIC vs ROE、留存四象限） |
| 资本结构 | 债务结构 + 流动比率 |
| 价格图 | 三线解读 + 历史回报 |
| 增长率 | CAGR + 季度趋势 |
| 检查清单 | 李录 5 问 + VL 综合信号 |

## 涉及模块

[[engine.py]] — report_data.json 数据源
[[generate_report.py]] — 互补报告（VL 单页）

## 相关概念

[[李录阅读法融合]]
[[vl/modules/generate_report.py.md]] · [[vl/index.md]]
[[vl/index.md]]
