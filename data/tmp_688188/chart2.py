import sqlite3, datetime as dt

c = sqlite3.connect('data/688188.db')

# ---------- 股价 ----------
d0s, d1s = '2021-08-01', '2023-12-31'
rows = c.execute("select date,high,low,close from kline where date between ? and ? order by date", (d0s, d1s)).fetchall()
d0 = dt.date.fromisoformat(d0s); d1 = dt.date.fromisoformat(d1s)
span = (d1 - d0).days
X0, X1 = 46.0, 644.0
PY0, PY1 = 62.0, 268.0
VMIN, VMAX = 50.0, 140.0

def X(ds):
    d = dt.date.fromisoformat(ds)
    return round(X0 + (d - d0).days / span * (X1 - X0), 1)

def Y(v):
    return round(PY1 - (v - VMIN) / (VMAX - VMIN) * (PY1 - PY0), 1)

KEEP = {'2021-08-27','2021-10-29','2021-12-31','2022-01-04','2022-04-15','2022-04-29','2022-08-09',
        '2022-10-28','2022-12-30','2023-01-03','2023-03-21','2023-04-11','2023-04-27','2023-08-16',
        '2023-08-31','2023-10-11','2023-12-29'}
sel = [r for i, r in enumerate(rows) if i % 4 == 0 or r[0] in KEEP]
pts = ' '.join(f'{X(r[0])},{Y(r[3])}' for r in sel)

# ---------- 单季营收同比（年报「分季度主要财务数据」原文口径，已核）----------
EV = [
    ('2022-04-29', '2022Q1',  1.40, '一季报'),
    ('2022-08-09', '2022Q2', -21.66, '中报'),
    ('2022-10-28', '2022Q3',  1.72, '三季报'),
    ('2023-04-11', '2022Q4', 18.62, '2022年报'),
    ('2023-04-27', '2023Q1', 42.39, '一季报'),
    ('2023-08-16', '2023Q2', 78.57, '中报'),
    ('2023-10-11', '2023Q3', 35.51, '三季报'),
]

GY0, GY1 = 300.0, 392.0
GMIN, GMAX = -30.0, 90.0

def GY(v):
    return round(GY1 - (v - GMIN) / (GMAX - GMIN) * (GY1 - GY0), 1)

base_g = GY(0)
pl = ' '.join(f'{X(d)},{GY(v)}' for d, _, v, _ in EV)

# ---------- SVG ----------
s = []
s.append('<svg viewBox="0 0 680 486" width="100%" role="img" xmlns="http://www.w3.org/2000/svg">')
s.append('<title>柏楚电子 2021-2023 股价、业绩与里海体系介入点时间线</title>')
s.append('<desc>上方为前复权收盘价，下方为单季营收同比折线（按公告日定位）；灰色带为里海体系的"双左侧"回避区，红色带为体系可介入窗口。</desc>')
s.append('<text x="40" y="22" font-family="var(--font-sans)" font-size="15" font-weight="500" fill="var(--color-text-primary)">柏楚电子：股价 × 业绩 × 按里海体系的介入点（2021-08 ~ 2023-12）</text>')

# 色带：回避区 / 可介入窗
def band(a, b, fill, title, tcol):
    xa, xb = X(a), X(b)
    s.append(f'<rect x="{xa}" y="{PY0}" width="{round(xb-xa,1)}" height="{round(GY1-PY0,1)}" fill="{fill}" opacity="0.30"/>')
    s.append(f'<text x="{round((xa+xb)/2,1)}" y="{PY0-6}" font-family="var(--font-sans)" font-size="11" fill="{tcol}" text-anchor="middle">{title}</text>')

band('2021-08-27', '2022-10-28', '#888780', '回避区：双左侧（基本面往下 + 股价往下）', 'var(--color-text-secondary)')
band('2023-03-21', '2023-08-31', '#d94f4f', '可介入窗口', '#d94f4f')

# 股价网格
for v in (60, 80, 100, 120):
    y = Y(v)
    s.append(f'<line x1="{X0}" y1="{y}" x2="{X1}" y2="{y}" stroke="var(--color-border-tertiary)" stroke-width="0.5"/>')
    s.append(f'<text x="{X0-6}" y="{y+3}" font-family="var(--font-sans)" font-size="10" fill="var(--color-text-tertiary)" text-anchor="end">{v}</text>')

# 公告日竖线
for d, _, v, name in EV:
    x = X(d)
    s.append(f'<line x1="{x}" y1="{PY0}" x2="{x}" y2="{GY1}" stroke="#888780" stroke-width="0.5" stroke-dasharray="3 3" opacity="0.8"/>')

# 股价折线
s.append(f'<polyline points="{pts}" fill="none" stroke="#185FA5" stroke-width="1.5"/>')

