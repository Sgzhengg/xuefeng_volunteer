# Zeabur部署指南

## 项目概述

本项目包含两个主要部分：
1. **后端API** - Python FastAPI服务
2. **前端Web应用** - Flutter Web应用

## 部署架构

```
┌─────────────────┐
│   Zeabur Cloud   │
└─────────────────┘
        │
        ├──────────────┬──────────────┐
        │              │              │
    ┌───▼────┐    ┌───▼────────┐  ┌───▼───────┐
    │ 后端API │    │ 前端Web   │  │  数据库   │
    │ :8000  │    │ (静态文件) │  │ SQLite   │
    └────────┘    └────────────┘  └───────────┘
```

## 前置准备

### 1. Zeabur账户准备
- 注册 [Zeabur](https://zeabur.com) 账户
- 连接GitHub账户
- 确保有足够的配额（免费版通常足够）

### 2. 项目代码准备
- 确保代码已推送到GitHub仓库
- 检查分支名称（通常为`main`）

## 部署步骤

### 步骤1: 部署后端API服务

#### 1.1 在Zeabur创建新服务
1. 登录Zeabur控制台
2. 点击"Create New Service"
3. 选择"GitHub"连接仓库
4. 选择项目分支：`main`
5. 设置服务名称：`xuefeng-volunteer-api`

#### 1.2 配置后端服务
**Dockerfile位置**: `/backend/Dockerfile`

**构建配置**:
```yaml
Name: Build and Deploy
Dockerfile: backend/Dockerfile
Working Directory: /backend
```

**环境变量** (在Zeabur控制台设置):
```bash
PORT=8000
PYTHONUNBUFFERED=1
PYTHONDONTWRITEBYTECODE=1
OPENROUTER_API_KEY=your_api_key_here
```

**资源配置**:
- 内存: 512MB - 1GB
- CPU: 0.5 - 1 vCPU
- 端口: 8000

#### 1.3 启动后端服务
- 点击"Deploy"按钮
- 等待构建完成（通常需要3-5分钟）
- 记录部署后的URL，例如：`https://xuefeng-volunteer-api.zeabur.app`

### 步骤2: 部署前端Web应用

#### 2.1 本地构建Flutter Web
在项目根目录执行构建脚本：

**Windows用户**:
```bash
frontend_web_build.bat
```

**Linux/Mac用户**:
```bash
chmod +x frontend_web_build.sh
./frontend_web_build.sh
```

#### 2.2 将构建产物推送到GitHub
```bash
git add build/web
git commit -m "chore: 添加Flutter Web构建产物"
git push origin main
```

#### 2.3 在Zeabur创建前端服务
1. 创建新服务
2. 选择"GitHub"连接同一仓库
3. 选择分支：`main`

#### 2.4 配置前端服务
**服务类型**: 静态站点托管

**构建配置**:
```yaml
Working Directory: /
Build Command: (留空)
Output Directory: build/web
```

**环境变量**:
```bash
# API端点（使用部署后的后端URL）
VITE_API_URL=https://xuefeng-volunteer-api.zeabur.app
```

#### 2.5 启动前端服务
- 点击"Deploy"按钮
- 等待部署完成
- 记录前端URL，例如：`https://xuefeng-volunteer.zeabur.app`

### 步骤3: 配置域名（可选）

#### 3.1 配置后端域名
1. 在Zeabur控制台选择后端服务
2. 进入"Domains"设置
3. 添加自定义域名或使用Zeabur提供的域名

#### 3.2 配置前端域名
1. 在Zeabur控制台选择前端服务
2. 添加自定义域名
3. 配置DNS记录（如果使用自定义域名）

### 步骤4: 更新前端API配置

部署后需要更新前端的API地址：

#### 4.1 修改Flutter配置
编辑 `lib/core/api_service.dart`:
```dart
// 开发环境
static const String BASE_URL = 'http://localhost:8000';

// 生产环境（部署后）
static const String BASE_URL = 'https://xuefeng-volunteer-api.zeabur.app';
```

#### 4.2 重新构建并部署前端
```bash
# 修改API配置后重新构建
flutter build web --release

# 提交并推送
git add lib/core/api_service.dart
git commit -m "chore: 更新API地址为生产环境"
git push origin main
```

## 验证部署

### 1. 检查后端API
访问部署后的URL并测试：
```bash
# 健康检查
curl https://xuefeng-volunteer-api.zeabur.app/health

# 应该返回：
# {"status":"healthy","services":{"api":"ok","cache":"ok","admin":"ok"}}
```

### 2. 检查前端应用
访问前端URL并测试功能：
- 打开网页
- 测试API连接
- 验证主要功能正常

## 环境变量配置

### 必需环境变量
在Zeabur控制台中设置：

| 变量名 | 值 | 说明 |
|--------|-----|------|
| `PORT` | 8000 | API端口 |
| `OPENROUTER_API_KEY` | `your_key` | OpenRouter API密钥 |

### 可选环境变量
| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `ADMIN_USERNAME` | admin | 管理员用户名 |
| `ADMIN_PASSWORD` | password | 管理员密码 |
| `LOG_LEVEL` | INFO | 日志级别 |
| `DEFAULT_DATA_YEAR` | 2025 | 默认数据年份 |

## 数据持久化

### Zeabur存储卷配置
后端服务配置以下持久化存储：

```yaml
volumes:
  - /app/data      # 数据文件
  - /app/database   # 数据库文件
  - /app/logs      # 日志文件
```

### 数据备份建议
- 定期导出重要数据
- 使用版本控制系统备份配置
- 考虑使用外部数据库服务（如PostgreSQL）

## 监控和日志

### 查看日志
1. 在Zeabur控制台选择服务
2. 点击"Logs"查看实时日志
3. 可以下载日志文件进行分析

### 性能监控
- Zeabur提供基本的性能指标
- 可以设置告警规则
- 监控CPU、内存、网络使用情况

## 故障排查

### 常见问题

#### 1. 后端服务启动失败
**症状**: 服务无法启动或频繁重启

**解决方案**:
- 检查日志中的错误信息
- 验证环境变量配置正确
- 确认依赖包完整安装
- 检查端口配置

#### 2. 前端无法连接后端
**症状**: API调用失败

**解决方案**:
- 检查后端服务是否正常运行
- 验证CORS配置
- 确认API地址配置正确
- 检查网络连接

#### 3. 数据丢失
**症状**: 重启后数据丢失

**解决方案**:
- 检查持久化存储配置
- 验证数据文件路径正确
- 考虑使用外部数据库

## 性能优化

### 1. 后端优化
- 增加资源配额（内存/CPU）
- 启用缓存机制
- 优化数据库查询
- 使用CDN加速静态资源

### 2. 前端优化
- 启用代码分割
- 优化图片资源
- 使用懒加载
- 启用Gzip压缩

## 成本估算

### Zeabur免费套餐
- **每月免费小时数**: 通常为100-500小时
- **内存**: 512MB - 1GB
- **CPU**: 0.5 - 1 vCPU
- **存储**: 1GB
- **带宽**: 100GB

### 预估成本
- **个人项目**: 免费套餐通常足够
- **小型商业**: $5-20/月
- **中型应用**: $20-100/月

## 安全建议

### 1. API安全
- 使用HTTPS加密传输
- 启用认证机制
- 定期更新依赖包
- 配置防火墙规则

### 2. 数据安全
- 加密敏感数据
- 定期备份重要数据
- 使用强密码策略
- 限制API访问频率

### 3. 访问控制
- 配置白名单/黑名单
- 启用速率限制
- 监控异常访问
- 定期审计日志

## 更新部署

### 自动部署
Zeabur支持GitHub集成，可配置：
- 推送代码到`main`分支自动部署
- Pull Request合并后自动部署
- 定时自动构建和部署

### 手动部署
```bash
# 1. 修改代码
git add .
git commit -m "更新描述"
git push origin main

# 2. 在Zeabur控制台点击"Redeploy"
```

## 回滚策略

### 版本回滚
1. 在Zeabur控制台选择服务
2. 点击"Deployments"查看部署历史
3. 选择要回滚的版本
4. 点击"Redeploy"重新部署该版本

### 数据回滚
- 定期备份重要数据
- 使用版本控制系统
- 准备回滚脚本

## 扩展功能

### 数据库升级
- 从SQLite迁移到PostgreSQL
- 配置读写分离
- 实现数据库主从复制

### 负载均衡
- 部署多个后端实例
- 配置负载均衡器
- 实现会话共享

### CDN加速
- 配置静态资源CDN
- 启用边缘缓存
- 优化全球访问速度

## 技术支持

### 官档资源
- [Zeabur官方文档](https://zeabur.com/docs)
- [Docker最佳实践](https://docs.docker.com/)
- [Flutter Web部署](https://flutter.dev/web)

### 社区支持
- Zeabur Discord社区
- GitHub Issues
- Stack Overflow

---

**部署检查清单**

- [ ] Zeabur账户已创建
- [ ] GitHub仓库已连接
- [ ] 后端Dockerfile已创建
- [ ] 环境变量已配置
- [ ] 后端服务已部署
- [ ] 前端Web已构建
- [ ] 前端服务已部署
- [ ] API连接已测试
- [ ] 主要功能已验证
- [ ] 域名已配置（可选）
- [ ] 监控告警已设置
- [ ] 备份策略已制定

祝您部署顺利！🚀
