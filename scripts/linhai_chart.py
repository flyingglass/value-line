# -*- coding: utf-8 -*-
"""linhai_chart.py — 里海案例周K复盘图（太极集团 / 再升科技 / 涪陵电力 / 博隆技术 / 凌玮科技）

视觉与 scripts/002507/review_chart.py 对齐（阶段框 / 年份 + 年中分割线 / 关键顶底 / 里海买卖点 /
关键水平位），差异：
  · 无「披露带」——这几只没有整理过业绩公告披露日，面板只有「主图 + 周成交量」
  · 顶底由脚本按「指定年份的最高 / 最低周」自动定位并取价，不手填日期与价位（避免臆造）
  · 买卖点价位 = 案例页原文口径（多为「名义价」），与图上前复权价口径不同，脚注已声明
  · 博隆技术 / 凌玮科技的**买卖价位原文未披露**（只知日期区间）——图上按日期定位，
    价位区间统一在脚注标注为「本地行情复核（data/<code>.db，qfq）」，与「案例页原文」严格区分：
    前者是口径说明，后者才是证据。

用法：.venv\\Scripts\\python scripts\\linhai_chart.py [code]
      不带参数 = 生成全部已配置标的
"""
import os
import sqlite3
import sys

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
plt.rcParams["font.sans-serif"] = ["Microsoft YaHei"]
plt.rcParams["axes.unicode_minus"] = False

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(BASE, "research-wiki", "research", "疯狂的里海", "assets")

UP, DOWN = "#d93a34", "#1f9e63"          # A 股惯例：涨红跌绿
BUY_C, SELL_C = "#c62828", "#0b7a4b"
PHASE_EC = "#2f6fd0"                     # 阶段框边界（蓝）
YEAR_C, MID_C = "#c3ccd9", "#b9c3d1"     # 年度分割线 / 年中分割线
LEVEL_C = "#b3261e"
PHASE_BG = ["#f4f7fb", "#fbf7f0"]

# ---------------------------------------------------------------------------
# 配置：每只标的的复盘图要素（买卖点价位均为案例页原文口径）
#   trades: (日期, 买/卖, 标签, 偏移(dx,dy), 说明)   —— 偏移逐个指定，避开密集区
#   hilo  : (年份, 'H'/'L', 说明)                    —— 日期与价位由脚本自动定位
#   phases: (起, 止, 框内标签, 悬停全称)
#   levels: (价位, 文字, 颜色)
# ---------------------------------------------------------------------------
SPECS = {}

