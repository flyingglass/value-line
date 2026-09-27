# -*- coding: utf-8 -*-
firms = [
    ("泛微网络", 8.486, [("营业成本",0.489,"#85B7EB","#185FA5"), ("销售费用",5.352,"#FAC775","#854F0B"),
                        ("管理费用",0.499,"#9FE1CB","#0F6E56"), ("研发费用",1.429,"#CECBF6","#534AB7")]),
    ("致远互联", 3.665, [("营业成本",1.506,"#85B7EB","#185FA5"), ("销售费用",1.956,"#FAC775","#854F0B"),
                        ("管理费用",0.493,"#9FE1CB","#0F6E56"), ("研发费用",0.962,"#CECBF6","#534AB7")]),
]
W, X0, X1, MAXP = 680, 110, 622, 140.0
sc = (X1 - X0) / MAXP
def px(p): return X0 + p * sc
TOP, BH, GAPB = 60, 46, 30
YB = TOP + 2*BH + GAPB
H = YB + 48
s = [f'<svg viewBox="0 0 {W} {H}" width="100%" role="img" xmlns="http://www.w3.org/2000/svg">',
     '<title>泛微与致远每100元营业收入的成本费用去向</title>',
     '<desc>横向堆积条：泛微成本费用合计占营收91.6%仍有利润空间，致远合计134.2%超出收入34.2%，为其亏损来源。</desc>',
     '<text x="40" y="22" font-size="14" font-weight="500" fill="#2C2C2A">同样收 100 元，成本和费用花掉多少（2026H1）</text>']
for v in [0, 25, 50, 75, 100, 125]:
    dash = ' stroke-dasharray="4 3"' if v == 100 else ''
    w = 0.9 if v == 100 else 0.5
    s.append(f'<line x1="{px(v):.1f}" y1="36" x2="{px(v):.1f}" y2="{YB:.1f}" stroke="#5F5E5A" stroke-width="{w}"{dash}/>')
    s.append(f'<text x="{px(v):.1f}" y="52" font-size="11" fill="#5F5E5A" text-anchor="middle">{v}%</text>')
y = TOP
for name, rev, items in firms:
    total = sum(a for _, a, _, _ in items) / rev * 100
    s.append(f'<text x="102" y="{y+18}" font-size="13" font-weight="500" fill="#2C2C2A" text-anchor="end">{name}</text>')
    s.append(f'<text x="102" y="{y+36}" font-size="11" fill="#5F5E5A" text-anchor="end">合计 {total:.1f}%</text>')
    cum = 0.0
    for label, amt, fill, stroke in items:
        pct = amt / rev * 100
        x0, x1 = px(cum), px(cum + pct)
        s.append(f'<rect x="{x0:.1f}" y="{y}" width="{x1-x0:.1f}" height="{BH}" fill="{fill}" stroke="#FFFFFF" stroke-width="0.6"/>')
        if pct >= 12:
            s.append(f'<text x="{(x0+x1)/2:.1f}" y="{y+BH/2+4:.1f}" font-size="11.5" fill="{stroke}" text-anchor="middle">{pct:.1f}%</text>')
        cum += pct
    if cum <= 100:
        s.append(f'<rect x="{px(cum):.1f}" y="{y}" width="{px(100)-px(cum):.1f}" height="{BH}" fill="#EAF3DE" stroke="#FFFFFF" stroke-width="0.6"/>')
        s.append(f'<text x="{px(100)+8:.1f}" y="{y+22:.1f}" font-size="11.5" fill="#3B6D11">经营利润空间 {100-cum:.1f}%</text>')
        s.append(f'<text x="{px(100)+8:.1f}" y="{y+38:.1f}" font-size="11" fill="#5F5E5A">另有存款利息与投资收益</text>')
    else:
        s.append(f'<rect x="{px(100):.1f}" y="{y}" width="{px(cum)-px(100):.1f}" height="{BH}" fill="#FCEBEB" stroke="#FFFFFF" stroke-width="0.6"/>')
        mx = (px(100) + px(cum)) / 2
        s.append(f'<text x="{mx:.1f}" y="{y+20:.1f}" font-size="11.5" fill="#A32D2D" text-anchor="middle">超支 {cum-100:.1f}%</text>')
        s.append(f'<text x="{mx:.1f}" y="{y+36:.1f}" font-size="11" fill="#A32D2D" text-anchor="middle">必然亏损</text>')
    y += BH + GAPB
lx, ly = 40, H - 20
for label, c, _ in [("营业成本","#85B7EB",0), ("销售费用","#FAC775",0), ("管理费用","#9FE1CB",0), ("研发费用","#CECBF6",0)]:
    s.append(f'<rect x="{lx}" y="{ly-9}" width="10" height="10" fill="{c}" stroke="#888780" stroke-width="0.4"/>')
    s.append(f'<text x="{lx+14}" y="{ly}" font-size="11.5" fill="#444441">{label}</text>')
    lx += 14 + len(label) * 12 + 18
s.append('</svg>')
open('data/tmp_603039/out_peer.svg','w',encoding='utf-8').write("\n".join(s))
print("H =", H, "| 条底:", YB, "| 图例 y:", ly, "| 最右元素:", f"{px(134.2):.0f}")
