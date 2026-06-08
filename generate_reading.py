# -*- coding: utf-8 -*-
"""
generate_reading.py — 从 report_data.json 生成 VL 标准阅读报告 (Markdown)
融合原生 VL 阅读指南 + 李录阅读法:
  前置. 李录式快速筛查卡片 (30秒)
  一.   Business 业务描述
  二.   Timeliness & Safety 评级 (VL 核心)
  三.   AI Commentary 5 段分析
  四.   24 行 Statistical Array (5组 + 诊断窗)
  五.   资本结构与流动性
  六.   价格图与市场表现
  七.   CAGR + 季度数据趋势
  八.   投资检查清单 + 总结

用法:
  python generate_reading.py              # 生成 report_data.json 中当前标的
  python generate_reading.py 09992        # 指定代码
  python generate_reading.py --all        # 生成所有标的
"""
import json, os, sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
READING_DIR = os.path.join(BASE_DIR, "report", "reading")
os.makedirs(READING_DIR, exist_ok=True)

# ---- helpers ----

def _fmt(val, unit="", decimals=1):
    if val is None: return "-"
    if isinstance(val, float):
        if abs(val) >= 100: return f"{val:,.0f}{unit}"
        return f"{val:,.{decimals}f}{unit}"
    return f"{val}{unit}"

def _fmt_pct(val, decimals=1):
    if val is None: return "-"
    return f"{val:,.{decimals}f}%"

def _fmt_sign(val):
    """带正负号格式化"""
    if val is None: return "-"
    return f"+{val:,.1f}" if val >= 0 else f"{val:,.1f}"

def _fmt_sign_pct(val, decimals=1):
    if val is None: return "-"
    return f"+{val:,.{decimals}f}%" if val >= 0 else f"{val:,.{decimals}f}%"

def _dir(val):
    """变化方向文字"""
    if val is None: return ""
    return "增长" if val > 0 else ("下降" if val < 0 else "持平")

def _arrow(val):
    if val is None: return "➡️"
    return "↗️" if val > 0 else ("↘️" if val < 0 else "➡️")

def _chg(cur, prev):
    return (cur / prev - 1) * 100 if cur and prev and prev > 0 else None

def _safe_div(a, b):
    return a / b if a is not None and b and b != 0 else None

INDUSTRY_CN = {
    "Consumer": "消费", "Consumer Staples": "必需消费", "Technology": "科技",
    "Energy": "能源", "Metals & Mining": "金属与矿业", "Media": "传媒",
    "Packaging": "包装", "Automotive": "汽车", "Healthcare": "医疗健康",
    "Home Appliances": "家电", "Pharmaceuticals": "制药", "Building Materials": "建材",
    "Utilities": "公用事业", "Insurance": "保险", "Financial Services": "金融服务",
}


# ============================================================
# 前置模块: 李录式快速筛查卡片
# ============================================================

def _render_quick_screen(data):
    """李录式 30 秒快速筛查 — 判断值不值得深读"""
    meta = data["meta"]
    spot = data.get("spot", {})
    years = data.get("years", [])
    metrics = data.get("data", {})

    if not years: return ""
    latest_yr = years[-1]
    ly = metrics.get(latest_yr, {})

    price = spot.get("price", 0) or 0
    pe = spot.get("pe", 0) or 0
    pb = spot.get("pb", 0) or 0
    median_pe = spot.get("median_pe")
    bps = ly.get("BPS")
    roce = ly.get("ROIC")
    roe = ly.get("ROE")
    lt_debt = ly.get("LT_DEBT") or 0
    working_cap = ly.get("WORKING_CAPITAL") or 0
    total_eq = ly.get("TOTAL_EQUITY") or 0

    # 李录式 5 秒判断
    checks = []

    # 1. 价格在净资产附近? (PB)
    if pb is not None:
        if pb <= 1.5:
            checks.append(("🟢", "PB", f"{pb:.1f}x", "接近净资产，便宜"))
        elif pb <= 3:
            checks.append(("🟡", "PB", f"{pb:.1f}x", "略高于净资产"))
        else:
            checks.append(("🔴", "PB", f"{pb:.1f}x", "远高于净资产，偏贵"))

    # 2. 账面资产干净?
    goodwill_pct = None
    if total_eq > 0:
        goodwill_pct = round((ly.get("GOODWILL", 0) or 0) / total_eq * 100, 1)
    if goodwill_pct is not None:
        if goodwill_pct < 10:
            checks.append(("🟢", "资产", f"商誉{goodwill_pct}%", "账面干净 ✅"))
        elif goodwill_pct < 30:
            checks.append(("🟡", "资产", f"商誉{goodwill_pct}%", "有一定商誉"))
        else:
            checks.append(("🔴", "资产", f"商誉{goodwill_pct}%", "商誉占比高"))

    # 3. ROIC > 15%?
    if roce is not None:
        if roce > 20:
            checks.append(("🟢", "ROIC", f"{roce:.1f}%", "生意很好"))
        elif roce > 10:
            checks.append(("🟡", "ROIC", f"{roce:.1f}%", "生意还行"))
        else:
            checks.append(("🔴", "ROIC", f"{roce:.1f}%", "生意一般"))

    # 4. 估值位置
    if pe and median_pe:
        pct = round(pe / median_pe * 100, 0)
        if pct < 70:
            checks.append(("🟢", "估值", f"PE {pe:.0f}x vs 中位{median_pe:.0f}x", "低于历史中枢"))
        elif pct < 130:
            checks.append(("🟡", "估值", f"PE {pe:.0f}x vs 中位{median_pe:.0f}x", "合理区间"))
        else:
            checks.append(("🔴", "估值", f"PE {pe:.0f}x vs 中位{median_pe:.0f}x", "高于历史中枢"))

    # 5. 负债安全?
    if lt_debt == 0:
        checks.append(("🟢", "负债", "零长期负债", "无债务风险"))
    elif total_eq > 0 and lt_debt / total_eq < 0.3:
        checks.append(("🟡", "负债", f"负债率{lt_debt/total_eq*100:.0f}%", "低杠杆"))
    else:
        checks.append(("🔴", "负债", f"负债率{lt_debt/total_eq*100:.0f}%" if total_eq > 0 else "", "高杠杆"))

    # 渲染卡片
    lines = []
    lines.append("## 🔍 李录式快速筛查（30 秒）")
    lines.append("")
    lines.append("> **李录心法**：跳过文案，直扑硬数据。一页资料，5 分钟判断值不值得深读。")
    lines.append("> 依次检查：便宜吗？ → 生意好吗？ → 资产干净吗？ → 管理层靠谱吗？")
    lines.append("")

    # 4 列卡片
    cols = [checks[i:i+4] for i in range(0, len(checks), 4)]
    for row_checks in cols:
        line = "|"
        sep = "|"
        for icon, label, value, note in row_checks:
            line += f" {icon} **{label}**: {value} |"
            sep += ":--|"
        lines.append(line)
        lines.append(sep)
        note_line = "|"
        for icon, label, value, note in row_checks:
            note_line += f" {note} |"
        lines.append(note_line)
        lines.append("")

    # 李录 5 问摘要
    green = sum(1 for c in checks if "🟢" in c[0])
    red = sum(1 for c in checks if "🔴" in c[0])

    if red == 0 and green >= 3:
        verdict = "✅ **通过快速筛查** — 价格合理、生意不错、资产干净。**值得深入阅读。**"
    elif red <= 1:
        verdict = "🟡 **谨慎乐观** — 部分指标需关注，但整体可读。建议深读后判断。"
    else:
        verdict = "🔴 **需谨慎** — 多项指标示警。不排除错杀可能，但需要更充分的证据。"

    lines.append(f"> {verdict}")
    lines.append("")
    lines.append("---")
    lines.append("")

    return "\n".join(lines)


# ============================================================
# 模块一: Business 业务描述
# ============================================================

def _render_business(data):
    meta = data["meta"]
    business = data.get("analyst", {}).get("business", "")
    spot = data["spot"]
    cap_struct = data.get("capital_structure", {})
    revenue_structure = data.get("revenue_structure", {})

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

    # 管理层持股 (李录关注点)
    emp_count = cap_struct.get("employee_count")
    if emp_count:
        lines.append(f"| **员工** | {emp_count/10000:.1f} 万人 ({cap_struct.get('employee_year','')}) |")

    lines.append(f"| **股价** | {_fmt(spot.get('price'), ' ' + meta.get('price_ccy', meta.get('currency','CNY')))} |")
    lines.append(f"| **PE(TTM)** | {_fmt(spot.get('pe'), 'x')} |")
    lines.append(f"| **总市值** | {_fmt(spot.get('mkt_cap'), ' 亿')} |")
    lines.append("")

    # 收入结构
    by_ip = revenue_structure.get("by_ip", [])
    by_region = revenue_structure.get("by_region", [])
    by_channel = revenue_structure.get("by_channel", [])
    by_product = revenue_structure.get("by_product", [])

    seg = by_ip or by_product or by_channel
    if seg:
        lines.append("### 收入结构")
        lines.append("")
        years_data = data.get("years", [])
        latest_yr = years_data[-1] if years_data else ""
        lines.append(f"| 来源 | FY{latest_yr} |")
        lines.append("|------|------|")
        for s in seg[:5]:
            lines.append(f"| {s['name']} | {s['pct']}% |")
        lines.append("")

    if by_region and len(by_region) >= 2:
        lines.append("### 地域分布")
        lines.append("")
        lines.append("| 地区 | 占比 |")
        lines.append("|------|------|")
        for r in by_region[:5]:
            lines.append(f"| {r['name']} | {r['pct']}% |")
        lines.append("")

    return "\n".join(lines)


