#!/usr/bin/env python
"""研报 PDF 图表数值提取（坐标吸附法）——research-ingest skill 配套脚本。

适用：有文本层的券商/投行研报 PDF，图表内数值以「柱顶/柱旁标签」形式存在，
      而正文段落里没有逐格数据（典型：花旗、伯恩斯坦一类消费者调研图）。

原理：同类图的数值列与图例（国家/分组名）**x 坐标严格对齐**，
      因此可按列 x 把数值吸附回列名，再按行 y 取该行的选项标签。

用法：
  # 1) 探测是否有文本层（无文本层的纯图片 PDF 只能走 OCR，见 SKILL.md）
  python extract_pdf_chart_values.py <pdf> --probe

  # 2) 诊断某页版面：打印每个词块的 (y, x0-x1)，用来判断标签与数值的对应关系
  python extract_pdf_chart_values.py <pdf> --dump 14 --y 440 600

  # 3) 批量提取图表数值，输出 markdown 草表（逐图一个表）
  python extract_pdf_chart_values.py <pdf> --pages 3-24 \
      --columns Overall,China,Japan,US,UK,Australia

  # 4) 版式不同时调参
  python extract_pdf_chart_values.py <pdf> --pages 5-9 \
      --columns Overall,China --col-tol 12 --inner 305,390 --inner-y 3 --outer-y 6

注意：脚本只做「吸附」，**不判断哪个配对正确**。必须用正文数字做交叉校验
      （见 SKILL.md「研报 PDF 图表数值提取」），凡校验不过的配对一律标注存疑。
"""

from __future__ import annotations

import argparse
import re
import sys
from typing import Iterable

import pdfplumber

VAL = re.compile(r"^-?\d+(?:[.,]\d+)?%$")           # 百分比数值
NUMBER = re.compile(r"^-?\d+(?:[.,]\d+)?$")          # 裸数字（含坐标轴刻度）
MONEY = re.compile(r"^(us\$|rmb|hk\$|\$)", re.I)     # 货币前缀（不当作标签）
FIGURE = re.compile(r"Figure\s+\d+\.")


def _reconfigure_stdout() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:  # pragma: no cover - 老版本 Python
        pass


def probe(pdf_path: str) -> None:
    """输出每页文本层字符数，判断能否直接提取。"""
    with pdfplumber.open(pdf_path) as pdf:
        print(f"文件：{pdf_path}\n页数：{len(pdf.pages)}")
        for i, page in enumerate(pdf.pages, 1):
            n = len(page.chars)
            flag = "有文本层" if n > 200 else ("疑似无文本层（需 OCR）" if n < 50 else "文本层极稀疏（需 OCR）")
            words = len(page.extract_words()) if n else 0
            print(f"  第 {i:>3} 页：chars={n:>6}  words={words:>4}  {flag}")


def rows_of(page, y_min: float | None = None, y_max: float | None = None,
            bucket: int = 2) -> list[tuple[float, list]]:
    """把词块按 y 分桶（bucket 越小越精细），返回 [(y, [word...]), ...]。"""
    buckets: dict[float, list] = {}
    for w in page.extract_words():
        if y_min is not None and w["top"] < y_min:
            continue
        if y_max is not None and w["top"] > y_max:
            continue
        buckets.setdefault(round(w["top"] / bucket) * bucket, []).append(w)
    return [(y, sorted(ws, key=lambda w: w["x0"])) for y, ws in sorted(buckets.items())]


def dump_page(pdf_path: str, page_no: int, y_min: float | None, y_max: float | None) -> None:
    """打印单页词块坐标，用于人工诊断版面（标签在左还是在柱旁、有无第二套标签）。"""
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[page_no - 1]
        print(f"===== page {page_no} (w={page.width:.0f} h={page.height:.0f}) =====")
        for y, ws in rows_of(page, y_min, y_max, bucket=3):
            line = "  ".join(f"{w['text']}[{w['x0']:.0f}-{w['x1']:.0f}]" for w in ws)
            print(f"y={y:6.0f} | {line}")


def _snap_columns(values: Iterable, legend: dict[str, float], tol: float) -> list[str]:
    """把数值按 x 吸附到列名。"""
    values = list(values)
    cells = []
    for name in legend:
        hit = ""
        for w in values:
            if abs(w["x0"] - legend[name]) <= tol:
                hit = w["text"]
        cells.append(hit)
    return cells


def _is_axis_row(words: list) -> bool:
    """判定整行是否为 x 轴刻度（如 0% 10% 20% ... 50%）。"""
    pcts = [w for w in words if VAL.match(w["text"]) and w["x0"] < 300]
    return len(pcts) >= 4


