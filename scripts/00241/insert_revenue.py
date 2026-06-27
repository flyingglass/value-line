# -*- coding: utf-8 -*-
"""阿里健康 00241 — 营收结构"""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import db_path
import sqlite3

CODE = "00241"

def build():
    db = db_path(CODE)
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute("DROP TABLE IF EXISTS revenue_structure")
    c.execute('''CREATE TABLE IF NOT EXISTS revenue_structure (
        code TEXT, year TEXT, dim_type TEXT, dim_name TEXT,
        amount REAL, pct REAL,
        PRIMARY KEY (code, year, dim_type, dim_name))''')

    # FY截止3月31日，按日历年标（如FY2025=截至2025年3月）
    # 金额单位：亿元人民币
    rows = [
        # FY2025: 营收305.98亿
        (CODE, "2025", "by_product", "医药自营B2C零售", 247.0, 80.7),
        (CODE, "2025", "by_product", "医药电商平台服务", 31.0, 10.1),
        (CODE, "2025", "by_product", "医疗健康及数字化", 28.0, 9.2),
        # FY2024: 营收270.27亿
        (CODE, "2024", "by_product", "医药自营B2C零售", 218.0, 80.6),
        (CODE, "2024", "by_product", "医药电商平台服务", 29.0, 10.7),
        (CODE, "2024", "by_product", "医疗健康及数字化", 23.6, 8.7),
        # FY2023: 营收249.04亿
        (CODE, "2023", "by_product", "医药自营B2C零售", 200.0, 80.3),
        (CODE, "2023", "by_product", "医药电商平台服务", 27.0, 10.8),
        (CODE, "2023", "by_product", "医疗健康及数字化", 22.0, 8.9),
    ]
    c.executemany("INSERT OR REPLACE INTO revenue_structure VALUES (?,?,?,?,?,?)", rows)
    conn.commit()
    conn.close()
    print("OK")

if __name__ == "__main__":
    build()
