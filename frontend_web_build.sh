#!/bin/bash

# Flutter Web 部署构建脚本
# 用于Zeabur部署

set -e

echo "🚀 开始构建Flutter Web应用..."

# 检查Flutter环境
if ! command -v flutter &> /dev/null; then
    echo "❌ Flutter未安装，请先安装Flutter SDK"
    exit 1
fi

# 设置镜像源（国内用户）
export PUB_HOSTED_URL=https://pub.flutter-io.cn
export FLUTTER_STORAGE_BASE_URL=https://storage.flutter-io.cn

echo "📦 获取Flutter依赖..."
flutter pub get

echo "🏗️  构建Web应用（Release模式）..."
flutter build web --release

echo "✅ 构建完成！"
echo "📁 构建产物位置: build/web"

# 检查构建产物
if [ -d "build/web" ]; then
    file_count=$(find build/web -type f | wc -l)
    echo "📊 生成了 $file_count 个文件"
    echo "📦 总大小: $(du -sh build/web | cut -f1)"
else
    echo "❌ 构建失败：build/web目录不存在"
    exit 1
fi

echo "🎉 Flutter Web应用已准备就绪！"
