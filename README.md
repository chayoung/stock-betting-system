# � 주식 종가배팅 시스템 (Stock Betting System) - NAS & Cloud Edition

본 프로젝트는 한국 주식 시장(KOSPI, KOSDAQ)을 대상으로 한 **종가배팅 전략 백테스트 및 실시간 자동 매매 보조 도구**입니다. 시각화된 대시보드를 통해 수익률을 확인하고, NAS(Synology 등) 환경에 Docker로 배포하여 24시간 자동화된 업데이트와 KIS(한국투자증권) API 연동을 지원합니다.

---

## ✨ 핵심 기능

- **📊 프리미엄 백테스트 대시보드**: React 기반의 다크 테마 UI를 통해 수익률 추이, 승률, 상세 거래 내역을 실계좌 조회하듯 시각화합니다.
- **⚡ KIS 서비스 수동 제어**: 웹 화면에서 버튼 클릭 한 번으로 KIS 모의투자 계좌 정보 테스트 및 매수/매도 배치 작업을 즉시 실행할 수 있습니다.
- **🐳 Docker 기반 NAS 최적화**: Docker Compose를 통해 백엔드(FastAPI), 프론트엔드(React + Nginx Proxy), 와치타워(자동 업데이트)를 통합 관리합니다.
- **🔄 Watchtower 자동 배포 연동**: Harbor와 같은 프라이빗 레지스트리와 연동하여, 새 이미지가 푸시되면 NAS에 자동으로 반영되는 CI/CD 환경을 지원합니다.
- **🔔 텔레그램 스마트 알림**: 백테스트 결과 및 KIS 자동 매수/매도 집행 내역을 텔레그램 봇으로 실시간 전송합니다.
- **📅 휴장일 자동 체크**: KIS API 연동 시 주말 및 공휴일을 자동으로 판별하여 불필요한 요청을 방지합니다.
- **📈 매매 상세 데이터 강화**: 매매 내역 조회 시 종목별 수량(`qty`), 수익금(`profit`) 정보를 추가하고, 기간별 누적 수익 요약을 제공합니다.

---

## 📅 최근 업데이트 내역 (2026.02.23)

### 1. 매매 내역 조회 및 UI 기능 강화
- **수량/수익금 컬럼 추가**: DB 스키마 업데이트를 통해 매매 내역 테이블에 수량(`qty`) 및 매도 시 수익금(`profit`) 항목을 신규 적용했습니다.
- **누적 수익 요약**: 조회 기간 내 총 매수/매도 금액 및 합계 수익금을 하단에 표시하여 투자 현황을 한눈에 파악할 수 있도록 개선했습니다.
- **Admin 제어 보안**: 민감한 수동 제어 섹션(매매 테스트 등)에 어드민 로그인 기능을 추가하여 보안을 강화했습니다.

### 2. 인프라 및 배포 최적화
- **빌드 캐시 문제 해결**: `deploy.sh`에 `--no-cache` 옵션을 추가하여 코드 수정 사항이 도커 이미지에 확실히 반영되도록 강제했습니다.
- **Harbor 업로드(Push) 안정화**: Cloudflare 프록시 환경에서의 대용량 레이어 전송 오류를 분석하고, 직접 연결(DNS Only) 설정을 통해 200MB 이상의 이미지 업로드 안정성을 확보했습니다.
- **시각 자동화**: Dockerfile 빌드 단계에서 시간대를 KST(Asia/Seoul)로 고정하여 텔레그램 알림 및 데이터 적재 시 정확한 한국 시간을 제공합니다.

### 3. 모바일 UI 최적화
- **Responsive Design**: 스마트폰에서도 대시보드를 편리하게 확인할 수 있도록 헤더 레이아웃, 버튼 크기, 테이블 스크롤 및 폰트 크기를 기기 너비에 맞게 조정했습니다.

---

## 🛠 기술 스택

| 구분 | 기술 스택 |
| :--- | :--- |
| **Backend** | Python 3.12, FastAPI, Pandas, FinanceDataReader, Uvicorn |
| **Frontend** | React, Vite, Recharts, Axios, Lucide React, Nginx |
| **DevOps** | Docker, Docker Compose, Portainer, Watchtower, Harbor |
| **API** | 한국투자증권(KIS) OpenAPI, Telegram Bot API |

---

## 📋 핵심 파일 구조

```text
.
├── backend/            # FastAPI 서버 및 KIS API 연동 로직
│   ├── main.py         # API 엔드포인트 및 서버 설정
│   ├── kis_api.py      # KIS OpenAPI 핵심 연동 모듈
│   ├── batch_run.py    # 매수/매도 배치 프로세스
│   └── data_loader.py  # 시장 데이터 로딩 (FinanceDataReader)
├── frontend/           # React 대시보드 애플리케이션
│   ├── src/App.jsx     # 메인 UI 및 API 통신 로직
│   └── nginx.conf      # 프론트엔드 배포 및 API 프록시 설정
├── docker-compose.yml  # 전체 서비스 오케스트레이션
└── deploy.sh           # 로컬 빌드 및 Harbor 푸시 자동화 스크립트
```

---

## 🚀 시작하기

### 1. 환경 설정 (.env)
`backend/.env` 파일을 작성하여 API 키와 계좌 정보를 설정합니다.
```env
# 텔레그램 알림 설정
TELEGRAM_BOT_TOKEN=your_token
TELEGRAM_CHAT_ID=your_id

# KIS API 설정 (모의투자/실전 선택)
KIS_APP_KEY=your_app_key
KIS_APP_SECRET=your_secret
KIS_CANO=your_account_number
KIS_URL=https://openapivts.koreainvestment.com:29443 # 모의투자 URL
```

### 2. 로컬 실행
```bash
# Backend 실행
cd backend
pip install -r requirements.txt
python main.py

# Frontend 실행
cd frontend
npm install
npm run dev
```

### 3. NAS 배포 (Docker Compose)
제공된 `deploy.sh`를 사용하여 Harbor에 빌드된 이미지를 푸시한 후, Portainer 등에서 `docker-compose.yml`을 사용하여 서비스를 가동합니다.

---

## 📈 백테스트 전략 (Closing Price Betting)
프로젝트의 기본 전략은 다음과 같은 기술적 조건을 바탕으로 합니다:
- **선정**: 당일 양봉 마감, 거래량 전일 대비 200% 이상 증가, 거래대금 상위 종목 우선.
- **매매**: 당일 종가(15:20) 매수 → 익일 시가(09:00) 매도.

---

## ⚠️ 면책 조항 (Disclaimer)
본 시스템은 개인의 투자 결정을 돕는 보조 도구로 설계되었습니다. 시스템의 결과가 실제 수익을 보장하지 않으며, 모든 투자에 대한 최종 책임은 사용자 본인에게 있습니다.
