# 投研操作日志

## [2026-08-16] ingest | 《置身事内：中国政府与经济发展》深度阅读 + 国企激励机制分析（茅台案例）

### 深度阅读
- `raw/research/articles/兰小欢_2021_置身事内-中国政府与经济发展.md` — 全书结构化摘要（前言 + 8 章 + 结束语 + 关键概念表 + 笔记），遵循 deep-read-summary 规范，尊重原文、区分事实与评价

### 综合分析（国企激励机制 × 茅台案例）
- `articles/synthesis/国企激励机制-置身事内框架与茅台案例.md` — 以《置身事内》框架分析茅台管理层激励：
  - **三重激励结构**（🟡 推导）：官场仕途 + 市场业绩 + 地方财政约束
  - **可查证事实**：年薪制（百万级）+ 几乎无股权激励 + 贵州财政依赖（茅台贡献贵州财政 53%—55%、遵义市税收 83%）
  - **分红转向**：2015—2021 年 51.9% → 2022 年 95.78%，与 2021 年划转社保 10% 股权时间重合
  - **严格区分事实与推导**：未查到茅台官方"因财政需要而提高分红"的表述，高分红与财政压力的因果仅作"合理但未证实的推断"

### 页面更新
- `index.md` — 收录 synthesis 新页面
- `log.md` — 本文

## [2026-08-13] fix | 腾讯 Q2 2026 业绩会中文翻译版 3 处对齐英文原文

对照 StockAnalysis 英文原文（stockanalysis.com/quote/hkg/0700/transcripts/667897-q2-2026/）逐项核对，修正 3 处翻译遗漏/口径偏差：
- 员工数补上「环比 +1%」
- 营销服务驱动因素从「eCPM 和曝光量提升」修正为「电商/互联网服务/本地服务等主要品类广告主支出增加」，并补「广告 AI 推荐系统参数量大幅扩展」
- TME 收购喜马拉雅补上「2026年5月完成」时间点

其余财务数据、发言人、7 个问答结构与英文原文完全一致。

## [2026-08-12] refactor | 竞争演化框架重写——原文/推演严格区分

### 问题
- 框架中混杂了三类内容未标注：五书原文、芒格原话、AI 推演
- 多处过度推理：汉密尔顿"公司内部博弈"的基因组类比被泛化为对公司本身的断言
- 芒格引语后紧跟 AI 推演，读者可能误以为是芒格的意思
- "致命 20 倍"等数字无出处
- "我们的投资生涯恰好落在间冰期末尾"是纯推测
- "病菌"概念向"生态锁定/转换成本"的映射未经论证
- 四个判据框架是 AI 自建，但放在芒格引语下可能造成混淆
- 茅台作为四重判据的例子，判断本身无足够数据支持

### 重写
- 全文标注 🔵 原文（五书及芒格原话）/ 🟡 推演（AI 逻辑延伸）
- 芒格原话独立成节（第二节），与推演明确分开
- 删除"致命 20 倍"、"间冰期末尾"等无出处表述
- 汉密尔顿引语保留为基因组内部博弈的类比，不泛化为公司断言
- 四个判据明确标注为 🟡 推演，增加"框架本身未经实战检验"的局限性声明
- 删除茅台等具体公司的判据举例（无足够数据）
- 移除原第一节"五个公理"中投资映射的过度推理，只保留原文
- 框架从 7 节精简为 4 节：前置→五书原文→芒格原话→推演交叉关系

## [2026-08-12] ingest | 竞争演化初步框架——五书多元思维模型整合 + 结构性护城河判据

基于五本演化论/生物学经典著作（《自私的基因》《盲眼钟表匠》《枪炮病菌与钢铁》《冰河期》《基因组》）的深度阅读，整合多元思维模型，构建竞争演化初步框架。

### 新增
- `articles/synthesis/竞争演化初步框架-五书多元思维模型.md` — 完整框架，包含：
  - **五个公理**：可复制单元、累积选择、环境决定命运、内部冲突永恒、淘汰是默认状态
  - **三层结构**：基因层（复制因子/ESS/延伸表型/博弈结构）→ 环境层（大陆轴线/安娜·卡列尼娜/占先驯化/病菌vs枪炮）→ 时间层（冰期节律/凉爽夏季/多节律叠加/正反馈）
  - **模型矩阵**：五书 × 五个学科 × 四个关键交叉点（ESS×占先驯化×累积选择、红后效应×凋亡失灵×冰期节律、延伸表型×病菌×正反馈、垃圾DNA×安娜·卡列尼娜×凉爽夏季）
  - **五重拷问**：操作性分析框架，对任何标的逐层压测
  - **五个终局洞察**：淘汰是默认状态、复杂适应不需要设计者、看不见的武器致命20倍、内部崩塌比外部攻击更常见、时间是最残酷的变量
  - **应用边界**：适用/不适用场景 + 后见之明偏差的局限性

### 更新
- `index.md` — 新增框架文章索引

### 与现有 wiki 的关系
- 此框架是 [[竞争性毁灭-四书格栅分析]]（四书格栅）的升级版，新增《盲眼钟表匠》作为第五本书
- 将 [[盲眼钟表匠-芒格评价与多元思维模型启示]] 中提取的五个模型整合进统一框架
- 将 [[自私的基因-商业基因映射分析]] 中的三道映射题（复制因子/延伸表型/ESS）提升为框架公理
- 将 [[枪炮病菌与钢铁-投资终极因框架]] 的七维映射整合进环境层

### 第二轮更新：结构性护城河判据（第七节）
- 新增 **四个判据** 区分运气与结构性护城河：
  1. **复制因子独立性**（基因能否跨载体跳转？）
  2. **筛选压力来源**（优势是涌现的还是某个人设计的？）
  3. **安娜·卡列尼娜条件**（后来者能否同时满足全部必要条件？）
  4. **时间检验**（护城河经历了多少轮冰期？每次是变宽还是变窄？）
- 四重判据交叉验证表 + 分级（四重通过=结构性，三重存疑，二重非结构性，一重零重=无护城河）
- **"赔率有利"的精确定义**：四个条件都满足 = 赔率对你有利，因为护城河不是运气——而市场的大多数参与者无法区分"运气好"和"结构性强"
- 修正第六节"关键局限"：框架的真正价值不是雷达（提前发现威胁），而是免疫系统（避免死于认知失调）

## [2026-08-08] fix | 修复根目录 index.html 空文件导致 404

- index.html 被清空为 0 字节，重新写入重定向代码
- `https://flyingglass.github.io/value-line/` 恢复可访问

## [2026-08-08] feat | 投研 Wiki 索引页上线 + 全量 industry 中文化 + 分类合并精简

### 新增
- **投研 Wiki 索引页**：`research-wiki/index.html` — 自包含 SPA，131 篇文章，按标的(19 个)+多学科(5 主题)分组展示
- 多学科分类：🧠芒格·格栅理论 / 🔄复杂经济学 / 🧬生物学 / 🧩心理学 / 📚书籍摘要
- report/index.html 和 wiki index 统一黑底 sticky bar 样式，双页面互链导航
- `scripts/generate_wiki_index.py` — 从 research-wiki/ 扫描 md，生成 index.html
- deploy.yml 扩展部署范围至 research-wiki/ + index.html

