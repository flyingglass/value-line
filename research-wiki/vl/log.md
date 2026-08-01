# 操作日志

## [2026-07-31] build | 批量新增 5 标的 + 1 待补

- 康臣药业 (01681)、海天味业 (603288)、万华化学 (600309)、中国平安 (601318)、海康威视 (002415) — 完整 VL + Reading 报告
- 拼多多 (PDD) — config + DB 就绪，stocklight 无 20-F 收录，暂放弃
- 川恒股份 (002895) org_id 修正：gssz1002895 → 9900032889
- research/ synthesis 新增《枪炮、病菌与钢铁》投资终极因框架

## [2026-07-30] lint | 全站健康检查 — 0 断链 0 孤儿

VL 侧 36 页面全部健康。research/ 侧发现 1 孤儿已修复。

## [2026-07-24] lint | 扫尾 — 移除 raw/ 分析文章后确认全站健康

### 状态
36 页面 · 0 断链 · 0 孤儿

## [2026-07-24] lint | VL 侧健康检查 — P0/P1 修复

### 修复
- **P0** `vl/index.md`：移除 `set_baba_meta.py` 条目（模块页不存在，属历史残留死链）
- **P1** `vl/index.md`：收录孤儿页面 `个股脚本标准`（concepts/ 下存在但未入索引）
- 更新 index.md 日期至 2026-07-24

### 已知遗留
- `raw/.../哈格斯特朗_...格栅理论.md` 引用 `[[articles/concepts/arthur-increasing-returns]]`（旧 wiki 页名），raw/ 只进不改不动

### 状态
36 页面 · 0 断链 · 0 孤儿

## [2026-07-24] lint | raw/research/articles/ 改名后 VL 侧断链修复

### 修复
- `vl/concepts/Arthur-收益递增与涌现.md`：raw 源存档引用 `arthur-increasing-returns-emergence` → `阿瑟-收益递增与涌现`

### 状态
全站 0 断链

## [2026-07-17] lint | 全站链接校验 — 4 处残留断链修复

### 修复
- 2x `munger-mental-models-analysis` 残留断链 → `芒格格栅理论-多学科思维投资框架`
- `安琪酵母/overview.md` 旧代码前缀修复
- `research/index.md` 跨命名空间链接修复

### 状态
103 页面 · 411 链接 · 0 真实断链 · 0 孤儿


## [2026-07-17] lint | Wiki P1 标的目录全面补全

### 新增 13 个标的页面
- **泡泡玛特**: thesis / industry-chain / operating-metrics / research-reports (4页)
- **润泽科技**: thesis / industry-chain / research-reports (3页)
- **人福医药**: thesis / industry-chain / operating-metrics / research-reports + raw/ (5项)
- **安琪酵母**: operating-metrics / research-reports + raw/ (3项)
- **TCL中环**: operating-metrics (1页)

### 触及 Wiki 页面
- [[research/index.md]] — 收录全部 13 个新页面
- [[research/log.md]] — 本次

---

## [2026-07-17] lint | Wiki 健康检查 — WIKI-SCHEMA + vl/synthesis/ + 断链修复

### 修复
- 创建 `WIKI-SCHEMA.md`：完整 Schema 配置（双轨目录结构 + 5 类页面模板 + 交叉引用规则 + 工作流）
- 创建 `vl/synthesis/` 目录（宪法要求但未建）
- 修复 research/index.md 断链 + 孤儿收录

### 触及 Wiki 页面
- [[WIKI-SCHEMA.md]] — 新建
- [[research/index.md]] — 断链修复 + 孤儿收录

---

## [2026-06-25] ingest | Arthur 收益递增与涌现 — 概念页创建 + 三层涌现补充

### 摄入内容
- 对话中探讨 W. Brian Arthur 复杂经济学中收益递增（increasing returns）与涌现（emergence）的关系
- 原始资料：Arthur 1999 *Science* 论文原文引用（web_search → web_fetch PDF 验证）
- 存为 `raw/research/articles/2026-06-25-arthur-increasing-returns-emergence.md`

### Wiki 产出
- `vl/concepts/Arthur-收益递增与涌现.md` — 新建概念页
  - Arthur 原文引用：涌现定义 + 正反馈主导论（1999 Science）
  - 四种自强化机制（1996 HBR）
  - **三层涌现分类**（结构涌现 / 行为涌现 / 技术涌现）— AI 推演框架，基于 Arthur 不同著作串联
  - 两者的因果链条：正反馈 → 涌现
  - 与投资框架的衔接

### 补充更新（11:52）
- raw 第四部分展开三层涌现的完整论述（原有仅一行简述）
- wiki 概念页新增 §2「涌现的三个层次」，含表格和 El Farol Bar 详解