# ============================================================
# 模块二: Timeliness & Safety 评级
# ============================================================

def _compute_ratings(data):
    """从数据计算 VL 三大评级 (Timeliness / Safety / Technical)"""
    spot = data.get("spot", {})
    years = data.get("years", [])
    metrics = data.get("data", {})
    cagr = data.get("cagr", {})
    position = data.get("position", {})
    total_returns = data.get("total_returns", {})

    result = {"timeliness": 3, "safety": 3, "technical": 3,
              "timeliness_detail": [], "safety_detail": [], "technical_detail": []}

    if not years:
        return result

    latest_yr = years[-1]
    ly = metrics.get(latest_yr, {})

    # ---- Timeliness: 基于 PE 百分位 + EPS 增速 + 价格动量 ----
    pe_pos = position.get("pe", {})
    pe_pct = pe_pos.get("pct")
    eps_1yr = cagr.get("eps", {}).get("1yr")
    stock_1yr = total_returns.get("stock", {}).get("1yr")

    score = 0
    if pe_pct is not None:
        if pe_pct < 20: score += 2; result["timeliness_detail"].append(("PE 百分位", f"底部 {pe_pct:.0f}%", "+2"))
        elif pe_pct < 40: score += 1; result["timeliness_detail"].append(("PE 百分位", f"偏低 {pe_pct:.0f}%", "+1"))
        elif pe_pct > 80: score -= 2; result["timeliness_detail"].append(("PE 百分位", f"顶部 {pe_pct:.0f}%", "-2"))
        elif pe_pct > 60: score -= 1; result["timeliness_detail"].append(("PE 百分位", f"偏高 {pe_pct:.0f}%", "-1"))
        else: result["timeliness_detail"].append(("PE 百分位", f"中间 {pe_pct:.0f}%", "0"))

    if eps_1yr is not None:
        if eps_1yr > 20: score += 2; result["timeliness_detail"].append(("EPS 1yr 增速", f"{eps_1yr:+.1f}%", "+2"))
        elif eps_1yr > 5: score += 1; result["timeliness_detail"].append(("EPS 1yr 增速", f"{eps_1yr:+.1f}%", "+1"))
        elif eps_1yr < -10: score -= 2; result["timeliness_detail"].append(("EPS 1yr 增速", f"{eps_1yr:+.1f}%", "-2"))
        elif eps_1yr < 0: score -= 1; result["timeliness_detail"].append(("EPS 1yr 增速", f"{eps_1yr:+.1f}%", "-1"))
        else: result["timeliness_detail"].append(("EPS 1yr 增速", f"{eps_1yr:+.1f}%", "0"))

    if stock_1yr is not None:
        if stock_1yr > 20: score += 1; result["timeliness_detail"].append(("价格动量 1yr", f"{stock_1yr:+.1f}%", "+1"))
        elif stock_1yr < -20: score -= 1; result["timeliness_detail"].append(("价格动量 1yr", f"{stock_1yr:+.1f}%", "-1"))

    if score >= 3: result["timeliness"] = 1
    elif score >= 1: result["timeliness"] = 2
    elif score >= -1: result["timeliness"] = 3
    elif score >= -3: result["timeliness"] = 4
    else: result["timeliness"] = 5

    # ---- Safety: 杠杆 + ROE 稳定性 + 波动 ----
    lt_debt = ly.get("LT_DEBT") or 0
    total_eq = ly.get("TOTAL_EQUITY") or 1
    debt_ratio = lt_debt / total_eq if total_eq > 0 else 0

    safety_score = 0
    if debt_ratio < 0.1: safety_score += 1; result["safety_detail"].append(("负债率", f"{debt_ratio*100:.0f}% (极低)", "+1"))
    elif debt_ratio < 0.3: result["safety_detail"].append(("负债率", f"{debt_ratio*100:.0f}% (偏低)", "0"))
    elif debt_ratio < 0.6: safety_score -= 1; result["safety_detail"].append(("负债率", f"{debt_ratio*100:.0f}% (偏高)", "-1"))
    else: safety_score -= 2; result["safety_detail"].append(("负债率", f"{debt_ratio*100:.0f}% (高)", "-2"))

    # ROE 稳定性
    roe_vals = [metrics.get(y, {}).get("ROE") for y in years[-5:]]
    roe_vals = [v for v in roe_vals if v is not None]
    if len(roe_vals) >= 3:
        import math
        mean_roe = sum(roe_vals) / len(roe_vals)
        variance = sum((v - mean_roe)**2 for v in roe_vals) / len(roe_vals)
        std_roe = math.sqrt(variance)
        cv = std_roe / mean_roe if mean_roe > 0 else 999
        if cv < 0.3: safety_score += 1; result["safety_detail"].append(("ROE 稳定", f"CV={cv:.2f} (稳定)", "+1"))
        elif cv > 0.7: safety_score -= 1; result["safety_detail"].append(("ROE 稳定", f"CV={cv:.2f} (波动)", "-1"))
        else: result["safety_detail"].append(("ROE 稳定", f"CV={cv:.2f} (适中)", "0"))

    if safety_score >= 2: result["safety"] = 1
    elif safety_score >= 0: result["safety"] = 2
    elif safety_score >= -1: result["safety"] = 3
    elif safety_score >= -2: result["safety"] = 4
    else: result["safety"] = 5

    # ---- Technical: 价格动量 ----
    tech_score = 0
    if stock_1yr is not None:
        if stock_1yr > 30: tech_score = 1
        elif stock_1yr > 0: tech_score = 2
        elif stock_1yr > -20: tech_score = 3
        elif stock_1yr > -40: tech_score = 4
        else: tech_score = 5
    else:
        tech_score = 3
    result["technical"] = tech_score
    result["technical_detail"].append(("价格动量 1yr", f"{stock_1yr:+.1f}%" if stock_1yr else "-", str(tech_score)))

    return result


def _render_ratings(data):
    """Timeliness & Safety 评级模块"""
    ratings = _compute_ratings(data)
    spot = data.get("spot", {})

    timeliness = ratings["timeliness"]
    safety = ratings["safety"]
    technical = ratings["technical"]

    t_emoji = {1: "🟢", 2: "🟢", 3: "🟡", 4: "🟠", 5: "🔴"}.get(timeliness, "⚪")
    s_emoji = {1: "🟢", 2: "🟢", 3: "🟡", 4: "🟠", 5: "🔴"}.get(safety, "⚪")
    tech_emoji = {1: "🟢", 2: "🟢", 3: "🟡", 4: "🟠", 5: "🔴"}.get(technical, "⚪")

    t_label = {1: "最高 (Top 100)", 2: "高于平均", 3: "中性", 4: "低于平均", 5: "最低 (Bottom 100)"}
    s_label = {1: "最安全", 2: "较安全", 3: "中性", 4: "较低", 5: "不安全"}
    tech_label = {1: "最强", 2: "偏强", 3: "中性", 4: "偏弱", 5: "最弱"}

    pe = spot.get("pe", 0) or 0
    median_pe = spot.get("median_pe")

    lines = []
    lines.append("## 二、Timeliness & Safety 评级")
    lines.append("")

    # 三栏评级
    lines.append(f"| **Timeliness 时效性** | **Safety 安全性** | **Technical 技术** |")
    lines.append("|:--:|:--:|:--:|")
    lines.append(f"| {t_emoji} **{timeliness}** - {t_label.get(timeliness, '')} | {s_emoji} **{safety}** - {s_label.get(safety, '')} | {tech_emoji} **{technical}** - {tech_label.get(technical, '')} |")
    lines.append(f"| 6-12个月预期表现 | 财务稳定性 + 股价风险 | 价格动量 |")
    lines.append("")

    # Timeliness 详情
    lines.append("### Timeliness 时效性详情")
    lines.append("")
    lines.append("| 评分因子 | 数据 | 得分 |")
    lines.append("|----------|------|------|")
    for name, data_val, score in ratings["timeliness_detail"]:
        lines.append(f"| {name} | {data_val} | {score} |")
    t_desc = {
        1: "未来 6-12 个月预期跑赢约 95% 的 VL 样本内股票",
        2: "预期表现优于多数股票（约前 30%）",
        3: "预期表现与市场持平",
        4: "预期表现低于多数股票（约后 30%）",
        5: "预期表现较差，需谨慎"
    }
    lines.append(f"\n> **综合 Timeliness: {timeliness}** — {t_desc.get(timeliness, '')}")
    lines.append("")

    # Safety 详情
    lines.append("### Safety 安全性详情")
    lines.append("")
    lines.append("| 评分因子 | 数据 | 得分 |")
    lines.append("|----------|------|------|")
    for name, data_val, score in ratings["safety_detail"]:
        lines.append(f"| {name} | {data_val} | {score} |")
    s_desc = {
        1: "财务稳健，波动性低，适合保守型投资者",
        2: "相对安全，财务指标良好",
        3: "中等风险，适合有一定风险承受能力的投资者",
        4: "风险偏高，需关注财务稳定性",
        5: "高风险，财务或经营存在重大不确定性"
    }
    lines.append(f"\n> **综合 Safety: {safety}** — {s_desc.get(safety, '')}")
    lines.append("")

    lines.append("---")
    lines.append("")
    return "\n".join(lines)


