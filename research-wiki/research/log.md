# 投研操作日志

## [2026-06-17] init | 投研 wiki 初始化

创建 research-wiki/research/ 目录结构：
- `index.md` — 投研索引
- `log.md` — 本日志
- `<code>/` — 按标的的投研页面（随 ingest/query 逐步创建）
- `themes/` — 跨标的主题研究
- `raw/research/<code>/` — 投研原始资料归档

设计原则：
- 与 VL wiki (`wiki/`) 双轨并行，通过交叉链接互通
- 共享 `data/<code>.db` 和 `data/pdfs/<code>/` 数据层
- VL 流水线 (build.py/engine.py/fetcher.py) 不受影响
