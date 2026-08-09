# Wiki 索引

> 最后更新：2026-07-24

## 概述

- [[overview|项目全景概述]] — 项目定义、市场覆盖、8+1 步流水线、核心产物
- [[项目目录结构]] — 完整目录树、路径规则、使用方式

## 模块 (modules/)

- [[build.py]] — 主入口，8+1 步流水线编排，估值倍数确认
- [[config.py]] — 标的配置中心，STOCKS 字典，市场配置，VL 指标定义
- [[engine.py]] — 核心计算引擎，~2500 行，24 项指标，双路径(TDX/AKShare)，动态数据源边界
- [[fetcher.py]] — 双源数据获取（TDX 三大表 + AKShare 指标/分红），三市场适配
- [[tdx_client.py]] — TDX HTTP API 封装，字段映射，单位转换
- [[pdf_downloader.py]] — 年报 PDF 下载，港交所/巨潮/SEC 多源
- [[extract_mda.py]] — PDF 文本提取，管理层讨论 6 类关键词分类
- [[generate_report.py]] — VL 单页 HTML 生成，ECharts K 线 + 24 行阵列
- [[generate_reading.py]] — 深度阅读报告（Markdown + HTML，李录方法融合）
- [[generate_index.py]] — 索引页生成，按行业分组展示所有标的卡片
- [[generate_wiki_index.py]] — 🆕 投研 Wiki 索引页生成，扫描 research-wiki/ 生成自包含 SPA 单页 (base64 + marked.js)
- [[generate_business_commentary.py]] — 🆕 自动生成个股 Commentary 脚本（14 行业模板）
- [[list_refs.py]] — 历史估值参考，批量 PE/PB 均值

## 概念 (concepts/)

- [[24 行统计阵列]] — VL 标准指标体系的 5 组 24 行 + 6 种交叉诊断模式
- [[VL 估值方法论]] — CF / PB 两种估值模式，估值倍数优先级，五种 P/E 口径
- [[8 步流水线]] — build.py 强制流水线 + Step 4.5 自动生成，每步阻断规则与诊断
- [[多源交叉验证]] — AKShare ↔ 财报 ↔ PDF 三层校验，7 项交叉验证
- [[BUSINESS 生成链路]] — 3 级 fallback + 自动生成：手写脚本 → MDA → 引擎内置
- [[三市场数据适配]] — A 股 / 港股 / 美股数据源差异与汇率处理
- [[李录阅读法融合]] — 李录 5 秒测试 + 5 问检查清单 + VL 原生方法融合
- [[数据口径与样式规范]] — Header/K 线/24 行数据口径，页面 CSS/像素规范
- [[开发环境配置]] — 虚拟环境 .venv，依赖清单，全局清理规则
- [[跨电脑迁移与云备份]] — 两 Tool 认证统一、新电脑手动迁移
- [[Wiki操作手册]] — Ingest / Query / Lint 工作流 + 页面格式模板
- [[新增标的流程]] — 从 config 到报告的简化步骤（含自动生成 Commentary）
- [[Arthur-收益递增与涌现]] — Arthur 复杂经济学：收益递增（正反馈）与涌现的关系及原文引用
- [[个股脚本标准]] — 标准四件套：business_commentary / insert_revenue / metric_adjustment / extract_business

## 实体 (entities/)

- [[数据源-AKShare]] — 主力数据 API，本项目使用的接口清单与限制
- [[数据源-通达信TDX]] — **已接入**，港股 2001 年深度，三大表已替换 EM 源
- [[工具-IMA知识库]] — 腾讯 IMA 知识库 MCP，本地 Python 服务
- [[原始资料-PDF-官方阅读指南2020]] — VL 2020 版官方阅读指南 PDF
- [[原始资料-PDF-产品指南]] — VL 产品指南 PDF
- [[原始资料-VL样式参考]] — generate_report.py HTML 样式规范（布局/图表/颜色/单位）

## 投资框架

- [[../raw/research/articles/投资框架-复杂经济学指导手册]] — 四本著作整合框架，已移至 raw/research/articles/（原始资料命名空间）

## 综合分析 (synthesis/)
