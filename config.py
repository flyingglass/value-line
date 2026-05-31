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
        "business_desc": "",
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
ACTIVE_STOCK = "09992"

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
    (1,  "每股营收",     "Revenues per sh (¥)",       "PER_OI",               "元",   "calculated"),
    (2,  "每股现金流",   "\"Cash Flow\" per sh (¥)",   "PER_NETCASH",          "元",   "calculated"),
    (3,  "每股收益*",    "Earnings per sh (¥)",        "BASIC_EPS",            "元",   "indicators"),
    (4,  "每股股息†",    "Div'ds Decl'd per sh (¥)",   "DPS",                  "元",   "dividend"),
    (5,  "每股资本支出", "Cap'l Spending per sh (¥)",  "CAPEX_PS",             "元",   "calculated"),
    (6,  "每股账面价值", "Book Value per sh (¥)",      "BPS",                  "元",   "indicators"),
    # === 股本与估值 (7-10) ===
    (7,  "发行在外股数", "Common Shs Outst'g (mil)",   "TOTAL_SHARES",         "百万股","calculated"),
    (8,  "平均年化PE",   "Avg Ann'l P/E Ratio",        "PE_AVG",               "倍",   "calculated"),
    (9,  "相对PE‡",      "Relative P/E Ratio",         "PE_RELATIVE",          "倍",   "calculated"),
    (10, "平均股息率",   "Avg Ann'l Div'd Yield (%)",  "DIV_YIELD",            "%",    "calculated"),
    # === 利润表指标 (11-17, Gross Margin 置于 Revenues 与 Op Margin 之间) ===
    (11, "总营收",       "Revenues (¥亿)",             "OPERATE_INCOME",       "亿",   "indicators"),
    (12, "毛利率",       "Gross Margin (%)",           "GROSS_MARGIN",         "%",    "calculated"),
    (13, "营业利润率",   "Operating Margin (%)",       "OP_MARGIN",            "%",    "calculated"),
    (14, "折旧摊销",     "Depreciation (¥亿)",         "DEPRECIATION",         "亿",   "cashflow"),
    (15, "净利润*",      "Net Profit (¥亿)",           "HOLDER_PROFIT",        "亿",   "indicators"),
    (16, "所得税率",     "Income Tax Rate (%)",        "TAX_EBT",              "%",    "indicators"),
    (17, "净利润率",     "Net Profit Margin (%)",      "NET_PROFIT_RATIO",     "%",    "calculated"),
    # === 资产负债指标 (18-20) ===
    (18, "营运资金",     "Working Cap'l (¥亿)",        "WORKING_CAPITAL",      "亿",   "calculated"),
    (19, "长期债务",     "Long-Term Debt (¥亿)",       "LT_DEBT",              "亿",   "calculated"),
    (20, "股东权益",     "Shr. Equity (¥亿)",          "TOTAL_EQUITY",         "亿",   "calculated"),
    # === 回报率指标 (21-24) ===
    (21, "总资本回报率", "Return on Total Cap'l (%)",  "ROIC",                 "%",    "calculated"),
    (22, "股东权益回报率","Return on Shr. Equity (%)",  "ROE",                  "%",    "indicators"),
    (23, "留存利润占比", "Retained to Com Eq (%)",     "RETAINED_RATIO",       "%",    "calculated"),
    (24, "股息支付率",   "All Div'ds to Net Prof (%)", "PAYOUT_RATIO",         "%",    "calculated"),
    # 脚注:
    # * 稀释EPS, 未扣除非经常性损益
    # † 宣告股息(Decl'd), AKShare数据
    # ‡ 对标HSI/CSI300, VL原版对标~1700只股票
]

if __name__ == "__main__":
    print(f"项目路径: {BASE_DIR}")
    print(f"数据目录: {DATA_DIR}")
    print(f"当前标的: {ACTIVE_STOCK} {STOCKS[ACTIVE_STOCK]['name']}")
    print(f"SQLite: {db_path(ACTIVE_STOCK)}")
