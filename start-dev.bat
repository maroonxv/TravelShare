@echo off
setlocal

if /i "%~1"=="--backend" goto backend
if /i "%~1"=="--frontend" goto frontend

if not exist "%~dp0backend\.venv\Scripts\activate.bat" (
    echo [ERROR] Backend virtual environment not found: "%~dp0backend\.venv"
    pause
    exit /b 1
)

if not exist "%~dp0backend\src\app.py" (
    echo [ERROR] Backend entry not found: "%~dp0backend\src\app.py"
    pause
    exit /b 1
)

if not exist "%~dp0frontend\package.json" (
    echo [ERROR] Frontend package.json not found: "%~dp0frontend\package.json"
    pause
    exit /b 1
)

start "TravelShare Backend" cmd /k ""%~f0" --backend"
start "TravelShare Frontend" cmd /k ""%~f0" --frontend"

echo Backend and frontend are starting in separate windows...
exit /b 0

:backend
cd /d "%~dp0backend" || goto start_error
call ".venv\Scripts\activate.bat" || goto start_error
python "src\app.py"
exit /b %errorlevel%

:frontend
cd /d "%~dp0frontend" || goto start_error
npm run dev
exit /b %errorlevel%

:start_error
echo [ERROR] Failed to start %~1
pause
exit /b 1
