# -*- coding: utf-8 -*-
"""
generate_reading.py — 从 report_data.json 生成 VL 标准阅读报告 (Markdown)
严格遵循 docs/VL_READING_GUIDE.md 的阅读流程:
  1. Business 业务描述
  2. AI Commentary 4段 VL风格分析
  3. 23行指标表速览 + CAGR

用法:
  python generate_reading.py              # 生成 report_data.json 中当前标的
  python generate_reading.py 09992        # 指定代码
  python generate_reading.py --all        # 生成所有标的
"""
import json, os, sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
READING_DIR = os.path.join(BASE_DIR, "reading")
os.makedirs(READING_DIR, exist_ok=True)

# ---- helpers ----

def _fmt(val, unit="", decimals=1):
    """安全格式化数值"""
    if val is None:
        return "-"
    if isinstance(val, float):
        if abs(val) >= 100:
            return f"{val:,.0f}{unit}"
        return f"{val:,.{decimals}f}{unit}"
    return f"{val}{unit}"

def _fmt_pct(val, decimals=1):
    """格式化百分比"""
    if val is None:
        return "-"
    return f"{val:,.{decimals}f}%"

def _is_pos(val):
    """判断是否正值"""
    return val is not None and val > 0

def _trend_arrow(val):
    """简单趋势箭头"""
    if val is None:
        return "➡️"
    return "↗️" if val > 0 else ("↘️" if val < 0 else "➡️")

# 行业中文映射
INDUSTRY_CN = {
    "Consumer": "消费",
    "Consumer Staples": "必需消费",
    "Technology": "科技",
    "Energy": "能源",
    "Metals & Mining": "金属与矿业",
    "Media": "传媒",
    "Packaging": "包装",
    "Automotive": "汽车",
    "Healthcare": "医疗健康",
    "Home Appliances": "家电",
    "Pharmaceuticals": "制药",
    "Building Materials": "建材",
    "Utilities": "公用事业",
    "Insurance": "保险",
    "Financial Services": "金融服务",
}

# ---- 模块1: Business ----

def _render_business(data):
    """业务描述模块"""
    meta = data["meta"]
    business = data.get("analyst", {}).get("business", "")
    spot = data["spot"]

    lines = []
    lines.append("## 一、Business 业务描述")
    lines.append("")

    if business:
        lines.append(f"> {business}")
        lines.append("")

    # 关键信息卡片
    lines.append("| 项目 | 内容 |")
    lines.append("|------|------|")
    lines.append(f"| **代码** | {meta['code']} |")
    lines.append(f"| **市场** | {meta.get('market','').upper()} |")
    lines.append(f"| **行业** | {INDUSTRY_CN.get(meta.get('industry',''), meta.get('industry',''))} |")
    lines.append(f"| **货币** | {meta.get('currency','CNY')} |")

    ceo = meta.get("ceo", "")
    inc = meta.get("inc", "")
    if ceo or inc:
        lines.append(f"| **管理层** | CEO: {ceo or '-'} · 注册地: {inc or '-'} |")

    lines.append(f"| **股价** | {_fmt(spot.get('price'), ' ' + spot.get('price_ccy', meta.get('price_ccy','HKD')))} |")
    lines.append(f"| **PE(TTM)** | {_fmt(spot.get('pe'), 'x')} |")
    lines.append(f"| **总市值** | {_fmt(spot.get('mkt_cap'), ' 亿')} |")
    lines.append("")

    return "\n".join(lines)


# ---- 模块2: AI Commentary 4段 ----

