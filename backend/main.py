from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from backtest import run_backtest
from notifier import send_telegram_message, format_backtest_report, send_sync_message
import uvicorn
import asyncio

app = FastAPI(title="KOSPI/KOSDAQ Closing Price Betting System")

# CORS 설정 (프론트엔드 연동용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "종가배팅 시스템 API 서버가 가동 중입니다."}

@app.get("/api/backtest")
def get_backtest_report(background_tasks: BackgroundTasks, start: str = None, end: str = None, notify: bool = False):
    """
    백테스트 리포트를 생성하여 반환합니다.
    start/end가 없으면 최근 5영업일을 자동으로 분석합니다.
    """
    report = run_backtest(start, end)
    
    if notify:
        msg = format_backtest_report(report)
        # BackgroundTasks를 통해 응답 반환 후 텔레그램 메시지 전송 실행
        background_tasks.add_task(send_sync_message, msg)
        
    return report

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
