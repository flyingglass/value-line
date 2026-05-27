# -*- coding: utf-8 -*-
"""
fetcher.py — AKShare 数据获取, 存入 SQLite
运行方式: python fetcher.py [code]
  不加参数: 使用 config.ACTIVE_STOCK
  加参数:   python fetcher.py 600519
"""
import os, sys, time, sqlite3, json
import warnings
warnings.filterwarnings("ignore")

# 项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config

# ---- 环境准备 ----
for k in list(os.environ.keys()):
    if any(x in k.upper() for x in ("PROXY", "HTTP_", "HTTPS_", "ALL_PROXY")):
        os.environ.pop(k, None)

import requests as _rq
_orig_init = _rq.Session.__init__
def _patched_init(self):
    _orig_init(self)
    self.trust_env = False
    self.proxies = {}
_rq.Session.__init__ = _patched_init

import akshare as ak

# ============================================================
# SQLite 工具
# ============================================================
class Store:
    def __init__(self, code):
        self.path = config.db_path(code)
        self.conn = sqlite3.connect(self.path)
        self._init_tables()

    def _init_tables(self):
        c = self.conn
        c.execute("""CREATE TABLE IF NOT EXISTS meta (
            key TEXT PRIMARY KEY, value TEXT)""")
        c.execute("""CREATE TABLE IF NOT EXISTS spot (
            date TEXT, price REAL, pe REAL, pb REAL, div_yield REAL,
            mkt_cap REAL, change_pct REAL, volume REAL, high_52w REAL, low_52w REAL)""")
        c.execute("""CREATE TABLE IF NOT EXISTS kline (
            date TEXT PRIMARY KEY, open REAL, high REAL, low REAL,
            close REAL, volume REAL, adjust TEXT)""")
        c.execute("""CREATE TABLE IF NOT EXISTS income (
            report_date TEXT, item_name TEXT, amount REAL, item_code TEXT,
            PRIMARY KEY (report_date, item_name))""")
        c.execute("""CREATE TABLE IF NOT EXISTS balance (
            report_date TEXT, item_name TEXT, amount REAL, item_code TEXT,
            PRIMARY KEY (report_date, item_name))""")
        c.execute("""CREATE TABLE IF NOT EXISTS cashflow (
            report_date TEXT, item_name TEXT, amount REAL, item_code TEXT,
            PRIMARY KEY (report_date, item_name))""")
        # 兼容旧表: 添加 item_code 列
        for tbl in ["income", "balance", "cashflow"]:
            try:
                c.execute(f"ALTER TABLE {tbl} ADD COLUMN item_code TEXT")
            except:
                pass  # 列已存在
        c.execute("""CREATE TABLE IF NOT EXISTS indicators (
            report_date TEXT, item_name TEXT, amount REAL,
            PRIMARY KEY (report_date, item_name))""")
        c.execute("""CREATE TABLE IF NOT EXISTS dividend (
            report_year TEXT, cash_dps REAL, special_dps REAL,
            ex_date TEXT, pay_date TEXT, total_amount REAL,
            PRIMARY KEY (report_year))""")
        c.execute("""CREATE TABLE IF NOT EXISTS revenue_structure (
            code TEXT, year TEXT, dim_type TEXT, dim_name TEXT,
            amount REAL, pct REAL,
            PRIMARY KEY (code, year, dim_type, dim_name))""")
        self.conn.commit()

    def set_meta(self, key, value):
        self.conn.execute(
            "INSERT OR REPLACE INTO meta VALUES (?,?)", (key, value))
        self.conn.commit()

    def get_meta(self, key):
        r = self.conn.execute(
            "SELECT value FROM meta WHERE key=?", (key,)).fetchone()
        return r[0] if r else None

    def upsert_indicators(self, report_date, items):
        """批量写入分析指标, 字段名→值"""
        for k, v in items.items():
            if v is None:
                continue
            try:
                self.conn.execute(
                    "INSERT OR REPLACE INTO indicators VALUES (?,?,?)",
                    (str(report_date), k, float(v)))
            except (ValueError, TypeError):
                pass
        self.conn.commit()

    def upsert_financials(self, table, df_batch):
        """将DataFrame行写入财务表"""
        for _, row in df_batch.iterrows():
            rd = str(row.get("REPORT_DATE", "")).split(" ")[0]
            name = str(row.get("STD_ITEM_NAME", ""))
            item_code = str(row.get("STD_ITEM_CODE", ""))
            try:
                amt = float(row.get("AMOUNT", 0))
            except (ValueError, TypeError):
                amt = 0
            self.conn.execute(
                f"INSERT OR REPLACE INTO {table} VALUES (?,?,?,?)",
                (rd, name, amt, item_code))
        self.conn.commit()

    def close(self):
        self.conn.close()

