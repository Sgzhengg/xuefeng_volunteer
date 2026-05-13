"""
志愿表模块
处理用户志愿的增删改查和评估功能
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.api.auth import get_current_user

router = APIRouter()

# 内存存储
user_plans = {}  # {user_id: [plan_item_dict, ...]}


# 请求模型
class PlanItem(BaseModel):
    university_id: str
    major_id: str
    university_name: str
    major_name: str
    probability: int
    roi_score: int
    tag: str  # 冲/稳/保


class AddPlanRequest(BaseModel):
    university_id: str
    major_id: str
    university_name: str
    major_name: str
    probability: int
    roi_score: int
    tag: str


# 响应模型
class PlanListResponse(BaseModel):
    code: int
    message: str
    data: Optional[dict] = None


class AddPlanResponse(BaseModel):
    code: int
    message: str


class RemovePlanResponse(BaseModel):
    code: int
    message: str


class EvaluatePlanResponse(BaseModel):
    code: int
    message: str
    data: Optional[dict] = None


@router.get("/plan/list", response_model=PlanListResponse)
async def get_plan_list(current_user: dict = Depends(get_current_user)):
    """
    获取用户的志愿列表

    Args:
        current_user: 当前登录用户

    Returns:
        用户的志愿列表
    """
    user_id = current_user["user_id"]

    if user_id not in user_plans:
        user_plans[user_id] = []

    plans = user_plans[user_id]

    # 为每个志愿添加ID（用于删除）
    for i, plan in enumerate(plans):
        if "id" not in plan:
            plan["id"] = f"{plan['university_name']}_{plan['major_name']}"

    return PlanListResponse(
        code=0,
        message="获取成功",
        data={
            "plans": plans,
            "total": len(plans)
        }
    )


@router.post("/plan/add", response_model=AddPlanResponse)
async def add_plan(
    request: AddPlanRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    添加志愿到用户的志愿表

    Args:
        request: 志愿项信息
        current_user: 当前登录用户

    Returns:
        添加结果
    """
    user_id = current_user["user_id"]

    if user_id not in user_plans:
        user_plans[user_id] = []

    # 检查是否已存在（通过university_name和major_name判断）
    plans = user_plans[user_id]
    for existing_plan in plans:
        if (existing_plan["university_name"] == request.university_name and
            existing_plan["major_name"] == request.major_name):
            return AddPlanResponse(
                code=1,
                message="该院校专业已在志愿表中"
            )

    # 添加新志愿
    new_plan = {
        "id": f"{request.university_name}_{request.major_name}",
        "university_id": request.university_id,
        "major_id": request.major_id,
        "university_name": request.university_name,
        "major_name": request.major_name,
        "probability": request.probability,
        "roi_score": request.roi_score,
        "tag": request.tag,
        "created_at": datetime.now().isoformat()
    }

    plans.append(new_plan)

    return AddPlanResponse(
        code=0,
        message="添加成功"
    )


@router.delete("/plan/remove", response_model=RemovePlanResponse)
async def remove_plan(
    major_id: str = Query(..., description="专业ID（用于标识志愿项）"),
    current_user: dict = Depends(get_current_user)
):
    """
    从用户的志愿表中删除志愿

    Args:
        major_id: 专业ID
        current_user: 当前登录用户

    Returns:
        删除结果
    """
    user_id = current_user["user_id"]

    if user_id not in user_plans:
        return RemovePlanResponse(
            code=1,
            message="志愿表为空"
        )

    plans = user_plans[user_id]

    # 查找并删除对应的志愿
    original_length = len(plans)
    user_plans[user_id] = [plan for plan in plans if plan["id"] != major_id]

    if len(user_plans[user_id]) == original_length:
        return RemovePlanResponse(
            code=1,
            message="未找到该志愿项"
        )

    return RemovePlanResponse(
        code=0,
        message="删除成功"
    )


@router.get("/plan/evaluate", response_model=EvaluatePlanResponse)
async def evaluate_plan(current_user: dict = Depends(get_current_user)):
    """
    评估用户的志愿表

    统计冲刺/稳妥/保底数量，计算评分，生成警告和建议

    Args:
        current_user: 当前登录用户

    Returns:
        评估结果，包含评分、统计、警告和建议
    """
    user_id = current_user["user_id"]

    if user_id not in user_plans:
        user_plans[user_id] = []

    plans = user_plans[user_id]

    # 统计各类别数量
    chong_count = 0
    wen_count = 0
    bao_count = 0

    for plan in plans:
        tag = plan.get("tag", "")
        if tag == "冲" or tag == "冲刺":
            chong_count += 1
        elif tag == "稳" or tag == "稳妥":
            wen_count += 1
        elif tag == "保" or tag == "保底":
            bao_count += 1

    # 计算总分
    total_count = len(plans)
    if total_count == 0:
        overall_score = 0
        risk_level = "low"
    else:
        # 基础分100分，根据规则扣分
        score = 100

        # 规则1: 冲刺 > 6 则警告
        if chong_count > 6:
            score -= 20

        # 规则2: 保底 < 3 则警告
        if bao_count < 3:
            score -= 20

        # 规则3: 稳妥+保底 < 10 则警告
        if (wen_count + bao_count) < 10:
            score -= 15

        # 规则4: 总数 < 8 则警告
        if total_count < 8:
            score -= 10

        overall_score = max(0, score)

        # 确定风险等级
        if overall_score >= 80:
            risk_level = "low"
        elif overall_score >= 60:
            risk_level = "medium"
        else:
            risk_level = "high"

    # 生成警告
    warnings = []

    if chong_count > 6:
        warnings.append({
            "type": "too_many_chong",
            "category": "结构风险",
            "message": f"冲刺院校过多（{chong_count}所），建议控制在6所以内",
            "severity": "high" if chong_count > 8 else "medium"
        })

    if bao_count < 3:
        warnings.append({
            "type": "too_few_bao",
            "category": "保底不足",
            "message": f"保底院校过少（{bao_count}所），建议至少3所",
            "severity": "high"
        })

    if (wen_count + bao_count) < 10:
        warnings.append({
            "type": "insufficient_safe",
            "category": "安全系数低",
            "message": f"稳妥+保底院校不足（{wen_count + bao_count}所），建议至少10所",
            "severity": "high" if (wen_count + bao_count) < 8 else "medium"
        })

    if total_count < 8:
        warnings.append({
            "type": "insufficient_total",
            "category": "数量不足",
            "message": f"志愿总数过少（{total_count}所），建议至少8所",
            "severity": "medium"
        })

    # 生成建议
    suggestions = []

    if chong_count > 6:
        suggestions.append({
            "content": f"减少{chong_count - 6}所冲刺院校，增加稳妥或保底院校"
        })

    if bao_count < 3:
        suggestions.append({
            "content": f"增加{3 - bao_count}所保底院校以提高录取安全性"
        })

    if (wen_count + bao_count) < 10:
        suggestions.append({
            "content": f"增加{10 - (wen_count + bao_count)}所稳妥或保底院校"
        })

    if total_count < 8:
        suggestions.append({
            "content": "建议填报8-12所志愿以提高录取概率"
        })

    if not warnings:
        suggestions.append({
            "content": "志愿表结构合理，继续保持！"
        })

    return EvaluatePlanResponse(
        code=0,
        message="评估成功",
        data={
            "overall_score": overall_score,
            "risk_level": risk_level,
            "chong_count": chong_count,
            "wen_count": wen_count,
            "bao_count": bao_count,
            "warnings": warnings,
            "suggestions": suggestions,
            "evaluated_at": datetime.now().isoformat()
        }
    )
