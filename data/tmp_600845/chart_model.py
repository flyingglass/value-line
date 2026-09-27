# -*- coding: utf-8 -*-
"""宝信「一次统建 + 长期续费」两段式客户模型验证图
上：项目制（波浪）vs 服务外包（单调上行）
下：服务外包同比增速（累积速度放缓）
数据源：2019-2025 各年报「主营业务分产品情况」一手原文
"""
YR = [2019, 2020, 2021, 2022, 2023, 2024, 2025]
PROJ = [45.70, 67.18, 85.02, 95.90, 93.22, 99.11, 71.64]   # 软件开发及工程服务
OUTS = [20.55, 26.16, 31.21, 34.10, 34.91, 36.56, 37.65]   # 服务外包
GRW  = [19.36, 27.31, 8.87, 9.27, 2.37, 4.73, 2.98]        # 服务外包同比

BLUE, GREEN = "#185FA5", "#0F6E56"
GRID, AXIS, TXT, MUTE = "#D3D1C7", "#888780", "#2C2C2A", "#5F5E5A"

W, H = 680, 410
X0, X1 = 62, 660
MT, PH = 52, 168          # 面板 A
BT, BH = 288, 66          # 面板 B
pw = X1 - X0
step = pw / (len(YR) - 1)
def X(i): return X0 + i * step
AMAX = 110.0
def Y(v): return MT + PH - v / AMAX * PH
BMAX = 32.0
def BY(v): return BT + BH - v / BMAX * BH

s = [f'<svg viewBox="0 0 {W} {H}" width="100%" role="img" xmlns="http://www.w3.org/2000/svg">',
     '<title>宝信软件：项目制收入与服务外包收入的七年形态对比</title>',
     '<desc>上半部分为两条收入折线：软件开发及工程服务呈波浪形大幅波动，服务外包自2019年至2025年单调递增从未下降。下半部分为服务外包同比增速柱，从2019年19.4%、2020年27.3%持续收窄至2025年3.0%。</desc>',
     f'<text x="18" y="20" font-size="14" font-weight="500" fill="{TXT}">同一个客户池，两种收入：项目制在坐过山车，服务外包只上不下（亿元）</text>']

# ---------- 面板 A ----------
for v in range(0, 111, 25):
    s.append(f'<line x1="{X0}" y1="{Y(v):.1f}" x2="{X1}" y2="{Y(v):.1f}" stroke="{GRID}" stroke-width="0.5"/>')
    s.append(f'<text x="{X0-6}" y="{Y(v)+4:.1f}" font-size="11" fill="{MUTE}" text-anchor="end">{v}</text>')
s.append(f'<line x1="{X0}" y1="{Y(0):.1f}" x2="{X1}" y2="{Y(0):.1f}" stroke="{AXIS}" stroke-width="0.8"/>')

poly_p = " ".join(f"{X(i):.1f},{Y(v):.1f}" for i, v in enumerate(PROJ))
poly_o = " ".join(f"{X(i):.1f},{Y(v):.1f}" for i, v in enumerate(OUTS))
s.append(f'<polyline points="{poly_p}" fill="none" stroke="{BLUE}" stroke-width="1.6"/>')
s.append(f'<polyline points="{poly_o}" fill="none" stroke="{GREEN}" stroke-width="1.6"/>')
for i, v in enumerate(PROJ):
    s.append(f'<circle cx="{X(i):.1f}" cy="{Y(v):.1f}" r="2.4" fill="{BLUE}"/>')
for i, v in enumerate(OUTS):
    s.append(f'<circle cx="{X(i):.1f}" cy="{Y(v):.1f}" r="2.4" fill="{GREEN}"/>')

