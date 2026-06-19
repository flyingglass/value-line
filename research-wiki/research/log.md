# 投研操作日志

## [2026-06-19] ingest | TCL中环 002129 首次入库 + VL 报告

### 新增标的
- `config.py` → STOCKS 添加 002129（TCL中环，A股 SZSE，org_id=9900002703，总股本 40.43 亿）
- `data/002129.db` — 9 表完整财务数据库（2004-2026，最近 15 年用于报告）
- `data/pdfs/002129/` — 47 份年报/中报/季报 PDF

### 营收结构
- `scripts/002129/insert_revenue.py` → `revenue_structure` 表，`dim_type='by_product'`
- 2021-2025 年，每年 4-5 产品线（光伏硅片/光伏组件/半导体材料/电站/其他），共 21 条

### VL 报告
- `report/TCL中环.html` — PB=1.0x，8 步流水线 68/72 PASS（PE/EPS/CAGR 因亏损预期内 FAIL）
- `report/reading/002129.md` + `.html` — 李录阅读法融合版

### 数据目录页
- `research/002129/overview.md` — revenue_structure 表结构 + 产品速查表 + 占比演变

### 索引更新
- `report/index.html` 重建（43 标的 16 行业）
- `research/index.md` 新增 [[002129/overview]]

## [2026-06-17] ingest | 泡泡玛特 09992 数据目录

### 新增数据
- `data/09992.db` → `revenue_structure` 表，`dim_type = 'china_online_channel'`
- 2021-2025 年，每年 4 子渠道（抽盒机/天猫/京东/抖音/其他），共 20 条
- 金额单位：百万元人民币

### 数据目录页
- `09992/overview.md` — revenue_structure 表结构 + 全维度说明 + SQL 查询示例 + 速查表 + 二元汇总

### 原始资料
- 年报 PDF 原文保留在 `data/pdfs/09992/`（2021-2025 年报），不再另存 raw

## [2026-06-17] init | 投研 wiki 初始化
