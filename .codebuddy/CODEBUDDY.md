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
| 汇率 | `data/fx_rates.db` | HKD/CNY 每日汇率 |
| 标的配置 | `config.py` | 42 只标的的基本信息 |

### 工作流
1. **Ingest**：原文全文 → `raw/` → 读取 → 创建 wiki 页面（不可跳过任何一步）
2. **Query**：从 wiki 提取观点，结合 DB/PDF 数据验证
3. **Wiki**：结果写回，更新 index + log

### VL 流水线（不可修改其流程）
`build.py` → `engine.py` → `report/`。入口、8 步、输出格式、估值方法均不动。

## 🔴 安全（不可违背）
**严禁硬编码任何密钥 / Token / 密码。** 凭证一律 `.env` + `os.getenv()`。
- 写新模块：确认凭证从 `.env` 读
- `git commit` 前：`git diff --staged` 无真实 token
- 发现硬编码：`git filter-branch` 清历史 + force push

> 2026-06-13：`tdx_client.py` 泄露 Bearer Token，已修复。不可再犯。

## 环境
Python `.venv\Scripts\python.exe`，依赖 `requirements.txt`，凭证 `.env`（.gitignore）。
