# -*- coding: utf-8 -*-
"""ai_sw_rank.py — 按「AI 吞噬顺序」给 AI 软件候选池分层排序

标准来源（三篇原文，均为庶人哑士）
---------------------------------
1. 《大模型吞噬软件：是叙事还是事实？》2026-09-24
   raw/research/articles/2026-09-24-庶人哑士-大模型吞噬软件-是叙事还是事实.md
2. 《关于AI应用的十个判断》2026-09-19  ← 判据主体（10a/10b/10c + 第 9 条四级跃迁）
   raw/research/articles/2026-09-19-庶人哑士-关于AI应用的十个判断.md
3. 《AI应用随想录》2026-09-02        ← 本体层（Ontology）定义
   raw/research/articles/2026-09-02-庶人哑士-AI应用随想录.md

作者的「谁会被吞噬 / 谁不会被」——原文摘录
------------------------------------------
- 10a「模型能力越来越强之后，做得最浅的工具型应用会被模型吞掉，比如美图、做个 PPT 这些」→ **L0 回避**
- 10b「像 Palantir 那种做的又深又重又垂直细分的，模型能力反而是赋能，而不会是吞噬。
       它们有着大模型最羡慕却拿不到的私有数据和进不去的真实业务场景」→ **L1 最优**
- 10c「还有一些领域，需要做深做重做垂直细分但价值量不大，模型公司深入不进去，体量又长不出
       一家 Palantir。这种长尾市场……适合 workbuddy 应用市场这种模式。而应用市场最稀缺的能力
       不是丰富，而是筛选判断」→ **L4**
- 第 9 条四级跃迁「帮客户数据治理➡️落自己的数据中台➡️本体层搭建➡️AIOS落地
       ＝ 土路➡️铺装路面➡️高速公路➡️AI跑车」→ **L3 修路 → L2 中台 → L1 本体/AIOS**
- 《随想录》「AI应用投资，就是要避开那些工具型的SaaS，去找到那些干本体活儿的公司……
       只要是在某个细分领域，能够让大模型理解具体业务，让 Agent 跑起来干活儿的就行」

作者的验证指标 → 本项目的近似代理
---------------------------------
   营收增长（谁跑得快）  →  26H1 营收同比          ✅ 可得
   NDR（谁做得深）       →  ❌ 不可得 → 近似用「毛利率 + 是否盈利」代替（产品化/议价能力）
   ⚠️ NDR 是作者的**核心**指标，本脚本拿不到，所有 L1/L2 结论都标记为「待中报核实」

用法
----
  .venv\\Scripts\\python scripts\\ai_sw_rank.py

输出
----
  scripts/out/ai_sw_rank.csv      排序后的全池（含层级）
  scripts/out/ai_sw_rank.md       分层表格片段（供 wiki 页面引用）
"""
import argparse
import csv
import os
import sys

import pandas as pd

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

_HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(_HERE, "out")

# ── 层级定义 ──
LAYERS = [
    ("L0", "被吞噬区：浅层工具型", "产品的核心功能本身就是通用大模型的基础能力"
     "（OCR/识别/图片视频编辑/PDF/语音/简单生成），无企业流程绑定、切换成本极低。"
     "→ 按 10a，**回避**"),
    ("L1", "本体层 / AIOS：被 AI 赋能", "在某一垂直行业握有 system of record：数据带业务语义与勾稽关系、"
     "有权限与工作流（谁能在什么条件下改什么）、能把动作**写回**底层系统执行、"
     "握有模型拿不到的私有数据与进不去的真实场景。→ 按 10b，**最优**"),
    ("L2", "数据中台层：跃迁期权", "数据平台/数据库/大数据底座/核心系统外包，客户数据已跑在其上"
     "（换中台如高速换轮子），但尚未到语义与动作层。→ 第 9 条第二级，**次优**"),
    ("L3", "数据治理 / 修路：周期红利", "帮客户把土路修成铺装路。项目制、人头计费、毛利率 7-25%，"
     "短期营收爆发但商业模式未跃迁。→ 第 9 条第一级，**不是终局**"),
    ("L4", "长尾 Agent / 应用市场：赔率高难挑", "做深做重但价值量不大的单点场景、AI 原生应用、Agent 平台与分发。"
     "→ 按 10c，**关键能力是筛选判断而非丰富**"),
]

