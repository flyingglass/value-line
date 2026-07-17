# 安琪酵母 600298 — 原始资料索引

> 创建：2026-07-17 | 回溯：基于 2026-06-23 ingest

---

## 数据来源

| 来源 | 内容 | 提取时间 |
|------|------|---------|
| 年报 2025 MDA 全文 | pdfplumber 自动提取 → meta.mda_text | 2026-06-23 |
| VL 阅读报告 | `report/reading/600298.md` | 2026-06-23 |
| `data/600298.db` | 三大报表 + 指标 + 分红 + 行情 + 营收拆分 | 自动 |
| `scripts/600298/business_commentary.py` | Business + 5 段 AI Commentary | 2026-06-23 |
| `scripts/600298/insert_revenue.py` | 营收结构（产品/地区/渠道 3 维度） | 2026-06-23 |

---

## Wiki 对应页面

- [[../../research/安琪酵母/overview]] — 数据目录
- [[../../research/安琪酵母/thesis]] — 投资 Thesis
- [[../../research/安琪酵母/industry-chain]] — 产业链全景
- [[../../research/安琪酵母/operating-metrics]] — 运营指标跟踪

## 数据缺口（待补充）

- [ ] 糖蜜价格时间序列（行业数据，非年报披露）
- [ ] 海外工厂产能/产量数据
- [ ] 历史年份海外毛利率（仅 2025 有 by_region）
- [ ] 酵母蛋白新品类成长数据（2025 增速 +54.4% 但基数未知）