SPECS["600129"] = dict(
    name="太极集团", start="2018-01-01",
    title=("太极集团（600129）里海案例复盘 · 周K（前复权）· 2018-2026　｜　"
           "关键顶底 × 里海操作点 × 关键水平位",
           "一句话：2019.12.31 大宗 @9.9 接盘（个人+合资 21 万股 + 集体 175 万股）→ 国药入主后死拿至 2023 高点 68 元"
           "（示范账户 30 万→100 万）；2023.6 该减 80% 只减 30%，2024.6 清仓 —— 「被抄作业者绑架」的代价"),
    footnote=(
        "数据：data/600129.db（kline 前复权 qfq，按周 W-FRI 聚合成周K，561 根 = 2018-01 ~ 2026-09）· "
        "操作点与事件出处见 research-wiki/research/疯狂的里海/案例/里海案例-太极集团.md\n"
        "口径：图为前复权连续价；买卖点价（9.9 / 11.46 / 14.32）为案例页原文口径。太极 2019 年后无送转、分红少，"
        "前复权价与名义价基本一致，故可直接比对。\n"
        "※ 账户口径：案例页明确「大账户 vs 示范账户口径差异巨大，分账户计数勿合并」——图上 2019.12.31 大宗（个人+合资 21 万股 + 集体账户 175 万股）"
        "与示范账户（2020.1.7 起 300 股 → 2020.11.17 换入 1700 股 → 2024.6 清仓）是两套账户，标注已分别写明，勿合并理解。\n"
        "顶底：由脚本按「该年最高 / 最低周」自动定位取价，未手填日期，故与案例页文字描述可能有极小的日期差（同一年内）。"),
    phases=[
        ("2018-01-01", "2018-12-31", "阶段一 · 深熊孕育\n2018", "2018 深熊：写书梳理重庆上市公司，发现太极「酝酿变化」"),
        ("2019-01-01", "2020-12-31", "阶段二 · 大宗接盘 → 国药入主预期\n2019-2020", "2019.12.31 大宗 9.9 元接盘 + 2021 国药入主实锤前的预期段"),
        ("2021-01-01", "2022-12-31", "阶段三 · 国药实锤主升\n2021-2022", "国药入主实锤；含 2022 初 27→14 腰斩（4 次 30%+ 回调中最窒息）"),
        ("2023-01-01", "2023-12-31", "阶段四 · 主升终点（68 元）\n2023", "2023 高点约 68 元；6.9 中阴线减 30%、7.3 大阴跌停确认顶部"),
        ("2024-01-01", "2026-12-31", "阶段五 · 清仓离场 + 弱跟踪\n2024-2026", "2024.6 示范账户清仓；2025.8.1 买 100 股参加股东会（观察仓）"),
    ],
    trades=[
        ("2019-12-31", "B", "2019-12-31 大宗接盘 @9.9", (-70, -42),
         "个人+合资 21 万股 + 集体账户 175 万股；昨收 9 折，「一交割就浮盈 15%」"),
        ("2020-01-07", "B", "2020-01-07 观察 300 股 @11.46", (58, -36), "30 万示范账户启航"),
        ("2020-07-01", "S", "2020-07-01 解禁全出 +57%", (72, 30), "换担保物（业绩差不可作担保），非看空"),
        ("2020-11-17", "B", "2020-11-17 换入 1700 股 @14.32", (62, 34), "卖秦安 3000 股 @8.22 换入"),
        ("2023-06-09", "S", "2023-06-09 起减仓 30%", (-66, 34), "「该卖 80% 只卖 30%」——本轮最大教训"),
        ("2024-06-01", "S", "2024-06 示范账户清仓", (0, -34), "买花园生物避最惨烈杀跌（太极 35→20 少亏十几万）"),
        ("2025-08-01", "B", "2025-08-01 买 100 股（观察）", (-58, 26), "参加股东会；冯柳同期悄悄买 2000 万股"),
    ],
    hilo=[
        ("2018", "L", "2018 深熊底（市值 30 多亿）"),
        ("2022", "L", "2022 初 27→14 腰斩（最窒息回调）"),
        ("2023", "H", "2023 高点 68 元：主升终点"),
        ("2024", "L", "2024 低点：清仓后仍继续跌"),
    ],
    levels=[
        (9.9, "大宗接盘成本 9.9 元（2019.12.31）", LEVEL_C),
        (68.0, "2023 高点 68 元（主升终点）", "#5a6473"),
    ],
)

