# -*- coding: utf-8 -*-
"""
Value Line 中文版 — 标的管理配置
"""
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

# 确保数据目录存在
os.makedirs(os.path.join(DATA_DIR, "pdfs"), exist_ok=True)

# ============================================================
# 标的定义
# ============================================================
# ============================================================
# 港股年报PDF直链 (手动维护, 从港交所披露易获取)
# URL格式: https://www.hkexnews.hk/listedco/listconews/sehk/{次年}/{MMDD}/{编号}_c.pdf
# ============================================================
HK_PDF_URLS = {
    "09992": {
        "2025": "https://www1.hkexnews.hk/listedco/listconews/sehk/2026/0325/2026032500285.pdf",
        "2024": "https://www1.hkexnews.hk/listedco/listconews/sehk/2025/0326/2025032600228_c.pdf",
        "2023": "https://www1.hkexnews.hk/listedco/listconews/sehk/2024/0320/2024032000318_c.pdf",
    }
}

STOCKS = {
    "09992": {
        "name": "泡泡玛特",
        "name_en": "POP MART",
        "market": "hk",
        "exchange": "SEHK",
        "currency": "CNY",
        "ceo": "王宁",
        "inc": "开曼群岛",
        "website": "www.popmart.com",
        "analyst": {
            "commentary": [
                "泡泡玛特增速见顶？股价从高点腰斩后何去何从",
                "2026年5月31日 — 泡泡玛特2025年报交出史诗级成绩：营收371.2亿（+185%），每股收益9.58元（+308%），ROE高达57%。但股价自高点HKD 334回落近半至HKD 173.4。是市场提前消化逆天增长，还是回调创造了入场机会？",
                "细看结构，海外收入占比从20%跃至44%。THE MONSTERS独占38%，SKULLPANDA及其他IP形成第二梯队。但2025年爆发式增长受益于海外门店从0到1的渠道红利——基数上升后2026年增速几乎必然放缓。我们的预测：营收增20%-30%、EPS增15%-25%。",
                "当前PE 18倍（TTM修复后），处于历史估值低位。PB 10.4倍位于中位，ROE 57%属顶级。公司净现金状态，无财务风险。2025年派息CNY 2.38/股，股息率1.4%。估值已回归合理甚至偏低，关注2026年中报海外同店增速作为验证信号。"
            ],
        },
        "org_id": "9900047555",
        "hkex_stock_id": "1000068054",
        "pfx": "hk",
        "shares": 1341043150,
        "shares_str": "1,341,043,150",
        "industry": "Consumer",
        "business_desc": "",
    },
    "09988": {
        "name": "阿里巴巴",
        "name_en": "Alibaba Group",
        "market": "hk",
        "exchange": "SEHK",
        "currency": "CNY",
        "org_id": "",
        "pfx": "hk",
        "fiscal_yr_end": "03-31",    # 3月底财年
        "shares": 19000000000,
        "shares_str": "19,000,000,000",
        "industry": "Technology",
        "business_desc": "阿里巴巴集团是全球领先的电子商务及科技公司，核心业务涵盖中国商业（淘宝、天猫、1688）、国际商业（AliExpress、Lazada、Trendyol）、云计算（阿里云，中国市场份额第一）、本地生活（饿了么、高德）、菜鸟物流及数字娱乐。FY2025营收9,963.5亿，中国商业65%、云计算12%、国际商业11%。员工198,000人。CEO: 吴泳铭。",
        "analyst": {
            "commentary": [
                "阿里云的AI转型能否成为第二增长曲线？",
                "2026年5月31日 — 阿里巴巴FY2025实现营收9,963.5亿元（+5.9%），每股收益6.70元（+71.4%）。云智能业务受益于AI推理需求爆发实现高速增长。核心电商在拼多多、抖音竞争下维持份额，88VIP会员突破4,500万。",
                "国际商业板块（AIDC）FY2025营收1,069亿元（+32%），但利润率承压。阿里云AI连续多季度三位数增长，智能云收入1,135亿元（+8%）。公司持续股份回购——FY2025约650亿美元等值。",
                "当前PE 21.4倍，低于历史中位数25.5。PB 1.0倍接近净资产，下行有限。ROE 9.2%偏低但改善中。阿里净现金超2,000亿元，云业务估值重估潜力+AI基础设施先发优势。关注阿里云AI收入占比突破20%——验证AI转型叙事的核心指标。"
            ],
            "recommendation": ""
        },
    },
    "600519": {
        "name": "贵州茅台",
        "name_en": "Kweichow Moutai",
        "market": "cn",
        "exchange": "SSE",
        "currency": "CNY",
        "org_id": "gssh0600519",      # 巨潮内部ID
        "pfx": "sh",
        "shares": 1256197800,          # 总股本(股数), 约12.56亿股
        "shares_str": "1,256,197,800",
        "industry": "Consumer Staples",
        "business_desc": "",
    },
    "01368": {
        "name": "特步国际",
        "name_en": "Xtep Int'l",
        "market": "hk",
        "exchange": "SEHK",
        "currency": "CNY",
        "pfx": "hk",
        "shares": 2806072400,
        "shares_str": "2,806,072,400",
        "industry": "Consumer",
        "business_desc": "",
    },
    "002027": {
        "name": "分众传媒",
        "name_en": "Focus Media",
        "market": "cn",
        "exchange": "SZSE",
        "currency": "CNY",
        "org_id": "gssz0002027",
        "pfx": "sz",
        "shares": 14442000000,
        "shares_str": "14,442,000,000",
        "industry": "Media",
        "business_desc": "",
    },
    "000807": {
        "name": "云铝股份",
        "name_en": "Yunnan Aluminium",
        "market": "cn",
        "exchange": "SZSE",
        "currency": "CNY",
        "org_id": "gssz0000807",
        "pfx": "sz",
        "shares": 3467957588,
        "shares_str": "3,467,957,588",
        "industry": "Metals & Mining",
        "business_desc": "",
    },
    "000933": {
        "name": "神火股份",
        "name_en": "Shenhuo",
        "market": "cn",
        "exchange": "SZSE",
        "currency": "CNY",
        "org_id": "gssz0000933",
        "pfx": "sz",
        "shares": 2248548808,
        "shares_str": "2,248,548,808",
        "industry": "Metals & Mining",
        "business_desc": "",
    },
    "600595": {
        "name": "中孚实业",
        "name_en": "Zhongfu Industrial",
        "market": "cn",
        "exchange": "SSE",
        "currency": "CNY",
        "org_id": "gssh0600595",
        "pfx": "sh",
        "shares": 4000000000,
        "shares_str": "4,000,000,000",
        "industry": "Metals & Mining",
        "business_desc": "",
    },
    "002128": {
        "name": "电投能源",
        "name_en": "SPIC Energy",
        "market": "cn",
        "exchange": "SZSE",
        "currency": "CNY",
        "org_id": "",
        "pfx": "sz",
        "shares": 2241573493,
        "shares_str": "2,241,573,493",
        "industry": "Energy",
        "business_desc": "",
    },
    "01378": {
        "name": "中国宏桥",
        "name_en": "China Hongqiao",
        "market": "hk",
        "exchange": "SEHK",
        "currency": "CNY",
        "org_id": "",
        "pfx": "hk",
        "shares": 9481881123,
        "shares_str": "9,481,881,123",
        "industry": "Metals & Mining",
        "business_desc": "",
    },
    "002532": {
        "name": "天山铝业",
        "name_en": "Tianshan Aluminum",
        "market": "cn",
        "exchange": "SZSE",
        "currency": "CNY",
        "org_id": "",
        "pfx": "sz",
        "shares": 4651885415,
        "shares_str": "4,651,885,415",
        "industry": "Metals & Mining",
        "business_desc": "",
    },
    "00700": {
        "name": "腾讯控股",
        "name_en": "Tencent Holdings",
        "market": "hk",
        "exchange": "SEHK",
        "currency": "CNY",
        "shares": 9180000000,
        "shares_str": "9,180,000,000",
        "fiscal_yr_end": "12-31",
        "industry": "Technology",
        "business_desc": "腾讯控股是中国最大的互联网科技公司之一，核心业务涵盖社交(微信/QQ)、游戏(国内+国际)、金融科技(微信支付/理财通)、云服务及企业服务。",
    },
    "01698": {
        "name": "腾讯音乐",
        "name_en": "Tencent Music",
        "market": "hk",
        "exchange": "SEHK",
        "currency": "CNY",
        "shares": 3220000000,
        "shares_str": "3,220,000,000",
        "fiscal_yr_end": "12-31",
        "industry": "Technology",
        "business_desc": "腾讯音乐娱乐集团是中国领先的在线音乐娱乐平台，运营QQ音乐、酷狗音乐、酷我音乐及全民K歌，通过会员订阅及直播打赏变现。",
    },
    "00696": {
        "name": "中国民航信息网络",
        "name_en": "TravelSky Technology",
        "market": "hk",
        "exchange": "SEHK",
        "currency": "CNY",
        "shares": 2926000000,
        "shares_str": "2,926,000,000",
        "fiscal_yr_end": "12-31",
        "industry": "Technology",
        "business_desc": "中国民航信息网络是中国航空旅游业信息技术解决方案的主导供应商，核心业务包括航空信息技术服务(GDS)、结算清算、机场信息技术等。",
    },
    "01114": {
        "name": "华晨中国",
        "name_en": "Brilliance China",
        "market": "hk",
        "exchange": "SEHK",
        "currency": "CNY",
        "shares": 5045000000,
        "shares_str": "5,045,000,000",
        "fiscal_yr_end": "12-31",
        "industry": "Automotive",
        "business_desc": "华晨中国汽车控股有限公司主要通过与宝马合资的华晨宝马获得主要利润贡献，同时制造及销售轻型客车及汽车零部件。",
    },
}

