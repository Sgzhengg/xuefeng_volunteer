from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # API 配置
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "学锋志愿教练"

    # OpenRouter 配置（必须配置）
    OPENROUTER_API_KEY: str = ""  # 从.env文件读取
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"

    # 缓存配置
    CACHE_TTL: int = 3600  # 1小时

    # CORS 配置
    BACKEND_CORS_ORIGINS: list = ["http://localhost:8080", "http://localhost:3000", "http://localhost:8081"]

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
