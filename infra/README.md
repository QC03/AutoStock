# Infra

7단계 로컬 통합 테스트를 위한 인프라 구성이 포함됩니다.

- `docker-compose.yml`: 전체 스택 로컬 실행 (backend, frontend, db, redis, celery worker)
- `scripts/run_stage7_e2e.py`: 모의투자 E2E + 자동매매 시나리오 검증
- `scripts/run_stage7_perf.py`: 핵심 API 지연시간 측정
- `nginx`: 리버스 프록시 설정 파일 위치

## 7단계 실행 방법

```powershell
cd infra
Copy-Item .env.example .env
docker compose up --build -d
```

## E2E 시나리오 테스트

```powershell
cd infra
python scripts/run_stage7_e2e.py --base-url http://localhost:8000
```

검증 흐름:

1. 회원가입/로그인
2. 종목 검색/시세 조회
3. 자동매매 ON
4. 신호 기반 주문 실행 (HOLD면 BUY 1주 폴백)
5. 주문 내역/성과 확인

## 성능 측정

```powershell
cd infra
python scripts/run_stage7_perf.py --base-url http://localhost:8000 --repeats 20
```

## 종료

```powershell
cd infra
docker compose down
```
