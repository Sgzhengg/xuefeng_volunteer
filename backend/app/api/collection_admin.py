"""
数据采集管理API
提供采集任务管理、进度跟踪、版本控制等功能
"""
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime
import asyncio

from app.services.collection_service import (
    get_collection_service,
    CollectionService,
    TaskStatus,
    TaskType
)
from app.api.admin import verify_admin
from app.services.auto_switch_service import get_auto_switch_service, scheduled_auto_switch_check

router = APIRouter()


# ==================== 数据模型 ====================

class CreateTaskRequest(BaseModel):
    """创建任务请求"""
    task_name: str
    task_type: str  # 'universities', 'admission_data', 'majors', 'validation'
    year: int
    province: Optional[str] = None


class UpdateVersionRequest(BaseModel):
    """更新版本请求"""
    status: Optional[str] = None
    data_completeness: Optional[int] = None
    university_count: Optional[int] = None
    major_count: Optional[int] = None
    province_coverage: Optional[Dict] = None
    metadata: Optional[Dict] = None


class SwitchVersionRequest(BaseModel):
    """切换版本请求"""
    to_year: int
    switch_type: str = "manual"  # 'manual', 'auto', 'rollback'
    reason: Optional[str] = None


# ==================== 采集任务管理 ====================

@router.get("/admin/collection/tasks")
async def list_collection_tasks(
    status: Optional[str] = None,
    task_type: Optional[str] = None,
    year: Optional[int] = None,
    limit: int = 50,
    offset: int = 0,
    is_admin: bool = Depends(verify_admin)
):
    """
    获取采集任务列表

    Args:
        status: 任务状态筛选
        task_type: 任务类型筛选
        year: 年份筛选
        limit: 返回数量
        offset: 偏移量

    Returns:
        任务列表
    """
    service = get_collection_service()
    tasks = service.list_tasks(status=status, task_type=task_type, year=year, limit=limit, offset=offset)

    return {
        "code": 0,
        "data": {
            "tasks": tasks,
            "total": len(tasks)
        }
    }


@router.get("/admin/collection/tasks/{task_id}")
async def get_task_detail(
    task_id: int,
    is_admin: bool = Depends(verify_admin)
):
    """
    获取任务详情

    Args:
        task_id: 任务ID

    Returns:
        任务详情
    """
    service = get_collection_service()
    task = service.get_task(task_id)

    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    # 获取任务日志
    logs = service.get_logs(task_id, limit=50)

    return {
        "code": 0,
        "data": {
            "task": task,
            "logs": logs
        }
    }


@router.post("/admin/collection/tasks")
async def create_collection_task(
    request: CreateTaskRequest,
    background_tasks: BackgroundTasks,
    is_admin: bool = Depends(verify_admin)
):
    """
    创建采集任务

    Args:
        request: 任务创建请求

    Returns:
        创建的任务ID
    """
    service = get_collection_service()

    # 创建任务
    task_id = service.create_task(
        task_name=request.task_name,
        task_type=request.task_type,
        year=request.year,
        province=request.province,
        created_by="admin"
    )

    # 添加后台任务执行采集
    background_tasks.add_task(
        execute_collection_task,
        task_id,
        request.task_type,
        request.year,
        request.province
    )

    return {
        "code": 0,
        "message": "任务创建成功",
        "data": {
            "task_id": task_id
        }
    }


@router.post("/admin/collection/tasks/{task_id}/cancel")
async def cancel_task(
    task_id: int,
    is_admin: bool = Depends(verify_admin)
):
    """
    取消采集任务

    Args:
        task_id: 任务ID

    Returns:
        取消结果
    """
    service = get_collection_service()
    task = service.get_task(task_id)

    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    if task["status"] not in ["pending", "running"]:
        return {
            "code": 1,
            "message": f"任务状态为 {task['status']}，无法取消"
        }

    service.update_task_status(task_id, TaskStatus.CANCELLED)
    service.add_log(task_id, "INFO", "任务已被管理员取消")

    return {
        "code": 0,
        "message": "任务已取消"
    }


