# Value Line 项目 — 长期记忆

## 项目概述
中文版 Value Line 风格投资研报生成系统。目标: 单页 HTML 报告，覆盖 A股+港股。

## 架构原则 (不可违反)
1. **所有数据走 SQLite** — engine.py 和 generate_report.py 零硬编码
2. **AKShare ↔ PDF 交叉校验** — engine.py 运行自动检查，15项比对
3. **数据准确性 > 覆盖度** — 宁缺毋滥
4. **支持多股票** — config.py 定义标的，fetcher.py 支持 code 参数

## 项目路径
`C:/LY/Repo/llm/value-line/`

## 数据流
```
fetcher.py + insert_revenue.py → SQLite (data/{code}.db)
    ↓
extract_mda.py  → meta.mda_text (PDF提取, 按6类关键词分段)
engine.py       → _parse_mda_text() → report_data.json
    ↓
generate_report.py → report.html (自包含)
```

### mda_text 数据流 (2026-06-01 终版)

```
extract_mda.py: PDF → _is_narrative()过滤 → scoring classify → quality gate
    ├─ quality=1 → 分段 mda_text → SQLite
    └─ quality=0 → build_mda_from_data() → SQLite (mda_quality=0)

engine.py: 读取 mda_quality
    ├─ quality=1 → _parse_mda_text() → BUSINESS/Commentary
    └─ quality=0 → _build_business_from_data() + _build_commentary_from_data()
         ↓ 纯财务数据自生成 (营收/利润/ROE/地域/业务/CAGR/PE)
         ↓ 零 config 依赖, 任何新股票加入即自动生成

config.py: business_desc / analyst.commentary 仅作为最后兜底 (可选)
```

质量门规则: categories_covered≥3 + total≥10 + overview_pct<70% + ≥300chars

## 关键文件
- `config.py` — 标的定义、23行指标、期间分类
- `fetcher.py` — AKShare全量数据拉取 (行情/K线/三大表含中报/分析指标/股息)
- `engine.py` — 从SQLite计算23行指标/CAGR/半年度/营收结构/交叉校验
- `generate_report.py` — HTML报告生成
- `pdf_downloader.py` — 年报PDF下载+校验
- `insert_revenue.py` — PDF营收结构数据入库

## AKShare 港股数据源
- 行情: `stock_hk_spot` (新浪)
- K线: `stock_hk_daily` (新浪, 前复权)
- 利润表/资产负债表/现金流量表: `stock_financial_hk_report_em(stock, symbol, indicator="全部")`
- 分析指标: `stock_financial_hk_analysis_indicator_em` (仅年报, **仅2017-2025共9年**)
- 股息: `stock_hk_dividend_payout_em` (常有0值, 需手动补充)
- HSI月线: `stock_hk_index_daily_sina` (新浪)

### engine.py 回退计算 (2026-06-01固化)
- 当 indicators 表缺某年数据时, 从 income/balance/cashflow 原始表当面计算 24 项指标
- 税率: `financial_item_by_code("income", "004012001")` / `004011999` (避免 item_name 编码乱码)
- BPS: `总权益(equity) / shares`
- shares: `share_count(rd)` → `total_shares(carry-forward)` → `config.STOCKS.shares` 三级兜底
- DIV_YIELD: DPS=0 时设 0.0 (不分红 → 股息率 = 0%)
- 前台: `generate_report.py` showYears = `Y.slice(-15)` (标准15年)

## STD_ITEM_CODE 映射 (income表)
- 004001001 = 营业总收入
- 004025002 = 归母净利润  
- 004027002 = 基本每股收益
- 004027003 = 稀释每股收益 (A股→basic_eps, 港股→diluted_eps)
- 004012001 = 所得税费用 (A股→income_tax_expense)
- 004011999 = 利润总额/除税前利润 (A股→profit_total)

## A股 vs 港股差异 (2026-06-02 固化)
- **item_code**: A股 income/balance/cashflow 表的 item_code 为空, 全部用 item_name(英文) 查询
- **cn_map 兜底**: financial_item_by_code() 对A股通过 cn_map 将 STD_ITEM_CODE 映射为英文 item_name
- **TAX_EBT**: A股 indicators 表无此字段, engine在 indicators 路径末尾回退到 income 表当面计算
- **EPS HKD**: A股无效, build.py step_8 仅对港股检查
- **revenue_structure dim**: A股用 by_product + by_industry (不含 by_channel/by_ip)
- **早年验证**: A股借壳上市股票(如002027)2018年前数据 mismatch 仅警告不阻断

