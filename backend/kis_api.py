import os
import requests
import json
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

APP_KEY = os.getenv("KIS_APP_KEY")
APP_SECRET = os.getenv("KIS_APP_SECRET")
CANO = os.getenv("KIS_CANO")
ACNT_PRDT_CD = os.getenv("KIS_ACNT_PRDT_CD", "01")
# 기본값은 모의투자 서버
URL_BASE = os.getenv("KIS_URL", "https://openapivts.koreainvestment.com:29443")

import time

def check_config():
    """필수 설정 확인"""
    if not APP_KEY or not APP_SECRET or not CANO:
        missing = []
        if not APP_KEY: missing.append("KIS_APP_KEY")
        if not APP_SECRET: missing.append("KIS_APP_SECRET")
        if not CANO: missing.append("KIS_CANO")
        print(f"[오류] KIS API 필수 설정 중 다음 항목이 누락되었습니다: {', '.join(missing)}")
        return False
    return True

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
os.makedirs(DATA_DIR, exist_ok=True)
TOKEN_FILE = os.path.join(DATA_DIR, "token_cache.json")

def get_access_token(retries=3, delay=2):
    """접근 토큰 발급 (OAuth2) - 캐싱 및 재시도 로직 포함"""
    if not check_config():
        return None

    # 1. 캐시된 토큰 확인 (12시간 이내)
    if os.path.exists(TOKEN_FILE):
        try:
            with open(TOKEN_FILE, "r") as f:
                cache = json.load(f)
                # 발급된 지 12시간 이내면 재사용
                if time.time() - cache.get("timestamp", 0) < 3600 * 12:
                    print("✅ 캐시된 KIS 토큰 사용")
                    return cache.get("access_token")
        except:
            pass

    url = f"{URL_BASE}/oauth2/tokenP"
    headers = {"Content-Type": "application/json"}
    payload = {
        "grant_type": "client_credentials",
        "appkey": APP_KEY,
        "appsecret": APP_SECRET
    }
    
    for i in range(retries):
        try:
            res = requests.post(url, headers=headers, data=json.dumps(payload), timeout=10)
            if res.status_code == 200:
                token_data = res.json()
                access_token = token_data.get("access_token")
                
                # 토큰 캐시 저장
                with open(TOKEN_FILE, "w") as f:
                    json.dump({
                        "access_token": access_token,
                        "timestamp": time.time()
                    }, f)
                
                print("✅ 새 KIS 액세스 토큰 발급 및 저장 성공")
                return access_token
            else:
                print(f"⚠️ 토큰 발급 시도 {i+1}/{retries} 실패: {res.status_code} {res.text}")
        except Exception as e:
            print(f"⚠️ 토큰 발급 중 예외 발생 {i+1}/{retries}: {e}")
            
        if i < retries - 1:
            time.sleep(delay)
            
    return None

def place_order(token, symbol, qty, price=0, side="buy"):
    """
    주식 주문 전송
    side: "buy" (매수), "sell" (매도)
    price: 0이면 시장가(지정금액 없음)
    """
    # TR_ID 설정: 모의투자 기준 (실전은 다름)
    # VTTC8434U: 매수, VTTC8435U: 매도 (모의투자)
    is_vts = "openapivts" in URL_BASE
    if side == "buy":
        tr_id = "VTTC8434U" if is_vts else "TTTC0802U"
    else:
        tr_id = "VTTC8435U" if is_vts else "TTTC0801U"

    url = f"{URL_BASE}/uapi/domestic-stock/v1/trading/order-cash"
    headers = {
        "Content-Type": "application/json",
        "authorization": f"Bearer {token}",
        "appkey": APP_KEY,
        "appsecret": APP_SECRET,
        "tr_id": tr_id,
        "custtype": "P"
    }
    
    payload = {
        "CANO": CANO,
        "ACNT_PRDT_CD": ACNT_PRDT_CD,
        "PDNO": symbol,
        "ORD_DVSN": "01", # 01: 시장가, 00: 지정가
        "ORD_QTY": str(qty),
        "ORD_UNPR": str(price) if price > 0 else "0"
    }
    
    # 429 과부하 방지를 위한 미세 지연 (Trading Bot Robustness Skill 적용)
    time.sleep(0.2)
    
    try:
        res = requests.post(url, headers=headers, data=json.dumps(payload), timeout=10)
        res_data = res.json()
        
        # 상세 에러 로깅 (EGW00001 등 대응)
        if res_data.get('rt_cd') != '0':
            print(f"⚠️ 주문 실패 [{symbol}]: {res_data.get('rt_cd')} - {res_data.get('msg1')}")
            
        return res_data
    except Exception as e:
        print(f"🚨 주문 시도 중 통신 에러 발생: {e}")
        return {"rt_cd": "E_CONN", "msg1": str(e)}

def get_balance(token):
    """주식 잔고 및 예수금 조회"""
    url = f"{URL_BASE}/uapi/domestic-stock/v1/trading/inquire-balance"
    tr_id = "VTTC8434R" if "openapivts" in URL_BASE else "TTTC8434R"
    
    headers = {
        "Content-Type": "application/json",
        "authorization": f"Bearer {token}",
        "appkey": APP_KEY,
        "appsecret": APP_SECRET,
        "tr_id": tr_id,
        "custtype": "P"
    }
    params = {
        "CANO": CANO,
        "ACNT_PRDT_CD": ACNT_PRDT_CD,
        "AFHR_FLPR_YN": "N",
        "OFL_YN": "",
        "INQR_DVSN": "02",
        "UNPR_DVSN": "01",
        "FUND_STTL_ICLD_YN": "N",
        "FNCG_AMT_AUTO_RDPT_YN": "N",
        "PRDT_DVSN_CD": "01",
        "PRCS_DVSN": "01",
        "TR_CONT_QUERY_SEQ": "",
        "CTX_AREA_FK100": "",
        "CTX_AREA_NK100": ""
    }
    res = requests.get(url, headers=headers, params=params)
    if res.status_code == 200:
        return res.json()
    return None