@router.delete("/admin/collection/tasks/{task_id}")
async def delete_task(
    task_id: int,
    is_admin: bool = Depends(verify_admin)
):
    """
    删除采集任务

    Args:
        task_id: 任务ID

    Returns:
        删除结果
    """
    service = get_collection_service()
    task = service.get_task(task_id)

    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    if task["status"] == "running":
        return {
            "code": 1,
            "message": "无法删除运行中的任务"
        }

    # 删除任务（通过数据库操作）
    import sqlite3
    from pathlib import Path

    db_file = Path("database/collection.db")
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # 删除日志
    cursor.execute("DELETE FROM collection_logs WHERE task_id = ?", (task_id,))
    # 删除任务
    cursor.execute("DELETE FROM collection_tasks WHERE id = ?", (task_id,))

    conn.commit()
    conn.close()

    return {
        "code": 0,
        "message": "任务已删除"
    }


@router.get("/admin/collection/tasks/{task_id}/logs")
async def get_task_logs(
    task_id: int,
    limit: int = 100,
    is_admin: bool = Depends(verify_admin)
):
    """
    获取任务日志

    Args:
        task_id: 任务ID
        limit: 返回数量

    Returns:
        日志列表
    """
    service = get_collection_service()
    logs = service.get_logs(task_id, limit=limit)

    return {
        "code": 0,
        "data": {
            "logs": logs,
            "total": len(logs)
        }
    }


@router.get("/admin/collection/stats")
async def get_collection_stats(
    is_admin: bool = Depends(verify_admin)
):
    """
    获取采集统计信息

    Returns:
        统计数据
    """
    service = get_collection_service()
    stats = service.get_stats()

    return {
        "code": 0,
        "data": stats
    }


# ==================== 版本控制 ====================

@router.get("/admin/collection/versions")
async def list_versions(
    is_admin: bool = Depends(verify_admin)
):
    """
    获取所有数据版本

    Returns:
        版本列表
    """
    service = get_collection_service()
    versions = service.list_versions()

    return {
        "code": 0,
        "data": {
            "versions": versions
        }
    }


@router.get("/admin/collection/versions/{year}")
async def get_version_detail(
    year: int,
    is_admin: bool = Depends(verify_admin)
):
    """
    获取指定年份的版本详情

    Args:
        year: 年份

    Returns:
        版本详情
    """
    service = get_collection_service()
    version = service.get_version(year)

    if not version:
        raise HTTPException(status_code=404, detail="版本不存在")

    # 解析元数据
    import json
    if version.get("metadata"):
        try:
            version["metadata"] = json.loads(version["metadata"])
        except:
            version["metadata"] = {}

    if version.get("province_coverage"):
        try:
            version["province_coverage"] = json.loads(version["province_coverage"])
        except:
            version["province_coverage"] = {}

    return {
        "code": 0,
        "data": version
    }


@router.put("/admin/collection/versions/{year}")
async def update_version(
    year: int,
    request: UpdateVersionRequest,
    is_admin: bool = Depends(verify_admin)
):
    """
    更新版本信息

    Args:
        year: 年份
        request: 更新请求

    Returns:
        更新结果
    """
    service = get_collection_service()

    service.update_version(
        year=year,
        status=request.status,
        data_completeness=request.data_completeness,
        university_count=request.university_count,
        major_count=request.major_count,
        province_coverage=request.province_coverage,
        metadata=request.metadata
    )

    return {
        "code": 0,
        "message": "版本信息已更新"
    }


@router.post("/admin/collection/versions/switch")
async def switch_version(
    request: SwitchVersionRequest,
    is_admin: bool = Depends(verify_admin)
):
    """
    切换数据版本

    Args:
        request: 切换请求

    Returns:
        切换结果
    """
    service = get_collection_service()

    result = service.switch_version(
        to_year=request.to_year,
        switch_type=request.switch_type,
        switched_by="admin",
        reason=request.reason
    )

    if result["success"]:
        return {
            "code": 0,
            "message": result["message"],
            "data": {
                "from_year": result.get("from_year"),
                "to_year": result["to_year"]
            }
        }
    else:
        return {
            "code": 1,
            "message": result["message"]
        }