def _render_commentary(data):
    """4段 VL 风格评论"""
    meta = data["meta"]
    commentary = data.get("analyst", {}).get("commentary", [])
    spot = data["spot"]
    cagr = data.get("cagr", {})
    yearly_hl = data.get("yearly_hl", [])
    position = data.get("position", {})

    lines = []
    lines.append("## 二、AI Commentary（4 段 VL 风格分析）")
    lines.append("")

    # 段1: 业绩快照
    lines.append("### 📈 段1：业绩快照")
    lines.append("")
    if len(commentary) >= 1:
        lines.append(commentary[0])
        lines.append("")
    else:
        # fallback: 自动生成
        rev_cagr = cagr.get("revenue", {}).get("1yr")
        eps_cagr = cagr.get("earnings", {}).get("1yr")
        lines.append(f"营收增长 {_fmt_pct(rev_cagr)}，每股收益增长 {_fmt_pct(eps_cagr)}。")
        lines.append("")

    # 段2: 每股资金流向
    lines.append("### 💰 段2：每股资金流向")
    lines.append("")
    if len(commentary) >= 2:
        lines.append(commentary[1])
        lines.append("")
    else:
        lines.append("（数据待生成）")
        lines.append("")

    # 段3: 业务质地 + 估值
    lines.append("### 🏢 段3：业务质地 + 估值")
    lines.append("")
    if len(commentary) >= 3:
        lines.append(commentary[3])
        lines.append("")
    else:
        # 从 spot 和 position 生成
        pe_cur = spot.get("pe")
        pe_pos = position.get("pe", {})
        pb_pos = position.get("pb", {})
        lines.append(f"当前 PE {_fmt(pe_cur, 'x')}，历史 PE 区间 {_fmt(pe_pos.get('min'), 'x')}~{_fmt(pe_pos.get('max'), 'x')}")
        lines.append(f"PB {_fmt(spot.get('pb'), 'x')}，股息率 {_fmt(spot.get('div_yield'), '%')}")
        lines.append("")

    # 段4: 转折点检测
    lines.append("### 🔍 段4：转折点检测 + 验证信号")
    lines.append("")
    if len(commentary) >= 4:
        lines.append(commentary[3])
        lines.append("")

    # 反转信号检测 (来自指南的4项)
    lines.append("| # | 信号 | 说明 |")
    lines.append("|---|------|------|")
    lines.append("| 1 | 营收增速反转 | 1yr 增速 > 0 且 5yr CAGR < -10% — 检测是否从长期收缩中恢复 |")
    lines.append("| 2 | 利润率反转 | 毛利率 1yr 改善 且 3yr 整体走低 — 检测利润率拐点 |")
    lines.append("| 3 | 现金流方向反转 | 净留存从正转负或反之 — 检测资金循环是否断裂 |")
    lines.append("| 4 | ROE 反转 | 1yr 变化 > 0 且 3yr 均值 < 0 — 检测 ROE 方向拐点 |")
    lines.append("")

    return "\n".join(lines)


# ---- 模块3: 23行指标表 ----

def _render_metrics(data):
    """23行指标表 + CAGR"""
    metric_defs = data.get("metric_defs", [])
    all_years = sorted(data.get("years", []))
    yearly_data = data.get("data", {})
    cagr = data.get("cagr", {})

    if not all_years:
        return "## 三、指标数据\n\n（暂无数据）\n"

    lines = []
    lines.append("## 三、23 行指标表速览")
    lines.append("")

    # 构建指标名 → 各年数据的映射
    metrics_map = {}
    for mdef in metric_defs:
        field = mdef["field"]
        name_cn = mdef["name_cn"]
        unit = mdef.get("unit", "")
        metrics_map[field] = {"name_cn": name_cn, "unit": unit, "values": {}}

    for yr in all_years:
        yr_data = yearly_data.get(yr, {})
        for field, info in metrics_map.items():
            info["values"][yr] = yr_data.get(field)

    # 选出要展示的关键行 (按 VL 指南的核心指标)
    key_fields = [
        "PER_OI", "PER_NETCASH", "BASIC_EPS", "DPS",
        "GROSS_MARGIN", "OP_MARGIN", "ROE", "ROIC",
        "BPS", "NET_PROFIT_RATIO",
    ]

    # 表头
    years_header = " | ".join([f" {y} " for y in all_years])
    lines.append(f"| 指标 | {years_header} | 趋势 |")
    sep = "|------" * (len(all_years) + 2) + "|"
    lines.append(sep)

    for field in key_fields:
        if field not in metrics_map:
            continue
        info = metrics_map[field]
        name = info["name_cn"]
        unit = info["unit"]
        values = info["values"]

        # 格式化每个年份的值
        yr_strs = []
        for y in all_years:
            v = values.get(y)
            if v is None:
                yr_strs.append(" - ")
            elif unit == "%":
                yr_strs.append(f" {_fmt_pct(v, 1)} ")
            elif unit in ("亿",):
                yr_strs.append(f" {_fmt(v, '', 1)} ")
            else:
                yr_strs.append(f" {_fmt(v, '', 2)} ")

        # 趋势
        vals_list = [values.get(y) for y in all_years if values.get(y) is not None]
        if len(vals_list) >= 2:
            arrow = _trend_arrow(vals_list[-1] - vals_list[0])
        else:
            arrow = "➡️"

        lines.append(f"| **{name}** |{'|'.join(yr_strs)}| {arrow} |")

    lines.append("")

    # ---- CAGR 复合增长率 ----
    lines.append("### CAGR 复合增长率（关键指标）")
    lines.append("")
    cagr_map = {
        "revenue": "每股营收",
        "eps": "每股收益",
        "cashflow": "每股现金流",
        "dividend": "每股股息",
        "equity": "每股账面价值",
    }
    lines.append("| 指标 | 1年 | 3年 | 5年 |")
    lines.append("|------|-----|-----|-----|")
    for key, label in cagr_map.items():
        c = cagr.get(key, {})
        lines.append(f"| {label} | {_fmt_pct(c.get('1yr'), 1)} | {_fmt_pct(c.get('3yr'), 1)} | {_fmt_pct(c.get('5yr'), 1)} |")
    lines.append("")

    return "\n".join(lines)


