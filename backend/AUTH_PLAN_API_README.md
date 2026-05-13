# 认证和志愿表API文档

## 概述

本系统为学锋志愿教练提供了完整的用户认证和志愿表管理功能，使用内存存储（MVP阶段），包含以下特性：

- 🔐 用户认证：手机号+验证码登录
- 📝 志愿管理：增删改查用户志愿
- 📊 智能评估：自动评估志愿表合理性并给出建议

## 快速开始

### 1. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 2. 启动服务

```bash
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. 测试API

```bash
# 运行测试脚本
python backend/test_auth_plan_api.py
```

或者访问API文档：`http://localhost:8000/docs`

## API接口说明

### 认证模块

#### 1. 发送验证码

**接口：** `POST /api/v1/auth/send_code`

**请求体：**
```json
{
  "phone": "13800138000"
}
```

**响应：**
```json
{
  "code": 0,
  "message": "验证码已发送（测试：123456）"
}
```

**注意：** MVP阶段验证码固定为`123456`，不实际发送短信。

#### 2. 用户登录

**接口：** `POST /api/v1/auth/login`

**请求体：**
```json
{
  "phone": "13800138000",
  "code": "123456"
}
```

**响应：**
```json
{
  "code": 0,
  "message": "登录成功",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
      "phone": "13800138000",
      "user_id": "13800138000"
    }
  }
}
```

**说明：**
- JWT token有效期为7天
- 验证码错误或过期会返回相应的错误信息

#### 3. 获取用户信息

**接口：** `GET /api/v1/auth/me`

**请求头：**
```
Authorization: Bearer {token}
```

**响应：**
```json
{
  "code": 0,
  "message": "获取成功",
  "data": {
    "user_id": "13800138000",
    "phone": "13800138000",
    "created_at": "2024-01-01T12:00:00"
  }
}
```

### 志愿表模块

**注意：** 所有志愿表接口都需要登录认证，需要在请求头中携带token。

#### 1. 获取志愿列表

**接口：** `GET /api/v1/plan/list`

**请求头：**
```
Authorization: Bearer {token}
```

**响应：**
```json
{
  "code": 0,
  "message": "获取成功",
  "data": {
    "plans": [
      {
        "id": "中山大学_计算机科学与技术",
        "university_id": "sysu",
        "major_id": "cs",
        "university_name": "中山大学",
        "major_name": "计算机科学与技术",
        "probability": 70,
        "roi_score": 85,
        "tag": "稳",
        "created_at": "2024-01-01T12:00:00"
      }
    ],
    "total": 1
  }
}
```

#### 2. 添加志愿

**接口：** `POST /api/v1/plan/add`

**请求头：**
```
Authorization: Bearer {token}
```

**请求体：**
```json
{
  "university_id": "sysu",
  "major_id": "cs",
  "university_name": "中山大学",
  "major_name": "计算机科学与技术",
  "probability": 70,
  "roi_score": 85,
  "tag": "稳"
}
```

**响应：**
```json
{
  "code": 0,
  "message": "添加成功"
}
```

**字段说明：**
- `university_id`: 院校ID
- `major_id`: 专业ID
- `university_name`: 院校名称
- `major_name`: 专业名称
- `probability`: 录取概率（0-100）
- `roi_score`: ROI得分（0-100）
- `tag`: 志愿类型（"冲"、"稳"、"保"）

#### 3. 删除志愿

**接口：** `DELETE /api/v1/plan/remove?major_id={major_id}`

**请求头：**
```
Authorization: Bearer {token}
```

**响应：**
```json
{
  "code": 0,
  "message": "删除成功"
}
```

#### 4. 评估志愿表

**接口：** `GET /api/v1/plan/evaluate`

**请求头：**
```
Authorization: Bearer {token}
```

**响应：**
```json
{
  "code": 0,
  "message": "评估成功",
  "data": {
    "overall_score": 85,
    "risk_level": "low",
    "chong_count": 2,
    "wen_count": 5,
    "bao_count": 3,
    "warnings": [],
    "suggestions": [
      {
        "content": "志愿表结构合理，继续保持！"
      }
    ],
    "evaluated_at": "2024-01-01T12:00:00"
  }
}
```

