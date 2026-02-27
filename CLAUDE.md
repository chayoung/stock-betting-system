# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 프로젝트 개요

한국 주식시장(KOSPI/KOSDAQ) 대상 **종가배팅 전략** 백테스트 및 실시간 자동 매매 보조 시스템.
- 당일 종가(15:20) 매수 → 익일 시가(09:00) 매도 전략
- KIS(한국투자증권) OpenAPI 연동, 텔레그램 알림, Docker 기반 NAS 배포

## 개발 명령어

### Backend (Python/FastAPI)
```bash
cd backend
pip install -r requirements.txt   # 의존성 설치
python main.py                    # 개발 서버 실행 (http://localhost:8000)
python backtest.py                # 백테스트 단독 실행 (직접 실행 가능)
python batch_run.py [buy|sell] [--force]   # 배치 수동 실행
python data_loader.py             # 데이터 로딩 테스트
```

### Frontend (React/Vite)
```bash
cd frontend
npm install       # 의존성 설치
npm run dev       # 개발 서버 (http://localhost:5173)
npm run build     # 프로덕션 빌드
npm run lint      # ESLint 린팅
npm run preview   # 빌드 결과물 미리보기
```

### Docker / 배포
```bash
./deploy.sh       # 백엔드+프론트엔드 이미지 빌드 후 Harbor에 푸시
# NAS에서는 docker-compose.yml 사용 (Portainer 또는 CLI)
```

## 아키텍처

```
backend/
├── main.py           # FastAPI 앱 진입점, API 엔드포인트 정의
├── backtest.py       # 백테스트 엔진 (run_backtest 함수)
├── batch_run.py      # 일일 배치 (매수/매도 자동 실행, DB 기록)
├── strategy.py       # 종목 선정 전략 (SURGE/PULLBACK/HYBRID)
├── data_loader.py    # FinanceDataReader로 OHLCV 데이터 fetch
├── database.py       # SQLite 연동 (backend/data/stocks.db)
├── kis_api.py        # KIS OpenAPI 래퍼 (토큰, 주문, 잔고)
├── notifier.py       # 텔레그램 알림 전송
└── .env              # 환경변수 (KIS API 키, 텔레그램 토큰 등)

frontend/
├── src/App.jsx       # 단일 컴포넌트 구조 - 모든 UI 로직 및 API 통신
├── nginx.conf        # /api/* 프록시 → backend:8000
└── vite.config.js    # Vite 설정

docker-compose.yml    # 4개 서비스: backend, frontend, batch-job, watchtower
```

## 데이터 흐름

1. **백테스트 흐름**: `data_loader.get_stock_list()` → `data_loader.get_ohlcv_data()` → `strategy.select_betting_stocks()` → `strategy.calculate_returns()` → `backtest.run_backtest()` 리포트 반환
2. **배치 흐름**: `batch_run.run_daily_batch(mode)` → KIS API 토큰 획득 → 삼성전자(005930) 데이터로 장 개장 여부 확인 → 매수/매도 집행 → `database.insert_trade()` → 텔레그램 알림
3. **프론트엔드**: `App.jsx` 단일 파일에서 Axios로 `/api/*` 호출. Nginx가 백엔드로 프록시.

## 핵심 설계 결정사항

- **분석 대상**: 상위 300개 종목만 스캔 (`backtest.py:46` - 성능/속도 절충)
- **종목 선정**: 거래대금 상위 5개 (`strategy.py:75`)
- **KIS 토큰 캐싱**: `backend/data/token_cache.json`에 12시간 캐시 (`kis_api.py:44`)
- **DB**: SQLite (`backend/data/stocks.db`) - Docker 볼륨 마운트로 영속성 유지
- **장 개장 확인**: 삼성전자(005930) 데이터 유무로 판단 (공휴일, 주말 자동 스킵)
- **어드민 인증**: `X-Admin-Password` 헤더 방식 (KIS 제어 API에만 적용)

## 환경변수 설정 (backend/.env)

`backend/.env.example` 참조. Docker 실행 시 `docker-compose.yml`의 `environment` 섹션으로 주입.

| 변수 | 설명 |
|------|------|
| `KIS_URL` | 모의투자: `https://openapivts.koreainvestment.com:29443` / 실전: `https://openapi.koreainvestment.com:9443` |
| `ADMIN_ID` / `ADMIN_PASS` | 웹 어드민 로그인 자격증명 |
| `TELEGRAM_BOT_TOKEN` / `TELEGRAM_CHAT_ID` | 알림 설정 |

## KIS API TR ID 매핑

- 모의투자 매수: `VTTC8434U` / 실전: `TTTC0802U`
- 모의투자 매도: `VTTC8435U` / 실전: `TTTC0801U`
- 잔고 조회: `VTTC8434R` (모의) / `TTTC8434R` (실전)