# ---- 模块4: 股价与市场表现 ----

def _render_price_history(data):
    """股价历史 and 估值区间"""
    yearly_hl = data.get("yearly_hl", [])
    position = data.get("position", {})
    spot = data.get("spot", {})
    returns = data.get("total_returns", {})
    meta = data.get("meta", {})

    if not yearly_hl:
        return ""

    lines = []
    lines.append("## 四、股价与市场表现")
    lines.append("")

    # 年度高低表
    lines.append("### 年度股价区间")
    lines.append("")
    ccy = meta.get("price_ccy", "HKD")
    lines.append("| 年份 | 最高 | 最低 | 波动 |")
    lines.append("|------|------|------|------|")
    for hl in yearly_hl:
        year = hl["year"]
        high = hl["high"]
        low = hl["low"]
        spread = high - low
        lines.append(f"| {year} | {_fmt(high, ' ' + ccy)} | {_fmt(low, ' ' + ccy)} | {_fmt(spread, ' ' + ccy)} |")
    lines.append("")

    # 回报率 vs 指数
    stock_ret = returns.get("stock", {})
    index_ret = returns.get("index", {})
    index_name = meta.get("index_name_cn", "指数")

    if stock_ret or index_ret:
        lines.append("### 历史回报率")
        lines.append("")
        lines.append(f"| 周期 | 个股回报 | {index_name}回报 |")
        lines.append("|------|----------|----------|")
        for period in ["1yr", "3yr", "5yr"]:
            s = stock_ret.get(period)
            i = index_ret.get(period)
            lines.append(f"| {period} | {_fmt_pct(s, 1)} | {_fmt_pct(i, 1)} |")
        lines.append("")

    # 估值区间
    pe_pos = position.get("pe", {})
    pb_pos = position.get("pb", {})

    if pe_pos or pb_pos:
        lines.append("### 估值区间")
        lines.append("")
        lines.append("| 估值指标 | 当前 | 最低 | 最高 | 均值 | 百分位 |")
        lines.append("|----------|------|------|------|------|--------|")
        if pe_pos:
            lines.append(f"| **PE** | {_fmt(pe_pos.get('current'), 'x')} | {_fmt(pe_pos.get('min'), 'x')} | {_fmt(pe_pos.get('max'), 'x')} | {_fmt(pe_pos.get('avg'), 'x')} | {_fmt_pct(pe_pos.get('pct'), 1)} |")
        if pb_pos:
            lines.append(f"| **PB** | {_fmt(pb_pos.get('current'), 'x')} | {_fmt(pb_pos.get('min'), 'x')} | {_fmt(pb_pos.get('max'), 'x')} | {_fmt(pb_pos.get('avg'), 'x')} | {_fmt_pct(pb_pos.get('pct'), 1)} |")
        lines.append("")

    return "\n".join(lines)


