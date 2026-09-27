# -*- coding: utf-8 -*-
"""宝信软件 600845 · 2444 视角位置图：月收盘（前复权）+ 阶段底色 + 顶底与事件点"""
import sqlite3, datetime as dt

c = sqlite3.connect("data/db/600845.db")
mon = c.execute("""
  SELECT date, close FROM kline
  WHERE date IN (SELECT MAX(date) FROM kline GROUP BY substr(date,1,7))
    AND date >= '2022-06-01' ORDER BY date
""").fetchall()
pts = [(dt.date.fromisoformat(d), float(v)) for d, v in mon]

W, H = 680, 436
ML, MR, MT, PH = 52, 18, 60, 250
X0, X1 = ML, W - MR
t0, t1 = pts[0][0], pts[-1][0]
def X(d): return X0 + (d - t0).days / (t1 - t0).days * (X1 - X0)
LO, HI = 14.0, 46.0
def Y(v): return MT + PH - (v - LO) / (HI - LO) * PH

# 阶段底色
bands = [
    (dt.date(2022, 6, 1),  dt.date(2023, 6, 20), "#F1EFE8", "① 预期定价：业绩平、股价冲顶"),
    (dt.date(2023, 6, 20), dt.date(2024, 12, 31), "#FAEEDA", "② 高位震荡：业绩见顶、估值先杀"),
    (dt.date(2024, 12, 31), dt.date(2026, 6, 29), "#FCEBEB", "③ 杀业绩：营收 -19.6% / 扣非 -42%"),
    (dt.date(2026, 6, 29), dt.date(2026, 9, 24), "#EAF3DE", "④ 低位待确认"),
]
s = [f'<svg viewBox="0 0 {W} {H}" width="100%" role="img" xmlns="http://www.w3.org/2000/svg">',
     '<title>宝信软件月收盘价与2444阶段划分（2022-06 至 2026-09）</title>',
     '<desc>前复权月收盘折线，按预期定价、高位震荡、杀业绩、低位待确认四个阶段着色；标注2023年6月顶43.58元与2026年6月低15.99元，以及两次财报披露日。</desc>',
     '<text x="20" y="20" font-size="14" font-weight="500" fill="#2C2C2A">宝信软件（600845）月收盘价 · 前复权 · 2444 视角位置</text>',
     '<text x="20" y="38" font-size="11" fill="#888780">数据：data/db/600845.db kline（qfq）｜截至 2026-09-24｜阶段划分为本项目分析层整理</text>']
for d0, d1, fill, label in bands:
    x0, x1 = X(d0), X(d1 if d1 <= t1 else t1)
    s.append(f'<rect x="{x0:.1f}" y="{MT}" width="{x1-x0:.1f}" height="{PH}" fill="{fill}" opacity="0.75"/>')
    _cx = (x0 + x1) / 2
    if _cx + len(label) * 5.6 <= W - 12:
        s.append(f'<text x="{_cx:.1f}" y="{MT+14}" font-size="11" fill="#5F5E5A" text-anchor="middle">{label}</text>')
    else:
        s.append(f'<text x="{min(x1, W-12):.1f}" y="{MT+14}" font-size="11" fill="#5F5E5A" text-anchor="end">{label}</text>')
    s.append(f'<line x1="{x0:.1f}" y1="{MT}" x2="{x0:.1f}" y2="{MT+PH}" stroke="#B4B2A9" stroke-width="0.5" stroke-dasharray="3 3"/>')

for v in range(15, 46, 5):
    s.append(f'<line x1="{X0}" y1="{Y(v):.1f}" x2="{X1}" y2="{Y(v):.1f}" stroke="#D3D1C7" stroke-width="0.5"/>')
    s.append(f'<text x="{X0-6}" y="{Y(v)+4:.1f}" font-size="11" fill="#5F5E5A" text-anchor="end">{v}</text>')
s.append(f'<line x1="{X0}" y1="{MT+PH}" x2="{X1}" y2="{MT+PH}" stroke="#888780" stroke-width="0.9"/>')

poly = " ".join(f"{X(d):.1f},{Y(v):.1f}" for d, v in pts)
s.append(f'<polyline points="{poly}" fill="none" stroke="#185FA5" stroke-width="1.5"/>')

for yy in [2023, 2024, 2025, 2026]:
    dd = dt.date(yy, 1, 1)
    if t0 <= dd <= t1:
        xx = X(dd)
        s.append(f'<line x1="{xx:.1f}" y1="{MT}" x2="{xx:.1f}" y2="{MT+PH:.1f}" stroke="#D3D1C7" stroke-width="0.4"/>')
        s.append(f'<text x="{xx+4:.1f}" y="{MT+PH-6:.1f}" font-size="11" fill="#888780">{yy}</text>')

marks = [
    (dt.date(2023, 6, 20), 43.58, "顶 43.58（2023-06-20）", "end", -8, 16, "#A32D2D"),
    (dt.date(2026, 6, 29), 15.99, "低 15.99（2026-06-29）", "end", -8, 20, "#0F6E56"),
    (dt.date(2026, 9, 24), 18.26, "现 18.26", "end", 4, -8, "#0C447C"),
]
for d, v, lab, anchor, dx, dy, col in marks:
    x, y = X(d), Y(v)
    s.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.2" fill="{col}"/>')
    s.append(f'<text x="{x+dx:.1f}" y="{y+dy:.1f}" font-size="11" fill="{col}" text-anchor="{anchor}">{lab}</text>')

ev = [(dt.date(2026, 4, 30), "4/30 年报+一季报"), (dt.date(2026, 8, 20), "8/20 中报")]
for _i, (d, lab) in enumerate(ev):
    x = X(d)
    s.append(f'<line x1="{x:.1f}" y1="{MT+PH}" x2="{x:.1f}" y2="{MT+PH+16:.1f}" stroke="#854F0B" stroke-width="0.9"/>')
    s.append(f'<text x="{min(x+14, X1):.1f}" y="{MT+PH+30+_i*14:.1f}" font-size="11" fill="#854F0B" text-anchor="end">{lab}</text>')

s.append(f'<text x="{X(dt.date(2025,3,1)):.1f}" y="{Y(16.6):.1f}" font-size="11" fill="#A32D2D" text-anchor="middle">↓ 自 2023-06 顶累计 -63%</text>')
s.append(f'<line x1="{X0}" y1="{MT+PH+70:.1f}" x2="{X1}" y2="{MT+PH+70:.1f}" stroke="#B4B2A9" stroke-width="0.5"/>')
s.append(f'<text x="{X0}" y="{MT+PH+86:.1f}" font-size="11" fill="#5F5E5A">④ 段：15.99（2026-06-29）低于 2021-11 低点 18.52，跌破三年箱体，现价较之 +14%</text>')
s.append(f'<text x="{X0}" y="{MT+PH+102:.1f}" font-size="11" fill="#854F0B">橙线：4/30 年报+一季报；8/20 中报（当日 +0.80%、其后续跌）—— 市场未认这份单季改善</text>')
s.append(f'<text x="{X0}" y="{MT+PH+118:.1f}" font-size="11" fill="#5F5E5A">按里海「底部是走出来的」：尚无长期横盘与筹码充分交换，④ 只能记「低位待确认」，不是底部</text>')
s.append('</svg>')
open("data/tmp_600845/out_2444.svg", "w", encoding="utf-8").write("\n".join(s))
print("bytes:", len("\n".join(s)), "| 月点:", len(pts), "| 首末:", pts[0], pts[-1])
print("底部注释 y =", MT + PH + 102, "/ H =", H)
