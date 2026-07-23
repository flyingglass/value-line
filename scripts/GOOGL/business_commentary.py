# -*- coding: utf-8 -*-
"""
GOOGL business_commentary.py — Alphabet (Google) 业务描述与分析评论
数据来源: SEC 10-K FY2025, westock-data 财务报表, web_search 研报
"""
def build(metrics=None, revenue_structure=None, cagr=None, spot=None):
    """生成 business 概述 + 5 段 commentary"""
    # ---- 从 metrics 提取最新年核心数据 ----
    latest_yr = "2025"
    rev = metrics.get("OPERATE_INCOME", {}).get(latest_yr, "N/A")
    ni  = metrics.get("HOLDER_PROFIT", {}).get(latest_yr, "N/A")
    eps = metrics.get("BASIC_EPS", {}).get(latest_yr, "N/A")
    gm  = metrics.get("GROSS_MARGIN", {}).get(latest_yr, "N/A")
    nm  = metrics.get("NET_PROFIT_RATIO", {}).get(latest_yr, "N/A")
    roe = metrics.get("ROE_AVG", {}).get(latest_yr, "N/A")

    def _fmt(v, unit=""):
        if v == "N/A": return "N/A"
        try:
            n = float(v)
            if abs(n) >= 1e8: return f"{n/1e8:.0f}亿{unit}"
            if abs(n) >= 1e4: return f"{n/1e4:.0f}万{unit}"
            return f"{n:.2f}{unit}"
        except: return str(v)

    business = (
        f"Alphabet（谷歌）是全球领先的AI驱动型科技巨头，总部位于美国加州山景城。"
        f"核心业务涵盖Google搜索（全球市占率约90%）、YouTube（月活超25亿）、"
        f"Google Cloud（全球第三大云服务商）、Android操作系统及AI大模型Gemini。"
        f"FY2025（截至2025年12月31日）营收4,029亿美元（+15% YoY），"
        f"净利润1,322亿美元（+32%），毛利率59.7%，净利率32.8%，ROE约35.7%。"
        f"Google Services（搜索+YouTube+广告）贡献85%营收，Google Cloud占14.6%。"
        f"AI全面嵌入搜索、云、广告三大核心业务，资本支出914亿美元投向AI基础设施。"
        f"CEO Sundar Pichai。"
    )

    commentary = [
        # 1. 经营分析
        (
            f"FY2025 Alphabet营收4,029亿美元（+15%），连续两年双位数增长。"
            f"Google Services营收3,427亿美元（+12%），其中搜索广告受AI Overviews和"
            f"Performance Max驱动量价齐升；YouTube年营收突破600亿美元（来源：2025Q4 Earnings Call），"
            f"Shorts货币化持续改善。Google Cloud营收587亿美元（+36%），首次全年经营利润转正"
            f"（139亿美元），AI基础设施需求（Gemini API、Vertex AI）是核心增长引擎。"
            f"经营利润率32.9%，较FY2024的32.1%略有提升，但研发费用611亿美元（+24%）和"
            f"资本支出914亿美元（+74%）大幅增长，反映AI军备竞赛的投入强度。"
            f"Other Bets（Waymo、Verily等）营收15亿美元，经营亏损75亿美元，仍处于投入期。"
        ),
        # 2. 现金流与资本配置
        (
            f"FY2025经营现金流1,647亿美元，自由现金流733亿美元（扣除914亿资本支出后），"
            f"自由现金流利润率约18.2%（vs FY2024的20.8%），因资本支出翻倍而被压缩。"
            f"公司维持极强的资产负债表：总资产5,953亿美元，现金及短期投资1,268亿美元，"
            f"长期债务613亿美元，净现金约655亿美元。"
            f"资本配置优先级：①AI基础设施投资（2026年Capex预计继续大幅增长）；"
            f"②股东回报：FY2025回购+股息合计约454亿美元（回购约350亿，季度股息$0.20→$0.21/季）；"
            f"③战略性收购（如云安全公司Wiz以320亿美元收购，2026年3月完成）。"
            f"股份回购持续缩减股本（FY2025回购约2.5%流通股），每股收益增厚效应显著。"
        ),
        # 3. 盈利质量与护城河
        (
            f"毛利率59.7%（FY2024: 58.2%），受益于搜索广告高毛利和Cloud规模效应改善；"
            f"净利率32.8%（FY2024: 28.6%），剔除一次性项目后核心利润率约30%。ROE 35.7%，"
            f"ROA 25.3%，均为全球科技巨头顶级水平。"
            f"护城河分析：①搜索引擎垄断——全球90%+市场份额，每天处理85亿+次搜索，"
            f"用户习惯+数据飞轮形成几乎不可逾越的壁垒；"
            f"②YouTube——全球第二大搜索引擎和最大视频平台，25亿+月活用户，"
            f"联网电视（CTV）观看时长超越移动端（来源：2025Q4 Earnings Call）；"
            f"③AI生态——Gemini模型族（Ultra/Pro/Flash/Nano）覆盖云端到端侧全场景，"
            f"TPU自研芯片（v6e）降低推理成本，Google Cloud借AI成为增长最快的主流云厂商；"
            f"④Android+Chrome生态——30亿+活跃设备，通过默认搜索分发巩固流量入口。"
            f"主要风险：①反垄断——美国司法部诉Google搜索垄断案（2025年8月裁定违法），"
            f"潜在结构性救济（可能强制剥离Chrome或终止默认搜索协议）为最大政策不确定性；"
            f"②AI竞争——微软Copilot+OpenAI对搜索份额的侵蚀，Perplexity等AI原生搜索崛起；"
            f"③广告周期敏感——宏观经济下行时广告预算首当其冲。"
        ),
        # 4. 估值分析
        (
            f"当前股价约$342（2026-07-23），PE约31x（基于FY2025稀释EPS $10.81）。"
            f"历史PE区间：过去5年均值约25x，过去10年均值约27x。"
            f"当前估值高于历史中枢，市场给予AI驱动的增长溢价。"
            f"估值支撑逻辑：①若FY2026 EPS增长15%至$12.43，forward PE约27.5x，"
            f"回落至历史均值附近；②Cloud加速增长（+36%）和AI货币化率提升是PE向上重估的关键；"
            f"③回购持续缩减股本~2-3%/年，每股价值自然增长。"
            f"估值风险：①反垄断救济可能导致搜索分发收入下降；"
            f"②AI Capex回报周期不确定——914亿资本支出何时转化为收入增长？"
            f"③广告周期下行时，25-30x PE的科技股历史上曾压缩至15-18x（2022年）。"
            f"可比公司：微软~35x PE（Azure+AI溢价更高），Meta~25x，Amazon~40x。"
            f"（来源：Westock Data实时行情 + SEC 10-K FY2025 + 标普500市场数据）"
        ),
        # 5. 催化剂
        (
            f"短期催化剂（6-12个月）：①Google Cloud利润率持续改善（Q4 FY2025经营利润率23.7%，"
            f"同比+7pp），AI推理需求爆发推动Cloud增速维持30%+；"
            f"②AI Overviews全面推广后搜索广告点击率提升（管理层指引正向）；"
            f"③YouTube Shorts广告加载率提升+CTV广告市场份额增长；"
            f"④Gemini 3模型发布（Google I/O 2026），Agent能力（Project Mariner）可能开创AI新交互范式。"
            f"中期催化剂（1-3年）：①Waymo商业化——已在旧金山/洛杉矶/凤凰城/奥斯汀运营，"
            f"2025年每周付费乘车15万+次（+200% YoY），Robotaxi TAM巨大；"
            f"②反垄断和解——若最终救济温和（如终止默认搜索协议费但不拆分），不确定性消除即为利好；"
            f"③TPU v7等自研芯片降低推理成本，AI毛利率有望结构性提升。"
            f"下行风险：①反垄断重罚/强制拆分→搜索流量和收入大幅下降；"
            f"②AI Capex过度投资→折旧摊销吞噬利润；"
            f"③宏观经济衰退→广告预算削减→收入增速降至个位数。"
            f"（来源：SEC 10-K FY2025 + 2025Q4 Earnings Call Transcript + Google I/O 2026）"
        ),
    ]

    return {"business": business, "commentary": commentary}
