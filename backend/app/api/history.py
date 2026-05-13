"""
历史推荐记录API
处理用户推荐历史的保存、查询等功能
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from jose import jwt, JWTError
from datetime import datetime
import uuid

router = APIRouter()

# JWT密钥（与auth.py保持一致）
SECRET_KEY = "xuefeng-volunteer-secret-key-2024"
ALGORITHM = "HS256"

# 内存存储用户历史数据 (MVP阶段)
# 格式：{user_id: [history_item_dict, ...]}
user_history: Dict[str, List[Dict[str, Any]]] = {}


# ==================== 数据模型 ====================

class HistorySaveRequest(BaseModel):
    """保存历史推荐请求"""
    rank: int
    province: str
    subjects: List[str]
    preference: str
    results: List[Dict[str, Any]]  # 推荐结果摘要


class HistoryItem(BaseModel):
    """历史记录项"""
    id: str  # 唯一标识
    user_id: str
    rank: int
    province: str
    subjects: List[str]
    preference: str
    results_summary: List[Dict[str, Any]]  # 推荐结果摘要
    results_count: int  # 推荐结果总数
    created_at: str


class HistoryDetail(BaseModel):
    """历史推荐详情"""
    id: str
    user_id: str
    rank: int
    province: str
    subjects: List[str]
    preference: str
    results: List[Dict[str, Any]]  # 完整推荐结果
    results_count: int
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

@router.post("/history/save")
async def save_history(
    request: HistorySaveRequest,
    authorization: str = Query(...)
):
    """
    保存本次推荐结果

    Args:
        request: 推荐请求数据
        authorization: Bearer token

    Returns:
        保存结果
    """
    try:
        # 验证token并获取用户ID
        user_id = verify_token(authorization)

        # 创建历史记录
        history_id = str(uuid.uuid4())
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 只保存推荐结果的摘要信息
        results_summary = []
        for result in request.results[:20]:  # 只保存前20条作为摘要
            results_summary.append({
                "university_name": result.get("university_name", ""),
                "major_name": result.get("major_name", ""),
                "type": result.get("type", ""),
                "probability": result.get("probability", 0)
            })

        history_item = {
            "id": history_id,
            "user_id": user_id,
            "rank": request.rank,
            "province": request.province,
            "subjects": request.subjects,
            "preference": request.preference,
            "results_summary": results_summary,
            "results": request.results,  # 保存完整结果用于详情查看
            "results_count": len(request.results),
            "created_at": created_at
        }

        # 初始化用户历史列表
        if user_id not in user_history:
            user_history[user_id] = []

        # 添加到历史列表（插入到最前面）
        user_history[user_id].insert(0, history_item)

        # 限制历史记录数量（最多保存50条）
        if len(user_history[user_id]) > 50:
            user_history[user_id] = user_history[user_id][:50]

        return {
            "code": 0,
            "message": "保存成功",
            "data": {
                "history_id": history_id,
                "created_at": created_at
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"保存历史失败: {str(e)}")


@router.get("/history/list")
async def get_history_list(
    page: int = Query(1, ge=1, description="页码"),
    limit: int = Query(10, ge=1, le=50, description="每页数量"),
    authorization: str = Query(...)
):
    """
    获取历史推荐列表（分页）

    Args:
        page: 页码
        limit: 每页数量
        authorization: Bearer token

    Returns:
        历史记录列表
    """
    try:
        # 验证token并获取用户ID
        user_id = verify_token(authorization)

        # 获取用户历史数据
        histories = user_history.get(user_id, [])

        # 分页处理
        total = len(histories)
        start = (page - 1) * limit
        end = start + limit
        page_histories = histories[start:end]

        # 格式化返回数据（只包含摘要信息）
        formatted_histories = []
        for item in page_histories:
            formatted_histories.append({
                "id": item["id"],
                "rank": item["rank"],
                "province": item["province"],
                "subjects": item["subjects"],
                "preference": item["preference"],
                "results_summary": item["results_summary"],
                "results_count": item["results_count"],
                "created_at": item["created_at"]
            })

        total_pages = (total + limit - 1) // limit if total > 0 else 1

        return {
            "code": 0,
            "data": {
                "histories": formatted_histories,
                "pagination": {
                    "total": total,
                    "page": page,
                    "limit": limit,
                    "total_pages": total_pages
                }
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取历史列表失败: {str(e)}")


@router.get("/history/detail/{history_id}")
async def get_history_detail(
    history_id: str,
    authorization: str = Query(...)
):
    """
    获取某次历史推荐的完整结果

    Args:
        history_id: 历史记录ID
        authorization: Bearer token

    Returns:
        历史推荐详情
    """
    try:
        # 验证token并获取用户ID
        user_id = verify_token(authorization)

        # 查找历史记录
        histories = user_history.get(user_id, [])
        history_item = None

        for item in histories:
            if item["id"] == history_id:
                history_item = item
                break

        if history_item is None:
            raise HTTPException(status_code=404, detail="历史记录不存在")

        # 返回完整的历史详情
        return {
            "code": 0,
            "data": {
                "id": history_item["id"],
                "rank": history_item["rank"],
                "province": history_item["province"],
                "subjects": history_item["subjects"],
                "preference": history_item["preference"],
                "results": history_item["results"],  # 返回完整结果
                "results_count": history_item["results_count"],
                "created_at": history_item["created_at"]
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取历史详情失败: {str(e)}")


@router.delete("/history/delete/{history_id}")
async def delete_history(
    history_id: str,
    authorization: str = Query(...)
):
    """
    删除某条历史记录

    Args:
        history_id: 历史记录ID
        authorization: Bearer token

    Returns:
        删除结果
    """
    try:
        # 验证token并获取用户ID
        user_id = verify_token(authorization)

        # 检查用户历史数据
        if user_id not in user_history:
            return {
                "code": 1,
                "message": "历史记录不存在"
            }

        # 查找并删除历史记录
        original_length = len(user_history[user_id])
        user_history[user_id] = [
            item for item in user_history[user_id]
            if item["id"] != history_id
        ]

        if len(user_history[user_id]) < original_length:
            return {
                "code": 0,
                "message": "删除成功"
            }
        else:
            return {
                "code": 1,
                "message": "历史记录不存在"
            }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除历史记录失败: {str(e)}")


# ==================== 辅助接口 ====================

@router.get("/history/stats")
async def get_history_stats(
    authorization: str = Query(...)
):
    """
    获取历史统计信息

    Args:
        authorization: Bearer token

    Returns:
        统计信息
    """
    try:
        # 验证token并获取用户ID
        user_id = verify_token(authorization)

        # 获取用户历史数据
        histories = user_history.get(user_id, [])

        # 统计信息
        total_recommendations = sum(item["results_count"] for item in histories)

        # 最常用的偏好设置
        preference_count = {}
        for item in histories:
            pref = item["preference"]
            preference_count[pref] = preference_count.get(pref, 0) + 1

        most_common_preference = max(preference_count.keys()) if preference_count else "balanced"

        return {
            "code": 0,
            "data": {
                "total_histories": len(histories),
                "total_recommendations": total_recommendations,
                "most_common_preference": most_common_preference,
                "latest_rank": histories[0]["rank"] if histories else None,
                "latest_province": histories[0]["province"] if histories else None
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取统计信息失败: {str(e)}")