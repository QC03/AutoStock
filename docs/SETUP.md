# 로컬 개발 환경 세팅 (1단계)

아래는 AutoStock 1단계 기준 최소 개발환경 준비 절차입니다.

## 1) 필수 설치

- Python 3.11+
- Node.js 20 LTS+
- Docker Desktop (Docker Compose 포함)
- Git

## 2) 저장소 클론 및 기본 구조 확인

```powershell
git clone <repository-url>
cd AutoStock
```

## 3) Python 가상환경 (backend)

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
cd ..
```

## 4) Node 환경 (frontend)

```powershell
cd frontend
node -v
npm -v
cd ..
```

## 5) Docker 확인

```powershell
docker --version
docker compose version
```

## 6) 다음 단계

- 2단계에서 데이터 수집 모듈 구현
- 5단계에서 FastAPI 초기화
- 6단계에서 Next.js 초기화
