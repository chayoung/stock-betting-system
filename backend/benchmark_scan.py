import sys
print("벤치마크 스크립트 로딩 완료...")
import time
import pandas as pd
from datetime import datetime
import FinanceDataReader as fdr
from data_loader import get_ohlcv_data
from strategy import select_betting_stocks

def benchmark_scanning(count=1000):
    print(f"--- 상위 {count}개 종목 스캔 성능 테스트 시작 ---")
    start_total = time.time()
    
    # 1. 종목 리스트 로딩
    stocks = fdr.StockListing('KOSPI') # 테스트용으로 코스피만
    selected_symbols = stocks['Code'].tolist()[:count]
    
    today = datetime.now().strftime('%Y-%m-%d')
    fetch_start = (datetime.now() - pd.Timedelta(days=20)).strftime('%Y-%m-%d')
    
    # 2. 데이터 로딩 (가장 오래 걸리는 부분)
    print(f"데이터 로딩 중... ({count}개 종목)")
    start_loading = time.time()
    daily_data_dict = {}
    
    for i, symbol in enumerate(selected_symbols):
        if i > 0 and i % 100 == 0:
            print(f"진행 중: {i}/{count}...")
            
        try:
            df = get_ohlcv_data(symbol, fetch_start, today)
            if not df.empty:
                name = stocks[stocks['Code'] == symbol]['Name'].values[0]
                df['Name'] = name
                daily_data_dict[symbol] = df
        except Exception:
            continue
            
    end_loading = time.time()
    loading_time = end_loading - start_loading
    
    # 3. 전략 연산
    print("전략 연산 시작...")
    start_strategy = time.time()
    picks = select_betting_stocks(daily_data_dict, today, mode='HYBRID')
    end_strategy = time.time()
    strategy_time = end_strategy - start_strategy
    
    total_time = time.time() - start_total
    
    print("\n--- 결과 요약 ---")
    print(f"총 소요 시간: {total_time:.2f}초")
    print(f"- 데이터 로딩: {loading_time:.2f}초")
    print(f"- 전략 연산: {strategy_time:.4f}초")
    print(f"발견된 종목 수: {len(picks)}개")
    if picks:
        for p in picks:
            print(f"- {p['name']} ({p['symbol']}): {p['reason']}")
            
    # 마감 시간(3시 20분)까지 충분한지 체크
    # 현재 시간이 1시 15분이라고 가정하면 약 2시간 여유
    print(f"\n최종 판정: {'안정적' if total_time < 300 else '주의 요망 (5분 이상 소요)'}")

if __name__ == "__main__":
    benchmark_scanning(1000)
