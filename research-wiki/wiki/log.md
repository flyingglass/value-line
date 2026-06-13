# 操作日志

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
