# AI Metric Pulse - Script de Inicialização PowerShell
$ErrorActionPreference = "Stop"

Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host "         AI METRIC PULSE - INICIALIZADOR               " -ForegroundColor Cyan
Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host ""

$rootDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$pythonExe = Join-Path $rootDir ".venv\Scripts\python.exe"

# Localizar Node.js
$nodeCmd = "node"
if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    $cursorNode = "$env:LOCALAPPDATA\Programs\cursor\resources\app\resources\helpers\node.exe"
    if (Test-Path $cursorNode) {
        $nodeCmd = $cursorNode
    }
}

Write-Host "[1/2] Iniciando Backend Flask (porta 5000)..." -ForegroundColor Yellow
Start-Process -FilePath "cmd.exe" -ArgumentList "/k", "cd /d `"$rootDir\backend`" && `"$pythonExe`" app.py" -WindowStyle Normal

Start-Sleep -Seconds 3

Write-Host "[2/2] Iniciando Frontend Quasar / Vite..." -ForegroundColor Yellow
Start-Process -FilePath "cmd.exe" -ArgumentList "/k", "cd /d `"$rootDir\frontend`" && `"$nodeCmd`" ./node_modules/@quasar/app-vite/bin/quasar dev" -WindowStyle Normal

Write-Host ""
Write-Host "=======================================================" -ForegroundColor Green
Write-Host "  Servidores em execução com sucesso!" -ForegroundColor Green
Write-Host "  • Backend API: http://localhost:5000/api/kpis" -ForegroundColor White
Write-Host "  • Frontend:    http://localhost:9000" -ForegroundColor White
Write-Host "=======================================================" -ForegroundColor Green
