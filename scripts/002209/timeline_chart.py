# -*- coding: utf-8 -*-
"""
达意隆 002209 — 五轨时间线对照图生成器

设计要点（前版踩过的坑，勿回退）：
1. 股价用日度序列连续成线；财务指标用季末点直接按真实日期连线，
   **禁止**先铺月度数组再填充季度值（会导致每季仅 1 点、线段被判为孤立点而不绘制）。
2. 同比增速在盈亏切换期会失真（如 23Q1 -639.8%、25Q1 +935.5%），
   基数绝对值 < 0.1 亿 或 |yoy| > 300% 一律置空并在图注列出。
3. 财务点锚定"报告期季末"，非披露日；仅对已核实日期的事件画竖线，不编造披露日。

输出：report/002209-timeline.html
"""
import sqlite3, datetime, os, json

DB = r'C:/LY/Repo/llm/value-line/data/002209.db'
OUT = r'C:/LY/Repo/llm/value-line/report/002209-timeline.html'

# ============================== 取数 ==============================
con = sqlite3.connect(DB); cur = con.cursor()

def ser(tbl, item):
    return {d: a for d, a in cur.execute(
        "SELECT report_date,amount FROM %s WHERE item_name=?" % tbl, (item,))}

rev = ser('income', '*营业总收入')          # 累计口径
dkl = ser('income', '*扣除非经常性损益后的净利润')
cl = ser('balance', '合同负债'); cl.update(ser('balance', '预收款项'))
inv = ser('balance', '存货')

PREV = {'06': ('03', '31'), '09': ('06', '30'), '12': ('09', '30')}
def single(acc, d):
    """累计 -> 单季"""
    if d not in acc: return None
    md = d[5:7]
    if md == '03': return acc[d]
    pq, day = PREV[md]
    b = acc.get('%s-%s-%s' % (d[:4], pq, day))
    return None if b is None else acc[d] - b

def ttm(acc, y, q):
    """TTM = 上年年报 + 本年累计 - 上年同期累计"""
    cur_d = '%d-%s' % (y, {'1': '03-31', '2': '06-30', '3': '09-30', '4': '12-31'}[str(q)])
    if cur_d not in acc: return None
    prev_d = '%d-%s' % (y - 1, {'1': '03-31', '2': '06-30', '3': '09-30', '4': '12-31'}[str(q)])
    last_y_d = '%d-12-31' % (y - 1)
    if prev_d not in acc or last_y_d not in acc: return None
    return acc[cur_d] + acc[last_y_d] - acc[prev_d]

QEND = {1: (3, 31), 2: (6, 30), 3: (9, 30), 4: (12, 31)}
quarters = [(y, q) for y in range(2020, 2027) for q in (1, 2, 3, 4)]
quarters = [(y, q) for y, q in quarters if '2021-01-01' <= '%d-%02d-%02d' % (y, *QEND[q]) <= '2026-09-22']

recs = []   # 每季一条，按报告期季末定位
for y, q in quarters:
    m, d = QEND[q]
    ds = '%d-%02d-%02d' % (y, m, d)
    recs.append(dict(
        y=y, q=q, date=datetime.date(y, m, d),
        rev=single(rev, ds), dkl=single(dkl, ds),
        cl=cl.get(ds), inv=inv.get(ds),
        ttm_dkl=ttm(dkl, y, q),
    ))

# 同比（同一季度跨年比）
def yoy(c, p):
    """同比。剔除两种数学上无意义的情形：
       ① 基数 <= 0（负基数算同比无经济含义，如 -0.180 -> 0.098 得 -154.4%）
       ② 基数绝对值 < 0.1 亿（微小基数放大失真）"""
    if c is None or p is None: return None
    if p <= 0: return None
    if abs(p) < 1e7: return None
    v = (c / p - 1) * 100
    if abs(v) > 300: return None
    return v

