# AutoStock Development Server Starter
# 백엔드와 프론트엔드 서버를 동시에 시작합니다

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  AutoStock Development Server" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 현재 디렉토리 확인
$rootDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Write-Host "Root Directory: $rootDir" -ForegroundColor Green

# 프로세스 확인
$backendPort = 8000
$frontendPort = 3000

Write-Host ""
Write-Host "[1/4] 기존 프로세스 확인..." -ForegroundColor Yellow

$backendProcess = Get-NetTCPConnection -LocalPort $backendPort -ErrorAction SilentlyContinue | Select-Object -First 1
$frontendProcess = Get-NetTCPConnection -LocalPort $frontendPort -ErrorAction SilentlyContinue | Select-Object -First 1

if ($backendProcess) {
    Write-Host "[!] 포트 $backendPort 이미 사용 중 (PID: $($backendProcess.OwningProcess))" -ForegroundColor Red
} else {
    Write-Host "[+] 포트 $backendPort 사용 가능" -ForegroundColor Green
}

if ($frontendProcess) {
    Write-Host "[!] 포트 $frontendPort 이미 사용 중 (PID: $($frontendProcess.OwningProcess))" -ForegroundColor Red
} else {
    Write-Host "[+] 포트 $frontendPort 사용 가능" -ForegroundColor Green
}

Write-Host ""
Write-Host "[2/4] 백엔드 서버 시작..." -ForegroundColor Yellow

# 백엔드 시작
$backendPath = Join-Path $rootDir "backend"
if (Test-Path $backendPath) {
    Write-Host "    $backendPath" -ForegroundColor Gray
    Write-Host "[+] 필요한 패키지 설치 중..." -ForegroundColor Yellow
    $backendProcess = Start-Process -FilePath "cmd.exe" -ArgumentList "/c cd /d `"$backendPath`" && python -m pip install -r requirements.txt && python -m uvicorn app.main:app --host 0.0.0.0 --port $backendPort --reload" -PassThru -NoNewWindow
    Write-Host "[+] 백엔드 서버 시작 (PID: $($backendProcess.Id))" -ForegroundColor Green
    Write-Host "    접근: http://localhost:$backendPort" -ForegroundColor Cyan
    Write-Host "    문서: http://localhost:$backendPort/docs" -ForegroundColor Cyan
} else {
    Write-Host "[-] 백엔드 디렉토리를 찾을 수 없습니다" -ForegroundColor Red
}

Write-Host ""
Write-Host "[3/4] 프론트엔드 서버 시작..." -ForegroundColor Yellow

# 프론트엔드 시작
$frontendPath = Join-Path $rootDir "frontend"
if (Test-Path $frontendPath) {
    Write-Host "    $frontendPath" -ForegroundColor Gray
    $frontendProcess = Start-Process -FilePath "cmd.exe" -ArgumentList "/c cd /d `"$frontendPath`" && npm run dev" -PassThru -NoNewWindow
    Write-Host "[+] 프론트엔드 서버 시작 (PID: $($frontendProcess.Id))" -ForegroundColor Green
    Write-Host "    접근: http://localhost:$frontendPort" -ForegroundColor Cyan
} else {
    Write-Host "[-] 프론트엔드 디렉토리를 찾을 수 없습니다" -ForegroundColor Red
}

Write-Host ""
Write-Host "[4/4] 서버 시작 완료" -ForegroundColor Yellow
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  서버가 시작되었습니다!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "접근 주소:" -ForegroundColor Cyan
Write-Host "  - 백엔드: http://localhost:$backendPort" -ForegroundColor White
Write-Host "  - API 문서: http://localhost:$backendPort/docs" -ForegroundColor White
Write-Host "  - 프론트엔드: http://localhost:$frontendPort" -ForegroundColor White
Write-Host ""
Write-Host "중지하려면 각 창에서 Ctrl+C를 누르세요" -ForegroundColor Gray
Write-Host ""