# ── 逐只归类 ──
# ⚠️ 作者只在文章中点名过 Palantir / 迈富时 / 北森 / 美图 等极少数公司。
#    以下对 A 股的归类均为**本项目按上述原文的判定特征所作推断**，逐只标「待核」。
RANK = {
    # ── L0：核心能力本身就是模型原生能力 ──
    "L0": [
        "688095",  # 福昕软件  PDF 工具，AI 可直接生成/解析 PDF
        "300624",  # 万兴科技  视频/图形编辑，与美图同类
        "688615",  # 合合信息  扫描/OCR（模型原生能力）；毛利率 87% 但护城河来自入口不是场景
        "688318",  # 财富趋势  行情终端是典型工具
        "688088",  # 虹软科技  手机视觉算法，卖算法包，模型能力越强越不值钱
        "300229",  # 拓尔思    NLP，被 LLM 替代风险最直接
        "688327",  # 云从科技  CV 四小龙，同上
        "688207",  # 格灵深瞳  CV
        "688343",  # 云天励飞  算法+芯片，纯 AI 能力供给方
        "01357",   # 美图      ★作者点名为被吞噬代表（10a 原文）
    ],
    # ── L1：垂直行业的本体层 ──
    "L1": [
        "600588",  # 用友网络  ERP/BIP，企业财务与流程的 system of record
        "603039",  # 泛微网络  OA＝组织架构/审批流/汇报关系，正是本体「动力学元素」
        "688777",  # 中控技术  工业：工艺流程+实时数据+写回控制执行
        "002410",  # 广联达    建筑：国标清单/成本/施工 know-how，极深垂直
        "301269",  # 华大九天  EDA：研发流程内核
        "688206",  # 概伦电子  EDA
        "301095",  # 广立微    EDA 良率
        "688188",  # 柏楚电子  激光切割控制系统，直接写回执行设备
        "600845",  # 宝信软件  钢铁行业 MES/产线，数据与场景都在自己手里
        "600570",  # 恒生电子  券商核心交易与清算，金融 system of record
        "300348",  # 长亮科技  银行核心系统
        "002153",  # 石基信息  酒店 PMS / 零售 POS，垂直极深
        "603171",  # 税友股份  税务规则库
        "300253",  # 卫宁健康  医疗 HIS/EMR
        "300451",  # 创业慧康  医疗 HIS
        "002063",  # 远光软件  电力财务/ERP
        "002230",  # 科大讯飞  ⚠️争议：语音是模型原生能力，但教育/医疗私有场景深厚
        "301638",  # 南网数字  电网场景与数据在自己体系内
        "00696",   # 中国民航信息网络  航司订座/离港垄断 system of record（港股）
    ],
    # ── L2：数据中台 / 底座 ──
    "L2": [
        "300378",  # 鼎捷数智  制造业 ERP
        "300687",  # 赛意信息  制造 MES/ERP（偏实施）
        "603859",  # 能科科技  PLM/MBSE
        "688083",  # 中望软件  CAD/CAE 设计工具+know-how 混合
        "688507",  # 索辰科技  CAE 仿真
        "688692",  # 达梦数据  国产数据库底座
        "688031",  # 星环科技  大数据基础软件
        "688258",  # 卓易信息  BIOS/BMC 固件底座
        "300674",  # 宇信科技  银行 IT
        "603927",  # 中科软    保险 IT
        "300377",  # 赢时胜    资管 TA
        "600446",  # 金证股份  证券 IT
        "603383",  # 顶点软件  证券交易系统
        "300682",  # 朗新科技  电力营销系统
        "688479",  # 用友汽车  汽车经销
        "301153",  # 中科江南  财政支付
        "300525",  # 博思软件  财政票据
        "688232",  # 新点软件  政务招投标
        "688109",  # 品茗科技  建筑施工安全
        "002777",  # 久远银海  人社/医保
        "300166",  # 东方国信  大数据
        "688568",  # 中科星图  数字地球/遥感
        "300496",  # 中科创达  操作系统+智能座舱软硬一体
        "03317",   # 迅策      资管数据平台（港股·作者点名）
        "01384",   # 滴普科技  数据智能（港股·作者点名）
        "02718",   # 明略科技  数据智能/门店数字化（港股·作者点名）
    ],
    # ── L3：数据治理 / 修路 ──
    "L3": [
        "300170",  # 汉得信息  ERP 实施咨询
        "300520",  # 科大国创  政企软件+数据治理
        "600536",  # 中国软件  信创集成
        "002368",  # 太极股份  系统集成
        "920799",  # 艾融软件  银行 IT 解决方案
        "688562",  # 航天软件  军工软件
        "300085",  # 银之杰    金融信息化
        "300468",  # 四方精创  银行 IT
        "002987",  # 京北方    银行 IT 外包（毛利 21%）
        "300872",  # 天阳科技  银行 IT
        "300075",  # 数字政通  政务
        "002279",  # 久其软件  报表管理
        "688158",  # 优刻得    云 IaaS，算力层非本体层
    ],
    # ── L4：长尾 Agent / 应用市场 ──
    "L4": [
        "688111",  # 金山办公  ⚠️争议：文档工具 vs 组织文档资产 + 私有化 + WPS AI
        "688365",  # 光云科技  电商 SaaS，小微客户
        "002315",  # 焦点科技  跨境 B2B 平台 + AI 外贸助手
        "301162",  # 国能日新  新能源功率预测，典型单点价值量有限的 AI 场景
        "301556",  # 托普云农  农业 SaaS
        "002530",  # 金财互联  财税服务
        "603990",  # 麦迪科技  医疗专科
        "300766",  # 每日互动  数据服务
        "688787",  # 海天瑞声  AI 训练数据（供给侧，非被吞噬但格局分散）
        "02556",   # 迈富时    营销 Agent ★作者点名，且明言是「先卖 Agent 再渗透中台」的难路径
        "09669",   # 北森控股  HR Agent ★作者点名，同为难路径；但 HR 的组织数据是本体素材
        "06608",   # 百融云    风控决策服务 ★作者点名，⚠️26H1 营收 -43.3%
    ],
}

