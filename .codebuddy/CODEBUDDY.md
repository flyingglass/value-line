# Value Line — 宪法

## 项目
自动化投资研究报告系统。A/港/美股，8步流水线。Wiki: `research-wiki/`。详见 [[Wiki操作手册]]、[[项目全景概述]]。

## 🔴 安全（不可违背）
**严禁硬编码任何密钥 / Token / 密码。** 凭证一律 `.env` + `os.getenv()`。
- 写新模块：确认凭证从 `.env` 读
- `git commit` 前：`git diff --staged` 无真实 token
- 发现硬编码：`git filter-branch` 清历史 + force push

> 2026-06-13：`tdx_client.py` 泄露 Bearer Token，已修复。不可再犯。

## 环境
Python `.venv\Scripts\python.exe`，依赖 `requirements.txt`，凭证 `.env`（.gitignore）。