# ============================================================
# 市场配置 (通用化: 兼容A股/H股/美股)
# ============================================================
MARKET_CONFIG = {
    "hk": {
        "name": "港股",
        "currency": "HKD",
        "index_name": "HSI",
        "index_name_cn": "恒生指数",
        "index_symbol": "HSI",
        "index_akshare_func": "stock_hk_index_daily_sina",
        "pe_estimate": {
            "2013": 11.0, "2014": 10.5, "2015": 10.0, "2016": 11.5,
            "2017": 12.5, "2018": 10.5, "2019": 11.0, "2020": 13.5,
            "2021": 10.5, "2022": 7.5,  "2023": 9.0,  "2024": 8.5, "2025": 8.0,
        },
    },
    "cn": {
        "name": "A股",
        "currency": "CNY",
        "index_name": "CSI300",
        "index_name_cn": "沪深300",
        "index_symbol": "000300",
        "index_akshare_func": "stock_zh_index_daily",
        "pe_estimate": {
            "2013": 12.0, "2014": 13.0, "2015": 18.0, "2016": 14.0,
            "2017": 15.0, "2018": 12.0, "2019": 14.0, "2020": 16.0,
            "2021": 15.0, "2022": 12.0, "2023": 13.0, "2024": 14.0, "2025": 14.0,
        },
    },
    "us": {
        "name": "美股",
        "currency": "USD",
        "index_name": "SPX",
        "index_name_cn": "标普500",
        "index_symbol": "SPX",
        "index_akshare_func": "",
        "pe_estimate": {},
    },
}