# ============================================================
# 行情数据
# ============================================================
def fetch_spot_hk(store, code):
    """港股实时行情"""
    print("  [spot_hk] ", end="", flush=True)
    df = ak.stock_hk_spot()
    row = df[df["代码"] == code]
    if row.empty:
        print("未找到")
        return
    r = row.iloc[0]
    store.conn.execute("DELETE FROM spot")
    store.conn.execute(
        "INSERT INTO spot VALUES (?,?,?,?,?,?,?,?,?,?)",
        (str(pd.Timestamp.now().date()), float(r.get("最新价", 0)),
         float(r.get("市盈率", 0)), float(r.get("市净率", 0)),
         0.0, float(r.get("总市值", 0)),
         float(r.get("涨跌幅", 0)), float(r.get("成交量", 0)),
         0.0, 0.0))
    store.conn.commit()
    print(f"OK 股价={r['最新价']}")

def fetch_spot_cn(store, code, pfx):
    """A股实时行情 (新浪)"""
    print("  [spot_cn] ", end="", flush=True)
    df = ak.stock_zh_a_spot()
    full_code = f"{pfx}{code}"
    row = df[df["代码"] == full_code]
    if row.empty:
        print("未找到")
        return
    r = row.iloc[0]
    store.conn.execute("DELETE FROM spot")
    store.conn.execute(
        "INSERT INTO spot VALUES (?,?,?,?,?,?,?,?,?,?)",
        (str(pd.Timestamp.now().date()), float(r.get("最新价", 0)),
         float(r.get("市盈率", 0)) if "市盈率" in df.columns else 0,
         float(r.get("市净率", 0)) if "市净率" in df.columns else 0,
         0.0, 0.0,
         float(r.get("涨跌幅", 0)), float(r.get("成交量", 0)),
         0.0, 0.0))
    store.conn.commit()
    print(f"OK 股价={r['最新价']}")

# ============================================================
# K线数据
# ============================================================
def fetch_kline_hk(store, code):
    """港股日线K线 (新浪)"""
    print("  [kline_hk] ", end="", flush=True)
    df = ak.stock_hk_daily(symbol=code, adjust="qfq")
    store.conn.execute("DELETE FROM kline WHERE adjust='qfq'")
    for _, r in df.iterrows():
        store.conn.execute(
            "INSERT OR REPLACE INTO kline VALUES (?,?,?,?,?,?,?)",
            (str(r["date"]).split(" ")[0],
             float(r.get("open", 0)), float(r.get("high", 0)),
             float(r.get("low", 0)), float(r.get("close", 0)),
             float(r.get("volume", 0)), "qfq"))
    store.conn.commit()
    print(f"OK {len(df)}条")

