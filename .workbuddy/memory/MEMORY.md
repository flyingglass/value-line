# Value Line 项目 — 长期记忆

## 项目
中文版 Value Line 风格投研系统：`C:/LY/Repo/llm/value-line/`，单页自包含 HTML 报告，A股+港股。
架构原则（不可违反）：① 数据全走 SQLite，engine/generate_report 零硬编码 ② AKShare ↔ PDF 自动交叉校验 ③ 数据准确性 > 覆盖度 ④ config.py 定义标的，fetcher 支持 code 参数。

## 数据流
```
fetcher.py / insert_revenue.py → data/{code}.db
extract_mda.py → meta.mda_text（PDF 按 6 类关键词分段；质量门 = categories≥3 + total≥10 + overview_pct<70% + ≥300字）
engine.py → report_data.json（mda_quality=1 → _parse_mda_text；=0 → _build_business/_commentary_from_data 纯财务自生成）
generate_report.py → report.html
```
脚本：config.py / fetcher.py / engine.py / generate_report.py / pdf_downloader.py / insert_revenue.py

## 数据源与口径
**AKShare 港股**：行情 `stock_hk_spot` · K线 `stock_hk_daily`(前复权) · 三表 `stock_financial_hk_report_em` · 分析指标 `stock_financial_hk_analysis_indicator_em`(仅年报 **2017-2025**) · 股息 `stock_hk_dividend_payout_em`(常有 0 值) · HSI `stock_hk_index_daily_sina`
**engine.py 回退**：indicators 缺年 → 从三表当面算 24 项；税率用 item_code `004012001`/`004011999`（避开 item_name 乱码）；BPS = equity/shares；shares 三级兜底 share_count → total_shares → config.STOCKS.shares；DPS=0 → 股息率 0
**STD_ITEM_CODE（income）**：004001001 营业总收入 · 004025002 归母净利 · 004027002 基本EPS · 004027003 稀释EPS(港股) · 004012001 所得税 · 004011999 利润总额/除税前
**A股 vs 港股**：A股 item_code 为空，全用 item_name（**实测为中文**：`一、营业总收入`、`其中：营业收入`、`其中：营业成本`、`归属于母公司所有者的净利润`，前缀必须原样匹配）；revenue_structure 按标的实测（600519 含 by_channel + by_product + by_region）；TAX_EBT 走 indicators → income 回退；EPS HKD 仅港股校验；借壳股早年 mismatch 仅警告不阻断
**汇率**：`data/fx_rates.db` → `daily_rates(date, usd_cny, hkd_cny)`，源 AKShare `currency_boc_safe`，**单位为 100 外币兑 CNY**（hkd_cny=86.5 → 1HKD=0.865CNY），港股按日期换算

## 数据口径陷阱
- 🔴 dividend 表只存「年度分红」一笔，**不含中期**：600519 2025 年度 28.02 vs 真实全年 51.95（股息率 2.17% vs 4.02%）→ 算股息率前必须查该年中期分红并手工相加
- 单季拆分：Q1 用当年 Q1 累计值本身，**不可**用 Q1累计−上年Q4累计（会得负值垃圾）
- 🔴 **求 TTM（近四季）不可把 income 表四个累计值相加**——Q2/Q3/Q4 是**累计口径**，相加会高估约 2.3 倍（002209 实测：错算得 TTM 45.98 亿，真值 20.13 亿）。正确：`TTM = 上年年报 + 本年累计 − 上年同期累计`。凡比值型指标（合同负债/TTM 营收等）必先自检分母量级
- 茅台「营业总收入」含财务公司利息收入（与营业收入差约 15 亿）；毛利率用**营业收入**，费用率/净利率可用营业总收入，须同口径

## 页面布局 / 模板
- 宽 1360px，左栏 245px；K线高 240px；统计表 font 8px、第一列 130px；showYears = `Y.slice(-15)`
- BUSINESS 四段：P1 营收/归母/毛利率/ROE + 一句业务描述（全文渲染不截断）；P2 产品/行业维度；P3 折旧率/员工；P4 CEO/注册地/官网（config 需填 ceo/inc/website）
- Commentary 三段 300-400 字散文，无分节标题，解释「什么在变」而非罗列数据

## 用户偏好（行为准则）
- A股涨红跌绿（中国惯例）
- 🔴 **先对齐需求 → 用户确认 → 再动手；绝不在确认前修改任何文件**——含 skill md / 文档 / 配置，不只代码。纯问答场景只回答不动文件，改进想法写成提案等点头（曾两次答完问题顺手改 skill md 被当场指出）
- 节奏：给方案 → 等确认 → 执行 → 确认结果 → 下一步
- 中报数据标「仅 AKShare」来源
- CF 倍数：新股必须先问用户「默认 15.0x 是否调整」；build.py 未指定时默认 15.0 并打印醒目提示；AI 不得自行决定。**PB 法同理，倍数必须用户拍**（2026-09-23 金域医学：CF15x 估值线失真 → 用户改 PB 法 + 用户指定 2.0x）
- 估值方法/倍数写在 db meta（`valuation_method` / `pb_multiplier` / `cf_multiplier`），engine 从此读取；build.py `--method pb --pb 2.0` 会写入 meta

