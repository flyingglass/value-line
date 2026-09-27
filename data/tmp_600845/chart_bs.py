# -*- coding: utf-8 -*-
"""宝信软件 2026 中报：分部毛利率同比 + 合同负债蓄水池"""

# ---------- 图1：分部毛利率哑铃图 ----------
seg = [
    ("软件开发及工程服务 67.9%", 29.6936, 23.6994, "38.17 亿"),
    ("服务外包 31.6%", 44.7596, 42.9656, "17.76 亿"),
    ("系统集成 0.5%", 6.8576, 10.9377, "0.30 亿"),
    ("主营业务合计", 34.9142, 29.7186, "56.23 亿"),
]
W, H = 680, 322
X0, X1, MAXG = 130.0, 500.0, 50.0
sc = (X1 - X0) / MAXG
def gx(g): return X0 + g * sc
rows = [96, 142, 188, 234]

s = [f'<svg viewBox="0 0 {W} {H}" width="100%" role="img" xmlns="http://www.w3.org/2000/svg">']
s.append('<title>宝信软件2026年上半年分部毛利率同比变化</title>')
s.append('<desc>哑铃图展示四个分部2025年与2026年上半年毛利率对比：软件开发及工程服务29.70%降至23.70%，服务外包44.76%降至42.97%，系统集成6.86%升至10.94%，主营业务合计34.91%降至29.72%。</desc>')
s.append('<text x="40" y="22" font-size="14" font-weight="500" fill="#2C2C2A">毛利率掉在哪一块（2025H1 对比 2026H1）</text>')
s.append('<text x="40" y="42" font-size="12" fill="#5F5E5A">横轴为分部毛利率，右侧为 2026H1 收入体量</text>')
for g in range(0, 51, 10):
    x = gx(g)
    s.append(f'<line x1="{x:.1f}" y1="70" x2="{x:.1f}" y2="254" stroke="#D3D1C7" stroke-width="0.5"/>')
    s.append(f'<text x="{x:.1f}" y="64" font-size="11" fill="#888780" text-anchor="middle">{g}%</text>')
for (name, g25, g26, rev), y in zip(seg, rows):
    s.append(f'<text x="120" y="{y+4}" font-size="12.5" fill="#2C2C2A" text-anchor="end">{name}</text>')
    x25, x26 = gx(g25), gx(g26)
    s.append(f'<line x1="{x25:.1f}" y1="{y}" x2="{x26:.1f}" y2="{y}" stroke="#B4B2A9" stroke-width="2"/>')
    s.append(f'<circle cx="{x25:.1f}" cy="{y}" r="5" fill="#F1EFE8" stroke="#888780" stroke-width="1.2"/>')
    s.append(f'<circle cx="{x26:.1f}" cy="{y}" r="5.5" fill="#378ADD" stroke="#185FA5" stroke-width="1"/>')
    s.append(f'<text x="{x26-9:.1f}" y="{y+22}" font-size="11.5" fill="#0C447C" text-anchor="end">{g26:.2f}%</text>')
    s.append(f'<text x="{x25+9:.1f}" y="{y+22}" font-size="11.5" fill="#5F5E5A">{g25:.2f}%</text>')
    d = g26 - g25
    dc = "#A32D2D" if d < 0 else "#3B6D11"
    s.append(f'<text x="520" y="{y-3}" font-size="12" fill="{dc}">{d:+.2f}pct</text>')
    s.append(f'<text x="520" y="{y+15}" font-size="11.5" fill="#888780">{rev}</text>')
s.append('<line x1="40" y1="268" x2="640" y2="268" stroke="#D3D1C7" stroke-width="0.5"/>')
s.append('<circle cx="46" cy="286" r="5" fill="#F1EFE8" stroke="#888780" stroke-width="1.2"/>')
s.append('<text x="58" y="290" font-size="11.5" fill="#5F5E5A">2025H1</text>')
s.append('<circle cx="130" cy="286" r="5.5" fill="#378ADD" stroke="#185FA5" stroke-width="1"/>')
s.append('<text x="142" y="290" font-size="11.5" fill="#5F5E5A">2026H1</text>')
s.append('<text x="40" y="312" font-size="11.5" fill="#888780">毛利率按（收入−成本）÷收入自算；2025H1 数据取自 2025 年半年报同表</text>')
s.append('</svg>')
open('data/tmp_600845/out_gm.svg', 'w', encoding='utf-8').write("\n".join(s))

