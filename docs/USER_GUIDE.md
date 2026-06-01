# Value Line 报告生成 — 用户指南

## 快速开始

```bash
python build.py <代码> --cf <倍数>
```

例：
```bash
python build.py 09992 --cf 15.0     # 泡泡玛特, CF=15
python build.py 00700 --cf 10.0     # 腾讯, CF=10
python build.py 09988 --cf 10.0     # 阿里巴巴, CF=10
```

---

## 1. 确认页

执行命令后首先看到确认页。**确认页必须出现才进入流水线。**

```
============================================================
  Value Line 报告生成 — 确认页
============================================================
  企业:      腾讯控股
  代码:      00700.SEHK
  市场:      港股(H股)
  行业:      Technology
  报表币种:   CNY
  数据年份:   2001-2026 (共26年, 默认15年。--years N 可调整)
  CF 倍数:    10.0x
============================================================
```

| 字段 | 说明 | 如何修改 |
|------|------|---------|
| 企业/代码/市场 | 从 config.py 自动读取 | 编辑 `config.py` STOCKS |
| 数据年份 | 探测 income 表全量年份 | `--years N` 指定 |
| CF 倍数 | **必填** | `--cf N` |

**确认页正确 → 自动开始 8 步流水线。**

---

## 2. 生成流程

```
确认页
  ↓
Step 0: config 检查 (name_en必填, business_desc/commentary 仅 fallback)
Step 1: 数据拉取 (AKShare → SQLite)
Step 2: 年报PDF下载 (HKEX → 本地, ≥3年)
Step 3: MD&A 提取 (PDF → mda_text, 6类关键词分类)
Step 4: 营收拆分 (年报 → revenue_structure 表)
Step 5: config 切回
Step 6: 指标计算 + mda解析 + 交叉验证
       _parse_mda_text() → BUSINESS/Commentary
Step 7: HTML 生成 (BUSINESS/Commentary 优先 mda_text → config fallback)
Step 8: 72项字段校验 + 交叉校验阻断
  ↓
report/xxx.html
```

**任何一步失败 = 阻断 = 不生成报告。** 不存在 `--force`。

---

## 3. 查看报告

生成的报告在 `report/` 目录，文件名格式：`{英文名}.html`。

例：
- `report/POP_MART.html`
- `report/Tencent_Holdings.html`
- `report/Alibaba_Group.html`

直接用浏览器打开，或通过本地 HTTP 服务：
```bash
cd report && python -m http.server 8899
# 访问 http://localhost:8899/
```

---

## 4. 常见问题

### Q: "BUILD FAILED: revenue_structure为空"
> Step 4 阻断。年报营收拆分数据未入库。需要手动执行 `insert_revenue.py` 或联系维护者。

### Q: "BUILD FAILED: 仅2份PDF, 需≥3年年报"
> Step 2 阻断。HKEX PDF 下载不足。检查网络 / stockId / 公司名繁简体匹配。

### Q: "BUILD FAILED: N/72项缺失"
> Step 8 阻断。交叉校验发现数据不一致。查看具体 mismatch 项。

### Q: 如何添加新股票？
> 1. 编辑 `config.py` 的 STOCKS 表 (name, market, exchange, currency, shares, analyst 等)
> 2. 执行 `python build.py <新代码> --cf <倍数>`
> 3. Step 4 会在第一次运行时阻断，需要手动补 revenue_structure 数据

### Q: BUSINESS 和 AI Commentary 内容从哪来？
> **零手动配置**，按优先级自动决策：
> 1. PDF 年报提取 (extract_mda.py, quality=1 时)
> 2. 财务数据自生成 (engine.py `_build_business_from_data` / `_build_commentary_from_data`)
> 3. config.py fallback (仅在前两者都失败时)
>
> 任何新股票加入系统后无需手动写 business_desc 或 analyst.commentary。

### Q: 数据年份怎么调？
> `--years N`，默认规则：>10年可用 → 15年；≤10年 → 全用。不超过实际可用年份。

---

## 5. 数据校验说明

报告中的每个数字都经过交叉验证：

| 数据类型 | 验证方式 |
|---------|---------|
| 营收 (Revenue) | AKShare income 表 ↔ 年报 PDF 拆分 |
| 净利润 (NetProfit) | indicators 表 ↔ income 表 |
| 总资产 / 净资产 | indicators ↔ balance |
| 每股营收 / 每股净资产 | 当面公式反算 (Rev÷Shares) |
| 总股数 (TOTAL_SHARES) | 三源交叉 (indicators ↔ Rev/PER_OI ↔ Eq/BPS) |
| 折旧 (Depreciation) | indicators ↔ cashflow 表 |

> ⚠️ 股息 (DPS) 和实时股价 (Price) 暂无第二数据源，标记为单源字段。

### 年份覆盖说明

报告默认显示 **15年** 数据。港股 AKShare `indicators` 表仅提供最近 9 年 (2017-2025)，但 engine 会自动回退到 income/balance/cashflow 原始表当面计算全部 24 项指标，实现 15 年全覆盖。差异来源标注：
- **三源年份** (2017-2025): indicators ↔ income ↔ PDF
- **回退年份** (2011-2016): income/balance 当面计算，shares 从 config 取