## 用户偏好
- A股涨红跌绿 (中国惯例)
- 先对齐逻辑再实施
- **先对齐需求 → 用户确认 → 再动手。绝不在用户确认前修改代码**
- 给出方案→等用户确认→执行→确认结果→下一步
- 中报数据标记"仅AKShare"来源
- Memory放项目repo可随git提交
- **CF倍数流程 (2026-06-02 固化)**:
  - 新股生成时，**必须先问用户**: "CF倍数默认15.0，是否调整？"
  - `build.py` 代码层保障: `--cf` 不再 required；未指定时默认15.0但打印 `*** CF倍数未指定，使用默认值 15.0x ***` 醒目提示
  - `--skip-cf-confirm` 可跳过提示（仅用于重生成/自动化）
  - AI 绝不在未询问用户的情况下自行决定 CF 倍数
- **Wiki 新增概念 (2026-06-28)**: `芒格格栅理论-多学科思维投资框架` — 哈格斯特朗对芒格方法全解
  - 7 大学科模型: 物理(均衡vs复杂系统)、生物(进化论/创造性破坏)、社会(多样性/自组织临界)、心理(损失趋避/系统1-2)、哲学(实用主义)、文学(分析阅读)、数学(贝叶斯/凯利/DCF)、决策科学
  - 与 VL 体系直接关联: Commentary 狐狸思维、新增标的格栅检查清单、估值实用主义

## 已知Bug模式
- **单引号Bug**: `DIV'D` 等含 `'` 的词在 JS 单引号字符串中会截断。Python `\'` 在 f-string 中输出为字面量 `'`，必须改用 Unicode `\u2019`（右单引号）如 `DIV\u2019D`
- **花括号Bug**: Python f-string 中 JS 代码的 `{` `}` 必须用 `{{` `}}` 转义

## 汇率数据
- `data/fx_rates.db` → 表 `daily_rates`（date, usd_cny, hkd_cny）
- 数据源: AKShare `currency_boc_safe`（国家外汇管理局官方中间价）
- 1994-01-01 ~ 最新交易日, 每日粒度，7973条
- 单位: 100外币兑CNY（如 usd_cny=681.76 即 1USD=6.8176CNY）
- engine.py 中港股数据需按日期查询该表换算CNY

## 页面布局 (2026-06-02 终版)
- **页面宽度**: 1360px
- **左栏**: 245px (grid-template: 245px + 1fr)
- **K线高度**: 240px, legend表 colgroup: 130px + 40px + 15col
- **统计表**: font 8px, td padding 1px 4px, 第一列 130px
- **align表第一列**: 130px
- **K线年限**: kl.filter(>=showYears[0])
- **年份数**: showYears = Y.slice(-15)

## BUSINESS 区域模板 (2026-06-02 固化 — Pop Mart 风格)
```
P1: {year}年营收{X}亿元(同比±{g}%)，归母净利润{Y}亿元，毛利率{G}%，ROE {R}%。
     {一句话业务描述(规模/覆盖/触达)}
P2: 产品：{by_product top3}；行业：{by_industry top5}
P3: 折旧率{D}%。员工{E}万人（{year}）
P4: 首席执行官：{ceo}。注册地：{inc}。{website}
```
- P1 全文渲染，禁用截断 (generate_report.py bizP.push(desc))
- P2 支持全部维度: by_ip/by_channel/by_region/by_product/by_industry
- P4 来源: config.STOCKS → ceo/inc/website → engine meta
- 新股票 config 需填 ceo/inc/website
- **年份数**: showYears = Y.slice(-15)

## AI Commentary 模板 (2026-06-02 — VL 原生叙事风格)
```
P1: {日期} — {业绩快照+同比}。{趋势判断：什么在变、为什么重要}。
P2: {深度分析：业务变化、竞争格局、财务质地}。{估值快照 vs 历史中位}。
P3: {催化剂+风险}。关注{1-2个验证信号}。
```
- 总 300-400 字，3 段连续散文，无分节标题
- 原则：不罗列数据，解释"为什么"，指出"什么在变"