# ---------- 图2：合同负债蓄水池 ----------
tank = [("2025年上半年", 15.82, 11.13, 26.88, 31.58, 4.70), ("2026年上半年", 11.02, 14.67, 32.30, 28.65, -3.65)]
W2, H2 = 680, 440
BASE, SC = 310.0, 10.0
def by(v): return BASE - v * SC
s2 = [f'<svg viewBox="0 0 {W2} {H2}" width="100%" role="img" xmlns="http://www.w3.org/2000/svg">']
s2.append('<title>宝信软件合同负债蓄水池的进水与出水</title>')
s2.append('<desc>柱状对比：2025年上半年新增预收15.82亿元、结转收入11.13亿元，池子净增4.70亿元；2026年上半年新增预收降至11.02亿元、结转升至14.67亿元，池子净减3.65亿元。</desc>')
s2.append('<text x="40" y="22" font-size="14" font-weight="500" fill="#2C2C2A">合同负债这个蓄水池：去年进水多、今年出水多</text>')
s2.append('<text x="40" y="42" font-size="12" fill="#5F5E5A">单位：亿元。进水＝本期新收到的预收款，出水＝本期转成收入的预收款</text>')
for v in range(0, 21, 5):
    y = by(v)
    s2.append(f'<line x1="100" y1="{y:.1f}" x2="600" y2="{y:.1f}" stroke="#D3D1C7" stroke-width="0.5"/>')
    s2.append(f'<text x="92" y="{y+4:.1f}" font-size="11" fill="#888780" text-anchor="end">{v}</text>')
groups = [(220.0, 142.0, 228.0), (460.0, 382.0, 468.0)]
BW = 70.0
for (label, inflow, outflow, beg, end, net), (cx, xa, xb) in zip(tank, groups):
    ha, hb = inflow * SC, outflow * SC
    s2.append(f'<rect x="{xa:.1f}" y="{by(inflow):.1f}" width="{BW}" height="{ha:.1f}" fill="#B5D4F4" stroke="#185FA5" stroke-width="0.5"/>')
    s2.append(f'<rect x="{xb:.1f}" y="{by(outflow):.1f}" width="{BW}" height="{hb:.1f}" fill="#FAC775" stroke="#BA7517" stroke-width="0.5"/>')
    s2.append(f'<text x="{xa+BW/2:.1f}" y="{by(inflow)-7:.1f}" font-size="12.5" fill="#0C447C" text-anchor="middle">{inflow:.2f}</text>')
    s2.append(f'<text x="{xb+BW/2:.1f}" y="{by(outflow)-7:.1f}" font-size="12.5" fill="#854F0B" text-anchor="middle">{outflow:.2f}</text>')
    s2.append(f'<text x="{cx:.1f}" y="{BASE+20:.1f}" font-size="13" font-weight="500" fill="#2C2C2A" text-anchor="middle">{label}</text>')
    nc = "#3B6D11" if net > 0 else "#A32D2D"
    s2.append(f'<text x="{cx:.1f}" y="{BASE+42:.1f}" font-size="12.5" fill="{nc}" text-anchor="middle">池子净变化 {net:+.2f} 亿</text>')
    s2.append(f'<text x="{cx:.1f}" y="{BASE+60:.1f}" font-size="11.5" fill="#888780" text-anchor="middle">期初 {beg:.2f} → 期末 {end:.2f}</text>')
s2.append(f'<line x1="100" y1="{BASE:.1f}" x2="600" y2="{BASE:.1f}" stroke="#5F5E5A" stroke-width="0.8"/>')
s2.append('<rect x="40" y="396" width="12" height="12" fill="#B5D4F4" stroke="#185FA5" stroke-width="0.5"/>')
s2.append('<text x="58" y="406" font-size="11.5" fill="#5F5E5A">本期新增预收（推算）</text>')
s2.append('<rect x="216" y="396" width="12" height="12" fill="#FAC775" stroke="#BA7517" stroke-width="0.5"/>')
s2.append('<text x="234" y="406" font-size="11.5" fill="#5F5E5A">从期初合同负债结转成收入</text>')
s2.append('<text x="40" y="430" font-size="11.5" fill="#888780">新增预收＝期末余额−期初余额＋本期结转，属推算；余额取自两期资产负债表，结转额取自各期附注</text>')
s2.append('</svg>')
open('data/tmp_600845/out_tank.svg', 'w', encoding='utf-8').write("\n".join(s2))

print("gm bytes:", len("\n".join(s)))
print("tank bytes:", len("\n".join(s2)))
print("图1 右侧文字最右:", 520 + 8 * 6.5)
print("图2 柱最右:", max(x for _, _, x in groups) + BW)