dropped = []
by_q = {(r['y'], r['q']): r for r in recs}
for r in recs:
    p = by_q.get((r['y'] - 1, r['q']))
    r['rev_yoy'] = yoy(r['rev'], p['rev'] if p else None)
    r['dkl_yoy'] = yoy(r['dkl'], p['dkl'] if p else None)
    r['cl_yoy'] = yoy(r['cl'], p['cl'] if p else None)
    if p is not None:
        for k in ('rev', 'dkl'):
            if r[k] is None or p[k] is None: continue
            if p[k] <= 0:
                dropped.append('%dQ%d %s 基数≤0(%.3f亿)同比无意义' % (r['y'], r['q'], k, p[k] / 1e8))
            elif abs(p[k]) < 1e7:
                dropped.append('%dQ%d %s 基数过小(%.3f亿)' % (r['y'], r['q'], k, p[k] / 1e8))

px = [(datetime.date(int(d[:4]), int(d[5:7]), int(d[8:10])), c)
      for d, c in cur.execute("SELECT date,close FROM kline WHERE date>='2021-01-01' ORDER BY date")]
con.close()

# 已核实事件（依据：龙虎榜/行情核对过的公开披露日，未核实的一律不标）
EVENTS = [
    (datetime.date(2026, 4, 30), '一季报后跌停 -10.03%', '#C0392B'),
    (datetime.date(2026, 8, 21), '中报日涨停 +10.03%', '#C0392B'),
]
MARKS = [(datetime.date(2026, 4, 22), 17.38, '4/22 高 17.38', -6),
         (datetime.date(2026, 7, 21), 9.40, '26/7 年内低 9.40', 13),
         (datetime.date(2025, 7, 16), 5.17, '25/7 区间最低 5.17', -6)]

def anchor_for(x, w=80):
    """靠近右边界时靠左排，避免文字溢出画布"""
    return ('end', x - 5) if x > X1 - w else ('start', x + 5)

# ============================== 绘图 ==============================
T0 = datetime.date(2021, 1, 1); T1 = datetime.date(2026, 9, 22)
X0, X1 = 66, 648
def X(t):
    return X0 + (t - T0).days / (T1 - T0).days * (X1 - X0)

def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

S = []; A = S.append
PW = 108      # 面板高
GAP = 40      # 面板间距
TOP0 = 44

PANS = [
    dict(key='px',   title='① 股价（元·前复权·日收盘）',      mn=5.0, mx=18.6),
    dict(key='rev',  title='② 单季营业收入（亿元）',          mn=0,   mx=9.2),
    dict(key='dkl',  title='③ 单季扣非净利润（亿元）',        mn=-0.7, mx=1.15),
    dict(key='yoy',  title='④ 单季同比增速（%）— 蓝：营收 / 橙：扣非', mn=-110, mx=300),
    dict(key='cl',   title='⑤ 合同负债 / 存货（亿元·季末存量）', mn=0,   mx=15.5),
]
H = TOP0 + len(PANS) * (PW + GAP) + 8

A('<svg viewBox="0 0 680 %d" width="100%%" xmlns="http://www.w3.org/2000/svg" role="img">' % H)
A('<title>达意隆 002209 2021-2026 五轨时间线对照</title>')

# --- 面板通用骨架 ---
def panel(idx, title, mn, mx):
    top = TOP0 + idx * (PW + GAP); bot = top + PW
    def Y(v): return bot - (v - mn) / (mx - mn) * PW
    A('<rect x="%d" y="%d" width="%d" height="%d" fill="#FBFAF7" stroke="#D8D6CC" stroke-width="0.6"/>'
      % (X0, top, X1 - X0, PW))
    # 横向网格
    for i in range(5):
        gv = mn + (mx - mn) * i / 4
        A('<line x1="%d" y1="%.1f" x2="%d" y2="%.1f" stroke="%s" stroke-width="0.5" stroke-dasharray="2 2"/>'
          % (X0, Y(gv), X1, Y(gv), '#C0392B' if gv == 0 and mn < 0 else '#E5E3DA'))
        A('<text x="%d" y="%.1f" font-size="9.5" fill="#8A887E" text-anchor="end" '
          'dominant-baseline="central">%s</text>'
          % (X0 - 6, Y(gv), ('%.0f' % gv) if abs(mx - mn) > 6 else ('%.1f' % gv)))
    # 年度竖线
    for y in range(2021, 2027):
        t = datetime.date(y, 1, 1)
        if T0 <= t <= T1:
            A('<line x1="%.1f" y1="%d" x2="%.1f" y2="%d" stroke="#E5E3DA" stroke-width="0.5"/>'
              % (X(t), top, X(t), bot))
    A('<text x="%d" y="%d" font-size="11.5" fill="#45443F" font-weight="600">%s</text>'
      % (X0 + 2, top + 14, esc(title)))
    return top, bot, Y

