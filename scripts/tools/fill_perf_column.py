# -*- coding: utf-8 -*-
"""fill_perf_column.py — 给里海案例页「二、事件时间线」表补「业绩（间隔 / 公告）」列

口径（对齐《里海案例-涪陵榨菜》页）：
  第三列 = 该行事件日期 与「最近一期已披露定期报告」的关系
     公告：<报告期年份> <类别>      ← 只取定期报告（年报 / 半年报 / 一季报 / 三季报），不含预告 / 快报
     间隔：晚 N 天 / 早 N 天 / 同日
     发布：YYYY-MM-DD              ← 巨潮 cninfo 归档日（data/disclosure/<code>_disclosure.json）
  事件日期无法解析到「日」的行 → 填 —

用法：
  .venv\\Scripts\\python scripts\\tools\\fill_perf_column.py             # 全部（已 4 列的自动跳过）
  .venv\\Scripts\\python scripts\\tools\\fill_perf_column.py 000830      # 指定代码
  .venv\\Scripts\\python scripts\\tools\\fill_perf_column.py --dry 000830  # 只预览不写
"""
import io
import json
import os
import re
import sys
from datetime import datetime

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CASE_DIR = os.path.join(BASE, "research-wiki", "research", "疯狂的里海", "案例")
DISC_DIR = os.path.join(BASE, "data", "disclosure")

M = {
    "002507": "涪陵榨菜", "600129": "太极集团", "603601": "再升科技", "600452": "涪陵电力",
    "301373": "凌玮科技", "603325": "博隆技术", "603758": "秦安股份", "000830": "鲁西化工",
    "300435": "中泰股份", "002053": "云南能投", "002539": "云图控股", "300596": "利安隆",
    "605077": "华康股份", "603612": "索通发展", "300401": "花园生物", "300006": "莱美药业",
    "002478": "常宝股份", "300547": "川环科技", "300019": "硅宝科技", "300786": "国林科技",
    "002353": "杰瑞股份", "000625": "长安汽车",
}

PERIODIC = {"年报", "半年报", "一季报", "三季报"}


def load_disc(code):
    p = os.path.join(DISC_DIR, "%s_disclosure.json" % code)
    if not os.path.exists(p):
        return []
    js = json.load(io.open(p, encoding="utf-8"))
    out = []
    for d in js.get("disclosures") or []:
        if d.get("category") not in PERIODIC:
            continue
        try:
            dt = datetime.strptime(str(d["date"])[:10], "%Y-%m-%d")
        except Exception:
            continue
        out.append((dt, d["category"], str(d["date"])[:10]))
    out.sort()
    return out


def parse_date(s):
    m = re.search(r"(\d{4})[.\-](\d{1,2})[.\-](\d{1,2})", s)
    if not m:
        return None
    try:
        return datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    except ValueError:
        return None


def perf_for(disc, cell):
    dt = parse_date(cell)
    if dt is None:
        return "—"
    prev = [r for r in disc if r[0] <= dt]
    if not prev:
        return "—"
    pdt, cat, dstr = prev[-1]
    y = pdt.year - 1 if cat == "年报" else pdt.year
    gap = (dt - pdt).days
    g = "同日" if gap == 0 else ("晚 %d 天" % gap if gap > 0 else "早 %d 天" % -gap)
    return "公告：%d %s<br>间隔：%s<br>发布：%s" % (y, cat, g, dstr)


def main():
    dry = "--dry" in sys.argv
    only = [a for a in sys.argv[1:] if not a.startswith("-")]
    only = only[0] if only else None

    for code, name in sorted(M.items()):
        if only and code != only:
            continue
        path = os.path.join(CASE_DIR, "里海案例-%s.md" % name)
        if not os.path.exists(path):
            print("[缺] %s" % path)
            continue
        lines = io.open(path, encoding="utf-8").read().split("\n")

        hi = None
        for i, ln in enumerate(lines):
            if ln.strip().startswith("| 时间 | 事件 |"):
                hi = i
                break
        if hi is None:
            print("[无时间线表] %s" % code)
            continue
        if "业绩" in lines[hi]:
            print("[已 4 列，跳过] %s %s" % (code, name))
            continue

        disc = load_disc(code)
        lines[hi] = "| 时间 | 事件 | 业绩（间隔 / 公告） | 出处 |"
        lines[hi + 1] = "|---|---|---|---|"

        j, n, miss = hi + 2, 0, 0
        while j < len(lines) and lines[j].strip().startswith("|"):
            s = lines[j].strip()
            inner = s[1:-1]                      # 去掉首尾的 |
            # 只切前两段：**出处列可能含 |（wiki 链接语法 [[路径|显示名]]）**，不能整行 split
            a, b, c = inner.split("|", 2)
            perf = perf_for(disc, a)
            if perf == "—":
                miss += 1
            lines[j] = "|" + a + "|" + b + "| " + perf + " |" + c.strip() + " |"
            n += 1
            j += 1

        print("%s %s: %d 行（另有 %d 行日期不可解析→—；披露日 %d 条）"
              % (code, name, n, miss, len(disc)))
        if dry:
            for k in range(hi, min(j, hi + 6)):
                print("   " + lines[k])
        else:
            io.open(path, "w", encoding="utf-8").write("\n".join(lines))


if __name__ == "__main__":
    main()
