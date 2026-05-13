# 使用官方Python镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码（按顺序复制以确保正确性）
COPY app/ ./app/
COPY admin/ ./admin/
COPY data/ ./data/

# 创建必要的目录
RUN mkdir -p /app/data /app/database /app/logs /app/reports

# 验证关键文件存在
RUN ls -la /app/app/main.py && \
    ls -la /app/admin/templates/login.html && \
    echo "✓ 关键文件验证通过"

# 暴露端口
EXPOSE 8000

# 健康检查（使用Python替代curl）
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health', timeout=5)" || exit 1

# 启动命令
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