# 关键点
KPT = [('2021-08-27', 133.05, '133.05 顶（中报后 2 周）', '#d94f4f', 1, -8),
       ('2022-04-29', 55.17, '55.17 底（一季报当日）', '#2e9e5b', 1, 16),
       ('2023-03-21', 61.23, '61.23 底', '#2e9e5b', -1, 18),
       ('2023-08-31', 93.55, '93.55 顶（中报后 2 周）', '#d94f4f', -1, -10)]
for d, v, lab, col, dirn, dy in KPT:
    x, y = X(d), Y(v)
    s.append(f'<circle cx="{x}" cy="{y}" r="3" fill="{col}"/>')
    anchor = 'start' if dirn > 0 else 'end'
    tx = x + (8 * dirn)
    s.append(f'<text x="{tx}" y="{y+dy}" font-family="var(--font-sans)" font-size="11" fill="{col}" text-anchor="{anchor}">{lab}</text>')

# 业绩区
s.append(f'<line x1="{X0}" y1="{base_g}" x2="{X1}" y2="{base_g}" stroke="var(--color-border-secondary)" stroke-width="0.5"/>')
s.append('<text x="40" y="292" font-family="var(--font-sans)" font-size="11" fill="var(--color-text-secondary)">单季营收同比（折线，按该期报告的实际公告日定位）</text>')
s.append(f'<polyline points="{pl}" fill="none" stroke="#0F6E56" stroke-width="1.5"/>')
for d, _, v, name in EV:
    if v is None:
        continue
    x, y = X(d), GY(v)
    col = '#d94f4f' if v >= 0 else '#2e9e5b'
    s.append(f'<circle cx="{x}" cy="{y}" r="2.5" fill="{col}"/>')

# 只标 4 个体系关键值
KEYV = {'2022-08-09': (-21.66, 'down'), '2022-10-28': (1.72, 'up'), '2023-04-27': (42.39, 'up'), '2023-08-16': (78.57, 'up')}
for d, v, mode in [(k, a, b) for k, (a, b) in KEYV.items()]:
    x, y = X(d), GY(v)
    col = '#d94f4f' if v >= 0 else '#2e9e5b'
    ty = y + 15 if mode == 'down' else y - 8
    s.append(f'<text x="{x}" y="{ty}" font-family="var(--font-sans)" font-size="11" fill="{col}" text-anchor="middle">{v:+.1f}%</text>')

# 体系动作标注
ACT = [('2022-10-28', '① 进跟踪档', '单季斜率首次转正', 392 + 2),
       ('2023-04-27', '② 可介入（战术股）', '两季加速 + 股价先右侧', 392 + 2)]
for d, t, sub, _ in ACT:
    x = X(d)
    s.append(f'<line x1="{x}" y1="{GY1}" x2="{x}" y2="{GY1+14}" stroke="#5F5E5A" stroke-width="0.5"/>')
    s.append(f'<text x="{x}" y="{GY1+27}" font-family="var(--font-sans)" font-size="10.5" fill="var(--color-text-primary)" text-anchor="middle">{t}</text>')
    s.append(f'<text x="{x}" y="{GY1+40}" font-family="var(--font-sans)" font-size="10" fill="var(--color-text-tertiary)" text-anchor="middle">{sub}</text>')
# 卖出动作
x = X('2023-08-31')
s.append(f'<line x1="{x}" y1="{GY1}" x2="{x}" y2="{GY1+14}" stroke="#5F5E5A" stroke-width="0.5"/>')
s.append(f'<text x="{x+4}" y="{GY1+27}" font-family="var(--font-sans)" font-size="10.5" fill="var(--color-text-primary)" text-anchor="start">③ 中报后卖出</text>')

# x 轴年份 + 关键公告日
for lab, d in [('2021', '2021-10-15'), ('2022', '2022-06-19'), ('2023', '2023-12-10')]:
    s.append(f'<text x="{X(d)}" y="{GY1+62}" font-family="var(--font-sans)" font-size="11" fill="var(--color-text-tertiary)" text-anchor="middle">{lab}</text>')
for d in ['2022-04-29', '2022-08-09', '2022-10-28', '2023-04-27', '2023-08-16']:
    x = X(d)
    s.append(f'<text x="{x}" y="{GY1+62}" font-family="var(--font-sans)" font-size="10" fill="var(--color-text-tertiary)" text-anchor="middle">{d[5:].replace("-", "/")}</text>')
s.append('<line x1="46" y1="62" x2="46" y2="392" stroke="var(--color-border-tertiary)" stroke-width="0.5"/>')
s.append('</svg>')
out = '\n'.join(s)
open('data/tmp_688188/out2.svg', 'w', encoding='utf-8').write(out)
print('bytes', len(out.encode()))
