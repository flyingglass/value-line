---
module: generate_wiki_index.py.md
category: 流水线编排
depends_on: []
updated: 2026-09-10
---

# generate_wiki_index.py

## 概述

扫描 `research-wiki/` 下所有 `.md` 文件，生成 **多页静态站点**：
- `research-wiki/index.html` — 首页（白马 / 学股 / 疯狂的里海 / 多学科 **四个一级分类 tab** + 分类内卡片 + 搜索）
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

## 首页 HTML 结构（用户确认的标准，后续保持此版式）

首页 = **一级分类 tab + 分类内卡片**，分类与 `research/` 下一级目录对齐（2026-09-26 起）：

| tab | 卡片 | 来源 |
|-----|------|------|
| 白马 | 每个标的一张卡片，**按行业分行**（行业一个 `.secgrid`） | wiki 页面位于 `research/白马/<code>/` 的标的；仅有原始资料的组（AMZN / GOOGL / MSFT / 中芯国际）单列「仅原始资料」一节垫底，保留入口 |
| 学股 | 组内每个标签（广州 / 深圳 / 跟踪 / AI软件）一张卡片 | 点击直达组页对应标签 `view/cases/学股/index.html#dir=<标签>` |
| 疯狂的里海 | 组内每个标签（案例 / 方法论 / 时间线 / 概览 / 原始资料）一张卡片 | 同上 |
| 多学科 | 每个主题一张卡片（芒格·格栅理论 / 复杂经济学 / 生物学 / 心理学 / 书籍摘要） | `view/general/index.html#dir=<主题>` |

- 卡片规格（`.grp`）：两行居中布局——第一行 = 名称链接 `.name`（全名、**允许换行、不截断**），第二行 = 标签；**不带**「进入 →」链接，名称本身即链接。
  - 标的卡片：浅蓝底 `#f2f7ff` + 描边 `#b7cdea`，标签为行业色 `.pill.industry`
  - 专题卡片（`.casegrid`）：淡紫底 `#fbf6fe` + 描边 `#e2c9f0`，标签为「N 篇」`.pill.topic`
  - 多学科卡片：同标的卡片底色
- **行业标签配色**：每个行业一种「浅底 + 深字」固定色，色表集中在脚本顶部 `INDUSTRY_STYLE` 字典；新增行业在此补色，同类行业颜色全站一致（首页卡片与标的组页头部同一套）。

### 交互（`HOME_JS`）
- tab 点击 / `#dir=<分类>` hash 就地切换面板，不跳转；tab 上的数字 = 该分类下的卡片数。
- 搜索框实时过滤**全部 tab** 内的卡片，同步刷新每个 tab 的命中数；当前 tab 命中为 0 而别处有命中时**自动切到第一个有命中的分类**；全部无命中才显示「没有匹配的内容」。
- 某行业整个 `.secgrid` 无匹配时整行隐藏（不留白）。
- 响应式：iPad / iPhone 自适应，移动端网格降为单列。

## 数据流

```
扫描 research-wiki/ 下的 .md
  → 解析 YAML frontmatter（标题/日期/分类/tags）
  → 按来源归类：research/白马/<code>/（标的；容器目录对站点透明，组键仍为 <code>）、research/ 专题、
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
[[vl/index.md]]