### 交叉引用
- `raw/research/articles/投资框架-复杂经济学指导手册.md` §1.1 添加交叉引用链接

### 页面更新
- `vl/index.md` — 新增条目
- `vl/log.md` — 本次
- `research/log.md` — 本次

---

## [2026-06-23] feat | business_commentary.py 自动生成 — build.py Step 4.5

### 动机
新增标的时需要手写 `business_commentary.py`（5段 Commentary + Business 描述），耗时且容易遗漏关键段落（现金流分析等）。14 个行业的壁垒/催化剂模板重复手写。

### 改动
- **新建** `scripts/generate_business_commentary.py`（376行）：
  - 从 config.business_desc + DB revenue_structure 生成 Business 描述
  - P1/P2/P4 纯数据驱动公式（营收/现金流/估值）
  - P3/P5 行业专属模板：14 行业 moat + 9 行业 catalyst
  - 未匹配行业 → 通用默认模板
  - 已存在不覆盖（保护手工精调版本）
- **修改** `scripts/build.py`：
  - 新增 `step_4_5_auto_gen_commentary()` — Step 4 后自动调用生成器
  - 失败不阻断 → 回退 engine 内置 `_build_commentary_from_data()`

### 效果
- 新增标的无需手写 commentary，build.py 自动生成初稿
- 后续可选精调 P3（壁垒）和 P5（催化剂）段落
- 安琪酵母 (600298) 测试通过：72 ALL PASS，Business + Commentary 来自自动生成脚本
- `新增标的流程` 从 7 步简化为：config → build --fetch → insert_revenue → auto-gen commentary → reading → index

### 触及 Wiki 页面
- [[generate_business_commentary.py]] — 新建模块页
- [[BUSINESS 生成链路]] — 新增自动生成级别
- [[8 步流水线]] — 新增 Step 4.5
- [[build.py]] — 新增 step_4_5_auto_gen_commentary
- [[新增标的流程]] — 简化步骤 5（自动生成）
- [[index.md]] — 新增模块条目
- raw/2026-06-23-business-commentary-auto-gen.md — 原始设计记录

---

## [2026-06-23] add | 安琪酵母 (600298) VL 报告 + 专属 Commentary

新增标的安琪酵母：
- CF=15.0x，A股（SSE），Consumer Staples
- 营收结构：酵母71%/食品原料13%/制糖8%/包装2%/其他5%
- 地区：国内58.6%/国外40.9%（海外毛利率32%远高国内20%）
- 专属 `business_commentary.py`：5段数据驱动分析
- 阅读报告：`report/reading/600298.md` + `.html`
- index.html 更新：50 标的 / 18 行业

---

## [2026-06-23] fix | 颐海国际 (01579) 报告重建 + index.html 更新

颐海国际重新拉取数据（双源：AKShare + TDX），build.py 重建 + 阅读报告重生成。
7 个数据缺口（PE_AVG/股息率等港股 AKShare 未提供）非拉取可修复，CrossCheck 54/60。

---

## [2026-06-20] ingest | fetcher.py A 股 DPS 自动补入预案流程

### 改动
- `fetcher.py`：新增 `_extract_dps_from_pdf()` — 当巨潮 API 缺少最新年报分红时，从年报 PDF 提取预案 DPS
- 正则 `每\s*10\s*股\s*派[^\d]*?(\d+\.?\d*)\s*元` 兼容「派发现金红利」「派息」「派发」
- 更新 wiki: `fetcher.py.md` 写入 DPS 完整流程

## [2026-06-19] fix | 新增标的流程：行业中文 + 前台交互输入 CF/PB

### 改动
- `vl/concepts/新增标的流程.md`：
  - Step 1 强调 **industry 必须用中文**
  - Step 2 修正为 `build.py <code> --fetch`（去掉 `--cf N`），说明必须前台交互运行
  - 补充步骤 7（`generate_index.py` 重建索引）
  - 常见故障表新增"REFUSED: 未提供有效CF倍数"条目（根因：后台无 stdin）

### 来源
- TCL中环 002129 新增过程踩坑：后台运行 build.py 导致 `input()` EOFError，且 industry 初始用英文 `"Photovoltaic"`

### 触及 Wiki 页面
- [[新增标的流程]]

## [2026-06-19] refactor | 投资框架指导手册移至 research/ 命名空间

### 改动
- `vl/投资框架-复杂经济学指导手册.md` → `raw/research/articles/投资框架-复杂经济学指导手册.md`
- `vl/index.md`：更新链接指向新位置
- `research/index.md`：新增投资框架条目

