# -*- coding: utf-8 -*-
"""泛微网络 2026H1：经营活动现金流出结构 + 「支付其他」拆解
数据来源：603039_2026_中报.pdf 合并现金流量表(p94-95) + 现金流量表项目附注(p172)
          + 销售费用附注(p167) + 应付账款附注(p158) + 预付款项附注(p138)
单位：亿元
"""
W, H = 680, 420
LBL_X, BAR_X, BAR_MAX = 246, 254, 340

def YScale(total, vmax):
    return BAR_MAX / total

s = []
s.append(f'<svg viewBox="0 0 {W} {H}" width="100%" role="img" xmlns="http://www.w3.org/2000/svg">')
s.append('<title>泛微网络 2026 上半年经营活动现金流出结构与「支付其他与经营活动有关的现金」拆解</title>')
s.append('<desc>横向条形图。上半部分为经营活动现金流出 11.46 亿元的四个科目构成；下半部分为其中「支付其他与经营活动有关的现金」7.82 亿元的逐项拆解。数据来自 2026 年半年报原文。</desc>')

s.append('<text x="20" y="18" font-size="12" fill="#2C2C2A">泛微网络 2026H1：经营活动现金流出的钱，去了哪</text>')

def row(y, label, value, pct, width, fill, stroke, note=""):
    s.append(f'<text x="{LBL_X}" y="{y+13}" font-size="11" fill="#444441" text-anchor="end">{label}</text>')
    s.append(f'<rect x="{BAR_X}" y="{y}" width="{max(width,1.5):.1f}" height="18" rx="2" fill="{fill}" stroke="{stroke}" stroke-width="0.8"/>')
    s.append(f'<text x="{BAR_X+width+7:.1f}" y="{y+13}" font-size="11" fill="#2C2C2A">{value}</text>')
    if pct:
        s.append(f'<text x="{BAR_X+width+66:.1f}" y="{y+13}" font-size="11" fill="#888780">{pct}</text>')
    if note:
        s.append(f'<text x="{BAR_X+7:.1f}" y="{y+13}" font-size="11" fill="#5F5E5A">{note}</text>')

# ── 上半：经营活动现金流出 11.46 亿的构成 ──
s.append('<text x="20" y="46" font-size="11.5" fill="#0C447C">① 经营活动现金流出合计 11.46 亿元，由四个科目构成</text>')
k = YScale(11.457, 0)
rows1 = [
    ("支付其他与经营活动有关的现金", 7.820, "68%", "#FAEEDA", "#854F0B"),
    ("支付给职工及为职工支付的现金", 2.146, "19%", "#E6F1FB", "#185FA5"),
    ("支付的各项税费", 0.819, "7%", "#EAF3DE", "#3B6D11"),
    ("购买商品、接受劳务支付的现金", 0.672, "6%", "#EEEDFE", "#534AB7"),
]
for i, (lab, v, pct, f, st) in enumerate(rows1):
    row(58 + i * 32, lab, f"{v:.2f}亿", pct, v * k, f, st)

# ── 下半：7.82 亿的拆解 ──
s.append('<text x="20" y="206" font-size="11.5" fill="#854F0B">② 其中 7.82 亿元「支付其他」再往下拆（金额 / 占比）</text>')
k2 = YScale(7.820, 0)
rows2 = [
    ("当期项目实施费（付给服务商）", 4.624, "59%", "#FAC775", "#854F0B"),
    ("清偿上期应付项目实施费", 1.826, "23%", "#FAEEDA", "#854F0B"),
    ("预付服务商款项净增", 0.553, "7%", "#E6F1FB", "#185FA5"),
    ("其他零星（差旅·办公·推广·押金）", 0.817, "10%", "#D3D1C7", "#5F5E5A"),
]
for i, (lab, v, pct, f, st) in enumerate(rows2):
    row(216 + i * 32, lab, f"{v:.2f}亿", pct, v * k2, f, st)

s.append('<text x="20" y="368" font-size="11" fill="#888780">前三项＝「付给外部服务商的钱」共 7.00 亿元，占该科目 90%（第 2、3 项为推算）</text>')
s.append('<text x="20" y="388" font-size="11" fill="#888780">推算依据：应付项目实施费 5.47→3.64 亿；预付款项 5.39→5.94 亿（半年报附注原文）</text>')
s.append('<text x="20" y="408" font-size="11" fill="#888780">对照：同期「支付给职工」仅 2.15 亿，不足「支付其他」的三分之一</text>')
s.append('</svg>')

svg = "\n".join(s)
open('data/tmp_603039/out_cashflow.svg', 'w', encoding='utf-8').write(svg)
print("bytes:", len(svg))
print("上半合计: 7.820+2.146+0.819+0.672 =", 7.820+2.146+0.819+0.672)
print("下半合计: 4.624+1.826+0.553+0.817 =", 4.624+1.826+0.553+0.817)
for lab, v, _, _, _ in rows1:
    print(f"  {lab}: w={v*k:.1f} → 右边界 {BAR_X+v*k+66:.0f}")
for lab, v, _, _, _ in rows2:
    print(f"  {lab}: w={v*k2:.1f} → 右边界 {BAR_X+v*k2+66:.0f}")
