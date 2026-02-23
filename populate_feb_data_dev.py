import sqlite3
import os
from datetime import datetime, timedelta
import random

DB_PATH = os.path.join(os.path.dirname(__file__), "backend", "data", "stocks.db")

def populate_feb_data():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 테이블이 없으면 생성 (최신 스펙)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            symbol TEXT NOT NULL,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            action TEXT NOT NULL,
            trade_type TEXT NOT NULL,
            reason TEXT,
            qty INTEGER NOT NULL DEFAULT 0,
            profit REAL NOT NULL DEFAULT 0.0
        )
    """)
    
    # 2월 1일부터 2월 23일까지의 데이터 생성
    start_date = datetime(2026, 2, 1)
    end_date = datetime(2026, 2, 23)
    
    stocks = [
        ("005930", "삼성전자"),
        ("000660", "SK하이닉스"),
        ("035420", "NAVER"),
        ("005380", "현대차"),
        ("068270", "셀트리온")
    ]
    
    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.strftime("%Y-%m-%d")
        
        # 매일 2~4건의 매매 참여 (주말 제외 등 복잡한 로직 생략하고 데이터 채우기 위함)
        num_trades = random.randint(2, 4)
        for _ in range(num_trades):
            symbol, name = random.choice(stocks)
            price = random.randint(50000, 1000000)
            action = random.choice(["BUY", "SELL"])
            trade_type = random.choice(["MOCK", "REAL"])
            qty = random.randint(1, 50)
            profit = round(random.uniform(-50000, 100000), 0) if action == "SELL" else 0.0
            reason = "테스트 매매"
            
            cursor.execute("""
                INSERT INTO trades (date, symbol, name, price, action, trade_type, reason, qty, profit)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (date_str, symbol, name, price, action, trade_type, reason, qty, profit))
            
        current_date += timedelta(days=1)
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    populate_feb_data()
    print("February test data insertion complete.")