### 触及 Wiki 页面
- [[../raw/research/articles/投资框架-复杂经济学指导手册]]
- [[index.md]] (wiki + research)

---

## [2026-06-18] ingest | 投资框架知识体系导入

### 摄入内容
- 新建 `raw/research/articles/投资框架-复杂经济学指导手册.md` — 四本著作 + 外部文章 + 访谈的整合框架
- 新建 `raw/research/articles/投资框架-参考著作.md` — 12 项原始资料来源记录（4 核心著作、2 辅助、3 论文、1 公众号、2 访谈）
- 更新 `vl/index.md` — 新增「投资框架」章节

### 来源
- 4 本核心著作：复杂经济学(阿瑟) / 竞争优势(格林沃尔德) / 技术革命与金融资本(佩蕾丝) / 柏基投资之道(李正)
- 辅助：第五消费时代(三浦展)、反脆弱(塔勒布)
- 论文：Bessembinder(2018)、Arthur(1994)×2
- 外部：庶人投资笔记公众号(2026-06-17)、James Anderson 访谈×2
- 所有原文存放于 IMA 知识库「投资」(kb_id: 7446496324648762)

### 框架结构
手册七部分：柏基三大基石 → 竞争优势壁垒检验 → 三段式估值(含PEG转折点核心) → 三周期叠加 → 七步决策流程 → 极端赢家三条件 → 酒吧问题与长期主义

---
## [2026-06-17] refactor | 项目结构重构：全部 .py 移入 scripts/ + 投研 wiki 框架

### 改动

**根目录清理**：11 个 .py 文件全部移入 `scripts/`，根目录不再有源码。

**路径系统修复**：
- `config.py` BASE_DIR 上移一层 → 项目根
- `build.py` BASE 上移一层 + 子进程调用加 `scripts/` 前缀 + `sys.path` 双轨
- `engine.py` 3 处 `scripts/<code>/` 引用去前缀（因自身已在 scripts/ 内）
- `extract_mda.py` `sys.path(".")` → 绝对路径
- `generate_report/generate_reading/generate_index/list_refs` BASE_DIR 上移一层
- `tdx_client.py` `.env` 路径上移一层

**投研 wiki 框架初始化**：
- `research-wiki/research/` 命名空间（index.md / log.md）
- `research-wiki/raw/research/` 投研原始资料归档
- `CODEBUDDY.md` 升级为投研系统宪法，VL 明确为子功能

**修复**：`engine.py` `_safe_float()` 容错 spot 数据中 pe/pb/div_y 可能为字符串 "-"

**归档**：`v1.0.0` tag 打在 `72e46b7`（纯净 VL 系统）

### 验证

`python scripts/build.py 09992 --cf 15.0` → 8步全通过，HTML 正常生成 (88KB)。

### 触及 Wiki 页面
- [[项目目录结构]] — 新建概念页
- [[index.md]] — 新增条目
- raw/2026-06-17-scripts-refactor.md — 原始记录

## [2026-06-15] feat | 心动公司 (02400) + business_commentary.py 定制模式

新增标的 + 确立 commentary 定制最佳实践：
- **不用 config.py analyst**（PDF 粗提取质量差），用 `scripts/<code>/business_commentary.py`
- 参照 `scripts/09992/business_commentary.py`：`build()` 函数返回 `{"business": ..., "commentary": [p1..p5]}`
- p2 必须含完整现金流分析：每股经营现金流 → 四大去向（资本支出/营运资金/分红/净留存）

## [2026-06-15] fix | 美的集团 HTML 本地丢失 — 中文文件名 + index.html 同步

**现象**：`report/美的集团.html` git 中存在但本地磁盘被删除，index.html 看似正常但不含新标的。

**根因**：中文文件名在某些操作（如 IDE 重载 / git 操作）下本地文件消失，但 git 历史保留。非代码问题，属环境偶发。

**修复**：`build.py 000333 --cf 15.0` 重新生成 + `generate_index.py` 刷新 index，确认 index.html 卡片链接正确（`美的集团.html` + `reading/000333.html`）。

**教训**：新增标的后务必 `generate_index.py` 重建索引，且验证 report/ 下文件实际存在。

## [2026-06-15] feat | 美的集团 (000333) 新增标的 + build 流水线双修复

**新增标的**：美的集团 CF=15.0x, A股, 家电行业, 15年数据, 72/72 ALL PASS。
- `config.py`：org_id=`9900005965`（通过 `http://www.cninfo.com.cn/new/data/szse_stock.json` API 查询获得），代码 `gssz` 前缀不适用所有 SZSE 股票
- `scripts/000333/insert_revenue.py`：营收结构（暖通空调/消费电器/机器人）