**评估规则：**
1. **基础分100分**，根据以下规则扣分
2. **冲刺 > 6**：扣20分
3. **保底 < 3**：扣20分
4. **稳妥+保底 < 10**：扣15分
5. **总数 < 8**：扣10分

**风险等级：**
- `low`: 80分及以上
- `medium`: 60-79分
- `high`: 60分以下

## 数据存储

### 内存存储结构

```python
# 用户会话
sessions = {
    "13800138000": {
        "user_id": "13800138000",
        "phone": "13800138000",
        "created_at": "2024-01-01T12:00:00"
    }
}

# 志愿表数据
user_plans = {
    "13800138000": [
        {
            "id": "中山大学_计算机科学与技术",
            "university_id": "sysu",
            "major_id": "cs",
            "university_name": "中山大学",
            "major_name": "计算机科学与技术",
            "probability": 70,
            "roi_score": 85,
            "tag": "稳",
            "created_at": "2024-01-01T12:00:00"
        }
    ]
}

# 验证码存储（5分钟过期）
verification_codes = {
    "13800138000": {
        "code": "123456",
        "expire_time": "2024-01-01T12:05:00"
    }
}
```

## 依赖说明

### 新增依赖

```txt
python-jose[cryptography]==3.3.0  # JWT token生成和验证
passlib[bcrypt]==1.7.4           # 密码加密（预留）
```

### 安装命令

```bash
pip install python-jose[cryptography]==3.3.0
pip install passlib[bcrypt]==1.7.4
```

## 错误码说明

| 错误码 | 说明 |
|--------|------|
| 0 | 成功 |
| 1 | 业务逻辑错误（如验证码错误、志愿不存在等） |
| 401 | 认证失败（token无效或过期） |
| 500 | 服务器内部错误 |

## 部署注意事项

### 生产环境配置

1. **JWT密钥**：使用环境变量配置
```python
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
```

2. **数据库**：替换内存存储为数据库
```python
# 推荐使用：PostgreSQL、MySQL
```

3. **短信服务**：集成真实短信服务
```python
# 推荐使用：阿里云短信、腾讯云短信
```

4. **CORS配置**：限制允许的域名
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # 限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 测试用例

### 完整测试流程

1. **注册/登录**
```bash
curl -X POST http://localhost:8000/api/v1/auth/send_code \
  -H "Content-Type: application/json" \
  -d '{"phone": "13800138000"}'

curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"phone": "13800138000", "code": "123456"}'
```

2. **管理志愿**
```bash
# 添加志愿
curl -X POST http://localhost:8000/api/v1/plan/add \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "university_id": "sysu",
    "major_id": "cs",
    "university_name": "中山大学",
    "major_name": "计算机科学与技术",
    "probability": 70,
    "roi_score": 85,
    "tag": "稳"
  }'

# 获取志愿列表
curl http://localhost:8000/api/v1/plan/list \
  -H "Authorization: Bearer YOUR_TOKEN"

# 评估志愿表
curl http://localhost:8000/api/v1/plan/evaluate \
  -H "Authorization: Bearer YOUR_TOKEN"

# 删除志愿
curl -X DELETE "http://localhost:8000/api/v1/plan/remove?major_id=cs" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 常见问题

### 1. Token过期怎么办？

答：Token有效期为7天，过期后需要重新登录获取新token。

### 2. 验证码有效期多长？

答：验证码有效期为5分钟，过期需要重新获取。

### 3. MVP阶段数据会丢失吗？

答：是的，当前使用内存存储，服务重启后数据会丢失。生产环境需要使用数据库持久化。

### 4. 如何扩展认证方式？

答：可以在`auth.py`中添加密码登录、第三方登录等方式。

## 下一步计划

- [ ] 集成真实短信服务
- [ ] 使用数据库替换内存存储
- [ ] 添加微信登录支持
- [ ] 实现志愿表导入导出功能
- [ ] 添加志愿填报历史记录
