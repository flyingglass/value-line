# -*- coding: utf-8 -*-
"""宝武系关联销售：客户×年度矩阵（修正版：只用各年报『本期』值，避免本期/上期重复累加）"""
import pdfplumber, re, json

def parse(path, pages):
    pdf = pdfplumber.open(path)
    txt = "\n".join((pdf.pages[i].extract_text() or "") for i in pages)
    lines = [l.rstrip() for l in txt.split("\n")]
    def nums(s): return [float(x.replace(",", "")) for x in re.findall(r"[\d,]+\.\d{2}", s)]
    out = []
    for i, ln in enumerate(lines):
        if "出售商品/提供劳务" in ln:
            name = ln.split("出售商品")[0].strip()
            tail = ln.split("出售商品/提供劳务", 1)[1].strip()
            v = nums(tail)
            if not v:
                acc = []
                for j in range(i + 1, min(i + 3, len(lines))):
                    acc += nums(lines[j])
                    if acc: break
                if not name: name = lines[i - 1].strip()
                v = acc
            if v: out.append((re.sub(r"\s+", "", name), v))
    return out

SPEC = [
    ("data/tmp_600845/600845_2019_年报.pdf", [157, 158, 159], "FY2019", "FY2018"),
    ("data/tmp_600845/600845_2020_年报.pdf", [162, 163, 164], "FY2020", "FY2019"),
    ("data/tmp_600845/600845_2021_年报.pdf", [176, 177, 178, 179], "FY2021", "FY2020"),
    ("data/tmp_600845/600845_2022_年报.pdf", [169, 170, 171, 172], "FY2022", "FY2021"),
    ("data/tmp_600845/600845_2023_年报.pdf", [178, 179, 180, 181], "FY2023", "FY2022"),
    ("data/tmp_600845/600845_2024_年报.pdf", [193, 194, 195, 196], "FY2024", "FY2023"),
    ("data/tmp_600845/600845_2025_年报.pdf", [186, 187, 188, 189], "FY2025", "FY2024"),
]
groups = [
    (r"宝山钢铁|^宝钢股份|^宝钢集团", "宝钢股份"),
    (r"马钢|马鞍山钢铁", "马钢系"),
    (r"昆明钢铁|昆钢", "昆钢系"),
    (r"武汉钢铁|^武钢", "武钢系"),
    (r"湛江", "湛江钢铁"),
    (r"太钢|山西太钢", "太钢系"),
    (r"梅山", "梅山系"),
    (r"新余钢铁|^新钢", "新余钢铁"),
    (r"八一钢铁", "八一钢铁"),
    (r"鄂城|鄂钢", "鄂钢"),
    (r"昆明钢铁|昆钢", "昆钢系"),
    (r"山东钢铁|山钢|莱芜", "山钢系"),
    (r"重庆钢铁|^重钢", "重庆钢铁"),
    (r"欧冶", "欧冶系"),
    (r"长江钢铁", "长江钢铁"),
    (r"宝武集团其他子公司|宝武集团及其子公司", "【集团长尾汇总】"),
    (r"^宝武集团$|中国宝武钢铁集团|宝武集团有限公司", "宝武集团本部"),
]
def norm(n):
    for pat, g in groups:
        if re.search(pat, n): return g
    return n

YR = ["FY2018", "FY2019", "FY2020", "FY2021", "FY2022", "FY2023", "FY2024", "FY2025"]
M, totals = {}, {}
for path, pages, yc, yp in SPEC:
    rows = parse(path, pages)
    totals[yc] = sum(v[0] for _, v in rows)
    if yp not in totals:                              # FY2018 无独立年报，取自 2019 年报上期列
        totals[yp] = sum(v[1] for _, v in rows if len(v) > 1)
    for n, v in rows:
        g = norm(n)
        M.setdefault(g, {})
        M[g][yc] = M[g].get(yc, 0) + v[0]          # 同组多个关联方累加；跨年份互不干扰
        if len(v) > 1 and yp == "FY2018":          # 仅补最早的 FY2018（来自 2019 年报上期列）
            M[g][yp] = M[g].get(yp, 0) + v[1]

REV = {"FY2018": 58.19, "FY2019": 68.49, "FY2020": 102.25, "FY2021": 117.59,
       "FY2022": 131.50, "FY2023": 129.16, "FY2024": 136.44, "FY2025": 109.72}
json.dump({"matrix": M, "totals": totals, "rev": REV},
          open("data/tmp_600845/rel_matrix.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

print("=== 关联销售 / 营收 / 占比 ===")
for y in YR:
    t = totals.get(y); r = REV[y]
    print(f"  {y}: {t/1e8:>7.2f} 亿 | 营收 {r:>7.2f} | 占比 {t/1e8/r*100:>5.1f}% | 非关联 {r-t/1e8:>7.2f}")
print(f"\n{'客户/集团':<20}" + "".join(f"{y[2:]:>9}" for y in YR) + "   峰值")
for g, d in sorted(M.items(), key=lambda x: -max(x[1].values())):
    if max(d.values()) < 1.0e8: continue
    vals = "".join(f"{d[y]/1e8:>9.2f}" if y in d else f"{'—':>9}" for y in YR)
    pk = max(d, key=lambda k: d[k])
    print(f"{g[:18]:<20}{vals}   {pk[2:]}")
