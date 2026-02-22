import os
import requests
import json
from dotenv import load_dotenv
from notifier import send_sync_message

# .env 파일 로드
load_dotenv()

APP_KEY = os.getenv("KIS_APP_KEY")
APP_SECRET = os.getenv("KIS_APP_SECRET")
CANO = os.getenv("KIS_CANO") # 계좌번호 앞 8자리
ACNT_PRDT_CD = os.getenv("KIS_ACNT_PRDT_CD", "01") # 계좌번호 뒤 2자리 (보통 01)
URL_BASE = os.getenv("KIS_URL", "https://openapivts.koreainvestment.com:29443") # 기본값은 모의투자

def get_access_token():
    """접근 토큰 발급"""
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
    else:
        print(f"Error getting token: {res.text}")
        return None

def get_stock_price(token, symbol):
    """현재가 조회"""
    url = f"{URL_BASE}/uapi/domestic-stock/v1/quotations/inquire-price"
    headers = {
        "Content-Type": "application/json",
        "authorization": f"Bearer {token}",
        "appkey": APP_KEY,
        "appsecret": APP_SECRET,
        "tr_id": "FHKST01010100" # 주식 현재가 시세 tr_id
    }
    params = {
        "fid_cond_mrkt_div_code": "J", # 주식
        "fid_input_iscd": symbol
    }
    res = requests.get(url, headers=headers, params=params)
    if res.status_code == 200:
        return res.json()
    else:
        print(f"Error getting price: {res.text}")
        return None

def get_balance(token):
    """주식 잔고 조회"""
    url = f"{URL_BASE}/uapi/domestic-stock/v1/trading/inquire-balance"
    
    # KIS API 문서 - 국내주식 잔고조회 (주식)
    # TR_ID: TTTC8434R (실전투자), VTTC8434R (모의투자)
    tr_id = "TTTC8434R" if "openapi.koreainvestment.com" in URL_BASE else "VTTC8434R"
    
    headers = {
        "Content-Type": "application/json",
        "authorization": f"Bearer {token}",
        "appkey": APP_KEY,
        "appsecret": APP_SECRET,
        "tr_id": tr_id,
        "custtype": "P" # 개인
    }
    params = {
        "CANO": CANO,
        "ACNT_PRDT_CD": ACNT_PRDT_CD,
        "AFHR_FLPR_YN": "N", # 시간외단일가여부 (N:기본)
        "OFRT_WTHR_YN": "N", # 오프셋여부 (N:기본)
        "PRDT_DVSN_CD": "01", # 상품구분코드 (01:주식)
        "TR_CONT_QUERY_SEQ": "", # 연속조회검색조건
        "UNPR_DVSN_CD": "01", # 단가구분코드 (01:평균단가)
        "CTX_AREA_FK100": "", # 연속조회키100
        "CTX_AREA_NK100": ""  # 연속조회키100
    }
    res = requests.get(url, headers=headers, params=params)
    if res.status_code == 200:
        return res.json()
    else:
        print(f"Error getting balance: {res.text}")
        return None

def main():
    if not APP_KEY or not APP_SECRET:
        print("Error: KIS_APP_KEY and KIS_APP_SECRET must be set in .env file.")
        return

    print("Checking KIS API connection...")
    token = get_access_token()
    
    msg = "🚀 *KIS API 연동 테스트 결과*\n\n"
    
    if token:
        print("Success: Access token acquired.")
        msg += "✅ 접근 토큰 발급 성공\n"
        
        # 1. 삼성전자(005930) 정보 조회 테스트
        symbol = "005930"
        print(f"\n[Test 1: Stock Price Inquiry ({symbol})]")
        data = get_stock_price(token, symbol)
        
        if data and data.get("rt_cd") == "0":
            output = data.get("output", {})
            price = output.get('stck_prpr')
            print(f"Name: {output.get('hts_kor_isnm')}")
            print(f"Current Price: {price}")
            msg += f"✅ 종목 조회 성공 (삼성전자: {price}원)\n"
        else:
            print(f"Error in price retrieval: {data.get('msg1') if data else 'Unknown error'}")
            msg += "❌ 종목 조회 실패\n"

        # 2. 잔고 조회 테스트
        print("\n[Test 2: Account Balance Inquiry]")
        balance_data = get_balance(token)
        
        if balance_data and balance_data.get("rt_cd") == "0":
            output2 = balance_data.get("output2", [{}])[0]
            total_asset = output2.get('tot_evlu_amt')
            print(f"Account: {CANO}-{ACNT_PRDT_CD}")
            print(f"Total Asset: {total_asset} KRW")
            msg += f"✅ 잔고 조회 성공 (총 자산: {total_asset}원)\n"
        else:
            print(f"Error in balance retrieval: {balance_data.get('msg1') if balance_data else 'Unknown error'}")
            msg += "❌ 잔고 조회 실패\n"
    else:
        print("Failed to get access token.")
        msg += "❌ 접근 토큰 발급 실패\n"

    # 텔레그램 메시지 전송
    print("\n텔레그램 메시지 전송 중...")
    send_sync_message(msg)

if __name__ == "__main__":
    main()