## 新增标的速查（VL 流水线）
```
① cninfo 查 org_id: POST http://www.cninfo.com.cn/new/information/topSearch/query  keyWord=<简称>
② config.py 加 STOCKS + 切 ACTIVE_STOCK（注意 engine.py 只读 ACTIVE_STOCK，直接命令行跑脚本会串标的！）
③ fetcher.py <code> → pdf_downloader.py <code>（两者自带 pop 代理，直接跑即可）
④ extract_mda.py <code>
⑤ scripts/<code>/insert_revenue.py（金额统一为百万元；pct 由金额自算避免手工误差；单一取值维度不入库）
⑥ scripts/<code>/business_commentary.py（build(stock, metrics, revenue_structure, years, cagr, spot)）
⑦ engine.py → generate_report.py   （或全程 build.py <code> --method pb --pb 2.0）
```
CN 补充：此机器上 eastmoney 直连必失败，**但 fetcher/pdf_downloader 自带去代理、直接跑即可**；手搓 `python -c` 调 AKShare 会 ProxyError，不要因此怀疑数据源。即时行情/总股本可用 `qt.gtimg.cn/q=sh<6位>`（GBK → iconv）。

## 引擎已知不修的行为（勿改 engine，只标注）
- `_compute_ttm_eps` 要求最新年度 EPS > 0，否则跳过 TTM 滚动 → **亏损股**必然出现 Header.P/E、Header.EPS TTM、Stat.PE_AVG（仅盈利年份有值）、PE_RELATIVE、CAGR.earnings 全数 gap，属正常（2026-09-23 002209 与 603882 实测各 4-5 个 gap）
- `PER_NETCASH` 是 VL 口径「扣非净利 + 折旧」，**不是**现金流量表经营现金流；写评论时须分开标注
- A 股 `metrics.HOLDER_PROFIT` / `BASIC_EPS` 为**扣非**口径，与年报归母差异可能很大（亏损年尤甚）

## Wiki 落库规范
**四件套**：① 新页（YAML frontmatter：topic/category/created/sources，sources 带完整 URL）② `research/index.md` 加条目 + 更新首行「最后更新：」③ `research/log.md` 末尾追加条目（末写「触及页面：」）④ 跑 `scripts/generate_wiki_index.py` 重建
**参见双向**：新页写 `## 参见`，同时反向补齐被引页，否则 `scripts/wiki_lint.py` 报「交叉引用缺口」
**🔴 页面禁止过程注脚 / 对账叙述**：正文只放**当前有效**结论与名单，家数只写在标题/计数行，口径只在表内逐行；变更一律记 log.md。**页面只被覆盖，只进不改的是 raw**（用户已三轮同类诉求，病根是每轮把「这次改了什么」追加进页面 → 越滚越长且新旧家数自相矛盾）
**🔴 概念/框架页立页门槛（2026-09-23 用户驳回教训）**：①**单一信源（尤其二手/AI 生成的雪球帖）不配撑起一个框架页**——从一篇垃圾帖归纳出的"框架"必然空泛（常识复述、无阈值无反例），且会把辨伪过程当正文，违反「页面禁止过程注脚」；此类产出一律**压缩成一行判据并入对应案例页**，不单独成页。②框架页必须可执行（阈值/反例/边界），做不到就别立。③行业规模数字属**案例页/行业页**，塞进概念页＝内容漂移。④攒够 2-3 个真实案例再考虑归纳框架。
**归档类名单独立成页**：主表只留当前有效集合。先例 `广州待选池-依据存档.md`(2026-09-17)、`广州名单-已划掉（134 家）.md`(2026-09-19)；拆表时页内位置引用（如「第五节」）须改为「见依据存档」；节号跳号**不重编号**
**证据等级**：🟢 观测 · 🟡 推算（交代假设+给区间）· 🔴 不可识别；被推翻的推导保留在「存证」节不删
脚本：`.venv/Scripts/python.exe scripts/wiki_lint.py`（健康检查）/ `scripts/generate_wiki_index.py`（重建）

## 已知 Bug 模式
- **单引号**：JS 单引号字符串里 `DIV'D` 会截断 → 改用 Unicode `\u2019`
- **花括号**：Python f-string 里的 JS `{ }` 必须写 `{{ }}`
- 🔴 **bash 双引号 + `python -c` 写 Markdown**：反引号被当命令替换；若其中是**真实存在的相对路径**（如 `学股/广州/xxx.md`），sh 会**把该 md 当脚本执行**，`> **来源**：` 行触发重定向凭空造垃圾文件。
  规避：多行文本先用 Write 工具落文件，或 python 代码用**单引号**包裹；检测：`git status` 冒出 `??` 异常文件名 → 立刻用 python `os.remove` 精确删除