**流水线修复**：
1. `build.py` `_need_fresh_prices`：回溯 `range(3)`→`range(5)`，覆盖长周末（周一查不到周五K线）
2. `build.py` + `fetcher.py`：子进程检测 `"拉取完成"`→`"FETCH_OK"`（ASCII 标记），避免编码乱码导致误判失败

## [2026-06-14] refactor | 报告文件名统一中文 + 删除英文旧文件

`generate_report.py` / `generate_index.py` / `build.py` `_report_path`：文件名从 `name_en` 改为 `name`（中文），如 `泡泡玛特.html`。删除全部 40 个英文旧报告，index 同步刷新。

## [2026-06-14] fix | AI Commentary 先左后右 + 09992品类占比动态读取 + FOOTNOTES大写

- Commentary 分栏：CSS `column-count` → JS `flex` 手动分半，左栏填满再右栏
- 09992 BUSINESS 品类占比从 `revenue_structure.by_product` 动态读取
- `generate_report.py` BUSINESS 不再自动拼 IP/渠道/地域/产品，全权交还脚本

## [2026-06-14] refactor | BUSINESS 职责分离 — 模板不再自动拼接收拆分

**问题**：`generate_report.py` 自动从 `revenue_structure` 拼 IP/渠道/地域/产品到 BUSINESS 段落，与 `business_commentary.py` 生成的内容重复。09992 的品类描述和 Revenue 区的 IP/渠道/地域/产品明细出现三重冗余。

**修复**：
- `generate_report.py`：移除 IP/渠道/地域/产品自动拼接（L428-438），BUSINESS 内容全权交还 `business_commentary.py`
- 通用模板升级：21 只股票新增从 `revenue_structure` 读取最相关维度（by_product > by_channel > by_region）加入 BUSINESS
- 09992：品类描述（毛绒/手办/MEGA/衍生品）+ 财务快照，不再重复 Revenue 数据
- 新增 `by_product` 维度到 09992 的 `insert_revenue.py`（2025 年报 P29 品类数据）

**职责划分**：
- BUSINESS → `business_commentary.py` 全权控制
- Revenue Structure → `insert_revenue.py` 独立展示
- 模板仅附加折旧率/员工数/CEO/注册地等通用信息

**触及 Wiki 页面**：
- [[generate_report.py]] — 更新 BUSINESS 渲染逻辑
- [[个股脚本标准]] — 更新职责划分

## [2026-06-14] fix | 新增股票流程补全 — index.html 自动刷新

**问题**：百润股份 (002568) 新增后未更新 `report/index.html`。

**修复**：运行 `generate_index.py` 重新生成索引（39 标的 15 行业）。新增股票流程已写入 [[个股脚本标准]] 第 4 步强制要求。

## [2026-06-14] fix | f-string 百分号转义错误 — %25 → %

**问题**：手写 business_commentary.py 时误用 `%25`（URL 编码）替代百分号，f-string 原样输出 `80%25`。

**根因**：Python f-string 中 `%` 是普通字符，无需转义。误将 `%25` 当作 `%` 的转义形式。

**修复**：`%25` → `%`，仅 002568 和 NVDA 两只手写脚本受影响。batch 生成的 21 只不受影响（模板用 `%%` 经 `.format()` 正确输出 `%`）。全局 38 文件检查 0 残留。

## [2026-06-14] fix | 新增股票三修复 — 确认页历史PE/PB + 流式输出防卡死 + 6位代码兼容

**问题**：
1. **确认页不显示历史PE/PB参考**：`_get_hist_valuation_ref` PE_AVG 分支被 `years`（BPS/EPS/K线交集）阻断 — A股 raw indicators 字段名不同（`basic_eps` 非 `BASIC_EPS`），交集为空 → PE_AVG 永不执行
2. **拉数据/年报卡死无反馈**：`_run` 用 `capture_output=True` — 全程静默，用户看到白屏 5+ 分钟
3. **6位代码兼容**：`_set_active` 正则 `[0-9]+` 不匹配 NVDA；PDF 年份检测 `\d{5}` 不匹配 6 位 A 股代码

**修复**：
- `build.py` `_get_hist_valuation_ref`：CF 的 PE_AVG 分支独立运行，不再依赖 BPS/EPS 交集（`if method == "cf" and years:` → `if method == "cf":`）
- `build.py` `confirm_and_build`：历史 PE/PB 参考移到 `if cf_multiplier is None:` 外部，**始终展示**
- `build.py` `_run`：添加"运行中..."进度提示；超时调整：fetcher 300→600s, generate_report 30→60s
- `build.py` `_set_active`：正则 `[0-9]+` → `[^"]*` 匹配任意代码格式
- `build.py` PDF 年份检测：`\d{5}` / `\d{4,6}` → `[A-Za-z0-9]+` 兼容字母+数字代码

