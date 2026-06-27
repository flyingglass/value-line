## TDX MCP API 参考文档

数据源：通达信官方 MCP 服务 `https://txmcp.tdx.com.cn:3001/txmcp`
接入方式：CodeBuddy → MCP connector (streamable-http)

> 数据字典基于实际 API 返回值反推，字段名即返回 JSON key。

---

## 一、港股财务数据

### 1.1 综合损益表 (利润表)

**接口**: `tdx_api_data` entry=`TdxSharePCCW.skef10_hk_cwfx` fixedTag=`1`

**参数**: `code` (5位, 如 `00700`)

**返回字段与数据字典**:

| 字段 | 单位 | 说明 |
|------|------|------|
| `截止日期` / `报告期` | date | 报告截止日期, 如 2025-12-31 |
| `开始日期` | date | 报告起始日期 |
| `营业额` | 万元 | 营业总收入 (Revenue), 对应 VL: OPERATE_INCOME |
| `经营溢利` | 万元 | 营业利润 (Operating Profit) |
| `除税前盈利` | 万元 | 税前利润 (Pretax Profit) |
| `税项` | 万元 | 所得税费用 |
| `股东应占溢利` | 万元 | 归母净利润, 对应 VL: HOLDER_PROFIT |
| `少数股东应占溢利` | 万元 | 少数股东损益 |
| `每股盈利-基本` | 元/股 | 基本每股收益, 对应 VL: BASIC_EPS |
| `每股盈利-摊薄` | 元/股 | 稀释每股收益 |
| `折旧` | 万元 | 折旧与摊销 (含负号), 对应 VL: DEPRECIATION |
| `销售费用` | 万元 | 销售及分销费用 |
| `利息支出` | 万元 | 财务费用-利息支出 |
| `应占联合营公司盈利` | 万元 | 联营/合营企业投资收益 |
| `毛利` | 万元 | 毛利 (较早年份缺失) |
| `股息` | 万元 | 已宣告股息 (部分年份) |
| `公告日期` | datetime | 财报公告日 |
| `币种` | string | 报表货币 (人民币/港币/美元) |
| `同比上一年度截止日期` | date | 同比对比期 |

**数据范围**: 实测 00700 腾讯 90 期 (2001-12-31 至 2026-03-31), 包含年报+季报+中报。

**货币**: 港股以万元为单位, 币种由 `币种` 字段标识。需与 config 中的 `currency` 不一致时做汇率换算 (如 HKD 交易价 → CNY 财报)。

---

### 1.2 资产负债表

**接口**: `tdx_api_data` entry=`TdxSharePCCW.skef10_hk_cwfx` fixedTag=`2`

**参数**: `code` (5位)

**返回字段与数据字典**:

| 字段 | 单位 | 说明 |
|------|------|------|
| `总资产` | 万元 | Total Assets |
| `非流动资产` | 万元 | Non-current Assets |
| `物业、厂房及设备` | 万元 | PPE |
| `联营公司及合营公司权益` | 万元 | Investment in Associates/JV |
| `流动资产` | 万元 | Current Assets |
| `存货` | 万元 | Inventory |
| `应收账款` | 万元 | Accounts Receivable |
| `现金及银行存款` | 万元 | Cash & Bank Deposits |
| `总负债` | 万元 | Total Liabilities |
| `流动负债` | 万元 | Current Liabilities |
| `应付账款` | 万元 | Accounts Payable |
| `短期银行及其他借款` | 万元 | Short-term Borrowings |
| `流动资产净额` | 万元 | Net Current Assets (=CA-CL), 对应 VL: WORKING_CAPITAL |
| `非流动负债` | 万元 | Non-current Liabilities |
| `长期银行及其他借款` | 万元 | LT Borrowings, 对应 VL: LT_DEBT |
| `股东权益` | 万元 | Shareholders' Equity, 对应 VL: TOTAL_EQUITY |
| `少数股东权益` | 万元 | Minority Interest |
| `股本` | 万元 | Share Capital (较早年份) |

**BPS 计算**: `股东权益 / 总股数` (注: TDX 的"股东权益"是归母权益, 与 EM indicators BPS 口径一致, 0.6% 偏差)

**数据范围**: 实测 00700 腾讯 89 期 (2001-12-31 至 2026-03-31)。

---

### 1.3 现金流量表

**接口**: `tdx_api_data` entry=`TdxSharePCCW.skef10_hk_cwfx` fixedTag=`3`

**返回字段与数据字典**:

| 字段 | 单位 | 说明 |
|------|------|------|
| `经营活动产生的现金净额` | 万元 | Operating Cash Flow |
| `资本支出` | 万元 | Capex (=购建固定资产等), 对应 VL: CAPEX_PS |
| `投资活动产生的现金净额` | 万元 | Investing Cash Flow |
| `融资活动产生的现金净额` | 万元 | Financing Cash Flow |
| `现金及现金等价物净值` | 万元 | Net Change in Cash |
| `期初/期末现金及现金等价物` | 万元 | Beginning/Ending Cash |

**数据范围**: 实测 00700 腾讯 86 期 (2001-12-31 至 2026-03-31)。

---

## 二、A 股财务数据

### 2.1 利润表

**接口**: `tdx_api_data` entry=`TdxShareCW.ph_agf10_cw_lyb` fixedTag=`00101` (报告期) / `00102` (单季度)

**返回字段与数据字典**:

| 字段 | 单位 | 说明 |
|------|------|------|
| `营业总收入` | 元 | 营业总收入 (含其他业务收入) |
| `营业收入` | 元 | 主营业务收入 |
| `营业成本` | 元 | COGS |
| `营业税金及附加` | 元 | 消费税等 (茅台此项目占比极高, 含消费税) |
| `销售费用` | 元 | Sales Expense |
| `管理费用` | 元 | Admin Expense |
| `研发费用` | 元 | R&D Expense |
| `财务费用` | 元 | Finance Cost (负值=净收入) |
| `营业利润` | 元 | Operating Profit |
| `利润总额` | 元 | Pretax Profit |
| `所得税费用` | 元 | Income Tax |
| `净利润` | 元 | Net Profit |
| `归属母公司净利润` | 元 | NP attributable to parent |
| `归属少数股东损益` | 元 | Minority Interest |
| `基本每股收益` | 元/股 | Basic EPS |
| `稀释每股收益` | 元/股 | Diluted EPS |
| `扣非净利润` | 元 | Adjusted NP (扣除非经常性损益) |
| `投资收益` | 元 | Investment Income |
| `公允价值变动净收益` | 元 | Fair Value Changes |
| `信用减值损失(新)` | 元 | Credit Loss Provisions |

**数据范围**: 实测 600519 茅台 25 期 (2020Q1至2026Q1) → **A股仅覆盖 6 年, 不如 EM 同花顺的 15 年**。

### 2.2 资产负债表

**接口**: `tdx_api_data` entry=`TdxShareCW.ph_agf10_cw_zcfzb`

待全量拉取补充字段。

### 2.3 现金流量表

**接口**: `tdx_api_data` entry=`TdxShareCW.ph_agf10_cw_xjllb` fixedTag=`00101`

待全量拉取补充字段。

---

## 三、辅助工具

### 3.1 股票代码查询

**接口**: `tdx_lookup_stock`

| 参数 | 说明 |
|------|------|
| `query` | 中文名称 (`腾讯`, `贵州茅台`) |
| `range` | `AG`=A股, `HK-GP`=港股, `MG-GP`=美股, `ZS`=指数 |

返回: 代码(`00700`/`600519`), setcode, 别名列表。

### 3.2 指标查询

**接口**: `tdx_indicator_select`

仅支持 A 股 (`rang=AG`) 的最新一期指标查询, 不返回时间序列。

---

## 四、覆盖率总结

| 市场 | 利润表 | 资产负债表 | 现金流量表 | 最早年份 | vs EM |
|------|:---:|:---:|:---:|------|------|
| **港股** | ✅ 90期 | ✅ 89期 | ✅ 86期 | **2001** (25y) | ✅ 胜出 |
| A 股 | ✅ 25期 | ✅ | ✅ | 2020 (6y) | ❌ EM 更优 |
| 美股 | 有限 | 有限 | 有限 | 待验证 | - |

### 替换策略

| 市场 | 数据源 | 说明 |
|------|--------|------|
| **港股** | **TDX 全替换 EM** | 2001-2026, 数据完美一致, 撤回 2017 截断 |
| **A 股** | **保留 EM 同花顺** | 2011-2026, 15年 > TDX 6年 |
| 美股 | 保留 EM | 待验证 TDX 覆盖 |

---

## 五、数据一致性验证

| 标的 | 市场 | 营收 | 净利润 | EPS | 年份 |
|------|------|:---:|:-----:|:---:|------|
| 00700 腾讯 | HK | 0.0% | 0.0% | 0.0% | 2017-2025 (9年) |
| 600519 茅台 | A | 0.0% | 0.0% | 0.0% | 2024 |

---

## 六、货币与单位

| 市场 | 财报单位 | 货币 |
|------|---------|------|
| 港股 | 万元 | 人民币 / 港币 / 美元 (依 `币种` 字段) |
| A股 | 元 | 人民币 |