# ============================================================
# 模块三: AI Commentary 5 段分析
# ============================================================

def _render_commentary(data):
    """5 段 VL 风格评论: 业绩归因 | 资金循环 | 业务质地 | 估值锚定 | 验证信号"""
    meta = data["meta"]
    commentary = data.get("analyst", {}).get("commentary", [])
    spot = data.get("spot", {})
    cagr = data.get("cagr", {})
    metrics = data.get("data", {})
    years = data.get("years", [])
    revenue_structure = data.get("revenue_structure", {})
    position = data.get("position", {})

    if not years: return "## 三、AI Commentary\n\n（数据不足）\n"

    latest_yr = years[-1]
    ly = metrics.get(latest_yr, {})
    prev_yr = years[-2] if len(years) >= 2 else None
    py = metrics.get(prev_yr, {}) if prev_yr else {}

    lines = []
    lines.append("## 三、AI Commentary（5 段 VL 风格分析）")
    lines.append("")

    # ---- 段1: 业绩快照与变化归因 ----
    lines.append("### 📈 段1：业绩快照与变化归因")
    lines.append("")
    if len(commentary) >= 1 and commentary[0]:
        lines.append(commentary[0])
        lines.append("")
    else:
        rev = ly.get("OPERATE_INCOME")
        np_val = ly.get("HOLDER_PROFIT")
        eps = ly.get("BASIC_EPS")
        rev_chg = _chg(rev, py.get("OPERATE_INCOME"))
        np_chg = _chg(np_val, py.get("HOLDER_PROFIT"))
        gm = ly.get("GROSS_MARGIN")
        npm = ly.get("NET_PROFIT_RATIO")

        parts = []
        if rev: parts.append(f"营收 {_fmt(rev, '亿')} ({_dir(rev_chg)} {_fmt_pct(abs(rev_chg) if rev_chg else None)})")
        if np_val: parts.append(f"扣非净利润 {_fmt(np_val, '亿')} ({_dir(np_chg)} {_fmt_pct(abs(np_chg) if np_chg else None)})")
        if eps: parts.append(f"每股收益 ¥{eps:.2f}")

        if np_chg is not None and rev_chg is not None and abs(np_chg - rev_chg) > 10:
            if np_chg > rev_chg:
                parts.append(f"利润超营收增长，经营杠杆释放，净利润率 {_fmt_pct(npm)}")
            else:
                parts.append(f"利润增速落后营收，成本承压")
        lines.append("，".join(parts) + "。")
        lines.append("")

    # ---- 段2: 每股资金流向与现金循环 ----
    lines.append("### 💰 段2：每股资金流向与现金循环")
    lines.append("")
    if len(commentary) >= 2 and commentary[1]:
        lines.append(commentary[1])
        lines.append("")
    else:
        per_oi = ly.get("PER_OI")
        eps = ly.get("BASIC_EPS")
        per_cf = ly.get("PER_NETCASH")
        per_capex = ly.get("CAPEX_PS") or 0
        dps = ly.get("DPS") or 0
        op_margin = ly.get("OP_MARGIN")
        tax_rate = (ly.get("TAX_EBT", 25) or 25) / 100
        payout = ly.get("PAYOUT_RATIO")

        if per_oi and op_margin and eps and per_cf:
            op_eps = round(per_oi * (op_margin / 100) * (1 - tax_rate), 2)
            nonop_eps = round(eps - op_eps, 2)
            op_pct = round(op_eps / eps * 100) if eps else 0
            nonop_pct = round(nonop_eps / eps * 100) if eps else 0
            net_ps = round(per_cf - per_capex - dps, 2)

            lines.append(f"每股收益 ¥{eps:.2f} 中，主业贡献 ¥{op_eps:.2f} ({op_pct}%)，非经营性 ¥{nonop_eps:.2f} ({nonop_pct}%)。")
            lines.append(f"每股现金流 ¥{per_cf:.2f}（内生现金生成 = 净利润 + 折旧），四大去向：")
            lines.append(f"① 资本支出 ¥{per_capex:.2f}/股（扩建/更换厂房设备）；")

            # 营运资金变化
            shares_cur = ly.get("TOTAL_SHARES")
            shares_prev = py.get("TOTAL_SHARES") if years and len(years) >= 2 else None
            wc_cur = ly.get("WORKING_CAPITAL")
            wc_prev = py.get("WORKING_CAPITAL") if years and len(years) >= 2 else None
            if wc_cur is not None and wc_prev is not None:
                wc_chg = round(wc_cur - wc_prev, 1)
                wc_chg_ps = f"折合¥{abs(wc_chg * 100 / shares_cur):.2f}/股，" if shares_cur and shares_cur > 0 else ""
                if wc_chg > 0:
                    lines.append(f"② 营运资金占用 +{wc_chg:.1f}亿（{wc_chg_ps}扩张期正常，需关注效率）；")
                elif wc_chg < 0:
                    lines.append(f"② 营运资金释放 {wc_chg:.1f}亿（{wc_chg_ps}快收慢付，竞争优势 ✅）；")
                else:
                    lines.append(f"② 营运资金基本持平；")

            # 股利
            pay_str = f"（支付率{payout:.0f}%）" if payout else ""
            lines.append(f"③ 现金分红 ¥{dps:.2f}/股{pay_str}；")

            # 回购检测（通过股数变化）
            if shares_cur and shares_prev and shares_prev > 0:
                shr_chg = round((shares_cur - shares_prev) / shares_prev * 100, 1)
                if shr_chg < -0.3:
                    lines.append(f"④ 股份回购（股数 {shr_chg:+.1f}%）— 增厚每股价值 ✅；")
                elif shr_chg > 1:
                    lines.append(f"④ 股本扩张（股数 {shr_chg:+.1f}%）— 摊薄每股指标 ⚠️；")
                else:
                    lines.append(f"④ 股数基本持平；")

            if net_ps > 0:
                lines.append(f"净留存 ¥{net_ps:.2f}/股，现金流充裕 ✅。")
            else:
                lines.append(f"入不敷出 ¥{net_ps:.2f}/股，消耗存量现金 ⚠️。")
        lines.append("")

    # ---- 段3: 业务质地与竞争壁垒 ----
    lines.append("### 🏢 段3：业务质地与竞争壁垒")
    lines.append("")
    if len(commentary) >= 3 and commentary[2]:
        lines.append(commentary[2])
        lines.append("")
    else:
        roce = ly.get("ROIC")
        roe = ly.get("ROE")
        npm = ly.get("NET_PROFIT_RATIO")
        lt_debt = ly.get("LT_DEBT") or 0

        parts = []
        if roce: parts.append(f"ROIC {roce:.1f}%")
        if roe:
            roe_str = f"ROE {roe:.1f}%"
            roe_p = py.get("ROE")
            if roe_p: roe_str += f"(同比{_dir(roe - roe_p)})"
            parts.append(roe_str)
        if npm: parts.append(f"净利润率 {npm:.1f}%")
        if lt_debt == 0: parts.append("零长期负债，经营效率驱动回报")

        seg = revenue_structure.get("by_ip", []) or revenue_structure.get("by_product", [])
        if seg and len(seg) >= 2:
            parts.append(f"以{seg[0]['name']}({seg[0]['pct']}%)和{seg[1]['name']}({seg[1]['pct']}%)为主")

        lines.append("，".join(parts) + "。")
        lines.append("")

    # ---- 段4: 估值锚定与安全边际 ----
    lines.append("### 🎯 段4：估值锚定与安全边际")
    lines.append("")
    if len(commentary) >= 4 and commentary[3]:
        lines.append(commentary[3])
        lines.append("")
    else:
        pe = spot.get("pe", 0) or 0
        median_pe = spot.get("median_pe")
        pb = spot.get("pb", 0) or 0
        div_yield = spot.get("div_yield", 0) or 0
        bps = ly.get("BPS")
        working_cap = ly.get("WORKING_CAPITAL") or 0

        pe_pos = position.get("pe", {})
        pe_pct = pe_pos.get("pct")

        parts = []
        if pe and median_pe:
            vs = "低于" if pe < median_pe else "高于"
            parts.append(f"PE {pe:.1f}x ({vs}历史中位数 {median_pe:.1f}x)")
        if pe_pct is not None:
            parts.append(f"历史百分位 {pe_pct:.0f}%")
        if pb: parts.append(f"PB {pb:.2f}x")
        if div_yield: parts.append(f"股息率 {div_yield:.2f}%")

        lines.append("，".join(parts) + "。")
        lines.append("")

    # ---- 段5: 转折点检测与验证信号 ----
    lines.append("### 🔍 段5：转折点检测与待验证信号")
    lines.append("")

    # 4 项反转检测
    rev_1yr = cagr.get("revenue", {}).get("1yr")
    rev_5yr = cagr.get("revenue", {}).get("5yr")
    gm = ly.get("GROSS_MARGIN")
    gm_p = py.get("GROSS_MARGIN")
    eps_1yr = cagr.get("eps", {}).get("1yr")
    eps_3yr = cagr.get("eps", {}).get("3yr")
    roe = ly.get("ROE")
    roe_p = py.get("ROE")
    net_ps = None
    per_cf = ly.get("PER_NETCASH")
    per_capex = ly.get("CAPEX_PS") or 0
    dps = ly.get("DPS") or 0
    if per_cf: net_ps = round(per_cf - per_capex - dps, 2)

    triggers = []
    # 1. 营收反转
    rev_trig = rev_1yr is not None and rev_1yr > 0 and rev_5yr is not None and rev_5yr < -10
    triggers.append((1, "营收增速反转", "✅ 触发" if rev_trig else "➡️ 未触发",
        "1yr>0 且 5yr CAGR<-10 — 检测从长期收缩恢复" if rev_trig else "未检测到营收从收缩中恢复的信号"))

    # 2. 利润率反转
    margin_trig = gm and gm_p and gm > gm_p
    gm_3y_vals = [metrics.get(str(y), {}).get("GROSS_MARGIN") for y in years[-3:]]
    gm_3y_vals = [v for v in gm_3y_vals if v is not None]
    if margin_trig and len(gm_3y_vals) >= 2:
        margin_trig = gm_3y_vals[-1] > gm_3y_vals[0]
    triggers.append((2, "利润率反转", "✅ 触发" if margin_trig else "➡️ 未触发",
        f"毛利率 {gm:.1f}% (去年 {gm_p:.1f}%) — 盈利质量边际改善" if margin_trig else "毛利率未出现持续改善"))

    # 3. 现金流反转
    cf_trig = None
    py_cf = py.get("PER_NETCASH")
    if net_ps is not None and py_cf is not None:
        py_net = round(py_cf - (py.get("CAPEX_PS") or 0) - (py.get("DPS") or 0), 2)
        if net_ps > 0 and py_net < 0: cf_trig = True
        elif net_ps < 0 and py_net > 0: cf_trig = True
        else: cf_trig = False
    triggers.append((3, "现金流方向反转", "✅ 触发" if cf_trig else "➡️ 未触发",
        "净留存由负转正/由正转负" if cf_trig else "现金流方向未改变"))

    # 4. ROE 反转
    roe_trig = False
    if roe and roe_p and roe > roe_p * 1.1:
        roe_vals = [metrics.get(str(y), {}).get("ROE") for y in years]
        roe_vals = [v for v in roe_vals if v is not None]
        if len(roe_vals) >= 3:
            avg_prev = sum(roe_vals[:-1]) / (len(roe_vals) - 1)
            roe_trig = roe_vals[-1] > avg_prev * 1.1
    triggers.append((4, "ROE 反转", "✅ 触发" if roe_trig else "➡️ 未触发",
        f"ROE {roe:.1f}% 较近期均值大幅改善" if roe_trig else "ROE 未出现显著反转"))

    lines.append("| # | 信号 | 状态 | 说明 |")
    lines.append("|---|------|------|------|")
    for num, name, status, desc in triggers:
        lines.append(f"| {num} | {name} | {status} | {desc} |")
    lines.append("")

    # 验证信号
    watch_items = []
    pe = spot.get("pe", 0) or 0
    median_pe = spot.get("median_pe")
    if net_ps is not None and net_ps < 0:
        watch_items.append(f"关注 {int(latest_yr)+1} 年中报净留存是否回升")
    if pe and median_pe and pe < median_pe * 0.6:
        watch_items.append("估值处历史低位，需业绩拐点确认")
    elif pe and median_pe and pe > median_pe * 1.5 and pe > 15:
        watch_items.append("估值高于历史中枢，需盈利增长验证")

    if rev_1yr is not None and eps_3yr is not None and rev_1yr > eps_3yr * 2:
        watch_items.append(f"营收爆发增速({rev_1yr:+.1f}%)vs 3年EPS均值({eps_3yr:+.1f}%)，关注利润率能否跟上")

    if watch_items:
        lines.append("**⚠️ 待验证信号：**")
        for item in watch_items:
            lines.append(f"- {item}")
        lines.append("")

    lines.append("---")
    lines.append("")
    return "\n".join(lines)


