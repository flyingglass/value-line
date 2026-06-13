# -*- coding: utf-8 -*-
"""
tdx_client.py — TDX HTTP API 客户端，拉取港股三大财报
直接 HTTP 调用 TDX/TQLEX 内部接口，绕过 AKShare。

支持的数据接口：
- 港股损益表 (fixedTag=1) → income_table
- 港股资产负债表 (fixedTag=2) → balance_table
- 港股现金流量表 (fixedTag=3) → cashflow_table

用法示例：
    from tdx_client import fetch_hk_income
    rows = fetch_hk_income("00700")
    # rows = [{"截止日期": "2025-12-31", "营业额": 75176600, ...}, ...]
"""
import json
import os
import urllib.request
from typing import Any


def _load_dotenv():
    """从项目根目录 .env 加载环境变量（不依赖 python-dotenv）"""
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if not os.path.exists(env_path):
        return
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, val = line.partition("=")
            key, val = key.strip(), val.strip()
            if key and val and key not in os.environ:
                os.environ[key] = val


_load_dotenv()

# TDX API 端点 + 认证（从 .env 读取，不硬编码 token）
TDX_ENDPOINT = "http://tdxhub.icfqs.com:7615/TQLEX"
TDX_TOKEN = os.getenv("TDX_TOKEN", "")
if TDX_TOKEN and not TDX_TOKEN.startswith("Bearer "):
    TDX_TOKEN = f"Bearer {TDX_TOKEN}"

# Entry 名称
ENTRY = "TdxSharePCCW.skef10_hk_cwfx"

# 超时秒数
TIMEOUT = 30


def _call_tdx(fixed_tag: str, code: str, timeout: int = TIMEOUT) -> dict:
    """
    调用 TDX HTTP API，返回解析后的行列表。
    :param fixed_tag: "1"=损益表, "2"=资产负债表, "3"=现金流量表
    :param code: 5-digit HK stock code, e.g. "00700"
    :returns: {"rows": [...], "summary": "..."}
    """
    url = f"{TDX_ENDPOINT}?Entry={ENTRY}"
    data = json.dumps({"Params": [fixed_tag, code]}).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Content-Type": "application/json",
            "token": TDX_TOKEN,
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = json.loads(resp.read().decode("utf-8"))
    except urllib.error.URLError as e:
        raise RuntimeError(f"TDX 请求失败 [{fixed_tag}/{code}]: {e}")
    except json.JSONDecodeError as e:
        raise RuntimeError(f"TDX 响应解析失败 [{fixed_tag}/{code}]: {e}")

    # 直接 HTTP 响应格式: {ErrorCode, ResultSets: [...]}
    if body.get("ErrorCode", 0) != 0:
        raise RuntimeError(f"TDX ErrorCode={body.get('ErrorCode')} [{fixed_tag}/{code}]")
    result_sets = body.get("ResultSets", [])
    if not result_sets:
        return {"rows": [], "summary": "empty"}
    # 取第二个 ResultSet (table1) 作为数据表，第一个是 isjrl 标记
    data_set = result_sets[1] if len(result_sets) > 1 else result_sets[0]
    col_names = data_set.get("ColName", [])
    content = data_set.get("Content", [])
    # 将 ColName + Content 转为 dict 列表
    rows = []
    for row_data in content:
        row = {}
        for i, col_name in enumerate(col_names):
            if i < len(row_data) and row_data[i] is not None:
                row[col_name] = row_data[i]
        rows.append(row)
    return {"rows": rows, "summary": f"{code} 共 {len(rows)} 期数据"}


# ── TDX 原始英文字段 → 引擎期望的标准中文名 ──
# income (损益表) — ColName: bgq, StartDate, EndDate, ProfitBT, AJProfit, ProfitFO,
#   TurnOver, Depreciation, SExpense, Salaries, IExpense, Taxation, ProfitFTY,
#   SHProfit, MProfit, Dividends, EPSBasic, EPSDiluted, Currency, InfoDate, LastEndDate
_INCOME_NAME_MAP = {
    "bgq": "报告期",
    "EndDate": "截止日期",
    "TurnOver": "营业额",
    "ProfitFO": "经营溢利",
    "SExpense": "销售费用",
    "IExpense": "融资成本",          # 引擎查询 "融资成本"
    "SHProfit": "股东应占溢利",
    "MProfit": "少数股东应占溢利",
    "ProfitBT": "除税前盈利",
    "AJProfit": "应占联合营公司盈利",
    "Taxation": "所得税",
    "EPSBasic": "每股基本盈利",
    "EPSDiluted": "每股摊薄盈利",
    "Depreciation": "折旧及摊销",
    "ProfitFTY": "本年度溢利",
}

