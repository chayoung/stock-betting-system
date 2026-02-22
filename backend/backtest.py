import pandas as pd
from data_loader import get_stock_list, get_ohlcv_data
from strategy import select_betting_stocks, calculate_returns
from datetime import datetime
import os

def run_backtest(start_date=None, end_date=None, initial_balance=2000000):
    """
    지정된 기간 동안 종가배팅 백테스트를 실행합니다.
    start_date, end_date가 None일 경우 최근 5영업일을 자동으로 선정합니다.
    """
    # 1. 종목 리스트 및 기준 종목(삼성전자) 데이터 로드
    stocks = get_stock_list()
    samsung_symbol = '005930'
    
    # 분석 기간 설정을 위한 기준 데이터 (충분한 기간 확보)
    if start_date and end_date:
        fetch_start = (datetime.strptime(start_date, '%Y-%m-%d') - pd.Timedelta(days=15)).strftime('%Y-%m-%d')
        fetch_end = (datetime.strptime(end_date, '%Y-%m-%d') + pd.Timedelta(days=5)).strftime('%Y-%m-%d')
    else:
        # 최근 5영업일을 찾기 위해 최근 한 달치 데이터를 먼저 가져옴
        fetch_end = datetime.now().strftime('%Y-%m-%d')
        fetch_start = (datetime.now() - pd.Timedelta(days=30)).strftime('%Y-%m-%d')

    samsung_df = get_ohlcv_data(samsung_symbol, fetch_start, fetch_end)
    if samsung_df.empty:
        return {"error": "기준 데이터를 가져올 수 없습니다."}

    # 실제 영업일 리스트 확인
    all_trading_days = samsung_df.index
    
    if not start_date or not end_date:
        # 최근 5영업일 선정 (오늘이 휴일일 수 있으므로 마지막 영업일부터 역산)
        # 종가배팅 특성상 다음 날 시가가 있어야 하므로, 마지막 날은 제외하거나 마지막 전날까지 수행
        # '최근 5일'은 배팅이 일어나는 5개 날짜를 의미함
        trading_days = all_trading_days[-6:-1] # 마지막 날은 시가 매도 데이터 확인용으로만 쓰고 배팅은 그 전 5일간 수행
        start_date = trading_days[0].strftime('%Y-%m-%d')
        end_date = trading_days[-1].strftime('%Y-%m-%d')
    else:
        trading_days = all_trading_days[(all_trading_days >= start_date) & (all_trading_days <= end_date)]

    print(f"{start_date}부터 {end_date}까지 (총 {len(trading_days)} 영업일) 백테스트 시작...")
    print(f"초기 예수금: {initial_balance:,}원")
    
    # 2. 분석 대상 종목 선정 (상위 200개)
    selected_symbols = stocks['Code'].tolist()[:200] 
    daily_data_dict = {}
    print("데이터 로딩 중...")
    
    for symbol in selected_symbols:
        df = get_ohlcv_data(symbol, fetch_start, fetch_end)
        if not df.empty:
            name = stocks[stocks['Code'] == symbol]['Name'].values[0]
            market = stocks[stocks['Code'] == symbol]['Market'].values[0]
            df['Name'] = name
            df['Market'] = market
            daily_data_dict[symbol] = df

    # 3. KOSPI 지수 데이터 가져오기 (비교용)
    kospi_data = get_ohlcv_data('KS11', fetch_start, fetch_end)
    
    total_logs = []
    daily_summary = []
    current_balance = initial_balance
    
    # 4. 날짜별 시뮬레이션
    for day in trading_days:
        print(f"{day.strftime('%Y-%m-%d')} 분석 중 (잔고: {int(current_balance):,}원)...")
        
        picks = select_betting_stocks(daily_data_dict, day)
        if not picks:
            daily_summary.append({
                'date': day.strftime('%Y-%m-%d'),
                'avg_return': 0,
                'balance': int(current_balance),
                'count': 0
            })
            continue
            
        day_results = calculate_returns(picks, daily_data_dict, day)
        if day_results:
            # 자금 배분: 당일 선정된 종목 수만큼 균등 배분
            allocation = current_balance / len(day_results)
            day_profit_krw = 0
            
            for r in day_results:
                r['market'] = daily_data_dict[r['symbol']]['Market'].iloc[0]
                # 개별 종목 수익금 계산
                profit_krw = allocation * (r['profit_rate'] / 100)
                day_profit_krw += profit_krw
                r['profit_krw'] = int(profit_krw)
                r['invested'] = int(allocation)
            
            current_balance += day_profit_krw
            total_logs.extend(day_results)
            
            avg_return = sum([r['profit_rate'] for r in day_results]) / len(day_results)
            kospi_return = 0
            if day in kospi_data.index:
                idx_k = kospi_data.index.get_loc(day)
                if idx_k > 0:
                    prev_close = kospi_data.iloc[idx_k-1]['Close']
                    curr_close = kospi_data.iloc[idx_k]['Close']
                    kospi_return = (curr_close - prev_close) / prev_close * 100

            daily_summary.append({
                'date': day.strftime('%Y-%m-%d'),
                'avg_return': round(float(avg_return), 2),
                'kospi_return': round(float(kospi_return), 2),
                'balance': int(current_balance),
                'profit_krw': int(day_profit_krw),
                'count': len(day_results)
            })

    # 5. 결과 집계
    total_return_pct = ((current_balance - initial_balance) / initial_balance * 100)
    win_trades = [r for r in total_logs if r['profit_rate'] > 0]
    win_rate = (len(win_trades) / len(total_logs) * 100) if total_logs else 0
    
    report = {
        'summary': {
            'initial_balance': initial_balance,
            'final_balance': int(current_balance),
            'total_profit_krw': int(current_balance - initial_balance),
            'total_profit_rate': round(float(total_return_pct), 2),
            'win_rate': round(float(win_rate), 2),
            'total_trades': int(len(total_logs)),
            'period': f"{start_date} ~ {end_date}"
        },
        'daily_returns': daily_summary,
        'trades': total_logs,
        'start_date': start_date,
        'end_date': end_date
    }
    
    return report

if __name__ == "__main__":
    # 2026년 1월 한달간 테스트 (실제 데이터가 없으므로 현재 날짜 기준으로 샘플 테스트 가능)
    # 하지만 사용자가 2026년 1월을 요청했으므로 코드 구조는 유지
    # 테스트를 위해 최근 데이터로 실행해볼 수 있음
    result = run_backtest('2024-01-01', '2024-01-31')
    print("\n[백테스트 결과 요약]")
    print(f"누적 수익률: {result['summary']['total_profit_rate']}%")
    print(f"승률: {result['summary']['win_rate']}%")
    print(f"총 거래 횟수: {result['summary']['total_trades']}")
