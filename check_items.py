# -*- coding: utf-8 -*-
import sqlite3, sys
sys.stdout.reconfigure(encoding='utf-8')
conn = sqlite3.connect("data/09988.db")
cur = conn.execute("SELECT DISTINCT item_name FROM balance WHERE report_date='2026-03-31' ORDER BY item_name")
for r in cur:
    try:
        print(r[0])
    except:
        print(repr(r[0]))
conn.close()
