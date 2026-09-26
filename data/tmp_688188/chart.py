import sqlite3, datetime as dt

c = sqlite3.connect('data/688188.db')
rows = c.execute("select date,high,low,close from kline where date between '2021-12-01' and '2023-06-30' order by date").fetchall()
d0 = dt.date.fromisoformat(rows[0][0]); d1 = dt.date.fromisoformat(rows[-1][0])
span = (d1 - d0).days
X0, X1 = 46.0, 644.0
PY0, PY1 = 56.0, 266.0
VMIN, VMAX = 52.0, 106.0
GY0, GY1 = 296.0, 384.0

def X(ds):
    d = dt.date.fromisoformat(ds)
    return round(X0 + (d - d0).days / span * (X1 - X0), 1)

def Y(v):
    return round(PY1 - (v - VMIN) / (VMAX - VMIN) * (PY1 - PY0), 1)

def GY(v):
    return round(GY1 - (v + 30) / 75 * (GY1 - GY0), 1)

base = GY(0)
KEEP = {'2021-12-31','2022-01-04','2022-04-27','2022-04-29','2022-08-05','2022-08-09','2022-10-28','2022-12-30','2023-01-03','2023-03-21','2023-04-11','2023-04-27','2023-06-30'}
sel = [r for i, r in enumerate(rows) if i % 3 == 0 or r[0] in KEEP]
pts = ' '.join(f'{X(r[0])},{Y(r[3])}' for r in sel)
disc = [('2022-04-29', '一季报', 1.40), ('2022-08-09', '中报', -21.66),
        ('2022-10-28', '三季报', 1.72), ('2023-04-11', '年报', 18.62),
        ('2023-04-27', '一季报', 42.39)]
label = {'2022-04-29': '4/29 一季报', '2022-08-09': '8/9 中报', '2022-10-28': '10/28 三季报',
         '2023-04-11': '4/11 年报', '2023-04-27': '4/27 一季报'}

s = []
s.append('<svg viewBox="0 0 680 466" width="100%" role="img" xmlns="http://www.w3.org/2000/svg">')
s.append('<title>柏楚电子 2022 年业绩与股价对照（按实际公告日）</title>')
s.append('<desc>上方为前复权收盘价走势，下方为单季营收同比柱，竖直虚线为定期报告实际公告日（巨潮 cninfo）。2022 年业绩最差的一段股价上涨 51%，业绩改善的一段股价下跌 18%。</desc>')
s.append('<text x="40" y="22" font-family="var(--font-sans)" font-size="15" font-weight="500" fill="var(--color-text-primary)">柏楚电子：业绩塌陷期股价在涨，业绩改善期股价在跌（2021-12 ~ 2023-06）</text>')
s.append('<text x="268" y="44" font-family="var(--font-sans)" font-size="11" fill="var(--color-text-tertiary)" text-anchor="middle">2022 年</text>')
s.append('<text x="556" y="44" font-family="var(--font-sans)" font-size="11" fill="var(--color-text-tertiary)" text-anchor="middle">2023 年</text>')
s.append(f'<line x1="{X("2022-12-30")}" y1="{PY0}" x2="{X("2022-12-30")}" y2="{GY1}" stroke="var(--color-border-tertiary)" stroke-width="0.5"/>')

for v in (60, 80, 100):
    y = Y(v)
    s.append(f'<line x1="{X0}" y1="{y}" x2="{X1}" y2="{y}" stroke="var(--color-border-tertiary)" stroke-width="0.5"/>')
    s.append(f'<text x="{X0-6}" y="{y+3}" font-family="var(--font-sans)" font-size="10" fill="var(--color-text-tertiary)" text-anchor="end">{v}</text>')

for d, name, val in disc:
    x = X(d)
    s.append(f'<line x1="{x}" y1="{PY0-4}" x2="{x}" y2="{GY1}" stroke="#888780" stroke-width="0.5" stroke-dasharray="3 3"/>')

s.append(f'<polyline points="{pts}" fill="none" stroke="#185FA5" stroke-width="1.4"/>')

xl, yl = X('2022-04-29'), Y(55.17)
xh, yh = X('2022-08-09'), Y(97.36)
s.append(f'<circle cx="{xl}" cy="{yl}" r="3" fill="#2e9e5b"/>')
s.append(f'<text x="{xl+8}" y="{yl-4}" font-family="var(--font-sans)" font-size="11" fill="#2e9e5b">55.17 全年最低</text>')
s.append(f'<circle cx="{xh}" cy="{yh}" r="3" fill="#d94f4f"/>')
s.append(f'<text x="{xh+8}" y="{yh-6}" font-family="var(--font-sans)" font-size="11" fill="#d94f4f">97.36 全年最高</text>')
s.append('<line x1="470" y1="66" x2="494" y2="66" stroke="#185FA5" stroke-width="1.4"/>')
s.append('<text x="500" y="70" font-family="var(--font-sans)" font-size="11" fill="var(--color-text-secondary)">股价（前复权收盘）</text>')

s.append(f'<line x1="{X0}" y1="{base}" x2="{X1}" y2="{base}" stroke="var(--color-border-secondary)" stroke-width="0.5"/>')
s.append('<text x="40" y="290" font-family="var(--font-sans)" font-size="11" fill="var(--color-text-secondary)">单季营收同比　红＝增长　绿＝下滑（柱位于该期报告的实际公告日）</text>')
for d, name, val in disc:
    x = X(d)
    yv = GY(val)
    top, bot = (yv, base) if val >= 0 else (base, yv)
    if abs(bot - top) < 3:
        bot = top + 3
    color = '#d94f4f' if val >= 0 else '#2e9e5b'
    s.append(f'<rect x="{round(x-7,1)}" y="{top}" width="14" height="{round(bot-top,1)}" rx="2" fill="{color}" opacity="0.85"/>')
    ly = top - 6 if val >= 0 else bot + 13
    s.append(f'<text x="{x}" y="{ly}" font-family="var(--font-sans)" font-size="11" fill="{color}" text-anchor="middle">{val:+.2f}%</text>')

for d in ['2022-04-29', '2022-08-09', '2022-10-28', '2023-04-27']:
    x = X(d)
    s.append(f'<text x="{x}" y="402" font-family="var(--font-sans)" font-size="10.5" fill="var(--color-text-secondary)" text-anchor="middle">{label[d]}</text>')
x = X('2023-04-11')
s.append(f'<line x1="{x}" y1="388" x2="{x}" y2="409" stroke="var(--color-border-tertiary)" stroke-width="0.5"/>')
s.append(f'<text x="{x}" y="419" font-family="var(--font-sans)" font-size="10.5" fill="var(--color-text-secondary)" text-anchor="middle">{label["2023-04-11"]}</text>')

s.append('<text x="40" y="440" font-family="var(--font-sans)" font-size="11" fill="#d94f4f">① 4/29 → 8/9（业绩最差）：股价 +51%，同期 Q1 +1.40% / Q2 −21.66%</text>')
s.append('<text x="40" y="456" font-family="var(--font-sans)" font-size="11" fill="#2e9e5b">② 8/9 → 12/30（业绩改善）：股价 −18%，同期 Q3 +1.72% / Q4 +18.62%</text>')
s.append('</svg>')
out = '\n'.join(s)
open('data/tmp_688188/out.svg', 'w', encoding='utf-8').write(out)
print(out)