# balance (资产负债表) — 实际 ColName: bgq, StartDate, EndDate, TAssets, NAssets,
#   ProPlaEqu, AJEquity, CAssets, Inventory, RAccounts, CasDep, TLiab, CLiab,
#   PAccounts, SBLoan, CANet, NLiab, LBLoan, SHEquity, MEquity, SCapital,
#   Currency, InfoDate, LastEndDate
_BALANCE_NAME_MAP = {
    "bgq": "报告期",
    "EndDate": "截止日期",
    "TAssets": "总资产",
    "NAssets": "非流动资产合计",
    "ProPlaEqu": "固定资产",
    "AJEquity": "于联营公司及合营公司之权益",
    "CAssets": "流动资产合计",
    "Inventory": "存货",
    "RAccounts": "应收帐款",
    "CasDep": "现金及等价物",
    "TLiab": "总负债",
    "CLiab": "流动负债合计",
    "PAccounts": "应付账款",
    "SBLoan": "短期贷款",
    "CANet": "流动资产净值",
    "NLiab": "非流动负债合计",
    "LBLoan": "长期贷款",
    "SHEquity": "股东权益",
    "MEquity": "少数股东权益",
    "SCapital": "股本",
}

# cashflow (现金流量表) — 实际 ColName: bgq, StartDate, EndDate, ONetCash, CExpense,
#   INetCash, FNetCash, CENet, REffect, CEBeg, CEEnd, Currency, InfoDate, LastEndDate
_CASHFLOW_NAME_MAP = {
    "bgq": "报告期",
    "EndDate": "截止日期",
    "ONetCash": "经营活动产生的现金流量净额",
    "INetCash": "投资活动产生的现金流量净额",
    "FNetCash": "融资活动产生的现金流量净额",
    "CENet": "现金及现金等价物净值",
    "CExpense": "购建固定资产",
    "CEBeg": "期初现金及现金等价物",
    "CEEnd": "期末现金及现金等价物",
    "REffect": "汇率变动影响净值",
}


def _transform_rows(rows: list, name_map: dict, compute_equity: bool = False) -> list:
    """
    将 TDX 行转换为标准行格式（直接 INSERT 到 SQLite 用的 dict 列表）。
    :param rows: TDX 原始 rows (key=英文ColName)
    :param name_map: 字段名映射 {tdx_col: std_cn_name}
    :param compute_equity: 是否为资产负债表，自动计算总权益
    :returns: [{"report_date": "2025-12-31", "item_name": "营业额", "amount": 75176600}, ...]
    """
    result = []
    for row in rows:
        rd = row.get("EndDate", row.get("bgq", ""))
        if not rd:
            continue
        for tdx_name, std_name in name_map.items():
            if tdx_name in row and row[tdx_name] is not None:
                val = row[tdx_name]
                try:
                    amount = float(val)
                except (ValueError, TypeError):
                    continue
                if amount == 0:
                    continue
                result.append({
                    "report_date": rd,
                    "item_name": std_name,
                    "amount": amount,
                })

        # 资产负债表: 自动计算 "总权益" = 股东权益 + 少数股东权益
        if compute_equity:
            eq = row.get("SHEquity")
            minority = row.get("MEquity", 0)
            if eq is not None:
                try:
                    total = float(eq) + float(minority or 0)
                except (ValueError, TypeError):
                    total = 0
                if total > 0:
                    result.append({
                        "report_date": rd,
                        "item_name": "总权益",
                        "amount": total,
                    })

    return result


# ── 公开 API ──

def fetch_hk_income(code: str) -> list:
    """获取港股损益表，返回标准行列表"""
    resp = _call_tdx("1", code)
    return _transform_rows(resp["rows"], _INCOME_NAME_MAP)


def fetch_hk_balance(code: str) -> list:
    """获取港股资产负债表，返回标准行列表（含总权益）"""
    resp = _call_tdx("2", code)
    return _transform_rows(resp["rows"], _BALANCE_NAME_MAP, compute_equity=True)


def fetch_hk_cashflow(code: str) -> list:
    """获取港股现金流量表，返回标准行列表"""
    resp = _call_tdx("3", code)
    return _transform_rows(resp["rows"], _CASHFLOW_NAME_MAP)


if __name__ == "__main__":
    import sys
    code = sys.argv[1] if len(sys.argv) > 1 else "00700"

    print(f"=== 港股损益表 {code} ===")
    inc = fetch_hk_income(code)
    print(f"  共 {len(inc)} 条记录")
    if inc:
        latest = max(r["report_date"] for r in inc)
        items = set(r["item_name"] for r in inc if r["report_date"] == latest)
        print(f"  最新期: {latest}, {len(items)} 个项目: {sorted(items)}")

    print(f"\n=== 港股资产负债表 {code} ===")
    bal = fetch_hk_balance(code)
    print(f"  共 {len(bal)} 条记录")
    if bal:
        latest = max(r["report_date"] for r in bal)
        items = set(r["item_name"] for r in bal if r["report_date"] == latest)
        print(f"  最新期: {latest}, {len(items)} 个项目: {sorted(items)}")

    print(f"\n=== 港股现金流量表 {code} ===")
    cf = fetch_hk_cashflow(code)
    print(f"  共 {len(cf)} 条记录")
    if cf:
        latest = max(r["report_date"] for r in cf)
        items = set(r["item_name"] for r in cf if r["report_date"] == latest)
        print(f"  最新期: {latest}, {len(items)} 个项目: {sorted(items)}")
