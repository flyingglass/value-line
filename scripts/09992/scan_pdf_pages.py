# -*- coding: utf-8 -*-
"""scan_pdf_pages.py — 扫描泡泡玛特(09992)报告 PDF，输出命中关键词的整页原文

用途：定位中报 / 年报里的「分地区收入」「分部资料」等表格页，供人工核对与引用（引用需标注 PDF 文件名 + 页码）。

用法：
    .venv\\Scripts\\python scripts\\09992\\scan_pdf_pages.py 2022 地区 海外 --period 中报
    .venv\\Scripts\\python scripts\\09992\\scan_pdf_pages.py 2025 亚太 美洲 --period 中报 --start 20 --end 60
"""
import argparse
import logging
import os
import sys

import pdfplumber

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
logging.getLogger("pdfminer").setLevel(logging.ERROR)   # 屏蔽 pdfminer 的 color 警告

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("year")
    ap.add_argument("keywords", nargs="+")
    ap.add_argument("--period", default="中报", choices=["中报", "年报"])
    ap.add_argument("--start", type=int, default=1)
    ap.add_argument("--end", type=int, default=9999)
    ap.add_argument("--code", default="09992")
    a = ap.parse_args()

    path = os.path.join(BASE, "data", "pdfs", a.code,
                        "%s_%s_%s.pdf" % (a.code, a.year, a.period))
    if not os.path.exists(path):
        print("未找到:", path)
        return
    print("PDF: %s" % os.path.basename(path))

    with pdfplumber.open(path) as pdf:
        total = len(pdf.pages)
        hits = 0
        for i in range(a.start - 1, min(a.end, total)):
            t = pdf.pages[i].extract_text() or ""
            hit = [k for k in a.keywords if k in t]
            if not hit:
                continue
            hits += 1
            print("\n" + "=" * 78)
            print("[page %d/%d] 命中: %s" % (i + 1, total, hit))
            print("=" * 78)
            print(t)
        print("\n共命中 %d 页（PDF 总页数 %d）" % (hits, total))


if __name__ == "__main__":
    main()
