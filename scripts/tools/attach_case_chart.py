# -*- coding: utf-8 -*-
"""attach_case_chart.py — 给里海案例页追加「附：周K 复盘图」节

用法：
  .venv\\Scripts\\python scripts\\tools\\attach_case_chart.py            # 处理全部（幂等，已含图的跳过）
  .venv\\Scripts\\python scripts\\tools\\attach_case_chart.py 000830     # 只处理指定代码

说明：图片由 scripts/linhai_chart.py 生成到 research-wiki/research/疯狂的里海/assets/；
      本脚本只负责在案例页末尾追加引用块（不覆盖已有内容，不重复追加）。
"""
import io
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CASE_DIR = os.path.join(BASE, "research-wiki", "research", "疯狂的里海", "案例")

# code -> (案例名, 起始年, 结束年)
M = {
    "000830": ("鲁西化工", 2020, 2026),
    "603758": ("秦安股份", 2019, 2026),
    "002478": ("常宝股份", 2021, 2026),
    "300547": ("川环科技", 2022, 2026),
    "300786": ("国林科技", 2022, 2026),
    "300019": ("硅宝科技", 2021, 2026),
    "300006": ("莱美药业", 2022, 2026),
    "300401": ("花园生物", 2023, 2026),
    "002053": ("云南能投", 2023, 2026),
    "300435": ("中泰股份", 2024, 2026),
    "002539": ("云图控股", 2024, 2026),
    "300596": ("利安隆", 2018, 2026),
    "605077": ("华康股份", 2024, 2026),
    "603612": ("索通发展", 2024, 2026),
    "002353": ("杰瑞股份", 2013, 2026),
    "000625": ("长安汽车", 2013, 2026),
}

TPL = """
---

## 附：周K 复盘图（{y0}-{y1}）

![{name}（{code}）里海案例复盘 · 周K（前复权）· {y0}-{y1}](../assets/kline-{code}-review.png)

> **读图**：主图 = 周K（前复权）+ 阶段框（蓝线为阶段切换年）+ 关键顶底 + 里海买卖点（文字为案例页原文「当时成交名义价」，与前复权价口径不同）+ 关键水平位。
> 主图下方「披露带」= 定期报告 / 业绩预告披露日（橙 = 业绩预告 · 快报，灰 = 年报 / 中报 / 一季报 / 三季报，标签 = 两位年份 + 报告期，如 21A / 21H1 / 21Q3）；底部 = 周成交量。三块面板共用同一时间轴。
> 生成脚本 `scripts/linhai_chart.py`（`SPECS["{code}"]`），数据源 `data/{code}.db`（kline 前复权 qfq）+ `data/disclosure/{code}_disclosure.json`（巨潮 cninfo 归档日）。
> 顶底由脚本按「该年最高 / 最低周」自动定位，未手填日期；买卖点价位未披露者只标日期、不标价。
"""


def main():
    only = sys.argv[1] if len(sys.argv) > 1 else None
    done, skip = [], []
    for code, (name, y0, y1) in sorted(M.items()):
        if only and code != only:
            continue
        path = os.path.join(CASE_DIR, "里海案例-%s.md" % name)
        if not os.path.exists(path):
            print("  [缺] %s" % path)
            continue
        txt = io.open(path, encoding="utf-8").read()
        if "kline-%s-review.png" % code in txt:
            skip.append(code)
            continue
        if not txt.endswith("\n"):
            txt += "\n"
        txt += TPL.format(code=code, name=name, y0=y0, y1=y1)
        io.open(path, "w", encoding="utf-8").write(txt)
        done.append(code)

    print("已追加图节：%s" % (" ".join(done) if done else "（无）"))
    print("已含图跳过：%s" % (" ".join(skip) if skip else "（无）"))


if __name__ == "__main__":
    main()
