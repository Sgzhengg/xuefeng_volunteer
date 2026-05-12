"""
管理后台 API
处理管理员登录、院校管理、数据导入等功能
"""
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
import json
import csv
import os
from pathlib import Path

router = APIRouter()

# JWT密钥（与auth.py保持一致）
SECRET_KEY = "xuefeng-volunteer-secret-key-2024"
ALGORITHM = "HS256"

# 数据目录
DATA_DIR = Path("data")
UNIVERSITIES_FILE = DATA_DIR / "universities_list.json"
ADMISSION_DATA_FILE = DATA_DIR / "major_rank_data.json"

# 硬编码的管理员账户
ADMIN_CREDENTIALS = {
    "username": "admin",
    "password": "password"
}

# 安全认证
security = HTTPBearer()


# ==================== 数据模型 ====================

class AdminLoginRequest(BaseModel):
    username: str
    password: str


class UniversityAddRequest(BaseModel):
    name: str
    province: str
    city: str
    type: str
    level: Optional[str] = "本科"
    website: Optional[str] = ""
    founded: Optional[str] = ""
    description: Optional[str] = ""


class UniversityUpdateRequest(BaseModel):
    name: Optional[str] = None
    province: Optional[str] = None
    city: Optional[str] = None
    type: Optional[str] = None
    level: Optional[str] = None
    website: Optional[str] = None
    founded: Optional[str] = None
    description: Optional[str] = None


# ==================== 依赖注入 ====================

def verify_admin(credentials: HTTPAuthorizationCredentials = Depends(security)) -> bool:
    """验证管理员token"""
    from jose import jwt, JWTError

    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username != "admin":
            raise HTTPException(status_code=401, detail="管理员权限不足")
        return True
    except JWTError:
        raise HTTPException(status_code=401, detail="Token无效或已过期")