### 修复
- generate_report.py: .toFixed() TypeError — capital structure/trailingPE 字段加 Number() 防御
- engine.py: spot.pe/pb/div_yield 无汇率时从 "-" 改为 None

### 分类整理
- 全量 18 个英文 industry → 中文统一命名
- 安琪酵母/食品添加剂/磷化工 → 并入"化工"
- 保险+金融服务 → 合并"金融"
- 科技 → 重命名"互联网"
- 必需消费品+奢侈品 → 合并"消费"
- 索引页从 22 个行业精简到 17 个

## [2026-08-06] ingest | StockAnalysis.com 美股 transcript 数据源 + AMD Q2 2026 业绩会入库

### 背景
用户发现 stockanalysis.com 可以获取美股 earnings call transcripts，这是投研的重要信息来源。

### 摄入内容
- **raw 原始资料**：`raw/research/articles/amd-q2-2026-earnings-call.md` — AMD Q2 2026 业绩会关键信息摘要
  - 来源：stockanalysis.com/stocks/amd/transcripts/660937-q2-2026/（数据提供：Quartr）
  - 营收 $115 亿（+50% YoY），数据中心 $67 亿（+107%），毛利率 56%
  - Anthropic 签 2 GW MI450 大单，Microsoft Azure Helios 大规模部署
  - Q3 指引 ~$130 亿，2027 数据中心收入翻倍以上
- **wiki 实体页**：`articles/entities/stockanalysis-transcripts.md` — 美股 transcript 数据源完整指南
  - stockanalysis / seekingalpha / motley fool / SEC EDGAR 四大渠道对比
  - 投研用途：管理层语气分析、分析师关注点、指引变化跟踪、客户披露
  - 中文翻译工作流

### 页面更新
- `index.md` — 收录 stockanalysis-transcripts 实体页
- `log.md` — 本文

---

## [2026-08-06] ingest | 伯克希尔股东大会 1994-2021 全 PDF → 16 类深度摘要 + 格栅对照

### 新增
- `raw/research/articles/伯克希尔股东大会1994-2021-分类版深度摘要.md` — 685 页全文 16 类摘要 + 与哈格斯特朗 8 学科格栅对照
- `articles/synthesis/巴芒论迪士尼.md` — 巴芒论迪士尼原文汇编：消费者心智/米老鼠/艾斯纳/卖出原因/泡泡玛特类比
- `articles/synthesis/巴芒论迪士尼.md` 更新 — 第八节重写：基于 Kingswell 2023 Daily Journal 年会 62 问答全文深度解读芒格晚年迪士尼观点（在位者困境/否认偏差/几乎一切都会消亡/从"例外"到"一员"）

---

## [2026-08-06] new | 建滔集团(00148) + 建滔积层板(01888) 纳入覆盖

### 新增
- `建滔集团/overview.md` — 数据目录 (5业务分部 FY2025, PB=0.6x)
- `建滔集团/thesis.md` — 投资 Thesis (垂直一体化/周期复苏+AI驱动/破净折价)
- `建滔集团/industry-chain.md` — 电子材料产业链全景 (铜箔→CCL→PCB)
- `建滔积层板/overview.md` — 数据目录 (纯覆铜板 FY2025, PB=0.6x)
- `建滔积层板/thesis.md` — 投资 Thesis (纯赛道龙头/AI高端材料/周期弹性)

### 数据
- 建滔集团：营收453.75亿(+5.3%), 净利44.02亿(+170%), PE 12.3x, PB 0.78x
- 建滔积层板：营收204亿(+10%), 净利24.42亿(+84%), PE 48.8x, PB 7.29x
- 母子关系：建滔集团控股建滔积层板约70%+

### 更新
- `index.md` — 收录 6 个新页面，更新时间戳
- `log.md` — 本文

## [2026-07-31] synthesis | 《枪炮、病菌与钢铁》→ 投资终极因框架

### 新增
- `articles/synthesis/枪炮病菌与钢铁-投资终极因框架.md` — 戴蒙德七维框架映射投资决策：
  终极因>近因 / 安娜·卡列尼娜原则 / 大陆轴线 / 病菌vs枪炮 / 占先驯化 / 自然实验 / 现金流=文明发动机

### 更新
- `index.md` — 收录新页面，更新时间戳
- `log.md` — 本文

## [2026-07-30] lint | 全站健康检查 — P1 孤儿收录 · 0 断链 0 孤儿

### 修复
- `articles/synthesis/芒格多元学科投资决策框架.md` 孤儿页面 → 补入 index.md

### 状态
92 页面 · 0 断链 · 0 孤儿

## [2026-07-26] ingest | ESS 切换 — 企业跨越与失败分析

### 过程
- 基于五家公司横评提炼 ESS 切换存活的三个必要条件
- 四条可操作原则 + 失败复盘（Nokia/Kodak/阿里）
- 写入 `research/articles/synthesis/ESS切换-企业跨越与失败分析.md`
- 更新 index.md

### 内容
1. 三个必要条件：基因够抽象 / 单细胞瓶颈独立孵化 / 延伸表型不随旧载体死
2. 失败复盘：Nokia(条件1), Kodak(条件1+2), 阿里PDD攻击(条件2)
3. 四原则：单细胞瓶颈 / 主动自噬 / 延伸表型分类投资 / 逆向分析法
4. 五家生存力评分表

### 交叉链接
- ← [[ESS切换-企业跨越与失败分析]]
- ← [[自私的基因-商业基因映射分析]]
- ← [[../concepts/竞争性毁灭]]
- ← [[竞争性毁灭-四书格栅分析]]

---

## [2026-07-26] ingest | 自私的基因 x 商业基因映射分析

### 过程
- 基于道金斯《自私的基因》框架 × 读通《枪炮·病菌与钢铁》后，合成分析五家公司
- 写入 `research/articles/synthesis/自私的基因-商业基因映射分析.md`
- 更新 index.md

### 内容
- 泡泡玛特：复制因子=IP运营引擎（非IP本身），延伸表型 = 抽盒机+IP矩阵基因组合作+消费者情感依赖
- 腾讯：复制因子=社交图谱（非微信），延伸表型=身份+支付+小程序=环境本身，AI风险=基因贬值（道金斯式）
- 字节：复制因子=推荐算法，基因复制性最高（TikTok跨150国），AI风险=内容消费模式消失
- 阿里：复制因子=搜索商业基础设施，克里斯坦森式困境最标准案例，AI时代搜索基因死/物流基因可能活
- 苹果：复制因子=集成设计哲学，3次基因跳转（Mac→iPod→iPhone→多载体），AI考验载体老化

### 交叉链接
- ← [[自私的基因-商业基因映射分析]]
- ← [[../concepts/竞争性毁灭]]
- ← [[竞争性毁灭-四书格栅分析]]
- ← [[../../泡泡玛特/thesis]]
- ← [[../../腾讯控股/thesis]]

