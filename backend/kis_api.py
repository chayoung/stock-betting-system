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

def get_access_token():
    """접근 토큰 발급 (OAuth2)"""
    url = f"{URL_BASE}/oauth2/tokenP"
    headers = {"Content-Type": "application/json"}
    payload = {
        "grant_type": "client_credentials",
        "appkey": APP_KEY,
        "appsecret": APP_SECRET
    }
    res = requests.post(url, headers=headers, data=json.dumps(payload))
    if res.status_code == 200:
        return res.json().get("access_token")
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
    
    res = requests.post(url, headers=headers, data=json.dumps(payload))
    return res.json()

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