def evline(top, bot):
    for d, lab, col in EVENTS:
        if T0 <= d <= T1:
            A('<line x1="%.1f" y1="%d" x2="%.1f" y2="%d" stroke="%s" stroke-width="1" '
              'stroke-dasharray="3 3" opacity="0.65"/>' % (X(d), top, X(d), bot, col))

def poly(pts, color, Yf, w=1.4, dash=None):
    """pts: [(date, value)]，None 自动断段；单段 >=2 点才画。
    Yf 为该面板的值->像素映射函数（务必传入，否则会用原始数值当像素坐标）。"""
    seg = []
    for t, v in pts:
        if v is None:
            if len(seg) >= 2: emit(seg, color, w, dash)
            seg = []
        else:
            seg.append((X(t), Yf(v)))
    if len(seg) >= 2: emit(seg, color, w, dash)

def emit(seg, color, w, dash):
    d = 'M' + ' L'.join('%.1f,%.1f' % (x, y) for x, y in seg)
    A('<path d="%s" fill="none" stroke="%s" stroke-width="%s" stroke-linejoin="round"'
      '%s/>' % (d, color, w, (' stroke-dasharray="%s"' % dash) if dash else ''))

# ---- 面板① 股价 ----
top, bot, Y = panel(0, PANS[0]['title'], PANS[0]['mn'], PANS[0]['mx'])
evline(top, bot)
poly([(t, c) for t, c in px], '#2C6FAD', Y, 1.3)
for d, v, lab, dy in MARKS:
    an, tx = anchor_for(X(d))
    A('<circle cx="%.1f" cy="%.1f" r="2.6" fill="#C0392B"/>' % (X(d), Y(v)))
    A('<text x="%.1f" y="%.1f" font-size="9.5" fill="#C0392B" font-weight="600" '
      'text-anchor="%s">%s</text>' % (tx, Y(v) + dy, an, esc(lab)))
A('<text x="%.1f" y="%.1f" font-size="9.5" fill="#2C6FAD" font-weight="600">最新 %.2f</text>'
  % (X(px[-1][0]) - 52, Y(px[-1][1]) - 7, px[-1][1]))

# ---- 面板② 单季营收柱 ----
top, bot, Y = panel(1, PANS[1]['title'], PANS[1]['mn'], PANS[1]['mx'])
evline(top, bot)
BW = 7.0
for r in recs:
    if r['rev'] is None: continue
    x = X(r['date']); y = Y(r['rev'] / 1e8); y0 = Y(0)
    A('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#2C6FAD" opacity="0.85"/>'
      % (x - BW / 2, y, BW, abs(y0 - y)))
# ---- 面板③ 单季扣非柱 ----
top, bot, Y = panel(2, PANS[2]['title'], PANS[2]['mn'], PANS[2]['mx'])
evline(top, bot)
for r in recs:
    if r['dkl'] is None: continue
    x = X(r['date']); y = Y(r['dkl'] / 1e8); y0 = Y(0)
    A('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" opacity="0.9"/>'
      % (x - BW / 2, min(y, y0), BW, abs(y0 - y), '#E08A2E' if r['dkl'] >= 0 else '#3E8E5A'))
A('<line x1="%d" y1="%.1f" x2="%d" y2="%.1f" stroke="#45443F" stroke-width="0.8"/>'
  % (X0, Y(0), X1, Y(0)))
# 极值标注
mx_r = max((r for r in recs if r['dkl'] is not None), key=lambda r: r['dkl'])
mn_r = min((r for r in recs if r['dkl'] is not None), key=lambda r: r['dkl'])
for r, txt, dy in [(mx_r, '%dQ%d 峰值 %.3f' % (mx_r['y'], mx_r['q'], mx_r['dkl'] / 1e8), -6),
                   (mn_r, '%dQ%d 谷底 %.3f' % (mn_r['y'], mn_r['q'], mn_r['dkl'] / 1e8), 12)]:
    an, tx = anchor_for(X(r['date']))
    A('<text x="%.1f" y="%.1f" font-size="9" fill="#5F5E5A" text-anchor="%s">%s</text>'
      % (tx, Y(r['dkl'] / 1e8) + dy, an, esc(txt)))

