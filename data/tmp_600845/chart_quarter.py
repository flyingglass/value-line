# -*- coding: utf-8 -*-
"""宝信软件单季营收（2021-2026）：验证 2026Q2 +37.3% 是否源于低基数"""
W, H = 680, 372
ML, MR, MT, PH = 56, 16, 56, 216
X0, X1 = ML, W - MR
YM = 56.0
YEARS = [2021, 2022, 2023, 2024, 2025, 2026]
DATA = {
    2021: [20.18, 28.56, 25.31, 43.54],
    2022: [24.98, 24.64, 26.91, 54.97],
    2023: [25.22, 31.55, 31.41, 40.98],
    2024: [33.91, 33.52, 30.14, 38.87],
    2025: [25.38, 21.77, 23.37, 39.20],
    2026: [26.44, 29.88, None, None],
}
def Y(v): return MT + PH - v / YM * PH
slot = (X1 - X0) / len(YEARS)
bw = slot * 0.19
COL = {1: "#B5D4F4", 2: "#185FA5", 3: "#9FE1CB", 4: "#D3D1C7"}
s = [f'<svg viewBox="0 0 {W} {H}" width="100%" role="img" xmlns="http://www.w3.org/2000/svg">',
     '<title>宝信软件单季营业收入 2021-2026</title>',
     '<desc>分组柱状图显示各年四个季度营收。2025年二季度21.77亿元为2021年以来最低，2026年二季度29.88亿元仍低于2023与2024年同期。</desc>',
     '<text x="20" y="20" font-size="14" font-weight="500" fill="#2C2C2A">单季营业收入：2026Q2 的 +37.3% 来自哪（亿元）</text>',
     '<text x="20" y="38" font-size="11" fill="#888780">数据：data/db/600845.db income「一、营业总收入」，单季由累计值拆分｜2026 年 Q3/Q4 未披露</text>']
for v in range(0, 57, 10):
    s.append(f'<line x1="{X0}" y1="{Y(v):.1f}" x2="{X1}" y2="{Y(v):.1f}" stroke="#D3D1C7" stroke-width="0.5"/>')
    s.append(f'<text x="{X0-6}" y="{Y(v)+4:.1f}" font-size="11" fill="#5F5E5A" text-anchor="end">{v}</text>')
s.append(f'<line x1="{X0}" y1="{Y(0):.1f}" x2="{X1}" y2="{Y(0):.1f}" stroke="#888780" stroke-width="0.9"/>')
for yi, yr in enumerate(YEARS):
    base = X0 + slot * yi + slot * 0.5 - bw * 2
    for qi, val in enumerate(DATA[yr]):
        if val is None:
            x = base + bw * qi
            s.append(f'<rect x="{x:.1f}" y="{Y(0)-14:.1f}" width="{bw-1:.1f}" height="14" fill="none" stroke="#D3D1C7" stroke-width="0.6" stroke-dasharray="2 2"/>')
            continue
        x = base + bw * qi
        fill = COL[qi + 1]
        s.append(f'<rect x="{x:.1f}" y="{Y(val):.1f}" width="{bw-1:.1f}" height="{val/YM*PH:.1f}" fill="{fill}" stroke="#888780" stroke-width="0.4"/>')
    s.append(f'<text x="{X0 + slot*yi + slot*0.5:.1f}" y="{Y(0)+15:.1f}" font-size="11" fill="#5F5E5A" text-anchor="middle">{yr}</text>')
# 两条对比虚线
for yr, qi, val, col, lab, dy in [(2024, 1, 33.52, "#0F6E56", "2024Q2 33.52", -6), (2023, 1, 31.55, "#534AB7", "2023Q2 31.55", -6)]:
    yy = Y(val)
    s.append(f'<line x1="{X0}" y1="{yy:.1f}" x2="{X1}" y2="{yy:.1f}" stroke="{col}" stroke-width="0.8" stroke-dasharray="5 3"/>')
    s.append(f'<text x="{X1-2:.1f}" y="{yy+dy:.1f}" font-size="11" fill="{col}" text-anchor="end">{lab}</text>')
# 高亮 2025Q2 与 2026Q2
x25 = X0 + slot * 4 + slot * 0.5 - bw * 2 + bw * 1
x26 = X0 + slot * 5 + slot * 0.5 - bw * 2 + bw * 1
s.append(f'<circle cx="{x25+bw/2:.1f}" cy="{Y(21.77):.1f}" r="3.4" fill="#A32D2D"/>')
s.append(f'<text x="{x25+bw/2:.1f}" y="{Y(21.77)+34:.1f}" font-size="11" fill="#A32D2D" text-anchor="middle">2025Q2 21.77</text>')
s.append(f'<text x="{x25+bw/2:.1f}" y="{Y(21.77)+48:.1f}" font-size="11" fill="#A32D2D" text-anchor="middle">2021年以来最低</text>')
s.append(f'<circle cx="{x26+bw/2:.1f}" cy="{Y(29.88):.1f}" r="3.4" fill="#185FA5"/>')
s.append(f'<text x="{x26+bw/2-4:.1f}" y="{Y(29.88)-14:.1f}" font-size="11" fill="#0C447C" text-anchor="end">2026Q2 29.88（+37.3%）</text>')
s.append(f'<text x="{X0}" y="{H-30:.1f}" font-size="11" fill="#5F5E5A">读法：2026Q2 的 29.88 亿仍低于 2023Q2(31.55)、2024Q2(33.52)；涨幅来自 2025Q2 的坑，而非绝对水平创新高</text>')
s.append(f'<text x="{X0}" y="{H-14:.1f}" font-size="11" fill="#854F0B">同期交叉验证：2026H1 销售收现 -7.3%、合同负债 -9.3%、存货 42.48 亿（两年 +46%）→ 增长在消耗存量</text>')
s.append('</svg>')
open("data/tmp_600845/out_quarter.svg", "w", encoding="utf-8").write("\n".join(s))
print("bytes:", len("\n".join(s)), "| 2026Q2 y =", round(Y(29.88), 1), "| 2025Q2 y =", round(Y(21.77), 1))
