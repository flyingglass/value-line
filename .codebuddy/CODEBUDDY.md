# 投研系统 — 宪法

## 项目
投资研究系统，A/港/美股。AI agent 驱动 ingest ↔ query 循环持续积累投研知识。
VL 单页报告（`build.py` 8 步流水线）是其中一个子功能。

### Wiki 双轨架构
```
research-wiki/
├── raw/                       原始资料，只进不改
│   ├── vl/                    VL 项目内部
│   │   ├── articles/          VL 项目通用文章
│   │   ├── akshare-reference/ 数据源参考
│   │   ├── tdx-reference/
│   │   ├── karpathy-reference/
│   │   └── vl-reference/
│   └── research/              投研原始资料
│       ├── articles/          通用文章
│       └── <code>/            按标的的原始资料
├── vl/                      VL 项目内部 wiki
│   ├── index.md              索引
│   ├── overview.md           概述
│   ├── log.md                操作日志
│   ├── concepts/             核心概念
│   ├── modules/              代码模块
│   └── entities/             实体（数据源/工具）
└── research/                  投研 wiki
    ├── index.md              索引（按标的 + 按主题）
    ├── overview.md           概述
    ├── log.md                操作日志
    ├── <code>/               标的目录
    │   ├── overview.md       数据目录
    │   ├── thesis.md         投资 Thesis
    │   ├── industry-chain.md 产业链全景
    │   ├── operating-metrics.md 运营指标
    │   └── research-reports.md  券商研报索引
    └── articles/             通用投研文章（与 vl/ 同构）
        ├── concepts/         投资概念与框架
        ├── entities/         人物/机构
        ├── papers/           论文与参考书目
        └── synthesis/        综合分析
```

### 🔴 命名空间规则

**vl/** — VL 项目内部文档：
- 模块代码、流水线概念、数据源实体等
- 结构与 `research/` 并行，两者交叉链接互通

**research/** — 投研 wiki：
- 标的专项 → `research/<code>/`（overview / thesis / industry-chain 等）
- 通用知识 → `research/articles/concepts|entities|papers|synthesis/`
- 必须有 `index.md`、`overview.md`、`log.md`

**raw/** — 原始资料，只进不改：
- VL 项目相关 → `raw/vl/articles/`
- 投研通用话题/文章 → `raw/research/articles/`
- 标的专项 → `raw/research/<code>/`
- 数据源/工具参考 → `raw/vl/<source>-reference/`

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

## 🔴 入库规范（不可违背）
**raw/ 入库必须保留来源链接。** 原始资料标注了来源（微信公众号 / 网页 / PDF / 播客等）的，链接必须一并保存到 raw 文件头部元数据，格式 `> 原文链接：<url>`。
- 禁止只记来源名称不记链接（如"微信公众号「XX」"但无 `mp.weixin.qq.com/s/...` URL）
- Ingest 时原始资料自带链接 → 完整保留，不得丢弃
- 缺失 → 主动向用户索要或 web_search 搜索补齐；确实找不到则标注"原文链接待补"
- 转载链接（雪球/虎扑等）可作过渡，找到公众号原文后替换

> 2026-08-20：《本汤普森_2026_BenThompson播客-AI融资与科技巨头护城河.md》只有来源名「我有充足的时间」无链接，已列为规范，不可再犯。

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

## 🔴 AI 行为准则（不可违背）
**AI 辅助投研对话中，严禁编造任何信息。**
- **严禁编造名人引语**：任何带引号的芒格/巴菲特/其他人物的引语，必须先查证，查不到出处就说"未找到出处"。不得为了论证效果而编造。
- **不确定的就说不知道**：不为了解释的完整性而填充自己不确定的内容。区分"有证据的"和"推测的"，标注清楚。
- **禁止先画靶再找证据**：不做 presentation，做研究。论证链条断了就承认断了，不强行凑齐。
- **概念区分要准确**：不同物种（三丽鸥模式 vs 日本动漫模式）不可混为一谈。混淆概念比不知道更危险。

> 2026-08-04：对话中多次编造芒格引语、混淆三丽鸥与日本动漫模式、编造"汉字培养视觉模因敏感度"假说。此后加入 AI 行为准则，不可再犯。

## 环境
Python `.venv\Scripts\python.exe`，依赖 `requirements.txt`，凭证 `.env`（.gitignore）。
