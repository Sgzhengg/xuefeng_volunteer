"""
数据库模型定义
用于存储从阳光高考爬取的数据
"""

from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


# ========== 院校相关模型 ==========

class UniversityBase(BaseModel):
    """院校基础信息"""
    id: str
    name: str
    province: str
    city: Optional[str] = None
    type: str  # 综合类、理工类等
    level: Optional[str] = None  # 985、211、双一流等
    website: Optional[str] = None


class UniversityDetail(BaseModel):
    """院校详细信息"""
    id: str
    name: str
    english_name: Optional[str] = None
    province: str
    city: Optional[str] = None
    type: str
    level: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None
    founded_year: Optional[int] = None
    campus_area: Optional[str] = None
    departments: Optional[List[str]] = []
    tuition: Optional[str] = None
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()


class UniversityListResponse(BaseModel):
    """院校列表响应"""
    universities: List[UniversityBase]
    total: int
    updated_at: str


# ========== 专业相关模型 ==========

class MajorBase(BaseModel):
    """专业基础信息"""
    code: str
    name: str
    category: str  # 学科门类
    degree: str  # 学位层次
    duration: str  # 学制


class MajorDetail(BaseModel):
    """专业详细信息"""
    code: str
    name: str
    category: str
    degree: str
    duration: str
    description: Optional[str] = None
    employment_rate: Optional[float] = None
    salary_avg: Optional[float] = None
    related_majors: Optional[List[str]] = []
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()


class MajorListResponse(BaseModel):
    """专业列表响应"""
    majors: List[MajorBase]
    total: int
    updated_at: str


# ========== 录取分数线相关模型 ==========

class AdmissionScore(BaseModel):
    """录取分数线"""
    university: str
    province: str
    year: int
    major: Optional[str] = None
    min_score: int
    avg_score: Optional[int] = None
    max_score: Optional[int] = None
    rank: Optional[int] = None
    batch: Optional[str] = None  # 批次


class AdmissionScoresResponse(BaseModel):
    """录取分数线列表响应"""
    province: str
    year: int
    scores: List[AdmissionScore]
    total: int
    updated_at: str


# ========== 志愿方案相关模型 ==========

class VolunteerRequest(BaseModel):
    """志愿方案请求"""
    province: str
    score: int
    rank: Optional[int] = None
    subject_type: str = "综合"
    target_majors: List[str] = []
    preferences: Optional[dict] = None


class SchoolChoice(BaseModel):
    """院校选择"""
    university_name: str
    major: str
    probability: str  # 录取概率
    suggestion: str  # 建议
    type: str  # 985、211等
    province: str
    city: Optional[str] = None


class VolunteerScheme(BaseModel):
    """志愿方案"""
    province: str
    score: int
    subject_type: str
    generated_at: str
    chong: List[SchoolChoice]  # 冲刺
    wen: List[SchoolChoice]   # 稳妥
    bao: List[SchoolChoice]   # 保底
    dian: List[SchoolChoice]  # 垫底
    advice: List[str]


# ========== API 响应模型 ==========

class SuccessResponse(BaseModel):
    """成功响应"""
    success: bool = True
    message: Optional[str] = None
    data: Optional[dict] = None
    source: str = "sunshine"  # sunshine、cache、mock


class ErrorResponse(BaseModel):
    """错误响应"""
    success: bool = False
    message: str
    error_code: Optional[str] = None
    data: None = None