@router.get("/admin/collection/versions/active")
async def get_active_version(
    is_admin: bool = Depends(verify_admin)
):
    """
    获取当前活跃的版本

    Returns:
        活跃版本信息
    """
    service = get_collection_service()
    version = service.get_active_version()

    if not version:
        return {
            "code": 1,
            "message": "没有活跃的版本"
        }

    # 解析元数据
    import json
    if version.get("metadata"):
        try:
            version["metadata"] = json.loads(version["metadata"])
        except:
            version["metadata"] = {}

    return {
        "code": 0,
        "data": version
    }


@router.get("/admin/collection/versions/history")
async def get_switch_history(
    limit: int = 20,
    is_admin: bool = Depends(verify_admin)
):
    """
    获取版本切换历史

    Args:
        limit: 返回数量

    Returns:
        切换历史列表
    """
    service = get_collection_service()
    history = service.get_switch_history(limit=limit)

    return {
        "code": 0,
        "data": {
            "history": history,
            "total": len(history)
        }
    }


@router.get("/admin/collection/versions/compare")
async def compare_versions(
    year1: int = 2025,
    year2: int = 2026,
    is_admin: bool = Depends(verify_admin)
):
    """
    对比两个版本的数据

    Args:
        year1: 第一年份
        year2: 第二年份

    Returns:
        版本对比数据
    """
    service = get_collection_service()

    version1 = service.get_version(year1)
    version2 = service.get_version(year2)

    if not version1 or not version2:
        return {
            "code": 1,
            "message": "版本不存在"
        }

    return {
        "code": 0,
        "data": {
            "year1": version1,
            "year2": version2,
            "comparison": {
                "university_diff": version2.get("university_count", 0) - version1.get("university_count", 0),
                "major_diff": version2.get("major_count", 0) - version1.get("major_count", 0),
                "completeness_diff": version2.get("data_completeness", 0) - version1.get("data_completeness", 0)
            }
        }
    }


# ==================== 后台任务执行 ====================

async def execute_collection_task(
    task_id: int,
    task_type: str,
    year: int,
    province: Optional[str] = None
):
    """
    执行采集任务（后台）

    Args:
        task_id: 任务ID
        task_type: 任务类型
        year: 年份
        province: 省份
    """
    service = get_collection_service()

    try:
        # 更新任务状态为运行中
        service.update_task_status(task_id, TaskStatus.RUNNING, progress=0)
        service.add_log(task_id, "INFO", f"开始执行 {task_type} 采集任务")

        # 根据任务类型执行不同的采集逻辑
        if task_type == "universities":
            await _collect_universities(task_id, year, service)
        elif task_type == "admission_data":
            await _collect_admission_data(task_id, year, province, service)
        elif task_type == "majors":
            await _collect_majors(task_id, year, service)
        elif task_type == "validation":
            await _validate_data(task_id, year, service)
        else:
            raise ValueError(f"不支持的任务类型: {task_type}")

        # 任务完成
        service.update_task_status(
            task_id,
            TaskStatus.SUCCESS,
            progress=100,
            result_summary={"message": "采集完成"}
        )
        service.add_log(task_id, "INFO", "任务执行成功")

    except Exception as e:
        # 任务失败
        service.update_task_status(
            task_id,
            TaskStatus.FAILED,
            error_message=str(e)
        )
        service.add_log(task_id, "ERROR", f"任务执行失败: {str(e)}")


async def _collect_universities(task_id: int, year: int, service: CollectionService):
    """采集院校数据"""
    service.add_log(task_id, "INFO", f"开始采集 {year} 年院校数据")

    # 模拟采集过程
    total_items = 100  # 假设有100所院校

    for i in range(total_items):
        await asyncio.sleep(0.1)  # 模拟网络请求

        # 更新进度
        service.update_task_progress(task_id, i + 1, total_items)

        if (i + 1) % 20 == 0:
            service.add_log(task_id, "INFO", f"已采集 {i + 1}/{total_items} 所院校")

    service.add_log(task_id, "INFO", f"院校数据采集完成，共 {total_items} 所")