def fetch_kline_cn(store, code, pfx):
    """A股日线K线 (新浪)"""
    print("  [kline_cn] ", end="", flush=True)
    df = ak.stock_zh_a_daily(symbol=f"{pfx}{code}", adjust="qfq")
    store.conn.execute("DELETE FROM kline WHERE adjust='qfq'")
    for _, r in df.iterrows():
        store.conn.execute(
            "INSERT OR REPLACE INTO kline VALUES (?,?,?,?,?,?,?)",
            (str(r["date"]).split(" ")[0],
             float(r.get("open", 0)), float(r.get("high", 0)),
             float(r.get("low", 0)), float(r.get("close", 0)),
             float(r.get("volume", 0)), "qfq"))
    store.conn.commit()
    print(f"OK {len(df)}条")

# ============================================================
# 港股财务数据 (东方财富)
# ============================================================
def fetch_hk_financials(store, code):
    """港股三大表(含中报) + 分析指标 + 分红"""
    import pandas as pd
    # 三大表 — 用 "全部" 获取年报+中报
    for table, sym in [("income", "利润表"),
                       ("balance", "资产负债表"),
                       ("cashflow", "现金流量表")]:
        print(f"  [hk_{table}] ", end="", flush=True)
        df = ak.stock_financial_hk_report_em(
            stock=code, symbol=sym, indicator="全部")
        store.upsert_financials(table, df)
        # 统计各期间数量
        dates = df["REPORT_DATE"].apply(lambda x: str(x)[:10]).unique()
        n_annual = sum(1 for d in dates if d.endswith("12-31"))
        n_semi = sum(1 for d in dates if d.endswith("06-30"))
        print(f"OK {len(df)}行 ({n_annual}年报+{n_semi}中报)")

    # 分析指标
    print("  [hk_indicators] ", end="", flush=True)
    df = ak.stock_financial_hk_analysis_indicator_em(
        symbol=code, indicator="年度")
    # 将宽表转为 key-value
    for _, row in df.iterrows():
        rd = str(row.get("REPORT_DATE", "")).split(" ")[0]
        items = {}
        for col in df.columns:
            if col in ("SECUCODE", "SECURITY_CODE", "SECURITY_NAME_ABBR",
                       "ORG_CODE", "REPORT_DATE", "DATE_TYPE_CODE",
                       "START_DATE", "FISCAL_YEAR", "CURRENCY"):
                continue
            try:
                items[col] = float(row[col])
            except (ValueError, TypeError):
                pass
        store.upsert_indicators(rd, items)
    print(f"OK {len(df)}行")
    # 保存币种信息到 meta
    if len(df) > 0:
        raw_currency = str(df.iloc[0].get("CURRENCY", ""))
        if raw_currency:
            store.set_meta("currency", raw_currency)

    # 分红
    print("  [hk_dividend] ", end="", flush=True)
    df = ak.stock_hk_dividend_payout_em(symbol=code)
    for _, r in df.iterrows():
        store.conn.execute(
            "INSERT OR REPLACE INTO dividend VALUES (?,?,?,?,?,?)",
            (str(r.get("财政年度", "")),
             float(r.get("每股派息", 0)) if "每股派息" in df.columns else 0,
             0.0,
             str(r.get("除净日", "")),
             str(r.get("发放日", "")),
             float(r.get("总派息", 0)) if "总派息" in df.columns else 0))
    store.conn.commit()
    print(f"OK {len(df)}条")

    # 股息补充: AKShare港股股息经常返回0, 用已知数据覆盖
    _supplement_dividend(store, code)


def _supplement_dividend(store, code):
    """补充股息数据 (AKShare港股缺口)"""
    KNOWN_DPS = {
        "09992": {
            "2021": 0.1533, "2022": 0.1472, "2023": 0.3096,
            "2024": 0.9970, "2025": 0.3630,
        }
    }
    if code not in KNOWN_DPS:
        return
    for yr, dps in KNOWN_DPS[code].items():
        existing = store.conn.execute(
            "SELECT cash_dps FROM dividend WHERE report_year=?",
            (yr,)).fetchone()
        if existing and existing[0] > 0:
            continue
        store.conn.execute(
            "INSERT OR REPLACE INTO dividend (report_year, cash_dps, special_dps) VALUES (?,?,0)",
            (yr, dps))
    store.conn.commit()
    print(f"  [dividend_supp] OK {len(KNOWN_DPS[code])}年股息已补充")