def get_universities_data() -> dict:
    """读取院校数据"""
    try:
        with open(UNIVERSITIES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        return {"universities": []}


def save_universities_data(data: dict) -> bool:
    """保存院校数据"""
    try:
        with open(UNIVERSITIES_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"保存数据失败: {e}")
        return False


# ==================== 认证接口 ====================

@router.post("/admin/login")
async def admin_login(request: AdminLoginRequest):
    """
    管理员登录

    Args:
        request: 登录请求，包含username和password

    Returns:
        登录结果，包含token
    """
    # 验证用户名和密码
    if (request.username != ADMIN_CREDENTIALS["username"] or
        request.password != ADMIN_CREDENTIALS["password"]):
        return {
            "code": 1,
            "message": "用户名或密码错误"
        }

    # 生成JWT token
    from jose import jwt
    from datetime import timedelta

    token = jwt.encode(
        {
            "sub": "admin",
            "exp": datetime.utcnow() + timedelta(days=7)
        },
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return {
        "code": 0,
        "message": "登录成功",
        "data": {
            "token": token,
            "username": "admin"
        }
    }


# ==================== 统计接口 ====================

@router.get("/admin/stats")
async def get_admin_stats(is_admin: bool = Depends(verify_admin)):
    """
    获取系统统计数据

    Returns:
        系统统计信息
    """
    # 获取当前活跃的年份
    from app.services.collection_service import get_collection_service
    collection_service = get_collection_service()
    active_version = collection_service.get_active_version()
    current_year = active_version['year'] if active_version else 2025

    # 读取院校数据
    universities_data = get_universities_data()
    university_count = len(universities_data.get("universities", []))

    # 读取录取数据
    try:
        with open(ADMISSION_DATA_FILE, 'r', encoding='utf-8') as f:
            admission_data = json.load(f)
            # 统计院校+专业组合数量（更准确的反映专业覆盖）
            records = admission_data.get("major_rank_data", [])
            unique_combinations = set()
            for record in records:
                unique_combinations.add(f"{record['university_name']}_{record['major_name']}")
            major_count = len(unique_combinations)
    except:
        major_count = 0

    # 模拟用户数量（从sessions获取）
    from app.api.auth import sessions
    user_count = len(sessions)

    # 获取数据更新时间
    try:
        admission_mtime = os.path.getmtime(ADMISSION_DATA_FILE)
        updated_at = datetime.fromtimestamp(admission_mtime).strftime("%Y-%m-%d %H:%M:%S")
    except:
        updated_at = "未知"

    return {
        "code": 0,
        "data": {
            "user_count": user_count,
            "university_count": university_count,
            "major_count": major_count,
            "current_year": current_year,
            "updated_at": updated_at,
            "data_source_year": current_year,
            "data_source_label": f"{current_year}年数据"
        }
    }


# ==================== 院校管理接口 ====================

@router.get("/admin/universities")
async def get_universities(
    page: int = 1,
    limit: int = 20,
    keyword: str = "",
    is_admin: bool = Depends(verify_admin)
):
    """
    获取院校列表（分页+搜索）

    Args:
        page: 页码
        limit: 每页数量
        keyword: 搜索关键词

    Returns:
        院校列表和分页信息
    """
    data = get_universities_data()
    universities = data.get("universities", [])

    # 搜索过滤
    if keyword:
        universities = [
            uni for uni in universities
            if keyword.lower() in uni.get("name", "").lower() or
               keyword.lower() in uni.get("province", "").lower()
        ]

    # 分页
    total = len(universities)
    start = (page - 1) * limit
    end = start + limit
    paginated_list = universities[start:end]

    return {
        "code": 0,
        "data": {
            "list": paginated_list,
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": (total + limit - 1) // limit
        }
    }


@router.post("/admin/universities")
async def add_university(
    request: UniversityAddRequest,
    is_admin: bool = Depends(verify_admin)
):
    """
    添加院校

    Args:
        request: 院校信息

    Returns:
        添加结果
    """
    data = get_universities_data()
    universities = data.get("universities", [])

    # 生成新ID（最大ID+1）
    max_id = max([int(uni.get("id", 0)) for uni in universities] + [0])
    new_id = str(max_id + 1)

    # 创建新院校记录
    new_university = {
        "id": new_id,
        "name": request.name,
        "province": request.province,
        "city": request.city,
        "type": request.type,
        "level": request.level,
        "website": request.website,
        "founded": request.founded,
        "description": request.description
    }

    universities.append(new_university)
    data["universities"] = universities

    # 保存数据
    if save_universities_data(data):
        return {
            "code": 0,
            "message": "添加成功",
            "data": {"id": new_id}
        }
    else:
        return {
            "code": 1,
            "message": "保存失败"
        }


@router.put("/admin/universities/{university_id}")
async def update_university(
    university_id: str,
    request: UniversityUpdateRequest,
    is_admin: bool = Depends(verify_admin)
):
    """
    更新院校信息

    Args:
        university_id: 院校ID
        request: 更新的字段

    Returns:
        更新结果
    """
    data = get_universities_data()
    universities = data.get("universities", [])

    # 查找目标院校
    target_university = None
    for uni in universities:
        if uni.get("id") == university_id:
            target_university = uni
            break

    if not target_university:
        return {
            "code": 1,
            "message": "院校不存在"
        }

    # 更新字段
    update_data = request.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if value is not None:
            target_university[key] = value

    # 保存数据
    if save_universities_data(data):
        return {
            "code": 0,
            "message": "更新成功"
        }
    else:
        return {
            "code": 1,
            "message": "保存失败"
        }


@router.delete("/admin/universities/{university_id}")
async def delete_university(
    university_id: str,
    is_admin: bool = Depends(verify_admin)
):
    """
    删除院校

    Args:
        university_id: 院校ID

    Returns:
        删除结果
    """
    data = get_universities_data()
    universities = data.get("universities", [])

    # 查找并删除
    original_length = len(universities)
    universities = [uni for uni in universities if uni.get("id") != university_id]

    if len(universities) == original_length:
        return {
            "code": 1,
            "message": "院校不存在"
        }

    data["universities"] = universities

    # 保存数据
    if save_universities_data(data):
        return {
            "code": 0,
            "message": "删除成功"
        }
    else:
        return {
            "code": 1,
            "message": "保存失败"
        }


# ==================== 数据导入接口 ====================

@router.post("/admin/import/admission")
async def import_admission_data(
    file: UploadFile = File(...),
    is_admin: bool = Depends(verify_admin)
):
    """
    导入录取数据（CSV格式）- 完善版

    功能：
    - 自动检测CSV格式（分隔符、编码）
    - 验证必填列
    - 数据去重
    - 详细的导入结果报告

    Args:
        file: 上传的CSV文件

    Returns:
        导入结果（成功数量、失败数量、错误列表）
    """
    start_time = datetime.now()
    imported_count = 0
    failed_count = 0
    error_list = []

    try:
        # 1. 读取文件内容
        contents = await file.read()

        # 2. 自动检测编码
        import chardet
        detected = chardet.detect(contents)
        encoding = detected['encoding'] or 'utf-8'
        confidence = detected['confidence'] or 0

        # 如果编码检测置信度较低，尝试常见编码
        if confidence < 0.7:
            for fallback_encoding in ['utf-8', 'gbk', 'gb2312']:
                try:
                    test_decode = contents.decode(fallback_encoding)
                    encoding = fallback_encoding
                    break
                except:
                    continue
        else:
            csv_text = contents.decode(encoding)

        # 3. 自动检测分隔符
        import csv
        from io import StringIO

        # 尝试不同的分隔符
        delimiter = None
        csv_reader = None

        for test_delim in [',', '\t', ';', '|']:
            try:
                test_file = StringIO(csv_text)
                test_reader = csv.DictReader(test_file, delimiter=test_delim)
                test_row = next(test_reader)
                if len(test_row) > 1:  # 至少有2列
                    delimiter = test_delim
                    break
            except:
                continue

        if delimiter is None:
            delimiter = ','  # 默认逗号

        # 4. 解析CSV
        csv_file = StringIO(csv_text)
        csv_reader = csv.DictReader(csv_file, delimiter=delimiter)

        # 获取列名
        fieldnames = csv_reader.fieldnames

        # 5. 验证必填列（支持多种列名格式）
        required_columns = {
            'university_name': ['院校名称', '学校名称', '大学名称', '院校', 'university', 'school', 'college'],
            'major_name': ['专业名称', '专业', 'major'],
            'year': ['年份', '年', 'year'],
            'province': ['省份', '省', 'province'],
            'min_rank': ['最低位次', '位次', '最低排位', 'rank', '排位']
        }

        # 标准化列名映射
        column_mapping = {}
        for standard_name, possible_names in required_columns.items():
            for field_name in fieldnames:
                if field_name in possible_names:
                    column_mapping[standard_name] = field_name
                    break

            # 如果没找到匹配的列名，尝试直接匹配
            if standard_name not in column_mapping:
                for possible_name in possible_names:
                    if possible_name in fieldnames:
                        column_mapping[standard_name] = possible_name
                        break

        # 检查是否有足够的必填列
        missing_columns = [col for col in required_columns.keys() if col not in column_mapping]
        if len(missing_columns) > 3:  # 允许缺少部分列
            return {
                "code": 1,
                "message": f"CSV文件格式不正确，缺少必要的列: {', '.join(missing_columns)}",
                "data": {
                    "detected_columns": list(fieldnames),
                    "required_columns": list(required_columns.keys()),
                    "encoding": encoding,
                    "delimiter": delimiter,
                    "suggestions": "请确保CSV包含：院校名称、专业名称、年份、省份、最低位次等列"
                }
            }

        # 6. 读取现有数据用于去重
        try:
            with open(ADMISSION_DATA_FILE, 'r', encoding='utf-8') as f:
                admission_data = json.load(f)
                existing_data = admission_data.get("major_rank_data", [])
        except:
            existing_data = []

        # 构建已存在记录的集合（用于去重）
        existing_keys = set()
        for record in existing_data:
            key = f"{record.get('university_name', '')}_{record.get('major_name', '')}_{record.get('year', '')}_{record.get('province', '')}"
            existing_keys.add(key)

        # 7. 解析每一行数据
        new_records = []
        duplicate_count = 0

        for row_num, row in enumerate(csv_reader, start=2):  # 从第2行开始（第1行是表头）
            try:
                # 提取字段数据
                university_name = row.get(column_mapping.get('university_name', ''), '').strip()
                major_name = row.get(column_mapping.get('major_name', ''), '').strip()
                year_str = row.get(column_mapping.get('year', ''), '').strip()
                province = row.get(column_mapping.get('province', ''), '').strip()
                min_rank_str = row.get(column_mapping.get('min_rank', ''), '').strip()

                # 验证必填字段
                if not all([university_name, major_name, year_str, province, min_rank_str]):
                    error_list.append({
                        "row": row_num,
                        "data": dict(row),
                        "error": "缺少必填字段",
                        "missing_fields": [
                            field for field, value in [
                                ('院校名称', university_name),
                                ('专业名称', major_name),
                                ('年份', year_str),
                                ('省份', province),
                                ('最低位次', min_rank_str)
                            ] if not value
                        ]
                    })
                    failed_count += 1
                    continue

                # 数据类型转换
                try:
                    year = int(year_str)
                    min_rank = int(min_rank_str)
                except ValueError:
                    error_list.append({
                        "row": row_num,
                        "data": dict(row),
                        "error": "数据格式错误，年份和位次必须为数字"
                    })
                    failed_count += 1
                    continue

                # 提取可选字段
                min_score_str = row.get(column_mapping.get('min_score', '最低分', 'score', ''), '').strip()
                min_score = int(min_score_str) if min_score_str else None

                # 构建记录
                record = {
                    "university_major_id": f"{hash(university_name + major_name) % 1000}_{year}",
                    "university_id": str(hash(university_name) % 10000),
                    "university_name": university_name,
                    "major_name": major_name,
                    "major_code": "000000",  # 默认专业代码
                    "major_category": "未分类",  # 默认专业类别
                    "year": year,
                    "province": province,
                    "min_score": min_score,
                    "min_rank": min_rank,
                    "avg_score": min_score,  # 默认平均分等于最低分
                    "avg_rank": min_rank,   # 默认平均排位等于最低排位
                    "data_source": "admin_import"
                }

                # 去重检查
                record_key = f"{university_name}_{major_name}_{year}_{province}"
                if record_key in existing_keys:
                    duplicate_count += 1
                    continue

                # 添加到新记录列表
                new_records.append(record)
                existing_keys.add(record_key)
                imported_count += 1

            except Exception as e:
                error_list.append({
                    "row": row_num,
                    "data": dict(row),
                    "error": f"解析错误: {str(e)}"
                })
                failed_count += 1
                continue

        # 8. 保存导入的数据
        if imported_count > 0:
            # 合并现有数据和新数据
            updated_data = existing_data + new_records

            admission_data = {
                "metadata": {
                    "table_name": "major_rank_data",
                    "description": "全国院校专业录取位次数据（含高职专科）",
                    "version": "6.0.1",
                    "generated_at": datetime.now().isoformat(),
                    "total_records": len(updated_data),
                    "coverage": "nationwide_including_vocational",
                    "accuracy": "本科（精确）+ 高职（估算）",
                    "last_import": start_time.isoformat()
                },
                "major_rank_data": updated_data
            }

            with open(ADMISSION_DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(admission_data, f, ensure_ascii=False, indent=2)

        # 9. 计算导入耗时
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        # 10. 返回详细结果
        return {
            "code": 0,
            "message": f"导入完成！成功: {imported_count}条，重复: {duplicate_count}条，失败: {failed_count}条",
            "data": {
                "imported_count": imported_count,
                "duplicate_count": duplicate_count,
                "failed_count": failed_count,
                "total_count": len(existing_data) + imported_count,
                "duration_seconds": duration,
                "encoding": encoding,
                "delimiter": str(delimiter),
                "column_mapping": column_mapping,
                "error_samples": error_list[:10],  # 只返回前10个错误样本
                "preview_new_data": new_records[:3]   # 预览前3条导入的数据
            }
        }

    except UnicodeDecodeError:
        return {
            "code": 1,
            "message": "文件编码检测失败，请确保文件为UTF-8、GBK或GB2312编码"
        }
    except csv.Error as e:
        return {
            "code": 1,
            "message": f"CSV解析错误: {str(e)}，请检查文件格式"
        }
    except Exception as e:
        import traceback
        return {
            "code": 1,
            "message": f"导入失败: {str(e)}",
            "data": {
                "traceback": traceback.format_exc(),
                "error_type": type(e).__name__
            }
        }


@router.post("/admin/import/admission/preview")
async def preview_admission_data(
    file: UploadFile = File(...),
    is_admin: bool = Depends(verify_admin)
):
    """
    预览录取数据（前5行）

    Args:
        file: 上传的CSV文件

    Returns:
        预览数据
    """
    # 验证文件类型
    if not file.filename.endswith('.csv'):
        return {
            "code": 1,
            "message": "请上传CSV文件"
        }

    try:
        # 读取CSV文件
        contents = await file.read()

        # 解码并解析CSV
        from io import StringIO
        csv_text = contents.decode('utf-8')
        csv_file = StringIO(csv_text)
        csv_reader = csv.DictReader(csv_file)

        # 只读取前5行
        preview_data = []
        for i, row in enumerate(csv_reader):
            if i >= 5:
                break
            preview_data.append(dict(row))

        return {
            "code": 0,
            "data": {
                "preview": preview_data,
                "total_rows": len(preview_data)
            }
        }

    except Exception as e:
        return {
            "code": 1,
            "message": f"预览失败: {str(e)}"
        }