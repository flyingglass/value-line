# -*- coding: utf-8 -*-
"""图1：宝信软件营收结构（上：宝武系关联销售 vs 非关联收入堆叠柱｜下：关联占比折线）"""
YR = [2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025]
REL = [23.70, 29.32, 47.04, 65.65, 74.50, 72.65, 69.16, 61.16]
REV = [58.19, 68.49, 102.25, 117.59, 131.50, 129.16, 136.44, 109.72]
NREL = [round(r - a, 2) for r, a in zip(REV, REL)]
PCT = [round(a / r * 100, 1) for a, r in zip(REL, REV)]

W, H = 680, 400
ML, MR = 52, 46
X0, X1 = ML, W - MR
MT, PH = 44, 196
MT2, PH2 = 276, 66
YM, BW = 145.0, 40
def X(i): return X0 + (X1 - X0) * (i + 0.5) / len(YR)
def Y(v): return MT + PH - v / YM * PH
def Y2(p): return MT2 + PH2 - (p - 20) / 40 * PH2

s = [f'<svg viewBox="0 0 {W} {H}" width="100%" role="img" xmlns="http://www.w3.org/2000/svg">',
     '<title>宝信软件营收结构：宝武系关联销售与非关联收入（2018-2025）</title>',
     '<desc>上图为堆叠柱（下层宝武系关联销售、上层非关联收入），下图为关联销售占营收比重折线。关联销售2022年见顶74.5亿元后连续三年降至61.2亿元。</desc>',
     '<text x="20" y="20" font-size="14" font-weight="500" fill="#2C2C2A">宝信软件的营收结构：宝武系关联销售 vs 非关联收入（亿元）</text>']
for v in range(0, 141, 30):
    s.append(f'<line x1="{X0}" y1="{Y(v):.1f}" x2="{X1}" y2="{Y(v):.1f}" stroke="#D3D1C7" stroke-width="0.5"/>')
    s.append(f'<text x="{X0-6}" y="{Y(v)+4:.1f}" font-size="11" fill="#5F5E5A" text-anchor="end">{v}</text>')
s.append(f'<line x1="{X0}" y1="{Y(0):.1f}" x2="{X1}" y2="{Y(0):.1f}" stroke="#888780" stroke-width="0.9"/>')
for i in range(len(YR)):
    x = X(i)
    s.append(f'<rect x="{x-BW/2:.1f}" y="{Y(REL[i]):.1f}" width="{BW}" height="{REL[i]/YM*PH:.1f}" fill="#B5D4F4" stroke="#185FA5" stroke-width="0.6"/>')
    s.append(f'<rect x="{x-BW/2:.1f}" y="{Y(REV[i]):.1f}" width="{BW}" height="{NREL[i]/YM*PH:.1f}" fill="#D3D1C7" stroke="#888780" stroke-width="0.6"/>')
    s.append(f'<text x="{x:.1f}" y="{Y(REV[i])-5:.1f}" font-size="11" fill="#2C2C2A" text-anchor="middle">{REV[i]:.1f}</text>')
    if i in (0, 2, 4, 7):
        s.append(f'<text x="{x:.1f}" y="{Y(REL[i]/2)+4:.1f}" font-size="11" fill="#0C447C" text-anchor="middle">{REL[i]:.1f}</text>')
s.append(f'<line x1="{X(4):.1f}" y1="{MT-6}" x2="{X(4):.1f}" y2="{MT+PH:.1f}" stroke="#A32D2D" stroke-width="0.8" stroke-dasharray="4 3"/>')
s.append(f'<text x="{X(4)+5:.1f}" y="{MT+10}" font-size="11" fill="#A32D2D">关联销售峰值 74.5 亿</text>')
s.append(f'<text x="{X(7)+8:.1f}" y="{MT+28}" font-size="11" fill="#A32D2D" text-anchor="end">三年连降至 61.2 亿（-17.9%）</text>')

for p in [20, 30, 40, 50, 60]:
    s.append(f'<line x1="{X0}" y1="{Y2(p):.1f}" x2="{X1}" y2="{Y2(p):.1f}" stroke="#D3D1C7" stroke-width="0.5"/>')
    s.append(f'<text x="{X0-6}" y="{Y2(p)+4:.1f}" font-size="11" fill="#854F0B" text-anchor="end">{p}%</text>')
s.append(f'<line x1="{X0}" y1="{MT2+PH2:.1f}" x2="{X1}" y2="{MT2+PH2:.1f}" stroke="#888780" stroke-width="0.9"/>')
s.append(f'<text x="{X0}" y="{MT2-8:.1f}" font-size="11" fill="#5F5E5A">关联销售占营业收入比重</text>')
pts = " ".join(f"{X(i):.1f},{Y2(PCT[i]):.1f}" for i in range(len(YR)))
s.append(f'<polyline points="{pts}" fill="none" stroke="#854F0B" stroke-width="1.4"/>')
for i in range(len(YR)):
    s.append(f'<circle cx="{X(i):.1f}" cy="{Y2(PCT[i]):.1f}" r="2.6" fill="#BA7517"/>')
    s.append(f'<text x="{X(i):.1f}" y="{Y2(PCT[i])-8:.1f}" font-size="11" fill="#854F0B" text-anchor="middle">{PCT[i]:.0f}%</text>')
    s.append(f'<text x="{X(i):.1f}" y="{MT2+PH2+15:.1f}" font-size="11" fill="#5F5E5A" text-anchor="middle">{YR[i]}</text>')

ly = H - 16
lx = 20
for lab, c, st in [("宝武系关联销售", "#B5D4F4", "#185FA5"), ("非关联收入（含 IDC、外部客户）", "#D3D1C7", "#888780")]:
    s.append(f'<rect x="{lx}" y="{ly-10}" width="11" height="11" fill="{c}" stroke="{st}" stroke-width="0.6"/>')
    s.append(f'<text x="{lx+15}" y="{ly}" font-size="11" fill="#444441">{lab}</text>')
    lx += 15 + len(lab) * 12.6 + 20
s.append(f'<line x1="{lx}" y1="{ly-5}" x2="{lx+16}" y2="{ly-5}" stroke="#854F0B" stroke-width="1.4"/>')
s.append(f'<circle cx="{lx+8}" cy="{ly-5}" r="2.6" fill="#BA7517"/>')
s.append(f'<text x="{lx+21}" y="{ly}" font-size="11" fill="#444441">关联销售占比</text>')
s.append('</svg>')
open("data/tmp_600845/out_rel.svg", "w", encoding="utf-8").write("\n".join(s))
print("bytes:", len("\n".join(s)), "| 图例最右 ≈", round(lx + 21 + 6 * 12.6), "/", W)
for y, a, n, r, p in zip(YR, REL, NREL, REV, PCT):
    print(f"  {y}: 关联 {a:>6.2f} + 非关联 {n:>6.2f} = {r:>6.2f}  占比 {p}%")
