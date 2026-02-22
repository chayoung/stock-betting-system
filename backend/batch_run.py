import asyncio
import sys
from backtest import run_backtest
from data_loader import get_ohlcv_data
from notifier import send_telegram_message, format_backtest_report, send_sync_message
import kis_api
from datetime import datetime, timedelta
import pandas as pd
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

async def run_daily_batch(mode="buy", force=False):
    """
    매일 실행되는 배치 작업
    mode="buy": 장 마감 직전 매수 후보 알림
    mode="sell": 장 시작 직후 매도 알림
    """
    now = datetime.now()
    today_str = now.strftime('%Y-%m-%d')
    print(f"[{now}] 주식 배치 작업 시작 (모드: {mode})...")
    
    try:
        # KIS API 설정 확인
        if not kis_api.APP_KEY or not kis_api.APP_SECRET:
            raise Exception("KIS API 설정(KEY, SECRET)이 누락되었습니다. 컨테이너 환경 변수를 확인하세요.")

        # KIS API 토큰 발급
        token = kis_api.get_access_token()
        if not token:
            raise Exception("KIS API 접근 토큰 발급에 실패했습니다. API 키를 확인하세요.")

        # 1. 오늘이 실제 장이 열린 날인지 확인
        check_start = (now - timedelta(days=7)).strftime('%Y-%m-%d')
        samsung_df = get_ohlcv_data('005930', check_start, today_str)
        
        if not force and (samsung_df.empty or samsung_df.index[-1].strftime('%Y-%m-%d') != today_str):
            msg = f"📅 {today_str}: 오늘은 주식 시장이 열리지 않는 날(공휴일 또는 주말)입니다. 배치를 실행하지 않습니다. (강제 실행: --force)"
            print(msg)
            await send_telegram_message(msg)
            return

        if mode == "buy":
            # 매수 후보 종목 찾기 (종가배팅)
            report = run_backtest(start_date=today_str, end_date=today_str)
            if not report:
                raise Exception("백테스트 엔진 리포트 생성 실패")
            
            if not report.get('trades'):
                msg = f"📉 {today_str}: 오늘 종가배팅 조건에 맞는 종목이 없습니다."
                await send_telegram_message(msg)
            else:
                # 실제로 KIS API를 통해 주문 전송 (예시: 종목당 1주씩 시장가 매수)
                order_results = []
                for trade in report['trades']:
                    res = kis_api.place_order(token, trade['symbol'], qty=1, side="buy")
                    order_results.append(f"- {trade['name']}: {res.get('msg1')}")
                
                summary_msg = f"🚀 [모의투자 매수 집행] {today_str}\n"
                summary_msg += "\n".join(order_results) + "\n\n"
                summary_msg += format_backtest_report(report)
                await send_telegram_message(summary_msg)

        elif mode == "sell":
            # 전일 매수 종목 전량 매도 (잔고 조회 후 매도)
            balance_data = kis_api.get_balance(token)
            if balance_data and balance_data.get('rt_cd') == '0':
                stocks = balance_data.get('output1', [])
                sell_results = []
                for stock in stocks:
                    qty = int(stock.get('hldg_qty', 0))
                    if qty > 0:
                        symbol = stock.get('pdno')
                        name = stock.get('prdt_name')
                        res = kis_api.place_order(token, symbol, qty=qty, side="sell")
                        sell_results.append(f"- {name}({symbol}): {qty}주 매도 - {res.get('msg1')}")
                
                if sell_results:
                    summary_msg = f"💰 [모의투자 매도 집행] {today_str}\n"
                    summary_msg += "\n".join(sell_results)
                    await send_telegram_message(summary_msg)
                else:
                    await send_telegram_message(f"ℹ️ {today_str}: 현재 잔고에 매도할 종목이 없습니다.")

    except Exception as e:
        error_msg = f"⚠️ [배치 실행 오류] {today_str}\n사유: {str(e)}"
        print(error_msg)
        # 에러 발생 시 텔레그램으로 상세 사유 전송
        await send_telegram_message(error_msg)

    print(f"배치 작업({mode})이 완료되었습니다.")

if __name__ == "__main__":
    # 인자로 모드 전달 (기본값 buy)
    run_mode = "buy"
    is_force = False
    
    if len(sys.argv) > 1:
        run_mode = sys.argv[1]
    
    if "--force" in sys.argv:
        is_force = True
    
    asyncio.run(run_daily_batch(run_mode, is_force))
