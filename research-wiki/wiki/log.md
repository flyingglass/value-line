# 操作日志

## [2026-06-09] bootstrap | Wiki 初始化

创建 research-wiki/ 三层架构（Schema + Raw + Wiki），基于 Andrej Karpathy LLM Wiki 方法论。
初始摄入：项目全景概述、模块清单、核心概念索引、关键实体。
触及页面：overview.md, index.md, log.md（共 3 页）。

## [2026-06-09] ingest | docs/ 文档深度摄入

处理全部 docs/ 目录资料（9 MD + 2 PDF 参考文档）。
PDF 为原始参考文档，现有 MD 文件是其加工整理后的正式文档版本。

概念页（7 个）：24 行统计阵列、VL 估值方法论、8 步流水线、多源交叉验证、BUSINESS 生成链路、三市场数据适配、李录阅读法融合。
实体页（2 个）：原始资料-PDF-官方阅读指南2020、原始资料-PDF-产品指南。

## [2026-06-09] ingest | 核心模块逐文件摄入

为 7 个核心 .py 模块创建 Wiki 页面：
- build.py — 832 行，流水线编排 + 估值解析
- config.py — 873 行，标的管理配置 + 24 行指标定义
- engine.py — ~2500 行，核心计算引擎 + 交叉验证 + 早年回退
- fetcher.py — 数据获取，三市场 AKShare API
- pdf_downloader.py — 年报 PDF 下载，多市场适配
- extract_mda.py — MD&A 文本提取，6 类关键词分类
- generate_report.py — VL 单页 HTML，ECharts + 24 行阵列

触及页面：以上 7 个 module 页。
更新：index.md

Wiki 构建完成。共 20 页（1 overview + 7 modules + 9 concepts + 2 entities + 1 index + 1 log）。

## [2026-06-09] ingest | AKShare Stock API 文档

用户分享 AKShare 官方 stock 模块 API 文档。
- raw 层: `akshare-stock-api-ref.md` 记录文档来源
- entities: `数据源-AKShare.md` — 本项目使用接口清单、关键限制、三市场适配
触及页面: 2 页（1 raw ref + 1 entity）
更新: index.md
