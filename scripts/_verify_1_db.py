# -*- coding: utf-8 -*-
"""校验步骤1b: DB 关键财务字段聚焦表"""
import sqlite3
conn = sqlite3.connect(r'c:\LY\Repo\llm\value-line\data\09992.db')
cur = conn.cursor()
dates = [d for (d,) in cur.execute("SELECT DISTINCT report_date FROM income ORDER BY report_date")]
keys = ['营业额','销售成本','毛利','经营溢利','本年度溢利','股东应占溢利','除税前溢利','本公司拥有人应占全面收益总额','全面收益总额','少数股东应占溢利','非控股权益应占全面收益总额']
print("report_date | " + " | ".join(keys))
for d in dates:
    row = {}
    for k in keys:
        r = cur.execute("SELECT amount FROM income WHERE report_date=? AND item_name=?", (d, k)).fetchone()
        row[k] = r[0] if r else None
    gm = None
    if row['营业额'] and row['销售成本']:
        gm = row['营业额'] + row['销售成本']  # 销售成本为负
    line = [d] + [str(row[k]/1e8 if row[k] is not None else '') for k in keys]
    line.append(f"毛利(算)={gm/1e8:.2f}" if gm else "")
    print(" | ".join(line))
