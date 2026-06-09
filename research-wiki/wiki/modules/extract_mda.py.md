---
module: extract_mda.py
category: 文本挖掘
depends_on: [pdf_downloader.py]
updated: 2026-06-09
---

# extract_mda.py — 管理层讨论提取

## 职责

从年报 PDF 中提取管理层讨论与分析（MD&A）的中文叙事内容，
按 6 类关键词打分分类，质量评分过滤后写入 DB。

## 流程

```
PDF 年报 → pdfplumber 提取文本
    ↓ _is_narrative() 过滤纯财务数据句（数字比例 > 50%）
    ↓ scoring-based classify_sentences() 6 类关键词打分
    ↓ 质量门：categories ≥ 3 + total ≥ 10 + overview < 70% + ≥ 300 chars
    ↓
    ├─ quality=1 → mda_text（按【章节】分段）
    └─ quality=0 → build_mda_from_data()（财务数据动态生成）
         ↓ 写入 SQLite meta.mda_text + meta.mda_quality
```

## 6 类关键词

1. 经营情况 (business/operation)
2. 产品业务 (product/business)
3. 渠道市场 (channel/market)
4. 地区分布 (region/geography)
5. 成本费用 (cost/expense)
6. 研发展望 (R&D/outlook)

## 输出

- `meta.mda_text`：结构化 MD&A 文本
- `meta.mda_quality`：质量评分（0 或 1）
- engine.py 读取：quality=1 时 `_parse_mda_text()` 解析为 BUSINESS/Commentary

## 涉及模块

[[pdf_downloader.py]] — 提供 PDF 文件
[[engine.py]] — 消费 mda_text
[[build.py]] — Step 3 调用

## 相关概念

[[BUSINESS 生成链路]]
