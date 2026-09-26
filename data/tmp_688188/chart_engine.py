# -*- coding: utf-8 -*-
"""柏楚电子：逐年收入增量的引擎拆解（2020-2026H1）
数据来源：各年年报「主营业务分产品情况」+ 中报分部信息表（一手 PDF 原文），单位亿元
"""
BLUE, GREEN, PURPLE, GRAY, ORANGE, RED = '#B5D4F4', '#9FE1CB', '#CECBF6', '#B4B2A9', '#FAC775', '#E8A0A0'

groups = [
    ("2020", [("随动系统", 0.558, BLUE), ("板卡系统", 0.590, GREEN), ("总线系统", 0.469, PURPLE), ("其他", 0.331, GRAY)]),
    ("2021", [("随动系统", 0.796, BLUE), ("板卡系统", 0.792, GREEN), ("总线系统", 0.698, PURPLE), ("其他", 1.140, GRAY)]),
    ("2022", [("随动系统", -0.854, BLUE), ("板卡系统", -0.704, GREEN), ("总线系统", 0.006, PURPLE), ("其他", 1.232, GRAY)]),
    ("2023", [("随动系统", -0.443, BLUE), ("板卡系统", 1.545, GREEN), ("总线系统", 1.861, PURPLE), ("切割头+其他", 2.182, ORANGE)]),
    ("2024*", [("平面解决方案", 1.189, BLUE), ("管材解决方案", 1.051, GREEN), ("三维解决方案", 0.296, PURPLE), ("其他", 0.683, RED)]),
    ("2025", [("平面解决方案", 1.681, BLUE), ("管材解决方案", 1.072, GREEN), ("三维解决方案", 0.271, PURPLE), ("其他", 1.463, RED)]),
    ("26H1", [("平面解决方案", 0.297, BLUE), ("管材解决方案", 0.435, GREEN), ("三维解决方案", 0.010, PURPLE), ("其他", 1.007, RED)]),
]

W, H = 680, 464
X0, X1 = 58, 662
YT, YB = 78, 328
VMIN, VMAX = -1.0, 2.55
PW = X1 - X0
SLOT = PW / len(groups)

def X(i): return X0 + SLOT * (i + 0.5)
def Y(v): return YB - (v - VMIN) / (VMAX - VMIN) * (YB - YT)

s = []
s.append(f'<svg viewBox="0 0 {W} {H}" width="100%" role="img" xmlns="http://www.w3.org/2000/svg">')
s.append('<title>柏楚电子逐年收入增量的引擎拆解 2020-2026H1</title>')
s.append('<desc>按年分组柱状图，每组四根柱表示当期各业务线贡献的收入增量（亿元），正值向上、负值向下，组上方标注当期净增量。2024年起披露口径变更。数据来自年报与中报原文。</desc>')

bands = [
    (0, 2, "① 中低功率软件渗透", '#EAF3DE', '#3B6D11'),
    (2, 4, "② 高功率总线 + 智能切割头", '#FAEEDA', '#854F0B'),
    (4, 6, "③ 软硬一体化 + 管材", '#E6F1FB', '#0C447C'),
    (6, 7, "④ 智能焊接 / 微加工", '#FCEBEB', '#A32D2D'),
]
for i0, i1, label, fill, tc in bands:
    xa = X0 + SLOT * i0 + 3
    xb = X0 + SLOT * i1 - 3
    s.append(f'<rect x="{xa:.1f}" y="28" width="{xb-xa:.1f}" height="20" rx="4" fill="{fill}"/>')
    s.append(f'<text x="{(xa+xb)/2:.1f}" y="42.5" font-size="11" fill="{tc}" text-anchor="middle">{label}</text>')

s.append('<text x="58" y="16" font-size="11.5" fill="#2C2C2A">逐年收入增量由谁贡献（亿元，向上＝拉动 / 向下＝拖累）</text>')

