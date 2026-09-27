# -*- coding: utf-8 -*-
"""图2：宝武系各集团在宝信的收入生命周期（小倍数图）｜单位亿元 2018-2025"""
YR = [2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025]
DATA = [
    ("马钢系",   [None, 0.06, 0.81, 12.43, 9.79, 6.73, 4.72, 2.67], "2021"),
    ("太钢系",   [None, None, 0.18, 0.52, 6.04, 7.44, 2.13, 1.94], "2023"),
    ("昆钢系",   [None, None, None, 0.23, 3.55, 2.01, 1.99, 0.74], "2022"),
    ("湛江钢铁", [1.54, 2.60, 4.23, 6.90, 4.30, 3.03, 2.09, 2.22], "2021"),
    ("武钢系",   [3.32, 5.75, 5.85, 4.52, 6.35, 7.35, 9.10, 5.07], "2024"),
    ("梅山系",   [2.58, 2.41, 2.75, 4.52, 4.85, 4.90, 5.52, 2.03], "2024"),
    ("欧冶系",   [0.33, 0.47, 0.72, 3.46, 6.42, 5.53, 4.02, 3.72], "2022"),
    ("山钢系",   [None, None, None, None, 0.21, 0.72, 0.24, 4.57], "2025 上升中"),
]
W, H = 680, 334
LEFT, TOP, CW, CH = 18, 44, 163, 128
s = [f'<svg viewBox="0 0 {W} {H}" width="100%" role="img" xmlns="http://www.w3.org/2000/svg">',
     '<title>宝武系各集团在宝信软件的收入生命周期</title>',
     '<desc>八个小图各自显示一个宝武系集团在宝信的收入：均为集团重组或新基地投产后一至三年冲到峰值、随后大幅回落，峰值位置各不相同。</desc>',
     f'<text x="18" y="19" font-size="14" font-weight="500" fill="#2C2C2A">宝武系各集团在宝信的收入：一律「冲高—回落」，只是峰值年份不同（亿元）</text>']
for k, (name, vals, pk) in enumerate(DATA):
    row, col = k // 4, k % 4
    cx, cy = LEFT + col * CW, TOP + row * CH
    gx, gy, GW, GH = cx + 3, cy + 34, CW - 26, 66
    clean = [v for v in vals if v is not None]
    mx = max(clean) * 1.15
    def PX(i): return gx + GW * i / (len(YR) - 1)
    def PY(v): return gy + GH - v / mx * GH
    s.append(f'<text x="{cx}" y="{cy+12}" font-size="12" font-weight="500" fill="#2C2C2A">{name}</text>')
    s.append(f'<text x="{cx}" y="{cy+26}" font-size="11" fill="#A32D2D">峰 {max(clean):.2f} 亿 · {pk}</text>')
    s.append(f'<line x1="{gx}" y1="{gy+GH}" x2="{gx+GW}" y2="{gy+GH}" stroke="#B4B2A9" stroke-width="0.6"/>')
    s.append(f'<line x1="{gx}" y1="{gy}" x2="{gx}" y2="{gy+GH}" stroke="#B4B2A9" stroke-width="0.6"/>')
    seg, cur = [], []
    for i, v in enumerate(vals):
        if v is None:
            if len(cur) > 1: seg.append(cur)
            cur = []
        else:
            cur.append((PX(i), PY(v)))
    if len(cur) > 1: seg.append(cur)
    for sg in seg:
        s.append('<polyline points="' + " ".join(f"{a:.1f},{b:.1f}" for a, b in sg) + '" fill="none" stroke="#185FA5" stroke-width="1.3"/>')
    for i, v in enumerate(vals):
        if v is None: continue
        is_pk = abs(v - max(clean)) < 1e-9
        s.append(f'<circle cx="{PX(i):.1f}" cy="{PY(v):.1f}" r="{3.3 if is_pk else 2.2}" fill="{"#A32D2D" if is_pk else "#185FA5"}"/>')
    s.append(f'<text x="{gx}" y="{gy+GH+14}" font-size="11" fill="#888780">2018</text>')
    s.append(f'<text x="{gx+GW}" y="{gy+GH+14}" font-size="11" fill="#888780" text-anchor="end">2025</text>')
s.append(f'<text x="18" y="{H-6}" font-size="11" fill="#888780">口径：各年年报附注「关联方出售商品/提供劳务」，同一集团下多家子公司已合并。红点＝该集团峰值年；山钢系为近年新重组、仍在上升段</text>')
s.append('</svg>')
open("data/tmp_600845/out_life.svg", "w", encoding="utf-8").write("\n".join(s))
print("bytes:", len("\n".join(s)), "| H =", H, "| 末行底部 =", TOP + CH + 24 + GH + 14)
