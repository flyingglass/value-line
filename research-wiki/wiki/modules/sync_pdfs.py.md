---
module: sync_pdfs.py
category: 数据同步
depends_on: [upload_to_weiyun.py (weiyun skill)]
updated: 2026-06-13
---

# sync_pdfs.py — 微云双向增量同步

## 职责

将 `data/pdfs/` 目录与微云 `value-line-pdfs/` 双向增量同步。
JSON-RPC 2.0 直调微云 MCP API，不依赖 AI 工具。

## 用法

```bash
python sync_pdfs.py status     # 查看差异
python sync_pdfs.py upload     # 上传增量到微云
python sync_pdfs.py download   # 从微云下载增量
```

## 增量策略

- 比对: 文件名 + 文件大小
- 同名同大小 → 跳过
- 仅本地有 → upload
- 仅微云有 → download
- 大小不同 → 覆盖更新

## 设计决策

- **CPU×2 并发**: 上传和下载均使用线程池
- **上传依赖**: 调用 weiyun skill 的 `upload_to_weiyun.py` (SHA1 分块计算)
- **下载直连**: JSON-RPC `weiyun.download` 获取 HTTPS 链接
- **完整性**: 上传后重新扫描校验远程大小，下载时逐个比对并自动重试
- **幂等**: 可安全重复运行，断点续传

## 涉及模块

[[数据源-通达信TDX]] — 微云 MCP API 端点
