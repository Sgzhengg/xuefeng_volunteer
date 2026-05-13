@echo off
chcp 65001 >nul
echo ========================================
echo Flutter Web 部署构建脚本
echo ========================================
echo.

echo [1/3] 设置镜像源...
set PUB_HOSTED_URL=https://pub.flutter-io.cn
set FLUTTER_STORAGE_BASE_URL=https://storage.flutter-io.cn
echo ✓ 镜像源已设置

echo.
echo [2/3] 获取依赖...
call flutter pub get
echo ✓ 依赖已安装

echo.
echo [3/3] 构建Web应用...
call flutter build web --release
echo ✓ 构建完成

echo.
echo ========================================
echo 构建完成！
echo 产物位置: build/web
echo ========================================
pause
