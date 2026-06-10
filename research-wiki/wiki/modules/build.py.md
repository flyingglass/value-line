---
module: build.py
category: 流水线编排
depends_on: [config.py, fetcher.py, engine.py, pdf_downloader.py, extract_mda.py, generate_report.py]
lines: 832
updated: 2026-06-09
---

# build.py — 主入口，8 步流水线

## 职责

系统唯一入口，编排 8 步强制流水线，处理估值倍数确认、前置校验、步骤调度。
任何一步失败即阻断，不生成报告。

## 关键函数

| 函数 | 职责 |
|------|------|
| `confirm_and_build()` | 确认页 + 估值解析 + 触发流水线 |
| `build()` | 执行完整 8 步 |
| `step_0_check_config()` | config 完整性检查（name_en 必填） |
| `step_1_fetch()` | 数据拉取（DB 存在时跳过） |
| `step_2_pdf()` | 年报 PDF 下载（≥3 年） |
| `step_3_mda()` | MD&A 提取（美股跳过） |
| `step_4_revenue()` | 营收结构入库（唯一步骤需手动脚本） |
| `step_6_engine()` | 调用 engine.py 计算指标 |
| `step_7_generate()` | 调用 generate_report.py |
| `step_8_verify()` | 72 项逐字段完整性校验 |
| `_write_valuation_meta()` | 估值参数写入 DB meta 表 |
| `_read_valuation_meta()` | 从 DB 读取已有估值参数 |
| `_get_hist_valuation_ref()` | 从 DB 计算历史 PE/PB 均值 |

## 估值倍数优先级

```
CLI --cf/--pb  >  DB meta 已确认值  >  用户交互输入（含历史PE/PB参考）
```

**关键**：`_write_valuation_meta()` 必须在 `step_6_engine()` **之前**调用，因为 engine.py 作为子进程从 DB meta 表读估值参数。

## 数据流

```
CLI 参数 → 确认页 → Step 0-8 流水线 → HTML 报告
                                ↓
                        估值参数 → DB meta 表 → engine.py 读取
```

## 设计决策

- 无 `--force`：任何步骤失败即阻断，确保报告质量
- 估值参数 8 步成功后才写入 DB（防止中途失败覆盖已有值）
- `_set_active()` 通过正则替换 config.py 的 ACTIVE_STOCK 标记来切换标的
- Step 8 失败降级为 WARNING 而非阻断（报告仍生成）

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
