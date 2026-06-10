# 操作日志

## [2026-06-09] bootstrap | Wiki 初始化

创建 research-wiki/ 三层架构（Schema + Raw + Wiki），基于 Andrej Karpathy LLM Wiki 方法论。
初始摄入：项目全景概述、模块清单、核心概念索引、关键实体。
触及页面：overview.md, index.md, log.md（共 3 页）。

## [2026-06-09] ingest | docs/ 文档深度摄入

处理全部 docs/ 目录资料（9 MD + 2 PDF 参考文档）。
概念页（7 个）、实体页（2 个）。

## [2026-06-09] ingest | 核心模块逐文件摄入

为 7 个核心 .py 模块创建 Wiki 页面。

## [2026-06-09] ingest | AKShare Stock API 文档

raw 层: akshare-stock-api.md + entities: 数据源-AKShare.md

## [2026-06-09] ingest | docs/ 残留文档处理

创建 2 个概念页（开发环境配置、数据口径与样式规范），删除 docs/ 目录。

## [2026-06-09] build | 紫金矿业 (02899)

PB=1.0x, 新建 scripts/02899/business_commentary.py, valuation_method="pb" 写入 config。

## [2026-06-10] lint | Wiki 健康检查 + 修复

全站 Lint 扫描结果：
- 修复 8 处断链：数据口径规范→数据口径与样式规范 (×2)、估值倍数优先级→VL 估值方法论 (×2)、
  VL 官方指南 2020 中文解读→概念页组 (×2)、requirements.txt→移除
- 创建 4 个缺失模块页：generate_reading.py、generate_index.py、list_refs.py、set_baba_meta.py
- 修复 Step 8 矛盾：统一为 WARNING（非 BLOCK），对齐实际代码行为
- 添加 6 条反向链接解决孤儿页面：数据源-AKShare、李录阅读法融合、开发环境配置
- 更新 index.md

修复后状态：25 页（1 overview + 11 modules + 9 concepts + 3 entities + 1 index + 1 log），0 断链，0 孤儿。
