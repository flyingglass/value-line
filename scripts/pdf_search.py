# -*- coding: utf-8 -*-
"""pdf_search.py — 在年报/中报 PDF 中按关键词定位并输出「命中页原文」

用途：从 data/pdfs/<code>/ 的报告里定位「核心竞争力 / 行业格局 / 竞争对手 / 市占率 / 出海」等
      章节原文，供 research-wiki 案例页引用（引用时必须标注 PDF 文件名 + 页码）。

用法：
    .venv\\Scripts\\python scripts\\pdf_search.py <code> <关键词1> [关键词2 ...]
                                            [--year 2025] [--period 年报]
                                            [--start 1] [--end 200] [--head 60]

示例：
    .venv\\Scripts\\python scripts\\pdf_search.py 603325 核心竞争力 竞争对手 --year 2025
    .venv\\Scripts\\python scripts\\pdf_search.py 301373 市占率 出海 --year 2025 --head 800

注意：只读，不写任何文件；不加 --head 则输出整页文本。
"""
import os
import sys
import glob
import argparse

import pdfplumber

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("code")
    ap.add_argument("keywords", nargs="+")
    ap.add_argument("--year", default="2025")
    ap.add_argument("--period", default="年报")
    ap.add_argument("--start", type=int, default=1)
    ap.add_argument("--end", type=int, default=200)
    ap.add_argument("--head", type=int, default=0, help="每页只输出前 N 字符；0=整页")
    a = ap.parse_args()

    pat = os.path.join(config.pdf_dir(a.code),
                       f"{config.pdf_code(a.code)}_{a.year}_{a.period}.pdf")
    files = sorted(glob.glob(pat), reverse=True)
    if not files:
        print("未找到:", pat)
        return
    path = files[0]
    print("PDF:", os.path.basename(path))

    hits = 0
    with pdfplumber.open(path) as pdf:
        total = len(pdf.pages)
        for i in range(a.start - 1, min(a.end, total)):
            t = pdf.pages[i].extract_text() or ""
            matched = [k for k in a.keywords if k in t]
            if not matched:
                continue
            hits += 1
            print("\n" + "=" * 78)
            print(f"[page {i + 1}/{total}] 命中: {matched}")
            print("=" * 78)
            print(t if a.head <= 0 else t[:a.head])
    print(f"\n共命中 {hits} 页")


if __name__ == "__main__":
    main()
