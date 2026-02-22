import pandas as pd

def select_betting_stocks(daily_data_dict, target_date, mode='SURGE'):
    """
    종가배팅 종목 선정 (모드 선택 가능)
    - SURGE: 거래량 급증 + 양봉 (Momentum)
    - PULLBACK: 기준봉 이후 거래량 급감 (Stable)
    - HYBRID: 두 가지 케이스를 모두 고려 (Optimized)
    """
    candidates = []
    
    for symbol, df in daily_data_dict.items():
        if target_date not in df.index:
            continue
            
        idx = df.index.get_loc(target_date)
        if idx < 10:
            continue
            
        today = df.iloc[idx]
        yesterday = df.iloc[idx-1]
        
        # --- Mode 1: SURGE (기존 급증형) ---
        is_surge = (today['Close'] > today['Open']) and \
                   (yesterday['Volume'] > 0 and today['Volume'] >= yesterday['Volume'] * 2)
        
        # --- Mode 2: PULLBACK (눌림목형) ---
        # 최근 10일 이내 breakout 탐색
        recent_df = df.iloc[idx-10:idx]
        breakout_found = False
        breakout_vol = 0
        breakout_close = 0
        breakout_open = 0
        
        for i in range(len(recent_df)):
            day = recent_df.iloc[i]
            if (day['Close'] - day['Open']) / day['Open'] * 100 >= 15:
                breakout_found = True
                breakout_vol = day['Volume']
                breakout_close = day['Close']
                breakout_open = day['Open']
        
        is_pullback = breakout_found and \
                      (today['Volume'] <= breakout_vol * 0.3) and \
                      (breakout_open < today['Close'] < breakout_close)

        # 선정 기준 적용
        selected = False
        reason = ""
        
        if mode == 'SURGE' and is_surge:
            selected = True
            reason = "급증"
        elif mode == 'PULLBACK' and is_pullback:
            selected = True
            reason = "눌림목"
        elif mode == 'HYBRID':
            if is_pullback:
                selected = True
                reason = "하이브리드(눌림)"
            elif is_surge and breakout_found: # 최근 강했던 종목이 다시 튀는 경우
                selected = True
                reason = "하이브리드( momentum)"
        
        if selected:
            candidates.append({
                'symbol': symbol,
                'name': today.get('Name', symbol),
                'close': today['Close'],
                'amount': today['Close'] * today['Volume'],
                'reason': reason
            })
            
    # 거래대금 상위 5개
    return sorted(candidates, key=lambda x: x['amount'], reverse=True)[:5]

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
