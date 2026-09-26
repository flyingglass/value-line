# 营收结构变化堆叠柱（2019-2023 老口径 / 2024-2026H1 新口径）
old = [
    ('2019', {'随动系统':1.6460,'板卡系统':1.5137,'总线系统':0.2375,'其他':0.3635}),
    ('2020', {'随动系统':2.2035,'板卡系统':2.1035,'总线系统':0.7068,'其他':0.6945}),
    ('2021', {'随动系统':2.9996,'板卡系统':2.8957,'总线系统':1.4049,'其他':1.8342}),
    ('2022', {'随动系统':2.1456,'板卡系统':2.1918,'总线系统':1.4106,'其他':3.0661}),
    ('2023', {'随动系统':1.7030,'板卡系统':3.7365,'总线系统':3.2715,'切割头':3.3464,'其他':1.9015}),
]
new = [
    ('2024', {'平面解决方案':11.2481,'管材解决方案':3.8023,'三维解决方案':0.3678,'其他':1.7605}),
    ('2025', {'平面解决方案':12.9291,'管材解决方案':4.8745,'三维解决方案':0.6389,'其他':3.2239}),
    ('25H1', {'平面解决方案':6.7711,'管材解决方案':2.3650,'三维解决方案':0.3437,'其他':1.5550}),
    ('26H1', {'平面解决方案':7.0683,'管材解决方案':2.7985,'三维解决方案':0.3538,'其他':2.5619}),
]
C = {'随动系统':'#B5D4F4','板卡系统':'#9FE1CB','总线系统':'#CECBF6','切割头':'#FAC775','其他':'#B4B2A9',
     '平面解决方案':'#B5D4F4','管材解决方案':'#9FE1CB','三维解决方案':'#CECBF6'}
W, H = 680, 430
BT, BH = 40, 292
ymax = 22.0
def Y(v): return BT + BH - v / ymax * BH
s = [f'<svg viewBox="0 0 {W} {H}" width="100%" role="img" xmlns="http://www.w3.org/2000/svg">',
     '<title>柏楚电子营收结构变化 2019-2026H1</title>',
     '<desc>堆叠柱状图：2019至2023年按产品（随动/板卡/总线/切割头/其他），2024年起按解决方案（平面/管材/三维/其他）披露。</desc>']
# 网格
for v in range(0, 23, 5):
    s.append(f'<line x1="46" y1="{Y(v):.1f}" x2="664" y2="{Y(v):.1f}" stroke="#D3D1C7" stroke-width="0.5"/>')
    s.append(f'<text x="41" y="{Y(v)+3:.1f}" font-size="9" fill="#5F5E5A" text-anchor="end">{v}</text>')
s.append(f'<text x="46" y="24" font-size="9" fill="#5F5E5A">营业收入（亿元）</text>')
s.append('<text x="46" y="12" font-size="10" fill="#2C2C2A">2019-2023 按产品口径</text>')
s.append('<text x="392" y="12" font-size="10" fill="#2C2C2A">2024-2026H1 按解决方案口径</text>')
s.append('<line x1="374" y1="20" x2="374" y2="392" stroke="#888780" stroke-width="0.6" stroke-dasharray="4 3"/>')
s.append('<text x="374" y="404" font-size="9" fill="#854F0B" text-anchor="middle">2024 起披露口径变更：切割头并入各解决方案线</text>')

def bar(cx, name, d, bw):
    y = BT + BH
    for k, v in d.items():
        h = v / ymax * BH
        y -= h
        s.append(f'<rect x="{cx-bw/2:.1f}" y="{y:.1f}" width="{bw}" height="{h:.1f}" fill="{C[k]}" stroke="#FFFFFF" stroke-width="0.6"/>')
    s.append(f'<text x="{cx:.1f}" y="{y-4:.1f}" font-size="9" fill="#444441" text-anchor="middle">{sum(d.values()):.2f}</text>')
    s.append(f'<text x="{cx:.1f}" y="{BT+BH+12:.1f}" font-size="9.5" fill="#5F5E5A" text-anchor="middle">{name}</text>')

for i, (name, d) in enumerate(old):
    bar(72 + i * 60, name, d, 40)
for i, (name, d) in enumerate(new):
    bar(432 + i * 62, name, d, 44)

# 图例（两组分开，避免歧义）
def legend(x0, y0, items):
    x = x0
    for label, c in items:
        s.append(f'<rect x="{x}" y="{y0-7}" width="9" height="9" fill="{c}" stroke="#888780" stroke-width="0.4"/>')
        s.append(f'<text x="{x+12}" y="{y0+1}" font-size="9" fill="#444441">{label}</text>')
        x += 12 + len(label) * 8.4 + 10

legend(46, 372, [('随动系统', C['随动系统']), ('板卡系统', C['板卡系统']), ('总线系统', C['总线系统'])])
legend(46, 388, [('切割头（23 年单独拆出）', C['切割头']), ('其他', C['其他'])])
legend(392, 372, [('平面解决方案', C['平面解决方案']), ('管材解决方案', C['管材解决方案'])])
legend(392, 388, [('三维解决方案', C['三维解决方案']), ('其他（含智能切割头等硬件）', C['其他'])])
s.append('</svg>')
svg = "\n".join(s)
open('data/tmp_688188/out_mix.svg', 'w', encoding='utf-8').write(svg)
print("bytes:", len(svg))