# 作者框架未覆盖的一层：网络安全（11 只）。
# 《大模型吞噬软件》路径 1 提到 Palantir/北森「把 RBAC 变成 agent 的操作边界」——
# 即权限体系是本体的一部分，故安全公司单列，不强行塞进 L1/L2。
SECURITY = ["601360", "300454", "688561", "002439", "002268", "600271",
            "300768", "300188", "002212", "300369", "688225"]

# 港股点名 7 家（26H1 数据来自 TDX 损益表，与既有页面一致；单位亿元）
# 来源：scripts/tdx_client.py（09669/06608/02718）+ 学股/AI软件名单-港股通待选池.md（其余 4 只）
HK_ROWS = [
    dict(market="HK", code="00696", name="中国民航信息网络", layer="L1", mktcap_yi=255.0,
         pe=9.2, pb=0.89, rev=41.12, yoy=5.6, np_=23.42, note="25FY归母；26H1营收"),
    dict(market="HK", code="03317", name="迅策", layer="L2", mktcap_yi=348.0,
         pe=450.1, pb=12.17, rev=9.67, yoy=388.8, np_=-0.94, note="25FY归母"),
    dict(market="HK", code="01384", name="滴普科技", layer="L2", mktcap_yi=101.0,
         pe=-13.8, pb=7.36, rev=2.84, yoy=115.0, np_=-9.35, note="25FY归母"),
    dict(market="HK", code="02718", name="明略科技", layer="L2", mktcap_yi=None,
         pe=None, pb=None, rev=7.60, yoy=18.0, np_=-0.69, note="非港股通；26H1归母"),
    dict(market="HK", code="02556", name="迈富时", layer="L4", mktcap_yi=149.0,
         pe=50.6, pb=5.11, rev=19.60, yoy=111.2, np_=0.89, note="25FY归母"),
    dict(market="HK", code="09669", name="北森控股", layer="L4", mktcap_yi=None,
         pe=None, pb=None, rev=11.05, yoy=16.9, np_=-0.23, note="非港股通；FY2026(截至03-31)"),
    dict(market="HK", code="06608", name="百融云创", layer="L4", mktcap_yi=None,
         pe=None, pb=None, rev=9.14, yoy=-43.3, np_=-3.20, note="非港股通；26H1归母"),
    dict(market="HK", code="01357", name="美图公司", layer="L0", mktcap_yi=168.0,
         pe=18.2, pb=2.50, rev=22.13, yoy=21.5, np_=5.83, note="★作者点名为被吞噬代表(10a)"),
]

