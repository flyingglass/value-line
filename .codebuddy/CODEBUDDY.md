# Value Line — 项目宪法

## 项目

自动化投资研究报告生成系统。A 股 / 港股 / 美股，8 步流水线 → VL 单页 HTML 报告。

Wiki 知识库：`research-wiki/`。操作流程详见 [[Wiki操作手册]]，项目全景详见 [[项目全景概述]]。

## 🔴 安全红线（不可违背）

**源码中严禁硬编码任何密钥 / Token / 密码 / API Key。**

1. 所有凭证必须通过 `.env` + `os.getenv()` 读取
2. `.env` 在 `.gitignore`，模板 `.env.example`（值为 `xxx` 占位）
3. 写新模块前检查：是否从 `.env` 读凭证？
4. `git commit` 前自查：`git diff --staged` 不得出现真实 token
5. 发现硬编码 = 立即 `git filter-branch` 清理历史 + force push

> 2026-06-13：`tdx_client.py:23` 硬编码 Bearer Token 泄露，已修复。不可再犯。

## 环境

- Python：`.venv\Scripts\python.exe`（虚拟环境，不可用全局 Python）
- 依赖：`requirements.txt`（akshare, pdfplumber, requests, pandas）
- 凭证：`.env` 管理所有 API token（TDX / IMA）
