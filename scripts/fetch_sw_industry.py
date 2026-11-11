#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""拉取申万 2021 版行业分类原始数据到 data/sw_industry/。

只做数据落地：不改任何现有 DB、报告或 wiki 页面。
官方个股分类表用 6 位分类代码；AKShare 层级表用 801xxx.SI 指数代码，
两套编码不同，本脚本不做任何映射（口径待确认）。

来源：
  - 官方个股分类变动历史（申万宏源研究）
    https://www.swsresearch.com/swindex/pdf/SwClass2021/StockClassifyUse_stock.xls
  - 行业层级表：akshare sw_index_first/second/third_info（乐咕乐股口径，
    层级数与申万官方 2021 版 31/134/346 不一致，仅作参考）
"""

import io
import json
import os
import sys
import time
import urllib3
from datetime import date

import pandas as pd
import requests

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(BASE, "data", "sw_industry")
STAMP = date.today().isoformat()
OFFICIAL_URL = (
    "https://www.swsresearch.com/swindex/pdf/SwClass2021/StockClassifyUse_stock.xls"
)
HEADERS = {"User-Agent": "Mozilla/5.0"}

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def _get(url, tries=3, timeout=90):
    last = None
    for i in range(tries):
        try:
            r = requests.get(url, headers=HEADERS, verify=False, timeout=timeout)
            r.raise_for_status()
            return r.content
        except Exception as e:
            last = e
            print(f"    retry {i + 1}/{tries}: {type(e).__name__}")
            time.sleep(2)
    raise last


def _write_csv(df, name):
    path = os.path.join(OUT_DIR, f"{name}_{STAMP}.csv")
    df.to_csv(path, index=False, encoding="utf-8-sig")
    return path


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    meta = {"fetched": STAMP, "sources": [], "note": "只落地原始数据，未做行业口径映射"}

    # 1. 官方个股行业分类变动历史（原表 + UTF-8 CSV，股票代码保留前导零）
    print("[1/2] 申万宏源官方个股分类表 ...")
    raw = _get(OFFICIAL_URL)
    xls_path = os.path.join(OUT_DIR, f"StockClassifyUse_stock_{STAMP}.xls")
    with open(xls_path, "wb") as f:
        f.write(raw)
    df = pd.read_excel(io.BytesIO(raw), dtype={"股票代码": "str", "行业代码": "str"})
    csv_path = _write_csv(df, "stock_classify_sw2021")
    print(f"    {len(df)} 行 / {df['行业代码'].nunique()} 个行业代码 -> {os.path.basename(xls_path)}")
    meta["sources"].append({
        "name": "申万宏源研究-全部个股行业分类变动历史(2021版)",
        "url": OFFICIAL_URL,
        "files": [os.path.basename(xls_path), os.path.basename(csv_path)],
        "rows": len(df),
        "columns": list(df.columns),
        "industry_code_count": int(df["行业代码"].nunique()),
        "official_levels": "31/134/346（申万官方 2021 版；本表仅给 6 位分类代码，未含代码名称对照表）",
    })

    # 2. AKShare 三层级行业表（乐咕乐股口径，带估值与成份数）
    print("[2/2] AKShare 申万一级/二级/三级行业表 ...")
    import akshare as ak
    for level, fn in (
        ("level1", ak.sw_index_first_info),
        ("level2", ak.sw_index_second_info),
        ("level3", ak.sw_index_third_info),
    ):
        d = None
        last = None
        for attempt in range(3):
            try:
                d = fn()
                break
            except Exception as e:
                last = e
                print(f"    {level}: retry {attempt + 1}/3 {type(e).__name__}")
                time.sleep(2)
        if d is None:
            print(f"    {level}: FAIL {type(last).__name__}: {last}")
            meta["sources"].append({"name": f"AKShare sw_index_{level}_info", "error": str(last)})
            continue
        p = _write_csv(d, f"sw_{level}_legulegu")
        print(f"    {level}: {len(d)} 行 -> {os.path.basename(p)}")
        meta["sources"].append({
            "name": f"AKShare sw_index_{level}_info（乐咕乐股口径）",
            "url": "https://legulegu.com/stockdata/sw-industry-overview#level1",
            "files": [os.path.basename(p)],
            "rows": len(d),
            "columns": list(d.columns),
        })

    # 3. 覆盖率：config 中 105 只标的在官方表里的命中情况（只统计，不写回）
    sys.path.insert(0, os.path.join(BASE, "scripts"))
    import config
    codes = set(df["股票代码"].astype(str))
    coverage = {}
    for market in ("cn", "hk", "us"):
        pool = [c for c, v in config.STOCKS.items() if v.get("market") == market]
        def hit(c):
            for form in (c, c.lstrip("0"), c.zfill(6), c[-5:]):
                if form in codes:
                    return form
            return None
        matched = {c: hit(c) for c in pool if hit(c)}
        coverage[market] = {
            "total": len(pool),
            "matched": matched,
            "missing": [c for c in pool if not hit(c)],
        }
        print(f"    {market}: {len(matched)}/{len(pool)} 字符串命中")
    meta["coverage"] = coverage
    meta["coverage_note"] = (
        "仅按代码字符串匹配；非 A 股命中可能是港股 5 位代码与 A 股 6 位代码的碰撞，"
        "不代表申万实际覆盖，需逐只核实"
    )

    meta_path = os.path.join(OUT_DIR, f"_meta_{STAMP}.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    print(f"[OK] {OUT_DIR}  ({os.path.basename(meta_path)})")


if __name__ == "__main__":
    main()
