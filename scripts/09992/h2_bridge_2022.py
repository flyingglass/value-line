# -*- coding: utf-8 -*-
"""
2022H2 桥接：H2 = FY2022 - 2022H1

数据源（均为公司原始披露，单位人民币千元）：
  22A  : 2022 年报 附注5「收益及分部资料」P242
  22H1 : 2022 中报 附注5「收益及分部资料」P68
门店数：22 年报 P12/P13（329 店 / 2,067 台；海外 43 店 / 120 台）
       22 中报 P9/P10（308 店 / 1,916 台；海外 24 店 / 98 台）
IP 收入：22 年报 P10、22 中报 P7（管理层讨论，非附注口径）
"""
import csv
import io
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

OUT = os.path.join("scripts", "out", "09992_2022_h2_bridge.csv")

# ---------- 收入：渠道 x 地区 ----------
REV = [
    # (地区, 渠道, 22A, 22H1)
    ("中国内地", "零售店", 1691112, 891701),
    ("中国内地", "线上", 1829809, 977933),
    ("中国内地", "机器人商店", 378830, 203957),
    ("中国内地", "批发", 263635, 128537),
    ("港澳台及海外", "零售店", 135559, 34794),
    ("港澳台及海外", "线上", 90224, 34829),
    ("港澳台及海外", "机器人商店", 15209, 3863),
    ("港澳台及海外", "批发", 212946, 83204),
]

# ---------- 期末门店/台数 ----------
NUM = [
    # (地区, 类型, 22A期末, 22H1期末, 2021期末)
    ("中国内地", "零售店", 329, 308, 288),
    ("中国内地", "机器人商店", 2067, 1916, 1861),
    ("港澳台及海外", "零售店(含加盟)", 43, 24, None),
    ("港澳台及海外", "机器人商店(含加盟)", 120, 98, None),
]

# ---------- IP 收入（管理层讨论口径，单位百万元） ----------
IP = [
    ("SKULLPANDA", 851.6, 461.8),
    ("MOLLY", 802.2, 404.3),
    ("DIMOO", 577.9, 298.4),
    ("小甜豆", 147.9, 81.2),
    ("SKULLPANDA 夜之城系列（累计）", 228.4, 179.1),
    ("MEGA 珍藏系列", 466.8, 193.4),
]


def pct(h2, h1):
    return None if h1 == 0 else (h2 - h1) / h1 * 100.0


rows = []
print("=" * 78)
print("一、收入 H2 = FY2022 − 2022H1（人民币千元）")
print("=" * 78)
print("%-12s %-12s %10s %10s %10s %8s" % ("地区", "渠道", "22H1", "22H2", "22A", "H2vsH1"))
for reg, ch, a, h in REV:
    h2 = a - h
    r = pct(h2, h)
    rows.append([reg, ch, h, h2, a, None if r is None else round(r, 1)])
    print("%-12s %-12s %10d %10d %10d %7.1f%%" % (reg, ch, h, h2, a, r))

for reg in ("中国内地", "港澳台及海外"):
    a = sum(x[2] for x in REV if x[0] == reg)
    h = sum(x[3] for x in REV if x[0] == reg)
    r = pct(a - h, h)
    rows.append([reg, "小计", h, a - h, a, round(r, 1)])
    print("%-12s %-12s %10d %10d %10d %7.1f%%" % (reg, "小计", h, a - h, a, r))

a_all = sum(x[2] for x in REV)
h_all = sum(x[3] for x in REV)
rows.append(["合计", "总收入", h_all, a_all - h_all, a_all, round(pct(a_all - h_all, h_all), 1)])
print("%-12s %-12s %10d %10d %10d %7.1f%%" % ("合计", "总收入", h_all, a_all - h_all, a_all,
                                              pct(a_all - h_all, h_all)))

# 海外占比
o_h = sum(x[3] for x in REV if x[0] == "港澳台及海外")
o_a = sum(x[2] for x in REV if x[0] == "港澳台及海外")
print("\n海外收入占比：22H1 %.2f%% → 22H2 %.2f%%"
      % (o_h / h_all * 100, (o_a - o_h) / (a_all - h_all) * 100))

print("\n" + "=" * 78)
print("二、开店与店效（半年口径，千元/店·期）")
print("=" * 78)
print("%-16s %-16s %6s %6s %10s %10s %8s" % ("地区", "类型", "H1末", "A末", "H1单店", "H2单店", "H2vsH1"))
eff = []
for reg, tp, a_n, h_n, _ in NUM:
    a_rev = dict(((x[0], x[1]), x[2]) for x in REV)[(reg, tp.split("(")[0])]
    h_rev = dict(((x[0], x[1]), x[3]) for x in REV)[(reg, tp.split("(")[0])]
    h2_rev = a_rev - h_rev
    e_h = h_rev / h_n
    e_h2 = h2_rev / a_n
    r = pct(e_h2, e_h)
    eff.append([reg, tp, h_n, a_n, round(e_h, 1), round(e_h2, 1), round(r, 1)])
    print("%-16s %-16s %6d %6d %10.1f %10.1f %7.1f%%" % (reg, tp, h_n, a_n, e_h, e_h2, r))

# 海外零售店：新店的边际产出
h2_rev_os = 135559 - 34794
print("\n海外零售店 H2 增量拆解：收入 +%d 千元，净增 %d 店 → 边际 %.1f 千元/新增店·半年"
      % (h2_rev_os, 43 - 24, h2_rev_os / (43 - 24)))
print("（对照：H1 存量店单店 %.1f 千元/半年，边际是存量的 %.2f 倍）"
      % (34794 / 24, (h2_rev_os / (43 - 24)) / (34794 / 24)))

print("\n" + "=" * 78)
print("三、IP / 产品线 H1 → H2（百万元，管理层讨论口径）")
print("=" * 78)
print("%-28s %8s %8s %8s %8s" % ("项目", "22H1", "22H2", "22A", "H2vsH1"))
ip_rows = []
for name, a, h in IP:
    h2 = a - h
    r = pct(h2, h)
    ip_rows.append([name, h, round(h2, 1), a, round(r, 1)])
    print("%-28s %8.1f %8.1f %8.1f %7.1f%%" % (name, h, h2, a, r))
print("\n注：夜之城为累计口径（截至 6/30 vs 截至 12/31），H2 列是当期新增而非半年销售额。")

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f)
    w.writerow(["section", "region", "item", "v1", "v2", "v3", "v4", "H2_vs_H1_pct"])
    w.writerow(["字段说明", "",
                "revenue: v1=22H1收入 v2=22H2收入 v3=22A收入(千元)",
                "efficiency: v1=H1末数 v2=A末数 v3=H1单店 v4=H2单店(千元/期)",
                "ip: v1=22H1 v2=22H2 v3=22A(百万元)", "", ""])
    for r in rows:
        w.writerow(["revenue"] + r)
    for r in eff:
        w.writerow(["efficiency", r[0], r[1], r[2], r[3], r[4], r[5], r[6]])
    for r in ip_rows:
        w.writerow(["ip", "", r[0], r[1], r[2], r[3], "", r[4]])
print("\nCSV ->", OUT)
