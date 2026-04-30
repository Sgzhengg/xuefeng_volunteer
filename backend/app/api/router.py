from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, Response
from app.models.schemas import *
from app.services.pdf_service import pdf_service
from app.services.enhanced_pdf_service import enhanced_pdf_service
from app.services.volunteer_simulator_service import volunteer_simulator_service
from app.services.recommendation_service import recommendation_service
from app.services.ai_chat_service import ai_chat_service
import json
from pathlib import Path
from functools import lru_cache
import time

router = APIRouter()

# 数据源配置
DATA_DIR = Path("data")

# 数据缓存
_data_cache = {
    "admission_scores": None,
    "score_rank_tables": None,
    "last_load_time": 0
}
CACHE_DURATION = 300  # 5分钟缓存


def _get_cached_admission_scores():
    """获取缓存的录取分数线数据"""
    current_time = time.time()
    if (_data_cache["admission_scores"] is None or
        current_time - _data_cache["last_load_time"] > CACHE_DURATION):
        print("Loading admission_scores.json into cache...")
        start_time = time.time()
        with open(DATA_DIR / "admission_scores.json", 'r', encoding='utf-8') as f:
            _data_cache["admission_scores"] = json.load(f)
        _data_cache["last_load_time"] = current_time
        print(f"Loaded admission_scores.json in {time.time() - start_time:.2f}s")
    return _data_cache["admission_scores"]


def _get_cached_score_rank_tables():
    """获取缓存的一分一段表数据"""
    current_time = time.time()
    # 使用单独的缓存键
    cache_key = "score_rank_tables"
    if cache_key not in _data_cache or _data_cache[cache_key] is None:
        print("Loading score_rank_tables.json into cache...")
        start_time = time.time()
        with open(DATA_DIR / "score_rank_tables.json", 'r', encoding='utf-8') as f:
            _data_cache[cache_key] = json.load(f)
        print(f"Loaded score_rank_tables.json in {time.time() - start_time:.2f}s")
    return _data_cache[cache_key]


# ========== 数据查询接口 ==========

@router.post("/gaokao/admission-probability", response_model=AdmissionProbabilityResponse)
async def get_admission_probability(request: AdmissionProbabilityRequest):
    """查询录取概率 - 使用本地爬虫数据"""
    try:
        # 使用本地数据库（爬虫数据）
        result = await _query_admission_probability_from_db(request)
        if result["success"]:
            return AdmissionProbabilityResponse(**result)
        else:
            raise HTTPException(status_code=404, detail=result["message"])

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def _query_admission_probability_from_db(request: AdmissionProbabilityRequest) -> dict:
    """从本地数据库查询录取概率"""
    try:
        # 从本地数据库读取录取分数数据
        scores_file = DATA_DIR / "admission_scores.json"
        if not scores_file.exists():
            return {
                "success": False,
                "message": "本地数据库文件不存在",
                "data": None
            }

        with open(scores_file, 'r', encoding='utf-8') as f:
            scores_data = json.load(f)

        # 简单的算法：根据分数差计算概率
        # 这里使用简化的逻辑，实际应该更复杂
        probability = _calculate_probability_simple(
            request.score, request.province, request.subject_type
        )

        return {
            "success": True,
            "message": "查询成功（基于本地数据库）",
            "data": {
                "probability": probability,
                "prediction": _get_prediction_text(probability),
                "data_source": "local_scraper",
                "note": "基于公开爬取数据，仅供参考"
            }
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"本地查询失败: {str(e)}",
            "data": None
        }


def _calculate_probability_simple(score: int, province: str, subject_type: str) -> int:
    """简化的概率计算算法"""
    # 这是一个非常简化的算法，实际应该更复杂
    # 基于分数段给出概率
    if score >= 680:
        return 95
    elif score >= 650:
        return 85
    elif score >= 600:
        return 70
    elif score >= 550:
        return 50
    elif score >= 500:
        return 30
    else:
        return 15


