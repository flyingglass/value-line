# -*- coding: utf-8 -*-
"""泡泡玛特 09992 — VL 经常性净利润口径调整

港股 IFRS 利润表非经常项目排除:

其他收益 (-1.60亿, 2025):
  - 按公允价值计入损益的金融工具变动 (FVTPL)
  - 业务合并重新计量前JV权益收益 (一次性并购会计)
  - 汇兑亏损 + 捐款 + 其他杂项
  → 全部非经营/非经常，VL 排除

其他收入 (+1.50亿, 2025):
  - 政府补贴、授权费等非核心收入
  → 非经营收入，VL 排除

减值及拨备 (+0.12亿, 2025):
  - 贸易应收款 IFRS 9 ECL 减值
  → 经营性费用，VL 保留 (不排除)
"""


def adjust_metrics(reader, rd, np_val, tax_rate, stock_cfg):
    """个股净利润口径调整 — 引擎钩子

    Args:
        reader: 数据库读取器 (DataReader)
        rd:     报告日期 "YYYY-12-31"
        np_val: 归母净利润 (HOLDER_PROFIT)
        tax_rate: 实际税率
        stock_cfg: STOCKS[code] 配置

    Returns:
        (adj_np, footnotes_list)
    """
    footnotes = []
    if np_val is None:
        return None, footnotes

    other_gain = reader.financial_item("income", "其他收益", rd) or 0
    other_income = reader.financial_item("income", "其他收入", rd) or 0

    # NVPL 经常性 NP = 归母 - 其他收益×(1-tax) - 其他收入×(1-tax)
    # 减值及拨备 (贸易应收款 ECL) 属于经营性，不排除
    nonrecur_adj = (other_gain + other_income) * (1 - tax_rate)
    adj_np = np_val - nonrecur_adj

    parts = []
    if abs(other_gain) > 5e6:
        parts.append(
            f"排除其他收益 {other_gain/1e8:+.1f}亿 "
            f"(公允价值变动、汇兑等非经常项目)"
        )
    if abs(other_income) > 5e6:
        parts.append(
            f"排除其他收入 {other_income/1e8:+.1f}亿 "
            f"(政府补贴、授权费等非经营收入)"
        )
    if parts:
        parts.append(
            f"VL经常性净利润 {adj_np/1e8:.1f}亿 "
            f"(较归母{np_val/1e8:.1f}亿)"
        )
        footnotes.append("; ".join(parts))

    return adj_np, footnotes
