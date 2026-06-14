# 操作日志

## [2026-06-14] fix | 新增股票三修复 — 确认页历史PE/PB + 流式输出防卡死 + 6位代码兼容

**问题**：
1. **确认页不显示历史PE/PB参考**：`_get_hist_valuation_ref` PE_AVG 分支被 `years`（BPS/EPS/K线交集）阻断 — A股 raw indicators 字段名不同（`basic_eps` 非 `BASIC_EPS`），交集为空 → PE_AVG 永不执行
2. **拉数据/年报卡死无反馈**：`_run` 用 `capture_output=True` — 全程静默，用户看到白屏 5+ 分钟
3. **6位代码兼容**：`_set_active` 正则 `[0-9]+` 不匹配 NVDA；PDF 年份检测 `\d{5}` 不匹配 6 位 A 股代码

**修复**：
- `build.py` `_get_hist_valuation_ref`：CF 的 PE_AVG 分支独立运行，不再依赖 BPS/EPS 交集（`if method == "cf" and years:` → `if method == "cf":`）
- `build.py` `confirm_and_build`：历史 PE/PB 参考移到 `if cf_multiplier is None:` 外部，**始终展示**
- `build.py` `_run`：添加"运行中..."进度提示；超时调整：fetcher 300→600s, generate_report 30→60s
- `build.py` `_set_active`：正则 `[0-9]+` → `[^"]*` 匹配任意代码格式
- `build.py` PDF 年份检测：`\d{5}` / `\d{4,6}` → `[A-Za-z0-9]+` 兼容字母+数字代码

**关键原则**：**确认页必须始终出现**，显示历史 PE/PB 参考。`--cf`/`--pb` 传参时不弹交互框但必须展示参考数据。

**验证**：A/H/美股 14/14 测试全通过。

**触及 Wiki 页面**：
- [[build.py]] — 更新确认页 + _run 流式输出
- [[8 步流水线]] — 强调确认页展示规则

## [2026-06-14] feat | 全量脚本标准化 — 38只全部对齐09992四件套

**动机**：09992 (泡泡玛特) 的 scripts 目录是唯一完整的标准：4 件脚本各司其职。其余 37 只股票缺失不等。

**标准四件套**：

| 脚本 | 作用 | 实现方式 |
|------|------|---------|
| `business_commentary.py` | 动态 Business + 5 段 AI Commentary | `build(stock, metrics, revenue_structure, years, cagr, spot)` 数据驱动 |
| `insert_revenue.py` | 营收拆分数据入库 | 手工维护年报分业务/分渠道/分地区数据 |
| `metric_adjustment.py` | EPS 非经常性调整 | A股 CAS扣非 / 港股探 FV+FX+GS+IM+OG / 美股直通 |
| `extract_business.py` | PDF 提取员工数等补充信息 | pdfplumber 搜索关键词 |

**效果**：
- 新增 93 个 `.py` 脚本，总计 153 个，全部语法检查通过
- 38 只股票全量报告重新生成，0 失败，17 只 ALL PASS
- 后续新增股票也按此标准

**触及 Wiki 页面**：
- [[个股脚本标准]] — 新建概念页
- [[项目全景概述]] — 补充 scripts 目录说明

---

## [2026-06-14] feat | Footnotes 重构 — 分行展示 EPS 调整项明细

**设计**：每项非经常调整独立一行，标签用中文全称，数据两位小数（百万级精度），无数据留空。

**格式**：
```
Footnotes      2018  2019  2020  ...
政府补贴       0.05  0.17  0.45  ...
公允价值变动     —     —   (0.11) ...
───────────────────────────────────
adj.NP         0.04  0.13  0.25  ...
```

**引擎**：`engine.py` → `all_footnotes` 新增 `adj`/`diff`/`src` 结构化字段，diff 用原始 `np_val`/`adj_np` 直算避免脚注文本四舍五入失真。

**前端**：`generate_report.py` JS 端解析 `src` 提取各缩写出现的年份，每项一行；表格含灰色垂直分割线；合计行 `adj.NP` 位于底部分隔线上方。

**缩写表**：GS=政府补贴, FV=公允价值变动, FX=汇兑收益, II=投资收益, IM=资产减值, EL=权益法亏损, OG=其他收益, CD=A股扣非

