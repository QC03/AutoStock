# Backend (FastAPI)

현재는 5단계(백엔드 API 서버 MVP)까지의 백엔드 기초 구성이 포함됩니다.

- `app/api`: 라우터
- `app/models`: DB 모델
- `app/schemas`: Pydantic 스키마
- `app/services`: 비즈니스 로직
- `app/core`: 설정/인증/의존성
- `scripts`: 실행 스크립트
- `tests`: 테스트

## 2단계 데이터 파이프라인

`app/services/data_pipeline.py`에 다음 기능이 포함되어 있습니다.

- OHLCV 수집 provider (`dummy`, `yfinance`)
- 데이터 정제 (이상치/중복 제거)
- 기술지표 계산 (SMA20, RSI14, MACD, Bollinger Band)
- Min-Max 정규화
- SQLite 저장 (`market_features` 테이블)

## 실행 방법

### 의존성 설치

```powershell
cd backend
python -m pip install -r requirements.txt
```

### 파이프라인 실행 (더미 데이터)

```powershell
cd backend
python -m scripts.run_data_pipeline --provider dummy --symbol AAPL --market US --start 2024-01-01 --end 2024-03-31
```

### 파이프라인 실행 (yfinance)

```powershell
cd backend
python -m scripts.run_data_pipeline --provider yfinance --symbol AAPL --market US --start 2024-01-01 --end 2024-03-31
```

기본 DB 경로는 `backend/data/market_data.db`입니다.

## 4단계 자동매매 엔진 (MVP)

`app/services/trading_engine.py`에 다음 기능이 포함되어 있습니다.

- 모의 증권사 API 연동 (`MockBrokerClient`)
- 주문 실행 (시장가/지정가)
- 포트폴리오 관리 (보유 종목, 평가손익, 총자산)
- 리스크 관리 (최대 주문금액, 일일 최대 손실, 손절)
- 손절 조건 강제 청산 (`enforce_stop_losses`)

### 데모 실행

```powershell
cd backend
python -m scripts.run_trading_engine_demo
```

## Celery 스케줄링 골격

`app/services/trading_scheduler.py`에 장 시작/종료 스케줄 태스크 골격이 포함되어 있습니다.

- 장 시작 태스크: `run_market_open_job`
- 장 종료 태스크: `run_market_close_job`

### Celery 워커 실행 예시

```powershell
cd backend
celery -A app.services.trading_scheduler.celery_app worker --loglevel=INFO
```

### Celery Beat 실행 예시

```powershell
cd backend
celery -A app.services.trading_scheduler.celery_app beat --loglevel=INFO
```

## 5단계 백엔드 API 서버 (MVP)

### FastAPI 실행

```powershell
cd backend
uvicorn app.main:app --reload
```

### 주요 API

- 인증: `POST /auth/signup`, `POST /auth/login` (JWT)
- 데이터: `GET /data/search`, `GET /data/quote/{symbol}`, `GET /data/indicators/{symbol}`
- 매매: `POST /trading/orders`, `POST /trading/auto-trade`
- 대시보드: `GET /dashboard/portfolio`, `GET /dashboard/trades`, `GET /dashboard/performance`

### WebSocket

- 실시간 시세 스트리밍: `ws://localhost:8000/ws/quotes/{symbol}`

### Alembic 마이그레이션

```powershell
cd backend
alembic upgrade head
```

초기 마이그레이션은 `alembic/versions/20260325_0001_init.py`입니다.

### 테스트

```powershell
cd backend
python -m pytest tests/test_api_stage5.py -q
```
