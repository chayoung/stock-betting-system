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
from database import init_db, insert_trade

load_dotenv()

# DB 초기화
init_db()

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
            
        # 모의투자 / 실전투자 여부 확인
        trade_type = "MOCK" if "openapivts" in kis_api.URL_BASE else "REAL"

        # 1. 오늘이 장이 열리는 날인지 확인 (FDR 데이터 기준)
        # 오전(sell)에는 오늘 데이터가 아직 없으므로 마지막 영업일이 오늘 또는 어제(평일)인지 확인
        check_start = (now - timedelta(days=10)).strftime('%Y-%m-%d')
        samsung_df = get_ohlcv_data('005930', check_start, today_str)
        
        last_trading_day = samsung_df.index[-1].strftime('%Y-%m-%d') if not samsung_df.empty else None
        
        # 주말/공휴일 체크: 주말이면 무조건 패스
        if not force and now.weekday() >= 5: # 5: Sat, 6: Sun
            print(f"📅 {today_str}: 주말이므로 배치를 실행하지 않습니다.")
            return

        if not force:
            if mode == "buy":
                # 오후 매수 시점: 오늘 데이터가 반드시 있어야 함
                if last_trading_day != today_str:
                    msg = f"⏳ {today_str}: 아직 오늘의 주가 데이터가 거래소에 반영되지 않았습니다. (마지막 영업일: {last_trading_day})"
                    print(msg)
                    # 너무 일찍 실행된 경우 등을 고려해 텔레그램은 생략하거나 별도 처리
                    return
            else:
                # 오전 매도 시점: 최근 영업일이 어제(또는 가까운 과거)여야 함
                # 오늘 데이터가 없는 것은 정상임
                if last_trading_day is None:
                    print(f"⚠️ {today_str}: 영업일 데이터를 확인할 수 없습니다.")
                    return
                
                if last_trading_day > today_str: # 미래 데이터가 있을 순 없지만 방어코드
                     pass 
                elif (now - samsung_df.index[-1]).days > 4: # 마지막 영업일이 너무 멀면 (연휴 등)
                    msg = f"📅 {today_str}: 장기 휴장 중이거나 데이터 확인이 필요합니다. (마지막 영업일: {last_trading_day})"
                    print(msg)
                    return

        print(f"✅ 장 개장 확인됨 (마지막 영업일: {last_trading_day}) - {mode} 모드 시작")

        if mode == "buy":
            # 매수 후보 종목 찾기 (종가배팅)
            report = run_backtest(start_date=today_str, end_date=today_str)
            if not report:
                raise Exception("백테스트 엔진 리포트 생성 실패")
            
            # 'trades'는 다음날 데이터가 있어야 생성되므로, 당일 배팅은 'signals'를 사용
            targets = report.get('signals', [])
            
            if not targets:
                msg = f"📉 {today_str}: 오늘 종가배팅 조건에 맞는 종목이 없습니다."
                await send_telegram_message(msg)
            else:
                # 1. 예수금 확인 (현금 잔고 확인)
                balance_data = kis_api.get_balance(token)
                cash_available = 0
                if balance_data and balance_data.get('rt_cd') == '0':
                    # output2 (계좌 잔고 요약)에서 dsc_psbl_amt(출금가능금액/현금) 확인
                    summary = balance_data.get('output2', [{}])[0]
                    cash_available = float(summary.get('dnca_tot_amt', 0)) # 주문가능 현금 총액
                    print(f"💰 현재 주문 가능 현금: {cash_available:,.0f}원")
                
                # 실제로 KIS API를 통해 주문 전송
                order_results = []
                success_count = 0
                
                for trade in targets:
                    # 간단한 예산 전략: 균등 배분 (종목당 금액 설정 시 로직 보강 가능)
                    # 여기서는 1주씩 매수하되 현금이 부족하면 건너뜀
                    if cash_available < (trade.get('close', 0) * 1.01): # 1% 수수료/오차 고려
                        order_results.append(f"- {trade['name']}: ❌ 잔고 부족 (필요: {trade.get('close', 0):,.0f}원)")
                        continue

                    res = kis_api.place_order(token, trade['symbol'], qty=1, side="buy")
                    msg1 = res.get('msg1', '알 수 없는 결과')
                    order_results.append(f"- {trade['name']}: {msg1}")
                    
                    # 주문 성공/접수 시 DB 기록
                    if res.get('rt_cd') == '0':
                        success_count += 1
                        buy_price = trade.get('buy_price') or trade.get('close', 0)
                        insert_trade(
                            date=today_str,
                            symbol=trade['symbol'],
                            name=trade['name'],
                            price=float(buy_price),
                            action="BUY",
                            trade_type=trade_type,
                            reason=trade.get('reason', ''),
                            qty=1,
                            profit=0.0
                        )
                        # 예수금 차감 (근사치)
                        cash_available -= buy_price
                
                summary_msg = f"🚀 [{trade_type} 매수 집행 리포트] {today_str}\n"
                summary_msg += f"✅ 성공: {success_count}건 / 전체: {len(targets)}건\n\n"
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
                        
                        # 주문 성공/접수 시 DB 기록
                        if res.get('rt_cd') == '0':
                            profit_amt = float(stock.get('evlu_pfls_amt', 0))
                            insert_trade(
                                date=today_str,
                                symbol=symbol,
                                name=name,
                                price=float(stock.get('prpr', 0)), # 현재가(종가/시가) 기준
                                action="SELL",
                                trade_type=trade_type,
                                reason="전일 종가배팅 매도",
                                qty=qty,
                                profit=profit_amt
                            )
                
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
