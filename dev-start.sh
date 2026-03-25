#!/bin/bash
# AutoStock Development Server Starter
# 백엔드와 프론트엔드 서버를 동시에 시작합니다

echo ""
echo "========================================"
echo "  AutoStock Development Server"
echo "========================================"
echo ""

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_PORT=8000
FRONTEND_PORT=3000

if command -v python3 &> /dev/null; then
    PYTHON_CMD=python3
elif command -v python &> /dev/null; then
    PYTHON_CMD=python
else
    echo "[-] Python 실행 파일을 찾을 수 없습니다"
    exit 1
fi

echo "[1/4] 기존 프로세스 확인..."
echo ""

# 포트 확인 (macOS/Linux)
if command -v lsof &> /dev/null; then
    if lsof -Pi :$BACKEND_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo "[!] 포트 $BACKEND_PORT 이미 사용 중"
    else
        echo "[+] 포트 $BACKEND_PORT 사용 가능"
    fi
    
    if lsof -Pi :$FRONTEND_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo "[!] 포트 $FRONTEND_PORT 이미 사용 중"
    else
        echo "[+] 포트 $FRONTEND_PORT 사용 가능"
    fi
else
    echo "[!] 포트 확인 도구를 찾을 수 없습니다"
fi

echo ""
echo "[2/4] 백엔드 서버 시작..."

BACKEND_PATH="$ROOT_DIR/backend"
if [ -d "$BACKEND_PATH" ]; then
    echo "    $BACKEND_PATH"
    cd "$BACKEND_PATH"
    echo "[+] 필요한 패키지 설치 중..."
    "$PYTHON_CMD" -m pip install -r requirements.txt
    "$PYTHON_CMD" -m uvicorn app.main:app --host 0.0.0.0 --port $BACKEND_PORT --reload &
    BACKEND_PID=$!
    echo "[+] 백엔드 서버 시작 (PID: $BACKEND_PID)"
    echo "    접근: http://localhost:$BACKEND_PORT"
    echo "    문서: http://localhost:$BACKEND_PORT/docs"
else
    echo "[-] 백엔드 디렉토리를 찾을 수 없습니다"
fi

echo ""
echo "[3/4] 프론트엔드 서버 시작..."

FRONTEND_PATH="$ROOT_DIR/frontend"
if [ -d "$FRONTEND_PATH" ]; then
    echo "    $FRONTEND_PATH"
    cd "$FRONTEND_PATH"
    npm run dev &
    FRONTEND_PID=$!
    echo "[+] 프론트엔드 서버 시작 (PID: $FRONTEND_PID)"
    echo "    접근: http://localhost:$FRONTEND_PORT"
else
    echo "[-] 프론트엔드 디렉토리를 찾을 수 없습니다"
fi

echo ""
echo "[4/4] 서버 시작 완료"
echo ""
echo "========================================"
echo "  서버가 시작되었습니다!"
echo "========================================"
echo ""
echo "접근 주소:"
echo "  - 백엔드: http://localhost:$BACKEND_PORT"
echo "  - API 문서: http://localhost:$BACKEND_PORT/docs"
echo "  - 프론트엔드: http://localhost:$FRONTEND_PORT"
echo ""
echo "중지하려면 아래 명령어를 실행하세요:"
echo "  kill $BACKEND_PID $FRONTEND_PID"
echo ""

# 프로세스가 계속 실행되도록
wait
