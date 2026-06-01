# Value Line 报告生成流程（强制8步，无豁免）

> **唯一入口：`python build.py <代码> --cf <倍数> [--years N]`**

---

## 0. 确认页（强制交互）

```
python build.py <代码> --cf <倍数> [--years N]

============================================================
  Value Line 报告生成 — 确认页
============================================================
  企业:      [名称]              ← config 自动读
  代码:      [代码].[交易所]
  市场:      [港股(H股) / A股]
  行业:      [行业]
  报表币种:   [CNY/HKD]
  数据年份:   YYYY-YYYY (共X年, 默认N年。--years N 可调整)
  CF 倍数:    [N]x               ← --cf 必填
============================================================
```

**拒绝条件：**

| 条件 | 行为 |
|------|------|
| 缺 `--cf` | argparse 拒绝 |
| `--cf` ≤ 0 | argparse 拒绝 |
| 代码不在 config.STOCKS | 拒绝 |
| 市场不是 hk/cn | 拒绝 |
| `--years` < 3 | argparse 拒绝 |

**确认页不出现 = 拒绝执行。**

### 年份规则

```
--years 未指定:
  ├─ 可用 > 10年 → 默认 min(15, 可用)
  └─ 可用 ≤ 10年 → 全用

--years N 指定:
  └─ N = min(N, 可用)  (不超过实际)
```

### 输入项

| 参数 | 必填 | 默认 | 说明 |
|------|------|------|------|
| `<代码>` | ✅ | — | 股票代码，如 09992 00700 |
| `--cf N` | ✅ | — | CF 倍数，如 15.0 |
| `--years N` | — | 15/全用 | 使用最近N年 |
| `--force` | ❌ | — | **已禁用** |

---

## 8步流水线（全阻断）

| Step | 操作 | 脚本 | 缺则 | 自愈 |
|------|------|------|------|------|
| 0 | config 完整性检查 | — | **BLOCK** | 缺 name_en 才阻断; business_desc/commentary 仅 INFO |
| 1 | 数据拉取 | fetcher.py | **BLOCK** | 自动下载 |
| 2 | 年报PDF下载 | pdf_downloader.py | **BLOCK** | 自动下载 (≥3年) |
| 3 | MD&A 提取 | extract_mda.py | **BLOCK** | 自动提取 → mda_text |
| 4 | 营收拆分入库 | insert_revenue.py | **BLOCK** | **手动补** |
| 5 | config final | — | **BLOCK** | — |
| 6 | **指标计算 + mda解析 + 交叉验证** | engine.py | **BLOCK** | _parse_mda_text() 解析为 BUSINESS/Commentary |
| 7 | HTML 生成 | generate_report.py | **BLOCK** | BUSINESS/Commentary 优先 mda_text → config fallback |
| 8 | **72项逐字段 + 交叉校验阻断** | build.py | **BLOCK** | — |

---

## 数据源（5层 + 回退计算）

| 层 | 源 | 内容 | 年份范围 |
|----|-----|------|---------|
| 1 | AKShare `analysis_indicator_em` | 年度预计算指标 (PE/BPS/ROE等) | **最近9年** (上游限制) |
| 2 | AKShare `financial_report_em` | 利润表/资产负债/现金流 原始数据 | **2001+** (全量) |
| 3 | AKShare 股息 + 手动 | dividend 表 | 2004+ |
| 4 | 年报 PDF → SQLite | 营收拆分 revenue_structure | **需手动维护** |
| 5 | 新浪 index | HSI 指数 | 全量 |

> **回退计算** (`engine.py`): 当 indicators 表缺某年数据时，自动从 income/balance/cashflow 原始表当面计算全部 24 项指标。税率用 `item_code` (004012001=税项, 004011999=除税前利润) 代替 `item_name` 以避免编码乱码。

## Step 6 内置交叉验证

> **原则：** 页面显示多少年数据 → 验证覆盖多少年。每一年的每个输入字段必须有第二源对比。

### 验证体系

```
交叉校验: 68/68 (0 mismatch)
  覆盖年份: 15/15 (100%)
  三源年份: 2017-2025 (9年, indicators↔income↔PDF)
  双源年份: 2011-2016 (6年, income↔balance↔PDF, 当面算 per-share)
  单源字段: DPS, Price (无第二数据源, 标记未验)
```

