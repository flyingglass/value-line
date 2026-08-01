---
module: extract_mda.py
category: 文本挖掘
depends_on: [pdf_downloader.py]
updated: 2026-06-14
---

# extract_mda.py — 管理层讨论提取

## 职责

从年报 PDF 中提取管理层讨论与分析（MD&A）的中文叙事内容，
按 6 类关键词打分分类，质量评分过滤后写入 DB。

**2026-06-14 改造**：放宽质量阈值 + 原始文本兜底 + 年份追踪，覆盖更多年报。

## 流程

```
PDF 年报 → pdfplumber 提取文本
    ↓ _is_narrative() 过滤纯财务数据句（数字比例 > 22%）
    ↓ scoring-based classify_sentences() 6 类关键词打分
    ↓ 质量门：categories ≥ 2 + total ≥ 6 + overview < 85%
    ↓
    ├─ quality=1 → mda_text（按【章节】分段，≥200 chars 即通过）
    └─ 不足 → 保留原始叙事文本（≥3句），quality=0
         ↓ 写入 SQLite meta.mda_text + meta.mda_quality + meta.mda_extracted_year
```

## 质量阈值变化

| 参数 | 旧值 | 新值 |
|------|------|------|
| 最少覆盖类别 | 3 | 2 |
| 最少总句数 | 10 | 6 |
| overview 占比上限 | 70% | 85% |
| 最低字符数 | 300 | 200 |
| 兜底策略 | build_mda_from_data() (需 engine 先产出) | 保留原始叙事文本 |

## 6 类关键词

1. 经营情况 (overview)
2. 产品业务 (product)
3. 渠道市场 (channel)
4. 地区分布 (region)
5. 成本费用 (cost)
6. 研发展望 (outlook)

## 输出

- `meta.mda_text`：结构化 MD&A 文本
- `meta.mda_quality`：质量评分（0 或 1）
- `meta.mda_extracted_year`：提取的 PDF 年份（用于 build.py 检测新鲜度）

## 涉及模块

[[pdf_downloader.py]] — 提供 PDF 文件
[[engine.py]] — 消费 mda_text
[[build.py]] — Step 3 调用

## 相关概念

[[BUSINESS 生成链路]]
[[vl/log.md]] · [[vl/concepts/多源交叉验证.md]]
[[vl/concepts/个股脚本标准.md]] · [[vl/log.md]]