---

## [2026-07-25] ingest | 竞争性毁灭——四书格栅分析

### 过程
1. 读取四本原始资料（自私的基因、枪炮病菌与钢铁、基因组、冰河期）
2. 从每本书提取与竞争性毁灭直接相关的核心概念
3. 四书格栅交叉，形成竞争性毁灭的四重维度：
   - 《自私的基因》→ 底层机制（ESS/选择单位/囚徒困境/六种制约）
   - 《枪炮病菌与钢铁》→ 环境框架（终极因/大陆轴线/安娜·卡列尼娜原则/占先驯化/病菌vs枪炮）
   - 《基因组》→ 内部冲突（垃圾DNA/性染色体战争/凋亡/没有固定的基因组）
   - 《冰河期》→ 时间与非线性（冰期为默认/凉爽夏季/多节律叠加/正反馈/时间残酷性）
4. 形成完整因果链：环境剧变→旧ESS瓦解→内部正反馈加速崩溃→多周期叠加锁定命运
5. 附带艾德勒四级阅读法建议（总计约50-70小时）
6. Wiki 页面 → `articles/synthesis/竞争性毁灭-四书格栅分析.md`
7. 更新 index + log

### 关键洞察
- 竞争性毁灭不是单一现象，是四个维度同时作用的因果序列
- 四个维度的叠加 = Lollapalooza式的毁灭效应
- 时间是最残酷的变量：米兰科维奇模型被否定了30年才被验证，你可能全对但死在时间面前
- 芒格的投资哲学可以从四个维度推导出来：默认状态→护城河是唯一反制→只买护城河足够宽且在变宽的企业

## [2026-07-24] lint | 扫尾 — 移除 `芒格-多元思维模型-推演与分析.md` 后全站验证 · 0 断链 0 孤儿

## [2026-07-24] ingest | 《穷查理宝典》完整 Wiki 入库

### 过程
1. EPUB 全文提取（UTF-8 无损，避开了 PDF 编码乱码问题）
2. 原始资料入库 → `raw/research/articles/kaufman_2005_poor_charlies_almanack.md`（深度阅读摘要）
3. 艾德勒四级阅读法摘要 → `raw/research/articles/穷查理宝典_艾德勒阅读法.md`
4. Wiki 实体页 → `articles/entities/查理·芒格.md`
5. 思维模型 → `articles/concepts/芒格-临界质量.md`、`竞争性毁灭.md`、`倾覆力矩.md`
6. 更新 index + log

### 关键发现
- 芒格明确列出"最重要的模型"：冗余备份、复利、临界点、倾覆力矩、自我催化、达尔文综合、认知误判
- 第二讲列出"必须掌握的基础知识"：数学→会计学→硬科学→心理学→微观经济学
- 竞争性毁灭的1911年证据：50家最活跃公司仅存通用电气
- Lollapalooza = 临界质量的心理学版本

## [2026-07-24] lint | 全站健康检查 — concepts/ 改名后扫尾

### 状态
85 页面 · 0 断链 · 0 孤儿

### 已知遗留
- `raw/.../哈格斯特朗_...格栅理论.md` L687 引用 `[[articles/concepts/arthur-increasing-returns]]`（旧 wiki 页名），raw/ 只进不改不动

## [2026-07-24] lint | raw/research/articles/ 中文改名后全站断链修复

### 背景
`raw/research/articles/` 下 8 个英文文件名改为中文，1 个文件被删除。导致 wiki 页面中 10 处 raw 源链接断链。

### 修复清单 (P0)
| # | 文件 | 修复内容 |
|---|------|------|
| 1 | `articles/concepts/arthur-increasing-returns.md` | raw 源链接 `arthur-increasing-returns-emergence` → `阿瑟-收益递增与涌现` (×2) |
| 2 | `articles/entities/seth-klarman-interview.md` | raw 源链接 `seth-klarman-interview` → `塞斯卡拉曼访谈-企业分析原则` (×2) |
| 3 | `articles/synthesis/dahang-weekly-76.md` | raw 源链接 `dahang-weekly-76` → `大航周报76-贵州茅台专题` (×2) |
| 4 | `articles/concepts/munger-poor-charlie-lecture2.md` | raw 源指向已删除文件 → 重定向到 `考夫曼_2005_穷查理宝典`（全本）+ `芒格-多元思维模型-推演与分析` |
| 5 | `articles/papers/hagstrom-grid-theory.md` | raw 源链接 `hagstrom_2023_investing_last_liberal_art` → `哈格斯特朗_2023_查理芒格的智慧-投资的格栅理论` |
| 6 | `articles/concepts/芒格格栅理论-多学科思维投资框架.md` | 同上 |
| 7 | `articles/concepts/艾德勒-四级阅读法.md` | 同上 |
| 8 | `articles/concepts/munger-critical-mass.md` | 引用 `kaufman_2005_poor_charlies_almanack` → `考夫曼_2005_穷查理宝典` |
| 9 | `index.md` | `hagstrom_2023_..._艾德勒阅读法` → `哈格斯特朗_2023_查理芒格的智慧_艾德勒阅读法` |
| 10 | `vl/concepts/Arthur-收益递增与涌现.md` | raw 源链接 `arthur-increasing-returns-emergence` → `阿瑟-收益递增与涌现` |

### P1 — 孤儿页面收录
- `articles/concepts/munger-critical-mass.md`（芒格临界质量）→ 添加到 `index.md`

### 状态
0 断链 · 0 孤儿

## [2026-07-22] ingest | 批量初始化 — 腾讯/时代天使/云铝/神火/京东方/TCL科技 共 30 wiki 页面

| # | 标的 | 代码 | 行业 | 估值 | 核心发现 |
|---|------|------|------|:---:|------|
| 1 | 腾讯控股 | 00700 | Technology | CF | 毛利率 43→56% 四年提升, 净利 2,248 亿, ROE 21% |
| 2 | 时代天使 | 06699 | Healthcare | CF | 毛利率 63% 极稳, 海外占比 44%, 盈利从低谷恢复 |
| 3 | 云铝股份 | 000807 | Metals | CF | 水电铝成本优势, PE 10.4x, 负债率仅 19.8% |
| 4 | 神火股份 | 000933 | Metals | CF | 煤电铝一体化, PE 10.5x |
| 5 | 京东方 | 000725 | 面板 | PB | 全球 LCD 龙头, 面板周期行业, PE 36.7x |
| 6 | TCL科技 | 000100 | 面板 | PB | 面板+光伏双主业, 2024 低谷后盈利恢复中 |

各标的均按 5 页面模板生成: overview / thesis / industry-chain / operating-metrics / research-reports。

### 数据说明
- 腾讯(00700) + 时代天使(06699): 港股, indicators 表数据完整 (4 年)
- 云铝/神火/京东方/TCL: A股, indicators 以 FY2025 为主, 通过 income 表补充历史数据
- 所有数据来源: `data/<code>.db` + `scripts/<code>/`