# ============================================================
# 当前活跃标的
# ============================================================
ACTIVE_STOCK = \"00700\"

# ============================================================
# SQLite 路径
# ============================================================
def db_path(code):
    return os.path.join(DATA_DIR, f"{code}.db")

def pdf_dir(code):
    d = os.path.join(DATA_DIR, "pdfs", code)
    os.makedirs(d, exist_ok=True)
    return d

# ============================================================
# 财报期间定义
# ============================================================
# A股 巨潮分类码
CNINFO_CATEGORIES = {
    "FY":  "category_ndbg_szsh;",   # 年度报告
    "H1":  "category_bndbg_szsh;",  # 半年度报告
    "Q1":  "category_yjdbg_szsh;",  # 一季报
    "Q3":  "category_sjdbg_szsh;",  # 三季报
}

# 港股 港交所披露易分类码
HKEX_CATEGORIES = {
    "FY":  {"t1code": "40000", "t2code": "40100"},  # 年报
    "H1":  {"t1code": "40000", "t2code": "40200"},  # 中期报告
    "Q1":  {"t1code": "10000", "t2code": "13600"},  # 一季报
    "Q3":  {"t1code": "10000", "t2code": "13600"},  # 三季报
}

# 期间中文名
PERIOD_NAME = {
    "FY": "年报",
    "H1": "中报",
    "Q1": "一季报",
    "Q3": "三季报",
}

# ============================================================
# 标题黑名单 (排除非财报公告)
# ============================================================
TITLE_BLACKLIST = [
    "摘要", "已取消", "已撤销", "撤回", "取消", "更正前",
    "募集说明书", "ESG", "可持续发展",
    "审计报告", "财务报表", "意见",
    "英文版", "英文简版", "(英文)", "english",
    "港股公告", "H股公告",
]

