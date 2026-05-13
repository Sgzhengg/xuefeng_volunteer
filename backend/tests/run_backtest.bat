@echo off
chcp 65001 >nul
echo ======================================
echo 推荐系统回溯测试工具
echo ======================================
echo.

REM 检查Python环境
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未找到Python环境
    echo 请先安装Python 3.8+
    pause
    exit /b 1
)

REM 检查依赖
echo 🔍 检查依赖包...
pip show requests >nul 2>&1
if errorlevel 1 (
    echo 📦 安装依赖包...
    pip install requests tqdm
)

REM 检查后端服务
echo 🔍 检查后端服务...
curl -s -o /dev/null -w "%%{http_code}" http://localhost:8000/docs | findstr "200" >nul
if errorlevel 1 (
    echo ❌ 错误: 后端服务未启动
    echo 请先启动后端服务: python -m app.main
    pause
    exit /b 1
)

echo ✅ 后端服务运行正常
echo.

REM 显示菜单
echo 请选择测试模式:
echo 1. 快速测试 (50条样本, ~1分钟)
echo 2. 完整测试 (500条样本, ~10分钟)
echo 3. 自定义样本量
echo 4. 退出
echo.

set /p choice="请输入选择 (1-4): "

if "%choice%"=="1" (
    echo.
    echo 🚀 开始快速测试...
    python backtest.py --quick
) else if "%choice%"=="2" (
    echo.
    echo 📊 开始完整测试...
    python backtest.py
) else if "%choice%"=="3" (
    echo.
    set /p sample_size="请输入样本量 (建议100-1000): "
    echo.
    echo 🎯 开始自定义测试...
    python backtest.py --sample %sample_size%
) else if "%choice%"=="4" (
    echo 退出
    exit /b 0
) else (
    echo ❌ 无效选择
    pause
    exit /b 1
)

echo.
echo ======================================
echo 测试完成！
echo ======================================
echo.
echo 📁 测试报告已保存到 results/ 目录:
echo   - JSON详细报告: backtest_report_YYYYMMDD_HHMMSS.json
echo   - 未命中案例: backtest_unhit_details_YYYYMMDD_HHMMSS.json
echo   - CSV统计表: backtest_hit_rate_by_rank_YYYYMMDD_HHMMSS.csv
echo   - HTML可视化报告: backtest_report_YYYYMMDD_HHMMSS.html
echo.

pause