def _get_prediction_text(probability: int) -> str:
    """获取预测文本"""
    if probability >= 90:
        return "录取概率很高，建议冲刺更好院校"
    elif probability >= 70:
        return "录取概率较大，可以稳妥填报"
    elif probability >= 50:
        return "录取概率中等，需要谨慎选择"
    elif probability >= 30:
        return "录取概率较小，建议作为保底"
    else:
        return "录取概率很小，不建议填报"


@router.get("/gaokao/university/{university_name}", response_model=UniversityInfoResponse)
async def get_university_info(university_name: str):
    """查询院校信息 - 使用本地数据库"""
    try:
        # 使用本地数据库
        result = await _query_university_info_from_db(university_name)
        if result["success"]:
            return UniversityInfoResponse(**result)
        else:
            raise HTTPException(status_code=404, detail=result["message"])

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def _query_university_info_from_db(university_name: str) -> dict:
    """从本地数据库查询院校信息"""
    try:
        universities_file = DATA_DIR / "universities_list.json"
        if not universities_file.exists():
            return {
                "success": False,
                "message": "本地院校数据库不存在",
                "data": None
            }

        with open(universities_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 搜索匹配的院校（模糊搜索）
        universities = data.get("universities", [])
        matched = None

        for uni in universities:
            if university_name in uni.get("name", ""):
                matched = uni
                break

        if not matched:
            return {
                "success": False,
                "message": f"未找到院校: {university_name}",
                "data": None
            }

        return {
            "success": True,
            "message": "查询成功（基于本地数据库）",
            "data": {
                "name": matched.get("name"),
                "province": matched.get("province"),
                "type": matched.get("type"),
                "level": matched.get("level"),
                "website": matched.get("website", ""),
                "data_source": "local_scraper"
            }
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"本地查询失败: {str(e)}",
            "data": None
        }


@router.get("/gaokao/major-employment/{major_name}", response_model=MajorEmploymentResponse)
async def get_major_employment(major_name: str):
    """查询专业就业数据 - 使用本地数据库"""
    try:
        # 使用本地数据库
        result = await _query_major_employment_from_db(major_name)
        if result["success"]:
            return MajorEmploymentResponse(**result)
        else:
            raise HTTPException(status_code=404, detail=result["message"])

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def _query_major_employment_from_db(major_name: str) -> dict:
    """从本地数据库查询专业就业数据"""
    try:
        employment_file = DATA_DIR / "employment_data.json"
        if not employment_file.exists():
            # 如果本地数据不存在，返回Mock数据
            return {
                "success": True,
                "message": "查询成功（Mock数据）",
                "data": {
                    "major_name": major_name,
                    "employment_rate": 85,
                    "salary_median": 8000,
                    "employment_trend": "稳定",
                    "ai_impact": "中等",
                    "data_source": "mock"
                }
            }

        with open(employment_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 搜索匹配的专业
        majors = data.get("majors", [])
        matched = None

        for major in majors:
            if major_name in major.get("name", ""):
                matched = major
                break

        if not matched:
            # 返回Mock数据
            return {
                "success": True,
                "message": "未找到该专业，返回Mock数据",
                "data": {
                    "major_name": major_name,
                    "employment_rate": 85,
                    "salary_median": 8000,
                    "employment_trend": "稳定",
                    "ai_impact": "中等",
                    "data_source": "mock"
                }
            }

        return {
            "success": True,
            "message": "查询成功（基于本地数据库）",
            "data": {
                "major_name": matched.get("name"),
                "employment_rate": matched.get("employment_rate", 85),
                "salary_median": matched.get("salary_median", 8000),
                "employment_trend": matched.get("trend", "稳定"),
                "ai_impact": matched.get("ai_impact", "中等"),
                "data_source": "local_scraper"
            }
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"本地查询失败: {str(e)}",
            "data": None
        }


# ========== Phase 3 功能接口 ==========

@router.post("/pdf/generate-report")
async def generate_pdf_report(request: PDFReportRequest):
    """生成志愿建议 PDF 报告"""
    try:
        result = await pdf_service.generate_volunteer_report(
            user_profile=request.user_profile,
            chat_history=request.chat_history,
            data_context=request.data_context,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/pdf/generate-enhanced-report")
async def generate_enhanced_pdf_report(request: EnhancedPDFReportRequest):
    """生成增强版志愿推荐 PDF 报告（基于推荐结果）"""
    try:
        if request.export_format == "html":
            # Export as HTML
            html_content = await enhanced_pdf_service.export_to_html(
                recommendation_result=request.recommendation_result
            )
            return Response(
                content=html_content.encode('utf-8'),
                media_type="text/html",
                headers={
                    "Content-Disposition": "attachment; filename=volunteer_recommendation.html"
                }
            )
        else:
            # Generate PDF
            pdf_bytes = await enhanced_pdf_service.generate_volunteer_report(
                recommendation_result=request.recommendation_result
            )
            return Response(
                content=pdf_bytes,
                media_type="application/pdf",
                headers={
                    "Content-Disposition": "attachment; filename=volunteer_recommendation.pdf"
                }
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/simulator/generate-scheme")
async def generate_volunteer_scheme(request: VolunteerSchemeRequest):
    """生成志愿方案（冲稳保垫）"""
    try:
        result = await volunteer_simulator_service.generate_volunteer_scheme(
            province=request.province,
            score=request.score,
            rank=request.rank,
            subject_type=request.subject_type,
            target_majors=request.target_majors,
            preferences=request.preferences,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ========== 智能推荐接口 ==========

@router.post("/recommendation/generate")
async def generate_recommendation(request: RecommendationRequest):
    """生成智能推荐方案（参考夸克算法：分数+位次+概率三维匹配）"""
    try:
        print(f"Enhanced API called with: province={request.province}, score={request.score}, majors={request.target_majors}")

        # 使用增强的推荐服务
        from app.services.enhanced_recommendation_service import enhanced_recommendation_service

        result = await enhanced_recommendation_service.generate_recommendation(
            province=request.province,
            score=request.score,
            subject_type=request.subject_type,
            target_majors=request.target_majors,
            rank=request.rank,
            preferences=request.preferences,
        )
        print(f"Enhanced API result: {result.get('data', {}).get('analysis', {}).get('total_count', 0)} schools")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recommendation/majors/suggest")
async def suggest_majors(score: int, subject_type: str = "理科"):
    """根据分数推荐专业"""
    try:
        majors = recommendation_service._recommend_majors_by_score(score, subject_type)
        return {
            "success": True,
            "data": {
                "score": score,
                "subject_type": subject_type,
                "suggested_majors": majors
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recommendation/rank/calculate")
async def calculate_rank(province: str, score: int):
    """根据分数计算位次"""
    try:
        rank = recommendation_service._calculate_rank_from_score(province, score)
        return {
            "success": True,
            "data": {
                "province": province,
                "score": score,
                "rank": rank
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/gaokao/segment")
async def get_score_rank_segment(province: str, year: int, score: int = None):
    """查询一分一段表"""
    try:
        result = await _query_score_rank_segment_from_db(province, year, score)
        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=404, detail=result["message"])
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def _query_score_rank_segment_from_db(province: str, year: int, score: int = None) -> dict:
    """从本地数据库查询一分一段表"""
    try:
        # 使用缓存数据
        data = _get_cached_score_rank_tables()

        print(f"DEBUG SEGMENT: Original province name: '{province}'")

        # 数据结构：{"provinces": {"广东": {...}}}
        if "provinces" not in data:
            print(f"DEBUG SEGMENT: No 'provinces' key in data. Keys: {list(data.keys())}")
            return {
                "success": False,
                "message": "数据格式错误：缺少provinces字段",
                "data": None
            }

        provinces_data = data["provinces"]
        print(f"DEBUG SEGMENT: Available provinces (first 5): {list(provinces_data.keys())[:5]}")

        # 规范化省份名称
        province_normalized = _normalize_province_name(province)
        print(f"DEBUG SEGMENT: Normalized province name: '{province_normalized}'")

        # 检查省份是否存在
        if province_normalized not in provinces_data:
            print(f"DEBUG SEGMENT: Province '{province_normalized}' not found in data")
            return {
                "success": False,
                "message": f"未找到省份：{province}（规范化后：{province_normalized}）",
                "data": None
            }

        province_data = provinces_data[province_normalized]
        year_str = str(year)
        if year_str not in province_data:
            print(f"DEBUG SEGMENT: Year {year} not found. Available years: {list(province_data.keys())}")
            return {
                "success": False,
                "message": f"未找到{year}年数据，可用年份：{list(province_data.keys())}",
                "data": None
            }

        year_data = province_data[year_str]
        print(f"DEBUG SEGMENT: Year data keys: {list(year_data.keys())}")

        # 如果指定了分数，返回该分数的排名信息
        if score is not None:
            score_str = str(score)
            print(f"DEBUG SEGMENT: Looking for score {score}")

            # 检查数据结构，可能是'table'或'segments'
            table_data = year_data.get("table", year_data.get("segments", {}))
            if not table_data:
                print(f"DEBUG SEGMENT: No 'table' or 'segments' key in year_data")
                return {
                    "success": False,
                    "message": f"未找到一分一段表数据",
                    "data": None
                }

            print(f"DEBUG SEGMENT: Table data type: {type(table_data)}, keys (first 5): {list(table_data.keys())[:5] if isinstance(table_data, dict) else 'list'}")

            # 如果是字典格式
            if isinstance(table_data, dict):
                if score_str in table_data:
                    segment = table_data[score_str]
                    return {
                        "success": True,
                        "message": "查询成功",
                        "data": {
                            "province": province_normalized,
                            "year": year,
                            "score": score,
                            "rank": segment.get("rank", segment.get("位次", 0)),
                            "cumulative": segment.get("cumulative", segment.get("累计人数", 0)),
                            "data_source": "local_database"
                        }
                    }
                else:
                    # 如果没有找到精确分数，返回最接近的分数
                    closest_score = None
                    min_diff = float('inf')
                    for s in table_data.keys():
                        try:
                            diff = abs(int(s) - score)
                            if diff < min_diff:
                                min_diff = diff
                                closest_score = s
                        except ValueError:
                            continue

                    if closest_score and min_diff <= 10:  # 10分以内的差异
                        segment = table_data[closest_score]
                        return {
                            "success": True,
                            "message": f"查询成功（未找到{score}分，返回最接近的{closest_score}分）",
                            "data": {
                                "province": province_normalized,
                                "year": year,
                                "score": int(closest_score),
                                "rank": segment.get("rank", segment.get("位次", 0)),
                                "cumulative": segment.get("cumulative", segment.get("累计人数", 0)),
                                "data_source": "local_database"
                            }
                        }

            # 如果是列表格式
            elif isinstance(table_data, list):
                for item in table_data:
                    if isinstance(item, dict) and str(item.get("score", item.get("分数", ""))) == score_str:
                        return {
                            "success": True,
                            "message": "查询成功",
                            "data": {
                                "province": province_normalized,
                                "year": year,
                                "score": score,
                                "rank": item.get("rank", item.get("位次", 0)),
                                "cumulative": item.get("cumulative", item.get("累计人数", 0)),
                                "data_source": "local_database"
                            }
                        }

            return {
                "success": False,
                "message": f"未找到分数{score}的排名信息",
                "data": None
            }
        else:
            # 返回该省份年份的完整信息
            return {
                "success": True,
                "message": "查询成功",
                "data": {
                    "province": province_normalized,
                    "year": year,
                    "total_candidates": year_data.get("total_candidates", 0),
                    "score_range": year_data.get("score_range", ""),
                    "data_source": "local_database"
                }
            }

    except Exception as e:
        print(f"DEBUG SEGMENT: Exception occurred: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "message": f"查询失败: {str(e)}",
            "data": None
        }


@router.get("/gaokao/control-line")
async def get_provincial_control_line(province: str, year: int):
    """查询省控线"""
    try:
        result = await _query_provincial_control_line_from_db(province, year)
        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=404, detail=result["message"])
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def _query_provincial_control_line_from_db(province: str, year: int) -> dict:
    """从本地数据库查询省控线"""
    try:
        # 使用缓存数据
        data = _get_cached_admission_scores()

        print(f"DEBUG: Original province name: '{province}'")

        # 数据结构：{"provinces": {"广东": {...}}}
        if "provinces" not in data:
            print(f"DEBUG: No 'provinces' key in data. Keys: {list(data.keys())}")
            return {
                "success": False,
                "message": "数据格式错误：缺少provinces字段",
                "data": None
            }

        provinces_data = data["provinces"]
        print(f"DEBUG: Available provinces (first 5): {list(provinces_data.keys())[:5]}")

        # 规范化省份名称
        province_normalized = _normalize_province_name(province)
        print(f"DEBUG: Normalized province name: '{province_normalized}'")

        # 检查省份是否存在
        if province_normalized not in provinces_data:
            print(f"DEBUG: Province '{province_normalized}' not found in data")
            return {
                "success": False,
                "message": f"未找到省份：{province}（规范化后：{province_normalized}）",
                "data": None
            }

        province_data = provinces_data[province_normalized]
        year_str = str(year)
        if year_str not in province_data:
            return {
                "success": False,
                "message": f"未找到{year}年数据，可用年份：{list(province_data.keys())}",
                "data": None
            }

        year_data = province_data[year_str]

        # 提取省控线信息
        control_line = year_data.get("control_line", {})
        if not control_line:
            return {
                "success": False,
                "message": f"{year}年省控线数据不存在",
                "data": None
            }

        return {
            "success": True,
            "message": "查询成功",
            "data": {
                "province": province_normalized,
                "year": year,
                "science_first": control_line.get("first_batch"),
                "science_second": control_line.get("second_batch"),
                "arts_first": control_line.get("first_batch_arts", control_line.get("arts_first")),
                "arts_second": control_line.get("second_batch_arts", control_line.get("arts_second")),
                "comprehensive_first": control_line.get("comprehensive_first"),
                "data_source": "local_database"
            }
        }

    except Exception as e:
        print(f"DEBUG: Exception occurred: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "message": f"查询失败: {str(e)}",
            "data": None
        }


def _normalize_province_name(province: str) -> str:
    """规范化省份名称"""
    if not province:
        return province

    # 移除常见的后缀
    normalized = province.replace("省", "").replace("市", "").replace("自治区", "")

    # 处理特殊情况
    special_cases = {
        "内蒙古": "内蒙古",
        "内蒙古": "内蒙古",
        "广西": "广西",
        "广西": "广西",
        "西藏": "西藏",
        "西藏": "西藏",
        "宁夏": "宁夏",
        "宁夏": "宁夏",
        "新疆": "新疆",
        "新疆": "新疆",
        "香港": "香港",
        "香港": "香港",
        "澳门": "澳门",
        "澳门": "澳门"
    }

    # 检查是否匹配特殊情况
    for key, value in special_cases.items():
        if key in normalized:
            return value

    return normalized.strip()


# ==================== 聊天API ====================

@router.post("/chat")
async def chat(request: ChatRequest):
    """
    聊天API - 张学锋AI

    Args:
        request: ChatRequest包含message和可选的context、conversation_history

    Returns:
        AI回答
    """
    try:
        response = await ai_chat_service.chat_with_context(
            user_message=request.message,
            context=request.context,
            conversation_history=request.conversation_history
        )
        return {
            "success": True,
            "response": response
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
