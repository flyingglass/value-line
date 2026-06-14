import sqlite3, os
codes = ['00883','01368','01378','00696','01698','000807','000933','600595','002128','002532','300308','000651']
for c in codes:
    db = f'data/{c}.db'
    if os.path.exists(db):
        sz = os.path.getsize(db)//1024
        try:
            conn = sqlite3.connect(db)
            cnt = conn.execute("SELECT COUNT(*) FROM revenue_structure WHERE code=?",(c,)).fetchone()[0]
            conn.close()
            print(f'{c}: DB={sz}KB revenue={cnt}')
        except Exception as e:
            print(f'{c}: DB={sz}KB ERROR={e}')
    else:
        print(f'{c}: NO DB')
