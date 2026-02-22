import asyncio
import os
from datetime import datetime
from dotenv import load_dotenv
import kis_api
from notifier import send_telegram_message

# .env 파일 로드
load_dotenv()

async def test_account_info():
    print("🔍 KIS 모의계좌 정보 및 텔레그램 알림 테스트를 시작합니다...")
    
    try:
        # 1. 접근 토큰 발급 테스트
        print("\n1. 토큰 발급 테스트 중...")
        token = kis_api.get_access_token()
        if token:
            print("✅ KIS API 접근 토큰 발급 성공!")
        else:
            print("❌ 토큰 발급 실패. .env 파일의 APP_KEY, APP_SECRET을 확인하세요.")
            return

        # 2. 계좌 잔고 조회 테스트
        print("\n2. 계좌 잔고 조회 테스트 중...")
        balance = kis_api.get_balance(token)
        
        if balance and balance.get('rt_cd') == '0':
            account_info = balance.get('output2', [{}])[0]
            deposit = account_info.get('dnca_tot_amt', '0') # 예수금
            total_eval = account_info.get('tot_evlu_amt', '0') # 총 평가금액
            
            success_msg = (
                f"✅ [KIS 모의계좌 조회 성공]\n"
                f"💰 예수금: {int(deposit):,}원\n"
                f"📈 총 평가금액: {int(total_eval):,}원\n"
                f"🤖 테스트 시각: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
            print(success_msg)
            
            # 3. 텔레그램 알림 테스트
            print("\n3. 텔레그램 알림 전송 중...")
            sent = await send_telegram_message(success_msg)
            if sent:
                print("✅ 텔레그램 메시지 전송 성공!")
            else:
                print("❌ 텔레그램 전송 실패. .env의 BOT_TOKEN, CHAT_ID를 확인하세요.")
        else:
            error_msg = f"❌ 잔고 조회 실패: {balance.get('msg1', '알 수 없는 오류')}"
            print(error_msg)
            await send_telegram_message(f"⚠️ [KIS 테스트 실패]\n{error_msg}")

    except Exception as e:
        print(f"❌ 테스트 중 예외 발생: {e}")
        await send_telegram_message(f"⚠️ [KIS 테스트 오류]\n사유: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_account_info())
