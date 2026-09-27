# -*- coding: utf-8 -*-
"""解析宝信年报/中报「关联方出售商品/提供劳务」明细，构建客户×年度矩阵"""
import pdfplumber, re, json, os

def parse(path, pages):
    pdf = pdfplumber.open(path)
    txt = "\n".join((pdf.pages[i].extract_text() or "") for i in pages)
    lines = [l.rstrip() for l in txt.split("\n")]
    def nums(s):
        return [float(x.replace(",", "")) for x in re.findall(r"[\d,]+\.\d{2}", s)]
    rows = []
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
                if not name:
                    name = lines[i - 1].strip()
                v = acc
            if v:
                rows.append((name, v))
    return rows

SPEC = {
    "2022": ("data/tmp_600845/600845_2022_年报.pdf", [169, 170, 171, 172], "FY2022", "FY2021"),
    "2023": ("data/tmp_600845/600845_2023_年报.pdf", [178, 179, 180, 181], "FY2023", "FY2022"),
    "2024": ("data/tmp_600845/600845_2024_年报.pdf", [193, 194, 195, 196], "FY2024", "FY2023"),
    "2025": ("data/tmp_600845/600845_2025_年报.pdf", [186, 187, 188, 189], "FY2025", "FY2024"),
}

series = {}   # name -> {year: value}
totals = {}
for k, (path, pages, yc, yp) in SPEC.items():
    rows = parse(path, pages)
    c = sum(v[0] for _, v in rows)
    p = sum(v[1] for _, v in rows if len(v) > 1)
    totals[yc] = c
    if len([1 for _, v in rows if len(v) > 1]) > 5:
        totals[yp] = p
    for n, v in rows:
        n = re.sub(r"\s+", "", n)
        series.setdefault(n, {})
        series[n][yc] = v[0]
        if len(v) > 1:
            series[n][yp] = v[1]
    print(f"{yc}: 列示 {len(rows)} 行 | 本期合计 {c/1e8:.4f} 亿 | 上期({yp}) {p/1e8:.4f} 亿")

print("\n=== 各年度关联销售合计（亿元）===")
for y in ["FY2021", "FY2022", "FY2023", "FY2024", "FY2025"]:
    print(f"  {y}: {totals.get(y, float('nan'))/1e8:.4f}")

with open("data/tmp_600845/rel_series.json", "w", encoding="utf-8") as f:
    json.dump({"series": series, "totals": totals}, f, ensure_ascii=False, indent=1)

print("\n=== 前 25 大客户（按 FY2025 / 或缺省最新值）时间序列（亿元）===")
YR = ["FY2021", "FY2022", "FY2023", "FY2024", "FY2025"]
def latest(d):
    for y in reversed(YR):
        if y in d: return d[y]
    return 0
print(f"{'客户':<32}" + "".join(f"{y:>10}" for y in YR))
for n, d in sorted(series.items(), key=lambda x: -latest(x[1]))[:25]:
    vals = "".join(f"{d[y]/1e8:>10.4f}" if y in d else f"{'—':>10}" for y in YR)
    print(f"{n[:30]:<32}{vals}")
