# Value Line 阅读指南

## 报告结构

每份报告包含以下核心模块：

### 1. Business（业务描述）
描述公司核心业务、主要利润来源、行业地位。

**数据源优先级**：`scripts/<code>/business_commentary.py` > PDF MDA 提取 > engine 自动生成

### 2. AI Commentary（4 段 VL 风格分析）

| 段 | 标题 | 内容 |
|----|------|------|
| 段1 | 业绩快照 | 营收、净利润、EPS + 解释"为什么变化"（毛利率/费用/结构因素） |
| 段2 | 每股资金流向 | 钱从哪来（主业 vs 非经营性贡献）、花到哪去（CAPEX vs 分红 vs 净留存） |
| 段3 | 业务质地 + 估值 | 业务结构、财务质地、PE/PB vs 历史中位数 |
| 段4 | 转折点检测 + 验证信号 | 4 项反转信号 + 可操作验证指标 + 管理层展望 |

**数据源优先级**：`scripts/<code>/business_commentary.py` > PDF MDA 提取 > engine 自动生成

### 3. 23 行指标表
Value Line 标准格式，15 年历史 + CAGR + 预测（仅历史，不做预测）

## 每股资金流向公式

```
op_eps = Row1(每股营收) × Row12(营业利润率)
nonop  = Row3(EPS) - op_eps
net    = Row2(每股现金流) - Row5(每股CAPEX) - Row4(每股股息)
```

- `net > 0` → 现金流充裕，自给自足
- `net < 0` → 入不敷出，消耗存量现金储备

**无需行业判断，统一会计恒等式框架。**

## 转折点检测（4 项）

1. **营收增速反转**：1yr 增速 > 0 AND 5yr CAGR < -10%
2. **利润率反转**：毛利率 1yr 改善 AND 3yr 整体走低
3. **现金流方向反转**：净留存从正转负或反之
4. **ROE 反转**：1yr 变化 > 0 AND 3yr 均值 < 0

## 个股脚本目录

```
scripts/<code>/
├── business_commentary.py  # 自定义 Business + AI Commentary
├── metric_adjustment.py    # 自定义 24 项指标计算 (EPS调整、减值口径等)
├── insert_revenue.py       # 营收结构数据
├── diag_outlook.py         # PDF outlook 提取诊断（按需）
```

通用工具放 `scripts/` 根目录。

## 引擎调用链

```
per-stock script → PDF MDA (quality=1) → engine 内置通用逻辑
```

每层有 fallback，保证所有个股都能生成基础报告。
