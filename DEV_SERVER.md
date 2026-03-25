# 테스트 서버 시작 가이드

AutoStock 프로젝트의 테스트 서버를 쉽게 시작할 수 있습니다.

## Windows 사용자

### 방법 1: Batch 파일 (권장)
```bash
.\dev-start.bat
```

더블클릭하거나 터미널에서 실행하면:
- 백엔드 서버가 포트 8000에서 실행
- 프론트엔드 서버가 포트 3000에서 실행
- 각각 새로운 cmd 창에서 실행됨

### 방법 2: PowerShell
```powershell
powershell -ExecutionPolicy Bypass -File .\dev-start.ps1
```

## macOS / Linux 사용자

### 사전 준비
Bash 스크립트에 실행 권한 부여:
```bash
chmod +x dev-start.sh
```

### 실행
```bash
./dev-start.sh
```

## 접근 주소

서버가 시작되면 다음 주소에서 접근할 수 있습니다:

| 서비스 | URL | 설명 |
|--------|-----|------|
| 프론트엔드 | http://localhost:3000 | 웹 애플리케이션 |
| 백엔드 API | http://localhost:8000 | API 서버 |
| API 문서 | http://localhost:8000/docs | Swagger UI |
| API 스키마 | http://localhost:8000/openapi.json | OpenAPI 스키마 |

## 로그인 정보

프론트엔드에 접근한 후:
1. **회원가입** 페이지에서 계정을 생성하거나
2. **로그인** 페이지에서 기존 계정으로 로그인

## 서버 중지

각 터미널/창에서 `Ctrl+C`를 눌러 서버를 중지할 수 있습니다.

## 문제 해결

### 포트가 이미 사용 중인 경우
```powershell
# Windows - 포트를 사용하는 프로세스 찾기
netstat -ano | findstr :8000
netstat -ano | findstr :3000

# 프로세스 종료
taskkill /PID <PID> /F
```

```bash
# macOS/Linux - 포트를 사용하는 프로세스 찾기
lsof -i :8000
lsof -i :3000

# 프로세스 종료
kill -9 <PID>
```

### 의존성 설치

`dev-start.bat`, `dev-start.ps1`, `dev-start.sh`는 백엔드 실행 전에 자동으로 아래를 수행합니다.

```bash
python -m pip install -r requirements.txt
```

수동 설치가 필요하면 아래 명령을 사용하세요.

백엔드:
```bash
cd backend
python -m pip install -r requirements.txt
```

프론트엔드:
```bash
cd frontend
npm install
```

## 개발 팁

- **백엔드 리로드**: 코드 변경 시 자동으로 재로드됨 (uvicorn --reload)
- **프론트엔드 리로드**: 코드 변경 시 자동으로 재로드됨 (next dev)
- **API 문서**: http://localhost:8000/docs 에서 API 테스트 가능
