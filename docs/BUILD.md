# Value Line 报告生成流程（强制8步）

> 泡泡玛特(09992)作为模板标杆。新增标的必须走完完整8步，不允许跳过。

## 前置条件
- `config.py` 中标的已配置（STOCKS + analyst.commentary + business_desc）
- AKShare 网络可达（港股 Sina 源，A 股 East Money 源）

---

## 第1步：数据拉取

```bash
# 修改 config.py ACTIVE_STOCK 为目标代码
PYTHONIOENCODING=utf-8 python fetcher.py
```

**产出：** `data/{code}.db`
- spot（行情）
- kline（日K/月K 前复权）
- income（利润表，年报+中报）
- balance（资产负债表，年报+中报）
- cashflow（现金流量表）
- indicators（年度分析指标，24行基础数据）
- dividend（分红）
- meta（code, market, currency, last_fetch）

---

## 第2步：年报PDF下载

```bash
PYTHONIOENCODING=utf-8 python pdf_downloader.py
```

**产出：** `data/pdfs/{code}/*.pdf`
- 港股：港交所 hkexnews.hk
- A股：巨潮资讯 / 交易所
- 默认下载最近3年年报

---

## 第3步：MD&A 提取

```bash
PYTHONIOENCODING=utf-8 python extract_mda.py
```

**产出：** DB meta 表新增 `mda_text` 键
- 从PDF提取管理层讨论与分析
- 存入 SQLite meta 表，engine 自动读取
- engine 中 `_build_capital_structure` 读取 `mda_text` 写入 mda_text 字段

---

## 第4步：营收结构提取

```bash
PYTHONIOENCODING=utf-8 python insert_revenue.py
```

**产出：** DB revenue_structure 表
- 按产品/地区/渠道等维度拆分营收
- 写入 `revenue_structure(code, year, dim_type, dim_name, amount, pct)`
- engine 读取后写入 report_data.json 的 revenue_structure 字段

---

## 第5步：Config 检查

确认 `config.py` 中标的配置完整：

```python
STOCKS = {
    "09992": {
        "name": "泡泡玛特",         # 中文名
        "name_en": "POP MART",      # 英文名（用于文件名）
        "market": "hk",             # hk / cn
        "exchange": "SEHK",         # SEHK / SSE / SZSE
        "currency": "CNY",          # 报表货币
        "shares": 1341043150,       # 总股本（先填近似，API会覆盖）
        "shares_str": "1,341,043,150",
        "fiscal_yr_end": "12-31",   # 财年结束日
        "industry": "Consumer",     # 行业
        "analyst": {                # AI Commentary（必须）
            "commentary": [
                "标题",
                "日期+导语",
                "分析段落1",
                "分析段落2",
            ]
        },
        "business_desc": "...",     # Business 区块描述（必须）
    }
}
```

---

## 第6步：Engine 计算

```bash
PYTHONIOENCODING=utf-8 python engine.py
```

**产出：** `report_data.json`
- spot（Header 数据：price, pe, pb, div_yield, median_pe, mkt_cap 等）
- data（24行 Statistical Array 各年指标）
- kline（月K线数据）
- index_kline（指数月线，港股 HSI / A股 CSI300）
- cf_line（15×CF per share HKD）
- capital_structure（资本结构完整数据）
- current_position（3年短期资产负债）
- annual_rates（CAGR 1/3/5/10yr）
- quarterly（半年度/季度数据）
- revenue_structure（营收拆分）
- balance_summary / income_summary
- yearly_hl（年度最高最低价）
- position（估值定位）
- total_returns（% HIST.RETURN）
- analyst（AI Commentary）
- validation（交叉校验）
- meta（元数据）

**验证：** 控制台输出应显示 `年数: N | K线: M个月 | 季度/半年: K年`

---

## 第7步：HTML 生成

```bash
PYTHONIOENCODING=utf-8 python generate_report.py
```

**产出：** `report/{Name_En}.html`
- 1280px 自包含 HTML
- ECharts 5.5 CDN 引入
- 样式对齐 VL_REGION_ALIGNMENT.md

---

## 第8步：本地预览

```bash
# 启动 HTTP 服务（如未运行）
python -m http.server 8899 &
```

访问：`http://192.168.0.115:8899/report/`

验证项：
- [ ] Header 所有数值有数据
- [ ] K线图+成交量图正常渲染
- [ ] 24行统计表全部有值
- [ ] Capital Structure 数据完整
- [ ] Annual Rates 有百分比
- [ ] Quarterly Data 有数字
- [ ] Business + AI Commentary 有文字
- [ ] Revenue Structure 有营收拆分（如有）
- [ ] 页脚显示货币声明+日期

---

## 批量生成脚本

```python
import os, sys, re

stocks = ['09992', '09988', '00700', ...]
for code in stocks:
    # 切换标的
    with open('config.py', 'r', encoding='utf-8') as f:
        content = f.read()
    content = re.sub(r'ACTIVE_STOCK = "[^"]*"', f'ACTIVE_STOCK = "{code}"', content)
    with open('config.py', 'w', encoding='utf-8') as f:
        f.write(content)
    # 执行各步
    os.system(f'{sys.executable} engine.py')
    os.system(f'{sys.executable} generate_report.py')
```

---

## 数据完整性检查清单

| 步骤 | 检查项 | 确认 |
|------|--------|------|
| 1 | `data/{code}.db` 存在且 ≥200KB | [ ] |
| 2 | `data/pdfs/{code}/` 有PDF文件 | [ ] |
| 3 | DB meta 表有 `mda_text` 键 | [ ] |
| 4 | DB 有 revenue_structure 表且不为空 | [ ] |
| 5 | config 有 analyst.commentary + business_desc | [ ] |
| 6 | engine 输出年数/K线月数/季度年数 | [ ] |
| 7 | `report/{Name_En}.html` 产生 | [ ] |
| 8 | 浏览器可访问，各区域有数据 | [ ] |