### 页面更新
- 6 标的 × 5 页面 = 30 wiki 页面
- `research/index.md`: 新增 30 条目
- `research/log.md`: 本次

---

## [2026-07-22] ingest | 紫金矿业 (02899) 投研体系初始化 — 5 wiki 页面

### Wiki 产出

| # | 页面 | 内容 |
|---|------|------|
| 1 | `research/紫金矿业/overview.md` | 数据目录（DB 表结构、营收拆分 FY2025 五产品、四年财务指标、资产负债、现金流） |
| 2 | `research/紫金矿业/thesis.md` | 投资 Thesis（铜/金/锌/锂/银五产品赚钱逻辑、四大护城河、五风险、五催化剂） |
| 3 | `research/紫金矿业/industry-chain.md` | 产业链全景（矿山→冶炼→终端、全球八大主力矿山、竞争格局、铜/金/锂周期） |
| 4 | `research/紫金矿业/operating-metrics.md` | 运营指标跟踪（金铜双核+锂成长、利润超级弹性、现金流翻倍、敏感度分析） |
| 5 | `research/紫金矿业/research-reports.md` | 券商研报索引（待拉取方向：铜行业/金价展望/锂板块/矿山跟踪） |

### 数据来源
- `data/02899.db` — 9 表完整财务数据库（港股格式）
- `scripts/02899/business_commentary.py` — VL 流水线 business + commentary
- `scripts/config.py` — 标的配置

### 核心发现
- **利润超级弹性**：营收 +29% 但归母净利 +159%（2022→2025），毛利率 15.7%→27.7% 近乎翻倍
- **金铜共振**：铜价+金价同时处于历史高位，紫金是全球金铜双轮驱动最纯的标的
- **降杠杆**：资产负债率 59.3%→51.6%，经营 CF 287→754 亿（三年翻 2.6 倍）
- **极致低估值**：PE 3.44x，受益于商品超级周期但市场仍未充分定价
- **牛市弹性**：铜价 +$1000/吨 ≈ 年化利润 +100 亿（估算）

### 页面更新
- `research/紫金矿业/`：新建 5 个 wiki 页面
- `research/index.md`：新增 5 条目
- `research/log.md`：本次

---

## [2026-07-22] ingest | 宁德时代 (300750) 投研体系初始化 — 5 wiki 页面

### Wiki 产出

| # | 页面 | 内容 |
|---|------|------|
| 1 | `research/宁德时代/overview.md` | 数据目录（DB 表结构、营收拆分 FY2025、六年财务指标、资产负债、现金流） |
| 2 | `research/宁德时代/thesis.md` | 投资 Thesis（四层业务赚钱逻辑、四大护城河、五风险、五催化剂） |
| 3 | `research/宁德时代/industry-chain.md` | 产业链全景（矿产→材料→电芯→回收/应用、五梯队竞争格局、行业周期） |
| 4 | `research/宁德时代/operating-metrics.md` | 运营指标跟踪（产品结构/盈利能力趋势/现金流/资产负债/行业信号） |
| 5 | `research/宁德时代/research-reports.md` | 券商研报索引（待拉取方向 + 后续行动计划） |

### 数据来源
- `data/300750.db` — 9 表完整财务数据库（income/balance/cashflow/indicators/revenue_structure/spot/meta）
- `scripts/300750/business_commentary.py` — VL 流水线 business + commentary
- `scripts/300750/insert_revenue.py` — revenue_structure 录入脚本
- `scripts/config.py` — 标的配置

### 核心发现
- **盈利能力持续改善**：毛利率 20.3%→26.3% 四年连升，净利率 10.2%→18.1% 加速改善
- **储能第二曲线**：储能营收 624 亿（14.7%），增速超动力电池
- **降杠杆**：资产负债率 70.6%→61.9%，货币资金 3335 亿远超短期借款 129 亿
- **V 型反转**：2024 年营收下滑 9.7%，2025 年恢复增长 17%，归母净利大增 42%
- **data boundary**：营收拆分仅 FY2025 有 by_product，历史年份/渠道/地区不可得

### 页面更新
- `research/宁德时代/`：新建 5 个 wiki 页面
- `research/index.md`：新增 5 条目
- `research/log.md`：本次

---

## [2026-07-21] ingest | 格栅理论全书摘要精炼 + 艾德勒阅读法元摘要

### 本轮完成
- 第6-9章摘要精炼（基于 IMA 原书 PDF 逐段比对）
- 新建 wiki 页 [[艾德勒-四级阅读法]]
- 删除重复段落，更新学科清单/思维导图/Wiki关系/笔记，全书收尾对齐
- 🆕 用艾德勒四级阅读法生成全书元摘要（检视/通读/分析/比较）：文件 `raw/research/articles/hagstrom_2023_investing_last_liberal_art_艾德勒阅读法.md`

## [2026-07-21] ingest | 哈格斯特朗第6-7章精炼 + 四级阅读法 wiki 化

## [2026-07-19] ingest | 哈格斯特朗全量 raw 精炼 + wiki 同步

### 本轮完成
- 导读：分层+扩充（狐狸与刺猬 / 思维格栅 / 阅读意义）
- 前言：补充版本沿革、结构变化、无捷径警告
- 第1章：五分节+精炼+加粗，压缩至25行
- 第2章：四分节+精炼+加粗，压缩至28行
- 第3章：添加一/二/三标题
- 第4章：四层递进重构（谜题→机制→深层原因→指南针）
- 第5章：三层重写（情绪→认知→修正方案）
- 同步 concept 页、hagstrom-grid-theory.md

### 细化
- 第1章进一步精炼+加粗
- 第2章进一步精炼+加粗
- concept 页核心思想段全量刷新（新增小灯泡比喻、芒格引语、富兰克林原则详述）

## [2026-07-19] ingest | 哈格斯特朗导读+前言+第1章 raw 重构分层 + wiki 同步（旧）

### 操作
- 导读：拆为三层（一、狐狸与刺猬 / 二、思维格栅是什么为什么 / 三、阅读意义），补充芒格最爱两个模型、价值投资局限、复杂性论述
- 前言：扩充原文关键信息（版本沿革、结构变化、无捷径的警告）
- 第1章：拆为五层（一、芒格南加大演讲 / 二、富兰克林三原则 / 三、联结主义 / 四、霍兰德创新两步法 / 五、小灯泡比喻与Lollapalooza）
- 同步 hagstrom-grid-theory.md

## [2026-07-19] ingest | 哈格斯特朗第2章(物理学) raw 重写为四层结构 + wiki 同步

### 操作
- 对照原文重写：一、牛顿的均衡宇宙（开普勒/伽利略/笛卡尔→三大定律→钟表宇宙）；二、均衡进入经济学（马歇尔三层均衡+萨缪尔森）；三、均衡统治金融市场（考尔斯/肯德尔/巴舍利耶→萨缪尔森影子价格→法玛EMH→夏普CAPM）；四、对均衡的质疑（圣达菲CAS+1987股灾+审慎立场）
- 删去"布赖恩·亚瑟新旧经济学对比"——该内容属于第3章，第2章原文未展开
- 同步 concept 页和 hagstrom-grid-theory.md