# ============================================================
# Value Line 24行指标定义 (完整复刻VL官方名称, A股/H股对齐)
# Gross Margin 置于 Revenues 与 Operating Margin 之间
# 分隔线: 每股(#6) | 估值(#10) | 利润表(#17) | 资产负债(#20)
# ============================================================
VL_METRICS = [
    # (行号, 中文名, 英文名(VL原文), 数据字段, 单位, 来源表)
    # === 每股指标 (1-6) ===
    (1,  "每股营收",     "Revenues per sh",           "PER_OI",               "元",   "calculated"),
    (2,  "每股现金流",   "\"Cash Flow\" per sh",       "PER_NETCASH",          "元",   "calculated"),
    (3,  "每股收益",     "Earnings per sh",            "BASIC_EPS",            "元",   "indicators"),
    (4,  "每股股息",     "Div'ds Decl'd per sh",       "DPS",                  "元",   "dividend"),
    (5,  "每股资本支出", "Cap'l Spending per sh",      "CAPEX_PS",             "元",   "calculated"),
    (6,  "每股账面价值", "Book Value per sh",          "BPS",                  "元",   "indicators"),
    # === 股本与估值 (7-10) ===
    (7,  "发行在外股数", "Common Shs Outst'g (Mill.)",  "TOTAL_SHARES",         "百万股","calculated"),
    (8,  "平均年化PE",   "Avg Ann'l P/E Ratio",        "PE_AVG",               "倍",   "calculated"),
    (9,  "相对PE",       "Relative P/E Ratio",         "PE_RELATIVE",          "倍",   "calculated"),
    (10, "平均股息率",   "Avg Ann'l Div'd Yield",      "DIV_YIELD",            "%",    "calculated"),
    # === 利润表指标 (11-17, Gross Margin 置于 Revenues 与 Op Margin 之间) ===
    (11, "总营收",       "Revenues (亿)",               "OPERATE_INCOME",       "亿",   "indicators"),
    (12, "毛利率",       "Gross Margin",               "GROSS_MARGIN",         "%",    "calculated"),
    (13, "营业利润率",   "Operating Margin",           "OP_MARGIN",            "%",    "calculated"),
    (14, "折旧摊销",     "Depreciation (亿)",           "DEPRECIATION",         "亿",   "cashflow"),
    (15, "净利润",       "Net Profit (亿)",             "HOLDER_PROFIT",        "亿",   "indicators"),
    (16, "所得税率",     "Income Tax Rate",            "TAX_EBT",              "%",    "indicators"),
    (17, "净利润率",     "Net Profit Margin",          "NET_PROFIT_RATIO",     "%",    "calculated"),
    # === 资产负债指标 (18-20) ===
    (18, "营运资金",     "Working Cap'l (亿)",          "WORKING_CAPITAL",      "亿",   "calculated"),
    (19, "长期债务",     "Long-Term Debt (亿)",         "LT_DEBT",              "亿",   "calculated"),
    (20, "股东权益",     "Shr. Equity (亿)",            "TOTAL_EQUITY",         "亿",   "calculated"),
    # === 回报率指标 (21-24) ===
    (21, "总资本回报率", "Return on Total Cap'l",      "ROIC",                 "%",    "calculated"),
    (22, "股东权益回报率","Return on Shr. Equity",      "ROE",                  "%",    "indicators"),
    (23, "留存利润占比", "Retained to Com Eq",         "RETAINED_RATIO",       "%",    "calculated"),
    (24, "股息支付率",   "All Div'ds to Net Prof",     "PAYOUT_RATIO",         "%",    "calculated"),
    # 单位: 元(per sh), 亿(aggregate), %(ratio), 百万股(shares)
    # * DILUTED_EPS优先, AKShare
    # † 宣告股息(Decl'd), AKShare
    # ‡ 对标HSI/CSI300, VL ~1700只
]

if __name__ == "__main__":
    print(f"项目路径: {BASE_DIR}")
    print(f"数据目录: {DATA_DIR}")
    print(f"当前标的: {ACTIVE_STOCK} {STOCKS[ACTIVE_STOCK]['name']}")
    print(f"SQLite: {db_path(ACTIVE_STOCK)}")