**触及 Wiki 页面**：
- [[generate_report.py]] — 新增 Footnotes 渲染章节
- [[engine.py]] — 补充 footnotes 结构化字段

## [2026-06-14] fix | 脚本 revenue_structure 类型 + SourceFileLoader 编码 + A股 TDX footnote 三连修

**问题**：
1. `importlib.spec_from_file_location(encoding="utf-8")` 在 Python 3.11 不支持 → `TypeError`
2. engine 传的 `revenue_structure` 是 `{"by_product": [...]}` dict，脚本里 `revenue_structure[:3]` 把 dict 当 list → `str.get()` 报错 → 脚本静默失败 → 回退到 PDF 乱码
3. A 股也显示了"通达信(TDX)财报计算" footnote（AKShare indicators 早年为空触发 `has_fallback=True`）

**修复**：
- `engine.py` 3 处加载点改用 `SourceFileLoader`（自动检测 `# coding: utf-8`）
- `scripts/000408/`: `isinstance(revenue_structure, dict)` + 遍历 `items()` 取前 3 条
- `scripts/09992/`: `revenue_structure.get("by_ip", [])` 替代 list comprehension
- `engine.py` L653: `and market == "hk"` 限定仅港股生成 footnote

**验证**：14 只有动态脚本的标的全部 Commentary PASS，藏格从乱码修复为 `from_script: True`。

**触及 Wiki 页面**：
- [[engine.py]] — 更新脚本加载 + 数据源 footnote 说明
- [[BUSINESS 生成链路]] — 补充 revenue_structure 参数类型

## [2026-06-14] feat | 全链路智能新鲜度检测 — 双轨模型

**设计**：将报告数据分为两类，各自独立检测新鲜度：
1. **股价类**（Header/K线/估值线）：查最近 3 个自然日 K 线是否存在 → 缺则自动拉取
2. **财报类**（24行/季度/CAGR/估值）：查最新 report_date，对比当前日期推算应发布报告期 → 有新品则自动拉取

**改动**：
- `build.py`：`step_1_fetch` 新增 `_need_fresh_prices()` + `_need_fresh_financials()` 双轨检测
- `build.py`：`step_2_pdf` 检测最新 PDF 年份落后当前年份 → 自动下载
- `build.py`：`step_3_mda` 存 `mda_extracted_year`，新年报 PDF → 强制重提
- `fetcher.py`：新增 `last_fetch_date` meta key（YYYY-MM-DD 格式）
- **效果**：`python build.py <code>` 无需 `--fetch`，自动判断哪些步骤需要刷新

**触及 Wiki 页面**：
- [[build.py]] — 更新 Step 1/2/3 描述
- [[extract_mda.py]] — 更新质量阈值 + 年份追踪
- [[engine.py]] — 更新 mda_parsed 逻辑
- [[8 步流水线]] — 更新 Step 描述

## [2026-06-14] refactor | 移除全部硬编码 commentary → 动态 business_commentary.py

**原则**：Business 和 AI Commentary 不应写死数字，应通过 `build(stock, metrics, revenue_structure, years, cagr, spot)` 从实时数据动态生成。

**改动**：
- 新建 `scripts/{000408,00883,09992,300308}/business_commentary.py`（4 只）
- 重写 `scripts/{002027,00981,02097,600519}/business_commentary.py`（4 只）
- 删除 8 只股票的 config `analyst.commentary` 硬编码
- `extract_mda.py`：质量阈值放宽（≥2 类 + ≥6 句 + overview<85%），原始文本兜底
- `engine.py`：移除 `mda_quality=="1"` 门控 → 无条件尝试解析 mda_text

**动态脚本接口**：
```python
def build(stock, metrics, revenue_structure, years, cagr, spot):
    return {"business": str, "commentary": [p1,p2,p3,p4,p5]}
```

**触及 Wiki 页面**：
- [[BUSINESS 生成链路]] — 更新优先级链
- [[engine.py]] — 更新 commentary 生成逻辑
- [[extract_mda.py]] — 更新质量阈值

## [2026-06-14] fix | generate_report.py K线 tooltip PB 线缺失 + 系列名规范化

**根因**：K 线图 hover tooltip 估值线数值判断仅匹配 `x CF`（L623），PB 估值线（`0.67x PB`）永不符合 → hover 时无价格显示。

