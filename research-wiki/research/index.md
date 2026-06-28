# 投研索引

> 最后更新：2026-06-28

## 概述

- [[overview]] — 投研 wiki 概述与目录结构

## 按标的

- [[安琪酵母/overview]] — 安琪酵母 · 必需消费 · 数据目录 (revenue_structure 3 维度, FY2025 产品/地区/渠道拆分, CF=15.0x)
- [[安琪酵母/thesis]] — 安琪酵母 · 投资 Thesis
- [[安琪酵母/industry-chain]] — 安琪酵母 · 产业链全景
- [[人福医药/overview]] — 人福医药 · Pharmaceuticals · 数据目录 (6 子公司营收全景 + ROE + 毛利率参考 + 应收账款分析)
- [[泡泡玛特/overview]] — 泡泡玛特 · Consumer · 数据目录 (revenue_structure 表 5 维度)
- [[TCL中环/overview]] — TCL中环 · 光伏 · 数据目录
- [[TCL中环/thesis]] — TCL中环 · 投资 Thesis
- [[TCL中环/industry-chain]] — TCL中环 · 产业链全景
- [[TCL中环/research-reports]] — TCL中环 · 券商研报索引 (民生/国金/国联 5 篇)
- [[润泽科技/overview]] — 润泽科技 · 数据中心/AIDC · 数据目录
- [[润泽科技/operating-metrics]] — 润泽科技 · 运营指标跟踪 (上架率/PUE/电费 2022-2025)

## 按主题 — 文章目录

### 概念 (articles/concepts/)
- [[articles/concepts/arthur-increasing-returns]] — Arthur 收益递增与涌现
- [[articles/concepts/munger-poor-charlie-lecture2]] — 芒格多元思维模型（《穷查理宝典》第二讲 · 七大学科 · 投资检查清单）
- [[articles/concepts/munger-mental-models-analysis]] — 芒格推演与分析（9步投资流程 · 双轨分析 · Lollapalooza）
- [[articles/concepts/投资框架-复杂经济学指导手册]] — 四本著作整合框架（柏基 + 竞争优势 + 三段式估值 + 三周期）
- [[articles/concepts/芒格格栅理论-多学科思维投资框架]] — 🔥 哈格斯特朗《查理·芒格的智慧》全书解读：7 大学科 × 投资模型，格栅思维构建指南

### 实体 (articles/entities/)
- [[articles/entities/seth-klarman-interview]] — Klarman：44年年化20%的企业分析原则

### 论文与参考 (articles/papers/)
- [[articles/papers/投资框架-参考著作]] — 12 项原始资料来源记录

### 综合分析 (articles/synthesis/)
- [[articles/synthesis/popmart-chason-rebuttal]] — 🆕 驳论 — 拆解 Chason 七个论断（3年周期·代际无共鸣·毛绒退烧·The Monster化）
- [[articles/synthesis/popmart-cycle-defense-comparison]] — 外部观点 vs 我们框架 — Chason 该文对比
- [[articles/synthesis/popmart-historical-cycle-defense]] — 泡泡玛特历史周期防御 — 四模式归纳 × 三条防线演绎 × 冗余备份
- [[articles/synthesis/popmart-ip-cycle-defense]] — 泡泡玛特抵御IP/品类周期 — 代际转化的本质
- [[articles/synthesis/popmart-demand-decomposition]] — 泡泡玛特"买不买 vs 买多少" — 三层拆解 × 茅台对称性
- [[articles/synthesis/maotai-drink-logic-analysis]] — 茅台"喝不喝 vs 喝多少" — 归纳演绎法 × 芒格多元模型
- [[articles/synthesis/dahang-weekly-76]] — 大航周报76：2026年第26周

## 共享数据

投研过程中可随时查询以下数据资产：

| 资产 | 位置 | 内容 |
|------|------|------|
| 财务数据库 | `data/<code>.db` | 三大报表、分析指标、分红、行情、营收拆分 (9 表) |
| 年报 PDF | `data/pdfs/<code>/` | 港交所/A股年报/中报/季报原始文件 |
| 汇率 | `data/fx_rates.db` | HKD/CNY 每日汇率 |
| 标的配置 | `config.py` > STOCKS | 53 只标的的基本信息 |

## 工作流

遵循 ingest → query → wiki 循环：

1. **Ingest**：将原始资料全文存入 `raw/research/<code>/` 或 `raw/research/articles/`，再读取后创建 wiki 页面
2. **Query**：从 wiki 页面提取观点，结合 DB/PDF 数据验证或深化
3. **Wiki**：将 query 结果写回 wiki 页面（thesis/moat/risks 等），更新 index.md + log.md

详细规范见 [[Wiki操作手册]]（`vl/concepts/Wiki操作手册.md`）。
