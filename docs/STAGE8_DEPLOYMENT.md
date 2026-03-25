# Stage 8 - 배포/운영 가이드

이 문서는 `8단계(배포/운영)`를 빠르게 시작하기 위한 최소 운영 구성입니다.

## 포함된 구성

- `infra/docker-compose.prod.yml`
  - `db`, `redis`, `backend`, `celery-worker`, `frontend`, `nginx`, `prometheus`, `grafana`
- `infra/nginx/autostock.prod.conf`
  - HTTPS 종료, `/api` 및 `/ws` 프록시
- `.github/workflows/stage8-cicd.yml`
  - 백엔드 테스트 + 프론트 빌드 + GHCR 이미지 푸시 + SSH 자동배포
- `frontend/Dockerfile.prod`
  - Next.js production build/start 이미지
- `infra/.env.production.example`
  - 운영 환경 변수 샘플
- `infra/scripts/deploy_stage8.sh`
  - 운영 스택 재기동 + 마이그레이션 실행
- `infra/scripts/migrate_prod.sh`
  - 운영 DB alembic 마이그레이션 실행
- `infra/grafana/...`
  - 데이터소스/대시보드 자동 프로비저닝

## 1) 운영 환경 변수 준비

```powershell
cd infra
Copy-Item .env.production.example .env.production
```

- `POSTGRES_PASSWORD`, `AUTOSTOCK_JWT_SECRET`, `GRAFANA_ADMIN_PASSWORD`는 반드시 강한 값으로 변경하세요.
- `NEXT_PUBLIC_API_BASE_URL`은 실제 도메인 기준으로 설정하세요.

## 2) TLS 인증서 배치

`infra/nginx/certs` 경로에 아래 파일을 배치합니다.

- `fullchain.pem`
- `privkey.pem`

## 3) 운영 스택 실행

```powershell
cd infra
docker compose -f docker-compose.prod.yml --env-file .env.production up -d --build
```

## 4) 상태 확인

```powershell
cd infra
docker compose -f docker-compose.prod.yml ps
```

- 앱 헬스: `https://<your-domain>/health`
- Prometheus: `http://<server-ip>:9090`
- Grafana: `http://<server-ip>:3001`

## 5) CI/CD 동작

`main` 브랜치 푸시 시:

1. 백엔드 테스트 실행
2. 프론트 빌드 실행
3. GHCR에 백엔드/프론트 이미지 푸시
4. SSH로 운영 서버 접속 후 `infra/scripts/deploy_stage8.sh` 실행

### GitHub Secrets (필수)

- `STAGE8_SSH_HOST`
- `STAGE8_SSH_PORT` (예: `22`)
- `STAGE8_SSH_USER`
- `STAGE8_SSH_PRIVATE_KEY`
- `STAGE8_DEPLOY_PATH` (서버 내 레포 경로)

### 수동 마이그레이션 (필요 시)

```bash
cd infra
./scripts/migrate_prod.sh
```

## 체크리스트

- [ ] 운영 도메인 연결
- [ ] TLS 인증서 배치
- [ ] `.env.production` 보안값 적용
- [ ] GitHub Actions 성공 확인
- [ ] Grafana 대시보드/알림 설정
- [ ] 백업 정책(POSTGRES) 수립
