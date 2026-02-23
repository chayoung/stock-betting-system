import FinanceDataReader as fdr
import pandas as pd
from datetime import datetime, timedelta

# 코스피, 코스닥 종목 리스트를 가져오는 함수
def get_stock_list():
    """
    KOSPI와 KOSDAQ 종목 리스트를 가져옵니다.
    """
    print("종목 리스트를 불러오는 중...")
    try:
        df_kospi = fdr.StockListing('KOSPI')
        df_kosdaq = fdr.StockListing('KOSDAQ')
        df_stocks = pd.concat([df_kospi, df_kosdaq], ignore_index=True)
    except Exception as e:
        print(f"데이터 로딩 실패: {e}")
        # 예외 상황 대비하여 빈 데이터프레임 반환
        return pd.DataFrame(columns=['Code', 'Name', 'Market'])
        
    return df_stocks[['Code', 'Name', 'Market']]

# 특정 기간의 OHLCV 데이터를 가져오는 함수
def get_ohlcv_data(symbol, start_date, end_date):
    """
    특정 종목의 시가, 고가, 저가, 종가, 거래량 데이터를 가져옵니다.
    """
    try:
        df = fdr.DataReader(symbol, start_date, end_date)
        return df
    except Exception as e:
        print(f"데이터 로딩 실패 ({symbol}): {e}")
        return pd.DataFrame()

if __name__ == "__main__":
    # 테스트 실행
    stocks = get_stock_list()
    print(f"총 {len(stocks)}개 종목 확인됨.")
    print(stocks.head())
    
    # 삼성전자(005930) 데이터 테스트
    test_data = get_ohlcv_data('005930', '2026-01-01', '2026-01-31')
    print("삼성전자 2026년 1월 데이터 샘플:")
    print(test_data.head())