SPECS["603601"] = dict(
    name="再升科技", start="2015-01-01",
    title=("再升科技（603601）里海案例复盘 · 周K（前复权）· 2015-2026　｜　"
           "关键顶底 × 里海操作点 × 关键水平位",
           "一句话：生涯研究最深的一只（2016 深研五篇、业绩预测几乎全中），却是最大滑铁卢 —— "
           "高位建仓 + 把战术股当战略股死拿，2016 买到 2024 才认赔（全账户「从赚约 200 万到亏约 100 万」）"),
    footnote=(
        "数据：data/603601.db（kline 前复权 qfq，按周 W-FRI 聚合成周K）· 操作点与事件出处见 "
        "research-wiki/research/疯狂的里海/案例/里海案例-再升科技.md\n"
        "口径：图上价格为前复权；买卖点价（8.04 / 10.75 / 18.32 / 13.36 / 14.30 / 15.45 / 3.22）为案例页原文「操作流水账」口径。"
        "再升 2016 年经历十送十二，**复权口径差异大**——案例页「矛盾 1」明确「建仓成本约 33 元（除权前）/ 15 元（除权后）/ 补到 6 元多（前复权）勿合并」，本图按日期定位、文字写原文口径。\n"
        "※ 本图是反面教材：2016 建仓（战术机会但买贵）→ 2020.2-3 疫情爆炒三个月 +1 倍（战术兑现窗口）未走 → "
        "2021-2024 阴跌 80%+ → 2024.2 以 3.22 元全砍（示范账户第一个实亏）。作者自评：把战术股当战略股。\n"
        "顶底：由脚本按「该年最高 / 最低周」自动定位取价；2024 年低点 2.28 与案例页「砍后再升跌到 2.28 到底」一致。"),
    phases=[
        ("2015-01-01", "2016-12-31", "阶段一 · 上市爆炒 → 深研建仓\n2015-2016", "2015 上市小盘牛市爆炒 10 倍（市值 90 亿 / 净利仅 3600 万）；2016 深研五篇"),
        ("2017-01-01", "2018-12-31", "阶段二 · 高位阴跌 + 深熊补仓\n2017-2018", "2017 全年 -18%；2018 深熊持仓 70%、8 元以下补仓，10 月到底"),
        ("2019-01-01", "2020-12-31", "阶段三 · 低位共振 → 疫情爆炒\n2019-2020", "2019.12 低位（6-7 元）共振买点；2020.2-3 口罩暴利驱动三个月 +1 倍"),
        ("2021-01-01", "2023-12-31", "阶段四 · 战术股当战略股 · 长期套牢\n2021-2023", "被「唯一以强者思维长期持有」的标的拖累；2022 全年 -40%、持 20000 股"),
        ("2024-01-01", "2026-12-31", "阶段五 · 认赔出局 → 再度爆炒\n2024-2026", "2024.2 以 3.22 元全砍认赔；2025-2026 再升被再次爆炒（作者已无持仓）"),
    ],
    trades=[
        ("2016-03-01", "B", "2016.2-3 低点多档建仓", (-72, -40), "研究最深的一只；建仓成本口径混乱（案例矛盾 1）"),
        ("2020-01-07", "B", "2020-01-07 建 12600 股 @8.04", (-64, 36), "30 万示范账户启航（8.04 成交 5000 / 7.98 成交 7600）"),
        ("2020-02-10", "S", "2020-02-10 卖 2600 股 @10.75", (58, -36), "疫情爆炒中减仓"),
        ("2020-03-11", "S", "2020-03-11 卖 2000 股 @18.32", (66, 32), "三个月 +1 倍的战术兑现窗口"),
        ("2020-04-23", "B", "2020-04-23 买 3200 股 @13.36", (-62, -40), "卖涪陵榨菜 36 元换入"),
        ("2020-09-04", "B", "2020-09-04 抄底 1500 股 @14.30", (0, -42), "榨菜清仓后转投"),
        ("2020-10-22", "S", "2020-10-22 卖 1500 股 @15.45", (62, 28), "换成鲁西化工 2400 股"),
        ("2024-02-05", "S", "2024-02 认赔全砍 @3.22", (0, 44), "示范账户第一个实亏「祭旗」；砍后跌到 2.28 见底"),
    ],
    hilo=[
        ("2015", "H", "2015 上市爆炒 10 倍（净利仅 3600 万）"),
        ("2018", "L", "2018 深熊底：持仓 70%、8 元以下补仓"),
        ("2020", "H", "2020 疫情爆炒（口罩暴利）高点"),
        ("2024", "L", "2024 低点 2.28：认赔出局后见底"),
        ("2026", "H", "2026 再度爆炒（作者已无持仓）"),
    ],
    levels=[
        (3.22, "2024.2 认赔全砍 3.22 元", LEVEL_C),
    ],
)

