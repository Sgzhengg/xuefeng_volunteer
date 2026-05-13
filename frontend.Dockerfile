FROM zeabur/caddy-static

LABEL "language"="static"

# 创建 Caddyfile 配置
# 使用环境变量获取后端服务地址，或使用默认的 Zeabur 内网格式
RUN mkdir -p /etc/caddy && cat > /etc/caddy/Caddyfile << 'EOF'
:8080 {
  # 反向代理 API 请求到后端服务
  handle /api/* {
    reverse_proxy {$BACKEND_API_URL:backend-api.zeabur.internal:8000}
  }

  # 反向代理管理后台
  handle /admin* {
    reverse_proxy {$BACKEND_API_URL:backend-api.zeabur.internal:8000}
  }

  # 反向代理 API 文档
  handle /docs {
    reverse_proxy {$BACKEND_API_URL:backend-api.zeabur.internal:8000}
  }

  handle /openapi.json {
    reverse_proxy {$BACKEND_API_URL:backend-api.zeabur.internal:8000}
  }

  # 健康检查端点
  handle /health {
    reverse_proxy {$BACKEND_API_URL:backend-api.zeabur.internal:8000}
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

# 复制前端构建产物
COPY build/web /usr/share/caddy

EXPOSE 8080
