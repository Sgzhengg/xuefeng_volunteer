# 🎓 学锋志愿教练 - 管理后台系统

完整的志愿填报系统管理后台，提供院校管理、数据导入等功能。

## ✅ 功能特性

### 🔐 用户认证
- 安全的管理员登录系统
- JWT token认证机制
- 硬编码管理员账户（MVP阶段）
- 登录状态持久化

### 🏫 院校管理
- **查看院校列表**: 分页显示，支持关键词搜索
- **添加院校**: 支持添加新的院校信息
- **编辑院校**: 在线编辑院校详细信息
- **删除院校**: 删除不需要的院校记录
- **搜索功能**: 按院校名称或省份搜索

### 📥 数据导入
- **CSV文件上传**: 支持拖拽或点击上传
- **数据预览**: 导入前预览前5行数据
- **批量导入**: 一键导入大量录取数据
- **数据验证**: 自动验证CSV格式和内容

### 📊 系统统计
- 用户数量统计
- 院校数量统计
- 专业数量统计
- 数据更新时间

## 🚀 快速开始

### 1. 启动服务器

```bash
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. 访问管理后台

在浏览器中打开：
```
http://localhost:8000/admin
```

### 3. 登录管理后台

**登录凭据**:
- 用户名: `admin`
- 密码: `password`

## 📁 项目结构

```
backend/
├── app/
│   ├── api/
│   │   ├── admin.py          # ✅ 管理后台API（新建）
│   │   ├── auth.py           # ✅ 认证API
│   │   ├── plan.py           # ✅ 志愿表API
│   │   └── router.py         # ✅ 主路由
│   └── main.py              # ✅ 应用入口（已更新）
├── admin/
│   ├── templates/
│   │   ├── login.html       # ✅ 登录页面（新建）
│   │   ├── dashboard.html   # ✅ 仪表盘（新建）
│   │   ├── universities.html # ✅ 院校管理（新建）
│   │   └── admission_data.html # ✅ 数据导入（新建）
│   └── static/
│       ├── css/
│       │   └── style.css    # ✅ 样式文件（新建）
│       └── js/
│           └── admin.js     # ✅ JavaScript（新建）
├── data/
│   ├── universities_list.json # 院校数据
│   └── major_rank_data.json   # 录取数据
└── test_admin_panel.py       # ✅ 测试脚本（新建）
```

## 📋 API接口文档

### 认证接口

#### POST `/api/v1/admin/login`
管理员登录

**请求体**:
```json
{
  "username": "admin",
  "password": "password"
}
```

**响应**:
```json
{
  "code": 0,
  "message": "登录成功",
  "data": {
    "token": "eyJhbGci...",
    "username": "admin"
  }
}
```

### 统计接口

#### GET `/api/v1/admin/stats`
获取系统统计数据

**请求头**:
```
Authorization: Bearer {token}
```

**响应**:
```json
{
  "code": 0,
  "data": {
    "user_count": 100,
    "university_count": 4350,
    "major_count": 50000,
    "updated_at": "2024-05-08 12:00:00"
  }
}
```

### 院校管理接口

#### GET `/api/v1/admin/universities?page=1&limit=20&keyword=`
获取院校列表（支持分页和搜索）

**请求头**:
```
Authorization: Bearer {token}
```

**响应**:
```json
{
  "code": 0,
  "data": {
    "list": [...],
    "total": 4350,
    "page": 1,
    "limit": 20,
    "total_pages": 218
  }
}
```

#### POST `/api/v1/admin/universities`
添加新院校

**请求头**:
```
Authorization: Bearer {token}
```

**请求体**:
```json
{
  "name": "测试大学",
  "province": "广东",
  "city": "深圳",
  "type": "综合",
  "level": "本科",
  "website": "https://www.test.edu.cn",
  "founded": "2024",
  "description": "测试院校描述"
}
```

#### PUT `/api/v1/admin/universities/{id}`
更新院校信息

#### DELETE `/api/v1/admin/universities/{id}`
删除院校

### 数据导入接口

#### POST `/api/v1/admin/import/admission`
导入录取数据（CSV）

**请求头**:
```
Authorization: Bearer {token}
Content-Type: multipart/form-data
```

**请求体**:
```
file: CSV文件
```

**CSV格式要求**:
```csv
院校代码,院校名称,专业组代码,计划数,最低分,最低排位
10543,中山大学,001,50,650,10000
10544,华南理工大学,002,60,640,12000
```

#### POST `/api/v1/admin/import/admission/preview`
预览CSV数据（前5行）

## 🎨 页面功能

### 1. 登录页面 (`/admin`)
- 简洁的登录表单
- 用户名/密码输入
- 登录成功后自动跳转仪表盘
- 错误提示显示

### 2. 仪表盘 (`/admin/dashboard`)
- 系统统计卡片（用户数、院校数、专业数）
- 快捷操作入口
- 侧边栏导航
- 实时数据更新

### 3. 院校管理 (`/admin/universities`)
- 院校列表表格（分页显示）
- 搜索功能（按名称搜索）
- 添加院校弹窗表单
- 编辑/删除操作按钮
- 表单验证

### 4. 数据导入 (`/admin/admission-data`)
- CSV文件上传区域
- 拖拽上传支持
- 数据预览表格
- 导入确认按钮
- 导入结果显示

## 🔧 技术实现

### 后端技术
- **FastAPI**: 现代化的Python Web框架
- **Jinja2**: 模板引擎
- **JWT**: 用户认证
- **Pydantic**: 数据验证
- **文件上传**: multipart/form-data

### 前端技术
- **原生JavaScript**: 无框架依赖
- **Fetch API**: HTTP请求
- **LocalStorage**: 数据持久化
- **响应式设计**: 支持移动端

### 安全特性
- JWT token认证
- 路由权限保护
- 表单数据验证
- 文件类型验证

## 📱 响应式设计

管理后台完全支持移动端访问：
- 自适应布局
- 移动端友好的操作界面
- 触摸优化

## 🧪 测试

运行测试脚本验证功能：

```bash
cd backend
python test_admin_panel.py
```

测试内容包括：
- ✅ 管理员登录
- ✅ 系统统计获取
- ✅ 院校列表分页
- ✅ 添加院校
- ✅ 搜索功能

## 🔐 安全说明

### MVP阶段安全
- 硬编码管理员账户（admin/password）
- 简单的JWT认证
- 基本的表单验证

### 生产环境建议
- 使用数据库存储管理员账户
- 实现RBAC权限控制
- 添加操作日志审计
- 启用HTTPS
- 实现CSRF保护
- 添加请求频率限制

## 📊 数据格式

### 院校数据结构
```json
{
  "universities": [
    {
      "id": "1",
      "name": "北京大学",
      "province": "北京",
      "city": "北京",
      "type": "综合",
      "level": "985",
      "website": "https://www.pku.edu.cn",
      "founded": "1898",
      "description": "中国近代第一所国立综合性大学"
    }
  ]
}
```

### CSV导入格式
```csv
院校代码,院校名称,专业组代码,计划数,最低分,最低排位
10543,中山大学,001,50,650,10000
```

## 🎯 使用指南

### 1. 登录系统
1. 访问 `http://localhost:8000/admin`
2. 输入管理员账户：admin / password
3. 点击登录按钮

