# Zeabur快速部署指南

## 5分钟快速部署

### 第一步：准备GitHub仓库（2分钟）

1. 确保代码已推送到GitHub
2. 检查当前分支为`main`

```bash
git status
git add .
git commit -m "准备部署到Zeabur"
git push origin main
```

### 第二步：部署后端API（2分钟）

1. 访问 [Zeabur.com](https://zeabur.com) 并登录
2. 点击"Create New Service"
3. 连接GitHub仓库，选择`xuefeng_volunteer`项目
4. 配置服务：
   - **名称**: `xuefeng-backend`
   - **Dockerfile路径**: `/backend/Dockerfile`
   - **工作目录**: `/backend`
   - **环境变量**:
     ```
     PORT=8000
     PYTHONUNBUFFERED=1
     ```
5. 点击"Deploy"

### 第三步：构建并部署前端（1分钟）

1. 在本地构建Flutter Web应用：
   ```bash
   # Windows
   frontend_web_build.bat

   # Mac/Linux
   chmod +x frontend_web_build.sh
   ./frontend_web_build.sh
   ```

2. 将构建产物推送到GitHub：
   ```bash
   git add build/web
   git commit -m "chore: 添加Web构建产物"
   git push origin main
   ```

3. 在Zeabur创建前端服务：
   - **名称**: `xuefeng-frontend`
   - **类型**: 静态站点
   - **输出目录**: `/build/web`

4. 点击"Deploy"

### 完成！

访问您的应用：
- **后端API**: `https://xuefeng-backend.zeabur.app`
- **前端应用**: `https://xuefeng-frontend.zeabur.app`

## 配置API密钥

在Zeabur后端服务中添加环境变量：
```
OPENROUTER_API_KEY=your_actual_api_key_here
```

## 更新前端API地址

修改 `lib/core/api_service.dart`:
```dart
// 将开发环境地址改为生产地址
static const String BASE_URL = 'https://xuefeng-backend.zeabur.app';
```

## 测试部署

```bash
# 测试后端健康检查
curl https://xuefeng-backend.zeabur.app/health

# 测试前端
# 在浏览器打开前端URL并测试功能
```

## 常见问题

**Q: 构建失败怎么办？**
A: 检查Dockerfile语法，确保所有依赖都在requirements.txt中

**Q: API调用失败？**
A: 检查CORS配置，确认API地址正确

**Q: 数据丢失？**
A: 检查Zeabur存储卷配置，确保数据目录正确挂载

**Q: 性能问题？**
A: 在Zeabur控制台增加资源配置

## 下一步

- 配置自定义域名
- 设置数据库备份
- 配置CDN加速
- 启用监控告警

详细部署指南请查看 [ZEBUR_DEPLOYMENT_GUIDE.md](ZEBUR_DEPLOYMENT_GUIDE.md)
