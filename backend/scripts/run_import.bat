@echo off
chcp 65001 >nul
echo ======================================
echo 2025年高考数据批量导入工具
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
echo 🔄 检查依赖...
pip show requests >nul 2>&1
if errorlevel 1 (
    echo 📦 安装依赖包...
    pip install requests chardet
)

REM 创建必要目录
if not exist "..\data" mkdir "..\data"
if not exist "province_data_2025" mkdir "province_data_2025"
if not exist "logs" mkdir "logs"

echo.
echo 📂 请将省份CSV文件放入以下目录结构:
echo    province_data_2025\
echo    ├── 广东\
echo    │   ├── 2025年本科录取数据.csv
echo    │   └── 2025年专科录取数据.csv
echo    ├── 河南\
echo    ├── 山东\
echo    └── ...
echo.
echo ⚠️  确保后端服务已启动 (python -m app.main)
echo.

pause

echo.
echo 🚀 开始导入...
echo.

python import_2025_data.py

echo.
echo pause