### 验证项（7项）

| 验证项 | 方式 | 阈值 | 覆盖 |
|--------|------|------|------|
| AKShare↔PDF Revenue | income vs PDF by_region sum | 5% (早年25%) | 15年 |
| AKShare↔Income Revenue | indicators vs income.004001001 | 3% | 9年 |
| AKShare↔Cashflow Dep | indicators vs cashflow | 1% | 8年 |
| PerSh OI consistency | PER_OI vs Rev/Sh 当面算 | 0.5% | 15年 |
| PerSh BPS consistency | BPS vs Eq/Sh 当面算 | 10% | 15年 |
| SHARES: Rev/PER_OI 反算 | TOTAL_SHARES vs Rev÷PER_OI | 0.5% | 15年 |
| SHARES: Eq/BPS 反算 | TOTAL_SHARES vs Eq÷BPS | 10% | 15年 |

> NetProfit / TotalAssets / Equity 三项全 15 年 0% 差异（内部过滤输出）。

### 验证方式说明

| 方式 | 含义 |
|------|------|
| **双表对照** | 同一指标在两张不同表中取值对比 (indicators vs income) |
| **当面计算** | 用原始数据按公式反推，与既有值对比 (PER_OI vs Rev/Sh) |
| **三源交叉** | 一条数据从三条独立路径推算验证 (TOTAL_SHARES) |
| **PDF 营收交叉** | AKShare 营收总额 vs 年报人工拆分的 by_region 汇总 |
| **H1+H2 自洽** | 半年 + 半年 = 全年的一致性 |

### Step 8 校验规则

```
validation.mismatches > 0  →  BLOCK (不生成报告)
validation.status != "OK"  →  BLOCK
```

---

## BUSINESS & AI Commentary 生成链路 (2026-06-01)

```
extract_mda.py → PDF文本 → _is_narrative()过滤财务数据句
    ↓  scoring-based classify_sentences()
    ↓  质量评分: categories≥3 + total≥10 + overview<70%
    ↓
    ├─ quality=1 → mda_text (按【章节】分段)
    └─ quality=0 → build_mda_from_data() (数据动态生成)
         ↓ SQLite meta.mda_text + meta.mda_quality
engine.py
    ↓  _parse_mda_text() if quality=1
    ├─ OK  → business_summary + mda_sections → 报告使用
    └─ None → _build_business_from_data() [自生成]
             → _build_commentary_from_data() [自生成]
         ↓ 纯财务数据 (营收/利润/ROE/地域/业务拆分/CAGR/PE)
generate_report.py → 渲染 BUSINESS + AI Commentary
```

**零 config.py 依赖** — 所有股票加入后自动从财务数据生成，无需手动维护 business_desc / analyst.commentary。

## 关键原则（不可违反）

1. **页面显示 N 年 → 验证 N 年。**
2. **每步阻断先溯源。** 脚本问题修脚本做兼容，数据问题确认后手补。
3. **PDF 校验宽容。** 结构损坏才删，繁简体不匹配保留。
4. **数据源兼容优先。** 毛利率：毛利直取 > COGS 回退。
5. **AKShare 港股 indicators 仅 9 年。** 早于 2017 年的年份 engine 自动回退到 income/balance/cashflow 当面计算，含税率 (item_code 004012001/004011999)、BPS (总权益/股数)、shares (config 兜底)。前台 `showYears` 截取后 15 年（`Y.slice(-15)`）。

---

## 阻断诊断

```
BUILD FAILED →
  ├─ Step 0: 补 config.py 的 analyst + business_desc
  ├─ Step 1: 检查 AKShare 网络
  ├─ Step 2: PDF < 3 → HKEX 搜索参数 / stockId / 繁简体
  ├─ Step 3: mda_text < 100chars → PDF 存在但提取失败
  ├─ Step 4: revenue_structure 空 → 手动 insert_revenue.py
  ├─ Step 6: engine 报错 → 字段映射兼容
  └─ Step 8: validation.mismatches > 0 → 交叉校验不通过
```
