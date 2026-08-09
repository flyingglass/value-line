# generate_wiki_index.py

## 概述

扫描 `research-wiki/` 下所有 `.md` 文件，生成自包含 SPA HTML 索引页。

## 核心设计

### 自包含单文件
一个 `research-wiki/index.html` 包含全部文章数据 + CSS + JS，无服务端依赖，直接部署到 GitHub Pages。

### 数据流
```
扫描 .md → 解析 YAML frontmatter → base64 编码正文 → JSON 嵌入 HTML → 浏览器端渲染
```

- 正文用 base64 编码后嵌入 JSON，避免特殊字符导致 JS 语法错误
- 前端 `marked.js` CDN 实时渲染 markdown → HTML（弹窗展示）

### 文章来源（5 类）

| 来源 | 路径 | 说明 |
|------|------|------|
| 标的 wiki | `research-wiki/research/<code>/` | overview / thesis / industry-chain 等 |
| 标的原始资料 | `research-wiki/raw/research/<code>/` | 研报、数据日志 |
| 投研知识 | `research-wiki/research/articles/` | concepts / entities / papers / synthesis |
| 通用原始资料 | `research-wiki/raw/research/articles/` | 书籍摘要、访谈笔记 |
| 海外标的 | `research-wiki/raw/research/AMZN|GOOGL|MSFT/` | 美股原始资料 |

### 分组逻辑

**按标的**：同一 code 目录下的 wiki 页 + raw 资料合并展示，按行业排序。

**多学科**：通用文章按关键词匹配 5 个主题：
- 🧠芒格·格栅理论 — 芒格/穷查理/格栅/伯克希尔/巴芒/迪士尼/竞争性毁灭/倾覆力矩/临界质量/ESS
- 🔄复杂经济学 — 复杂经济/阿瑟/收益递增/技术自创生/技术本质/技术革命
- 🧬生物学 — 道金斯/戴蒙德/里德利/格里宾/自私/枪炮/基因组/冰河期
- 🧩心理学 — 西奥迪尼/影响力
- 📚书籍摘要 — 艾德勒/阅读法/四级阅读

匹配范围：标题 + 路径 + 正文前 300 字符。

### 前端功能
- 搜索：全文检索（标题 + 内容）
- 筛选：全部 / 按标的 / 多学科
- 展开：点击卡片 → 弹窗 `marked.js` 渲染 markdown
- 折叠：标的分组可折叠
- 响应式：iPad/iPhone 自适应

## 运行

```bash
.venv\Scripts\python scripts/generate_wiki_index.py
```

输出：`research-wiki/index.html`

## 依赖

- Python: `yaml`
- 前端 CDN: `marked.js`

## 参见

- [[generate_report.py]] — VL 单页报告生成（类似自包含设计）
- [[generate_index.py]] — Value Line 索引页生成
