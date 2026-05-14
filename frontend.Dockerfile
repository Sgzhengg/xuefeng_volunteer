# 多阶段构建 - 第一阶段：构建Flutter应用
FROM cirrusci/flutter:3.24.5 AS builder

WORKDIR /app

# 安装必要的依赖库
RUN apt-get update && apt-get install -y \
    curl \
    git \
    unzip \
    xz-utils \
    zip \
    libglu1-mesa \
    && rm -rf /var/lib/apt/lists/*

# 预热Flutter
RUN flutter config --no-analytics && \
    flutter doctor -v && \
    flutter upgrade

# 复制项目文件
COPY . .

# 安装依赖
RUN flutter pub get

# 构建Web应用（添加更多标志以确保稳定性）
RUN flutter build web --release --web-renderer canvaskit

# 第二阶段：使用Caddy提供静态文件服务
FROM zeabur/caddy-static

LABEL "language"="static"
LABEL "version"="2026-05-14-v5"

# 创建 Caddyfile 配置 - 使用内部服务通信
RUN mkdir -p /etc/caddy && cat > /etc/caddy/Caddyfile << 'EOF'
:8080 {
  # 反向代理 API 请求到后端服务（使用内部服务名）
  handle /api/* {
    reverse_proxy http://service-6a042f655e7e3bf5e93f3747:8000
  }

  # 反向代理管理后台
  handle /admin* {
    reverse_proxy http://service-6a042f655e7e3bf5e93f3747:8000
  }

  # 反向代理 API 文档
  handle /docs {
    reverse_proxy http://service-6a042f655e7e3bf5e93f3747:8000
  }

  handle /openapi.json {
    reverse_proxy http://service-6a042f655e7e3bf5e93f3747:8000
  }

  # 健康检查端点
  handle /health {
    reverse_proxy http://service-6a042f655e7e3bf5e93f3747:8000
  }

  # 静态文件服务
  root * /usr/share/caddy
  file_server

  # 自定义错误页面
  handle_errors {
    @404 {
      expression {http.error.status_code} == 404
    }
    rewrite @404 /index.html
    file_server
  }
}
EOF

# 从构建阶段复制前端构建产物
COPY --from=builder /app/build/web /usr/share/caddy

EXPOSE 8080