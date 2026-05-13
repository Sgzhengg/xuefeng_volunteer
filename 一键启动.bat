@echo off
chcp 65001 >nul
echo ========================================
echo    学锋志愿教练 - 一键启动
echo ========================================
echo.

echo [1/3] 正在启动后端服务...
cd /d "%~dp0backend"
python simple_server.py
if errorlevel 1 (
    echo.
    echo [ERROR] 后端服务启动失败！
    pause
    exit /b 1
)

echo.
echo [2/3] 正在启动前端服务...
cd /d "%~dp0"
python -m http.server 8080
if errorlevel 1 (
    echo.
    echo [ERROR] 前端服务启动失败！
    pause
    exit /b 1
)

echo.
echo [3/3] 服务启动完成！
echo.
echo ================== 访问地址 ==================
echo 前端界面: http://localhost:8080/frontend.html
echo 后端API:  http://localhost:5000
echo API健康检查: http://localhost:5000/api/v1/health
echo.
echo ================== 功能说明 ==================
echo 1. 打开浏览器访问: http://localhost:8080/frontend.html
echo 2. 在"和老师聊"标签页与学锋老师对话
echo 3. 在"志愿模拟器"标签页生成志愿方案
echo.
echo 按 Ctrl+C 停止所有服务
echo ========================================

pause