# 考生查分系统设计方案

## 📋 查分流程详解

### 1. 传统查分流程

```
考生 → 教育考试院官网 → 输入信息 → 查询成绩
```

### 2. 本系统集成查分流程

```
考生 → 本App → 后端API → 教育考试院API → 返回成绩
```

## 🔐 需要的输入信息

### 基础信息（必需）
- **准考证号** (exam_id) - 14位数字
- **身份证号** (id_card) - 18位身份证号码
- **考生姓名** (name) - 用于验证

### 辅助信息（可选）
- **省份** (province) - 确定考试院
- **科类** (subject_type) - 文科/理科/综合
- **验证码** (captcha) - 防止爬虫

## 📊 查分返回数据

### 成绩信息
```json
{
  "exam_id": "1425********01",
  "name": "张三",
  "province": "广东",
  "year": 2025,

  "总分": 620,

  "各科成绩": {
    "语文": 125,
    "数学": 138,
    "英语": 130,
    "综合": 195,
    "听力": 32    // 部分省份
  },

  "位次信息": {
    "全省排名": 8500,
    "科类排名": 7200,
    "一分一段": "620分对应8500位"
  },

  "其他信息": {
    "性别": "男",
    "学校": "XX中学",
    "考生类别": "城市应届",
    "查询时间": "2025-06-25 10:30:00"
  }
}
```

## 🔧 系统需要的接口

### 1. 前端界面

#### 查分页面
```dart
// lib/features/score_query/score_query_page.dart
class ScoreQueryPage extends StatefulWidget {
  @override
  State<ScoreQueryPage> createState() => _ScoreQueryPageState();
}

class _ScoreQueryPageState extends State<ScoreQueryPage> {
  final _examIdController = TextEditingController();
  final _idCardController = TextEditingController();
  final _nameController = TextEditingController();
  final _captchaController = TextEditingController();

  // 查询成绩
  Future<void> _queryScore() async {
    final result = await scoreQueryApiService.queryScore(
      examId: _examIdController.text,
      idCard: _idCardController.text,
      name: _nameController.text,
      captcha: _captchaController.text,
    );

    // 显示成绩
    _showScoreDialog(result);
  }
}
```

### 2. 后端API接口

#### 查分API端点
```python
# backend/app/api/score_query.py

@router.post("/score/query")
async def query_score(request: ScoreQueryRequest):
    """
    查询高考成绩

    Args:
        request: 包含准考证号、身份证号、姓名等

    Returns:
        成绩信息
    """
    try:
        # 1. 验证输入信息
        if not validate_input(request):
            raise HTTPException(status_code=400, detail="输入信息不合法")

        # 2. 调用教育考试院API
        score_data = await education_api_service.query_score(
            exam_id=request.exam_id,
            id_card=request.id_card,
            name=request.name,
            province=request.province
        )

        # 3. 保存查询记录（可选）
        await save_query_history(request, score_data)

        # 4. 返回成绩
        return {
            "success": True,
            "data": score_data
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/score/captcha")
async def get_captcha(province: str):
    """
    获取验证码图片

    Args:
        province: 省份，不同省份验证码不同

    Returns:
        验证码图片
    """
    captcha_image = await education_api_service.get_captcha(province)
    return Response(content=captcha_image, media_type="image/png")
```

### 3. 教育考试院API适配器

#### 统一接口适配
```python
# backend/app/services/education_api_service.py

class EducationAPIService:
    """教育考试院API服务"""

    def __init__(self):
        self.apis = {
            "广东": GuangdongEducationAPI(),
            "河南": HenanEducationAPI(),
            "山东": ShandongEducationAPI(),
            # ... 其他省份
        }

    async def query_score(self, exam_id: str, id_card: str,
                         name: str, province: str) -> dict:
        """查询成绩"""
        api = self.apis.get(province)

        if not api:
            raise ValueError(f"暂不支持{province}省份")

        # 调用具体省份API
        score_data = await api.query_score(
            exam_id=exam_id,
            id_card=id_card,
            name=name
        )

        return score_data

    async def get_captcha(self, province: str) -> bytes:
        """获取验证码"""
        api = self.apis.get(province)
        return await api.get_captcha()
```

#### 具体省份实现（以广东为例）
```python
# backend/app/services/education_apis/guangdong.py

class GuangdongEducationAPI:
    """广东省教育考试院API"""

    BASE_URL = "https://eea.gd.gov.cn"

    async def query_score(self, exam_id: str, id_card: str,
                         name: str) -> dict:
        """查询广东考生成绩"""

        # 1. 获取Session
        session = aiohttp.ClientSession()

        # 2. 获取验证码
        captcha = await self._get_captcha(session)

        # 3. 识别验证码（OCR或人工）
        captcha_code = await self._recognize_captcha(captcha)

        # 4. 提交查询请求
        response = await session.post(
            f"{self.BASE_URL}/query",
            data={
                "exam_id": exam_id,
                "id_card": id_card,
                "name": name,
                "captcha": captcha_code
            }
        )

        # 5. 解析响应
        html = await response.text()
        score_data = self._parse_score_html(html)

        await session.close()
        return score_data

    async def _get_captcha(self, session) -> bytes:
        """获取验证码图片"""
        response = await session.get(
            f"{self.BASE_URL}/captcha"
        )
        return await response.read()

    async def _recognize_captcha(self, image: bytes) -> str:
        """识别验证码"""
        # 方案1: OCR识别
        # return await ocr_service.recognize(image)

        # 方案2: 人工识别
        # 显示验证码给用户，用户输入

        # 方案3: 第三方验证码识别服务
        return await captcha_service.solve(image)

    def _parse_score_html(self, html: str) -> dict:
        """解析成绩HTML"""
        soup = BeautifulSoup(html, 'html.parser')

        return {
            "exam_id": soup.find(id="exam_id").text,
            "name": soup.find(id="name").text,
            "总分": int(soup.find(id="total_score").text),
            "语文": int(soup.find(id="chinese").text),
            "数学": int(soup.find(id="math").text),
            "英语": int(soup.find(id="english").text),
            "综合": int(soup.find(id="comprehensive").text),
            "全省排名": int(soup.find(id="rank").text)
        }
```

