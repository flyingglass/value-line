# WIKI-SCHEMA.md — 投研 Wiki 配置

> 基于 Andrej Karpathy LLM Wiki 方法论。
> 此文件定义 wiki 的目录结构、页面模板、交叉引用规则、领域分类和工作流。
> LLM 和用户共同维护，随 wiki 演进持续更新。

---

## 目录结构

```
research-wiki/
├── WIKI-SCHEMA.md           # 本文件 — wiki 配置
├── raw/                     # 原始资料（不可变，只进不改）
│   ├── vl/                  # VL 项目内部原始资料
│   │   ├── articles/        # 设计记录、变更日志
│   │   ├── akshare-reference/
│   │   ├── tdx-reference/
│   │   ├── karpathy-reference/
│   │   └── vl-reference/
│   └── research/            # 投研原始资料
│       ├── articles/        # 通用文章（日期前缀命名）
│       └── <code>/          # 按标的归档
├── vl/                      # VL 项目内部 wiki（LLM 维护）
│   ├── index.md             # 内容目录
│   ├── overview.md          # 项目全景概述
│   ├── log.md               # 操作日志（只追加）
│   ├── modules/             # 代码模块页
│   ├── concepts/            # 核心概念页
│   ├── entities/            # 实体页（数据源/工具/原始资料）
│   └── synthesis/           # 综合分析（query 高价值产出）
└── research/                # 投研 wiki（LLM 维护）
    ├── index.md             # 索引（按标的 + 按主题）
    ├── overview.md          # 投研 wiki 概述
    ├── log.md               # 操作日志（只追加）
    ├── <code>/              # 标的目录（页面文件名用中文，见「约定」第 7 条）
    │   ├── 数据目录.md       # 数据目录（原 overview.md）
    │   ├── 投资论点.md       # 投资 Thesis（原 thesis.md）
    │   ├── 产业链.md         # 产业链全景（原 industry-chain.md）
    │   ├── 运营指标.md       # 运营指标（原 operating-metrics.md）
    │   ├── 渠道改革.md       # 渠道改革（可选，拆分自运营指标）
    │   └── 销量与吨价.md     # 销量与吨价（可选）
    └── articles/            # 通用投研文章
        ├── concepts/        # 投资概念与框架
        ├── entities/        # 人物/机构
        ├── papers/          # 论文与参考书目
        └── synthesis/       # 综合分析
```

## 命名空间规则

| 命名空间 | 定位 | LLM 写入权限 | 示例 |
|---------|------|:---:|------|
| `raw/` | 原始资料 | ❌ 只读 | 文章全文、API 文档、PDF 摘要 |
| `vl/` | VL 项目内部文档 | ✅ | 模块、流水线概念、数据源实体 |
| `research/` | 投研知识 | ✅ | 标的分析、投资框架、综合分析 |

`raw/` 只进不改。`vl/` 和 `research/` 通过交叉链接互通，共享 `data/` 数据层。

## 页面格式模板

### 模块页（vl/modules/）

```markdown
---
module: <文件名>
category: 流水线编排
depends_on: [<依赖模块>]
updated: YYYY-MM-DD
---

# <文件名>

## 职责
一句话描述。

## 关键函数
- `main()` — 入口

## 数据流
输入 → 处理 → 输出

## 依赖
- config.py: STOCKS 配置

## 设计决策
原理与权衡。

## 已知问题 / TODO
- [ ] 待改进项
```

### 概念页（vl/concepts/ 或 research/articles/concepts/）

```markdown
---
topic: <概念名称>
category: [估值方法 / 指标定义 / 数据流 / 设计模式 / 投资框架]
created: YYYY-MM-DD
updated: YYYY-MM-DD
sources: [<raw 源文件>]
---

# <概念名称>

## 定义

## 关键要点

## 涉及模块 / 相关概念
[[交叉引用]]

## 笔记
```

### 实体页（vl/entities/ 或 research/articles/entities/）

```markdown
---
entity: <实体名称>
type: [股票标的 / 数据源 / 外部服务 / 人物 / 机构]
created: YYYY-MM-DD
---

# <实体名称>

## 概述

## 关键属性

## 相关模块 / 相关页面
[[交叉引用]]
```

### 综合分析页（vl/synthesis/ 或 research/articles/synthesis/）

```markdown
---
title: <标题>
type: synthesis
created: YYYY-MM-DD
updated: YYYY-MM-DD
sources: [<相关 raw 源>]
tags: [<标签>]
---

# <标题>

## 问题

## 分析

## 结论

## 参见
[[交叉引用]]
```

### 标的页（research/<code>/）

标的各子页面使用与概念页相同的 frontmatter 规范，增加 `stock` 和 `market` 字段。

## 交叉引用规则

1. **格式**: `[[页面名]]`（Obsidian 风格），路径相对于当前目录
2. **跨命名空间**: `[[../vl/concepts/页面名]]` 或 `[[../../vl/concepts/页面名]]`
3. **原始资料**: 使用完整路径 `[[../raw/research/articles/文件名]]`
4. **强制要求**: 每个页面底部必须有 `## 参见` 或 `## 相关页面` 反向链接区块
5. **index.md 必须收录**: 任何新页面必须在对应命名空间的 index.md 中注册

## 日志格式

```markdown
## [YYYY-MM-DD] <操作类型> | <简要描述>

### 摄入内容 / 操作
...

### Wiki 产出 / 页面更新
- 页面1
- 页面2
```

操作类型：`init`, `ingest`, `query`, `fix`, `refactor`, `lint`, `feat`, `add`, `build`, `cleanup`, `security`

## 工作流

### Ingest（摄入）
1. 原文全文 → `raw/` 归档（日期前缀命名：`YYYY-MM-DD-<描述>.md`）
2. LLM 读取 → 与用户讨论关键要点
3. LLM 创建/更新 wiki 页面
4. 更新 index.md + log.md（vl 和 research 各一份）
5. 汇报触及页面清单

### Query（查询）
1. 读 index.md → 定位相关页面
2. 深入阅读 → 结合 DB/PDF 验证
3. 高价值回答 → `vl/synthesis/` 或 `research/articles/synthesis/` 存回
4. 追加 log.md

### Lint（健康检查）
检查项：矛盾、过时声明、孤立页面、断链、缺失概念页、交叉引用缺口、数据缺口。
每次 Lint 追加 log.md。

## 领域分类

### vl/ 概念分类
`估值方法`, `指标定义`, `数据流`, `设计模式`, `约定 / 流程`, `工具`, `方法论`

### research/ 文章分类
`投资框架`, `企业分析`, `行业分析`, `方法论`, `人物访谈`, `论文解读`, `综合研判`

## 约定

1. **语言**: wiki 页面中文编写，代码引用保持英文
2. **frontmatter**: 每个页面 YAML frontmatter 开头
3. **日期格式**: `YYYY-MM-DD`
4. **log.md**: 只追加，不修改历史条目
5. **raw 命名**: 日期前缀 `YYYY-MM-DD-<描述>.md`（允许例外如 `hagstrom_2023_...`）
6. **禁止编造数据**: 所有数据必须有出处，优先级：年报 PDF > DB > report_data.json > 外部来源
7. **页面文件名用中文**: `research/<code>/` 标的目录下的页面文件名一律使用中文（如 `数据目录.md`、`投资论点.md`、`产业链.md`、`券商研报.md`、`运营指标.md`、`渠道改革.md`、`销量与吨价.md`），不使用英文名（overview.md / thesis.md 等）。页面内交叉引用 `[[链接]]` 亦使用中文文件名。
