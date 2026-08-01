---
module: pdf_downloader.py
category: 文档采集
updated: 2026-06-09
---

# pdf_downloader.py — 年报 PDF 下载

## 职责

下载各标的历年年度报告 PDF，多市场适配。

## 下载来源

| 市场 | 来源 | 方式 |
|------|------|------|
| 港股 hk | 港交所披露易 | 搜索 API + 直链下载（含 config.HK_PDF_URLS fallback） |
| A 股 cn | 巨潮资讯网 | CNINFO_CATEGORIES 分类码搜索 |
| 美股 us | SEC EDGAR | CIK 搜索 10-K → stocklight.com 下载 |

## 校验机制

- PDF ≥ 3 年才通过
- 繁简体匹配兼容
- 结构损坏才删除重下
- 美股 10-K .htm 文件同样计入

## 存储

`data/pdfs/<code>/` 目录，命名格式 `{code}_{year}_年报.pdf`

## 涉及模块

[[config.py]] — HK_PDF_URLS、STOCKS
[[build.py]] — Step 2 调用

## 相关概念

[[三市场数据适配]]
[[vl/concepts/8 步流水线.md]] · [[vl/index.md]]
[[vl/modules/extract_mda.py.md]] · [[vl/modules/build.py.md]]
