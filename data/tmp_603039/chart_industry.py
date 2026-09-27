# -*- coding: utf-8 -*-
tiers = [
    ("互联网平台型（SaaS）", "钉钉 · 企业微信 · 飞书 · 金山WPS",
     "免费/低价获客，正从中小往大客户渗透", "#E6F1FB", "#85B7EB", "#0C447C", "#185FA5"),
    ("传统产品主导型（泛微所在层）", "泛微 · 致远互联 · 蓝凌（钉钉系）",
     "央国企＋信创大单，重本地化实施", "#FAEEDA", "#EF9F27", "#633806", "#854F0B"),
    ("ERP 生态捆绑型", "用友（友空间）· 金蝶（云之家）",
     "随 ERP 一起卖，独立获客弱", "#E1F5EE", "#5DCAA5", "#085041", "#0F6E56"),
    ("项目定制 / 区域小厂", "慧点科技（东软系）· 万户 · 华天动力 · 九思",
     "单个项目收费高、规模化低，被逐步出清", "#F1EFE8", "#B4B2A9", "#2C2C2A", "#5F5E5A"),
]
W = 680
TOP = 34
TH, GAP = 74, 14
H = TOP + len(tiers)*TH + (len(tiers)-1)*GAP + 46
s = [f'<svg viewBox="0 0 {W} {H}" width="100%" role="img" xmlns="http://www.w3.org/2000/svg">',
     '<title>中国协同管理软件行业玩家分层</title>',
     '<desc>四层结构：互联网平台型SaaS、传统产品主导型、ERP生态捆绑型、项目定制与区域小厂。</desc>',
     f'<text x="40" y="18" font-size="14" font-weight="500" fill="#2C2C2A">协同管理软件行业的四层玩家</text>']
y = TOP
for name, vendors, feat, fill, stroke, tcol, scol in tiers:
    s.append(f'<rect x="40" y="{y}" width="{W-80}" height="{TH}" rx="10" fill="{fill}" stroke="{stroke}" stroke-width="0.5"/>')
    s.append(f'<rect x="40" y="{y}" width="4" height="{TH}" rx="2" fill="{scol}"/>')
    s.append(f'<text x="60" y="{y+26}" font-size="14" font-weight="500" fill="{tcol}">{name}</text>')
    s.append(f'<text x="60" y="{y+48}" font-size="12.5" fill="#2C2C2A">{vendors}</text>')
    s.append(f'<text x="60" y="{y+66}" font-size="11.5" fill="#5F5E5A">{feat}</text>')
    y += TH + GAP
s.append(f'<text x="40" y="{H-22}" font-size="11.5" fill="#888780">分层依据：中报三分法（产品主导型／项目定制型／SaaS服务型）＋收入量级与获客路径</text>')
s.append('</svg>')
open('data/tmp_603039/out_industry.svg','w',encoding='utf-8').write("\n".join(s))
print("H =", H, "bytes:", len("\n".join(s)))