s.append(f'<text x="{X(0)+6:.1f}" y="{Y(45.70)+16:.1f}" font-size="11" fill="{BLUE}">软件开发及工程服务（项目制）</text>')
s.append(f'<text x="{X(1)+2:.1f}" y="{Y(26.16)+16:.1f}" font-size="11" fill="{GREEN}">服务外包（运维＋云＋IDC）</text>')
s.append(f'<text x="{X(6):.1f}" y="{Y(71.64)+16:.1f}" font-size="11" fill="{BLUE}" text-anchor="end">2025 年 71.64（-27.7%）</text>')
s.append(f'<text x="{X(6):.1f}" y="{Y(37.65)+15:.1f}" font-size="11" fill="{GREEN}" text-anchor="end">2025 年 37.65（+3.0%）</text>')
s.append(f'<text x="{X(4):.1f}" y="{Y(93.22)-20:.1f}" font-size="11" fill="{BLUE}" text-anchor="middle">2022-2024 平台 93-99 亿</text>')

# x 轴年份
for i, y in enumerate(YR):
    s.append(f'<line x1="{X(i):.1f}" y1="{Y(0):.1f}" x2="{X(i):.1f}" y2="{Y(0)+4:.1f}" stroke="{AXIS}" stroke-width="0.6"/>')
    s.append(f'<text x="{X(i):.1f}" y="{Y(0)+17:.1f}" font-size="11" fill="{MUTE}" text-anchor="middle">{y}</text>')

# ---------- 面板 B ----------
s.append(f'<text x="18" y="{BT-10}" font-size="12" font-weight="500" fill="{TXT}">服务外包同比增速（%）——「续费年金」的累积速度在放缓</text>')
for v in range(0, 31, 10):
    s.append(f'<line x1="{X0}" y1="{BY(v):.1f}" x2="{X1}" y2="{BY(v):.1f}" stroke="{GRID}" stroke-width="0.5"/>')
    s.append(f'<text x="{X0-6}" y="{BY(v)+4:.1f}" font-size="11" fill="{MUTE}" text-anchor="end">{v}</text>')
s.append(f'<line x1="{X0}" y1="{BY(0):.1f}" x2="{X1}" y2="{BY(0):.1f}" stroke="{AXIS}" stroke-width="0.8"/>')
bw = 34
for i, v in enumerate(GRW):
    h = v / BMAX * BH
    s.append(f'<rect x="{X(i)-bw/2:.1f}" y="{BY(v):.1f}" width="{bw}" height="{h:.1f}" fill="#9FE1CB" stroke="{GREEN}" stroke-width="0.7"/>')
    s.append(f'<text x="{X(i):.1f}" y="{BY(v)-5:.1f}" font-size="11" fill="{GREEN}" text-anchor="middle">{v:.1f}</text>')
for i, y in enumerate(YR):
    s.append(f'<text x="{X(i):.1f}" y="{BT+BH+17:.1f}" font-size="11" fill="{MUTE}" text-anchor="middle">{y}</text>')

s.append(f'<text x="18" y="{H-19}" font-size="11" fill="{MUTE}">口径：各年报「主营业务分产品情况」原生科目。服务外包含运维、云计算运营与 IDC 运营三项，非纯运维费</text>')
s.append(f'<text x="18" y="{H-6}" font-size="11" fill="{MUTE}">2019-2025 服务外包七年单调递增（20.6 → 37.7 亿），项目制同期两次负增长；两者比值 0.45 → 0.53</text>')
s.append('</svg>')
open('data/tmp_600845/out_model.svg', 'w', encoding='utf-8').write("\n".join(s))
print("bytes:", len("\n".join(s)))
print("服务外包 7 年:", OUTS, "单调递增:", all(OUTS[i] < OUTS[i+1] for i in range(len(OUTS)-1)))
print("项目制 CAGR 2019->2025: %.2f%%" % (((PROJ[-1]/PROJ[0])**(1/6)-1)*100))
print("服务外包 CAGR 2019->2025: %.2f%%" % (((OUTS[-1]/OUTS[0])**(1/6)-1)*100))
print("服务外包/项目制 比值: 2019 %.3f -> 2025 %.3f" % (OUTS[0]/PROJ[0], OUTS[-1]/PROJ[-1]))
print("项目制 2025 回落: %.1f%%  服务外包 2025: %+.1f%%" % ((PROJ[-1]/PROJ[-2]-1)*100, (OUTS[-1]/OUTS[-2]-1)*100))
