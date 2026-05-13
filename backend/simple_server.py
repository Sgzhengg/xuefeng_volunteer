from flask import Flask, jsonify, request
import json
import os

app = Flask(__name__)

@app.route('/api/v1/chat', methods=['POST'])
def chat():
    """聊天API"""
    data = request.json
    message = data.get('message', '')

    # Mock响应
    response = {
        "id": "chat_" + str(hash(message)) % 10000,
        "message": f"学锋老师：{message} - 这是一个测试响应！",
        "timestamp": "2026-05-10T19:40:00Z",
        "type": "text"
    }

    return jsonify(response)

@app.route('/api/v1/health', methods=['GET'])
def health():
    """健康检查"""
    return jsonify({
        "status": "healthy",
        "services": {
            "api": "ok",
            "chat": "ok"
        }
    })

@app.route('/')
def root():
    """根路径"""
    return jsonify({
        "message": "学锋志愿教练 API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "chat": "/api/v1/chat",
            "health": "/api/v1/health"
        }
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)