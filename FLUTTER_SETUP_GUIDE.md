# Flutter环境配置指南

## 📋 当前状态
- ✅ Flutter已安装 (3.24.5)
- ✅ 支持Web开发 (Chrome/Edge)
- ❌ Android开发需要Android Studio
- ❌ 网络连接有问题（无法访问pub.dev）

## 🎯 两种解决方案

### 方案一：专注于Web开发（推荐）
当前项目可以正常运行Web版本，无需Android配置。

### 方案二：配置Android开发
如果需要Android应用，按以下步骤配置：

## 📲 Android配置步骤

### 第1步：下载Android Studio
1. 访问：https://developer.android.com/studio
2. 下载Windows版本
3. 运行安装程序，选择"Custom"自定义安装
4. 务必勾选：
   - ✅ Android SDK
   - ✅ Android Virtual Device
   - ✅ Android SDK Platform-Tools
   - ✅ Intel x86 Emulator Accelerator (HAXM installer)

### 第2步：配置环境变量
1. 打开"编辑系统环境变量"
2. 在"Path"中添加：
   ```
   C:\Users\18826\AppData\Local\Android\Sdk\platform-tools
   C:\Users\18826\AppData\Local\Android\Sdk\tools
   C:\Users\18826\AppData\Local\Android\Sdk\cmdline-tools\latest\bin
   ```

### 第3步：运行配置脚本
```cmd
# 双击运行
C:\Users\18826\Desktop\setup_flutter_android.bat
```

### 第4步：创建Android虚拟设备
```cmd
# 安装完成后运行
flutter emulators
# 创建新设备
flutter emulators --create --name Pixel_4_API_30
# 启动模拟器
flutter emulators --launch Pixel_4_API_30
```

## 🌐 Web开发方案（无需Android）

由于网络连接问题，我们使用Web版本来运行项目：

### 1. 运行后端服务
```cmd
cd d:\xuefeng_volunteer\backend
python simple_server.py
```

### 2. 运行前端
```cmd
# 方式A：使用HTTP服务器
cd d:\xuefeng_volunteer
python -m http.server 8080

# 方式B：打开Web界面
# 浏览器访问：http://localhost:8080/frontend.html
# 或访问高级版：http://xuefeng_volunteer/ADVANCED_WEB_APP/index.html
```

### 3. 功能说明
- ✅ 聊天功能（Mock数据）
- ✅ 志愿模拟器
- ✅ 实时响应
- ✅ 现代化界面

## 🔧 常见问题

### 网络连接问题
```
X A network error occurred while checking "https://pub.dev/"
```
**解决方案**：使用Web版本，无需依赖pub.dev

### Android SDK路径问题
```
X Unable to locate Android SDK.
```
**解决方案**：按上述步骤安装Android Studio

### 模拟器无法启动
1. 确保已安装Intel HAXM
2. 在BIOS中启用虚拟化技术
3. 尝试不同的AVD配置

## 📱 移动开发替代方案

如果确实需要移动应用，考虑：

### 1. Flutter Web打包
```cmd
flutter build web --web-renderer canvaskit
```
生成的Web应用可以在手机浏览器中访问

### 2. 使用混合开发
- 使用WebView包装Web应用
- 发布为PWA（Progressive Web App）
- 使用Flutter to Web编译

## 🎯 推荐操作

1. **立即使用Web版本**
   - 无需安装Android Studio
   - 功能完整可用
   - 支持所有桌面浏览器

2. **可选：配置Android开发**
   - 如果确实需要Android应用
   - 按照上述步骤配置
   - 测试完成后再部署

## 📞 技术支持

遇到问题时：
1. 查看 `CLEANUP_REPORT.md` 了解项目结构
2. 检查后端服务是否运行在端口5000
3. 确认Web界面是否正常访问

---

**注意**：当前网络环境下，Web版本是最佳选择！