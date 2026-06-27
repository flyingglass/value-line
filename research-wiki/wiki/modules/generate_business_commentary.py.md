---
module: generate_business_commentary.py
category: 代码生成
depends_on: [config.py]
lines: 376
created: 2026-06-23
---

# generate_business_commentary.py — 自动生成个股 Commentary 脚本

## 职责

根据 config 配置 + DB 数据，自动生成 `scripts/<code>/business_commentary.py`。

**核心原则**：生成的脚本完全数据驱动（`build(stock, metrics, ...)` 接口），运行时从实时 `metrics`/`revenue_structure`/`spot` 读取数据，不硬编码任何数字。

## 关键函数

| 函数 | 职责 |
|------|------|
| `generate(code)` | 主入口。读 config + DB → 生成完整的 .py 文件 |
| `INDUSTRY_MOAT` | 14 个行业的专属壁垒分析模板（P3 段） |
| `INDUSTRY_CATALYST` | 9 个行业的专属催化剂模板（P5 段） |
| `DEFAULT_MOAT` / `DEFAULT_CATALYST` | 未匹配行业时的通用模板 |

## 生成内容

| 段落 | 来源 | 说明 |
|------|------|------|
| Business | config.business_desc + revenue_structure | 核心叙事 + 产品结构 |
| P1 业绩快照 | metrics 动态 | 营收/利润/增速/毛利率/净利率 + 地区拆分 |
| P2 资金流向 | metrics 动态 | EPS/经营CF/资本支出/FCF/分红/净资产 |
| P3 业务壁垒 | 行业模板 | 行业专属壁垒分析（14 行业覆盖） |
| P4 估值锚定 | metrics + spot 动态 | PE/PB/股息率 + CF 估值区间 |
| P5 催化剂 | 行业模板 | 行业专属催化剂与风险提示（9 行业覆盖） |

## 安全策略

- **已存在 → 不覆盖**：保护手工精调的专属脚本
- **非阻断**：生成失败时 engine 回退内置通用模板（`_build_commentary_from_data`）
- **可后续精调**：生成后用户可修改任意段落

## 行业模板覆盖

```
Consumer Staples / Consumer / Technology / Energy
Metals & Mining / Media / Semiconductor / Packaging
Automotive / Home Appliances / Pharmaceuticals / Healthcare
Building Materials / Insurance / Financial Services / Utilities
```
未匹配行业 → 通用默认模板。

## 相关模块

[[build.py]] — Step 4.5 调用
[[engine.py]] — 消费生成的脚本
[[config.py]] — 读取 business_desc / industry

## 相关概念

[[BUSINESS 生成链路]]
[[新增标的流程]]
