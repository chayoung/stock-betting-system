from fastapi import FastAPI, BackgroundTasks, Header, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from backtest import run_backtest
from notifier import send_telegram_message, format_backtest_report, send_sync_message
from database import get_today_trades, get_trades_by_date_range
import uvicorn
import asyncio
import os

# 어드민 계정 설정 (환경변수)
ADMIN_ID = os.getenv("ADMIN_ID", "admin")
ADMIN_PASS = os.getenv("ADMIN_PASS", "admin1234")

def verify_admin(x_admin_password: str = Header(None)):
    if x_admin_password != ADMIN_PASS:
        raise HTTPException(status_code=401, detail="Admin password required or invalid")
    return True

app = FastAPI(title="KOSPI/KOSDAQ Closing Price Betting System")

@app.post("/api/login")
async def admin_login(payload: dict):
    """
    어드민 로그인을 처리합니다.
    """
    username = payload.get("username")
    password = payload.get("password")
    
    if username == ADMIN_ID and password == ADMIN_PASS:
        return {"status": "success", "message": "로그인 성공"}
    else:
        raise HTTPException(status_code=401, detail="아이디 또는 비밀번호가 일치하지 않습니다.")

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
    """
    report = run_backtest(start, end)
    
    if notify:
        msg = format_backtest_report(report)
        background_tasks.add_task(send_sync_message, msg)
        
    return report

@app.get("/api/today_trades")
def get_today_trades_api():
    """
    오늘 실행된 매수/매도 내역을 반환합니다.
    """
    trades = get_today_trades()
    return {"status": "success", "data": trades}

@app.get("/api/trades_history")
def get_trades_history_api(start: str, end: str):
    """
    지정된 기간의 매수/매도 내역을 반환합니다.
    """
    trades = get_trades_by_date_range(start, end)
    return {"status": "success", "data": trades}

@app.post("/api/kis/test")
async def run_kis_test(background_tasks: BackgroundTasks, authorized: bool = Depends(verify_admin)):
    """
    KIS 모의계좌 정보 및 텔레그램 알림을 테스트합니다.
    """
    from check_balance_test import test_account_info
    background_tasks.add_task(test_account_info)
    return {"status": "success", "message": "KIS 계좌 테스트가 백그라운드에서 시작되었습니다. 텔레그램을 확인하세요."}

@app.post("/api/kis/batch")
async def run_kis_batch(background_tasks: BackgroundTasks, mode: str = "buy", force: bool = False, authorized: bool = Depends(verify_admin)):
    """
    주식 배치 작업을 수동으로 실행합니다.
    """
    from batch_run import run_daily_batch
    background_tasks.add_task(run_daily_batch, mode, force)
    return {"status": "success", "message": f"주식 배치({mode}, force={force}) 작업이 백그라운드에서 시작되었습니다."}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
