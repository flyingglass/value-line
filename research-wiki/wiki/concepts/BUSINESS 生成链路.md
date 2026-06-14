---
topic: BUSINESS 生成链路
category: 数据流
source: docs/BUILD.md, docs/DATA_VERIFICATION.md
created: 2026-06-09
---

# BUSINESS & Commentary 生成链路

## 3 级优先级 (2026-06-14 改)

```
1. 个股动态脚本 scripts/<code>/business_commentary.py::build(stock, metrics, ...)
       ↓ 14只已有, 从实时数据动态生成, 无硬编码
2. PDF 年报 MDA 提取 (extract_mda.py → engine 无条件解析)
       ↓ engine 不再 gate by quality, 直接尝试 _parse_mda_text()
3. 引擎通用自生成 _build_business_from_data() + _build_commentary_from_data()
```

**已废弃**：config.py 的 `analyst.commentary`（engine 不消费，仅 generate_report.py 以前可能引用）。
config `business_desc` 仅作为 engine 自生成时的补充信息，不独立成级。

## 动态脚本接口

```python
def build(stock, metrics, revenue_structure, years, cagr, spot):
    """
    参数: 全部从 DB/engine 实时计算
    返回: {"business": "动态业务描述", "commentary": [p1,p2,p3,p4,p5]}
    """
```

所有涉及数字的部分（营收、增长率、PE、ROE 等）通过 `ly.get("FIELD")` 从实时指标字典获取，
确保每次拉取最新财报后报告自动同步更新。

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
