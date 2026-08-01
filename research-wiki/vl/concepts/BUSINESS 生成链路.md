---
topic: BUSINESS 生成链路
category: 数据流
source: docs/BUILD.md, docs/DATA_VERIFICATION.md
created: 2026-06-09
updated: 2026-06-23
---

# BUSINESS & Commentary 生成链路

## 3 级优先级 + 自动生成 (2026-06-23 改)

```
1. 个股动态脚本 scripts/<code>/business_commentary.py::build(stock, metrics, ...)
       ↓ 手工精调 或 自动生成（Step 4.5），从实时数据动态生成，无硬编码
2. PDF 年报 MDA 提取 (extract_mda.py → engine 无条件解析)
       ↓ engine 不再 gate by quality, 直接尝试 _parse_mda_text()
3. 引擎通用自生成 _build_business_from_data() + _build_commentary_from_data()
```

**自动生成机制 (2026-06-23 新增)**：
- `generate_business_commentary.py` 在 Step 4.5 自动生成脚本
- 14 个行业专属 moat 模板 + 9 个行业催化剂模板
- 生成的脚本 100% 数据驱动，运行时从 metrics/revenue_structure/spot 动态读取
- 已存在不覆盖（保护手工精调版本）

**已废弃**：config.py 的 `analyst.commentary`（engine 不消费，仅 generate_report.py 以前可能引用）。
config `business_desc` 仅作为自动生成时的 Business 叙事来源，不独立成级。

## 动态脚本接口

```python
def build(stock, metrics, revenue_structure, years, cagr, spot):
    """
    stock: {"name": "腾讯控股", "market": "hk", ...}
    metrics: {"2025": {"OPERATE_INCOME": 7200.0, "BASIC_EPS": 24.15, ...}, ...}
    revenue_structure: {"by_product": [{"name":"...", "pct":82.4}], ...}  # 注意: 是 dict!
    years: ["2011","2012",...,"2025"]
    cagr: {"sales": {"1yr": 10.2, "3yr": ...}, ...}
    spot: {"pe": 15.9, "pb": 2.96, "div_yield": 1.19, ...}
    返回: {"business": "...", "commentary": [p1,p2,p3,p4,p5]}
    """
```

⚠️ `revenue_structure` 是 dict，需 `isinstance(dict)` 检查后用 `.items()` 遍历或 `.get("dim_key", [])` 取值，不可直接切片。

## MDA 提取流程

```
extract_mda.py → PDF 文本 → _is_narrative() 过滤
    ↓ quality: categories ≥ 2 + total ≥ 6 + overview < 85%
    ↓ 写入 meta.mda_text + meta.mda_quality + meta.mda_extracted_year
    ↓ build.py step_3: PDF 年份 > 已提取年份 → 强制重提
engine.py
    ↓ _parse_mda_text() 无条件尝试解析
    ├─ OK → business_summary + mda_sections
    └─ None → 自生成
```

## 涉及模块

[[engine.py]]
[[extract_mda.py]]
[[build.py]]
[[generate_report.py]]
[[generate_business_commentary.py]]

## 参见

[[8 步流水线]] · [[vl/index.md]] · [[vl/log.md]] · [[vl/modules/engine.py.md]] · [[vl/modules/extract_mda.py.md]]
[[vl/log.md]] · [[vl/modules/generate_business_commentary.py.md]]
