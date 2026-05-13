@echo off
echo =========================================================
echo           Starting XueFeng Volunteer Coach
echo              with Admin Panel
echo =========================================================
echo.
echo Server will start at: http://localhost:8000
echo Admin Panel: http://localhost:8000/admin
echo API Docs: http://localhost:8000/docs
echo.
echo Login credentials:
echo   Username: admin
echo   Password: password
echo.
echo Press Ctrl+C to stop the server
echo =========================================================
echo.

cd /d "%~dp0"
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

pause
