# 投研操作日志

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
