# -*- coding: utf-8 -*-
"""海康威视 002415 — VL Business + AI Commentary"""
def build(stock, metrics, revenue_structure, years, cagr, spot):
    ly = metrics.get(years[-1], {}) if years else {}
    py = metrics.get(years[-2], {}) if len(years) >= 2 else {}
    def _c(c,p): return (c/p-1)*100 if c and p and p>0 else None
    def _f(v,d=0): return f"{v:,.{d}f}" if v is not None else "-"
    def _p(v): return f"{v:+.1f}%" if v is not None else "-"
    rev, npv, eps = ly.get("OPERATE_INCOME"), ly.get("HOLDER_PROFIT"), ly.get("BASIC_EPS")
    gm, npm, roe = ly.get("GROSS_MARGIN"), ly.get("NET_PROFIT_RATIO"), ly.get("ROE")
    rc, nc = _c(rev, py.get("OPERATE_INCOME")), _c(npv, py.get("HOLDER_PROFIT"))
    biz = f"海康威视是全球安防龙头，主营视频监控（全球市占率约30%）、AIoT、机器人及汽车电子。以视觉AI技术为核心向工业自动化延伸。FY{years[-1]}营收{_f(rev,0)}亿，净利{_f(npv,0)}亿，净利率{_p(npm)}，ROE {_p(roe)}。"
    p1 = f"2026年7月 — 海康威视营收{_f(rev,0)}亿，归母净利{_f(npv,0)}亿。毛利率{_p(gm)}、净利率{_p(npm)}。传统安防业务稳健（政府+大企业），创新业务（机器人/汽车电子/热成像）高速增长打开第二曲线。美国制裁影响逐步消化，海外收入韧性显现。"
    p2 = f"每股收益¥{_f(eps,2)}，每股经营现金流¥{_f(ly.get('PER_NETCASH'),2)}。全球40,000+员工（研发占比48%），年研发投入100亿+。拥有全球最大的视频AI训练数据库，视觉大模型（观澜）持续迭代。分红率长期40%+，股东回报稳定。"
    p3 = f"毛利率{_p(gm)}、净利率{_p(npm)}、ROE {_p(roe)}。壁垒：①规模优势——全球安防出货量第一，采购成本行业最低；②AI数据飞轮——百万路视频数据训练模型，算法越用越准；③软硬一体——从摄像头到后端平台全栈自研，切换成本极高；④渠道+服务——全球155个国家本地化服务网络。风险：美国制裁升级、国内政府支出缩减、AI竞争加剧。"
    pe, pb = spot.get("pe",0), spot.get("pb",0)
    p4 = f"PE约{_f(pe,1)}倍，PB{_f(pb,1)}倍。核心逻辑：①传统安防业务提供稳定现金流（20%+ ROIC）；②创新业务（机器人/汽车电子）高增速（30-50%），打开千亿级新市场；③视觉AI+大模型赋能千行百业（工业检测/智慧城市），从安防公司向AIoT平台转型；④当前PE处于5年低位，市场过度担忧制裁影响。"
    p5 = "催化剂：①机器人业务（AGV/机器视觉）放量→中国制造业自动化趋势受益；②汽车电子（车载摄像头/毫米波雷达）与比亚迪/蔚来深度合作；③观澜大模型商用落地→工业AI巡检/质检场景变现；④政府数字化+智慧城市投资回暖→传统安防增速恢复。关注创新业务收入占比和海外收入增速。"
    return {"business": biz, "commentary": [p1,p2,p3,p4,p5]}