LAYER_NAME = {k: v for k, v, _ in ((a, b, c) for a, b, c in LAYERS)}
ORDER = {"L1": 0, "L2": 1, "L3": 2, "L4": 3, "SEC": 4, "L0": 5}


def load_a():
    df = pd.read_csv(os.path.join(OUT, "ai_sw_a_pool.csv"))
    df["code6"] = df["code"].astype(str).str.zfill(6)
    return df[df["tier"] == "核心"]  # 只对核心软件 83 只排序


def build():
    df = load_a()
    idx = {c: layer for layer, codes in RANK.items() for c in codes}
    idx.update({c: "SEC" for c in SECURITY})

    rows = []
    seen = set()
    for _, r in df.iterrows():
        c6 = r["code6"]
        lay = idx.get(c6)
        if lay is None:
            print("  ⚠️ 未分层：%s %s（group=%s）" % (c6, r["name"], r["group"]))
            continue
        seen.add(c6)
        rows.append(dict(market="A", code=c6, name=r["name"], layer=lay,
                         group=r["group"], mktcap_yi=r["mktcap_yi"], pe=r["pe"],
                         pb=r["pb"], rev=r["rev_26h1"], yoy=r["rev_yoy_calc"],
                         np_=r["np_26h1"], gm=r["gm_26h1"], gm_chg=r["gm_chg_pp"], note=""))
    for h in HK_ROWS:
        h.setdefault("group", "")
        h.setdefault("gm", None)
        h.setdefault("gm_chg", None)
        h["code6"] = h["code"]
        rows.append(h)

    missing = [c for c in idx if c not in seen and len(c) == 6 and c not in
               {h["code"] for h in HK_ROWS}]
    if missing:
        print("  ⚠️ 以下代码在核心池中不存在或不匹配：%s" % ", ".join(missing))

    out = pd.DataFrame(rows)
    out["_o"] = out["layer"].map(ORDER)
    # 层内排序：营收同比降序（作者「谁跑得快」）→ 缺失排最后
    out = out.sort_values(["_o", "yoy"], ascending=[True, False])
    return out


def fmt(v, d=1):
    if v is None:
        return "-"
    try:
        if pd.isna(v):
            return "-"
    except TypeError:
        pass
    return round(float(v), d)


# 用户 2026-09-24 确认的三层框架（本项目的最终口径）
#   ① 浅层工具：最先被吃 → 回避
#   ② 本体层：吃不到，模型反而是赋能 → 最优
#   ③ 长尾 workbuddy：也吃不到但没人去吃 → 有，难挑
# L2（数据中台）/ L3（修路）/ SEC（网络安全）是作者第 9 条四级跃迁里的中间态
# 与框架未覆盖项，**不属于三层中的任何一层**，单列为「中间态 / 框架外」。
LAYER3 = {"L0": "① 浅层工具（最先被吃）", "L1": "② 本体层（吃不到·赋能）",
          "L4": "③ 长尾 workbuddy"}