## [2026-07-19] ingest | 哈格斯特朗第3章(生物学) raw 添加三层结构 + wiki 同步

### 操作
添加 ### 一/二/三 标题，内容未改

## [2026-07-19] ingest | 哈格斯特朗第4章(社会学) raw 重构为四层结构 + wiki 同步

### 操作
对照原文叙事线，将平铺式摘要重构为四层递进结构：
- 一、千古谜题：群体智慧 vs 群众性癫狂（引子→两派证据→结论：视情况而定）
- 二、运作机制：自组织临界性（自组织→涌现→巴克沙堆→预测局限）
- 三、深层原因：理查兹共识模型（巴克说"什么"，理查兹说"为什么"）
- 四、指南针与出路（四层框架→承认无知→社会≠自然→可能阻止雪崩）
- 同步 `research/articles/concepts/芒格格栅理论-多学科思维投资框架.md` 社会学段

## [2026-07-19] ingest | 哈格斯特朗第5章(心理学) raw 重写 + wiki 同步

### 问题
raw summary 将 11 个话题平行罗列，丢失了原文"情绪/认知"二分的核心结构。原文自述："心理学的研究分为两个大的方向：情绪和认知。"另外损失趋避在多个小标题下重复出现。

### 操作
- `raw/…/hagstrom_2023_investing_last_liberal_art.md`：重写为三层结构（一、情绪：预期理论→短视→交易→风险→二、认知：思维模型→信仰体系→三、修正：噪声→香农修正装置→芒格误判心理学）
- `research/…/芒格格栅理论-多学科思维投资框架.md`：心理学段按情绪/认知/修正三层重写
- `research/…/hagstrom-grid-theory.md`：Ch5 描述扩展

## [2026-07-19] ingest | 哈格斯特朗第4章(社会学) raw 补充 + wiki 同步

### 背景
对照原文 PDF 逐段比对，发现 raw summary 遗漏多个关键段落：约翰逊抗干扰实验、桑斯坦重组实验、巴克预测局限、理查兹认识论要点（信仰结构 vs 选择特异性、知识交换瓶颈）、章末指南针四层框架、最终行动洞察。

### 操作
- `raw/research/articles/hagstrom_2023_investing_last_liberal_art.md`：补充遗漏段落（5处），精炼理查兹共识模型段
- `research/articles/concepts/芒格格栅理论-多学科思维投资框架.md`：社会学段重写，新增约翰逊/桑斯坦/理查兹信仰结构框架/指南针/行动洞察
- `research/articles/papers/hagstrom-grid-theory.md`：Ch4 描述从3项扩展为完整摘要

## [2026-07-19] ingest | 哈格斯特朗第3章(生物学) raw 重写 + wiki 同步

### raw 重写
- 从清单式改写为叙事式摘要：凡勃伦→马歇尔→熊彼特→库恩→亚瑟→法默→罗闻全
- 核心补充：用"间断均衡"缝合渐进(达尔文/马歇尔)与飞跃(熊彼特/库恩)
- 补入原文遗漏细节：凡勃伦先驱、1907年熊彼特拜访马歇尔、entwicklung 词源

### wiki 同步
- `芒格格栅理论-多学科思维投资框架.md` §2(生物学) 同步更新
- 更新日期：2026-07-19

---

## [2026-07-19] ingest | 哈格斯特朗 raw 补充——生物学"间断均衡"缝合段（已废弃，被完整重写覆盖）

### 补充内容
- raw 第3章新增「渐进的 vs 飞跃的——间断均衡如何缝合矛盾」小节
- 补入原文 p.111 间断均衡引文、熊彼特拜访马歇尔轶事、entwicklung 词源、章末"范式终会坍塌"收束句
- 原因：原摘要遗漏了哈格斯特朗用生物学术语解决"自然从不飞跃 vs 进步具飞跃性"表面矛盾的关键段落

---

## [2026-07-17] lint | 全站链接校验 — 4 处断链修复

### 修复
- munger-poor-charlie-lecture2.md / hagstrom-grid-theory.md: `munger-mental-models-analysis` → `芒格格栅理论`
- 安琪酵母/overview.md: `600298/` → `安琪酵母/`
- research/index.md: `[[Wiki操作手册]]` → `[[../vl/concepts/Wiki操作手册]]`

### 状态
103 页面 · 411 链接 · 0 真实断链


## [2026-07-17] lint | Wiki 健康检查 — P0/P2 修复

### 修复清单
- 创建 `research-wiki/WIKI-SCHEMA.md`（llm-wiki 规范，整合双轨目录结构+模板+工作流）
- 修复断链：移除 `articles/concepts/munger-mental-models-analysis`（文件不存在，index.md 孤立引用）
- 修复孤儿：收录 `articles/synthesis/generational-risk-sanrio-disney-popmart` 到 index.md

### Lint 发现（P1 已修复）
- 5 标的 13 个缺失页面已全部补全（thesis/industry-chain/operating-metrics/research-reports）
- 安琪酵母 + 人福医药 raw/ 目录已创建

---

## [2026-07-17] lint | Wiki 健康检查 — P1 标的目录补全

## [2026-07-17] ingest | hagstrom_2023 — raw 文件归位 + wiki 链接修正

### 操作
- raw 文件从 `raw/research/book/` → `raw/research/articles/`（统一归入 articles 目录）
- 原 `book/` 目录已空

### 页面更新
- `articles/concepts/芒格格栅理论-多学科思维投资框架.md`：修复来源链接 → `raw/research/articles/`
- `articles/papers/hagstrom-grid-theory.md`：修复原始资料链接 → `raw/research/articles/`
- `research/log.md`：本次

---

## [2026-07-17] ingest | 《查理·芒格的智慧：投资的格栅理论》— enriched raw 再 ingest

### 背景
- 原始 raw 文件（`raw/research/articles/2026-06-28-charlie-munger-wisdom-latticework.md`）与 hagstrom 深度分析合并，含 9 类遗漏内容补全
- 合并文件移至 `raw/research/book/hagstrom_2023_investing_last_liberal_art.md`
- 原 articles 文件已删除（内容不丢失）

