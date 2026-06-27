# 投研 Wiki — 概述

> 创建：2026-06-27

## 定位

`research/` 是投研 wiki 命名空间，存放所有标的专项分析和通用投研知识。

## 目录结构

```
research/
├── index.md             投研索引（按标的 + 按主题）
├── overview.md          本概述
├── log.md               操作日志
├── <code>/              标的目录
│   ├── overview.md      数据目录
│   ├── thesis.md        投资 Thesis
│   ├── industry-chain.md 产业链全景
│   ├── operating-metrics.md 运营指标
│   └── research-reports.md  券商研报索引
└── articles/            通用投研文章
    ├── concepts/        投资概念与框架
    ├── entities/        人物/机构
    ├── papers/          论文与参考书目
    └── synthesis/       综合分析
```

## 与 vl/ 的关系

| 命名空间 | 定位 | 示例 |
|---------|------|------|
| `vl/` | VL 项目内部文档 | 模块、概念、实体、synthesis |
| `research/` | 投研知识 | 标的分析、投资框架、大师访谈 |

## 原始资料

所有投研内容都有对应的原始资料存档于 `raw/research/`：
- 标的专项 → `raw/research/<code>/`
- 通用文章 → `raw/research/articles/`
