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
            # Markdown 파싱 에러 방지를 위해 기본적으로는 파싱을 하지 않거나 명시적으로 받을 수 있게 수정
            await bot.send_message(chat_id=CHAT_ID, text=message)
            print("텔레그램 메시지 전송 완료")
            return True
    except Exception as e:
        print(f"텔레그램 메시지 전송 실패: {e}")
        return False

def send_sync_message(message: str):
    """
    동기 방식으로 메시지를 보낼 수 있는 래퍼 함수입니다.
    이미 실행 중인 이벤트 루프가 있는 경우와 없는 경우를 모두 처리합니다.
    """
    try:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            # 이미 루프가 실행 중인 경우 (비동기 함수 내부에서 호출된 경우 등)
            # 이 경우에는 사실 await send_telegram_message를 쓰는 것이 정석이지만,
            # 하위 호환성을 위해 스레드 세이프하게 스케줄링만 시도하거나 경고를 출력합니다.
            import threading
            print("[주의] 이미 실행 중인 이벤트 루프에서 동기 래퍼를 호출했습니다. 비동기 await 사용을 권장합니다.")
            # 강제로 실행하려면 새로운 스레드에서 루프를 돌려야 함
            result = [None]
            def run_in_new_loop():
                new_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(new_loop)
                result[0] = new_loop.run_until_complete(send_telegram_message(message))
                new_loop.close()
            
            thread = threading.Thread(target=run_in_new_loop)
            thread.start()
            thread.join()
            return result[0]
        else:
            # 실행 중인 루프가 없는 경우
            return asyncio.run(send_telegram_message(message))
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
    # 백테스트 리포트처럼 마크다운이 필요한 경우를 위해 별도 함수 보강 가능
    # 여기서는 간단히 기본 발송 함수가 파싱을 안 하도록 수정함
    return msg

async def send_markdown_message(message: str):
    """마크다운 형식이 포함된 메시지를 보냅니다."""
    async with Bot(token=BOT_TOKEN) as bot:
        try:
            await bot.send_message(chat_id=CHAT_ID, text=message, parse_mode='Markdown')
            return True
        except Exception as e:
            print(f"마크다운 전송 실패, 일반 텍스트로 전환: {e}")
            await bot.send_message(chat_id=CHAT_ID, text=message)
            return True
