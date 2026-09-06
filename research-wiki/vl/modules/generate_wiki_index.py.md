# generate_wiki_index.py

## 概述

扫描 `research-wiki/` 下所有 `.md` 文件，生成 **多页静态站点**：
- `research-wiki/index.html` — 首页（按标的 / 投资案例 / 多学科 三区卡片导航 + 搜索）
- `research-wiki/view/**` — 标的/案例组页、多学科整组页、每篇文章的独立 HTML 阅读页

纯静态、无服务端依赖；`.github/workflows/deploy.yml` 推送时把整个 `research-wiki/` 原样部署到 GitHub Pages。
**生成产物（index.html + view/）必须随源码一起提交**，否则线上首页卡片会指向不存在的 view 页面。

## 页面结构约定

```
view/stocks/<标的>/index.html       标的组页：文件夹 Tab（跟踪/经营/…/概览/原始资料），
                                   点击标签就地切换面板，不跳转
view/stocks/<标的>/<目录…>/<文章>.html   独立文章阅读页
view/cases/<专题>/…                 投资案例专题（组页同标的结构，标记「作者案例」）
view/general/index.html             多学科整组页（主题 = 顶栏 tab，就地切换）
view/general/<分类>/<文章>.html     通用文章阅读页
```

- 标的/专题元数据（行业、展示名）维护在脚本顶部 `stock_info`、`page_labels` 等字典及各 `.md` frontmatter
- 正文阅读页 = **base64 内嵌原文 + 浏览器端 marked.js CDN 渲染**，可离线解码阅读
- 首页检索为轻量前端过滤（按 名称 + 行业 + 文章标题），正文检索在各阅读页 Ctrl+F

## 首页 HTML 卡片格式（用户确认的标准，后续保持此版式）

首页自上而下三个分区（`.section-title` + `#sec-*` 容器），**此格式为最终样式，勿改回旧版**：

### 📌 按标的 `#sec-stocks`
- **按行业分块**：每个行业一个 `.secgrid` 网格行，同类标的连排、行内自动换行；**不同行业之间用独立行隔开**（块间留空）。
- **卡片 `.grp`**：浅蓝底 `#f2f7ff` + 描边 `#b7cdea` + 轻阴影，与下方白色卡片区分；
  卡片内 **两行居中布局**：第一行 = 标的名链接 `.name`（显示全名，允许换行、**不加省略号截断**），第二行 = 行业标签 `.pill.industry`。
- **不带**「进入 →」链接，也不铺文件夹 chip——标的名本身即是链接。
- **行业标签配色**：每个行业一种「浅底 + 深字」固定色，色表集中在脚本顶部 `INDUSTRY_STYLE` 字典；新增行业在此补色，同类行业颜色全站一致（首页卡片与标的组页头部同一套）。

### 📦 投资案例 `#sec-cases`
- 每个专题一张卡片，样式同标的卡片规格；标签为紫色「作者案例」。

### 📖 多学科 `#sec-general`
- **整块也做成卡片**：与标的卡片同底色/描边，标题「多学科 · N 篇」在卡片内居中；主题入口排列其下（不再用裸标题栏）。
- 通用文章按关键词归入主题（芒格·格栅理论 / 复杂经济学 / 生物学 / 心理学 / 书籍摘要）。

### 交互
- 搜索框实时过滤卡片；某行业整个 `.secgrid` 无匹配时整行隐藏（不留白）。
- 响应式：iPad / iPhone 自适应，移动端网格降为单列。

## 数据流

```
扫描 research-wiki/ 下的 .md
  → 解析 YAML frontmatter（标题/日期/分类/tags）
  → 按来源归类：research/<code>/（标的）、research/ 专题、
     research/articles/（通用多学科）、raw/**（原始资料，pdf 不入库）
  → 输出多页 HTML：首页 + view/ 组页 + 每文阅读页（base64 内嵌正文）
```

## 运行

```bash
.venv\Scripts\python scripts/generate_wiki_index.py
```

输出：`research-wiki/index.html` + `research-wiki/view/`（全量重建）。

## 依赖

- Python: `yaml`（其余 os/re/base64 均为标准库）
- 前端 CDN: `marked.js`（正文渲染）

## 参见

- [[generate_report.py]] — VL 单页报告生成
- [[generate_index.py]] — Value Line 索引页生成
- `research-wiki/research/log.md` — wiki 每次重建/改版的操作日志
