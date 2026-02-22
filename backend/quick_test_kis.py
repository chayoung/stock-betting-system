import os
import requests
import json
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

APP_KEY = os.getenv("KIS_APP_KEY")
APP_SECRET = os.getenv("KIS_APP_SECRET")
URL_BASE = os.getenv("KIS_URL", "https://openapivts.koreainvestment.com:29443")

def test_connection():
    if not APP_KEY or not APP_SECRET:
        print("❌ 오류: .env 파일에 KIS_APP_KEY와 KIS_APP_SECRET이 설정되어 있지 않습니다.")
        return

    print(f"🔍 KIS API 연결 테스트 시작 (URL: {URL_BASE})")
    
    # 1. 토큰 발급 테스트
    url = f"{URL_BASE}/oauth2/tokenP"
    headers = {"Content-Type": "application/json"}
    payload = {
        "grant_type": "client_credentials",
        "appkey": APP_KEY,
        "appsecret": APP_SECRET
    }
    
    try:
        res = requests.post(url, headers=headers, data=json.dumps(payload))
        if res.status_code == 200:
            token = res.json().get("access_token")
            print("✅ 접근 토큰 발급 성공!")
            
            # 2. 삼성전자 현재가 조회 테스트
            price_url = f"{URL_BASE}/uapi/domestic-stock/v1/quotations/inquire-price"
            price_headers = {
                "Content-Type": "application/json",
                "authorization": f"Bearer {token}",
                "appkey": APP_KEY,
                "appsecret": APP_SECRET,
                "tr_id": "FHKST01010100"
            }
            params = {
                "fid_cond_mrkt_div_code": "J",
                "fid_input_iscd": "005930"
            }
            
            price_res = requests.get(price_url, headers=price_headers, params=params)
            if price_res.status_code == 200:
                data = price_res.json()
                if data.get("rt_cd") == "0":
                    print(f"✅ 삼성전자 현재가 조회 성공: {data['output']['stck_prpr']}원")
                else:
                    print(f"❌ 조회 실패: {data.get('msg1')}")
            
            # 3. 계좌 잔고 조회 테스트
            cano = os.getenv("KIS_CANO")
            acnt_prdt_cd = os.getenv("KIS_ACNT_PRDT_CD", "01")
            
            if cano:
                balance_url = f"{URL_BASE}/uapi/domestic-stock/v1/trading/inquire-balance"
                balance_headers = {
                    "Content-Type": "application/json",
                    "authorization": f"Bearer {token}",
                    "appkey": APP_KEY,
                    "appsecret": APP_SECRET,
                    "tr_id": "VTTC8434R" if "openapivts" in URL_BASE else "TTTC8434R",
                    "custtype": "P"
                }
                balance_params = {
                    "CANO": cano,
                    "ACNT_PRDT_CD": acnt_prdt_cd,
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
                
                balance_res = requests.get(balance_url, headers=balance_headers, params=balance_params)
                if balance_res.status_code == 200:
                    b_data = balance_res.json()
                    if b_data.get("rt_cd") == "0":
                        output2 = b_data.get("output2", [{}])[0]
                        print(f"✅ 계좌 잔고 조회 성공!")
                        print(f"💰 총 평가 금액: {output2.get('tot_evlu_amt')}원")
                        print(f"💵 순자산 금액: {output2.get('nass_amt')}원")
                    else:
                        print(f"❌ 잔고 조회 실패: {b_data.get('msg1')}")
                else:
                    print(f"❌ 잔고 API 호출 실패 (HTTP {balance_res.status_code})")
        else:
            print(f"❌ 토큰 발급 실패 (HTTP {res.status_code}): {res.text}")
            
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")

if __name__ == "__main__":
    test_connection()
