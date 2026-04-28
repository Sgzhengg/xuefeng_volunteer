from pydantic import BaseModel
from typing import Optional, List
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
