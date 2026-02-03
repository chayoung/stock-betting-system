# 📊 주식 종가배팅 시스템 (Stock Betting System)

코스피(KOSPI) 및 코스닥(KOSDAQ) 종목을 대상으로 한 종가배팅 전략 백테스트 및 리포트 시각화 도구입니다.

## 🚀 주요 기능
- **자동 백테스트**: 선택한 기간 동안의 종가배팅 전략(당일 종가 매수 → 익일 시가 매도) 수익률 시뮬레이션.
- **시장 데이터 연동**: `FinanceDataReader`를 사용하여 KRX 실시간 데이터 및 KOSPI 지수와 비교.
- **프리미엄 대시보드**: React 기반의 다크 테마 UI를 통해 수익률 추이, 승률, 상세 거래 내역 시각화.
- **텔레그램 알림**: 백테스트 완료 시 총 수익률 및 주요 거래 내역을 텔레그램으로 즉시 발송.
- **스마트 기간 설정**: 영업일 기준 최근 5일 자동 조회 기능 제공.

## 🛠 기술 스택
- **Backend**: Python, FastAPI, Pandas, FinanceDataReader
- **Frontend**: React (Vite), Recharts, Axios, Lucide React
- **Notification**: Telegram Bot API

## 📋 설치 및 실행 방법

### Backend
1. **가상환경 설정**:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```
2. **패키지 설치**:
   ```bash
   pip install -r requirements.txt
   ```
3. **서버 실행**:
   ```bash
   python main.py
   ```

### Frontend
1. **패키지 설치**:
   ```bash
   cd frontend
   npm install
   ```
2. **실행**:
   ```bash
   npm run dev
   ```

## 🔔 텔레그램 설정
`backend/notifier.py` 파일 내의 `BOT_TOKEN`과 `CHAT_ID`를 본인의 정보로 수정하여 알림을 받을 수 있습니다.

## 📈 백테스트 전략 상세
- **선정 기준**:
  - 당일 양봉 마감
  - 전일 대비 거래량 2배 이상 증가
  - 거래대금 상위 종목 우선
- **매매 로직**: 당일 종가 매수 → 익일 시가 매도

---
본 프로젝트는 개인적인 투자 참고용으로 제작되었으며, 모든 투자의 책임은 투자자 본인에게 있습니다.
