@echo off
chcp 65001 >nul
REM AutoStock Development Server Starter
REM 백엔드와 프론트엔드 서버를 동시에 시작합니다

echo.
echo ========================================
echo   AutoStock Development Server
echo ========================================
echo.

setlocal enabledelayedexpansion

REM 이 배치파일의 디렉토리를 ROOT_DIR로 설정
set ROOT_DIR=%~dp0

set BACKEND_PORT=8000
set FRONTEND_PORT=3000

echo [1/4] 기존 프로세스 확인...
echo.

REM 포트 확인
netstat -ano | findstr ":%BACKEND_PORT% " >nul
if !errorlevel! equ 0 (
    echo 포트 %BACKEND_PORT% 이미 사용 중
) else (
    echo + 포트 %BACKEND_PORT% 사용 가능
)

netstat -ano | findstr ":%FRONTEND_PORT% " >nul
if !errorlevel! equ 0 (
    echo 포트 %FRONTEND_PORT% 이미 사용 중
) else (
    echo + 포트 %FRONTEND_PORT% 사용 가능
)

echo.
echo [2/4] 백엔드 서버 시작...

set BACKEND_PATH=%ROOT_DIR%backend
if exist "%BACKEND_PATH%" (
    echo %BACKEND_PATH%
    echo + 필요한 패키지 설치 중...
    start "AutoStock Backend" cmd /k "cd /d %BACKEND_PATH% && python -m pip install -r requirements.txt && python -m uvicorn app.main:app --host 0.0.0.0 --port %BACKEND_PORT% --reload"
    echo + 백엔드 서버 시작
    echo   접근: http://localhost:%BACKEND_PORT%
    echo   문서: http://localhost:%BACKEND_PORT%/docs
) else (
    echo - 백엔드 디렉토리를 찾을 수 없습니다
    echo   경로: %BACKEND_PATH%
)

timeout /t 2 /nobreak

echo.
echo [3/4] 프론트엔드 서버 시작...

set FRONTEND_PATH=%ROOT_DIR%frontend
if exist "%FRONTEND_PATH%" (
    echo %FRONTEND_PATH%
    start "AutoStock Frontend" cmd /k "cd /d %FRONTEND_PATH% && npm run dev"
    echo + 프론트엔드 서버 시작
    echo   접근: http://localhost:%FRONTEND_PORT%
) else (
    echo - 프론트엔드 디렉토리를 찾을 수 없습니다
    echo   경로: %FRONTEND_PATH%
)

echo.
echo [4/4] 서버 시작 완료
echo.
echo ========================================
echo   서버가 시작되었습니다!
echo ========================================
echo.
echo 접근 주소:
echo   - 백엔드: http://localhost:%BACKEND_PORT%
echo   - API 문서: http://localhost:%BACKEND_PORT%/docs
echo   - 프론트엔드: http://localhost:%FRONTEND_PORT%
echo.
echo 중지하려면 각 창에서 Ctrl+C를 누르세요
echo.