def filter3(out):
    """按用户确认的三层框架输出筛选结果（含中间态/框架外的统计）"""
    rows = []
    for _, r in out.iterrows():
        rows.append({
            "layer3": LAYER3.get(r["layer"], "中间态 / 框架外"),
            "src": r["layer"], "market": r["market"], "code": r["code"],
            "name": r["name"], "mktcap_yi": r["mktcap_yi"], "pe": r["pe"],
            "rev": r["rev"], "yoy": r["yoy"], "np_": r["np_"],
            "gm": r["gm"], "gm_chg": r["gm_chg"],
        })
    d = pd.DataFrame(rows)

    print("\n" + "=" * 62)
    print("按三层框架筛选（91 只）")
    print("=" * 62)
    for key in ("① 浅层工具（最先被吃）", "② 本体层（吃不到·赋能）", "③ 长尾 workbuddy"):
        sub = d[d["layer3"] == key]
        prof = sum(1 for _, r in sub.iterrows() if r["np_"] is not None
                   and not pd.isna(r["np_"]) and float(r["np_"]) > 0)
        print("\n%s ：%d 只（26H1 盈利 %d 只）" % (key, len(sub), prof))
        for _, r in sub.iterrows():
            print("  %-6s %-14s 市值%8s  PE%9s  26H1营收%8s  同比%8s  归母%8s" % (
                r["code"], str(r["name"])[:13], fmt(r["mktcap_yi"]), fmt(r["pe"]),
                fmt(r["rev"], 2), fmt(r["yoy"]), fmt(r["np_"], 2)))

    mid = d[d["layer3"] == "中间态 / 框架外"]
    print("\n中间态 / 框架外 ：%d 只" % len(mid))
    for src in ("L2", "L3", "SEC"):
        s = mid[mid["src"] == src]
        print("  %-4s %d 只：%s" % (src, len(s),
              "、".join("%s%s" % (r["code"], r["name"]) for _, r in s.iterrows())))

    with open(os.path.join(OUT, "ai_sw_filter3.csv"), "w", encoding="utf-8-sig",
              newline="") as f:
        w = csv.DictWriter(f, fieldnames=["layer3", "src", "market", "code", "name",
                                          "mktcap_yi", "pe", "rev", "yoy", "np_",
                                          "gm", "gm_chg"], extrasaction="ignore")
        w.writeheader()
        w.writerows(d.to_dict("records"))
    print("\n已写入 scripts/out/ai_sw_filter3.csv")
    return d


# 作者原文点名的 15 家（09-24 那篇）：美股 8 + 港股 7
NAMED_HK = {"02556", "09669", "01357", "06608", "01384", "03317", "02718"}
NAMED_US = {"PLTR", "SAP", "CRM", "HUBS", "WDAY", "DDOG", "SNOW", "NET"}
NAMED = NAMED_HK | NAMED_US

# 美股 8 家按同一把尺子的判读（本项目推断，作者只点名未分层）
# 依据：《十个判断》第 5 条「ERP、CRM 这类 system of record……就像一张张定格后的照片，
#       却没有从 A 到 B 的过程」→ SAP/CRM/WDAY/HUBS 握 record 缺过程，只够 L2
US_JUDGE = [
    ("PLTR", "Palantir", "② 本体层", "作者 10b 明说的唯一原型", 44.8, 56.2),
    ("SNOW", "Snowflake", "中间态 L2", "路径1：数据库变 agent 的记忆与知识库＝底座", 36.3, 29.2),
    ("SAP", "SAP", "中间态 L2", "第5条：ERP 是「定格照片」，缺过程", 415.3, 12.3),
    ("CRM", "Salesforce", "中间态 L2", "同上，CRM 同为定格照片", 378.9, 8.7),
    ("WDAY", "Workday", "中间态 L2", "HR system of record，与北森同类", 84.2, 16.9),
    ("HUBS", "Hubspot", "中间态 L2", "营销 SaaS，更轻", 31.3, 19.2),
    ("DDOG", "Datadog", "中间态 L2", "路径1：日志变 agent 行为证据＝可观测底座", 34.3, 27.7),
    ("NET", "Cloudflare", "框架外", "边缘网络/安全，三篇原文无对应层", 21.7, 29.9),
]


