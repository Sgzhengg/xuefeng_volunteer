@echo off
chcp 65001 >nul
echo ====================================
echo 2025广东高考投档线采集系统
echo ====================================
echo.

cd /d "%~dp0"

echo 检查依赖...
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请先安装Python 3.8+
    pause
    exit /b 1
)

echo.
echo 选择操作:
echo 1. API分析工具（推荐首次使用）
echo 2. 完整数据采集
echo 3. 安装依赖
echo 4. 查看使用说明
echo.

set /p choice="请选择 (1-4): "

if "%choice%"=="1" (
    echo.
    echo 启动API分析工具...
    python api_analyzer.py
) else if "%choice%"=="2" (
    echo.
    echo 启动完整数据采集...
    python guangdong_2025_admission_scraper.py
) else if "%choice%"=="3" (
    echo.
    echo 安装依赖包...
    pip install -r requirements_scraper.txt
    echo.
    echo 安装Playwright浏览器...
    playwright install chromium
    echo.
    echo 依赖安装完成！
) else if "%choice%"=="4" (
    echo.
    echo 打开使用说明...
    start "" "README_SCRAPER.md"
) else (
    echo 无效选择
)

echo.
pause
