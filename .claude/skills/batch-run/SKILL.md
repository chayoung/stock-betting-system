---
name: batch-run
description: This skill should be used when the user asks to "배치 실행", "매수 실행", "매도 실행", "batch run", "수동 매수", "수동 매도", "오늘 종가배팅 실행", "buy 모드", "sell 모드", or wants to manually trigger the daily trading batch job.
version: 1.0.0
---

# 배치 수동 실행 스킬

`batch_run.py`를 직접 실행해 KIS API를 통한 매수/매도를 수동으로 트리거합니다.

## 실행 방법

```bash
cd backend

# 매수 모드 (장 마감 후, 오늘 종가배팅 종목 매수)
python batch_run.py buy

# 매도 모드 (장 시작 후, 전일 매수 종목 전량 매도)
python batch_run.py sell

# 강제 실행 (주말/휴장일 체크 무시)
python batch_run.py buy --force
python batch_run.py sell --force
```

## 동작 흐름

1. KIS API 토큰 발급 (캐시: `data/token_cache.json`, 12시간 유효)
2. 삼성전자(005930) 데이터로 장 개장 여부 확인
3. **buy**: `backtest.run_backtest(today, today)` → `signals` 종목 매수 → DB 기록 → 텔레그램 알림
4. **sell**: KIS 잔고 조회 → 보유 종목 전량 매도 → DB 기록 → 텔레그램 알림

## 주의사항

- 실행 환경의 `backend/.env`에 KIS API 키가 설정돼 있어야 함
- 모의투자(`openapivts`) / 실전투자(`openapi`) URL로 구분
- `--force` 없이 실행 시 주말/공휴일은 자동 스킵
- DB 경로: `backend/data/stocks.db`
