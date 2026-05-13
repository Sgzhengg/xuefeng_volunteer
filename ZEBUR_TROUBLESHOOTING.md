# Zeabur部署故障排除指南

## ⚠️ 重要：正确的部署架构

### 只有2个服务，不是3个！

1. **后端API服务** (`backend-api`)
   - 包含：RESTful API + 管理后台
   - Dockerfile路径：`backend/Dockerfile`
   - 端口：8000
   - 访问路径：
     - API: `https://your-backend.zeabur.app/api/v1/*`
     - 管理后台: `https://your-backend.zeabur.app/admin`

2. **前端Web服务** (`frontend-web`)
   - 静态站点托管
   - 输出目录：`build/web`
   - 访问路径：`https://your-frontend.zeabur.app`

**❌ 不要创建单独的"管理后台"服务** - 它已经包含在后端API中！

---

## 🔧 常见部署失败问题修复

### 问题1: 前端服务部署失败 - "找不到构建产物"

**原因**：`build/web`目录不存在

**解决步骤**：
```bash
# 1. 运行构建脚本
flutter build web --release

# 2. 验证构建产物
test -d build/web && echo "✓ 构建成功" || echo "✗ 构建失败"

# 3. 推送到GitHub
git add build/web
git commit -m "chore: 添加Flutter Web构建产物"
git push origin main
```

### 问题2: 后端服务启动失败 - "健康检查失败"

**原因**：Dockerfile中使用`curl`命令不可用

**已修复**：Dockerfile已更新为使用Python进行健康检查

**验证修复**：
```dockerfile
# 新的健康检查（已修复）
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1
```

### 问题3: 依赖安装失败

**原因**：Python包版本冲突或缺少系统依赖

**解决步骤**：
1. 检查`requirements.txt`版本兼容性
2. 确保Dockerfile包含必要的系统包：
```dockerfile
RUN apt-get update && apt-get install -y \
    gcc g++ curl \
    && rm -rf /var/lib/apt/lists/*
```

### 问题4: 环境变量配置错误

**必需的环境变量**：
```bash
PORT=8000
PYTHONUNBUFFERED=1
```

**可选的环境变量**：
```bash
OPENROUTER_API_KEY=your_api_key_here
ADMIN_USERNAME=admin
ADMIN_PASSWORD=password
```

---

## 🚀 正确的部署步骤

### 步骤1: 准备代码

```bash
# 1. 确保在main分支
git checkout main

# 2. 构建前端
flutter build web --release

# 3. 推送所有代码
git add .
git commit -m "chore: 准备Zeabur部署"
git push origin main
```

### 步骤2: 在Zeabur创建服务

#### 服务1: 后端API
1. 点击"Create New Service"
2. 选择GitHub仓库：`xuefeng_volunteer`
3. 选择分支：`main`
4. 配置：
   - **服务名称**: `backend-api`
   - **Dockerfile路径**: `backend/Dockerfile`
   - **工作目录**: `/backend`
   - **端口**: `8000`
5. 环境变量：
   ```
   PORT=8000
   PYTHONUNBUFFERED=1
   ```
6. 点击"Deploy"

#### 服务2: 前端Web
1. 点击"Create New Service"
2. 选择GitHub仓库：`xuefeng_volunteer`
3. 选择分支：`main`
4. 配置：
   - **服务名称**: `frontend-web`
   - **服务类型**: 静态站点
   - **输出目录**: `build/web`
5. 点击"Deploy"

### 步骤3: 验证部署

```bash
# 1. 检查后端健康状态
curl https://your-backend.zeabur.app/health

# 2. 访问管理后台
# 浏览器打开: https://your-backend.zeabur.app/admin
# 登录: admin / password

# 3. 测试前端
# 浏览器打开: https://your-frontend.zeabur.app
```

---

## 🛠️ 调试技巧

### 查看部署日志

1. 进入Zeabur控制台
2. 选择失败的服务
3. 点击"Logs"查看详细错误信息
4. 常见错误：
   - `ModuleNotFoundError`: 缺少依赖包
   - `Permission denied`: 文件权限问题
   - `Connection refused`: 端口配置错误

### 重新部署

```bash
# 方法1: 在Zeabur控制台点击"Redeploy"

# 方法2: 推送新代码触发自动部署
git commit --allow-empty -m "trigger: 重新部署"
git push origin main
```

### 本地测试Docker镜像

```bash
# 1. 构建镜像
cd backend
docker build -t xuefeng-backend .

# 2. 运行容器
docker run -p 8000:8000 -e PORT=8000 xuefeng-backend

# 3. 测试健康检查
curl http://localhost:8000/health
```

---

## 📊 资源配置建议

### 免费套餐配置

**后端API**:
- 内存: 512MB
- CPU: 0.5 vCPU
- 存储: 1GB

**前端Web**:
- 内存: 256MB
- CPU: 0.2 vCPU
- 存储: 500MB

### 性能优化

如果遇到性能问题：
1. 增加内存配额到1GB
2. 启用CDN加速
3. 配置持久化存储
4. 优化数据库查询

---

## 🔐 安全配置

### 修改默认密码

部署后立即修改管理员密码：
1. 访问管理后台
2. 登录后修改密码
3. 或设置环境变量：
   ```
   ADMIN_PASSWORD=your_secure_password
   ```

### 配置HTTPS

Zeabur自动提供SSL证书，确保：
- 使用HTTPS访问
- 更新前端API地址为HTTPS
- 配置CORS允许HTTPS请求

---

## 🆘 获取帮助

### 检查清单

- [ ] 前端已构建（`build/web`存在）
- [ ] Dockerfile语法正确
- [ ] 环境变量已配置
- [ ] 端口配置正确（8000）
- [ ] 只创建了2个服务（不是3个）
- [ ] GitHub代码已推送
- [ ] 分支选择正确（main）

### 仍然失败？

1. 查看完整的部署日志
2. 检查Zeabur服务状态页面
3. 尝试在本地构建Docker镜像
4. 提交错误日志到GitHub Issues

---

**最后更新**: 2026-05-13
**相关文档**:
- [QUICK_START_ZEBUR.md](QUICK_START_ZEBUR.md)
- [ZEBUR_DEPLOYMENT_GUIDE.md](ZEBUR_DEPLOYMENT_GUIDE.md)