# ---- 模块5: 总结 ----

def _render_summary(data):
    """一句话总结"""
    lines = []
    lines.append("## 五、总结")
    lines.append("")
    lines.append("*本报告基于截至最新财年的公开财务数据，通过 Value Line 标准化框架生成。*")
    lines.append("*不构成投资建议。投资有风险，决策需谨慎。*")
    lines.append("")
    return "\n".join(lines)


# ---- 主入口 ----

def build_reading_report(data):
    """按 VL 阅读指南生成完整 Markdown 报告"""
    meta = data["meta"]
    spot = data["spot"]

    # 标题
    title = f"# {meta['name']} ({meta['code']}) — Value Line 阅读报告"
    subtitle = f"> 生成日: {meta.get('generated','')[:10]} | 股价: {_fmt(spot.get('price'), ' ' + meta.get('price_ccy','HKD'))} | PE(TTM): {_fmt(spot.get('pe'), 'x')} | 总市值: {_fmt(spot.get('mkt_cap'), ' 亿')}"
    toc = "**[Business](#一business-业务描述)** · **[Commentary](#二ai-commentary4-段-vl-风格分析)** · **[指标表](#三23-行指标表速览)** · **[股价](#四股价与市场表现)** · **[总结](#五总结)**"

    sections = [
        title,
        "",
        f"{meta.get('name_en','')} · {meta.get('exchange') or meta.get('market','').upper()} · {INDUSTRY_CN.get(meta.get('industry',''), meta.get('industry',''))}",
        "",
        subtitle,
        "",
        toc,
        "",
        "---",
        "",
        _render_business(data),
        "---",
        "",
        _render_commentary(data),
        "---",
        "",
        _render_metrics(data),
        "---",
        "",
        _render_price_history(data),
        "---",
        "",
        _render_summary(data),
    ]

    return "\n".join(sections)


def generate_one(code, data_path=None):
    """为单只股票生成阅读报告"""
    if data_path is None:
        data_path = os.path.join(BASE_DIR, "report_data.json")

    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    report = build_reading_report(data)

    out_path = os.path.join(READING_DIR, f"{code}.md")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"[OK] reading report generated: {out_path}")
    return out_path


def generate_all():
    """为所有标的生成阅读报告（需要 report_data.json 逐个存在）"""
    import config
    count = 0
    for code, stock in config.STOCKS.items():
        rpt_path = os.path.join(BASE_DIR, "report", f"{stock.get('name_en','') or code}.html")
        # 如果有 VL 图表报告，说明数据已生成
        json_path = os.path.join(BASE_DIR, "report_data.json")
        if os.path.exists(json_path):
            # 简单策略: 只生成当前 active stock
            pass

    # 实际上只对当前 report_data.json 对应的标的生成
    if os.path.exists(os.path.join(BASE_DIR, "report_data.json")):
        with open(os.path.join(BASE_DIR, "report_data.json"), "r", encoding="utf-8") as f:
            data = json.load(f)
        code = data["meta"]["code"]
        generate_one(code)
        count = 1
    print(f"共生成 {count} 份阅读报告")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="VL 阅读报告生成器")
    parser.add_argument("code", nargs="?", default=None, help="股票代码，默认从 report_data.json 读取当前标的")
    parser.add_argument("--all", action="store_true", help="生成所有标的")
    parser.add_argument("--json", default=None, help="指定 report_data.json 路径")

    args = parser.parse_args()

    if args.all:
        generate_all()
    elif args.code:
        generate_one(args.code, data_path=args.json)
    else:
        # 默认: 读取 report_data.json
        json_path = args.json or os.path.join(BASE_DIR, "report_data.json")
        if not os.path.exists(json_path):
            print(f"[ERROR] report_data.json not found, run engine.py first")
            sys.exit(1)
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        code = data["meta"]["code"]
        generate_one(code, data_path=json_path)