# ============================================================
# 模块四: 24 行 Statistical Array (5组 + 诊断窗)
# ============================================================

def _render_stat_array(data):
    """24 行指标表，按 VL 标准 5 组展示，每组附诊断窗"""
    metric_defs = data.get("metric_defs", [])
    all_years = sorted(data.get("years", []))
    metrics = data.get("data", {})

    if not all_years: return "## 四、Statistical Array\n\n（暂无数据）\n"

    # 构建指标映射
    metrics_map = {}
    for mdef in metric_defs:
        field = mdef["field"]
        name_cn = mdef["name_cn"]
        name_en = mdef.get("name_en", "")
        unit = mdef.get("unit", "")
        order = mdef.get("order", 0)
        metrics_map[field] = {"name_cn": name_cn, "name_en": name_en, "unit": unit, "order": order, "values": {}}

    for yr in all_years:
        yr_data = metrics.get(yr, {})
        for field, info in metrics_map.items():
            info["values"][yr] = yr_data.get(field)

    # 获取最近年份数据用于诊断
    latest_yr = all_years[-1]
    ly = metrics.get(latest_yr, {})
    prev_yr = all_years[-2] if len(all_years) >= 2 else None
    py = metrics.get(prev_yr, {}) if prev_yr else {}

    # 显示最近的年份 (最多 8 年)
    display_years = all_years[-8:] if len(all_years) > 8 else all_years

    lines = []
    lines.append("## 四、24 行 Statistical Array")
    lines.append("")
    lines.append("> **阅读提示**: 左 = 历史数据，粗体 = VL 估计/预测。从左→右读：先看历史趋势，再对比预测。")
    lines.append("")

    # ---- Group 1: 每股指标 #1-#6 ----
    group1_fields = ["PER_OI", "PER_NETCASH", "BASIC_EPS", "DPS", "CAPEX_PS", "BPS"]
    lines.append("### 📊 每股指标 #1-#6")
    lines.append("")
    lines += _render_metric_group(metrics_map, group1_fields, display_years, 1)

    # 诊断窗 #1-#6
    lines.append("> 🔍 **诊断窗 #1-#6**")
    lines.append(">")

    per_cf = ly.get("PER_NETCASH")
    eps = ly.get("BASIC_EPS")
    per_capex = ly.get("CAPEX_PS") or 0
    depr = ly.get("DEPRECIATION") or 0
    total_shares = ly.get("TOTAL_SHARES")
    bps = ly.get("BPS")
    bps_vals = [metrics.get(y, {}).get("BPS") for y in all_years]
    bps_vals = [v for v in bps_vals if v is not None]

    if per_cf and eps:
        gap = per_cf - eps
        # depr 是亿，total_shares 是百万股，每股折旧 = depr * 100 / shares
        depr_ps = round(depr * 100 / total_shares, 2) if total_shares else 0
        lines.append(f"> - 每股现金流/每股收益 = {per_cf/eps:.2f}x（差值 ¥{gap:.2f} ≈ 折旧 ¥{depr_ps:.2f}）→ {'轻资产，现金流质量高 ✅' if gap < eps*0.5 else '重资产，资本密集度高'}")
    if per_capex and depr and total_shares:
        depr_ps = round(depr / (total_shares or 1), 2)
        capex_depr = per_capex / depr_ps if depr_ps > 0 else None
        if capex_depr:
            label = "高速扩张" if capex_depr > 1.5 else ("稳健增长" if capex_depr > 0.8 else "维持型")
            lines.append(f"> - CAPEX/折旧 = {per_capex:.2f}/{depr_ps:.2f} = {capex_depr:.1f}x → {label}")
    if len(bps_vals) >= 3:
        bps_cagr = round((pow(bps_vals[-1] / bps_vals[0], 1/(len(bps_vals)-1)) - 1) * 100, 1) if bps_vals[0] > 0 else None
        if bps_cagr:
            lines.append(f"> - 每股账面价值 {len(bps_vals)-1}年 CAGR = {bps_cagr:+.1f}% → {'内在价值复利快 ✅' if bps_cagr > 10 else '增长一般'}")

    lines.append("")

    # ---- Group 2: 股本与估值 #7-#10 ----
    group2_fields = ["TOTAL_SHARES", "PE_AVG", "PE_RELATIVE", "DIV_YIELD"]
    lines.append("### 📈 股本与历史估值 #7-#10")
    lines.append("")
    lines += _render_metric_group(metrics_map, group2_fields, display_years, 7)

    # 诊断窗 #7-#10
    lines.append("> 🔍 **诊断窗 #7-#10**")
    lines.append(">")
    shares_vals = [metrics.get(y, {}).get("TOTAL_SHARES") for y in all_years]
    shares_vals = [v for v in shares_vals if v is not None]
    pe_avg_vals = [metrics.get(y, {}).get("PE_AVG") for y in all_years]
    pe_avg_vals = [v for v in pe_avg_vals if v is not None]
    pe_rel_vals = [metrics.get(y, {}).get("PE_RELATIVE") for y in all_years]
    pe_rel_vals = [v for v in pe_rel_vals if v is not None]

    if len(shares_vals) >= 2:
        dir_text = "回购中（对每股指标正面）" if shares_vals[-1] < shares_vals[0] else "增发/摊薄中"
        lines.append(f"> - #7 股数: {shares_vals[0]:.0f}M → {shares_vals[-1]:.0f}M → {dir_text}")
    if len(pe_avg_vals) >= 3:
        trend_text = "估值回归" if pe_avg_vals[-1] < pe_avg_vals[0] else "估值扩张"
        lines.append(f"> - #8 PE 中枢趋势: {pe_avg_vals[0]:.0f}x → {pe_avg_vals[-1]:.0f}x → {trend_text}")
    spot_pe = data.get("spot", {}).get("pe")
    if spot_pe and len(pe_avg_vals) >= 2:
        median_pe = sorted(pe_avg_vals)[len(pe_avg_vals)//2] if pe_avg_vals else None
        if median_pe:
            vs = "低于" if spot_pe < median_pe else "高于"
            lines.append(f"> - 当前 PE {spot_pe:.1f}x {vs} 历史中位数 {median_pe:.0f}x")

    lines.append("")

    # ---- Group 3: 利润表 #11-#17 ----
    group3_fields = ["OPERATE_INCOME", "GROSS_MARGIN", "OP_MARGIN", "DEPRECIATION", "HOLDER_PROFIT", "TAX_EBT", "NET_PROFIT_RATIO"]
    lines.append("### 📊 利润表指标 #11-#17")
    lines.append("")
    lines += _render_metric_group(metrics_map, group3_fields, display_years, 11)

    # 诊断窗 #11-#17: 三层利润率裂缝
    lines.append("> 🔍 **诊断窗 #11-#17: 三层利润率裂缝分析**")
    lines.append(">")
    gm_now = ly.get("GROSS_MARGIN")
    opm_now = ly.get("OP_MARGIN")
    npm_now = ly.get("NET_PROFIT_RATIO")
    gm_py = py.get("GROSS_MARGIN")
    opm_py = py.get("OP_MARGIN")
    npm_py = py.get("NET_PROFIT_RATIO")

    if gm_now and opm_now and npm_now:
        crack1 = gm_now - opm_now
        crack2 = opm_now - npm_now
        lines.append(f"> ```")
        lines.append(f"> 裂缝1: 毛利率 {gm_now:.1f}% - 营业利润率 {opm_now:.1f}% = {crack1:.1f}pp (SG&A 费用)")
        lines.append(f"> 裂缝2: 营业利润率 {opm_now:.1f}% - 净利润率 {npm_now:.1f}% = {crack2:.1f}pp (折旧+利息+税)")
        lines.append(f"> ```")
        if gm_py and opm_py:
            crack1_prev = gm_py - opm_py
            c1_trend = "缩小（规模效应发挥 ✅）" if crack1 < crack1_prev else "扩大（费用侵蚀利润 ⚠️）"
            lines.append(f"> 裂缝1 趋势: {crack1_prev:.1f}pp → {crack1:.1f}pp — {c1_trend}")
        lines.append(f"> 利润质量: {'高毛利 + 高经营利润率 → 强定价权 ✅' if gm_now > 50 and opm_now > 20 else '一般'}")

    lines.append("")

    # ---- Group 4: 资产负债 #18-#20 ----
    group4_fields = ["WORKING_CAPITAL", "LT_DEBT", "TOTAL_EQUITY"]
    lines.append("### 📊 资产负债指标 #18-#20")
    lines.append("")
    lines += _render_metric_group(metrics_map, group4_fields, display_years, 18)

    # 诊断窗 #18-#20
    lines.append("> 🔍 **诊断窗 #18-#20**")
    lines.append(">")
    wc = ly.get("WORKING_CAPITAL")
    lt_debt = ly.get("LT_DEBT") or 0
    total_eq = ly.get("TOTAL_EQUITY") or 1
    rev = ly.get("OPERATE_INCOME")

    if wc is not None and rev:
        wc_sign = "正" if wc > 0 else "负"
        rev_growing = rev > (py.get("OPERATE_INCOME") or 0)
        if wc > 0 and rev_growing:
            wc_diag = "扩张中需更多运营资金（正常）"
        elif wc > 0 and not rev_growing:
            wc_diag = "库存积压/应收账款回收困难（警惕 ⚠️）"
        elif wc < 0 and rev_growing:
            wc_diag = "快收慢付模式，竞争优势 ✅"
        else:
            wc_diag = "流动性可能断裂（危险 ⚠️）"
        lines.append(f"> - #18 营运资金 {wc:.0f}亿 (净{wc_sign}) + 营收 {'增长' if rev_growing else '下降'} → {wc_diag}")
    if lt_debt == 0:
        lines.append(f"> - #19 长期债务 = 0 → 零杠杆，ROE 全部来自经营效率 ✅")
    else:
        d2e = lt_debt / total_eq * 100
        lines.append(f"> - #19 长期债务 {lt_debt:.1f}亿，负债权益比 {d2e:.0f}%")
    eq_vals = [metrics.get(y, {}).get("TOTAL_EQUITY") for y in all_years]
    eq_vals = [v for v in eq_vals if v is not None]
    if len(eq_vals) >= 3:
        eq_cagr = round((pow(eq_vals[-1] / eq_vals[0], 1/(len(eq_vals)-1)) - 1) * 100, 1) if eq_vals[0] > 0 else None
        if eq_cagr:
            lines.append(f"> - #20 股东权益 {len(eq_vals)-1}年 CAGR = {eq_cagr:+.1f}%")

    lines.append("")

    # ---- Group 5: 回报率 #21-#24 ----
    group5_fields = ["ROIC", "ROE", "RETAINED_RATIO", "PAYOUT_RATIO"]
    lines.append("### 📊 回报率指标 #21-#24")
    lines.append("")
    lines += _render_metric_group(metrics_map, group5_fields, display_years, 21)

    # 诊断窗 #21-#24: 质量评分
    lines.append("> 🔍 **诊断窗 #21-#24: 资本配置质量评分**")
    lines.append(">")
    roce = ly.get("ROIC")
    roe = ly.get("ROE")
    retained = ly.get("RETAINED_RATIO")
    payout = ly.get("PAYOUT_RATIO")

    if roce and roe:
        gap = roe - roce
        if gap > 10:
            gap_diag = "差值大 → 高杠杆驱动回报，关注债务风险"
        elif gap > 0:
            gap_diag = "差值小 → 经营效率主导，质量高 ✅"
        else:
            gap_diag = "ROIC > ROE（正常，零杠杆企业 ROE 低于 ROIC 因税款扣减）"
        lines.append(f"> - ROIC {roce:.1f}% vs ROE {roe:.1f}% (差值 {gap:.1f}pp) → {gap_diag}")

    if retained is not None and roe:
        if roe > 20 and retained > 20:
            quadrant = "✅ 复利机器（留存每元产生高回报）"
        elif roe > 10 and retained > 10:
            quadrant = "🟡 稳健增长（留存回报中等）"
        elif retained > 10:
            quadrant = "❌ 价值毁灭（留存回报低，不如分给股东）"
        else:
            quadrant = "💰 现金牛（高分红，适合收息）"
        lines.append(f"> - 留存率 {retained:.1f}% + ROE {roe:.1f}% → {quadrant}")

    if payout is not None:
        if payout < 30:
            lines.append(f"> - 支付率 {payout:.1f}% < 30% → 安全区间 ✅")
        elif payout < 60:
            lines.append(f"> - 支付率 {payout:.1f}% → 典型成熟公司区间")
        elif payout < 80:
            lines.append(f"> - 支付率 {payout:.1f}% → 分红激进 ⚠️")
        else:
            lines.append(f"> - 支付率 {payout:.1f}% > 80% → 不可持续概率大 🔴")

    lines.append("")
    lines.append("---")
    lines.append("")
    return "\n".join(lines)


def _render_metric_group(metrics_map, fields, display_years, start_order):
    """渲染一组指标表格"""
    lines = []

    # 表头
    years_header = " | ".join([f" {y} " for y in display_years])
    lines.append(f"| # | 指标 | {years_header} | 趋势 |")
    sep = "|---|------" + "|------" * len(display_years) + "|:--:|"
    lines.append(sep)

    for field in fields:
        if field not in metrics_map:
            continue
        info = metrics_map[field]
        name = info["name_cn"]
        unit = info["unit"]
        values = info["values"]
        order = info["order"]

        # 格式化值
        yr_strs = []
        for y in display_years:
            v = values.get(y)
            if v is None:
                yr_strs.append(" - ")
            elif unit == "%":
                yr_strs.append(f" {_fmt_pct(v, 1)} ")
            elif unit in ("亿",):
                yr_strs.append(f" {_fmt(v, '', 1)} ")
            elif unit == "百万股":
                yr_strs.append(f" {_fmt(v, '', 0)} ")
            else:
                yr_strs.append(f" {_fmt(v, '', 2)} ")

        # 趋势
        vals_list = [values.get(y) for y in display_years if values.get(y) is not None]
        if len(vals_list) >= 2:
            arrow = _arrow(vals_list[-1] - vals_list[0])
        else:
            arrow = "➡️"

        lines.append(f"| {order} | **{name}** |{'|'.join(yr_strs)}| {arrow} |")

    lines.append("")
    return lines


# ============================================================
# 模块五: 资本结构与流动性
# ============================================================

def _render_financial_health(data):
    """资本结构 + 流动性"""
    cap_struct = data.get("capital_structure", {})
    cur_pos = data.get("current_position", {})
    years = data.get("years", [])
    spot = data.get("spot", {})
    meta = data.get("meta", {})

    if not cap_struct and not cur_pos:
        return ""

    lines = []
    lines.append("## 五、资本结构与流动性")
    lines.append("")

    # ---- Capital Structure ----
    if cap_struct:
        cs_unit = cap_struct.get("unit", "亿")
        cs_total_debt = cap_struct.get("total_debt", 0)
        cs_lt_debt = cap_struct.get("lt_debt", 0)
        cs_total_int = cap_struct.get("total_int", 0)
        cs_coverage = cap_struct.get("coverage", "NMF")
        cs_lt_debt_pct = cap_struct.get("lt_debt_pct", 0)
        cs_common_shares = cap_struct.get("common_shares_str", "N/A")
        cs_mkt_cap = cap_struct.get("mkt_cap", 0)
        cs_cap_label = cap_struct.get("cap_label", "")
        cs_total_equity = cap_struct.get("total_equity", 0)

        lines.append("### 资本结构")
        lines.append("")
        lines.append(f"| 项目 | 金额 |")
        lines.append("|------|------|")
        lines.append(f"| 总债务 (Total Debt) | {cs_total_debt:.1f} {cs_unit} |")
        lines.append(f"| 长期债务 (LT Debt) | {cs_lt_debt:.1f} {cs_unit} |")
        lines.append(f"| 长期利息 (LT Interest) | {cs_total_int:.2f} {cs_unit} |")
        lines.append(f"| **利息覆盖倍数** | **{cs_coverage}** |")
        lines.append(f"| 长期债务/总资本 | {cs_lt_debt_pct:.1f}% |")
        lines.append(f"| 股东权益 | {cs_total_equity:.1f} {cs_unit} |")
        lines.append(f"| 普通股 | {cs_common_shares} 股 |")
        lines.append(f"| **总市值** | **{cs_mkt_cap:.0f} {cs_unit}** ({cs_cap_label}) |")
        lines.append("")

        # 负债率判断
        if cs_total_equity > 0:
            debt_ratio = cs_total_debt / (cs_total_debt + cs_total_equity) * 100
            if debt_ratio < 20:
                lines.append(f"> 资产负债率 {debt_ratio:.0f}% — 极端保守 ✅")
            elif debt_ratio < 50:
                lines.append(f"> 资产负债率 {debt_ratio:.0f}% — 健康水平")
            else:
                lines.append(f"> 资产负债率 {debt_ratio:.0f}% — 偏高 ⚠️")
        lines.append("")

    # ---- Current Position ----
    if cur_pos:
        cp_years = cur_pos.get("years", [])
        cp_items = cur_pos.get("items", [])

        if cp_years and cp_items:
            lines.append("### 短期流动性（3 年对比）")
            lines.append("")
            lines.append("| 项目 | " + " | ".join([f" {y} " for y in cp_years]) + " |")
            lines.append("|------|" + "------|" * len(cp_years))

            # 资产端
            for idx, label in [(0, "现金及等价物"), (1, "应收帐款"), (2, "存货"), (3, "其他流动资产")]:
                item = cp_items[idx] if idx < len(cp_items) else {}
                vals = [f" {item.get(y, 0):.1f} 亿" for y in cp_years]
                lines.append(f"| {label} |" + "|".join(vals) + "|")

            # Current Assets
            item_ca = cp_items[4] if 4 < len(cp_items) else {}
            vals = [f" **{item_ca.get(y, 0):.1f} 亿**" for y in cp_years]
            lines.append(f"| **流动资产合计** |" + "|".join(vals) + "|")

            # 负债端
            for idx, label in [(5, "应付帐款"), (6, "到期债务"), (7, "其他流动负债")]:
                item = cp_items[idx] if idx < len(cp_items) else {}
                vals = [f" {item.get(y, 0):.1f} 亿" for y in cp_years]
                lines.append(f"| {label} |" + "|".join(vals) + "|")

            # Current Liabilities
            item_cl = cp_items[8] if 8 < len(cp_items) else {}
            vals = [f" **{item_cl.get(y, 0):.1f} 亿**" for y in cp_years]
            lines.append(f"| **流动负债合计** |" + "|".join(vals) + "|")

            lines.append("")

            # 比率
            lines.append("| 比率 | " + " | ".join([f" {y} " for y in cp_years]) + " |")
            lines.append("|------|" + "------|" * len(cp_years))
            ratios = []
            for y in cp_years:
                ca = item_ca.get(y, 0)
                cl = item_cl.get(y, 0)
                inv = cp_items[2].get(y, 0) if 2 < len(cp_items) else 0
                current_ratio = round(ca / cl, 2) if cl > 0 else 0
                cash = cp_items[0].get(y, 0) if 0 < len(cp_items) else 0
                recv = cp_items[1].get(y, 0) if 1 < len(cp_items) else 0
                quick = round((cash + recv) / cl, 2) if cl > 0 else 0
                ratios.append((current_ratio, quick))

            cr_vals = [f" {r[0]:.2f}x" for r in ratios]
            lines.append(f"| 流动比率 |" + "|".join(cr_vals) + "|")
            qr_vals = [f" {r[1]:.2f}x" for r in ratios]
            lines.append(f"| 速动比率 |" + "|".join(qr_vals) + "|")
            lines.append("")

    lines.append("---")
    lines.append("")
    return "\n".join(lines)


# ============================================================
# 模块六: 价格图与市场表现
# ============================================================

def _render_price_history(data):
    """股价历史 + 估值区间 (含价格图三条线解读)"""
    yearly_hl = data.get("yearly_hl", [])
    position = data.get("position", {})
    spot = data.get("spot", {})
    returns = data.get("total_returns", {})
    meta = data.get("meta", {})
    valuation_line = data.get("valuation_line", [])
    val_method = data.get("valuation_method", "cf")
    cf_mult = data.get("cf_multiplier", 15)
    pb_mult = data.get("pb_multiplier", 1)

    if not yearly_hl:
        return ""

    lines = []
    lines.append("## 六、价格图解读与市场表现")
    lines.append("")

    # 估值线说明
    if val_method == "pb":
        val_label = f"PB 基准线 = {pb_mult:.2f} × 每股账面价值"
    else:
        val_label = f"现金流基准线 = {cf_mult:.1f} × 每股现金流"

    price = spot.get("price", 0) or 0
    val_line_last = valuation_line[-1].get("value") if valuation_line else None

    lines.append("### 价格图三线解读")
    lines.append("")
    lines.append("| 线条 | 含义 | 当前状态 |")
    lines.append("|------|------|----------|")
    lines.append(f"| **月K线** | 股价月度高低范围 | 当前 {_fmt(price, ' ' + meta.get('price_ccy', 'HKD'))} |")
    lines.append(f"| **估值基准线 (实线)** | {val_label} | {_fmt(val_line_last)} |")

    if price and val_line_last and val_line_last > 0:
        vs = "低于" if price < val_line_last else "高于"
        lines.append(f"| → | VL 经典规律：股价倾向于回归基准线 | 当前 {vs}基准线 |")
    lines.append(f"| **相对价格强度线 (虚线)** | 个股 vs 市场指数的相对强度 | 近一年表现 |")
    lines.append("")

    # 年度高低表
    lines.append("### 年度股价区间")
    lines.append("")
    ccy = meta.get("price_ccy", "HKD")
    lines.append("| 年份 | 最高 | 最低 | 波动幅度 |")
    lines.append("|------|------|------|----------|")

    for hl in yearly_hl[-10:]:
        year = hl["year"]
        high = hl["high"]
        low = hl["low"]
        spread = high - low
        spread_pct = round(spread / low * 100, 0) if low > 0 else 0
        lines.append(f"| {year} | {_fmt(high, ' ' + ccy)} | {_fmt(low, ' ' + ccy)} | {_fmt(spread, ' ' + ccy)} ({spread_pct:.0f}%) |")
    lines.append("")

    # 回报率 vs 指数
    stock_ret = returns.get("stock", {})
    index_ret = returns.get("index", {})
    index_name = meta.get("index_name_cn", "指数")

    if stock_ret or index_ret:
        lines.append("### 历史回报率 vs 指数")
        lines.append("")
        lines.append(f"| 周期 | 个股回报 | {index_name}回报 | 超额 |")
        lines.append("|------|----------|----------|------|")
        for period in ["1yr", "3yr", "5yr"]:
            s = stock_ret.get(period)
            i = index_ret.get(period)
            excess = round(s - i, 1) if s is not None and i is not None else None
            lines.append(f"| {period} | {_fmt_pct(s, 1)} | {_fmt_pct(i, 1)} | {_fmt_sign_pct(excess, 1)} |")
        lines.append("")

    # 估值区间
    pe_pos = position.get("pe", {})
    pb_pos = position.get("pb", {})

    if pe_pos or pb_pos:
        lines.append("### 估值区间")
        lines.append("")
        lines.append("| 估值指标 | 当前 | 最低 | 最高 | 中位数 | 百分位 |")
        lines.append("|----------|------|------|------|--------|--------|")
        if pe_pos:
            median_pe = spot.get("median_pe")
            lines.append(f"| **PE** | {_fmt(pe_pos.get('current'), 'x')} | {_fmt(pe_pos.get('min'), 'x')} | {_fmt(pe_pos.get('max'), 'x')} | {_fmt(median_pe, 'x')} | {_fmt_pct(pe_pos.get('pct'), 0)} |")
        if pb_pos:
            lines.append(f"| **PB** | {_fmt(pb_pos.get('current'), 'x')} | {_fmt(pb_pos.get('min'), 'x')} | {_fmt(pb_pos.get('max'), 'x')} | {_fmt(pb_pos.get('avg'), 'x')} | {_fmt_pct(pb_pos.get('pct'), 0)} |")
        lines.append("")

    lines.append("---")
    lines.append("")
    return "\n".join(lines)


# ============================================================
# 模块七: CAGR + 季度数据趋势
# ============================================================

def _render_growth(data):
    """CAGR 增长率 + 季度数据"""
    cagr = data.get("cagr", {})
    quarterly = data.get("quarterly", {})
    annual_rates = data.get("annual_rates", {})

    lines = []
    lines.append("## 七、增长率与季度趋势")
    lines.append("")

    # CAGR
    lines.append("### CAGR 复合增长率（每股）")
    lines.append("")
    lines.append("| 指标 | 1年 | 3年 | 5年 |")
    lines.append("|------|-----|-----|-----|")
    cagr_items = [
        ("每股营收", cagr.get("revenue", {})),
        ("每股收益", cagr.get("eps", {})),
        ("每股现金流", cagr.get("cashflow", {})),
        ("每股股息", cagr.get("dividend", {})),
        ("每股账面价值", cagr.get("equity", {})),
    ]
    for label, c in cagr_items:
        lines.append(f"| {label} | {_fmt_sign_pct(c.get('1yr'), 1)} | {_fmt_sign_pct(c.get('3yr'), 1)} | {_fmt_sign_pct(c.get('5yr'), 1)} |")
    lines.append("")

    # Annual Rates (如果有 10 年数据)
    ar = annual_rates
    if ar and ar.get("has_10yr"):
        lines.append("### 长期历史增长率 (ANNUAL RATES)")
        lines.append("")
        cols = ["10年", "5年", "3年", "1年"] if ar.get("has_10yr") else ["5年", "3年", "1年"]
        lines.append("| 指标 | " + " | ".join(cols) + " |")
        lines.append("|------|" + "|".join(["-----"] * len(cols)) + "|")
        for label, key in [("营收", "sales"), ("现金流", "cashflow"), ("收益", "earnings"), ("股息", "dividends"), ("账面价值", "book_value")]:
            d = ar.get(key, {})
            vals = []
            for c in cols:
                k = c.replace("年", "yr")
                v = d.get(k)
                vals.append(f" {v:+.1f}%" if v is not None else " - ")
            lines.append(f"| {label} |" + "|".join(vals) + "|")
        lines.append("")

    # 季度数据
    qt_sales = quarterly.get("sales", [])
    qt_eps = quarterly.get("eps", [])

    if qt_sales:
        lines.append("### 季度营收趋势（近 5 年）")
        lines.append("")
        has_q = qt_sales[0].get("has_quarter", False) if qt_sales else False
        if has_q:
            lines.append("| 年份 | Q1 | Q2 | Q3 | Q4 | 全年 |")
            lines.append("|------|-----|-----|-----|-----|------|")
        else:
            lines.append("| 年份 | H1 | H2 | 全年 |")
            lines.append("|------|-----|-----|------|")

        for s in qt_sales[-5:]:
            yr = s.get("year", "")
            if has_q:
                lines.append(f"| {yr} | {_fmt(s.get('q1'), '亿')} | {_fmt(s.get('q2'), '亿')} | {_fmt(s.get('q3'), '亿')} | {_fmt(s.get('q4'), '亿')} | {_fmt(s.get('full'), '亿')} |")
            else:
                lines.append(f"| {yr} | {_fmt(s.get('q1'), '亿')} | {_fmt(s.get('q3'), '亿')} | {_fmt(s.get('full'), '亿')} |")
        lines.append("")
        if not has_q:
            lines.append("> *港股仅披露半年报（H1/H2）*")
            lines.append("")

    if qt_eps:
        lines.append("### 季度/半年 EPS 趋势")
        lines.append("")
        has_q = qt_eps[0].get("has_quarter", False) if qt_eps else False
        if has_q:
            lines.append("| 年份 | Q1 | Q2 | Q3 | Q4 | 全年 |")
            lines.append("|------|-----|-----|-----|-----|------|")
        else:
            lines.append("| 年份 | H1 | H2 | 全年 |")
            lines.append("|------|-----|-----|------|")
        for e in qt_eps[-5:]:
            yr = e.get("year", "")
            if has_q:
                lines.append(f"| {yr} | {_fmt(e.get('q1'), '', 2)} | {_fmt(e.get('q2'), '', 2)} | {_fmt(e.get('q3'), '', 2)} | {_fmt(e.get('q4'), '', 2)} | {_fmt(e.get('full'), '', 2)} |")
            else:
                lines.append(f"| {yr} | {_fmt(e.get('q1'), '', 2)} | {_fmt(e.get('q3'), '', 2)} | {_fmt(e.get('full'), '', 2)} |")
        lines.append("")

    lines.append("---")
    lines.append("")
    return "\n".join(lines)


# ============================================================
# 模块八: 投资检查清单 + 总结
# ============================================================

def _render_checklist(data):
    """李录 5 问 + VL 综合信号 + 关键验证节点"""
    metrics = data.get("data", {})
    years = data.get("years", [])
    spot = data.get("spot", {})
    cagr = data.get("cagr", {})
    position = data.get("position", {})
    ratings = _compute_ratings(data)

    if not years:
        return "## 八、总结\n\n（数据不足）\n"

    latest_yr = years[-1]
    ly = metrics.get(latest_yr, {})

    lines = []
    lines.append("## 八、投资检查清单与总结")
    lines.append("")

    # 李录 5 问
    pe = spot.get("pe", 0) or 0
    median_pe = spot.get("median_pe")
    pb = spot.get("pb", 0) or 0
    bps = ly.get("BPS")
    roce = ly.get("ROIC")
    roe = ly.get("ROE")
    lt_debt = ly.get("LT_DEBT") or 0
    rev_1yr = cagr.get("revenue", {}).get("1yr")
    pe_pct = position.get("pe", {}).get("pct")

    # Q1: 便宜吗?
    q1 = "🟡 合理偏低" if pe_pct is not None and pe_pct < 30 else ("🟢 便宜" if pe_pct is not None and pe_pct < 15 else "🟡 合理")
    q1_detail = f"PE {pe:.1f}x"
    if pe_pct is not None: q1_detail += f"，历史百分位 {pe_pct:.0f}%"
    if pb: q1_detail += f"，PB {pb:.1f}x"

    # Q2: 生意好吗?
    q2 = "🟢 很好" if roce and roce > 20 else ("🟡 还行" if roce and roce > 10 else "🔴 一般")
    q2_detail = f"ROIC {roce:.1f}%" if roce else ""
    if roe: q2_detail += f"，ROE {roe:.1f}%"
    if lt_debt == 0: q2_detail += "，零杠杆"

    # Q3: 管理层靠谱吗?
    q3 = "🟡 需验证"
    q3_detail = "待评估（持股比例、历史执行记录）"

    # Q4: 漏掉什么?
    q4 = "🟡 关注风险"
    q4_detail = "检查隐藏债务、关联交易、大额担保"

    # Q5: 为什么便宜?
    q5 = "🟡 理解中"
    q5_detail = f"1yr 增速 {rev_1yr:+.1f}%" if rev_1yr else "待分析"
    if rev_1yr and rev_1yr > 50:
        q5_detail += " — 市场可能担心高增速不可持续"

    lines.append("### 李录式 5 问检查")
    lines.append("")
    lines.append("| # | 问题 | 判断 | 依据 |")
    lines.append("|---|------|------|------|")
    lines.append(f"| 1 | **便宜吗？** | {q1} | {q1_detail} |")
    lines.append(f"| 2 | **生意好吗？** | {q2} | {q2_detail} |")
    lines.append(f"| 3 | **管理层靠谱吗？** | {q3} | {q3_detail} |")
    lines.append(f"| 4 | **漏掉了什么？** | {q4} | {q4_detail} |")
    lines.append(f"| 5 | **为什么便宜？** | {q5} | {q5_detail} |")
    lines.append("")

    # VL 综合信号
    lines.append("### VL 综合信号汇总")
    lines.append("")

    positive = []
    neutral = []
    negative = []

    t = ratings["timeliness"]
    s = ratings["safety"]
    if t <= 2: positive.append(f"Timeliness 排名 {t} — 预期跑赢多数股票")
    elif t == 3: neutral.append(f"Timeliness 排名 {t} — 中性")
    else: negative.append(f"Timeliness 排名 {t} — 预期跑输")

    if s <= 2: positive.append(f"Safety 排名 {s} — 财务稳健")
    elif s == 3: neutral.append(f"Safety 排名 {s} — 中等风险")
    else: negative.append(f"Safety 排名 {s} — 高风险")

    if roce and roce > 20: positive.append(f"ROIC {roce:.1f}% — 高质量资本回报")
    if lt_debt == 0: positive.append("零长期负债")
    if pe_pct is not None and pe_pct < 30: positive.append(f"PE 估值处历史低区 ({pe_pct:.0f}%)")
    if rev_1yr and rev_1yr > 50: neutral.append(f"营收增速极高 ({rev_1yr:+.1f}%)，市场担心持续性")
    if rev_1yr and rev_1yr < 0: negative.append(f"营收增速为负 ({rev_1yr:+.1f}%)")

    lines.append("| 信号类型 | 信号 |")
    lines.append("|----------|------|")
    for sig in positive:
        lines.append(f"| 🟢 积极 | {sig} |")
    for sig in neutral:
        lines.append(f"| 🟡 中性 | {sig} |")
    for sig in negative:
        lines.append(f"| 🔴 警惕 | {sig} |")
    lines.append("")

    # 关键验证节点
    lines.append("### 关键验证节点")
    lines.append("")
    lines.append(f"1. **{int(latest_yr)+1} 年中报**：营收增速是否保持？利润率趋势如何？")
    lines.append(f"2. **{int(latest_yr)+1} 年报**：全年业绩能否验证中报趋势？")
    lines.append(f"3. **行业动态**：关注竞争格局、监管变化、技术迭代等外部因素")
    lines.append("")

    # 免责声明
    lines.append("---")
    lines.append("")
    lines.append("*本报告基于截至最新财年的公开财务数据，通过 Value Line 标准化框架生成。*")
    lines.append("*Timeliness / Safety 评分为算法自动计算，仅供参考。*")
    lines.append("*不构成投资建议。投资有风险，决策需谨慎。*")
    lines.append("")

    return "\n".join(lines)


# ============================================================
# 主入口
# ============================================================

def build_reading_report(data):
    """按 VL 阅读指南生成完整 Markdown 报告"""
    meta = data["meta"]
    spot = data["spot"]

    title = f"# {meta['name']} ({meta['code']}) — Value Line 阅读报告"
    subtitle = (f"> 生成日: {meta.get('generated','')[:10]} | "
                f"股价: {_fmt(spot.get('price'), ' ' + meta.get('price_ccy', 'HKD'))} | "
                f"PE(TTM): {_fmt(spot.get('pe'), 'x')} | "
                f"总市值: {_fmt(spot.get('mkt_cap'), ' 亿')}")

    sections = [
        title, "", subtitle, "",
        "---", "",
        _render_quick_screen(data),     # 前置: 李录式 30 秒
        _render_business(data),         # 一: Business
        "---", "",
        _render_ratings(data),          # 二: Timeliness & Safety
        _render_commentary(data),       # 三: AI Commentary 5 段
        _render_stat_array(data),       # 四: 24 行 Statistical Array
        _render_financial_health(data), # 五: 资本结构与流动性
        _render_price_history(data),    # 六: 价格图与市场表现
        _render_growth(data),           # 七: CAGR + 季度数据
        _render_checklist(data),        # 八: 投资检查清单 + 总结
    ]

    return "\n".join(sections)


def build_reading_html(md_text, data):
    """将 Markdown 包装为独立 HTML"""
    meta = data["meta"]
    name = meta["name"]
    code = meta["code"]
    html_body = _md_to_html(md_text)

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{name} ({code}) — VL 阅读报告</title>
<style>
  :root {{
    --bg: #fafbfc; --text: #1a1a2e; --muted: #6c757d;
    --border: #e1e4e8; --code-bg: #f6f8fa; --link: #2563eb;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Noto Sans SC", sans-serif;
    background: var(--bg); color: var(--text); line-height: 1.75;
    -webkit-font-smoothing: antialiased;
  }}
  .container {{ max-width: 860px; margin: 0 auto; padding: 32px 20px 80px; }}
  h1 {{ font-size: 26px; font-weight: 700; margin: 24px 0 8px; letter-spacing: -0.5px; }}
  h2 {{ font-size: 20px; font-weight: 600; margin: 40px 0 12px; padding-bottom: 6px; border-bottom: 2px solid var(--border); }}
  h3 {{ font-size: 16px; font-weight: 600; margin: 24px 0 8px; }}
  h4 {{ font-size: 14px; font-weight: 600; margin: 20px 0 6px; }}
  p, blockquote {{ margin: 8px 0; }}
  blockquote {{ border-left: 3px solid #2563eb; padding: 8px 16px; color: var(--muted); background: #f0f4ff; border-radius: 0 6px 6px 0; }}
  table {{ width: 100%; border-collapse: collapse; margin: 12px 0; font-size: 13px; }}
  th, td {{ padding: 6px 10px; border: 1px solid var(--border); text-align: left; }}
  th {{ background: var(--code-bg); font-weight: 600; }}
  tr:nth-child(even) {{ background: #fafbfc; }}
  a {{ color: var(--link); text-decoration: none; }}
  a:hover {{ text-decoration: underline; }}
  hr {{ border: none; border-top: 1px solid var(--border); margin: 32px 0; }}
  .subtitle {{ color: var(--muted); font-size: 14px; margin: 4px 0 16px; }}
  code {{ font-family: "SF Mono", "Fira Code", monospace; font-size: 12px; background: var(--code-bg); padding: 2px 6px; border-radius: 4px; }}
  footer {{ text-align: center; margin-top: 48px; padding: 24px 0; color: var(--muted); font-size: 12px; border-top: 1px solid var(--border); }}
  @media (max-width: 640px) {{
    .container {{ padding: 16px 12px 60px; }}
    h1 {{ font-size: 22px; }}
    table {{ font-size: 11px; }}
    th, td {{ padding: 4px 6px; }}
  }}
</style>
</head>
<body>
<div class="container">
{html_body}
  <footer>Value Line Research · 不构成投资建议</footer>
</div>
</body>
</html>"""


def _md_to_html(md_text):
    """Markdown → HTML 转换"""
    import re
    lines = md_text.split("\n")
    out = []
    in_table = False
    in_code = False
    i = 0

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # 代码块
        if stripped.startswith("```"):
            if in_code:
                out.append('</code></pre>')
                in_code = False
            else:
                out.append('<pre><code>')
                in_code = True
            i += 1
            continue
        if in_code:
            out.append(line)
            i += 1
            continue

        # 表格
        if stripped.startswith("|") and stripped.endswith("|"):
            if not in_table:
                out.append('<table>')
                in_table = True
            cells = [c.strip() for c in stripped[1:-1].split("|")]
            if all(re.match(r'^[-:]+$', c) for c in cells):
                i += 1
                continue
            tag = "th" if i + 1 < len(lines) and re.match(r'^[\|\s\-:]+$', lines[i + 1].strip()) else "td"
            out.append('<tr>')
            for c in cells:
                out.append(f'<{tag}>{c}</{tag}>')
            out.append('</tr>')
        else:
            if in_table:
                out.append('</table>')
                in_table = False

            if stripped == "": pass
            elif stripped.startswith("# "): out.append(f'<h1>{stripped[2:]}</h1>')
            elif stripped.startswith("## "): out.append(f'<h2>{stripped[2:]}</h2>')
            elif stripped.startswith("### "): out.append(f'<h3>{stripped[3:]}</h3>')
            elif stripped.startswith("#### "): out.append(f'<h4>{stripped[4:]}</h4>')
            elif stripped.startswith("> "): out.append(f'<blockquote>{stripped[2:]}</blockquote>')
            elif stripped == "---": out.append('<hr>')
            elif stripped.startswith("- "): out.append(f'<p>{stripped}</p>')
            elif stripped and stripped[0].isdigit() and ". " in stripped[:4]:
                out.append(f'<p>{stripped}</p>')
            elif stripped: out.append(f'<p>{stripped}</p>')

        i += 1

    if in_table: out.append('</table>')
    return "\n".join(out)


# ---- CLI ----

def generate_one(code, data_path=None):
    if data_path is None:
        data_path = os.path.join(BASE_DIR, "report_data.json")
    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    report = build_reading_report(data)

    md_path = os.path.join(READING_DIR, f"{code}.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(report)

    html_content = build_reading_html(report, data)
    html_path = os.path.join(READING_DIR, f"{code}.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"[OK] reading reports: {md_path} + {html_path}")
    return md_path


def generate_all():
    import config
    count = 0
    json_path = os.path.join(BASE_DIR, "report_data.json")
    if os.path.exists(json_path):
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        code = data["meta"]["code"]
        generate_one(code)
        count = 1
    print(f"共生成 {count} 份阅读报告")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="VL 阅读报告生成器")
    parser.add_argument("code", nargs="?", default=None, help="股票代码")
    parser.add_argument("--all", action="store_true", help="生成所有标的")
    parser.add_argument("--json", default=None, help="report_data.json 路径")
    args = parser.parse_args()

    if args.all:
        generate_all()
    elif args.code:
        generate_one(args.code, data_path=args.json)
    else:
        json_path = args.json or os.path.join(BASE_DIR, "report_data.json")
        if not os.path.exists(json_path):
            print(f"[ERROR] report_data.json not found, run engine.py first")
            sys.exit(1)
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        code = data["meta"]["code"]
        generate_one(code, data_path=json_path)
