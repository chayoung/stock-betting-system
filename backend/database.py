import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "stocks.db")

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
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
    # Add qty and profit columns if they don't exist
    try:
        cursor.execute("ALTER TABLE trades ADD COLUMN qty INTEGER NOT NULL DEFAULT 0")
    except sqlite3.OperationalError:
        pass # Column already exists
    try:
        cursor.execute("ALTER TABLE trades ADD COLUMN profit REAL NOT NULL DEFAULT 0.0")
    except sqlite3.OperationalError:
        pass # Column already exists
    
    conn.commit()
    conn.close()

def insert_trade(date, symbol, name, price, action, trade_type, reason=None, qty=0, profit=0.0):
    """
    date: 'YYYY-MM-DD'
    action: 'BUY' or 'SELL'
    trade_type: 'MOCK' or 'REAL'
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO trades (date, symbol, name, price, action, trade_type, reason, qty, profit)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (date, symbol, name, price, action, trade_type, reason, qty, profit))
    conn.commit()
    conn.close()

def get_today_trades():
    """가장 최근 거래일의 매매 내역을 가져옵니다."""
    conn = sqlite3.connect(DB_PATH)
    # 딕셔너리 형태로 반환하기 위한 설정
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # 1. 가장 최근 날짜 확인
    cursor.execute("SELECT MAX(date) FROM trades")
    row = cursor.fetchone()
    if not row or row[0] is None:
        conn.close()
        return []
        
    latest_date = row[0]
    
    # 2. 해당 날짜의 내역 조회
    cursor.execute("SELECT * FROM trades WHERE date = ?", (latest_date,))
    rows = cursor.fetchall()
    
    results = []
    for r in rows:
        results.append({
            "id": r["id"],
            "date": r["date"],
            "symbol": r["symbol"],
            "name": r["name"],
            "price": r["price"],
            "action": r["action"],
            "trade_type": r["trade_type"],
            "reason": r["reason"],
            "qty": r["qty"],
            "profit": r["profit"]
        })
        
    conn.close()
    return results

def get_trades_by_date_range(start_date: str, end_date: str):
    """지정된 기간의 매매 내역을 가져옵니다."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM trades 
        WHERE date >= ? AND date <= ?
        ORDER BY date DESC, id DESC
    """, (start_date, end_date))
    rows = cursor.fetchall()
    
    results = []
    for r in rows:
        results.append({
            "id": r["id"],
            "date": r["date"],
            "symbol": r["symbol"],
            "name": r["name"],
            "price": r["price"],
            "action": r["action"],
            "trade_type": r["trade_type"],
            "reason": r["reason"],
            "qty": r["qty"],
            "profit": r["profit"]
        })
        
    conn.close()
    return results

if __name__ == "__main__":
    init_db()
    print("Database initialized.")