# ---- 面板④ 同比 ----
top, bot, Y = panel(3, PANS[3]['title'], PANS[3]['mn'], PANS[3]['mx'])
evline(top, bot)
poly([(r['date'], r['rev_yoy']) for r in recs], '#2C6FAD', Y, 1.4)
poly([(r['date'], r['dkl_yoy']) for r in recs], '#E08A2E', Y, 1.4)
A('<line x1="%d" y1="%.1f" x2="%d" y2="%.1f" stroke="#45443F" stroke-width="0.8"/>'
  % (X0, Y(0), X1, Y(0)))
for r in recs:
    for k, col in (('rev_yoy', '#2C6FAD'), ('dkl_yoy', '#E08A2E')):
        v = r[k]
        if v is None: continue
        A('<circle cx="%.1f" cy="%.1f" r="1.7" fill="%s"/>' % (X(r['date']), Y(v), col))

# ---- 面板⑤ 合同负债 / 存货 ----
top, bot, Y = panel(4, PANS[4]['title'], PANS[4]['mn'], PANS[4]['mx'])
evline(top, bot)
poly([(r['date'], r['cl'] / 1e8 if r['cl'] else None) for r in recs], '#128A7B', Y, 1.6)
poly([(r['date'], r['inv'] / 1e8 if r['inv'] else None) for r in recs], '#8A5CB8', Y, 1.6)
for r in recs:
    if r['cl']:
        A('<circle cx="%.1f" cy="%.1f" r="1.7" fill="#128A7B"/>' % (X(r['date']), Y(r['cl'] / 1e8)))
    if r['inv']:
        A('<circle cx="%.1f" cy="%.1f" r="1.7" fill="#8A5CB8"/>' % (X(r['date']), Y(r['inv'] / 1e8)))
A('<text x="%d" y="%d" font-size="10" fill="#128A7B" font-weight="600">■ 合同负债</text>' % (X1 - 150, top + 14))
A('<text x="%d" y="%d" font-size="10" fill="#8A5CB8" font-weight="600">■ 存货</text>' % (X1 - 66, top + 14))
last = recs[-1]
an, tx = anchor_for(X(last['date']))
A('<text x="%.1f" y="%.1f" font-size="9" fill="#128A7B" text-anchor="%s">%.2f</text>'
  % (tx, Y(last['cl'] / 1e8) + 3, an, last['cl'] / 1e8))

# --- 事件标注（顶部） ---
for d, lab, col in EVENTS:
    A('<text x="%.1f" y="%d" font-size="9.5" fill="%s" font-weight="600" text-anchor="middle" '
      'transform="rotate(-90 %.1f %d)">%s</text>' % (X(d), TOP0 - 6, col, X(d), TOP0 - 6, esc(lab)))

# --- X 轴标签（仅最底面板下方） ---
bot = TOP0 + (len(PANS) - 1) * (PW + GAP) + PW
for y in range(2021, 2027):
    for q in (1, 2, 3, 4):
        t = datetime.date(y, *QEND[q])
        if not (T0 <= t <= T1): continue
        A('<text x="%.1f" y="%d" font-size="8.5" fill="#8A887E" text-anchor="middle">%dQ%d</text>'
          % (X(t), bot + 14, y, q))
A('</svg>')

svg = '\n'.join(S)

# ============================== 自检 ==============================
import re
n_path = len(re.findall(r'<path ', svg))
n_rect = len(re.findall(r'<rect ', svg))
n_circ = len(re.findall(r'<circle ', svg))
n_text = len(re.findall(r'<text ', svg))
assert n_path >= 5, '路径过少，折线未绘制：%d' % n_path
assert n_rect >= 4 + len(recs), '柱子数量异常：%d' % n_rect

