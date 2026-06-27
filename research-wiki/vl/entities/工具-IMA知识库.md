---
entity: 工具-IMA知识库
type: 外部服务 / 知识库
protocol: MCP stdio (本地 Python 服务)
created: 2026-06-11
---

# 工具：IMA 知识库

## 概述

腾讯 IMA（智能知识库），通过本地 Python MCP 服务接入。用于查询和写入知识库内容。

## 关键属性

| 属性 | 值 |
|------|-----|
| 接入方式 | CodeBuddy stdio MCP (`~/.codebuddy/ima-mcp/`) |
| 服务脚本 | `server.py` |
| 依赖 | Python venv + `httpx` + `mcp` |
| 认证 | `.env` 文件：`IMA_CLIENT_ID` + `IMA_API_KEY` |

## 迁移配置

```json
// ~/.codebuddy/mcp.json
"ima-openapi": {
  "type": "stdio",
  "command": "C:/Users/<user>/.codebuddy/ima-mcp/.venv/Scripts/python.exe",
  "args": ["C:/Users/<user>/.codebuddy/ima-mcp/server.py"]
}
```

## 涉及模块

不直接参与 build 流水线，属于辅助工具链。

## 相关概念

[[开发环境配置]]
[[数据源-通达信TDX]]
