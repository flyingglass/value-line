# -*- coding: utf-8 -*-
import sqlite3
conn = sqlite3.connect("data/09988.db")
conn.execute("INSERT OR REPLACE INTO meta VALUES (?,?)",
             ("business_desc", "阿里巴巴集团是全球领先的电子商务及科技公司。旗下核心业务涵盖中国商业（淘宝、天猫、1688）、国际商业（AliExpress、Lazada）、本地生活（饿了么）、云计算（阿里云）、数字媒体及娱乐等。2025财年集团持续聚焦用户为先、AI驱动战略，云计算业务实现盈利增长，国际业务快速扩张。"))
conn.execute("INSERT OR REPLACE INTO meta VALUES (?,?)", ("employee_count", "198000"))
conn.execute("INSERT OR REPLACE INTO meta VALUES (?,?)", ("employee_year", "2025"))
conn.commit()
print("OK")
conn.close()