**修复**：
1. `valLabel` PB 模式改 `'x PB'` → `'*BPS'`（与 BPS 指标对齐，如 `0.67*BPS`）
2. tooltip 条件：`n.indexOf('x PB')>-1` → `n.indexOf('*BPS')>-1`
3. 同步匹配：`x CF` || `*BPS` 覆盖两种估值模式

**验证**：01114 华晨中国 × PB=0.67 → K 线 hover 显示 `0.67*BPS: {price}` ✅

**触及 Wiki 页面**:
- [[generate_report.py]] — 更新 tooltip 渲染 + 系列名
- [[VL 估值方法论]] — 补充 PB 图表标签格式

## [2026-06-13] fix | engine.py 季度前瞻双重漏洞修复 + ingest

**根因**：06699 季度区无 2026 年，排查发现两处漏洞：

1. `qtr_years` 追加（L2107）：仅探测 Q1 (03-31)，半年度报告公司仅发 H1 (06-30)，永远匹配不到
2. `build_semi_annual` 末尾前瞻（L1112-1115）：`financial_item_by_code` 无 `item_name` 回退，TDX 数据无 item_code → 静默失败

**修复**：L2107 追加 H1 探测；L1112-1115 加 `or reader.financial_item(...)` 回退。

**验证**：00700 2026 Q1 `forward: True` 正常 ✅。06699 无 2026 数据属公司未发布财报，非代码问题。

## [2026-06-13] ingest | CODEBUDDY.md 二次精简 — 15行纯宪法 + 腾讯全量报告

- `CODEBUDDY.md` 缩减为 3 段：项目身份 + 安全红线 + 环境规则（~30行）
- 新增 `concepts/Wiki操作手册.md` — 承载 Ingest/Query/Lint 流程 + 页面格式模板
- `overview.md` 追加 Wiki 目录结构 + "为什么存在"
- `index.md` 新增 Wiki操作手册 条目

## [2026-06-13] security | 🔴 TDX Token 硬编码泄露 — 已修复 + 写入宪法

**事件**：GitHub 扫描告警，`tdx_client.py:23` 硬编码 `Bearer TDX-e35604...` 暴露在仓库中。

**修复**：
1. `tdx_client.py` 改为从 `.env` 读取 token（`os.getenv("TDX_TOKEN")` + `_load_dotenv()`）
2. `git filter-branch` 重写 13 个 commit 从历史中抹掉 token
3. `git push --force` 覆盖远程

**宪法级规则**（写入 `CODEBUDDY.md` + Memory）：
- 源码中严禁硬编码任何密钥 / Token / 密码 / API Key
- 所有凭证必须通过 `.env` + `os.getenv()` 读取
- 写新模块前必须检查凭证来源
- Git commit 前自查 `git diff --staged`

## [2026-06-13] cleanup | 移除微云上传下载及相关 wiki 页面

删除内容：
- `research-wiki/wiki/entities/工具-微云网盘.md` — 整页删除
- `concepts/跨电脑迁移与云备份.md` — 移除微云引用，更新为两 Tool 方案
- `wiki/index.md` — 移除微云条目
- `.env` / `.env.example` — 移除 `WEIYUN_MCP_TOKEN`
- `tencent-weiyun/` 空目录 — 待手动删除

原因：微云 API 配额不足，改为手动同步。

## [2026-06-13] ingest | 季度数据修复 + 2026前向季报 + 股息0→—

### 改动

**engine.py**:
1. `build_semi_annual` H1 查询加 `or item_name` 回退（兼容 TDX 无 item_code）
2. Q1 季度查询全面加 `or item_name` 回退
3. 2026 前向季报：仅 Q1 时生成 `forward: True` 标记
4. `qtr_years` 动态追加下一年（如有 Q1 数据）

**generate_report.py**:
1. 季度股息 0.000 → "—"（`decimal===3&&v===0`）
2. 半年度格式股息同样处理

### 验证 (00700)

- Qtr.sales: 16y ✅ (含2026 Q1=1941.7亿)
- Qtr.eps: 16y ✅ (含2026 Q1=6.3)
- Qtr.dividends: 16y ✅
- Step 8: ALL PASS (73 checks, 0 fails)

## [2026-06-13] ingest | TDX 替换 fetcher 港股三大表 + engine 双路径改造

### 改动范围

**新建**: `tdx_client.py` — HTTP 直连 TDX API，字段映射，单位转换
**修改**: `fetcher.py` — 港股三大表改 TDX 拉取，indicators 改 INSERT OR IGNORE
**修改**: `engine.py` — 6 处改造：

