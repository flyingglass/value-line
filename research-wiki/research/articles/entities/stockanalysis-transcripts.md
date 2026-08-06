---
topic: 美股业绩会 transcript 数据源
category: 数据源
created: 2026-08-06
updated: 2026-08-06
---

# StockAnalysis.com — 美股 Earnings Call Transcripts

> 数据源实体 · 投研工具

## 基本信息

| 属性 | 内容 |
|------|------|
| 网址 | `stockanalysis.com/stocks/<ticker>/transcripts/` |
| 内容 | 美股上市公司季度业绩电话会议文字记录（transcript） |
| 覆盖 | 美股（NASDAQ + NYSE）主要上市公司 |
| 数据提供 | Quartr（音频 + 文字稿） |
| 费用 | 免费（网页版 transcript 摘要可读，完整逐字稿需 Quartr 授权） |
| 语言 | 英文原文 |

## 页面结构

每个 transcript 页面包含：
- **日期 + 股价**：业绩会当日收盘价及盘后变动
- **发言人列表**：公司管理层（CEO/CFO/IR）+ 提问分析师（机构名）
- **开场陈述**：CEO 战略概述 + CFO 财务数据
- **Q&A 环节**：分析师逐条问答
- **相关文件链接**：Slides PDF、Earnings Release

## 获取完整 transcript 的方法

1. **StockAnalysis 网页**：可读结构化摘要，但完整逐字稿受版权保护（Quartr 授权），不能全文复制
2. **Quartr 平台**：`quartr.com` — 原始数据提供方，有完整音频 + 文字稿
3. **Seeking Alpha**：`seekingalpha.com/symbol/<TICKER>/earnings/transcripts` — 另一个免费 transcript 来源，通常全文可读
4. **The Motley Fool**：`fool.com/earnings-call-transcripts/` — 免费但有时滞后

## 投研用途

- **管理层语气**：通过 Q&A 措辞判断管理层对未来的信心程度（qualitative signal）
- **分析师关注点**：哪些问题被反复追问 → 市场最关心的风险/机会
- **指引变化**：对比多个季度 guidance 的表述变化（"confident" vs "cautious"）
- **客户披露**：大客户名称、合作规模（如 GW 级别部署）往往在业绩会首次披露
- **中文翻译**：可用 AI 翻译成中文阅读，提炼关键信息入库

## 其他 transcript 来源

| 来源 | 特点 |
|------|------|
| Seeking Alpha | 老牌，覆盖全面，全文通常免费可读 |
| The Motley Fool | 免费，编辑整理，偶有滞后 |
| SEC EDGAR (8-K) | 部分公司会在 8-K 中附 transcript，但非强制 |
| 公司 IR 页面 | 部分公司官网提供 replay + transcript |

## 相关链接

- [[../concepts/投研框架-复杂经济学指导手册]] — 投研框架
- [[../../../raw/research/articles/amd-q2-2026-earnings-call]] — AMD Q2 2026 业绩会摘要（raw）
