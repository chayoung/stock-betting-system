---
name: backtest
description: This skill should be used when the user asks to "백테스트", "backtest", "수익률 확인", "기간 분석", "전략 테스트", "특정 기간 결과", or wants to run or analyze the closing price betting strategy backtest.
version: 1.0.0
---

# 백테스트 실행 스킬

`backtest.py`를 실행해 특정 기간의 종가배팅 전략 수익률을 분석합니다.

## 실행 방법

```bash
cd backend

# 기본 실행 (최근 5영업일 자동 선택)
python backtest.py

# 특정 기간 지정
python -c "
from backtest import run_backtest
result = run_backtest('2026-01-01', '2026-01-31')
print(f'수익률: {result[\"summary\"][\"total_profit_rate\"]}%')
print(f'승률: {result[\"summary\"][\"win_rate\"]}%')
print(f'총 거래: {result[\"summary\"][\"total_trades\"]}건')
"
```

## 전략 조건 (strategy.py)

- **SURGE 모드 (기본)**: 양봉(종가 > 시가) + 거래량 전일 대비 2배 이상
- **PULLBACK 모드**: 최근 10일 내 급등(+15%) 이후 눌림목 구간
- **HYBRID 모드**: PULLBACK 우선, 없으면 최근 강세 종목의 SURGE
- 선정 기준: 거래대금 상위 5개 종목

## 분석 범위

- 상위 300개 종목 스캔 (`backtest.py:46`)
- 초기 예수금 기본값: 200만원
- 수익 계산: 당일 종가 매수 → 익일 시가 매도

## 결과 구조

```python
{
  'summary': { 'total_profit_rate', 'win_rate', 'total_trades', ... },
  'daily_returns': [...],   # 날짜별 수익
  'trades': [...],          # 개별 거래 내역
  'signals': [...]          # 당일 매매 후보 (마지막 날)
}
```
