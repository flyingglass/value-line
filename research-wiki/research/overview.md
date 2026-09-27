---
topic: 投研 wiki 概述
category: 索引
created: 2026-08-01
updated: 2026-08-01
---

# 投研 Wiki — 概述

> 创建：2026-06-27

## 定位

`research/` 是投研 wiki 命名空间，存放所有标的专项分析和通用投研知识。

## 目录结构

```
research/                       （2026-09-27 起按「选股模型」分五类）
├── index.md             投研索引（按标的 + 按主题）
├── overview.md          本概述
├── log.md               操作日志
├── 白马/                标的容器 · 白马股（15 只：腾讯控股/TCL中环/紫金矿业…）
│   └── <code>/          标的（如 泡泡玛特/贵州茅台/腾讯控股…）
│       ├── overview.md      数据目录
│       ├── thesis.md        投资 Thesis
│       ├── industry-chain.md 产业链全景
│       ├── operating-metrics.md 运营指标
│       └── research-reports.md  券商研报索引
├── 消费/                标的容器 · 消费（贵州茅台/安琪酵母/泡泡玛特/时代天使/分众传媒）
│   └── <code>/          同白马标的四件套
├── AI软件/              标的容器 · AI 软件（中航信/柏楚电子/宝信软件）
│   ├── <code>/          同白马标的四件套 + `跟踪.md`
│   └── AI软件名单-*.md   池级名单（索引件）
├── 本地/                专题 · ＝广深（广州/、深圳/、assets/ + 跟踪页）
├── 疯狂的里海/          专题 · 作者案例专题
└── articles/            通用投研文章
    ├── concepts/        投资概念与框架
    ├── entities/        人物/机构
    ├── papers/          论文与参考书目
    └── synthesis/       综合分析
```

> **跟踪页**（本项目主产出物）按标的所属类别就近放置：广深标的 → `本地/` 根；AI 软件标的 → `AI软件/<标的>/跟踪.md`。

## 与 vl/ 的关系

| 命名空间 | 定位 | 示例 |
|---------|------|------|
| `vl/` | VL 项目内部文档 | 模块、概念、实体、synthesis |
| `research/` | 投研知识 | 标的分析、投资框架、大师访谈 |

## 原始资料

所有投研内容都有对应的原始资料存档于 `raw/research/`：
- 标的专项 → `raw/research/<code>/`
- 通用文章 → `raw/research/articles/`
