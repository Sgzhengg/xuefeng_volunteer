from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.router import router as api_router
from app.api.sunshine_router import router as sunshine_router

app = FastAPI(
    title="学锋志愿教练 API",
    description="高考志愿填报 AI 教练后端服务",
    version="2.0.0",
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(api_router, prefix="/api/v1")

# 注册阳光高考爬虫路由
app.include_router(sunshine_router, prefix="/api/v1", tags=["sunshine"])


@app.get("/")
async def root():
    return {
        "message": "学锋志愿教练 API",
        "version": "2.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "services": {
            "api": "ok",
            "cache": "ok"
        }
    }