**关键原则**：**确认页必须始终出现**，显示历史 PE/PB 参考。`--cf`/`--pb` 传参时不弹交互框但必须展示参考数据。

**验证**：A/H/美股 14/14 测试全通过。

**触及 Wiki 页面**：
- [[build.py]] — 更新确认页 + _run 流式输出
- [[8 步流水线]] — 强调确认页展示规则

## [2026-06-14] feat | 全量脚本标准化 — 38只全部对齐09992四件套

**动机**：09992 (泡泡玛特) 的 scripts 目录是唯一完整的标准：4 件脚本各司其职。其余 37 只股票缺失不等。

**标准四件套**：

| 脚本 | 作用 | 实现方式 |
|------|------|---------|
| `business_commentary.py` | 动态 Business + 5 段 AI Commentary | `build(stock, metrics, revenue_structure, years, cagr, spot)` 数据驱动 |
| `insert_revenue.py` | 营收拆分数据入库 | 手工维护年报分业务/分渠道/分地区数据 |
| `metric_adjustment.py` | EPS 非经常性调整 | A股 CAS扣非 / 港股探 FV+FX+GS+IM+OG / 美股直通 |
| `extract_business.py` | PDF 提取员工数等补充信息 | pdfplumber 搜索关键词 |

**效果**：
- 新增 93 个 `.py` 脚本，总计 153 个，全部语法检查通过
- 38 只股票全量报告重新生成，0 失败，17 只 ALL PASS
- 后续新增股票也按此标准

**触及 Wiki 页面**：
- [[个股脚本标准]] — 新建概念页
- [[项目全景概述]] — 补充 scripts 目录说明

---

## [2026-06-14] feat | Footnotes 重构 — 分行展示 EPS 调整项明细

**设计**：每项非经常调整独立一行，标签用中文全称，数据两位小数（百万级精度），无数据留空。

**格式**：
```
Footnotes      2018  2019  2020  ...
政府补贴       0.05  0.17  0.45  ...
公允价值变动     —     —   (0.11) ...
───────────────────────────────────
adj.NP         0.04  0.13  0.25  ...
```

**引擎**：`engine.py` → `all_footnotes` 新增 `adj`/`diff`/`src` 结构化字段，diff 用原始 `np_val`/`adj_np` 直算避免脚注文本四舍五入失真。

**前端**：`generate_report.py` JS 端解析 `src` 提取各缩写出现的年份，每项一行；表格含灰色垂直分割线；合计行 `adj.NP` 位于底部分隔线上方。

**缩写表**：GS=政府补贴, FV=公允价值变动, FX=汇兑收益, II=投资收益, IM=资产减值, EL=权益法亏损, OG=其他收益, CD=A股扣非

**触及 Wiki 页面**：
- [[generate_report.py]] — 新增 Footnotes 渲染章节
- [[engine.py]] — 补充 footnotes 结构化字段

## [2026-06-14] fix | 脚本 revenue_structure 类型 + SourceFileLoader 编码 + A股 TDX footnote 三连修

**问题**：
1. `importlib.spec_from_file_location(encoding="utf-8")` 在 Python 3.11 不支持 → `TypeError`
2. engine 传的 `revenue_structure` 是 `{"by_product": [...]}` dict，脚本里 `revenue_structure[:3]` 把 dict 当 list → `str.get()` 报错 → 脚本静默失败 → 回退到 PDF 乱码
3. A 股也显示了"通达信(TDX)财报计算" footnote（AKShare indicators 早年为空触发 `has_fallback=True`）

**修复**：
- `engine.py` 3 处加载点改用 `SourceFileLoader`（自动检测 `# coding: utf-8`）
- `scripts/000408/`: `isinstance(revenue_structure, dict)` + 遍历 `items()` 取前 3 条
- `scripts/09992/`: `revenue_structure.get("by_ip", [])` 替代 list comprehension
- `engine.py` L653: `and market == "hk"` 限定仅港股生成 footnote

**验证**：14 只有动态脚本的标的全部 Commentary PASS，藏格从乱码修复为 `from_script: True`。

**触及 Wiki 页面**：
- [[engine.py]] — 更新脚本加载 + 数据源 footnote 说明
- [[BUSINESS 生成链路]] — 补充 revenue_structure 参数类型

## [2026-06-14] feat | 全链路智能新鲜度检测 — 双轨模型

