Write-Host "Starting RetinalAI locally (no Docker)..." -ForegroundColor Cyan

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

$python = Join-Path $root ".venv/Scripts/python.exe"
if (-not (Test-Path $python)) {
  Write-Host "Virtual environment not found at .venv. Please create it first." -ForegroundColor Red
  exit 1
}

Write-Host "Installing backend dependencies..." -ForegroundColor Yellow
& $python -m pip install -r backend/requirements.txt | Out-Host

Write-Host "Installing frontend dependencies..." -ForegroundColor Yellow
Set-Location (Join-Path $root "frontend")
npm install | Out-Host
Set-Location $root

Write-Host "Starting backend on http://127.0.0.1:8000" -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$root/backend'; & '$python' -m uvicorn app.main:app --host 0.0.0.0 --port 8000"

Write-Host "Starting frontend (Vite)" -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$root/frontend'; npm run dev"

Write-Host "Done. Open frontend URL shown in terminal (usually http://localhost:5173)." -ForegroundColor Cyan