# ============================================================
# A股财务数据 (同花顺 + 巨潮)
# ============================================================
def fetch_cn_financials(store, code):
    """A股三大表 (同花顺) + 指标 + 分红 (巨潮)"""
    # 三大表 - 同花顺
    for table, fn in [("income", ak.stock_financial_benefit_ths),
                       ("balance", ak.stock_financial_debt_ths),
                       ("cashflow", ak.stock_financial_cash_ths)]:
        print(f"  [cn_{table}] ", end="", flush=True)
        # 同花顺接口返回的列名不同, 统一处理
        df = fn(symbol=code)
        # 宽表→长表
        for idx, row in df.iterrows():
            item = row.get("报告期", str(idx))
            for col in df.columns[1:]:
                try:
                    amt = float(row[col])
                except (ValueError, TypeError):
                    continue
                store.conn.execute(
                    f"INSERT OR REPLACE INTO {table} VALUES (?,?,?)",
                    (str(item), str(col), amt))
        store.conn.commit()
        print(f"OK {len(df)}行")

    # 分析指标 - 同花顺新版
    print("  [cn_indicators] ", end="", flush=True)
    df = ak.stock_financial_abstract_new_ths(
        symbol=code, indicator="按报告期")
    for _, row in df.iterrows():
        item = str(row.get("报告期", ""))
        for col in df.columns:
            if col in ("报告期",):
                continue
            try:
                amt = float(row[col])
                store.conn.execute(
                    "INSERT OR REPLACE INTO indicators VALUES (?,?,?)",
                    (item, str(col), amt))
            except (ValueError, TypeError):
                pass
    store.conn.commit()
    print(f"OK {len(df)}行")

    # 分红 - 巨潮
    print("  [cn_dividend] ", end="", flush=True)
    df = ak.stock_dividend_cninfo(symbol=code)
    for _, r in df.iterrows():
        try:
            store.conn.execute(
                "INSERT OR REPLACE INTO dividend VALUES (?,?,?,?,?,?)",
                (str(r.get("分红年度", "")),
                 float(r.get("每股转增", 0) or 0),
                 0.0,
                 str(r.get("除权除息日", "")),
                 str(r.get("分红发放日", "")),
                 0.0))
        except Exception:
            pass
    store.conn.commit()
    print(f"OK {len(df)}条")

# ============================================================
# 主函数
# ============================================================
import pandas as pd

def fetch(code=None):
    code = code or config.ACTIVE_STOCK
    stock = config.STOCKS[code]
    market = stock["market"]
    print(f"\n{'='*50}")
    print(f"开始拉取: {stock['name']} ({code}) [{market}]")
    print(f"SQLite: {config.db_path(code)}")
    print(f"PDF: {config.pdf_dir(code)}")
    print(f"{'='*50}\n")

    store = Store(code)

    try:
        if market == "hk":
            # 港股
            fetch_spot_hk(store, code)
            time.sleep(0.5)
            fetch_kline_hk(store, code)
            time.sleep(0.5)
            fetch_hk_financials(store, code)
        else:
            # A股
            pfx = stock.get("pfx", "sh")
            fetch_spot_cn(store, code, pfx)
            time.sleep(1)
            fetch_kline_cn(store, code, pfx)
            time.sleep(1)
            fetch_cn_financials(store, code)

        store.set_meta("last_fetch", str(pd.Timestamp.now()))
        store.set_meta("code", code)
        store.set_meta("market", market)

        print(f"\n{'='*50}")
        print(f"拉取完成! 数据已存入 {config.db_path(code)}")
        print(f"{'='*50}")
    finally:
        store.close()

if __name__ == "__main__":
    code = sys.argv[1] if len(sys.argv) > 1 else None
    fetch(code)
