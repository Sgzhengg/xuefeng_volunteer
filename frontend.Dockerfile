# 静态文件部署方案（本地构建完成）
FROM zeabur/caddy-static

LABEL "language"="static"
LABEL "version"="2026-05-14-v7"

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

# 复制本地构建好的前端文件（需要先执行 flutter build web --release）
COPY build/web /usr/share/caddy

EXPOSE 8080