**设计**：将报告数据分为两类，各自独立检测新鲜度：
1. **股价类**（Header/K线/估值线）：查最近 3 个自然日 K 线是否存在 → 缺则自动拉取
2. **财报类**（24行/季度/CAGR/估值）：查最新 report_date，对比当前日期推算应发布报告期 → 有新品则自动拉取

**改动**：
- `build.py`：`step_1_fetch` 新增 `_need_fresh_prices()` + `_need_fresh_financials()` 双轨检测
- `build.py`：`step_2_pdf` 检测最新 PDF 年份落后当前年份 → 自动下载
- `build.py`：`step_3_mda` 存 `mda_extracted_year`，新年报 PDF → 强制重提
- `fetcher.py`：新增 `last_fetch_date` meta key（YYYY-MM-DD 格式）
- **效果**：`python build.py <code>` 无需 `--fetch`，自动判断哪些步骤需要刷新

**触及 Wiki 页面**：
- [[build.py]] — 更新 Step 1/2/3 描述
- [[extract_mda.py]] — 更新质量阈值 + 年份追踪
- [[engine.py]] — 更新 mda_parsed 逻辑
- [[8 步流水线]] — 更新 Step 描述

## [2026-06-14] refactor | 移除全部硬编码 commentary → 动态 business_commentary.py

**原则**：Business 和 AI Commentary 不应写死数字，应通过 `build(stock, metrics, revenue_structure, years, cagr, spot)` 从实时数据动态生成。

**改动**：
- 新建 `scripts/{000408,00883,09992,300308}/business_commentary.py`（4 只）
- 重写 `scripts/{002027,00981,02097,600519}/business_commentary.py`（4 只）
- 删除 8 只股票的 config `analyst.commentary` 硬编码
- `extract_mda.py`：质量阈值放宽（≥2 类 + ≥6 句 + overview<85%），原始文本兜底
- `engine.py`：移除 `mda_quality=="1"` 门控 → 无条件尝试解析 mda_text

**动态脚本接口**：
```python
def build(stock, metrics, revenue_structure, years, cagr, spot):
    return {"business": str, "commentary": [p1,p2,p3,p4,p5]}
```

**触及 Wiki 页面**：
- [[BUSINESS 生成链路]] — 更新优先级链
- [[engine.py]] — 更新 commentary 生成逻辑
- [[extract_mda.py]] — 更新质量阈值

## [2026-06-14] fix | generate_report.py K线 tooltip PB 线缺失 + 系列名规范化

**根因**：K 线图 hover tooltip 估值线数值判断仅匹配 `x CF`（L623），PB 估值线（`0.67x PB`）永不符合 → hover 时无价格显示。

**修复**：
1. `valLabel` PB 模式改 `'x PB'` → `'*BPS'`（与 BPS 指标对齐，如 `0.67*BPS`）
2. tooltip 条件：`n.indexOf('x PB')>-1` → `n.indexOf('*BPS')>-1`
3. 同步匹配：`x CF` || `*BPS` 覆盖两种估值模式

**验证**：01114 华晨中国 × PB=0.67 → K 线 hover 显示 `0.67*BPS: {price}` ✅

**触及 Wiki 页面**:
- [[generate_report.py]] — 更新 tooltip 渲染 + 系列名
- [[VL 估值方法论]] — 补充 PB 图表标签格式

## [2026-06-13] fix | engine.py 季度前瞻双重漏洞修复 + ingest

**根因**：06699 季度区无 2026 年，排查发现两处漏洞：

1. `qtr_years` 追加（L2107）：仅探测 Q1 (03-31)，半年度报告公司仅发 H1 (06-30)，永远匹配不到
2. `build_semi_annual` 末尾前瞻（L1112-1115）：`financial_item_by_code` 无 `item_name` 回退，TDX 数据无 item_code → 静默失败

**修复**：L2107 追加 H1 探测；L1112-1115 加 `or reader.financial_item(...)` 回退。

**验证**：00700 2026 Q1 `forward: True` 正常 ✅。06699 无 2026 数据属公司未发布财报，非代码问题。

## [2026-06-13] ingest | CODEBUDDY.md 二次精简 — 15行纯宪法 + 腾讯全量报告

- `CODEBUDDY.md` 缩减为 3 段：项目身份 + 安全红线 + 环境规则（~30行）
- 新增 `concepts/Wiki操作手册.md` — 承载 Ingest/Query/Lint 流程 + 页面格式模板
- `overview.md` 追加 Wiki 目录结构 + "为什么存在"
- `index.md` 新增 Wiki操作手册 条目

## [2026-06-13] security | 🔴 TDX Token 硬编码泄露 — 已修复 + 写入宪法

