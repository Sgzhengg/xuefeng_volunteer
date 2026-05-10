# -*- coding: utf-8 -*-
import sys
import io
# 设置标准输出为UTF-8编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from app.core.config import settings
from app.api.router import router as api_router
from app.api.sunshine_router import router as sunshine_router
from app.api.auth import router as auth_router
from app.api.plan import router as plan_router
from app.api.admin import router as admin_router
from app.api.favorite import router as favorite_router
from app.api.history import router as history_router
import os

app = FastAPI(
    title="学锋志愿教练 API",
    description="高考志愿填报 AI 教练后端服务",
    version="2.0.0",
)

# ==================== 模板引擎配置 ====================
# 配置Jinja2模板引擎，用于管理后台页面
templates = Jinja2Templates(directory="admin/templates")

# ==================== 静态文件挂载 ====================
# 挂载管理后台的静态文件（CSS、JS等）
app.mount("/admin/static", StaticFiles(directory="admin/static"), name="admin_static")

# ==================== CORS 配置 ====================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== API 路由注册 ====================
# 注册主要API路由
app.include_router(api_router, prefix="/api/v1")

# 注册阳光高考爬虫路由
app.include_router(sunshine_router, prefix="/api/v1", tags=["sunshine"])

# 注册认证路由
app.include_router(auth_router, prefix="/api/v1", tags=["auth"])

# 注册志愿表路由
app.include_router(plan_router, prefix="/api/v1", tags=["plan"])

# 注册管理后台路由
app.include_router(admin_router, prefix="/api/v1", tags=["admin"])

# 注册收藏功能路由
app.include_router(favorite_router, prefix="/api/v1", tags=["favorite"])

# 注册历史推荐路由
app.include_router(history_router, prefix="/api/v1", tags=["history"])

# ==================== 管理后台页面路由 ====================
@app.get("/admin", response_class=HTMLResponse)
async def admin_root(request: Request):
    """管理后台登录页（根路径）"""
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/admin/{path:path}", response_class=HTMLResponse)
async def admin_pages(request: Request, path: str):
    """
    管理后台页面路由

    Args:
        request: FastAPI请求对象
        path: 页面路径（dashboard, universities, admission_data等）

    Returns:
        渲染后的HTML页面
    """
    # 支持的页面列表
    allowed_pages = ["dashboard", "universities", "admission-data", "admission_data"]

    # 移除.html后缀（如果存在）
    path = path.replace(".html", "")

    # 转换路径：将连字符转换为下划线以匹配模板文件名
    template_name = path.replace("-", "_")

    # 验证页面是否在允许列表中
    if path not in allowed_pages:
        # 如果页面不存在，重定向到仪表盘
        template_name = "dashboard"

    return templates.TemplateResponse(f"{template_name}.html", {"request": request})


# ==================== 系统路由 ====================
@app.get("/")
async def root():
    return {
        "message": "学锋志愿教练 API",
        "version": "2.0.0",
        "status": "running",
        "admin_available": True  # 指示管理后台可用
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "services": {
            "api": "ok",
            "cache": "ok",
            "admin": "ok"  # 管理后台状态
        }
    }


# ==================== 启动事件 ====================
@app.on_event("startup")
async def startup_event():
    """应用启动时的初始化操作"""
    import uvicorn
    print("""
    =========================================================
                     [OK] XueFeng Volunteer Coach
                        [OK] Admin Panel System

    [OK] API Server: http://localhost:8000
    [OK] Admin Panel: http://localhost:8000/admin
    [OK] API Docs: http://localhost:8000/docs

    [OK] Login: admin / password
    =========================================================
    """)

    # 检查必要的目录和文件
    required_dirs = ["admin/templates", "admin/static", "admin/static/css", "admin/static/js"]
    required_files = ["admin/templates/login.html", "admin/static/css/style.css"]

    for dir_path in required_dirs:
        if not os.path.exists(dir_path):
            print(f"[WARNING] Directory not found - {dir_path}")

    for file_path in required_files:
        if not os.path.exists(file_path):
            print(f"[WARNING] File not found - {file_path}")

    print("[OK] Admin panel system initialized successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时的清理操作"""
    print("[OK] XueFeng Volunteer Coach API stopped")
