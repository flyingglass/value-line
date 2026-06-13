# Value Line 项目 Wiki Schema

> 本文档是 Wiki 的操作手册，每次对话自动加载。
> 规定了 Wiki 结构、约定和工作流。随使用共同演化。

## 项目身份

**Value Line** 是一个自动化投资研究报告生成系统。输入股票代码和估值倍数，
自动拉取财务数据 → 下载年报 PDF → 提取管理层讨论 → 计算 24 项核心指标 → 生成自包含 HTML 报告。

复刻美国 Value Line Investment Survey (1931-) 的单页报告格式，覆盖 **A 股 / 港股 / 美股** 三个市场。

核心流水线 (build.py 8 步)：
1. fetcher.py → AKShare → SQLite
2. pdf_downloader.py → 年报 PDF
3. extract_mda.py → PDF→管理层讨论文本
4. scripts/<code>/insert_revenue.py → 营收结构入库
5. config final 切换标的
6. engine.py → 计算 24 项指标 → report_data.json
7. generate_report.py → 生成 HTML 报告
8. 72 项数据完整性验证

## Wiki 目录结构

```
research-wiki/
├── raw/                   # 原始资料（不可变，只进不改）
│   └── docs/              # 项目 docs/ 中的文档参考
├── wiki/                  # LLM 维护的 Wiki（你只读不写）
│   ├── index.md           # 内容目录（每个页面 + 一行摘要）
│   ├── log.md             # 操作日志（只追加）
│   ├── overview.md        # 项目全景概述
│   ├── modules/           # 代码模块页（每个 .py 文件一篇）
│   ├── concepts/          # 核心概念页（估值方法、指标定义、设计决策）
│   ├── entities/          # 实体页（股票标的、数据源、外部依赖）
│   └── synthesis/         # 综合分析（Query 产物存回）
└── assets/                # 图片、图表附件
```

Schema 本文件位于 `.codebuddy/rules`，每次对话自动加载，无需手动触发。

### 软件项目 vs 学术研究的适配

- `modules/` 替代 `papers/` — 每个核心 .py 文件一篇模块页
- `entities/` — 股票标的、数据源（AKShare、港交所、SEC）
- `concepts/` — 估值方法、24 行指标、交叉验证逻辑、设计权衡
- `synthesis/` — 调试记录、问题排查、重构决策分析

## 核心操作

### 1. Ingest（摄入新资料）

当用户提到以下情况时触发：
- **新代码变更**：某个 .py 文件被大幅修改或新增
- **新文档**：docs/ 下有新文档或文档更新
- **新标的**：config.py 新增股票，或 scripts/<code>/ 新增脚本
- **新概念**：讨论了新的设计决策、问题排查结论
- **外部资料**：用户分享研究文章、估值方法论参考

**执行流程**：
1. 将相关资料引用记录到 `raw/`
2. 阅读内容，与用户讨论关键要点
3. 在 `wiki/modules/` 创建或更新相关模块页
4. 在 `wiki/concepts/` 更新或创建相关概念页
5. 在 `wiki/entities/` 更新或创建相关实体页
6. 更新 `wiki/index.md` 添加新页面索引
7. 追加 `wiki/log.md` 记录本次摄入
8. 汇报触及了哪些 Wiki 页面

### 2. Query（对知识库提问）

当用户询问项目相关问题：
1. 先读 `wiki/index.md` 找到相关页面
2. 深入阅读相关 Wiki 页面
3. 综合回答，引用具体来源
4. 如果回答有持续价值，存回 `wiki/synthesis/`
5. 追加 `wiki/log.md`

### 3. Lint（健康检查）

定期或用户要求时：
1. 扫描所有 Wiki 页面，查找不一致、过时声明、孤立页面
2. 自动修复能修复的问题
3. 报告需要人工判断的问题
4. 追加 `wiki/log.md`

## 页面格式规范

### 模块页（wiki/modules/）

```markdown
---
module: build.py
category: 流水线编排
depends_on: [config.py, fetcher.py, engine.py, pdf_downloader.py, extract_mda.py, generate_report.py]
updated: 2026-06-09
---

## 职责
一句话描述这个模块做什么。

## 关键函数
- `main()` — 8 步流水线入口

## 数据流
输入 → 处理 → 输出

## 依赖
- config.py: STOCKS 配置

## 设计决策
为什么这样设计。

## 已知问题 / TODO
- [ ] 待改进项
```

### 概念页（wiki/concepts/）

```markdown
---
topic: 概念名称
category: [估值方法 / 指标定义 / 数据流 / 设计模式]
created: 2026-06-09
---

## 定义
这个概念是什么。

## 关键要点
- 要点 1

## 涉及模块
[[build.py]]

## 相关概念
[[CF 估值法]]

## 笔记
补充信息、边界条件、陷阱。
```

### 实体页（wiki/entities/）

```markdown
---
entity: 实体名称
type: [股票标的 / 数据源 / 外部服务]
created: 2026-06-09
---

## 概述
这个实体是什么。

## 关键属性
（股票：代码/市场/行业/估值方法；数据源：API/覆盖范围/限制）

## 相关模块
[[相关模块]]

## 历史记录
重要事件或变更。
```

## 🔴 安全红线（宪法级，不可违背）

**源码中严禁硬编码任何密钥 / Token / 密码 / API Key。**

- 所有敏感凭证必须通过 `.env` 文件 + `os.getenv()` 读取
- `.env` 在 `.gitignore` 中，已有模板 `.env.example`（值为 `xxx` 占位）
- 写新模块前必须检查：是否有硬编码凭证？→ 一律从 `.env` 读
- Git commit 前自查：`git diff --staged` 中不得出现真实 token
- 一旦发现硬编码 token，立即修复 + `git filter-branch` 清理历史 + force push

> 2026-06-13 事故：`tdx_client.py` 第 23 行硬编码 Bearer Token 被 GitHub 扫描告警。
> 已通过 filter-branch 重写 13 个 commit + force push 修复。不可再犯。

## 约定

1. **语言**：Wiki 页面用中文编写，代码引用保持原始英文
2. **文件链接**：使用 Markdown 标准链接 `[文件名](路径)`，相对于 wiki/ 目录
3. **frontmatter**：每个页面以 YAML frontmatter 开头，包含元数据
4. **交叉引用**：大量使用 `[[页面名]]` 风格的内部链接
5. **log.md 格式**：`## [YYYY-MM-DD] <操作类型> | <简要描述>`
6. **index.md**：按类别（模块/概念/实体/综合分析）组织，每个条目一行摘要

## 为什么这个 Wiki 存在

Value Line 是一个复杂的系统——8 步流水线、30+ 股票标的、3 个市场、24 项指标、
多源交叉验证、估值方法选择、PDF 解析、HTML 渲染。

传统做法：代码注释 + docs/ 文档 + 聊天记录。问题是代码注释过时后没人更新、
文档和代码脱节、聊天记录随对话消失。

Karpathy Wiki 的答案：LLM 维护一个持久化知识层——交叉引用自动保持、矛盾被标记、
摘要反映全部已知信息。

> 人的工作：写代码、做决策、提出好问题。
> LLM 的工作：文档、交叉引用、簿记、一致性维护。

## 参考

- Andrej Karpathy 原始 gist: https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