SPECS["600452"] = dict(
    name="涪陵电力", start="2018-01-01",
    title=("涪陵电力（600452）里海案例复盘 · 周K（前复权）· 2018-2026　｜　"
           "关键顶底 × 里海操作点 × 关键水平位",
           "一句话：「第二增长曲线 = 可复制投资模型」的原型标的 —— 2015 国网注入配电网节能资产打破业绩天花板，"
           "2019 逻辑翻转买入、2021 全年 +74%；2023 业绩放缓后清仓，自评「看对了但没重锤」"),
    footnote=(
        "数据：data/600452.db（kline 前复权 qfq，按周 W-FRI 聚合成周K）· 操作点与事件出处见 "
        "research-wiki/research/疯狂的里海/案例/里海案例-涪陵电力.md\n"
        "※ 口径差异最大的一只：涪陵电力分红 / 送转多，**前复权价与名义价差距显著**——案例页「2020.1.7 示范账户建仓 200 股 @18.54」"
        "为名义价，对应图上 2020 年初前复权价约 6 元区间（约 3 倍差）。故图上标注按**日期**定位、文字写**原文名义价**，"
        "切勿把标签里的数字当图上的价位读。\n"
        "操作口径：2019 逻辑翻转买入属**个人账户 / 100 万示范账户前身**（12 倍动态 PE）；2020.1.7 起为**30 万示范账户**"
        "（200 股 → 分红增持 → 2023 年内清仓）；「涪陵三剑客」+58.18% 是**虚拟组合**涨幅，非实盘盈亏。\n"
        "顶底：由脚本按「该年最高 / 最低周」自动定位取价。2018 底「4.55 元」为案例页名义价口径，图上前复权低点更低，两者不可混读。"),
    phases=[
        ("2018-01-01", "2018-12-31", "阶段一 · 被否定（赚钱不值钱）\n2018", "作者曾以「赚钱不值钱」否定电力，彼时逻辑未翻转"),
        ("2019-01-01", "2020-12-31", "阶段二 · 逻辑翻转 → 第二增长曲线\n2019-2020", "2015 国网注入配电网节能资产；2019 逻辑翻转买入，2018 业绩快报次日涨停为最佳介入点"),
        ("2021-01-01", "2022-12-31", "阶段三 · 连涨三年 · 主升\n2021-2022", "2021 全年 +74%（持仓股最亮的星）；2022.2 「25 元买电力 = 追涨」高位警示"),
        ("2023-01-01", "2026-12-31", "阶段四 · 业绩放缓 → 清仓 → 弱跟踪\n2023-2026", "2023 业绩下滑（H1 净利 -36%）；「第二增长曲线 = 可复制模型」事后升华为方法论"),
    ],
    trades=[
        ("2019-07-15", "B", "2019.7 逻辑翻转买入（约 12 倍 PE）", (-70, -42), "个人账户 / 示范账户前身；苍蝇拍同期同持"),
        ("2020-01-07", "B", "2020-01-07 建仓 200 股 @18.54", (-58, 36), "30 万示范账户启航（名义价）"),
        ("2021-05-06", "B", "2021-05-06 分红增持（验证逻辑）", (52, 38), "「不为赚钱就为验证逻辑」"),
        ("2023-10-11", "S", "2023 年内清仓（业绩放缓 + 信息不透明）", (0, -42), "卖出后仍保持弱跟踪，未退出能力圈"),
    ],
    hilo=[
        ("2018", "L", "2018 底：被否定期（案例口径 4.55 元）", 96),
        ("2021", "H", "2021 高点：连涨三年主升", -60),
        ("2024", "L", "2024 低点：业绩放缓后回落", 40),
        ("2026", "H", "2026 高点：创出新高（案例未覆盖）", -40),
    ],
    levels=[],
)

SPECS["603325"] = dict(
    name="博隆技术", start="2024-01-01",
    title=("博隆技术（603325）里海案例复盘 · 周K（前复权）· 2024-2026　｜　"
           "关键顶底 × 里海操作点",
           "一句话：2025.2-3 清仓硅宝后与凌玮同批买入 → 2025.9 以「短期确定性不太够」卖出切中泰 —— "
           "卖出点正落在 2025-08-29 历史高点（98.45）附近，此后 2026 回落至 48 元："
           "同一句「确定性不够」，博隆这一腿卖对了"),
    footnote=(
        "数据：data/603325.db（kline 前复权 qfq，按周 W-FRI 聚合成周K；2024-01-10 上市 ~ 2026-09-02，641 根）· "
        "操作点与事件出处见 research-wiki/research/疯狂的里海/案例/里海案例-博隆技术.md\n"
        "【注】原文只给了日期区间（2025.2-3 买 / 2025.9 卖），**未披露任何价位**——图上买卖点按日期定位，"
        "标签不含价格。\n"
        "本地行情复核（本项目 DB 口径，非作者原文）：2025.2-3 收盘 61.63~76.92 元；2025.9 收盘 82.86~95.91 元；"
        "全区间最高 98.45（2025-08-29）→ **9 月卖出点即落在历史最高区**；2026 最低 48.02。"
        "故「有浮盈的前提下切换」成立，且事后看卖点极佳。\n"
        "※ 与再升科技同属「隐形冠军 / 高端制造」类，但结局相反：再升=高位买入长期套牢；本页=低买高卖"
        "（是否买在低位，原文未披露，属待补研究）。\n"
        "顶底：由脚本按「该年最高 / 最低周」自动定位取价，未手填日期与价位。"),
    phases=[
        ("2024-01-01", "2024-12-31", "阶段一 · 上市首年\n2024",
         "2024-01-10 上市；2024-02-06 见底 40.59，全年高点 77.56"),
        ("2025-01-01", "2025-09-30", "阶段二 · 里海持有期\n2025.2-9",
         "2025.2-3 清仓硅宝后买入（与凌玮同批）→ 2025-08-29 摸 98.45 → 9 月卖出切中泰"),
        ("2025-10-01", "2026-12-31", "阶段三 · 卖出后回落\n2025.10-2026",
         "「确定性不够」卖出后股价回落，2026 最低 48.02（事后看卖对了）"),
    ],
    trades=[
        ("2025-03-01", "B", "2025.2-3 买入（价位未披露）", (-70, -38),
         "清仓硅宝后的资金去向之一；与凌玮同批（原文无买入逻辑）"),
        ("2025-09-01", "S", "2025.9 卖出 · 切中泰", (58, 32),
         "「博隆和凌玮短期的确定性不太够」——本地口径卖点落在 2025-08-29 高点 98.45 附近"),
    ],
    hilo=[
        ("2024", "L", "2024-02 上市首月见底"),
        ("2025", "H", "2025-08-29 高点 98.45：里海 9 月在此附近卖出"),
        ("2026", "L", "2026 低点：卖出后回落"),
    ],
    levels=[],
)