# 越界检查：所有 path 顶点必须落在画布内（防止漏做 Y 映射，用原始数值当像素）
_ys = [float(v) for m in re.findall(r'd="M([\d.\- ,L]+)"', svg)
       for v in re.findall(r',([-\d.]+)', m)]
_BOT = TOP0 + len(PANS) * (PW + GAP) - GAP      # 最后一个面板下沿
assert _ys and min(_ys) >= TOP0 - 6 and max(_ys) <= _BOT + 6, \
    '折线坐标越界（疑似漏 Y 映射或轴范围过窄）：%.1f ~ %.1f，允许 %d~%d' \
    % (min(_ys), max(_ys), TOP0 - 6, _BOT + 6)

drop_txt = '；'.join(sorted(set(dropped))) or '无'

TPL = """<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>达意隆 002209 · 五轨时间线对照</title>
<style>
 body{margin:0;padding:22px 26px;background:#fff;font-family:system-ui,-apple-system,"Microsoft YaHei",sans-serif;color:#2B2A26;}
 h1{font-size:17px;margin:0 0 4px;}
 .sub{font-size:12px;color:#8A887E;margin-bottom:14px;}
 .note{margin-top:16px;font-size:12px;line-height:1.75;color:#5F5E5A;border-top:1px solid #E5E3DA;padding-top:12px;max-width:900px;}
 .note b{color:#2B2A26;}
 table{border-collapse:collapse;font-size:11.5px;margin-top:10px;}
 th,td{border:1px solid #E5E3DA;padding:3px 8px;text-align:right;}
 th{background:#F5F4EF;font-weight:600;}
 td:first-child,th:first-child{text-align:left;}
</style></head><body>
<h1>达意隆 002209 · 五轨时间线对照（2021-01 → 2026-09）</h1>
<div class="sub">共享同一条真实日期时间轴 · 数据来源 data/002209.db（AKShare）· 股价为前复权日收盘</div>
__SVG__
<div class="note">
<b>读图要点</b><br>
1. 面板⑤ 合同负债与存货自 2023Q1 起同步上台阶（2.32 → 11.46 亿），两者是同一件事的两面：客户预付 → 公司备料在产，不是两个独立信号。<br>
2. 面板① 同期股价完成 10.51 → 7.54（−28%）→ 17.38 → 9.40（−46%）→ 13.46 两轮大幅摆动，与面板⑤的单调上升线之间<b>没有稳定映射</b>。<br>
3. 面板②③ 单季营收与单季扣非在 2026Q1 同步塌陷、2026Q2 同步创历史新高；面板④ 显示两者同比永远同向，但扣非振幅远大于营收（项目制 + 刚性费用的放大效应）。<br>
4. 两条红色虚线是已核实的披露事件：2026-04-30（一季报后跌停 −10.03%）、2026-08-21（中报日涨停 +10.03%）。两次事件中合同负债同比均为 +45% 以上、无差别，方向由单季利润决定。<br><br>
<b>口径说明</b><br>
· 财务点锚定<b>报告期季末</b>，非实际披露日（数据库无披露日表，未核实日期不作标注）。<br>
· 同比剔除（基数 &lt; 0.1 亿或 |增速| &gt; 300% 的盈亏切换失真）：<b>__DROP__</b><br>
· 单季 = 累计值差分；TTM 口径 = 上年年报 + 本年累计 − 上年同期累计。
</div>
</body></html>"""

html = TPL.replace('__SVG__', svg).replace('__DROP__', esc(drop_txt))

os.makedirs(os.path.dirname(OUT), exist_ok=True)
open(OUT, 'w', encoding='utf-8').write(html)

print('OUT :', OUT)
print('size: %.1f KB' % (len(html) / 1024))
print('path=%d rect=%d circle=%d text=%d' % (n_path, n_rect, n_circ, n_text))
print('季度数 =', len(recs), ' 股价点数 =', len(px))
print('剔除失真:', drop_txt)
print('末季:', recs[-1]['y'], 'Q', recs[-1]['q'],
      'CL=%.2f' % (recs[-1]['cl'] / 1e8), 'INV=%.2f' % (recs[-1]['inv'] / 1e8),
      '单季扣非=%.3f' % (recs[-1]['dkl'] / 1e8))
