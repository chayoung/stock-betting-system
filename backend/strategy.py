import pandas as pd

def select_betting_stocks(daily_data_dict, target_date):
    """
    특정 날짜(target_date)에 종가배팅할 종목을 선정합니다.
    기준: 
    1. 당일 양봉 마감 (종가 > 시가)
    2. 거래량이 전일 대비 2배 이상 증가
    3. 거래대금 상위 5개 종목 선정 (간소화를 위해 거래량 * 종가 기준)
    """
    candidates = []
    
    for symbol, df in daily_data_dict.items():
        if target_date not in df.index:
            continue
            
        # 해당 날짜 데이터와 전일 데이터 추출
        idx = df.index.get_loc(target_date)
        if idx < 1: # 전일 데이터가 없으면 스킵
            continue
            
        today = df.iloc[idx]
        yesterday = df.iloc[idx-1]
        
        # 1. 양봉 조건
        if today['Close'] <= today['Open']:
            continue
            
        # 2. 거래량 급증 조건 (전일 대비 2배 이상)
        if yesterday['Volume'] == 0 or today['Volume'] < yesterday['Volume'] * 2:
            continue
            
        # 거래대금 계산 (종가 * 거래량)
        amount = today['Close'] * today['Volume']
        
        candidates.append({
            'symbol': symbol,
            'name': today.get('Name', symbol),
            'close': today['Close'],
            'amount': amount
        })
        
    # 거래대금 순으로 정렬하여 상위 5개 반환
    selected = sorted(candidates, key=lambda x: x['amount'], reverse=True)[:5]
    return selected

def calculate_returns(selected_stocks, daily_data_dict, buy_date):
    """
    선정된 종목들의 다음 날 시가 매도 수익률을 계산합니다.
    """
    results = []
    
    for stock in selected_stocks:
        symbol = stock['symbol']
        df = daily_data_dict[symbol]
        
        idx = df.index.get_loc(buy_date)
        if idx + 1 >= len(df): # 다음 거래일 데이터가 없으면 계산 불가
            continue
            
        next_day = df.iloc[idx + 1]
        
        buy_price = stock['close'] # 당일 종가 매수
        sell_price = next_day['Open'] # 다음 날 시가 매도
        
        profit_rate = (sell_price - buy_price) / buy_price * 100
        
        results.append({
            'symbol': symbol,
            'name': stock['name'],
            'buy_date': buy_date.strftime('%Y-%m-%d'),
            'sell_date': next_day.name.strftime('%Y-%m-%d'),
            'buy_price': int(buy_price),
            'sell_price': int(sell_price),
            'profit_rate': round(profit_rate, 2)
        })
        
    return results
