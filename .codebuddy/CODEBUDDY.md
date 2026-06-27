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
| 券商研报 | `ak.stock_research_report_em(symbol)` | 东方财富-个股研报列表（机构/评级/日期/盈利预测），PDF 不可直链下载 |
| 汇率 | `data/fx_rates.db` | HKD/CNY 每日汇率 |
| 标的配置 | `config.py` | 42 只标的的基本信息 |

### 工作流
1. **Ingest**：原文全文 → `raw/` → 读取 → 创建 wiki 页面（不可跳过任何一步）
2. **Query**：从 wiki 提取观点，结合 DB/PDF 数据验证
3. **Wiki**：结果写回，更新 index + log

### VL 流水线（不可修改其流程）
`build.py` → `engine.py` → `report/`。入口、8 步、输出格式、估值方法均不动。

### 🔴 新增标的必须创建 `business_commentary.py`
每个标的在 `scripts/<code>/` 下**必须**有 `business_commentary.py`，定义 `build()` 函数返回 `{"business": "...", "commentary": ["p1","p2","p3","p4","p5"]}`。
- business：1 段公司概述 + 最新年核心数据
- commentary：5 段 AI 评论（经营分析 / 现金流与资本配置 / 盈利质量与护城河 / 估值分析 / 催化剂）
- 所有数据引用 `metrics`、`revenue_structure`、`cagr`、`spot` 参数，不硬编码
- 不含可比公司 PE 中枢、行业规模等 DB 中不存在的数字，此类数据必须引用年报或外部来源

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
**研报拉取优先级：用户手动传入 > web_search 搜索 > AKShare 列表参考。**

1. **AKShare 拉列表**：`ak.stock_research_report_em(symbol)` → 获取研报列表（机构、评级、日期、盈利预测），**PDF 直链不可直接下载（东方财富反爬），仅作索引参考**
2. **web_search 搜内容**：根据研报标题 + 机构名搜索转载/摘要，web_fetch 获取全文
3. **用户手动传入（最高优先）**：若检测到用户通过对话粘贴研报原文，直接使用，跳过步骤 1-2
4. **禁止**：手动从东方财富/同花顺网页逐条翻找复制；在 PDF 直链下载上反复尝试（已验证不可行）

> 2026-06-23：TCL中环尝试 playwright 下载 PDF 反复失败（反爬 + embed 渲染），此后放弃 PDF 直链下载路线。AKShare 列表 + web_search 转载文章为务实路径。

## 环境
Python `.venv\Scripts\python.exe`，依赖 `requirements.txt`，凭证 `.env`（.gitignore）。
