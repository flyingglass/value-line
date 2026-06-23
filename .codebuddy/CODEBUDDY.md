# 投研系统 — 宪法

## 项目
投资研究系统，A/港/美股。AI agent 驱动 ingest ↔ query 循环持续积累投研知识。
VL 单页报告（`build.py` 8 步流水线）是其中一个子功能。

### Wiki 双轨架构
```
research-wiki/
├── raw/         原始资料，只进不改 (共享)
├── wiki/        VL 项目内部文档，按概念/模块/实体组织
└── research/    投研 wiki，按标的/主题组织
```

两个 wiki 通过交叉链接互通，共享 `data/` 数据层。

### 共享数据（AI 可在 ingest/query 中读取）
| 资产 | 位置 | 内容 |
|------|------|------|
| 财务数据库 | `data/<code>.db` | 9 表：三大报表 + 指标 + 分红 + 行情 + 营收拆分 |
| 年报 PDF | `data/pdfs/<code>/` | 500+ PDF 年报/中报/季报 |
| 券商研报 | `ak.stock_research_report_em(symbol)` | 东方财富-个股研报列表（含 PDF 直链 + 盈利预测） |
| 汇率 | `data/fx_rates.db` | HKD/CNY 每日汇率 |
| 标的配置 | `config.py` | 42 只标的的基本信息 |

### 工作流
1. **Ingest**：原文全文 → `raw/` → 读取 → 创建 wiki 页面（不可跳过任何一步）
2. **Query**：从 wiki 提取观点，结合 DB/PDF 数据验证
3. **Wiki**：结果写回，更新 index + log

### VL 流水线（不可修改其流程）
`build.py` → `engine.py` → `report/`。入口、8 步、输出格式、估值方法均不动。

## 🔴 安全（不可违背）
**严禁硬编码任何密钥 / Token / 密码。** 凭证一律 `.env` + `os.getenv()`。
- 写新模块：确认凭证从 `.env` 读
- `git commit` 前：`git diff --staged` 无真实 token
- 发现硬编码：`git filter-branch` 清历史 + force push

> 2026-06-13：`tdx_client.py` 泄露 Bearer Token，已修复。不可再犯。

## 🔴 投研数据（不可违背）
**严禁编造任何数据。** 所有投研输出中的数字必须准确，且注明出处。
- 数据来源优先级：年报 PDF 原文 > `data/<code>.db` > `report_data.json` > IMA 知识库原始资料
- 无出处 = 不可用。标注"未知/待查"优于凭空估算
- 市场份额、行业规模、单价区间等不可从 DB 直接得出的数字，必须引用外部原文
- 引用格式：`（来源：<文件名/API/IMA kb 名称>）`

> 2026-06-19：宇通客车分析中编造市场保有量/份额/单价数据，已纠正。不可再犯。

## 🔴 研报拉取（不可违背）
**券商研报优先从 AKShare 拉取**，数据源为东方财富网-研究报告-个股研报。

- 接口：`ak.stock_research_report_em(symbol)` — 返回研报列表（机构、评级、日期、PDF 直链、盈利预测）
- 禁止手动从东方财富／同花顺网页翻找、手工复制粘贴研报内容
- Ingest 时如需研报原文：先用 AKShare 拉取列表 → 找到目标研报 → 通过 PDF 直链下载 → 存 `raw/` → 提取关键信息写入 wiki
- 研报 PDF 链接格式：`https://pdf.dfcfw.com/pdf/H3_AP<id>.pdf`，可直接 wget/requests 下载

> 2026-06-23：TCL中环 ingest 时手工 web_fetch 百家号/中财网转载的二手摘要，未走 AKShare 研报接口。已验证 AKShare 可拉 113 条完整研报（含 PDF），此后必须走接口。

## 环境
Python `.venv\Scripts\python.exe`，依赖 `requirements.txt`，凭证 `.env`（.gitignore）。
