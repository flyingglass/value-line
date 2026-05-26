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
engine.py → report_data.json
    ↓  
generate_report.py → report.html (自包含)
```

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
- 分析指标: `stock_financial_hk_analysis_indicator_em` (仅年报)
- 股息: `stock_hk_dividend_payout_em` (常有0值, 需手动补充)
- HSI月线: `stock_hk_index_daily_sina` (新浪)

## STD_ITEM_CODE 映射 (income表)
- 004001001 = 营业总收入
- 004025002 = 归母净利润  
- 004027002 = 基本每股收益

## 用户偏好
- A股涨红跌绿 (中国惯例)
- 先对齐逻辑再实施
- 给出方案→直接执行→确认结果→下一步
- 中报数据标记"仅AKShare"来源
- Memory放项目repo可随git提交
