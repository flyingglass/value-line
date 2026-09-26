import sqlite3, datetime as dt

con = sqlite3.connect('data/688188.db')
cur = con.cursor()
cur.execute("SELECT date, close FROM kline WHERE adj='qfq' ORDER BY date") if False else None
cur.execute("PRAGMA table_info(kline)")
cols = [r[1] for r in cur.fetchall()]
cur.execute("SELECT date, close FROM kline ORDER BY date")
rows = cur.fetchall()

# 月末收盘
bymonth = {}
for d, c in rows:
    ym = d[:7]
    bymonth[ym] = (d, c)
pts = [(dt.date.fromisoformat(d), c) for ym, (d, c) in sorted(bymonth.items())]
print("月点数:", len(pts), pts[0], pts[-1])

# 年度营收
cur.execute("""SELECT substr(report_date,1,4) y, amount FROM income
WHERE item_name='一、营业总收入' AND substr(report_date,5,9)='-12-31' AND substr(report_date,1,4)>='2019'
ORDER BY report_date""")
rev = [(int(y), a/1e8) for y, a in cur.fetchall()]

W, H = 680, 500
ML, MR, MT = 42, 16, 30
PH = 232          # 价格面板高
BH = 96           # 营收面板高
GAP = 34
pw = W - ML - MR
def X(d):  # date -> x
    t0 = dt.date(2019, 3, 1)
    t1 = dt.date(2026, 10, 1)
    return ML + (d - t0).days / (t1 - t0).days * pw

ymin, ymax = 20, 140
def Y(v):
    return MT + PH - (v - ymin) / (ymax - ymin) * PH

bands = [
    (dt.date(2019,8,8),  dt.date(2021,8,27),  "#FCEBEB", "① 双击兑现 19/08-21/08", "#A32D2D"),
    (dt.date(2021,8,27), dt.date(2022,10,28), "#EAF3DE", "② 双左侧 21/08-22/10", "#3B6D11"),
    (dt.date(2022,10,28),dt.date(2023,8,31),  "#FCEBEB", "③ 修复 22/10-23/08", "#A32D2D"),
    (dt.date(2023,8,31), dt.date(2024,9,30),  "#EAF3DE", "④ 业绩涨估值杀 23/08-24/09", "#3B6D11"),
    (dt.date(2024,9,30), dt.date(2026,9,24),  "#FAEEDA", "⑤ de-rating横盘 24/09-今", "#854F0B"),
]
s = []
s.append(f'<svg viewBox="0 0 {W} {H}" width="100%" role="img" xmlns="http://www.w3.org/2000/svg">')
s.append('<title>柏楚电子上市以来股价五阶段与年度营收</title>')
s.append('<desc>上部为2019年8月至2026年9月前复权月收盘价折线，按2444体系分五个阶段着色；下部为2019至2025年度营业收入柱。</desc>')

# 阶段色带 + 顶部标签
for x0d, x1d, fill, label, tc in bands:
    x0, x1 = X(x0d), X(x1d)
    s.append(f'<rect x="{x0:.1f}" y="{MT}" width="{x1-x0:.1f}" height="{PH+BH+GAP+18}" fill="{fill}" opacity="0.55"/>')
    s.append(f'<text x="{(x0+x1)/2:.1f}" y="{MT-13}" font-size="9" fill="{tc}" text-anchor="middle">{label}</text>')
    s.append(f'<line x1="{x0:.1f}" y1="{MT}" x2="{x0:.1f}" y2="{MT+PH+BH+GAP+18}" stroke="#B4B2A9" stroke-width="0.5" stroke-dasharray="3 3"/>')

# y 网格与刻度
for v in range(20, 141, 30):
    s.append(f'<line x1="{ML}" y1="{Y(v):.1f}" x2="{W-MR}" y2="{Y(v):.1f}" stroke="#D3D1C7" stroke-width="0.5"/>')
    s.append(f'<text x="{ML-5}" y="{Y(v)+3:.1f}" font-size="9" fill="#5F5E5A" text-anchor="end">{v}</text>')
s.append(f'<line x1="{ML}" y1="{Y(0):.1f}" x2="{W-MR}" y2="{Y(0):.1f}" stroke="#888780" stroke-width="0.8"/>')

# 价格折线
poly = " ".join(f"{X(d):.1f},{Y(c):.1f}" for d, c in pts)
s.append(f'<polyline points="{poly}" fill="none" stroke="#185FA5" stroke-width="1.3"/>')

# 关键点
marks = [
    (dt.date(2021,8,27), 133.05, "顶 133.05", "start", 0, 12),
    (dt.date(2022,4,29), 55.17,  "底 55.17", "start", 2, -8),
    (dt.date(2023,8,31), 93.55,  "93.55", "middle", 0, -8),
    (dt.date(2024,10,8), 124.43, "924脉冲 124.43", "end", -2, -8),
    (dt.date(2026,9,24), 95.25,  "现 95.25", "end", 2, 12),
]
for d, v, lab, anchor, dx, dy in marks:
    x, y = X(d), Y(v)
    s.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.4" fill="#185FA5"/>')
    s.append(f'<text x="{x+dx:.1f}" y="{y+dy:.1f}" font-size="9" fill="#0C447C" text-anchor="{anchor}">{lab}</text>')

# 营收柱
by0 = MT + PH + GAP + 18
revmax = 22.0
def RY(v): return by0 + BH - v / revmax * BH
s.append(f'<text x="{ML}" y="{by0-6}" font-size="9" fill="#5F5E5A">年度营业收入（亿元）</text>')
prev = None
for y, v in rev:
    xc = X(dt.date(y, 6, 30))
    h = v / revmax * BH
    s.append(f'<rect x="{xc-15:.1f}" y="{by0+BH-h:.1f}" width="30" height="{h:.1f}" fill="#B5D4F4" stroke="#185FA5" stroke-width="0.6"/>')
    s.append(f'<text x="{xc:.1f}" y="{by0+BH-h-3:.1f}" font-size="9" fill="#0C447C" text-anchor="middle">{v:.2f}</text>')
    s.append(f'<text x="{xc:.1f}" y="{by0+BH+11:.1f}" font-size="9" fill="#5F5E5A" text-anchor="middle">{y}</text>')
    if prev:
        s.append(f'<text x="{xc:.1f}" y="{by0+BH+23:.1f}" font-size="8.5" fill="#888780" text-anchor="middle">{(v/prev-1)*100:+.0f}%</text>')
    prev = v
s.append(f'<line x1="{ML}" y1="{by0+BH:.1f}" x2="{W-MR}" y2="{by0+BH:.1f}" stroke="#888780" stroke-width="0.8"/>')
s.append('</svg>')

svg = "\n".join(s)
open('data/tmp_688188/out_stage.svg', 'w', encoding='utf-8').write(svg)
print("bytes:", len(svg))
print(svg)
