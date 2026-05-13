"""
收藏功能API
处理用户收藏院校和专业的功能
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from jose import jwt, JWTError
from datetime import datetime

router = APIRouter()

# JWT密钥（与auth.py保持一致）
SECRET_KEY = "xuefeng-volunteer-secret-key-2024"
ALGORITHM = "HS256"

# 内存存储用户收藏数据 (MVP阶段)
# 格式：{user_id: [favorite_item_dict, ...]}
user_favorites: Dict[str, List[Dict[str, Any]]] = {}


# ==================== 数据模型 ====================

class FavoriteAddRequest(BaseModel):
    """添加收藏请求"""
    university_id: Optional[int] = None
    major_id: Optional[int] = None
    university_name: str
    major_name: str


class FavoriteItem(BaseModel):
    """收藏项"""
    id: str  # 格式：{university_id}_{major_id}
    university_id: Optional[int] = None
    major_id: Optional[int] = None
    university_name: str
    major_name: str
    created_at: str


# ==================== 依赖注入 ====================

def get_current_user(token: str) -> str:
    """
    从token中获取用户ID
    MVP阶段：从token中解析phone_number作为user_id
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("phone_number")  # MVP阶段使用phone_number作为user_id
        if user_id is None:
            raise HTTPException(status_code=401, detail="无效的token")
        return user_id
    except JWTError:
        raise HTTPException(status_code=401, detail="token验证失败")


def verify_token(authorization: str = Query(...)) -> str:
    """
    验证Bearer token
    """
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="无效的认证格式")

    token = authorization[7:]  # 移除 "Bearer " 前缀
    return get_current_user(token)


# ==================== API接口 ====================

@router.post("/favorite/add")
async def add_favorite(
    request: FavoriteAddRequest,
    authorization: str = Query(...)
):
    """
    添加收藏

    Args:
        request: 收藏请求数据
        authorization: Bearer token

    Returns:
        添加结果
    """
    try:
        # 验证token并获取用户ID
        user_id = verify_token(authorization)

        # 创建收藏项
        favorite_id = f"{request.university_id or 0}_{request.major_id or 0}"
        favorite_item = {
            "id": favorite_id,
            "university_id": request.university_id,
            "major_id": request.major_id,
            "university_name": request.university_name,
            "major_name": request.major_name,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        # 初始化用户收藏列表
        if user_id not in user_favorites:
            user_favorites[user_id] = []

        # 检查是否已收藏
        for item in user_favorites[user_id]:
            if item["id"] == favorite_id:
                return {
                    "code": 0,
                    "message": "已经收藏过了"
                }

        # 添加到收藏列表
        user_favorites[user_id].append(favorite_item)

        return {
            "code": 0,
            "message": "收藏成功",
            "data": favorite_item
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"添加收藏失败: {str(e)}")


@router.delete("/favorite/remove")
async def remove_favorite(
    major_id: int = Query(..., description="专业ID"),
    authorization: str = Query(...)
):
    """
    取消收藏

    Args:
        major_id: 专业ID (或者使用 {university_id}_{major_id} 格式的ID)
        authorization: Bearer token

    Returns:
        删除结果
    """
    try:
        # 验证token并获取用户ID
        user_id = verify_token(authorization)

        # 检查用户是否有收藏数据
        if user_id not in user_favorites:
            return {
                "code": 1,
                "message": "没有收藏数据"
            }

        # 查找并删除匹配的收藏项
        original_length = len(user_favorites[user_id])
        user_favorites[user_id] = [
            item for item in user_favorites[user_id]
            if item["major_id"] != major_id
        ]

        if len(user_favorites[user_id]) < original_length:
            return {
                "code": 0,
                "message": "取消收藏成功"
            }
        else:
            return {
                "code": 1,
                "message": "未找到对应的收藏项"
            }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"取消收藏失败: {str(e)}")


@router.get("/favorite/list")
async def get_favorite_list(
    authorization: str = Query(...)
):
    """
    获取用户收藏列表

    Args:
        authorization: Bearer token

    Returns:
        收藏列表
    """
    try:
        # 验证token并获取用户ID
        user_id = verify_token(authorization)

        # 获取用户收藏数据
        favorites = user_favorites.get(user_id, [])

        # 按创建时间倒序排列
        favorites = sorted(favorites, key=lambda x: x["created_at"], reverse=True)

        return {
            "code": 0,
            "data": {
                "favorites": favorites,
                "total": len(favorites)
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取收藏列表失败: {str(e)}")


@router.get("/favorite/check")
async def check_favorite(
    major_id: int = Query(..., description="专业ID"),
    authorization: str = Query(...)
):
    """
    检查是否已收藏

    Args:
        major_id: 专业ID
        authorization: Bearer token

    Returns:
        收藏状态
    """
    try:
        # 验证token并获取用户ID
        user_id = verify_token(authorization)

        # 检查用户收藏数据
        favorites = user_favorites.get(user_id, [])

        # 查找匹配的收藏项
        is_favorited = any(
            item["major_id"] == major_id
            for item in favorites
        )

        return {
            "code": 0,
            "data": {
                "is_favorited": is_favorited
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"检查收藏状态失败: {str(e)}")


# ==================== 辅助接口 ====================

@router.get("/favorite/stats")
async def get_favorite_stats(
    authorization: str = Query(...)
):
    """
    获取收藏统计信息

    Args:
        authorization: Bearer token

    Returns:
        统计信息
    """
    try:
        # 验证token并获取用户ID
        user_id = verify_token(authorization)

        # 获取用户收藏数据
        favorites = user_favorites.get(user_id, [])

        # 统计院校数量（去重）
        universities = set()
        for item in favorites:
            if item.get("university_name"):
                universities.add(item["university_name"])

        return {
            "code": 0,
            "data": {
                "total_favorites": len(favorites),
                "total_universities": len(universities),
                "total_majors": len(favorites)
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取统计信息失败: {str(e)}")