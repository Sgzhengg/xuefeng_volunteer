# -*- coding: utf-8 -*-
import sys
import io
# 设置标准输出为UTF-8编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
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
from app.api.collection_admin import router as collection_router
import os

app = FastAPI(
    title="学锋志愿教练 API",
    description="高考志愿填报 AI 教练后端服务",
    version="2.0.0",
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Log validation errors with the raw request body to help debug 422 issues from frontend payloads."""
    try:
        body_bytes = await request.body()
        try:
            body_text = body_bytes.decode('utf-8')
        except Exception:
            body_text = str(body_bytes)
    except Exception as e:
        body_text = f"<could not read body: {e}>"

    print(f"[VALIDATION ERROR] path={request.url.path} body={body_text} errors={exc.errors()}")

    # Return a JSON response that the frontend can parse (keeps status 422)
    return JSONResponse(status_code=422, content={
        "code": 1,
        "message": "validation error",
        "detail": exc.errors(),
        "body": body_text
    })

# ==================== 模板引擎配置 ====================
# 配置Jinja2模板引擎，用于管理后台页面
# 获取backend目录（app.main.py所在目录的父目录）
import pathlib
BACKEND_DIR = pathlib.Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BACKEND_DIR / "admin" / "templates"))

# ==================== 静态文件挂载 ====================
# 挂载管理后台的静态文件（CSS、JS等）
app.mount("/admin/static", StaticFiles(directory=str(BACKEND_DIR / "admin" / "static")), name="admin_static")

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

# 注册数据采集管理路由
app.include_router(collection_router, prefix="/api/v1", tags=["collection"])

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
    allowed_pages = ["dashboard", "universities", "admission-data", "admission_data",
                     "collection-center", "collection_center", "version-control"]

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
    # debug: print mapping file paths and counts to help detect missing data in deployments
    try:
        import json, subprocess, pathlib
        base = pathlib.Path(__file__).resolve().parent.parent
        simple_p = base / 'data' / 'group_code_mapping.json'
        detailed_p = base / 'data' / 'group_code_to_majors.json'

        def _try_count(p):
            try:
                if not p.exists():
                    return None
                with open(p, 'r', encoding='utf-8') as f:
                    d = json.load(f)
                    if isinstance(d, dict):
                        return len(d)
                    try:
                        return len(d)
                    except Exception:
                        return None
            except Exception as e:
                print(f"[DEBUG] failed to read {p}: {e}")
                return None

        print(f"[DEBUG] simple mapping path: {simple_p}, exists: {simple_p.exists()}")
        print(f"[DEBUG] detailed mapping path: {detailed_p}, exists: {detailed_p.exists()}")
        print(f"[DEBUG] simple mapping entries: {_try_count(simple_p)}")
        print(f"[DEBUG] detailed mapping entries: {_try_count(detailed_p)}")

        # try to show current commit if .git available inside image
        git_dir = base.parent / '.git'
        if git_dir.exists():
            try:
                commit = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD'], cwd=str(base.parent))
                commit = commit.decode().strip()
                print(f"[DEBUG] running commit: {commit}")
            except Exception:
                print("[DEBUG] could not read git commit")
        else:
            print('[DEBUG] .git not found in image; set DEPLOY_COMMIT env if needed')
        # If mapping files are missing in the image, try to download them from GitHub raw
        try:
            import urllib.request
            github_base = os.environ.get('GITHUB_RAW_BASE', 'https://raw.githubusercontent.com/Sgzhengg/xuefeng_volunteer/main')
            # ensure data dir exists
            app_data_dir = pathlib.Path(__file__).resolve().parent.parent / 'data'
            app_data_dir.mkdir(parents=True, exist_ok=True)

            def _download_if_missing(local_path: pathlib.Path, relative_url_path: str):
                if local_path.exists():
                    return False
                url = f"{github_base}/{relative_url_path}"
                try:
                    print(f"[DEBUG] attempting to download {url} -> {local_path}")
                    with urllib.request.urlopen(url, timeout=15) as resp:
                        if resp.status != 200:
                            print(f"[DEBUG] download failed status={resp.status} for {url}")
                            return False
                        data = resp.read()
                    with open(local_path, 'wb') as f:
                        f.write(data)
                    print(f"[DEBUG] downloaded and saved {local_path}")
                    return True
                except Exception as e:
                    print(f"[DEBUG] failed to download {url}: {e}")
                    return False

            # relative paths from repo root to backend/data
            _download_if_missing(base / 'data' / 'group_code_mapping.json', 'backend/data/group_code_mapping.json')
            _download_if_missing(base / 'data' / 'group_code_to_majors.json', 'backend/data/group_code_to_majors.json')
        except Exception as _e:
            print('[DEBUG] auto-download of mapping files failed:', _e)
    except Exception as _e:
        print('[DEBUG] startup mapping debug failed:', _e)
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
