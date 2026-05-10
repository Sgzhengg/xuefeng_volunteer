# -*- coding: utf-8 -*-
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


# 请求模型
class AdmissionProbabilityRequest(BaseModel):
    province: str
    score: int
    rank: Optional[int] = None
    subject_type: str
    university_name: Optional[str] = None
    major_name: Optional[str] = None


class UniversityInfoRequest(BaseModel):
    university_name: str


class MajorEmploymentRequest(BaseModel):
    major_name: str


class ChatMessage(BaseModel):
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: int


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    user_profile: Optional[dict] = None
    context: Optional[dict] = None  # 上下文信息（分数、省份等）
    conversation_history: Optional[List[ChatMessage]] = None  # 对话历史


# 响应模型
class AdmissionProbabilityResponse(BaseModel):
    success: bool
    message: Optional[str] = None
    data: Optional[dict] = None


class UniversityInfoResponse(BaseModel):
    success: bool
    message: Optional[str] = None
    data: Optional[dict] = None


class MajorEmploymentResponse(BaseModel):
    success: bool
    message: Optional[str] = None
    data: Optional[dict] = None


class ChatResponse(BaseModel):
    success: bool
    message: str
    session_id: str
    tool_calls: Optional[List[dict]] = None


# PDF 报告模型
class PDFReportRequest(BaseModel):
    user_profile: dict
    chat_history: List[ChatMessage]
    data_context: Optional[dict] = None


class VolunteerSchemeRequest(BaseModel):
    province: str
    score: int
    rank: Optional[int] = None
    subject_type: str
    target_majors: List[str]
    preferences: Optional[dict] = None


class RecommendationRequest(BaseModel):
    province: str
    score: int
    rank: Optional[int] = None
    subject_type: str = "理科"
    target_majors: Optional[List[str]] = None
    preferences: Optional[dict] = None


class EnhancedPDFReportRequest(BaseModel):
    """Enhanced PDF report generation request"""
    recommendation_result: dict  # Complete recommendation result data
    export_format: str = "pdf"  # 'pdf' or 'html'


# [NEW] 留粤VS出省对比请求模型
class CompareRequest(BaseModel):
    province: str  # 考生省份
    score: int  # 高考分数
    rank: int  # 全省位次
    subject_type: str = "理科"  # 科目类型
    target_majors: Optional[List[str]] = None  # 目标专业列表
    prefer_city: Optional[str] = None  # 偏好城市


# [NEW] 热词更新请求模型
class HeatWord(BaseModel):
    rank: int  # 排名
    word: str  # 热词
    heat: int  # 热度值
    trend: str  # 趋势：up/down/stable
    change: str  # 变化幅度，如"+15%"

class HeatWordsUpdateRequest(BaseModel):
    heat_words: List[HeatWord]  # 热词列表
    admin_key: str  # 管理员密钥（简单验证）


# [NEW] 志愿表评估相关模型
class VolunteerEvaluationRequest(BaseModel):
    """志愿表评估请求"""
    user_info: Dict[str, Any]  # 用户信息，包含rank、province等
    volunteers: List[Dict[str, Any]]  # 志愿列表


class PlanSummaryRequest(BaseModel):
    """志愿方案摘要请求"""
    plan_data: Dict[str, Any]  # 志愿方案数据
