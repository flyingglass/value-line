# -*- coding: utf-8 -*-
"""腾讯控股 00700 — VL 股息解析 (港币→人民币换算)

00700 公告格式:
  "每股派港币5.3元"                          — 普通现金分红
  "每股派港币1元"                             — 整数值股息
  "相当于每股派18.13港元"                     — 特别分派 (如 2022 美团实物分派)
  "每股派港币2.4元 相当于每股派1.92177港元"   — 取所有 HKD 数值求和

通用 fetcher 已做基本解析写入 DB。本脚本从 raw_text 独立重解析，
确保 HKD→CNY 换算控制权归属个股脚本。当通用 fetcher 行为变更时
不受影响。
"""

import os, sqlite3, re


def _read_fx_rate(date_str):
    """读取 HKD/CNY 汇率, 返回 1 HKD = ? CNY, 失败返回 None"""
    fx_db = os.path.join(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))), "data", "fx_rates.db")
    if not os.path.exists(fx_db):
        return None
    try:
        conn = sqlite3.connect(fx_db)
        row = conn.execute(
            "SELECT hkd_cny FROM daily_rates WHERE date=?", (date_str,)
        ).fetchone()
        if not row:
            row = conn.execute(
                "SELECT hkd_cny FROM daily_rates WHERE date<=? "
                "ORDER BY date DESC LIMIT 1", (date_str,)
            ).fetchone()
        conn.close()
        return row[0] / 100.0 if row else None
    except Exception:
        return None


def adjust_dividends(reader, stock_cfg):
    """00700 股息解析: 从 raw_text 重解析 HKD DPS → CNY 换算。

    Args:
        reader: DataReader 实例 (可读 dividend.raw_text)
        stock_cfg: config.STOCKS["00700"]

    Returns:
        {year: dps_cny} 字典, year 为 "2025" 等字符串
    """
    rows = reader.conn.execute(
        "SELECT report_year, cash_dps, raw_text FROM dividend ORDER BY report_year"
    ).fetchall()

    result = {}
    for yr, dps, raw in rows:
        txt = (raw or "").strip()
        if not txt:
            result[yr] = dps or 0
            continue

        # 从原始公告文本提取所有 HKD 数值
        # "每股派港币5.3元" → 5.3
        # "相当于每股派18.13港元" → 18.13
        normal = re.findall(r'每股派(?:港币|港元)?\s*(\d+\.?\d*)', txt)
        special = re.findall(r'相当于每股派(\d+\.?\d*)港元', txt)

        all_hkd = [float(n) for n in normal + special]
        if not all_hkd:
            # 无法从 raw_text 重新解析, 回退到 fetcher 通用结果
            result[yr] = dps or 0
            continue

        hkd_total = sum(all_hkd)

        # HKD → CNY: 00700 报表货币为人民币, 分红公告为港币
        fx = _read_fx_rate(f"{yr}-12-31")
        if fx:
            hkd_total = round(hkd_total * fx, 4)

        result[yr] = hkd_total

    return result
