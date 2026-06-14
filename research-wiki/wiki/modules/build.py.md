---
module: build.py
category: 流水线编排
depends_on: [config.py, fetcher.py, engine.py, pdf_downloader.py, extract_mda.py, generate_report.py]
lines: 832
updated: 2026-06-14
---

# build.py — 主入口，8 步流水线

## 职责

系统唯一入口，编排 8 步强制流水线，处理估值倍数确认、前置校验、步骤调度。
任何一步失败即阻断，不生成报告。

**2026-06-14 改造**：智能新鲜度检测，默认自动判断是否需要拉取最新数据，无需手动 `--fetch`。

## 关键函数

| 函数 | 职责 |
|------|------|
| `confirm_and_build()` | 确认页 + 估值解析 + 触发流水线 |
| `build()` | 执行完整 8 步 |
| `step_0_check_config()` | config 完整性检查（name_en 必填） |
| `step_1_fetch()` | 双轨检测：股价按交易日 / 财报按报告期 → 自动拉取 |
| `step_2_pdf()` | 年报 PDF 下载（检测新年报 → 自动下载） |
| `step_3_mda()` | MD&A 提取（检测 PDF 年份 > 已提取年份 → 强制重提） |
| `step_4_revenue()` | 营收结构入库（唯一步骤需手动脚本） |
| `step_6_engine()` | 调用 engine.py 计算指标 |
| `step_7_generate()` | 调用 generate_report.py |
| `step_8_verify()` | 72 项逐字段完整性校验 |
| `_write_valuation_meta()` | 估值参数写入 DB meta 表 |
| `_read_valuation_meta()` | 从 DB 读取已有估值参数 |
| `_get_hist_valuation_ref()` | 从 DB 计算历史 PE/PB 均值 |
| `_need_fresh_prices()` | 查询最近 3 天 K 线，缺则需拉取 |
| `_need_fresh_financials()` | 查询最新 report_date，推算应发布的新报告期 |

## 双轨智能新鲜度

| 数据类型 | 检测方式 | 示例 |
|---------|---------|------|
| 股价 (daily) | 查最近 3 自然日 K 线 | 周五→周一间隔有效 |
| 财报 (periodic) | Q1(4月)→H1(8月)→Q3(10月)→FY(次年4月) | 6月时 DB 只有 12月 → 触发拉取 |
| PDF 年报 (annual) | 比较最新 PDF 年份 vs 当前年 | 6月后缺去年 PDF → 自动下载 |
| MD&A | 比较 mda_extracted_year vs PDF 年份 | PDF 更新 → 强制重提 |

`--fetch` 强制跳过所有检测，无条件全量重拉。

## 确认页 — 🔴 必须出现

无论是否传 `--cf`/`--pb`，确认页始终展示，显示：

```
企业/代码/市场/行业/币种/数据年份/估值方法/历史参考/强制拉取状态
```

**历史 PE/PB 参考**（2026-06-14 修复）：
- `_get_hist_valuation_ref()` 优先用 AKShare 自带的 `PE_AVG`（无需 BPS/EPS 交集），跨 A/H/美股全支持
- CF/PB 两路径均展示，不因已传 CLI 参数而隐藏
- 只有历史参考才允许估值确认进入流水线

**估值倍数优先级**：
```
CLI --cf/--pb  >  DB meta 已确认值  >  用户交互输入
```

## `_run` 子进程执行

所有步骤通过 `_run(cmd, timeout)` 子进程运行。**2026-06-14 改流式**：打印"运行中..."提示防卡死。

| 步骤 | timeout | 原因 |
|------|---------|------|
| Step 1 fetcher | 600s | 首次拉数据最耗时 |
| Step 2 pdf_downloader | 600s | 批量下载 PDF |
| Step 3 extract_mda | 120s | PDF 文本解析 |
| Step 6 engine | 120s | 全量指标计算 |
| Step 7 generate_report | 60s | HTML 渲染 |

## CLI 参数

```
--cf N       CF 倍数（消费/科技/成长股）
--pb N       PB 倍数（银行/保险/周期股）
--method     cf | pb（显式指定估值方法）
--years N    数据年份数（默认 ≤15）
--fetch      强制重拉数据
--publish    git commit + push → GitHub Pages
```

## 相关模块

[[config.py]] — STOCKS 配置中心
[[engine.py]] — 指标计算
[[generate_report.py]] — HTML 渲染

## 相关概念

[[8 步流水线]]
[[VL 估值方法论]]
