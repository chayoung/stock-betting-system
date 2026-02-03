import asyncio
from notifier import send_telegram_message

async def main():
    print("텔레그램 전송 테스트를 시작합니다...")
    test_msg = "🚀 *종가배팅 시스템 테스트 메시지*\n\n연동이 성공적으로 완료되었습니다!"
    
    success = await send_telegram_message(test_msg)
    
    if success:
        print("\n✅ 메시지가 성공적으로 전송되었습니다! 텔레그램을 확인하세요.")
    else:
        print("\n❌ 전송에 실패했습니다. notifier.py의 토큰과 ID 설정을 다시 확인해 주세요.")

if __name__ == "__main__":
    asyncio.run(main())
