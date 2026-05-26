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
        "currency": "HKD",
        "org_id": "9900047555",
        "hkex_stock_id": "1000068054",  # 披露易内部ID
        "pfx": "hk",
    },
    "600519": {
        "name": "贵州茅台",
        "name_en": "Kweichow Moutai",
        "market": "cn",
        "exchange": "SSE",
        "currency": "CNY",
        "org_id": "gssh0600519",      # 巨潮内部ID
        "pfx": "sh",
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
# Value Line 23行指标定义
# ============================================================
VL_METRICS = [
    # (行号, 中文名, 英文名, 数据字段, 单位, 来源表)
    (1,  "每股营收",     "Revenues per sh",        "PER_OI",               "元",   "indicators"),
    (2,  "每股现金流",   "Cash Flow per sh",        "PER_NETCASH_OPERATE",  "元",   "indicators"),
    (3,  "每股收益",     "Earnings per sh",         "BASIC_EPS",            "元",   "indicators"),
    (4,  "每股股息",     "Div'ds Decl'd per sh",    "DPS",                  "元",   "dividend"),
    (5,  "每股资本支出", "Cap'l Exp'd per sh",      "CAPEX_PS",             "元",   "calculated"),
    (6,  "每股账面价值", "Book Value per sh",       "BPS",                  "元",   "indicators"),
    (7,  "发行在外股数", "Common Shs Outst'g",      "TOTAL_SHARES",         "百万股","balance"),
    (8,  "平均年化PE",   "Avg Ann'l P/E Ratio",     "PE_AVG",               "倍",   "calculated"),
    (9,  "相对PE",       "Relative P/E Ratio",      "PE_RELATIVE",          "倍",   "calculated"),
    (10, "平均股息率",   "Avg Ann'l Div'd Yield",   "DIV_YIELD",            "%",    "calculated"),
    (11, "总营收",       "Revenues",                "OPERATE_INCOME",       "亿",   "indicators"),
    (12, "营业利润率",   "Operating Margin",        "OP_MARGIN",            "%",    "calculated"),
    (13, "折旧摊销",     "Depreciation",            "DEPRECIATION",         "亿",   "cashflow"),
    (14, "净利润",       "Net Profit",              "HOLDER_PROFIT",        "亿",   "indicators"),
    (15, "所得税率",     "Income Tax Rate",         "TAX_EBT",              "%",    "indicators"),
    (16, "净利润率",     "Net Profit Margin",       "NET_PROFIT_RATIO",     "%",    "indicators"),
    (17, "营运资金",     "Working Cap'l",           "WORKING_CAPITAL",      "亿",   "calculated"),
    (18, "长期债务",     "Long-Term Debt",          "LT_DEBT",              "亿",   "balance"),
    (19, "股东权益",     "Shr. Equity",             "TOTAL_EQUITY",         "亿",   "balance"),
    (20, "总资本回报率", "Return on Total Cap'l",   "ROIC_YEARLY",          "%",    "indicators"),
    (21, "股东权益回报率","Return on Shr. Equity",   "ROE_AVG",              "%",    "indicators"),
    (22, "留存利润占比", "Retained to Com Eq",      "RETAINED_RATIO",       "%",    "calculated"),
    (23, "股息支付率",   "All'd to Div'ds",         "PAYOUT_RATIO",         "%",    "calculated"),
]

if __name__ == "__main__":
    print(f"项目路径: {BASE_DIR}")
    print(f"数据目录: {DATA_DIR}")
    print(f"当前标的: {ACTIVE_STOCK} {STOCKS[ACTIVE_STOCK]['name']}")
    print(f"SQLite: {db_path(ACTIVE_STOCK)}")