1. `if ind and ind.get("OPERATE_INCOME"):` — 防止空壳 indicators 误入标准路径
2. BPS 统一 `balance.总权益 ÷ shares` — 替代 `indicators.BPS` 直读
3. else 分支 EPS 反推加权股数 — `shares = NP / 每股基本盈利`
4. 财报查询 `item_code or item_name` 双重回退 — 兼容 TDX 无 code
5. 折旧 `income.折旧及摊销` 兜底 — TDX 折旧在 income 不在 cashflow
6. 动态数据源边界检测 — 仅混合数据源时生成 `data_source_note`

**触及 Wiki 页面**:
- [[tdx_client.py]] — 新建模块页
- [[fetcher.py]] — 更新港股 TDX 双源拉取说明
- [[engine.py]] — 更新双路径、回退增强、BPS 公式
- [[数据源-通达信TDX]] — 标记已接入，更新 API 格式
- [[index.md]] — 新增 tdx_client.py 条目

### 验证结果 (00700 腾讯)

- 2011-2025 共 15 年，交叉校验 83/83 通过
- TDX 回退 vs 引擎标准: 23/24 项 <2%，仅 BPS 差异 4-5%
- 2017 年前 6 年全部 TDX 计算，2017 后 9 年保留 AKShare

## [2026-06-11] ingest | TDX + 微云 + IMA 三工具接入与迁移方案

接入通达信 TDX MCP 服务（港股财务数据 2001-2025，0.0% 偏差），安装微云 Skill（云备份上传脚本），整理 IMA 知识库配置。
设计跨电脑迁移方案：`.env` 统一管理全部 Token，微云存储备份包，`setup.cmd` 一键初始化。
触及页面：entities/数据源-通达信TDX.md, entities/工具-微云网盘.md, entities/工具-IMA知识库.md, concepts/跨电脑迁移与云备份.md, index.md, log.md（共 6 页）。raw 层: tdx-reference/tdx-mcp-api.md（完整数据字典）。

## [2026-06-09] bootstrap | Wiki 初始化

创建 research-wiki/ 三层架构（Schema + Raw + Wiki），基于 Andrej Karpathy LLM Wiki 方法论。
初始摄入：项目全景概述、模块清单、核心概念索引、关键实体。
触及页面：overview.md, index.md, log.md（共 3 页）。

## [2026-06-09] ingest | docs/ 文档深度摄入

处理全部 docs/ 目录资料（9 MD + 2 PDF 参考文档）。
概念页（7 个）、实体页（2 个）。

## [2026-06-09] ingest | 核心模块逐文件摄入

为 7 个核心 .py 模块创建 Wiki 页面。

## [2026-06-09] ingest | AKShare Stock API 文档

raw 层: akshare-stock-api.md + entities: 数据源-AKShare.md

## [2026-06-09] ingest | docs/ 残留文档处理

创建 2 个概念页（开发环境配置、数据口径与样式规范），删除 docs/ 目录。

## [2026-06-09] build | 紫金矿业 (02899)

PB=1.0x, 新建 scripts/02899/business_commentary.py, valuation_method="pb" 写入 config。

## [2026-06-10] lint | Wiki 健康检查 + 修复

全站 Lint 扫描结果：
- 修复 8 处断链：数据口径规范→数据口径与样式规范 (×2)、估值倍数优先级→VL 估值方法论 (×2)、
  VL 官方指南 2020 中文解读→概念页组 (×2)、requirements.txt→移除
- 创建 4 个缺失模块页：generate_reading.py、generate_index.py、list_refs.py、set_baba_meta.py
- 修复 Step 8 矛盾：统一为 WARNING（非 BLOCK），对齐实际代码行为
- 添加 6 条反向链接解决孤儿页面：数据源-AKShare、李录阅读法融合、开发环境配置
- 更新 index.md

修复后状态：25 页（1 overview + 11 modules + 9 concepts + 3 entities + 1 index + 1 log），0 断链，0 孤儿。

## [2026-06-10] ingest | .workbuddy 清理

- 删除 vl_handbook.txt（与已有 PDF 源重复）
- 迁移 style-reference.md → raw/vl-reference/style-reference.md，创建实体页 entities/原始资料-VL样式参考.md
触及页面：index.md。
