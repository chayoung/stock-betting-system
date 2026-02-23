import os
import sys
from datetime import datetime

# backend 디렉토리를 path에 추가하여 모듈 임포트 가능하게 함
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backtest import run_backtest
from database import init_db, insert_trade

def populate_february_backtest():
    print("🚀 2026년 2월 백테스트 데이터 적재 시작...")
    
    # 1. DB 초기화 (필요 시)
    init_db()
    
    # 2. 2월 한달간 백테스트 실행 (초기 자산 200만원)
    # 실제 2026년 데이터가 부족할 수 있으므로, 2024년 2월로 테스트하거나 사용자가 요청한 2월 기간 수행
    start_date = "2026-02-01"
    end_date = "2026-02-23" # 현재 날짜 근처까지
    
    print(f"기간: {start_date} ~ {end_date}")
    report = run_backtest(start_date=start_date, end_date=end_date, initial_balance=2000000)
    
    if "error" in report:
        print(f"❌ 백테스트 실행 중 오류 발생: {report['error']}")
        return

    trades = report.get('trades', [])
    print(f"📊 총 {len(trades)}건의 매매 결과 발견.")
    
    count = 0
    for trade in trades:
        # 매수/매매 수량 계산 (투자금액 / 매수가)
        # 매수가가 0인 경우 방지
        buy_price = trade['buy_price']
        if buy_price <= 0: continue
        
        qty = max(1, trade['invested'] // buy_price)
        
        # 3. 매수(BUY) 기록 추가
        insert_trade(
            date=trade['buy_date'],
            symbol=trade['symbol'],
            name=trade['name'],
            price=trade['buy_price'],
            action="BUY",
            trade_type="MOCK",
            reason="백테스트 자동적재",
            qty=qty,
            profit=0.0
        )
        
        # 4. 매도(SELL) 기록 추가
        insert_trade(
            date=trade['sell_date'],
            symbol=trade['symbol'],
            name=trade['name'],
            price=trade['sell_price'],
            action="SELL",
            trade_type="MOCK",
            reason="백테스트 자동적재",
            qty=qty,
            profit=float(trade['profit_krw'])
        )
        count += 1
        
    print(f"✅ {count}쌍(매수/매도)의 데이터를 DB에 성공적으로 적재했습니다.")

if __name__ == "__main__":
    populate_february_backtest()