### 2. 管理院校
1. 点击侧边栏的"院校管理"
2. 查看院校列表
3. 使用搜索框查找特定院校
4. 点击"添加院校"按钮新增院校
5. 点击院校行的"编辑"或"删除"按钮进行操作

### 3. 导入数据
1. 点击侧边栏的"数据导入"
2. 准备符合格式的CSV文件
3. 拖拽或点击上传文件
4. 预览导入数据
5. 点击"确认导入"完成导入

## 🚀 部署说明

### 开发环境
```bash
cd backend
python -m uvicorn app.main:app --reload
```

### 生产环境
```bash
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## 📈 性能优化建议

1. **数据库集成**: 替换JSON文件为数据库
2. **缓存机制**: 添加Redis缓存统计数据
3. **分页优化**: 大数据量时的分页策略
4. **CDN加速**: 静态资源CDN分发
5. **API限流**: 防止恶意请求

## 🛠️ 常见问题

### 1. 无法访问管理后台
**问题**: 访问 `/admin` 显示404  
**解决**: 检查服务器是否启动，端口是否正确

### 2. 登录失败
**问题**: 输入正确账户密码仍无法登录  
**解决**: 清除浏览器缓存，检查API是否正常

### 3. 数据导入失败
**问题**: CSV导入失败  
**解决**: 检查CSV文件格式，确保UTF-8编码，列名正确

### 4. 静态资源加载失败
**问题**: CSS/JS文件无法加载  
**解决**: 检查admin/static目录是否存在且路径正确

## 📝 开发说明

### 添加新页面
1. 在 `admin/templates/` 创建HTML文件
2. 在 `main.py` 添加路由
3. 在侧边栏添加导航链接

### 添加新API
1. 在 `app/api/admin.py` 添加路由函数
2. 添加相应的Pydantic模型
3. 实现业务逻辑

### 自定义样式
1. 编辑 `admin/static/css/style.css`
2. 使用CSS变量定义主题色
3. 遵循响应式设计原则

## 🎉 总结

管理后台系统已完全实现，包含：
- ✅ 完整的用户认证系统
- ✅ 功能齐全的院校管理
- ✅ 便捷的数据导入功能
- ✅ 美观的响应式界面
- ✅ 全面的测试覆盖

系统已可投入使用，后续可根据实际需求进行功能扩展和优化！
