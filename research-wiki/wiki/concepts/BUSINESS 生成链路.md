---
topic: BUSINESS 生成链路
category: 数据流
source: docs/BUILD.md, docs/DATA_VERIFICATION.md
created: 2026-06-09
---

# BUSINESS & Commentary 生成链路

## 4 级 Fallback

```
1. 个股专属脚本 (scripts/<code>/business_commentary.py)  ← 最高质量
       ↓ fallback
2. PDF 年报 MDA 提取 (extract_mda.py, quality=1)
       ↓ fallback
3. 引擎内置通用逻辑 (engine.py _build_xxx_from_data)
       ↓ fallback
4. config.py 静态配置 (business_desc / analyst.commentary)
```

## MDA 提取流程

```
extract_mda.py → PDF 文本 → _is_narrative() 过滤财务数据句
    ↓ scoring-based classify_sentences()
    ↓ 质量门：categories ≥ 3 + total ≥ 10 + overview < 70% + ≥ 300 chars
    ↓
    ├─ quality=1 → mda_text（按【章节】分段）
    └─ quality=0 → build_mda_from_data()（数据动态生成）
         ↓ SQLite meta.mda_text + meta.mda_quality
engine.py
    ↓ _parse_mda_text() if quality=1
    ├─ OK → business_summary + mda_sections → 报告使用
    └─ None → _build_business_from_data() [自生成]
             → _build_commentary_from_data() [自生成]
```

## BUSINESS 模板 (Pop Mart 风格，4 段式)

```
P1: 年份+营收+净利润+毛利率+ROE+一句话业务描述
P2: 产品/行业/渠道/IP/地域营收结构（从 revenue_structure 表读取）
P3: 折旧率+员工数
P4: CEO+注册地+网站
```

## AI Commentary 模板 (3 段叙事体)

VL 官方原则：不罗列数据，解释"为什么"——why the numbers are what they are。

```
P1: 业绩快照 + 趋势判断
P2: 深度分析（业务变化、竞争格局、财务质地）+ 估值快照
P3: 催化剂+风险总结 + 验证信号
```

## 涉及模块

[[engine.py]]
[[extract_mda.py]]
[[generate_report.py]]
