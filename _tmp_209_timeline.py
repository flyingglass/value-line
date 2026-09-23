import sqlite3
db = r'C:/LY/Repo/llm/value-line/data/002209.db'
con = sqlite3.connect(db); cur = con.cursor()

# 月末收盘（前复权）
rows = cur.execute("SELECT date, close FROM kline WHERE date>='2021-01-01' ORDER BY date").fetchall()
from collections import OrderedDict
m = OrderedDict()
for d,c in rows:
    m[d[:7]] = (d, c)   # 覆盖，最后一天即月末
print('=== 月末收盘价（前复权）===')
yrs = {}
for k,(d,c) in m.items():
    print(k, '%.2f' % c)