for v in [-1, 0, 1, 2]:
    yy = Y(v)
    w = 1.0 if v == 0 else 0.5
    col = '#888780' if v == 0 else '#D3D1C7'
    s.append(f'<line x1="{X0}" y1="{yy:.1f}" x2="{X1}" y2="{yy:.1f}" stroke="{col}" stroke-width="{w}"/>')
    s.append(f'<text x="{X0-6}" y="{yy+4:.1f}" font-size="11" fill="#5F5E5A" text-anchor="end">{v:+d}</text>')

BW, GAPW = 14.0, 3.0
for i, (name, items) in enumerate(groups):
    n = len(items)
    total_w = n * BW + (n - 1) * GAPW
    x_start = X(i) - total_w / 2
    y0 = Y(0)
    vals = [v for _, v, _ in items]
    top_pos = max(range(n), key=lambda k: vals[k])
    for j, (label, val, color) in enumerate(items):
        x = x_start + j * (BW + GAPW)
        yy = Y(val)
        if val >= 0:
            top, h = yy, y0 - yy
        else:
            top, h = y0, yy - y0
        stroke = '#185FA5' if (j == top_pos and val > 0.5) else '#FFFFFF'
        sw = 1.1 if (j == top_pos and val > 0.5) else 0.5
        s.append(f'<rect x="{x:.1f}" y="{top:.1f}" width="{BW:.1f}" height="{max(h,1.0):.1f}" fill="{color}" stroke="{stroke}" stroke-width="{sw}"/>')
    tot = sum(vals)
    tc = '#185FA5' if tot > 0 else '#A32D2D'
    s.append(f'<text x="{X(i):.1f}" y="66" font-size="11.5" font-weight="500" fill="{tc}" text-anchor="middle">净 {tot:+.2f}</text>')
    s.append(f'<text x="{X(i):.1f}" y="{YB+18:.1f}" font-size="11" fill="#5F5E5A" text-anchor="middle">{name}</text>')

xd = X0 + SLOT * 4
s.append(f'<line x1="{xd:.1f}" y1="24" x2="{xd:.1f}" y2="{YB+24:.1f}" stroke="#888780" stroke-width="0.8" stroke-dasharray="4 3"/>')
s.append(f'<text x="{xd:.1f}" y="364" font-size="11" fill="#854F0B" text-anchor="middle">披露口径变更：切割头并入三大解决方案</text>')
s.append('<text x="58" y="382" font-size="11" fill="#5F5E5A">深色描边＝当年最大贡献引擎；2023「切割头＋其他」为口径重分类后的合计增量</text>')

def legend(x, y, items):
    cx = x
    for label, c in items:
        s.append(f'<rect x="{cx:.1f}" y="{y-9}" width="10" height="10" fill="{c}" stroke="#888780" stroke-width="0.5"/>')
        s.append(f'<text x="{cx+14:.1f}" y="{y:.1f}" font-size="11" fill="#444441">{label}</text>')
        n_ch = sum(2 if ord(ch) > 127 else 1 for ch in label)
        cx += 14 + n_ch * 5.9 + 16

s.append(f'<text x="58" y="404" font-size="11" fill="#5F5E5A">2019-2023：</text>')
legend(140, 404, [('随动/平板', BLUE), ('板卡', GREEN), ('总线', PURPLE), ('切割头', ORANGE), ('其他', GRAY)])
s.append(f'<text x="58" y="428" font-size="11" fill="#5F5E5A">2024-  ：</text>')
legend(140, 428, [('平面解决方案', BLUE), ('管材解决方案', GREEN), ('三维解决方案', PURPLE), ('其他＝焊接·微加工', RED)])
s.append(f'<text x="58" y="452" font-size="11" fill="#888780">* 2024 增量基数＝2023 重述口径（按 2024 年报四类同比反推，合计 13.96 亿）；26H1＝26H1 vs 25H1</text>')
s.append('</svg>')

svg = "\n".join(s)
open('data/tmp_688188/out_engine.svg', 'w', encoding='utf-8').write(svg)
print("bytes:", len(svg))
for name, items in groups:
    tot = sum(v for _, v, _ in items)
    top = max(items, key=lambda t: t[1])
    print(f"{name}: 净 {tot:+.3f} | 头号引擎 {top[0]} {top[1]:+.3f} | " + " ".join(f"{l}{v:+.3f}" for l, v, _ in items))
