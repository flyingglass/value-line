# Build 流程与规范

## 基本用法

```bash
# CF 估值模式（默认，适合消费/科技/成长股）
python build.py 09992 --cf 15.0

# PB 估值模式（适合银行/保险/资产型）
python build.py 01114 --pb 0.8

# 重建已有报告（无需重复确认）
python build.py 09992 --cf 15.0
```

## 流水线 8 步

| Step | 脚本 | 说明 |
|------|------|------|
| 0 | check config | 检查 config.py 完整性 |
| 1 | `fetcher.py` | 拉取财报 + K线数据 → `data/<code>.db` |
| 2 | `pdf_downloader.py` | 下载年报 PDF → `data/pdfs/<code>/` |
| 3 | `extract_mda.py` | PDF 提取管理层讨论分析 → DB `meta.mda_text` |
| 4 | `scripts/<code>/insert_revenue.py` | 营收结构写入 DB |
| 5 | config final | 最终 config 检查 |
| 6 | `engine.py` | 计算全部指标 → `report_data.json` |
| 7 | `generate_report.py` | 生成自包含 HTML → `report/<Name>.html` |
| 8 | verify | 逐字段完整性校验（1 项失败即阻断） |

**前置条件**：数据库 `data/<code>.db` 必须已存在且有 ≥3 年年报 PDF。

## 估值参数

### 参数存储

- 估值参数写入 `data/<code>.db` 的 `meta` 表：
  - `cf_multiplier`：CF 倍数
  - `pb_multiplier`：PB 倍数
  - `valuation_method`：`"cf"` 或 `"pb"`
- `engine.py` 从 DB 自动读取这些参数生成估值线

### 重建规则

1. **显式指定 `--cf N` / `--pb N`**：直接使用指定值，写入 DB
2. **省略倍数参数**：按优先级自动解析 — DB 已确认值 > 交互输入（显示历史PE/PB参考）
3. **估值参数写入时机**：所有 8 步成功后写入（防止中途失败覆盖已有值）

### 估值倍数自动复用

首次构建时用户确认的估值倍数会写入 DB `meta` 表。后续重建同一标的时，省略 `--cf`/`--pb` 即可自动复用，无需重复输入。

## 常见问题

### build.py exit code 1, step_8 交叉校验不通过

step_8 对 pre-IPO 年份的数据 mismatch 会报 FAIL。这通常是已知的早期数据质量问题（借壳上市、重组前年份），不影响 step_6/step_7 生成的数据正确性。

处理方式：
- 检查 mismatch 年份是否为 pre-IPO 年份（前 3 年常见）
- 如需绕过 step_8，可分别运行 `python engine.py && python generate_report.py`，但估值参数不会自动写入 DB

### DB 中估值参数被覆盖

**历史问题（已修复）**：之前 `_write_valuation_meta()` 在流水线开始时就写入，即使后续步骤失败也会覆盖已有值。
现在已改为流水线全部成功后写入。

### 重建多个标的

每个标的独立运行一次 `build.py`，最后运行 `python generate_index.py` 更新索引。

```bash
python build.py 09992 --cf 15.0
python build.py 002027 --cf 10.0
python generate_index.py
```
