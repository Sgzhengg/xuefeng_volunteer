@echo off
chcp 65001 >nul
echo ========================================
echo 使用Flutter中国镜像源启动
echo ========================================
echo.

REM 设置Flutter中国镜像源
set PUB_HOSTED_URL=https://pub.flutter-io.cn
set FLUTTER_STORAGE_BASE_URL=https://storage.flutter-io.cn

cd /d "%~dp0"

echo 镜像源已设置：
echo PUB_HOSTED_URL=%PUB_HOSTED_URL%
echo FLUTTER_STORAGE_BASE_URL=%FLUTTER_STORAGE_BASE_URL%
echo.

echo [1/3] 清理缓存...
call flutter clean

echo.
echo [2/3] 使用镜像源获取依赖...
call flutter pub get
if %errorlevel% neq 0 (
    echo 获取依赖失败！
    pause
    exit /b 1
)

echo.
echo [3/3] 启动应用...
echo 应用将启动在：http://localhost:8080
echo.
echo 按 Ctrl+C 停止应用
echo.
call flutter run -d chrome --web-port 8080

pause
