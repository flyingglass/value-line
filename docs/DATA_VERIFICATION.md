# VL 数据准确性原则与交叉验证流程

> **适用对象:** 每只股票(新股接入/已有标的重建)必须遵循本文档规定的验证流程。
> **核心目标:** 确保报告中的每一个数值都经 AKShare ↔ PDF 年报 ↔ Config 三源交叉校验。

---

## 一、核心原则

### 1.1 数据准确性第一优先级

| 优先级 | 数据源 | 适用场景 |
|--------|--------|---------|
| **S** | PDF 年报 (官方披露) | 最终仲裁、AKShare疑点校验 |
| **A** | AKShare (东方财富) | 主力数据源、自动化获取 |
| **B** | Config (手动维护) | 补充缺失字段、元数据 |

**规则:**
1. AKShare 能覆盖的指标优先使用 AKShare
2. AKShare 数据不足或存疑时，必须比对 PDF 年报
3. PDF 年报数据以 **CNY 元单位**为准，注意货币换算
4. 任何修改指标计算逻辑必须先验证 AKShare ↔ PDF 一致
5. 校验未通过的指标必须在报告中标注来源

### 1.2 深刻理解 VL 手册

所有指标的口径必须严格对照 `1503516_Reading_VL_Report_WEB_2.7.17.pdf` 定义：

| VL 手册页码 | 内容 |
|------------|------|
| P.6-7 | Ranks (Timeliness/Safety/Technical/Beta) |
| P.7 | Price Chart, CF Line, RS Line |
| P.8 | Target Price, Quarterly Data |
| P.9-10 | Statistical Array 23 行指标逐一定义 |
| P.11 | Annual Rates, Footnotes |
| P.13 | 样本报告 (Disney) |

---

## 二、新股接入 SOP

```
步骤 1: 标的定义
  ├── config.py: STOCKS[name/code/market/currency/shares]
  └── 确认 shares 字段为总股本(股数)

步骤 2: 数据拉取
  ├── fetcher.py: 拉取行情/K线/三大表/分析指标/股息 → SQLite
  └── 验证: engine.py 自动运行 15项交叉校验

步骤 3: PDF 年报下载
  ├── pdf_downloader.py: 下载历年PDF年报
  └── 存储: data/pdfs/{ticker}/

步骤 4: 指标验证 (本文档核心)
  ├── 运行 24行指标逐项验证表
  ├── AKShare ↔ PDF 关键指标(营业收入/净利润/EPS/权益)交叉校验
  └── 标记✅/⚠️/🔴/❌

步骤 5: 报告生成
  ├── engine.py → report_data.json
  ├── generate_report.py → {name_en}.html
  └── 全量检查 4 个左栏区域 + 图表
```

---

## 三、数据源对照

### 3.1 AKShare 数据结构

| 表 | 来源 | 用途 |
|----|------|------|
| `spot` | `stock_hk_spot` (港股) / `stock_zh_a_spot` (A股) | 行情快照 |
| `kline` | `stock_hk_daily` (港股, 前复权) | 月K线/成交量 |
| `indicators` | `stock_financial_hk_analysis_indicator_em` (港股年报) | 分析指标(EPS/BPS/ROE等) |
| `income` | `stock_financial_hk_report_em` (港股利润表, 含中报) | 营收/成本/利润/税率 |
| `balance` | `stock_financial_hk_report_em` (港股资产负债表) | 资产负债/权益 |
| `cashflow` | `stock_financial_hk_report_em` (港股现金流量表) | 折旧/资本支出 |

**港股关键字段映射 (AKShare → VL):**

| AKShare item_name | VL 用途 |
|-------------------|--------|
| 营业额 | Revenues |
| 销售成本 | COGS |
| 经营溢利 | Operating Profit |
| 股东应占利润 | Net Profit (归母) |
| 折旧及摊销 / 折旧及摊销 | Depreciation |
| 股东权益 / 归属于母公司所有者权益 | Common Equity |
| 总权益 | Total Equity |
| 流动资产合计 / 流动负债合计 | Working Capital |
| 长期贷款 / 应付债券 / 融资租赁负债(非流动) | Long-Term Debt |

