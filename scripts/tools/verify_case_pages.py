# -*- coding: utf-8 -*-
"""verify_case_pages.py — 校验 22 个里海案例页的交付一致性

检查项（每页 5 项）：
  1) 时间线表头为 4 列（含「业绩（间隔 / 公告）」）
  2) 页面引用了 kline-<code>-review.png
  3) 该图片文件在 assets/ 中真实存在
  4) data/<code>.db 存在
  5) data/disclosure/<code>_disclosure.json 存在

用法：.venv\\Scripts\\python scripts\\tools\\verify_case_pages.py
"""
import io
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CASE = os.path.join(BASE, "research-wiki", "research", "疯狂的里海", "案例")
ASSETS = os.path.join(BASE, "research-wiki", "research", "疯狂的里海", "assets")
HDR = "| 时间 | 事件 | 业绩（间隔 / 公告） | 出处 |"

M = {
    "002507": "涪陵榨菜", "600129": "太极集团", "603601": "再升科技", "600452": "涪陵电力",
    "301373": "凌玮科技", "603325": "博隆技术", "603758": "秦安股份", "000830": "鲁西化工",
    "300435": "中泰股份", "002053": "云南能投", "002539": "云图控股", "300596": "利安隆",
    "605077": "华康股份", "603612": "索通发展", "300401": "花园生物", "300006": "莱美药业",
    "002478": "常宝股份", "300547": "川环科技", "300019": "硅宝科技", "300786": "国林科技",
    "002353": "杰瑞股份", "000625": "长安汽车",
}

bad = []
print("%-8s %-8s %-5s %-6s %-6s %-6s %-5s" % ("代码", "名称", "4列", "图引用", "图文件", "披露日", "db"))
for code, name in sorted(M.items()):
    p = os.path.join(CASE, "里海案例-%s.md" % name)
    if not os.path.exists(p):
        print("%-8s %-8s 页面缺失" % (code, name))
        bad.append(code)
        continue
    txt = io.open(p, encoding="utf-8").read()
    img = "kline-%s-review.png" % code
    row = (
        code, name,
        "OK" if HDR in txt else "缺",
        "OK" if img in txt else "缺",
        "OK" if os.path.exists(os.path.join(ASSETS, img)) else "缺",
        "OK" if os.path.exists(os.path.join(BASE, "data", "disclosure", "%s_disclosure.json" % code)) else "缺",
        "OK" if os.path.exists(os.path.join(BASE, "data", "%s.db" % code)) else "缺",
    )
    print("%-8s %-8s %-5s %-6s %-6s %-6s %-5s" % row)
    if "缺" in row[2:]:
        bad.append(code)

print()
print("总计 %d 页；不合格：%s" % (len(M), " ".join(bad) if bad else "无 ✓"))
