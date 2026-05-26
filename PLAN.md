# Value Line 中文版 — 实现方案 v2

## 项目路径
```
C:/LY/Repo/llm/value-line/
├── config.py
├── fetcher.py
├── pdf_downloader.py
├── engine.py
├── report.html
├── PLAN.md
└── data/
    ├── {code}.db            SQLite
    └── pdfs/{code}/          PDF+校验日志
        ├── {code}_{year}_年报.pdf
        └── {code}_{year}_年报.validation.json
```

## 5个文件

| 文件 | 职责 | 输出 |
|------|------|------|
| config.py | 标的定义+路径 | STOCKS字典 |
| fetcher.py | AKShare→SQLite | {code}.db |
| pdf_downloader.py | 年报PDF下载+4层校验 | PDF+validation.json |
| engine.py | 计算23行指标→JSON | report_data.json |
| report.html | 渲染Value Line单页 | 7区域页面 |

## PDF下载流程

```
A股: 巨潮 hisAnnouncement/query
  stock={code},{orgId} category=ndbg/bndbg/yjdbg/sjdbg
  adjunctUrl → static.cninfo.com.cn/...PDF

港股: 披露易 titleSearchServlet
  stockId=1000068054 t2code=40100/40200/40300
  FILE_LINK → download
```

## PDF 4层严格校验 (每次下载后执行)

| 层 | 验证 | 不通过则 |
|----|------|---------|
| 1 | 文件头==`%PDF-` | 删除,标记FAIL |
| 2 | 大小>10KB | 删除,标记FAIL |
| 3 | 页数>5 | 删除,标记FAIL |
| 4 | 首页含公司名 | 删除,标记FAIL |
| + | 报告类型关键词 | warn |

## 多股票支持

```python
# config.py 加一行
STOCKS["00700"] = { "name":"腾讯控股", "market":"hk",
    "hkex_stock_id":"7609", ... }

# 执行
python fetcher.py 00700
python pdf_downloader.py 00700
```

## 当前标的

| 代码 | 名称 | 市场 | PDF |
|------|------|------|-----|
| 09992 | 泡泡玛特 | HK | FY2023-2025 |
| 600519 | 贵州茅台 | CN | FY2014-2025 |
