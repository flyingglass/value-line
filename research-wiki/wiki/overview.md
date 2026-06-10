---
topic: 项目全景概述
category: 综合
created: 2026-06-09
---

# Value Line — 项目全景概述

## 一句话定义

自动化投资研究报告生成系统，输入股票代码 → 输出一页 VL 标准格式 HTML 报告。

## 覆盖市场

| 市场 | 代码示例 | 数据源 | 财报来源 |
|------|---------|--------|---------|
| A 股 | 600519 (茅台), 002027 (分众) | 同花顺 / 巨潮 | 巨潮资讯网 |
| 港股 | 09992 (泡泡玛特), 00700 (腾讯) | 东方财富 | 港交所披露易 |
| 美股 | NVDA (英伟达) | 东方财富 | SEC EDGAR |

## 8 步流水线

```
build.py --cf 15.0
  │
  ├─ Step 0: config 完整性检查
  ├─ Step 1: fetcher.py → AKShare → SQLite
  ├─ Step 2: pdf_downloader.py → 年报 PDF
  ├─ Step 3: extract_mda.py → 管理层讨论
  ├─ Step 4: scripts/<code>/insert_revenue.py → 营收结构
  ├─ Step 5: config final 切回标的
  ├─ Step 6: engine.py → 计算指标 → report_data.json
  ├─ Step 7: generate_report.py → HTML 报告
  └─ Step 8: 72 项数据完整性验证
```

任何一步失败 = 阻断 = 不生成报告。

## 核心产物

| 产出 | 文件 | 说明 |
|------|------|------|
| SQLite 数据库 | data/<code>.db | 8 张表，全部财务数据 |
| 报告 JSON | report_data.json | engine.py 输出，所有计算指标 |
| VL 单页 HTML | report/<Name>.html | 自包含，含 ECharts K 线图 |
| 阅读报告 | report/<Name>_reading.md | 8 模块深度分析 |
| 索引页 | report/index.html | 所有标的卡片导航 |

## 24 行统计阵列

5 组指标，涵盖每股指标、股本估值、利润表、资产负债、回报率。

详见 [[24 行统计阵列]]

## 估值方法

- **CF 法**：CF 倍数 × 每股现金流 → 消费 / 科技 / 成长股
- **PB 法**：PB 倍数 × 每股净资产 → 银行 / 保险 / 周期股

## 技术栈

Python 3 + AKShare + SQLite + pdfplumber + ECharts (前端) + Jinja2 (模板)

## 关键设计原则

1. **强制完整性**：任何一步失败即阻断，不用 --force 不跳过
2. **多源交叉验证**：AKShare ↔ 原始财报 ↔ PDF 年报，三层校验
3. **估值倍数持久化**：首次确认 → DB meta 表 → 后续自动复用
4. **自包含输出**：HTML 报告内嵌所有 CSS/JS/数据，单文件可离线查看

## 相关概念

- [[24 行统计阵列]]
- [[VL 估值方法论]]
- [[数据源-AKShare]]
- [[开发环境配置]]
- [[李录阅读法融合]]