### 新增/更新内容
- **raw/research/book/**：新建 `hagstrom_2023_investing_last_liberal_art.md`（enriched 完整版）
- **articles/concepts/**：更新 `芒格格栅理论-多学科思维投资框架.md`
  - 补充：芒格最爱两个模型（机会成本 + 激励机制）、具体模型示例清单（8个）、库恩范式革命、C.P.斯诺两种文化、格雷厄姆投资vs投机、芒格哈佛法学院50周年演讲、E.O.威尔逊契合、9学科总结表
  - 新增第8学科（文学）完整展开：四级阅读法表格化、三大侦探方法论、圣约翰学院教育
  - 扩展第9学科（决策科学）：心智程序、勤勉的投资者、模块化思维+动态性
  - 修复来源链接 → `raw/research/book/`
- **articles/papers/**：新建 `hagstrom-grid-theory.md`（章节结构 + 人物索引 + VL关联 + 交叉引用）
- 更新：`research/index.md`、`research/log.md`

### 9 类遗漏补充明细
| # | 内容 | 融入位置 |
|---|------|------|
| 1 | 译者/出版社/推荐人/附录 | metadata |
| 2 | 8个具体思维模型示例 | 一、什么是思维模型 |
| 3 | 芒格最爱两个模型 | 一、什么是思维模型 |
| 4 | 库恩范式革命 + 简·雅各布斯 | 二、生物学 |
| 5 | C.P.斯诺两种文化 | 二、哲学 |
| 6 | 格雷厄姆投资vs投机 | 二、心理学 |
| 7 | 芒格哈佛法学院50周年演讲 | 二、决策科学 |
| 8 | E.O.威尔逊契合 | 二、决策科学 |
| 9 | 核心公式 + 9学科表 | 一、核心思想 + 三 |

## [2026-06-28] ingest | 《查理·芒格的智慧：投资的格栅理论》全书入库

- 来源：IMA 知识库「投资」PDF → 151,258 字全文提取
- 存档：`raw/research/articles/2026-06-28-charlie-munger-wisdom-latticework.md`（9 章完整摘要）
- Wiki 概念页：`articles/concepts/芒格格栅理论-多学科思维投资框架.md`
  - 7 学科 × 投资模型 + VL 体系关联 + 可深化方向
- 更新：`research/index.md`、`research/log.md`

## [2026-06-27] query | 驳论 — 拆解 Chason 对抗周期的七个论断

- 新建 `articles/synthesis/popmart-chason-rebuttal.md`
- 方法论：Molly 19年寿命证伪"3年周期"；Hello Kitty 52年证伪"代际无共鸣"；泡泡2021盲盒→2023毛绒证伪"品类转换不可靠"
- 核心反向判断："很难 ≠ 不是好生意"——泡泡的苦生意本质恰恰是护城河（别人做不了）

## [2026-06-27] ingest + query | 泡泡玛特外部观点 × 框架对比

- 原始资料：`raw/research/泡泡玛特/2026-06-17-popmart-past-present-future.md`（Chason《泡泡的过去、现在、未来》）
- 对比分析：`articles/synthesis/popmart-cycle-defense-comparison.md`
- Chason 补充了三个我们遗漏的维度：用户3年周期/平台化效率/The Monster化
- 框架升级为四层防御：IP矩阵 → 平台化 → 用户代际获取 → The Monster化

## [2026-06-27] query | 泡泡玛特历史周期防御 — 归纳四模式 × 演绎三防线 × 芒格八模型

- 新建 `articles/synthesis/popmart-historical-cycle-defense.md`
- 归纳四模式：IP矩阵熨平 / 品类形态转换（IP不变载体变）/ 地理扩张对冲 / 价格带拉宽
- 演绎三防线：签约-孵化-分发链条 / IP先行品类跟随 / 全球=周期地理对冲
- 核心发现：护城河不是2021年前有的，是2022年危机中建造的（冗余备份的工程学思维）

## [2026-06-27] query | 泡泡玛特抵御IP/品类周期 — 代际转化的本质

- 新建 `articles/synthesis/popmart-ip-cycle-defense.md`
- 核心：两种周期（IP可管理 / 品类需转换）→ 代际转化的本质（身份表达需求的载体代际更替）
- 防御：唱片公司模型（批量制造中等IP）、形态转换（盲盒→毛绒→MEGA→下一形态）
- 茅泡对比：茅台产品不变用户变，泡玛产品可随用户一起变

## [2026-06-27] query | 泡泡玛特"买不买 vs 买多少" — 三层拆解 × 茅台对称性

- 新建 `articles/synthesis/popmart-demand-decomposition.md`
- 核心发现：泡泡玛特与茅台消费逻辑完全同构——"会不会×多少×花多少钱"三层拆解
- 关键差异：茅台护城河是千年文化（极深极窄），泡泡玛特是IP迭代+机制驱动+全球扩张（四条腿）
- 四变量分解：数量 = 人数×件数×单价×频次，独有的"抽盒机制"放大"每次买几个"
- 芒格八模型映射：可变奖励/禀赋效应/Lollapalooza正负向/生态位/存量流量区分

## [2026-06-27] query | 茅台"喝不喝 vs 喝多少" — 归纳演绎 × 芒格模型

- 新建 `articles/synthesis/maotai-drink-logic-analysis.md`
- 核心发现：成瘾性保护"喝不喝"（二元变量），但"喝多少"由场景驱动（连续变量），两者机制不同
- 方法论：归纳假设 → 演绎拆解（四变量分解）→ 反过来想 → 实证闭环
- 芒格七模型映射：数学拆解/反过来想/双轨分析/Lollapalooza/心理学/会计学/生物学

## [2026-06-27] ingest | 芒格多元思维模型·《穷查理宝典》精读
- `raw/research/articles/munger-multidisciplinary-thinking.md` — 《穷查理宝典》第二章 + 第四讲第二讲全文精要（移至 raw/）
  - 核心理念：多元思维模型框架（100种模型，最重要的仅几个）
  - 六大核心学科模型：数学/会计/硬科学/生物学/心理学/微观经济学
  - 投资应用：能力圈 → 护城河 → 安全边际 → 双轨分析
  - 五大超级观念 + 投资原则检查清单（风险/独立/准备/谦虚/严格分析/配置/耐心/决心/改变/专注）
  - 来源：EPUB 原文提取，约 440 行第二讲全文 + 第二章 10 个段落

## [2026-06-27] ingest | research/ 全面重组 + raw/research/ 全面 ingest

### 目录重组
- 合并 articles/index.md、log.md、overview.md → research/ 级别
- 新建 `research/overview.md` — 投研 wiki 命名空间概述
- 更新 `research/index.md` — 含 articles/concepts|entities|papers|synthesis 四子目录

### 全面 ingest
- `research/TCL中环/research-reports.md` — 新建券商研报索引 (民生/国金/国联 5篇)
- `research/articles/` 四子目录全部已覆盖：
  - concepts/: Arthur收益递增、投资框架
  - entities/: Seth Klarman 访谈
  - papers/: 投资框架参考著作
  - synthesis/: 大航周报76

### 原始资料验证
- `raw/research/articles/` 5 篇全部有对应 wiki (含重建的 dahang-weekly)
- `raw/research/TCL中环/` 5 篇研报已通过 research-reports.md 索引
- `raw/research/润泽科技/` idc-operating-metrics 已有 wiki

## [2026-06-27] ingest | research/articles/ — 投研文章目录

### 新建 articles 目录
- `research/articles/index.md` — 文章索引（投资大师/投资框架/行业跟踪）
- `research/articles/seth-klarman-interview.md` — Klarman 访谈 wiki 页
- `research/articles/arthur-increasing-returns.md` — Arthur wiki 页
- `research/articles/dahang-weekly-76.md` — 大航周报76
- `research/articles/投资框架-参考著作.md` — 参考著作 wiki 页

### 原始资料
- `raw/research/articles/2026-06-25-seth-klarman-interview.md`
- `raw/research/articles/2026-06-26-dahang-weekly-76.md`

### 索引更新
- `research/index.md` 新增 articles/ 入口

## [2026-06-26] ingest | 润泽科技 300442 — IDC/AIDC 运营指标跟踪

### 摄入内容
- pdfplumber 从 2022-2025 年报 + 中报提取成本构成表（电费/折旧/薪酬）和经营讨论章节
- 原始资料：`raw/research/润泽科技/2026-06-26-idc-operating-metrics.md`

### Wiki 产出
- `research/润泽科技/operating-metrics.md` — 新建运营指标跟踪页
  - 核心 KPI：上架率(>90%)、PUE(1.09)、运营规模(750MW)、规划规模(6GW)
  - 电费成本：年报半年度完整对比表（2022-2025），IDC+AIDC 分拆
  - 电费比率趋势：70%→43%→46%，AIDC折旧(28%)远超电费(10.5%)
  - 数据可用性边界：季度不可得

### 关键发现
- AIDC是"折旧驱动"（28%）而非"电费驱动"（10.5%），与IDC相反
- 2025总电费13.99亿，同比+47%，AIDC电费+125%首次披露
- 2025年交付220MW，超过去16年累计的40%

### 页面更新
- `research/index.md` — 新增 [[润泽科技/overview]] + [[润泽科技/operating-metrics]]
- `research/log.md` — 本次

---

## [2026-06-25] ingest | Arthur 收益递增与涌现 — 理论深化

### 摄入内容
- W. Brian Arthur 1999 *Science* 论文《Complexity and the Economy》原文核对
- 涌现定义 + 正反馈/收益递增主导论的关系梳理
- 原始资料：`raw/research/articles/2026-06-25-arthur-increasing-returns-emergence.md`

### Wiki 产出
- `vl/concepts/Arthur-收益递增与涌现.md` — 新建理论概念页
- `raw/research/articles/投资框架-复杂经济学指导手册.md` §1.1 — 添加交叉引用

### 核心要点
- Arthur 1999 年即提出：涌现 = 复杂系统定义，正反馈 = 涌现的机制条件
- 与投资框架衔接：识别正反馈回路是识别极端赢家的第一步

---

## [2026-06-23] ingest | 安琪酵母 (600298) 投研体系初始化 — 3 wiki 页面

### 摄入内容
- 2025年报 MDA 全文 → `raw/research/安琪酵母/2025-mda-text.md`（pdfplumber 自动提取）
- VL 阅读报告摘要 → `raw/research/安琪酵母/2026-06-23-vl-report.md`（generate_reading.py 生成）

### 创建的 wiki 页面

| # | 页面 | 内容 |
|---|------|------|
| 1 | `research/安琪酵母/overview.md` | 数据目录（DB表结构、revenue_structure、毛利率趋势、数据源映射） |
| 2 | `research/安琪酵母/industry-chain.md` | 产业链全景（酵母上中下游、成本结构、竞争格局、毛利率周期） |
| 3 | `research/安琪酵母/thesis.md` | 投资Thesis（四业务赚钱逻辑、四大护城河、四风险、五催化剂、VL评级） |

### 核心发现
- **海外毛利率 32.1% vs 国内 19.7%**：全球化利润结构性改善是最大 alpha
- **毛利率 2025 年首次企稳回升**（+1.2pp），利润率反转信号已触发
- **竞争格局一超稳定**：国内 55% 市占率 + 乐斯福 14% + 马利 11%
- **糖蜜价格是最大变量**：占成本 40%+，2021 年暴涨导致毛利率断崖 37.6% → 27.3%
- **数据源混合**：财务指标/报表来自 AKShare（自动），营收拆分/竞争格局来自年报手动录入

### 页面更新
- `raw/research/安琪酵母/`：新增 2 份原始资料
- `research/安琪酵母/`：新增 3 个 wiki 页面
- `research/index.md`：新增 3 条目（置顶）
- `research/log.md`：本次

---

## [2026-06-23] ingest | TCL中环 002129 券商研报拉取 — 3篇核心研报

### 摄入内容（AKShare 列表 → web_search → web_fetch 全文）

| # | 机构 | 日期 | 评级 | 标题 |
|---|------|------|------|------|
| 1 | 国金证券 | 2026-03-25 | 增持 | 一体化布局加速，技术专利优势渐显 |
| 2 | 国金证券 | 2025-10-29 | 增持 | 亏损显著收窄，反内卷带动盈利能力修复 |
| 3 | 民生证券 | 2025-08-26 | 买入 | 成本与运营持续优化，组件业务亏损收窄 |

### 研报核心发现
- **硅片工费降超 40%**（三家一致），成本优势在周期底部持续强化
- **BC 专利授权爱旭 16.5 亿**（2026-02 宣布），"破除内卷式竞争"新武器
- **盈利预测分歧**：国金最新（2026-03）将 2026E 从 +12亿 调至 -23亿，拐点推迟
- **三家共识 2027 年扭亏**：国金 27亿 / 民生 22.5亿

### 方法论修正
- 宪法规则修正：PDF 直链下载不可行（东方财富反爬），改为 AKShare 列表 + web_search
- 研报拉取优先级：用户手动传入 > web_search > AKShare 列表

### 页面更新
- `raw/research/TCL中环/`：新增 3 份研报摘要
- `research/TCL中环/thesis.md`：新增「七、券商研报跟踪」（盈利预测对比 + 信号分析）
- `research/index.md`、`log.md`：本次

## [2026-06-23] ingest | TCL中环 002129 深度分析 — 投资 Thesis + 产业链全景

### 摄入内容
- 新建 `raw/research/TCL中环/2026-03-25-证券之星-2025年报分析.md` — 2025 年报经营分析（财务数据、业务进展、核心竞争力、行业破局）
- 新建 `raw/research/TCL中环/2026-04-02-国联民生证券-2025年报点评.md` — 券商点评（硅片龙头 + 一体化布局 + 盈利预测 + 风险）

### Wiki 产出
- `research/TCL中环/thesis.md` — 投资 Thesis（四业务赚钱逻辑、四大护城河、六大风险、五大催化剂、估值观点、验证节点）
- `research/TCL中环/industry-chain.md` — 产业链全景（光伏产业链定位 + 半导体硅片产业链 + 商业模式演进 + 竞争格局 + 行业周期判断）

### 数据细节
- 硅片工费同比降超 40%，全球市占率第一（23.5%），G12 出货 +40.8%
- 组件出货 15.1GW（+60.45%），半导体出货超 1200MSI（+21.75%）
- BC 专利授权爱旭 16.5 亿，拟收购一道新能源
- 券商预计 2027 年扭亏（24.57 亿），PE=15x

### 页面更新
- `research/index.md` — 新增 [[TCL中环/thesis]] + [[TCL中环/industry-chain]]
- `research/log.md` — 本次

## [2026-06-22] ingest | 人福医药 600079 子公司营收全景

### 新增数据
- 从 2025 年报 PDF (Page 49) 提取 6 家主要子公司营收/净利/净资产数据
- 从 Page 23 提取集团分行业毛利率（制造业 72.31% / 批发 12.90%）

### 数据要点
- 宜昌人福 88.10亿 / 27.48亿 / ROE 24.9% — 一柱擎天
- EpicPharma 净利 1.40→0.17亿 (-88%)，关税冲击
- 归母结构：宜昌人福贡献 118% 归母净利，其他 5 家拖累

### Wiki 产出
- `人福医药/overview.md` — 更新为子公司营收全景（表 + ROE + 净利率 + 毛利率参考 + 归母拆分）
- `index.md` + `log.md` — 更新

## [2026-06-20] ingest | 人福医药 600079 应收账款深度分析

### 分析范围
- AR 规模：94.35 亿（合并），AR/营收 39.4%，周转 142 天（2018-2025 趋势）
- 账龄结构：89.6% 1 年内，长账龄 AR 增速异常（1-2 年 +43%）
- 前五大欠款方 27.74 亿（28.4%），均为国药/上药/三甲医院
- 现金流影响：每年消耗 8-10 亿经营现金流
- 行业对比：恩华药业 AR 96 天 vs 人福 142 天；行业均值 制造 91 天/流通 140-152 天
- 分部报告限制：年报只有一个分部，不披露制造/批发各自 AR

### 关键发现
- 人福 AR 问题不能完全归因于批发业务——即使按合理假设拆分，仍有 ~15 亿缺口
- 制造端回款效率可能也低于恩华药业
- 综合判断：恶化趋势明确但无系统性坏账风险，招商局入主后需关注是否推动 AR 保理

### 数据来源
- 2025 年报 P148-151（账龄+坏账+前五大）、P239（分部报告）、P49-50（子公司）
- `data/600079.db`（balance/income/cashflow 表历史数据）
- 外部：商务部药品流通报告、Investing.com 恩华 AR 周转率、行业对比文章

### 页面更新
- `research/人福医药/overview.md` 新增「应收账款分析」六大模块

### 原始资料
- 行业背景 web search 结果已整合进 wiki，无需另存 raw

## [2026-06-20] query | 人福医药 600079 中枢神经业务深度分析

### 分析内容
- 中枢神经业务营收 92.25 亿，毛利率 86.32%，同业恩华药业 85.03%
- 核心子公司宜昌人福（80%）：营收 88.10 亿，净利 27.48 亿，国家麻醉药品定点研发生产基地
- 芬太尼系列（舒芬太尼/瑞芬太尼/阿芬太尼）属"麻醉药品和第一类精神药品"，**不参与集采**
- 2025 年新获批 9 个品种（含盐酸他喷他多片、琥珀酸地文拉法辛缓释片等）
- 研发管线：CXJM-66（III 期）、HW231019（II 期），向精神分裂症/ADHD/抑郁症拓展
- 竞争格局：恒瑞医药（600276）、恩华药业（002262），管制牌照为核心护城河

### 数据来源
- 2025 年报 PDF（`data/pdfs/600079/600079_2025_年报.pdf`，252 页）
- `scripts/600079/business_commentary.py`、`insert_revenue.py`
- `report_data.json`（600079 完整数据）

### 数据目录页
- `research/人福医药/overview.md` — revenue_structure + CNS 业务 6 大模块

### 索引更新
- `research/index.md` 新增 [[人福医药/overview]]

## [2026-06-19] ingest | TCL中环 002129 首次入库 + VL 报告

### 新增标的
- `config.py` → STOCKS 添加 002129（TCL中环，A股 SZSE，org_id=9900002703，总股本 40.43 亿）
- `data/002129.db` — 9 表完整财务数据库（2004-2026，最近 15 年用于报告）
- `data/pdfs/002129/` — 47 份年报/中报/季报 PDF

### 营收结构
- `scripts/002129/insert_revenue.py` → `revenue_structure` 表，`dim_type='by_product'`
- 2021-2025 年，每年 4-5 产品线（光伏硅片/光伏组件/半导体材料/电站/其他），共 21 条

### VL 报告
- `report/TCL中环.html` — PB=1.0x，8 步流水线 68/72 PASS（PE/EPS/CAGR 因亏损预期内 FAIL）
- `report/reading/002129.md` + `.html` — 李录阅读法融合版

### 数据目录页
- `research/TCL中环/overview.md` — revenue_structure 表结构 + 产品速查表 + 占比演变

### 索引更新
- `report/index.html` 重建（43 标的 16 行业）
- `research/index.md` 新增 [[TCL中环/overview]]

## [2026-06-17] ingest | 泡泡玛特 09992 数据目录

### 新增数据
- `data/09992.db` → `revenue_structure` 表，`dim_type = 'china_online_channel'`
- 2021-2025 年，每年 4 子渠道（抽盒机/天猫/京东/抖音/其他），共 20 条
- 金额单位：百万元人民币

### 数据目录页
- `泡泡玛特/overview.md` — revenue_structure 表结构 + 全维度说明 + SQL 查询示例 + 速查表 + 二元汇总

### 原始资料
- 年报 PDF 原文保留在 `data/pdfs/09992/`（2021-2025 年报），不再另存 raw

## [2026-06-17] init | 投研 wiki 初始化

## [2026-08-01] lint | research-wiki 健康检查

### 操作
- 运行 `scripts/wiki_lint.py` 全量检查 166 个 .md 文件（raw 36 / vl 36 / research 93）
- 检查项：结构完整性 / frontmatter / 断链 / 参见区块 / index 注册 / 孤立页面 / 内容质量 / raw 命名

### 修复（research/ 命名空间 5 处断链）
- `查理·芒格.md`：raw 文件名 kaufman_2005_poor_charlies_almanack → 考夫曼_2005_穷查理宝典
- `倾覆力矩.md`、`竞争性毁灭.md`：同上 + munger-critical-mass → 芒格-临界质量
- `TCL中环/research-reports.md`：`[[../../raw/research/TCL中环/]]` 目录链接 → 代码块

### 剩余发现（76 WARN / 5 INFO）
- 缺失概念页 20 处（均值回归/复杂适应系统/实用主义/思维格栅模型/有效市场假说/行为金融学/贝叶斯定理/Lollapalooza效应/人类误判心理学/能力圈原则/逆向思维 等）
- frontmatter 缺失 14 页（articles/concepts|synthesis + 润泽科技/operating-metrics + overview）
- 参见区块缺失 24 页（synthesis 系列普遍缺失）
- 内容过少 5 页（TCL科技/云铝/京东方/时代天使/神火 research-reports 仅 4 行）
- vl/synthesis/ 空目录
- `[[articles/concepts/arthur-increasing-returns]]` 在本 log 及 vl/log 历史条目中，按只追加规则不改

触及页面：查理·芒格.md、倾覆力矩.md、竞争性毁灭.md、TCL中环/research-reports.md
