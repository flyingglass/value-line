---
topic: Wiki 操作手册
category: 约定 / 流程
created: 2026-06-09
updated: 2026-06-13
---

# Wiki 操作手册

Wiki 工作流和页面格式规范。操作流程详见 `CODEBUDDY.md` 中定义的核心流程。

## 核心操作

### 1. Ingest（摄入新资料）

触发条件：
- **新代码变更**：某个 .py 文件被大幅修改或新增
- **新文档**：docs/ 下有新文档或文档更新
- **新标的**：config.py 新增股票，或 scripts/<code>/ 新增脚本
- **新概念**：讨论了新的设计决策、问题排查结论

执行流程：
1. 将相关资料引用记录到 `raw/`
2. 阅读内容，与用户讨论关键要点
3. 在 `vl/modules/` 创建或更新相关模块页
4. 在 `vl/concepts/` 更新或创建相关概念页
5. 在 `vl/entities/` 更新或创建相关实体页
6. 更新 `vl/index.md` 添加新页面索引
7. 追加 `vl/log.md` 记录本次摄入
8. 汇报触及了哪些 Wiki 页面

### 2. Query（对知识库提问）

1. 先读 `vl/index.md` 找到相关页面
2. 深入阅读相关 Wiki 页面
3. 综合回答，引用具体来源
4. 如果回答有持续价值，存回 `vl/synthesis/`
5. 追加 `vl/log.md`

### 3. Lint（健康检查）

1. 扫描所有 Wiki 页面，查找不一致、过时声明、孤立页面
2. 自动修复能修复的问题
3. 报告需要人工判断的问题
4. 追加 `vl/log.md`

## 页面格式规范

### 模块页（vl/modules/）

```markdown
---
module: build.py
category: 流水线编排
depends_on: [config.py, fetcher.py, engine.py, ...]
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

### 概念页（vl/concepts/）

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
[[VL 估值方法论]]

## 笔记
补充信息、边界条件、陷阱。
```

### 实体页（vl/entities/）

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
[[index|模块清单]]

## 历史记录
重要事件或变更。
```

## 约定

1. **语言**：Wiki 页面用中文编写，代码引用保持原始英文
2. **frontmatter**：每个页面以 YAML frontmatter 开头，包含元数据
3. **交叉引用**：使用双方括号 Obsidian 格式的页面链接
4. **log.md 格式**：`## [YYYY-MM-DD] <操作类型> | <简要描述>`
5. **index.md**：按类别（模块/概念/实体/综合分析）组织，每个条目一行摘要
[[vl/index.md]] · [[research/log.md]]
[[research/index.md]] · [[vl/overview.md]]
