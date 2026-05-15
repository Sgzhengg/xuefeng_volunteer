# 静态文件部署方案（本地构建完成）
FROM zeabur/caddy-static

LABEL "language"="static"
LABEL "version"="2026-05-14-v14"

# 创建 Caddyfile 配置 - 使用Zeabur内部服务标识符
RUN mkdir -p /etc/caddy && cat > /etc/caddy/Caddyfile << 'EOF'
:8080 {
  # 反向代理 API 请求到后端服务（使用Zeabur内部服务ID）
  handle /api/* {
    reverse_proxy http://service-6a05936d2376f7967820b216:8000
  }

  # 反向代理管理后台
  handle /admin* {
    reverse_proxy http://service-6a05936d2376f7967820b216:8000
  }

  # 反向代理 API 文档
  handle /docs {
    reverse_proxy http://service-6a05936d2376f7967820b216:8000
  }

  handle /openapi.json {
    reverse_proxy http://service-6a05936d2376f7967820b216:8000
  }

  # 健康检查端点
  handle /health {
    reverse_proxy http://service-6a05936d2376f7967820b216:8000
  }

  # 🆕 为静态文件设置缓存清除头（修复Caddy语法）
  @staticFiles path *.js *.html *.css *.json *.svg *.png *.jpg *.webp *.wasm *.dat
  header @staticFiles Cache-Control "no-cache, no-store, must-revalidate, max-age=0"
  header @staticFiles Pragma "no-cache"
  header @staticFiles Expires "0"

  # 🆕 为Service Worker设置特殊头
  @serviceWorker path /flutter_service_worker.js
  header @serviceWorker Cache-Control "no-cache, no-store, must-revalidate, max-age=0"
  header @serviceWorker Service-Worker-Allowed "/"

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

# 复制本地构建好的前端文件
COPY build/web /usr/share/caddy

EXPOSE 8080