**事件**：GitHub 扫描告警，`tdx_client.py:23` 硬编码 `Bearer TDX-e35604...` 暴露在仓库中。

**修复**：
1. `tdx_client.py` 改为从 `.env` 读取 token（`os.getenv("TDX_TOKEN")` + `_load_dotenv()`）
2. `git filter-branch` 重写 13 个 commit 从历史中抹掉 token
3. `git push --force` 覆盖远程

**宪法级规则**（写入 `CODEBUDDY.md` + Memory）：
- 源码中严禁硬编码任何密钥 / Token / 密码 / API Key
- 所有凭证必须通过 `.env` + `os.getenv()` 读取
- 写新模块前必须检查凭证来源
- Git commit 前自查 `git diff --staged`

## [2026-06-13] cleanup | 移除微云上传下载及相关 wiki 页面

删除内容：
- `research-wiki/vl/entities/工具-微云网盘.md` — 整页删除
- `concepts/跨电脑迁移与云备份.md` — 移除微云引用，更新为两 Tool 方案
- `vl/index.md` — 移除微云条目
- `.env` / `.env.example` — 移除 `WEIYUN_MCP_TOKEN`
- `tencent-weiyun/` 空目录 — 待手动删除

原因：微云 API 配额不足，改为手动同步。

## [2026-06-13] ingest | 季度数据修复 + 2026前向季报 + 股息0→—

### 改动

**engine.py**:
1. `build_semi_annual` H1 查询加 `or item_name` 回退（兼容 TDX 无 item_code）
2. Q1 季度查询全面加 `or item_name` 回退
3. 2026 前向季报：仅 Q1 时生成 `forward: True` 标记
4. `qtr_years` 动态追加下一年（如有 Q1 数据）

**generate_report.py**:
1. 季度股息 0.000 → "—"（`decimal===3&&v===0`）
2. 半年度格式股息同样处理

### 验证 (00700)

- Qtr.sales: 16y ✅ (含2026 Q1=1941.7亿)
- Qtr.eps: 16y ✅ (含2026 Q1=6.3)
- Qtr.dividends: 16y ✅
- Step 8: ALL PASS (73 checks, 0 fails)

## [2026-06-13] ingest | TDX 替换 fetcher 港股三大表 + engine 双路径改造

### 改动范围

**新建**: `tdx_client.py` — HTTP 直连 TDX API，字段映射，单位转换
**修改**: `fetcher.py` — 港股三大表改 TDX 拉取，indicators 改 INSERT OR IGNORE
**修改**: `engine.py` — 6 处改造：

1. `if ind and ind.get("OPERATE_INCOME"):` — 防止空壳 indicators 误入标准路径
2. BPS 统一 `balance.总权益 ÷ shares` — 替代 `indicators.BPS` 直读
3. else 分支 EPS 反推加权股数 — `shares = NP / 每股基本盈利`
4. 财报查询 `item_code or item_name` 双重回退 — 兼容 TDX 无 code
5. 折旧 `income.折旧及摊销` 兜底 — TDX 折旧在 income 不在 cashflow
6. 动态数据源边界检测 — 仅混合数据源时生成 `data_source_note`

**触及 Wiki 页面**:
- [[tdx_client.py]] — 新建模块页
- [[fetcher.py]] — 更新港股 TDX 双源拉取说明
- [[engine.py]] — 更新双路径、回退增强、BPS 公式
- [[数据源-通达信TDX]] — 标记已接入，更新 API 格式
- [[index.md]] — 新增 tdx_client.py 条目

### 验证结果 (00700 腾讯)

- 2011-2025 共 15 年，交叉校验 83/83 通过
- TDX 回退 vs 引擎标准: 23/24 项 <2%，仅 BPS 差异 4-5%
- 2017 年前 6 年全部 TDX 计算，2017 后 9 年保留 AKShare

## [2026-06-11] ingest | TDX + 微云 + IMA 三工具接入与迁移方案

接入通达信 TDX MCP 服务（港股财务数据 2001-2025，0.0% 偏差），安装微云 Skill（云备份上传脚本），整理 IMA 知识库配置。
设计跨电脑迁移方案：`.env` 统一管理全部 Token，微云存储备份包，`setup.cmd` 一键初始化。
触及页面：entities/数据源-通达信TDX.md, entities/工具-微云网盘.md, entities/工具-IMA知识库.md, concepts/跨电脑迁移与云备份.md, index.md, log.md（共 6 页）。raw 层: tdx-reference/tdx-mcp-api.md（完整数据字典）。

## [2026-06-09] bootstrap | Wiki 初始化

