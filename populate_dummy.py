import sqlite3
import os
import sys

# Make sure path is absolute or relative
DB_PATH = os.path.join(os.path.dirname(__file__), "backend", "data", "stocks.db")

def populate_dummy_data():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            symbol TEXT NOT NULL,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            action TEXT NOT NULL,
            trade_type TEXT NOT NULL,
            reason TEXT
        )
    """)
    cursor.execute("""
        INSERT INTO trades (date, symbol, name, price, action, trade_type, reason)
        VALUES ('2026-02-23', '005930', '삼성전자', 70000, 'BUY', 'MOCK', '눌림목'),
               ('2026-02-23', '000660', 'SK하이닉스', 150000, 'SELL', 'REAL', '전일 종가배팅 매도')
    """)
    conn.commit()
    conn.close()

if __name__ == "__main__":
    populate_dummy_data()
    print("Dummy data inserted.")