**A股 (THS) 数据差异:**
- A股用 THS 字段名(中文)，需通过 `THS_INDICATOR_MAP` 映射到英文名
- A股 `indicators` / `income` / `balance` / `cashflow` 格式为**长表** (EAV: item_name + amount)
- 单位: A股报表通常为万元，港股报表为元

### 3.2 PDF 年报数据

- 存储路径: `data/pdfs/{ticker}/`
- 文件命名: `{ticker}_{year}_年报.pdf`
- 校验数据来源页面:
  - 合并利润表 → 营业收入/净利润/EPS
  - 合并资产负债表 → 总权益/归母权益/长期借款
  - 附注 → 非经常性损益

---

## 四、24 指标逐项验证清单

> **验证状态:** ✅ 已对齐 | ⚠️ 需PDF校验 | 🔴 有差异 | ❌ 无法实现

| # | VL 指标 | VL 定义 (手册原文) | 本项目公式 | AKShare | PDF校验 | 状态 |
|---|---------|-------------------|-----------|---------|---------|------|
| 1 | Revenues per sh | Revenue ÷ Shares | `营业总收入 ÷ shares` | ✅ PER_OI | — | ✅ |
| 2 | "Cash Flow" per sh | (NI + D&A - PrefDiv) ÷ Shares | `(归母净利+折旧) ÷ shares` | ✅ | — | ✅ |
| 3 | Earnings per sh | Diluted EPS, excl. nonrecurring | `DILUTED_EPS` (fallback: BASIC_EPS) | ✅ | ⚠️ 扣非 | ✅ DILUTED |
| 4 | Div'ds Decl'd per sh | 宣告股息/股 | dividend 表年度 DPS | ⚠️ 实付 | ⚠️ 宣告 | ⚠️ |
| 5 | Cap'l Spending per sh | CapEx + Acquisitions ÷ Shares | `(购建固资+收购子公司) ÷ shares` | ✅ | — | ✅ |
| 6 | Book Value per sh | Common Equity ÷ Shares | `AKShare BPS` | ✅ | ⚠️ 待验 | ⚠️ |
| 7 | Common Shs Outst'g | 普通股流通股数(百万) | `shares ÷ 1e6` | ✅ | ✅ | ✅ |
| 8 | Avg Ann'l P/E | Avg Price ÷ EPS | `avg_close ÷ EPS` | ✅ | — | ✅ |
| 9 | Relative P/E | Stock P/E ÷ VL Universe P/E | `个股PE ÷ HSI PE` | ✅ | ❌ | 🔴 对标 |
| 10 | Avg Ann'l Div'd Yield | DPS ÷ Avg Price | `DPS ÷ avg_close × 100` | ⚠️ | — | ⚠️ 缺数据 |
| 11 | Revenues ($mill) | 百万美元 | 亿元 (÷1e8) | ✅ | ✅ 必验 | ⚠️ 单位 |
| 12 | Gross Margin | VL原版无，本项目新增 | `(营收-成本) ÷ 营收` | ✅ | — | ✅ 新增 |
| 13 | Operating Margin | EBITDA ÷ Revenue | `(经营溢利+折旧) ÷ 营收` | ✅ | — | ✅ |
| 14 | Depreciation ($mill) | 百万美元 | `折旧 ÷ 1e8` 亿元 | ✅ | — | ⚠️ 单位 |
| 15 | Net Profit ($mill) | 扣除非经常性后净利 | `归母净利 ÷ 1e8` 亿元 | ⚠️ 含非经常 | ⚠️ 年报扣非 | ⚠️ |
| 16 | Income Tax Rate | Tax ÷ Pre-Tax Income | `TAX_EBT` 直接取 | ✅ | — | ✅ |
| 17 | Net Profit Margin | NI ÷ Revenue | `(净利 ÷ 营收) × 100` | ✅ | — | ✅ |
| 18 | Working Cap'l ($mill) | CA - CL | `流动资产 - 流动负债` | ✅ | — | ✅ |
| 19 | Long-Term Debt ($mill) | 所有有息长期债务 | `长期贷款+应付债券+融资租赁+长期应付` | ✅ | ✅ | ✅ 已修复 |
| 20 | Shr. Equity ($mill) | 总权益(含少数) | `总权益 ÷ 1e8` 亿元 | ✅ | — | ✅ |
| 21 | Return on Total Cap'l | EBIT ÷ (LT Debt + Equity) | `EBIT ÷ (LT_Debt + 总权益)` | ✅ | — | ✅ |
| 22 | Return on Shr. Equity | NI ÷ (Common + Preferred) | `自算 NI ÷ 总权益 × 100` | ✅ | ⚠️ 待验 | ✅ 自算 |
| 23 | Retained to Com Eq | (NI - All Divs) ÷ Common Eq | `(净利-股息) ÷ 归母权益` | ✅ | — | ✅ |
| 24 | All Div'ds to Net Prof | Total Divs ÷ NI | `股息 ÷ 净利 × 100` | ✅ | — | ✅ |