async def _collect_admission_data(
    task_id: int,
    year: int,
    province: Optional[str],
    service: CollectionService
):
    """采集录取数据"""
    province_str = province or "全国"
    service.add_log(task_id, "INFO", f"开始采集 {year} 年 {province_str} 录取数据")

    # 模拟采集过程
    total_items = 1000  # 假设有1000条数据

    for i in range(total_items):
        await asyncio.sleep(0.05)  # 模拟网络请求

        # 更新进度
        service.update_task_progress(task_id, i + 1, total_items)

        if (i + 1) % 200 == 0:
            service.add_log(task_id, "INFO", f"已采集 {i + 1}/{total_items} 条数据")

    service.add_log(task_id, "INFO", f"录取数据采集完成，共 {total_items} 条")


async def _collect_majors(task_id: int, year: int, service: CollectionService):
    """采集专业数据"""
    service.add_log(task_id, "INFO", f"开始采集 {year} 年专业数据")

    # 模拟采集过程
    total_items = 500

    for i in range(total_items):
        await asyncio.sleep(0.08)

        service.update_task_progress(task_id, i + 1, total_items)

        if (i + 1) % 100 == 0:
            service.add_log(task_id, "INFO", f"已采集 {i + 1}/{total_items} 个专业")

    service.add_log(task_id, "INFO", f"专业数据采集完成，共 {total_items} 个")


async def _validate_data(task_id: int, year: int, service: CollectionService):
    """验证数据"""
    service.add_log(task_id, "INFO", f"开始验证 {year} 年数据")

    # 模拟验证过程
    total_items = 200

    for i in range(total_items):
        await asyncio.sleep(0.05)

        service.update_task_progress(task_id, i + 1, total_items)

    service.add_log(task_id, "INFO", f"数据验证完成")


# ==================== 自动切换控制 ====================

@router.get("/admin/collection/auto-switch/status")
async def get_auto_switch_status(
    is_admin: bool = Depends(verify_admin)
):
    """
    获取自动切换状态

    Returns:
        自动切换状态信息
    """
    auto_switch_service = get_auto_switch_service()
    status = auto_switch_service.get_switch_status()

    return {
        "code": 0,
        "data": status
    }


@router.post("/admin/collection/auto-switch/enable")
async def enable_auto_switch(
    required_completeness: int = 100,
    is_admin: bool = Depends(verify_admin)
):
    """
    启用自动版本切换

    Args:
        required_completeness: 要求的数据完整度百分比

    Returns:
        启用结果
    """
    auto_switch_service = get_auto_switch_service()
    auto_switch_service.enable_auto_switch(required_completeness)

    return {
        "code": 0,
        "message": f"自动版本切换已启用，要求完整度: {required_completeness}%"
    }


@router.post("/admin/collection/auto-switch/disable")
async def disable_auto_switch(
    is_admin: bool = Depends(verify_admin)
):
    """
    禁用自动版本切换

    Returns:
        禁用结果
    """
    auto_switch_service = get_auto_switch_service()
    auto_switch_service.disable_auto_switch()

    return {
        "code": 0,
        "message": "自动版本切换已禁用"
    }


@router.post("/admin/collection/auto-switch/check-now")
async def check_and_switch_now(
    is_admin: bool = Depends(verify_admin)
):
    """
    立即执行自动切换检查

    Returns:
        检查和切换结果
    """
    auto_switch_service = get_auto_switch_service()
    result = auto_switch_service.check_and_switch()

    if result.get("action") == "skipped":
        return {
            "code": 0,
            "message": f"跳过自动切换: {result.get('reason')}",
            "data": result
        }
    elif result.get("success"):
        return {
            "code": 0,
            "message": "自动版本切换成功",
            "data": result
        }
    else:
        return {
            "code": 1,
            "message": result.get("message", "自动切换失败"),
            "data": result
        }