SPECS["301373"] = dict(
    name="凌玮科技", start="2023-01-01",
    title=("凌玮科技（301373）里海案例复盘 · 周K（前复权）· 2023-2026　｜　"
           "关键顶底 × 里海操作点",
           "一句话：2025.2-3 从硅宝切来（简单/底部/变化三要素齐备：消光用二氧化硅绝对龙头 + 估值底部 + "
           "IPO 项目产能翻倍）→ 2025.9 因「掌握不了产能释放节奏」卖出（+20~30%）→ 2026 被 AI 覆铜板并购预期"
           "（收购江苏辉迈 → 球形硅微粉）推至 203.99 —— 错失约 6 倍，作者自评「交给运气、守正出奇」"),
    footnote=(
        "数据：data/301373.db（kline 前复权 qfq，按周 W-FRI 聚合成周K；2023-02-08 上市 ~ 2026-09-02，868 根）· "
        "操作点与事件出处见 research-wiki/research/疯狂的里海/案例/里海案例-凌玮科技.md\n"
        "【注】原文未披露买卖价位（只有「赚了百分之二三十」）；图上按日期定位、标签不含价格。\n"
        "本地行情复核（本项目 DB 口径，非作者原文）：2025.2-3 收盘 25.05~29.42 元；2025.9 收盘 31.25~34.94 元"
        "（**+20~30% 与原文「赚了百分之二三十」吻合 → 支持 2025.12.31 总结的「9 月卖出」口径**）；"
        "2026-03-12 专文当日 qfq 收 72.85（原文写「80 多」＝名义价口径，两者约 10% 差，未逐笔核对分红）；"
        "2026-06-17 最高 203.99。\n"
        "※ 卖出时点原文两说并存（2025.12.31「9 月切中泰」 vs 2026.3.12「去年赚了百分之二三十，年后就跑了」）"
        "——案例页照录不调和，本页亦不裁定。\n"
        "※ 2026 的暴涨是**外生并购催化**（标的尚处客户小试阶段），作者明确归为运气项，不计入体系战绩。\n"
        "顶底：由脚本按「该年最高 / 最低周」自动定位取价，未手填日期与价位。"),
    phases=[
        ("2023-01-01", "2024-12-31", "阶段一 · 上市 → 杀估值见底\n2023-2024",
         "2023-02-08 上市；2024-02-06 见底 17.03（与博隆同日见底）"),
        ("2025-01-01", "2025-09-30", "阶段二 · 里海持有期\n2025.2-9",
         "2025.2-3 从硅宝切来（本地口径 25~29 元）→ 2025.9 卖出（31~35 元，+20~30%）"),
        ("2025-10-01", "2026-12-31", "阶段三 · 错失主升\n2025.10-2026",
         "并购切入球形硅微粉（M9 级覆铜板 / AI 概念）→ 2026-06-17 最高 203.99：里海已无持仓"),
    ],
    trades=[
        ("2025-03-01", "B", "2025.2-3 买入（价位未披露）", (-74, -38),
         "原文三要素逐条：简单（绝对龙头+标准牵头单位）/底部（估值底部未被发现）/变化（IPO 产能翻倍）"),
        ("2025-09-01", "S", "2025.9 卖出（+20~30%）", (56, 30),
         "卖出理由=「无法掌握新产能的释放节奏」+ 担心折旧吞噬利润"),
    ],
    hilo=[
        ("2024", "L", "2024-02 上市后低点 17.03"),
        ("2025", "H", "2025 年内高点（里海持有期内）"),
        ("2026", "H", "2026-06-17 高点 203.99：AI 并购催化，里海已卖出", -60),
    ],
    levels=[],
)