## 🛡️ 安全和隐私保护

### 1. 数据加密
```python
# 传输加密
- HTTPS协议
- API密钥认证
- 请求签名验证

# 存储加密
- 身份证号AES加密
- 准考证号脱敏显示
- 查询记录加密存储
```

### 2. 访问控制
```python
# 频率限制
@router.post("/score/query")
@rate_limit(max_requests=5, window=60)  # 每分钟最多5次
async def query_score(request: ScoreQueryRequest):
    pass

# IP限制
@router.post("/score/query")
@ip_whitelist(allowed_ips=["*"])  # 可配置白名单
async def query_score(request: ScoreQueryRequest):
    pass
```

### 3. 日志审计
```python
# 记录所有查询
async def log_query(exam_id: str, ip: str, result: str):
    await QueryLog.create(
        exam_id=mask_exam_id(exam_id),  # 脱敏
        ip=ip,
        result=result,
        timestamp=datetime.now()
    )
```

## 🎯 实现方案对比

### 方案1: 官方API对接（推荐）
```
优点：
- 数据准确权威
- 稳定可靠
- 合法合规

缺点：
- 需要官方授权
- 接入复杂
- 可能有费用

实施：
1. 联系各省教育考试院
2. 申请API接入权限
3. 签署合作协议
4. 技术对接
```

### 方案2: 爬虫方案（不推荐）
```
优点：
- 无需授权
- 快速实现

缺点：
- 不稳定（网站改版就失效）
- 法律风险
- 验证码识别困难
- 容易被封IP

风险：
- 违反《计算机信息网络国际联网安全保护管理办法》
- 可能触犯《刑法》第285条（非法获取计算机信息系统数据罪）
```

### 方案3: 第三方服务（折中）
```
优点：
- 专业团队维护
- 稳定性较好
- 降低开发成本

缺点：
- 有服务费用
- 数据依赖第三方

提供商：
- 阿里云教育API
- 腾讯云教育服务
- 专业教育数据公司
```

## 📱 用户界面设计

### 查分页面
```
┌─────────────────────────────────┐
│      高考成绩查询              │
├─────────────────────────────────┤
│                                 │
│  准考证号                       │
│  [______________]               │
│                                 │
│  身份证号                       │
│  [______________________]       │
│                                 │
│  考生姓名                       │
│  [______________]               │
│                                 │
│  验证码                         │
│  [____] [图片]                  │
│                                 │
│  [查询成绩]                     │
│                                 │
└─────────────────────────────────┘
```

### 成绩展示页面
```
┌─────────────────────────────────┐
│      查询结果                  │
├─────────────────────────────────┤
│  姓名：张三                     │
│  准考证号：1425********01       │
│                                 │
│  ┌───────────────────────────┐  │
│  │      总分：620分          │  │
│  └───────────────────────────┘  │
│                                 │
│  语文：125分                    │
│  数学：138分                    │
│  英语：130分                    │
│  综合：195分                    │
│                                 │
│  全省排名：8500位               │
│                                 │
│  [保存成绩] [志愿推荐]         │
└─────────────────────────────────┘
```

## ⚠️ 重要提示

### 法律合规
1. **必须获得官方授权**才能提供查分服务
2. **不得使用爬虫**未经授权访问教育考试院网站
3. **用户隐私保护**符合《个人信息保护法》要求
4. **数据安全**符合《网络安全法》规定

### 技术风险
1. **并发压力**：查分期间流量巨大
2. **系统稳定性**：确保99.9%可用性
3. **数据准确性**：必须与官方数据一致
4. **响应速度**：查询时间<3秒

### 业务建议
1. **与官方合作**：申请成为官方指定查询渠道
2. **增值服务**：查分后提供志愿推荐
3. **数据服务**：历史分数线、位次查询
4. **用户服务**：查分咨询、志愿指导

---

## 🚀 总结

**查分功能实现**：
- ✅ 技术上完全可行
- ⚠️ 需要官方授权
- 📋 有完整的实现方案
- 🛡️ 必须遵守法律法规

**建议**：
1. 优先与教育考试院官方合作
2. 使用官方API或成为授权查询点
3. 提供增值服务（志愿推荐）
4. 确保数据安全和用户隐私

**当前项目状态**：
- ❌ 尚未实现查分功能
- ✅ 有分数转位次功能
- ✅ 有志愿推荐功能
- ✅ 可以集成查分功能