def final41(out):
    """用户 2026-09-24 拍板的最终口径：只保留落在三层框架内的 41 只，
    层内「作者点名优先 → 26H1 营收同比降序」"""
    d = out[out["layer"].isin(("L0", "L1", "L4"))].copy()
    d["named"] = d["code"].isin(NAMED)
    d["_l"] = d["layer"].map({"L1": 0, "L4": 1, "L0": 2})
    d = d.sort_values(["_l", "named", "yoy"], ascending=[True, False, False])

    hdr = ("| 代码 | 名称 | 点名 | 市值亿 | PE | 26H1营收 | 同比% | 26H1归母 | 毛利率% | Δpp |\n"
           "|---|---|---|---|---|---|---|---|---|---|")
    chunks = []
    for lay, title in (("L1", "② 本体层（吃不到·模型反而是赋能）"),
                       ("L4", "③ 长尾 workbuddy（吃不到但没人去吃）"),
                       ("L0", "① 浅层工具（最先被吃·回避）")):
        sub = d[d["layer"] == lay]
        lines = [hdr]
        for _, r in sub.iterrows():
            lines.append("| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
                r["code"], r["name"], "★" if r["named"] else "",
                fmt(r["mktcap_yi"]), fmt(r["pe"]), fmt(r["rev"], 2), fmt(r["yoy"]),
                fmt(r["np_"], 2), fmt(r["gm"]), fmt(r["gm_chg"], 2)))
        chunks.append("\n### %s：%d 只\n\n%s\n" % (title, len(sub), "\n".join(lines)))
        print("\n%s：%d 只" % (title, len(sub)))

    with open(os.path.join(OUT, "ai_sw_final41.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(chunks))
    print("\n合计 %d 只 → scripts/out/ai_sw_final41.md" % len(d))

    print("\n=== 作者点名 15 家的落位 ===")
    for code, name, judge, why, rev, yoy in US_JUDGE:
        print("  [US] %-5s %-11s → %-9s %s（FY25营收 %.1f 亿美元，%+.1f%%）"
              % (code, name, judge, why, rev, yoy))
    for _, r in out[out["code"].isin(NAMED_HK)].iterrows():
        lay = {"L0": "① 浅层工具", "L1": "② 本体层", "L4": "③ 长尾"}.get(
            r["layer"], "中间态/框架外")
        print("  [HK] %-5s %-11s → %-9s（26H1营收 %.2f 亿，%+.1f%%）"
              % (r["code"], r["name"], lay, float(r["rev"]), float(r["yoy"])))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--final", action="store_true",
                    help="只输出最终口径（三层 41 只，点名优先）")
    ap.add_argument("--filter3", action="store_true",
                    help="只输出按三层框架（①浅层/②本体/③长尾）筛选的结果")
    args = ap.parse_args()

    out = build()
    if args.filter3:
        filter3(out)
        return
    if args.final:
        final41(out)
        return
    cols = ["layer", "market", "code", "name", "mktcap_yi", "pe", "pb",
            "rev", "yoy", "np_", "gm", "gm_chg", "group", "note"]
    with open(os.path.join(OUT, "ai_sw_rank.csv"), "w", encoding="utf-8-sig",
              newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(out.to_dict("records"))
    print("\n已写入 scripts/out/ai_sw_rank.csv（%d 行）" % len(out))

    hdr = ("| 代码 | 名称 | 市值亿 | PE | 26H1营收 | 同比% | 26H1归母 | 毛利率% | Δpp |\n"
           "|---|---|---|---|---|---|---|---|---|")
    snippets = []
    print("\n=== 分层统计（按 AI 吞噬顺序）===")
    for code, nm, desc in LAYERS:
        sub = out[out["layer"] == code]
        profit = sum(1 for _, r in sub.iterrows()
                     if r["np_"] is not None and not pd.isna(r["np_"]) and float(r["np_"]) > 0)
        print("\n%s %s：%d 只（26H1 盈利 %d 只）" % (code, nm, len(sub), profit))
        if not sub.empty:
            lines = [hdr]
            for _, r in sub.iterrows():
                lines.append("| %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
                    r["code"], r["name"], fmt(r["mktcap_yi"]), fmt(r["pe"]),
                    fmt(r["rev"], 2), fmt(r["yoy"]), fmt(r["np_"], 2),
                    fmt(r["gm"]), fmt(r["gm_chg"], 2)))
            snippets.append("\n**%s %s（%d 只）**\n\n%s\n" % (code, nm, len(sub), "\n".join(lines)))
    sub = out[out["layer"] == "SEC"]
    lines = [hdr]
    for _, r in sub.iterrows():
        lines.append("| %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
            r["code"], r["name"], fmt(r["mktcap_yi"]), fmt(r["pe"]),
            fmt(r["rev"], 2), fmt(r["yoy"]), fmt(r["np_"], 2),
            fmt(r["gm"]), fmt(r["gm_chg"], 2)))
    snippets.append("\n**SEC 网络安全（%d 只，作者框架未涉及，单列）**\n\n%s\n"
                    % (len(sub), "\n".join(lines)))

    with open(os.path.join(OUT, "ai_sw_rank.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(snippets))
    print("\n已写入 scripts/out/ai_sw_rank.md")


if __name__ == "__main__":
    main()