# ---------------------------------------------------------------------------
# 数据
# ---------------------------------------------------------------------------
def load_kline(code, start):
    c = sqlite3.connect(os.path.join(BASE, "data", "%s.db" % code))
    df = pd.read_sql("select date,open,high,low,close,volume from kline "
                     "where date>=? order by date", c, params=(start,))
    c.close()
    df["date"] = pd.to_datetime(df["date"])
    return df


def to_week(df):
    w = (df.set_index("date").resample("W-FRI")
           .agg({"open": "first", "high": "max", "low": "min",
                 "close": "last", "volume": "sum"})
           .dropna().reset_index())
    return w


def week_pos(wi, t):
    t = pd.Timestamp(t)
    return int(np.clip(np.searchsorted(wi, t.to_datetime64(), side="right") - 1,
                       0, len(wi) - 1))


def year_extreme(w, year, kind):
    """该年最高(H) / 最低(L)的那一周 → (行号, 价位)。"""
    seg = w[w["date"].dt.year == int(year)]
    if seg.empty:
        return None
    i = seg["high"].idxmax() if kind == "H" else seg["low"].idxmin()
    return int(w.index.get_loc(i)), float(w.loc[i, "high" if kind == "H" else "low"])


def draw_candles(ax, seg, idx, lw=0.55, width=0.82):
    o, h, l, cl = (seg[k].to_numpy(dtype=float) for k in ("open", "high", "low", "close"))
    colors = np.where(cl >= o, UP, DOWN)
    ax.add_collection(LineCollection(
        [[(i, lo), (i, hi)] for i, lo, hi in zip(idx, l, h)],
        colors=colors, linewidths=lw, zorder=2))
    rng = h.max() - l.min()
    bot = np.minimum(o, cl)
    hgt = np.maximum(np.abs(cl - o), rng * 0.0016)
    ax.bar(idx, hgt, bottom=bot, width=width, color=colors, edgecolor="none", zorder=3)