def extract(pdf_path: str, pages: tuple[int, int], columns: list[str],
            col_tol: float, inner: tuple[float, float], inner_y: float,
            outer_y: float) -> None:
    """逐图打印「标签 | 各列数值」草表；配对正确性须由正文交叉校验（脚本不做判断）。"""
    with pdfplumber.open(pdf_path) as pdf:
        for page_no in range(pages[0], min(pages[1], len(pdf.pages)) + 1):
            page = pdf.pages[page_no - 1]
            lines = rows_of(page, bucket=2)
            texts = [(y, ws, " ".join(w["text"] for w in ws)) for y, ws in lines]

            starts = [i for i, (_, _, t) in enumerate(texts) if FIGURE.search(t)]
            print(f"\n########## PAGE {page_no} ##########")
            if not starts:
                print("  [本页未发现 Figure 标题]")
            for k, si in enumerate(starts):
                ei = starts[k + 1] if k + 1 < len(starts) else len(texts)
                block = [b for b in texts[si:ei] if "Source:" not in b[2][:12]]
                title = block[0][2].strip()
                legend: dict[str, float] | None = None
                for _, ws, _ in block:
                    hit = {w["text"]: w["x0"] for w in ws if w["text"] in columns}
                    if len(hit) >= max(2, len(columns) // 2):
                        legend = hit
                        break

                print(f"\n-- {title}")
                if legend:
                    print("   列 x：" + "  ".join(f"{c}={x:.0f}" for c, x in legend.items()))
                else:
                    print("   [未找到图例行，数值按出现顺序输出]")

                value_x_min = (min(legend.values()) - col_tol - 5) if legend else 300

                def label_token_ok(w, row_ws) -> bool:
                    """判断某词块能否作为「选项标签」的一部分。"""
                    tk = w["text"]
                    if w["x0"] >= value_x_min:          # 数值列区域
                        return False
                    if w["x0"] < 80 and (NUMBER.match(tk) or VAL.match(tk)):
                        return False                    # y 轴刻度
                    names_in_row = sum(1 for x in row_ws if x["text"] in columns)
                    if tk in columns and names_in_row >= 2:
                        return False                    # 第二面板的轴标签/图例
                    return True

                for y, ws, _ in block:
                    if _is_axis_row(ws):
                        continue
                    vals = [w for w in ws if VAL.match(w["text"]) and w["x0"] >= value_x_min]
                    if not vals:
                        continue
                    cells = _snap_columns(vals, legend, col_tol) if legend else [w["text"] for w in vals]

                    inner_labels, outer_labels = [], []
                    for yy, wws, _ in block:
                        for w in wws:
                            if not label_token_ok(w, wws):
                                continue
                            if inner[0] <= w["x0"] <= inner[1] and abs(yy - y) <= inner_y:
                                inner_labels.append((yy, w["x0"], w["text"]))
                            elif w["x1"] < inner[0] and w["x0"] >= 55 and abs(yy - y) <= outer_y:
                                outer_labels.append((yy, w["x0"], w["text"]))
                    use = inner_labels or outer_labels
                    label = " ".join(t for _, _, t in sorted(use, key=lambda c: (c[0], c[1])))
                    print(f"   | {label:<58} | " + " | ".join(f"{c:>4}" for c in cells))


def main() -> None:
    _reconfigure_stdout()
    ap = argparse.ArgumentParser(description="研报 PDF 图表数值提取（坐标吸附法）")
    ap.add_argument("pdf", help="PDF 路径")
    ap.add_argument("--probe", action="store_true", help="探测文本层")
    ap.add_argument("--dump", type=int, metavar="PAGE", help="打印指定页词块坐标")
    ap.add_argument("--y", nargs=2, type=float, metavar=("Y0", "Y1"), help="配合 --dump 限定 y 区间")
    ap.add_argument("--pages", metavar="A-B", help="批量提取的页范围，如 3-24")
    ap.add_argument("--columns", default="Overall,China,Japan,US,UK,Australia",
                    help="图例列名（逗号分隔，顺序即表头顺序）")
    ap.add_argument("--col-tol", type=float, default=14, help="列吸附容差 pt（默认 14）")
    ap.add_argument("--inner", default="300,392", help="图内标签 x 窗口（默认 300,392）")
    ap.add_argument("--inner-y", type=float, default=4, help="图内标签 y 容差（默认 4）")
    ap.add_argument("--outer-y", type=float, default=6, help="左侧长标签 y 容差（默认 6）")
    args = ap.parse_args()

    if args.probe:
        probe(args.pdf)
        return
    if args.dump:
        dump_page(args.pdf, args.dump, *(args.y or [None, None]))
        return
    if not args.pages:
        ap.error("请指定 --probe / --dump / --pages 之一")
    a, b = args.pages.split("-")
    inner = tuple(float(x) for x in args.inner.split(","))
    extract(args.pdf, (int(a), int(b)), [c.strip() for c in args.columns.split(",")],
            args.col_tol, inner, args.inner_y, args.outer_y)


if __name__ == "__main__":
    main()
