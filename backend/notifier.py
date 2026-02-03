import asyncio
from telegram import Bot
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 텔레그램 설정 (환경 변수 사용 권장)
# .env 파일 또는 시스템 환경 변수에 등록하여 사용하세요.
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "YOUR_CHAT_ID_HERE")
async def send_telegram_message(message: str):
    """
    텔레그램으로 메시지를 전송합니다.
    """
    if BOT_TOKEN == "YOUR_BOT_TOKEN" or CHAT_ID == "YOUR_CHAT_ID":
        print("[경고] 텔레그램 BOT_TOKEN 또는 CHAT_ID가 설정되지 않았습니다.")
        return False
        
    try:
        # python-telegram-bot v20+ 에서는 봇 객체를 컨텍스트 매니저로 사용하는 것이 권장됩니다.
        async with Bot(token=BOT_TOKEN) as bot:
            await bot.send_message(chat_id=CHAT_ID, text=message, parse_mode='Markdown')
            print("텔레그램 메시지 전송 완료")
            return True
    except Exception as e:
        print(f"텔레그램 메시지 전송 실패: {e}")
        return False

def send_sync_message(message: str):
    """
    동기 방식으로 메시지를 보낼 수 있는 래퍼 함수입니다.
    이벤트 루프가 상이한 환경에서도 안전하게 작동하도록 수정합니다.
    """
    try:
        # 새 이벤트 루프 생성 및 실행 (BackgroundTasks 환경 대응)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(send_telegram_message(message))
    except Exception as e:
        print(f"동기 메시지 전송 중 오류: {e}")
        return False

def format_backtest_report(report: dict):
    """
    백테스트 결과를 텔레그램용 메시지 형식으로 변환합니다.
    Numpy 타입을 일반 Python 타입으로 변환하여 오류를 방지합니다.
    """
    summary = report['summary']
    profit_rate = float(summary['total_profit_rate'])
    
    msg = f"📊 *종가배팅 백테스트 결과 보고*\n\n"
    msg += f"📅 기간: {summary['period']}\n"
    msg += f"📈 총 수익률: *{profit_rate:.2f}%*\n"
    msg += f"🎯 승률: {summary['win_rate']}%\n"
    msg += f"🔄 총 거래: {summary['total_trades']}회\n\n"
    
    msg += "🚀 *최근 거래 내역 (Top 3)*:\n"
    for trade in report['trades'][-3:]:
        p_rate = float(trade['profit_rate'])
        msg += f"- {trade['buy_date']}: {trade['name']} ({p_rate:.2f}%)\n"
        
    msg += "\n더 자세한 리포트는 대시보드에서 확인하세요!"
    return msg