# ---------------------------------------------------------------------------
# 绘图
# ---------------------------------------------------------------------------
def draw(code, spec):
    w = to_week(load_kline(code, spec["start"]))
    wi = w["date"].to_numpy()
    n = len(w)

    fig = plt.figure(figsize=(21, 9.6), dpi=150)
    fig.patch.set_facecolor("#ffffff")
    gs = fig.add_gridspec(2, 1, height_ratios=[4.0, 0.72],
                          left=0.052, right=0.984, top=0.885, bottom=0.155, hspace=0.07)
    ax_m = fig.add_subplot(gs[0])
    ax_v = fig.add_subplot(gs[1], sharex=ax_m)

    idx_all = np.arange(n)
    draw_candles(ax_m, w, idx_all)

    lo, hi = w["low"].min(), w["high"].max()
    rng = hi - lo
    y0, y1 = lo - rng * 0.10, hi + rng * 0.20
    ax_m.set_ylim(y0, y1)
    ax_m.set_xlim(-6, n + 6)
    ax_m.grid(axis="y", color="#e8eaee", lw=0.6, zorder=0)
    ax_m.set_axisbelow(True)
    for s in ("top", "right"):
        ax_m.spines[s].set_visible(False)
    ax_m.spines["left"].set_color("#c8ccd4")
    ax_m.spines["bottom"].set_color("#c8ccd4")
    ax_m.tick_params(labelsize=9, colors="#4a5058", length=3, axis="y")
    ax_m.tick_params(axis="x", length=0)
    ax_m.set_ylabel("前复权价（元）· 周K", fontsize=10, color="#4a5058")

    # 阶段框 + 框顶标签
    for i, (s, e, short, full) in enumerate(spec["phases"]):
        p0, p1 = week_pos(wi, s), week_pos(wi, e)
        ax_m.add_patch(Rectangle((p0 - 0.5, y0), (p1 - p0 + 1), (y1 - y0),
                                 fc=PHASE_BG[i % 2], ec=PHASE_EC, lw=1.2,
                                 ls=(0, (5, 3)), alpha=0.5, zorder=1.1))
        ax_m.annotate(short.replace("\n", "　"), ((p0 + p1) / 2.0, y1 - (y1 - y0) * 0.05),
                      ha="center", va="center", fontsize=9.6, fontweight="bold",
                      color="#2b3138", zorder=6,
                      bbox=dict(boxstyle="round,pad=0.42", fc="#ffffff",
                                ec="#9aa2ae", lw=1.0, alpha=0.94))

    # 关键水平位
    for px, txt, col in spec["levels"]:
        ax_m.axhline(px, color=col, lw=1.1, ls=(0, (6, 4)), alpha=0.55, zorder=1.5)
        ax_m.annotate(txt, (2, px), xytext=(0, 3), textcoords="offset points",
                      ha="left", va="bottom", fontsize=8.6, fontweight="bold",
                      color=col, zorder=22,
                      bbox=dict(boxstyle="round,pad=0.28", fc="#ffffff",
                                ec=col, lw=0.7, alpha=0.92))

    # 关键顶底（自动定位年份极值）；可选第 4 元素 = 水平偏移(dx)，用于避开买卖点标注
    for item in spec["hilo"]:
        year, kind, txt = item[0], item[1], item[2]
        dx = item[3] if len(item) > 3 else 0
        got = year_extreme(w, year, kind)
        if got is None:
            continue
        p, px = got
        ax_m.plot([p], [px], marker="o", ms=6, mfc="white", mec="#2b3138",
                  mew=1.2, zorder=12)
        up = kind == "H"
        ax_m.annotate("%s-%s · %.2f %s" % (year, w.loc[p, "date"].strftime("%m-%d"), px, txt),
                      (p, px), xytext=(dx, 14 if up else -16),
                      textcoords="offset points",
                      ha="center" if dx == 0 else ("left" if dx > 0 else "right"),
                      va="bottom" if up else "top", fontsize=8.6, fontweight="bold",
                      color="#2b3138", zorder=26,
                      bbox=dict(boxstyle="round,pad=0.30", fc="#ffffff",
                                ec="#c1c8d2", lw=0.8))

    # 里海操作点
    for date, side, short, (dx, dy), _note in spec["trades"]:
        p = week_pos(wi, date)
        is_buy = side == "B"
        col = BUY_C if is_buy else SELL_C
        y = w["close"].iloc[p]
        ax_m.plot([p], [y], marker="^" if is_buy else "v", ms=10,
                  mfc=col, mec="white", mew=1.2, zorder=14)
        ax_m.annotate(short, (p, y), xytext=(dx, dy), textcoords="offset points",
                      ha="center" if dx == 0 else ("left" if dx > 0 else "right"),
                      va="bottom" if dy > 0 else "top",
                      fontsize=8.2, fontweight="bold", color=col, zorder=27,
                      bbox=dict(boxstyle="round,pad=0.26", fc="#ffffff",
                                ec=col, lw=0.8, alpha=0.94),
                      arrowprops=dict(arrowstyle="-", color=col, lw=0.8,
                                      alpha=0.55, shrinkA=2, shrinkB=4))

    # 年份分割线 + 年中分割线
    yrs = pd.Series(wi).dt.year
    ypos = [int(i) for i in yrs.ne(yrs.shift()).to_numpy().nonzero()[0]]
    ypos = [p for p in ypos if p < n]
    ylab = [str(pd.Timestamp(wi[p]).year) for p in ypos]
    for p in ypos:
        ax_m.axvline(p, color=YEAR_C, lw=1.1, zorder=1.25)
        ax_v.axvline(p, color=YEAR_C, lw=1.1, zorder=0.6)
    jul = pd.Series(wi).dt.month.eq(7)
    for i in jul.ne(jul.shift()).to_numpy().nonzero()[0]:
        if not jul.iloc[i]:
            continue
        ax_m.axvline(int(i), color=MID_C, lw=0.95, ls=(0, (4, 3)), zorder=1.24)
        ax_v.axvline(int(i), color=MID_C, lw=0.95, ls=(0, (4, 3)), zorder=0.6)

    ax_m.set_xticks(ypos)
    ax_m.set_xticklabels(ylab, fontsize=10)
    ax_m.tick_params(axis="x", labelbottom=True, labelsize=10, colors="#333a42",
                     length=0, pad=4)

    # 标题 + 图例
    ax_m.set_title(spec["title"][0] + "\n" + spec["title"][1],
                   fontsize=13.2, fontweight="bold", color="#1a1d22",
                   loc="left", pad=16)
    ax_m.legend(
        handles=[
            Line2D([], [], marker="^", color="none", mfc=BUY_C, mec="white", ms=10, label="里海买点"),
            Line2D([], [], marker="v", color="none", mfc=SELL_C, mec="white", ms=10, label="里海卖点"),
            Line2D([], [], marker="o", color="none", mfc="white", mec="#2b3138", ms=7,
                   label="关键顶 / 底（年份最高最低周）"),
            Line2D([], [], color=PHASE_EC, lw=1.2, ls=(0, (5, 3)), label="阶段框边界"),
            Line2D([], [], color=YEAR_C, lw=1.1, label="年度分割线"),
            Line2D([], [], color=MID_C, lw=1.1, ls=(0, (4, 3)), label="年中分割线"),
        ],
        loc="lower right", ncol=2, fontsize=9.2, frameon=True, facecolor="white",
        edgecolor="#d5dae2", framealpha=0.94, handlelength=1.5, columnspacing=1.2,
        handletextpad=0.5, borderaxespad=0.5).set_zorder(40)

    # 周成交量
    vcol = np.where(w["close"].to_numpy() >= w["open"].to_numpy(), UP, DOWN)
    ax_v.bar(idx_all, w["volume"].to_numpy() / 1e8, width=0.82, color=vcol,
             edgecolor="none", zorder=3)
    ax_v.set_ylim(0, w["volume"].max() / 1e8 * 1.22)
    ax_v.grid(axis="y", color="#eef1f5", lw=0.6)
    ax_v.set_axisbelow(True)
    for s in ("top", "right"):
        ax_v.spines[s].set_visible(False)
    ax_v.tick_params(labelsize=9, colors="#4a5058", length=3, axis="y")
    ax_v.set_ylabel("周成交量\n（亿股）", fontsize=9, color="#4a5058")
    ax_v.tick_params(axis="x", labelbottom=True, labelsize=10, colors="#333a42",
                     length=4, pad=5)
    ax_v.set_xlabel("时间（每年一格；浅灰实线 = 年度分割线，浅灰虚线 = 年中分割线）",
                    fontsize=10, color="#4a5058")
    ax_v.legend(handles=[Line2D([], [], color=UP, lw=6, label="阳线量"),
                         Line2D([], [], color=DOWN, lw=6, label="阴线量")],
                loc="upper left", ncol=2, fontsize=9.2, frameon=True,
                facecolor="white", edgecolor="#d5dae2", framealpha=0.92,
                handlelength=1.5, columnspacing=1.6, handletextpad=0.5,
                borderaxespad=0.25)

    # 脚注
    fig.text(0.052, 0.008, spec["footnote"], fontsize=8.3, color="#5a6068",
             va="bottom", linespacing=1.6)

    out = os.path.join(ASSETS, "kline-%s-review.png" % code)
    os.makedirs(ASSETS, exist_ok=True)
    fig.savefig(out, facecolor="#ffffff")
    plt.close(fig)
    print("已输出 %s（周K %d 根，%s ~ %s）"
          % (out, n, w["date"].iloc[0].date(), w["date"].iloc[-1].date()))


def main():
    codes = sys.argv[1:] or sorted(SPECS)
    for code in codes:
        if code not in SPECS:
            print("跳过 %s（未配置）" % code)
            continue
        draw(code, SPECS[code])


if __name__ == "__main__":
    main()
