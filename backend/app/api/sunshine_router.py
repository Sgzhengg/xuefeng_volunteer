"""
后端 API 路由更新
集成阳光高考爬虫服务
"""

from fastapi import APIRouter, HTTPException
from app.models.sunshine_models import *
from app.services.sunshine_scraper import sunshine_scraper
from app.services.volunteer_simulator_service import volunteer_simulator_service

router = APIRouter()

# ========== 数据源配置 ==========

# 可以通过环境变量配置使用哪个数据源
# SUNSHINE_SCRAPER = True  # 使用阳光高考爬虫
# GUGUDATA_API = True      # 使用咕咕数据 API

USE_SUNSHINE_SCRAPER = True  # 当前使用爬虫

# ========== 阳光高考爬虫接口 ==========

@router.get("/sunshine/universities")
async def get_university_list(
    province: str = None,
    use_cache: bool = True
):
    """
    获取院校列表（阳光高考数据）

    Args:
        province: 省份筛选（可选）
        use_cache: 是否使用缓存

    Returns:
        院校列表
    """
    if not USE_SUNSHINE_SCRAPER:
        raise HTTPException(
            status_code=503,
            detail="阳光高考爬虫未启用"
        )

    try:
        async with sunshine_scraper as scraper:
            result = await scraper.scrape_university_list(
                province=province,
                use_cache=use_cache
            )
            return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sunshine/university/{university_id}")
async def get_university_detail(
    university_id: str,
    use_cache: bool = True
):
    """
    获取院校详细信息（阳光高考数据）

    Args:
        university_id: 院校 ID
        use_cache: 是否使用缓存

    Returns:
        院校详细信息
    """
    if not USE_SUNSHINE_SCRAPER:
        raise HTTPException(
            status_code=503,
            detail="阳光高考爬虫未启用"
        )

    try:
        async with sunshine_scraper as scraper:
            result = await scraper.scrape_university_detail(
                university_id=university_id,
                use_cache=use_cache
            )
            return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sunshine/admission-scores/{province}")
async def get_admission_scores(
    province: str,
    year: int = 2025,
    use_cache: bool = True
):
    """
    获取录取分数线（阳光高考数据）

    Args:
        province: 省份
        year: 年份
        use_cache: 是否使用缓存

    Returns:
        录取分数线列表
    """
    if not USE_SUNSHINE_SCRAPER:
        raise HTTPException(
            status_code=503,
            detail="阳光高考爬虫未启用"
        )

    try:
        async with sunshine_scraper as scraper:
            result = await scraper.scrape_admission_scores(
                province=province,
                year=year,
                use_cache=use_cache
            )
            return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sunshine/majors")
async def get_major_list(use_cache: bool = True):
    """
    获取专业列表（阳光高考数据）

    Args:
        use_cache: 是否使用缓存

    Returns:
        专业列表
    """
    if not USE_SUNSHINE_SCRAPER:
        raise HTTPException(
            status_code=503,
            detail="阳光高考爬虫未启用"
        )

    try:
        async with sunshine_scraper as scraper:
            result = await scraper.scrape_major_list(use_cache=use_cache)
            return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sunshine/batch-scrape")
async def batch_scrape_universities(
    limit: int = 100,
    delay: float = 2.0
):
    """
    批量爬取院校数据

    Args:
        limit: 爬取数量限制
        delay: 请求间隔（秒）

    Returns:
        批量爬取结果
    """
    if not USE_SUNSHINE_SCRAPER:
        raise HTTPException(
            status_code=503,
            detail="阳光高考爬虫未启用"
        )

    try:
        async with sunshine_scraper as scraper:
            result = await scraper.batch_scrape_universities(
                limit=limit,
                delay=delay
            )
            return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ========== 测试端点 ==========

@router.get("/test/db-read")
async def test_database_read():
    """测试数据库文件读取"""
    try:
        from pathlib import Path
        import json

        db_file = Path("data/admission_scores.json")
        if not db_file.exists():
            return {"error": "Database file not found", "path": str(db_file)}

        with open(db_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        return {
            "success": True,
            "file_exists": True,
            "provinces": list(data.get("provinces", {}).keys()),
            "zhejiang_years": list(data.get("provinces", {}).get("浙江", {}).keys())
        }
    except Exception as e:
        return {"error": str(e)}


# ========== 数据源状态接口 ==========

@router.get("/data-source/status")
async def get_data_source_status():
    """
    获取当前数据源状态

    Returns:
        数据源状态信息
    """
    return {
        "success": True,
        "data": {
            "primary_source": "sunshine_scraper" if USE_SUNSHINE_SCRAPER else "gugudata",
            "sunshine_scraper": {
                "enabled": USE_SUNSHINE_SCRAPER,
                "name": "阳光高考爬虫",
                "description": "从 gaokao.chsi.com.cn 爬取数据",
                "update_frequency": "手动触发",
                "last_update": "2026-04-22"  # 从缓存文件读取
            }
        }
    }


# ========== 保留原有的咕咕数据接口 ==========
# 注：咕咕数据 API 已弃用，现在使用本地数据库

# @router.post("/gaokao/admission-probability")
# async def get_admission_probability(request: dict):
#     """查询录取概率（咕咕数据 API）"""
#     try:
#         result = await gugudata_service.query_admission_probability(
#             province=request.get("province"),
#             score=request.get("score"),
#             rank=request.get("rank"),
#             subject_type=request.get("subject_type"),
#             university_name=request.get("university_name"),
#             major_name=request.get("major_name"),
#         )
#         return result
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


# ========== Phase 3 功能接口（保持不变）==========

@router.post("/pdf/generate-report")
async def generate_pdf_report(request: dict):
    """生成志愿建议 PDF 报告"""
    try:
        from app.services.pdf_service import pdf_service
        result = await pdf_service.generate_volunteer_report(
            user_profile=request.get("user_profile"),
            chat_history=request.get("chat_history"),
            data_context=request.get("data_context"),
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/simulator/generate-scheme")
async def generate_volunteer_scheme(request: dict):
    """生成志愿方案（冲稳保垫）"""
    try:
        result = await volunteer_simulator_service.generate_volunteer_scheme(
            province=request.get("province"),
            score=request.get("score"),
            rank=request.get("rank"),
            subject_type=request.get("subject_type"),
            target_majors=request.get("target_majors"),
            preferences=request.get("preferences"),
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ========== 健康检查接口 ==========

@router.get("/health")
async def health_check_sunshine():
    """
    健康检查（包含爬虫状态）
    """
    return {
        "status": "healthy",
        "services": {
            "api": "ok",
            "sunshine_scraper": "enabled" if USE_SUNSHINE_SCRAPER else "disabled",
            "gugudata": "disabled" if USE_SUNSHINE_SCRAPER else "optional"
        },
        "data_source": "sunshine_scraper" if USE_SUNSHINE_SCRAPER else "gugudata"
    }
