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
- **先对齐需求 → 我确认 → 再动手。绝不在我确认前修改代码**
- 给出方案→等我确认→执行→确认结果→下一步
- 中报数据标记"仅AKShare"来源
- Memory放项目repo可随git提交

## 已知Bug模式
- **单引号Bug**: `DIV'D` 等含 `'` 的词在 JS 单引号字符串中会截断。Python `\'` 在 f-string 中输出为字面量 `'`，必须改用 Unicode `\u2019`（右单引号）如 `DIV\u2019D`
- **花括号Bug**: Python f-string 中 JS 代码的 `{` `}` 必须用 `{{` `}}` 转义

## Header 最终布局 (generate_report.py)
- **方案**: HTML `<table>` 2行, 10列, rowspan=2 值跨行居中
- **公司名**: POP MART(18px bold) + 09992.HK(9px bold) 同行, padding 5px 10px
- **标签**: RECENT/PRICE, P/E/RATIO, RELATIVE/P/E RATIO, DIV\u2019D/YLD — 9px bold #000, padding 2px 8px
- **价格值**: 18px bold 居中; **其他值**: 17px bold 居中
- **括号区**: (Trailing:xx) Row1 / (Median:xx) Row2, 9px bold, border-right 分隔
- **竖线**: `border-right:1px solid #999` 在 公司名|价格|括号区|相对PE 后
- **底部**: `border-bottom:2px solid #000`
- **教训**: CSS Grid auto-flow 不可靠 → 改用 table; 括号跨行用 transform:scaleY → 失败改用每行独立括号
