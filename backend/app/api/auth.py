"""
认证模块
处理用户登录、注册、验证码等功能
"""
from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta
from jose import JWTError, jwt
import random

router = APIRouter()

# JWT密钥（生产环境应使用环境变量）
SECRET_KEY = "xuefeng-volunteer-secret-key-2024"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 7

# 内存存储
sessions = {}  # {phone: {"user_id": phone, "phone": phone}}
verification_codes = {}  # {phone: {"code": "123456", "expire_time": datetime}}


# 请求模型
class SendCodeRequest(BaseModel):
    phone: str


class LoginRequest(BaseModel):
    phone: str
    code: str


# 响应模型
class SendCodeResponse(BaseModel):
    code: int
    message: str


class LoginResponse(BaseModel):
    code: int
    message: str
    data: Optional[dict] = None


class UserInfoResponse(BaseModel):
    code: int
    message: str
    data: Optional[dict] = None


class TokenData(BaseModel):
    phone: str


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """生成JWT token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=7)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[str]:
    """验证JWT token，返回用户手机号"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        phone: str = payload.get("sub")
        if phone is None:
            return None
        return phone
    except JWTError:
        return None


def get_current_user(authorization: str = Header(...)) -> dict:
    """获取当前用户（依赖注入）"""
    # 提取Bearer token
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="无效的认证格式")

    token = authorization.split(" ")[1]
    phone = verify_token(token)

    if phone is None:
        raise HTTPException(status_code=401, detail="token无效或已过期")

    # 获取用户信息
    if phone not in sessions:
        raise HTTPException(status_code=401, detail="用户不存在")

    user = sessions[phone]
    return user


@router.post("/auth/send_code", response_model=SendCodeResponse)
async def send_code(request: SendCodeRequest):
    """
    发送验证码（MVP阶段不实际发送）

    Args:
        request: 包含phone的请求体

    Returns:
        验证码发送结果
    """
    phone = request.phone

    # 验证手机号格式
    if not phone or len(phone) != 11 or not phone.startswith("1"):
        return SendCodeResponse(
            code=1,
            message="手机号格式不正确"
        )

    # MVP阶段：固定验证码123456
    verification_codes[phone] = {
        "code": "123456",
        "expire_time": datetime.now() + timedelta(minutes=5)
    }

    return SendCodeResponse(
        code=0,
        message="验证码已发送（测试：123456）"
    )


@router.post("/auth/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """
    用户登录

    Args:
        request: 包含phone和code的请求体

    Returns:
        登录结果，包含token和用户信息
    """
    phone = request.phone
    code = request.code

    # 验证手机号格式
    if not phone or len(phone) != 11 or not phone.startswith("1"):
        return LoginResponse(
            code=1,
            message="手机号格式不正确"
        )

    # 验证验证码
    if phone not in verification_codes:
        return LoginResponse(
            code=1,
            message="请先获取验证码"
        )

    stored_code = verification_codes[phone]
    if datetime.now() > stored_code["expire_time"]:
        del verification_codes[phone]
        return LoginResponse(
            code=1,
            message="验证码已过期，请重新获取"
        )

    if code != stored_code["code"]:
        return LoginResponse(
            code=1,
            message="验证码错误"
        )

    # 验证码使用后删除
    del verification_codes[phone]

    # 创建或获取用户会话
    if phone not in sessions:
        sessions[phone] = {
            "user_id": phone,
            "phone": phone,
            "created_at": datetime.now().isoformat()
        }

    user = sessions[phone]

    # 生成JWT token
    access_token = create_access_token(
        data={"sub": phone},
        expires_delta=timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    )

    return LoginResponse(
        code=0,
        message="登录成功",
        data={
            "token": access_token,
            "user": {
                "phone": user["phone"],
                "user_id": user["user_id"]
            }
        }
    )


@router.get("/auth/me", response_model=UserInfoResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """
    获取当前用户信息

    Args:
        current_user: 当前登录用户（通过token获取）

    Returns:
        用户信息
    """
    return UserInfoResponse(
        code=0,
        message="获取成功",
        data={
            "user_id": current_user["user_id"],
            "phone": current_user["phone"],
            "created_at": current_user.get("created_at", "")
        }
    )
