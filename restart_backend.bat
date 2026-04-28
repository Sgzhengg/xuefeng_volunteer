@echo off
REM Restart Backend Service

echo Stopping backend service...
taskkill /F /IM uvicorn.exe 2>nul
taskkill /F /IM python.exe 2>nul

timeout /t 2 /nobreak >nul

echo Starting backend service...
cd backend
call venv\Scripts\activate.bat
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

pause