创建 research-wiki/ 三层架构（Schema + Raw + Wiki），基于 Andrej Karpathy LLM Wiki 方法论。
初始摄入：项目全景概述、模块清单、核心概念索引、关键实体。
触及页面：overview.md, index.md, log.md（共 3 页）。

## [2026-06-09] ingest | docs/ 文档深度摄入

处理全部 docs/ 目录资料（9 MD + 2 PDF 参考文档）。
概念页（7 个）、实体页（2 个）。

## [2026-06-09] ingest | 核心模块逐文件摄入

为 7 个核心 .py 模块创建 Wiki 页面。

## [2026-06-09] ingest | AKShare Stock API 文档

raw 层: akshare-stock-api.md + entities: 数据源-AKShare.md

## [2026-06-09] ingest | docs/ 残留文档处理

创建 2 个概念页（开发环境配置、数据口径与样式规范），删除 docs/ 目录。

## [2026-06-09] build | 紫金矿业 (02899)

PB=1.0x, 新建 scripts/02899/business_commentary.py, valuation_method="pb" 写入 config。

## [2026-06-10] lint | Wiki 健康检查 + 修复

全站 Lint 扫描结果：
- 修复 8 处断链：数据口径规范→数据口径与样式规范 (×2)、估值倍数优先级→VL 估值方法论 (×2)、
  VL 官方指南 2020 中文解读→概念页组 (×2)、requirements.txt→移除
- 创建 4 个缺失模块页：generate_reading.py、generate_index.py、list_refs.py、set_baba_meta.py
- 修复 Step 8 矛盾：统一为 WARNING（非 BLOCK），对齐实际代码行为
- 添加 6 条反向链接解决孤儿页面：数据源-AKShare、李录阅读法融合、开发环境配置
- 更新 index.md

修复后状态：25 页（1 overview + 11 modules + 9 concepts + 3 entities + 1 index + 1 log），0 断链，0 孤儿。

## [2026-06-10] ingest | .workbuddy 清理

- 删除 vl_handbook.txt（与已有 PDF 源重复）
- 迁移 style-reference.md → raw/vl-reference/style-reference.md，创建实体页 entities/原始资料-VL样式参考.md
触及页面：index.md。

## [2026-08-01] lint | research-wiki 健康检查

### 操作
- 运行 `scripts/wiki_lint.py` 全量检查 166 个 .md 文件
- 检查项：结构 / frontmatter / 断链 / 参见区块 / index 注册 / 孤立页面 / 内容质量 / raw 命名

### 修复（7 处断链）
- `generate_report.py.md`：`[[数据口径规范]]` → `[[数据口径与样式规范]]`
- `index.md`：`[[项目全景概述]]` → `[[overview|项目全景概述]]`
- `Wiki操作手册.md`：`[[相关模块]]` 占位 → `[[index|模块清单]]`
- `research/articles/entities/查理·芒格.md`：raw 文件名 kaufman → 考夫曼
- `倾覆力矩.md`、`竞争性毁灭.md`：同上 + munger-critical-mass → 芒格-临界质量
- `research/TCL中环/research-reports.md`：目录 wikilink → 代码块

### 剩余（76 WARN / 5 INFO）
- 缺失概念页 20 处（均值回归、复杂适应系统、Lollapalooza效应…）
- frontmatter 缺失 14 页（articles/concepts|synthesis + 润泽科技）
- 参见区块缺失 24 页（synthesis 系列普遍缺失）
- 内容过少 5 页（TCL科技/云铝/京东方/时代天使/神火 research-reports）
- vl/synthesis/ 空目录
- `[[项目全景概述]]` 在本 log 历史条目中，按只追加规则不改

触及页面：vl/index.md、vl/concepts/Wiki操作手册.md、vl/modules/generate_report.py.md

## [2026-08-01] fix | 批量修复 frontmatter + 参见区块 + 交叉引用

### 操作
- 编写 `scripts/wiki_fix.py`，基于 lint 数据自动补全缺失的 frontmatter、参见区块、交叉引用缺口
- 两轮修复：138 + 81 = 219 项

### 修复结果
- frontmatter 缺失 → **全部清零**（原 14 页）
- ## 参见 区块缺失 → **全部清零**（原 24 页）
- 可修断链 → **全部清零**
- 交叉引用缺口 → 剩余 ~343 处（系统性，增补一轮即产生新入链缺口，diminishing returns）

### 未修
- raw/ 文件 ~18 处断链（只读，不可改）— 标记为缺失概念页
- 交叉引用缺口 343 处 — 增补已达均衡点

触及页面：大量 vl/ + research/ 页面（批量修复）
