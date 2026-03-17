# AutoStock
바이브 코딩 연습 및 주식 자동매매 웹 사이트 구현을 목표로 한 레포지토리

> AI를 활용한 주식 자동 매매 플랫폼. 로컬 환경에서 시작해 서버 배포까지 단계별로 확장합니다.

---

## 프로젝트 단계별 계획

### 1단계 – 환경 설정 및 기술 스택 선정

- [ ] 프로젝트 디렉터리 구조 설계 (frontend / backend / ai / infra)
- [ ] 기술 스택 확정
  - **Frontend**: React (Next.js) + TypeScript
  - **Backend**: FastAPI (Python)
  - **AI/ML**: Python (scikit-learn, LightGBM, PyTorch 등)
  - **Database**: PostgreSQL (운영) + SQLite (로컬 테스트)
  - **Task Queue**: Celery + Redis (자동매매 스케줄링)
  - **Container**: Docker / Docker Compose
- [ ] 로컬 개발 환경 세팅 (Python venv, Node.js, Docker Compose)
- [ ] GitHub 저장소 브랜치 전략 수립 (`main` / `develop` / `feature/*`)

---

### 2단계 – 데이터 수집 및 전처리

- [ ] 주식 데이터 소스 선정 및 연동
  - 한국 주식: 한국투자증권 API(KIS) 또는 PyKrx
  - 해외 주식: yfinance / Alpha Vantage
- [ ] OHLCV (시가·고가·저가·종가·거래량) 데이터 수집 모듈 구현
- [ ] 기술적 지표 계산 (이동평균, RSI, MACD, 볼린저 밴드 등)
- [ ] 뉴스·공시 데이터 크롤링 (선택)
- [ ] 데이터 정제 및 정규화 파이프라인 구축
- [ ] 로컬 DB에 수집 데이터 저장

---

### 3단계 – AI 예측 모델 개발

- [ ] 학습 데이터 분할 (train / validation / test)
- [ ] 베이스라인 모델 구현 (이동평균 전략 등 룰 기반)
- [ ] 머신러닝 모델 학습
  - 시계열 예측: LSTM / Transformer
  - 분류/회귀: LightGBM, XGBoost
- [ ] 모델 평가 지표 정의 (Sharpe ratio, MDD, 승률 등)
- [ ] 모델 버전 관리 및 저장 (MLflow 또는 파일 기반)
- [ ] 매수·매도 신호 생성 로직 구현

---

### 4단계 – 자동 매매 엔진 구현

- [ ] 증권사 API 연동 (모의 투자 계좌로 먼저 테스트)
  - 한국: 한국투자증권 KIS API
  - 해외: Alpaca / Interactive Brokers (선택)
- [ ] 주문 실행 모듈 (시장가·지정가 주문)
- [ ] 포트폴리오 관리 (보유 종목, 평가손익 조회)
- [ ] 리스크 관리 로직 (손절선, 최대 손실한도 설정)
- [ ] Celery를 이용한 장 시작/종료 시 자동 실행 스케줄링

---

### 5단계 – 백엔드 API 서버 구현

- [ ] FastAPI 프로젝트 초기화
- [ ] REST API 엔드포인트 설계
  - 인증: 회원가입 / 로그인 (JWT)
  - 데이터: 종목 검색, 시세 조회, 지표 조회
  - 매매: 수동 주문 실행, 자동매매 ON/OFF
  - 대시보드: 포트폴리오 현황, 매매 내역, 수익률
- [ ] 데이터베이스 모델 정의 (SQLAlchemy + Alembic 마이그레이션)
- [ ] WebSocket 실시간 시세 스트리밍
- [ ] 단위 테스트 작성 (pytest)

---

### 6단계 – 프론트엔드 구현

- [ ] Next.js 프로젝트 초기화
- [ ] 페이지 구성
  - 로그인 / 회원가입 페이지
  - 대시보드 (포트폴리오 현황, 수익률 그래프)
  - 종목 상세 페이지 (차트, AI 예측 신호)
  - 매매 설정 페이지 (자동매매 전략 선택·파라미터 조정)
  - 매매 내역 페이지
- [ ] 실시간 시세 차트 컴포넌트 (TradingView Lightweight Charts 또는 Recharts)
- [ ] API 연동 (Axios / React Query)
- [ ] 반응형 UI 구현 (Tailwind CSS)

---

### 7단계 – 로컬 통합 테스트

- [ ] Docker Compose로 전체 스택 로컬 실행 환경 구성
  - 서비스: backend, frontend, db(PostgreSQL), redis, celery worker
- [ ] 모의투자 계좌로 전 기능 E2E 테스트
- [ ] 자동매매 시나리오 테스트 (신호 발생 → 주문 실행 → 내역 반영)
- [ ] 성능 측정 및 버그 수정

---

### 8단계 – 서버 배포 및 운영 환경 구축

- [ ] 클라우드 서버 선택 (AWS EC2 / GCP / 자체 서버)
- [ ] Docker 이미지 빌드 및 컨테이너 레지스트리 푸시 (Docker Hub / ECR)
- [ ] 운영 환경 환경변수 관리 (`.env.production`, AWS Secrets Manager 등)
- [ ] Nginx 리버스 프록시 설정 (HTTPS, SSL 인증서)
- [ ] CI/CD 파이프라인 구성 (GitHub Actions → 자동 빌드·테스트·배포)
- [ ] 운영 DB 마이그레이션 (PostgreSQL 운영 서버)
- [ ] 모니터링 및 알림 설정 (Prometheus + Grafana 또는 CloudWatch)
- [ ] 로그 수집 (ELK Stack 또는 클라우드 로그 서비스)

---

### 9단계 – 고도화 및 유지보수 (선택)

- [ ] 강화학습(RL) 기반 트레이딩 에이전트 도입 (PPO, DQN 등)
- [ ] 멀티 전략 / 멀티 종목 동시 운영
- [ ] 백테스팅 엔진 구현 (과거 데이터로 전략 시뮬레이션)
- [ ] 사용자 알림 기능 (이메일 / Slack / 텔레그램)
- [ ] 전략 마켓플레이스 (사용자 커스텀 전략 등록·공유)

---

## 디렉터리 구조 (예시)

```
AutoStock/
├── backend/          # FastAPI 서버
│   ├── app/
│   │   ├── api/      # 라우터
│   │   ├── models/   # DB 모델
│   │   ├── schemas/  # Pydantic 스키마
│   │   ├── services/ # 비즈니스 로직
│   │   └── core/     # 설정, 인증, 의존성
│   └── tests/
├── frontend/         # Next.js 앱
│   ├── pages/
│   ├── components/
│   └── styles/
├── ai/               # AI 모델 학습 및 추론
│   ├── data/         # 데이터 수집·전처리
│   ├── models/       # 모델 정의·학습
│   └── signals/      # 매매 신호 생성
├── infra/            # 인프라 설정
│   ├── docker-compose.yml
│   ├── docker-compose.prod.yml
│   └── nginx/
└── README.md
```

---

## 기술 스택 요약

| 영역 | 기술 |
|------|------|
| Frontend | Next.js, TypeScript, Tailwind CSS |
| Backend | FastAPI, SQLAlchemy, Alembic |
| AI/ML | PyTorch, LightGBM, scikit-learn |
| Database | PostgreSQL, Redis |
| Task Queue | Celery |
| Container | Docker, Docker Compose |
| CI/CD | GitHub Actions |
| Monitoring | Prometheus, Grafana |