---

## 五、关键交叉校验项 (每只股票必做)

### 5.1 必验指标 (AKShare ↔ PDF)
| 指标 | AKShare 字段 | PDF 页面 | 容差 |
|------|-------------|----------|------|
| 营业收入 | `indicators.OPERATE_INCOME` | 合并利润表 | ±1% |
| 归母净利润 | `indicators.HOLDER_PROFIT` | 合并利润表 | ±1% |
| 基本/稀释 EPS | `indicators.BASIC_EPS` / `DILUTED_EPS` | 利润表 | ±0.01 |
| 总权益 | `balance.总权益` | 合并资产负债表 | ±1% |
| 归母权益 | `balance.股东权益` | 资产负债表 | ±1% |
| 每股净资产(BPS) | `indicators.BPS` | 资产负债表÷股本 | ±5% |

### 5.2 货币单位处理
- 港股报表: 人民币(CNY) 元为单位
- A股报表: 人民币(CNY) 万元或元
- AKShare 港股指标: 元
- AKShare A股指标: 与报表单位一致
- **年报数据以 CNY 为准，报表若为 HKD 需汇率换算**

---

## 六、无法修复项清单 (所有股票通用)

| # | 问题 | 原因 | 披露方式 |
|---|------|------|---------|
| 1 | 非经常性项目剔除 | AKShare 无扣非稀释 EPS | 标注"AKeStat"或脚注 |
| 2 | Relative P/E 对标 | 需 VL Universe ~1700 只股票 | 用 HSI/CSI300 替代，差异注明 |
| 3 | Div'ds Decl'd vs 实付 | AKShare 只有实付股息 | 标注数据来源 |
| 4 | 单位(VL: 百万美元) | 本项目用亿元 CNY | 这是设计决策，非缺陷 |
| 5 | 预测列 (粗斜体) | 无分析师预测能力 | 标注 N/A |
| 6 | 评级 (Timeliness/Safety) | 需量化模型 | 标注 N/A |

---

## 七、验证执行记录模板

```
## {code} {name} — 验证记录

### 基本信息
- AKShare 年报数: {count}
- PDF 年报数: {count}
- 覆盖年份: {start}-{end}
- 货币: {CNY/HKD}

### 交叉校验结果
| 年份 | 项目 | AKShare | PDF | 偏差 | 状态 |
|------|------|---------|-----|------|------|
| 2025 | 营业收入(亿) | XXX | XXX | 0.1% | ✅ |
| 2025 | 归母净利(亿) | XXX | XXX | 0.2% | ✅ |
| 2025 | EPS(元) | XXX | XXX | 0.01 | ✅ |
| 2025 | 总权益(亿) | XXX | XXX | 0.5% | ✅ |

### 已知问题
- [ ] BPS 待 PDF 验证
- [ ] 扣非净利待提取
- [ ] 股息宣告 vs 实付差异

### 验证人 & 日期
- 验证日期: YYYY-MM-DD
- 状态: [通过/有条件通过/未通过]
```

---

> **最后更新:** 2026-05-31
> **维护者:** AI Agent + 用户
> **相关文档:** `VL_REGION_ALIGNMENT.md`, `VL_INDICATORS_SPEC.md`
