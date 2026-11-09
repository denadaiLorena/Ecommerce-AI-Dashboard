@echo off
chcp 65001 > nul
title AI Metric Pulse - Inicializador

echo =======================================================
echo          AI METRIC PULSE - INICIALIZADOR
echo =======================================================
echo.

:: 1. Definir caminhos
set "ROOT_DIR=%~dp0"
set "PYTHON_EXE=%ROOT_DIR%.venv\Scripts\python.exe"
set "NODE_EXE=node"

:: Verifica se node esta no PATH, senao busca no Cursor/Appdata
where node >nul 2>nul
if %ERRORLEVEL% neq 0 (
    if exist "%LOCALAPPDATA%\Programs\cursor\resources\app\resources\helpers\node.exe" (
        set "NODE_EXE=%LOCALAPPDATA%\Programs\cursor\resources\app\resources\helpers\node.exe"
    )
)

:: 2. Iniciar Backend Flask
echo [1/2] Iniciando Backend Flask na porta 5000...
start "AI Metric Pulse - Backend Flask" cmd /k "cd /d "%ROOT_DIR%backend" && "%PYTHON_EXE%" app.py"

:: Aguarda 3 segundos para o Flask subir
timeout /t 3 /nobreak > nul

:: 3. Iniciar Frontend Quasar
echo [2/2] Iniciando Frontend Quasar / Vite...
start "AI Metric Pulse - Frontend Quasar" cmd /k "cd /d "%ROOT_DIR%frontend" && "%NODE_EXE%" ./node_modules/@quasar/app-vite/bin/quasar dev"

echo.
echo =======================================================
echo   Servidores em execucao!
echo   - Backend:  http://localhost:5000/api/kpis
echo   - Frontend: http://localhost:9000
echo.
echo   Pressione qualquer tecla para encerrar este assistente.
echo =======================================================
pause > nul
