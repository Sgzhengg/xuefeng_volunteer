/**
 * 管理后台通用JavaScript文件
 * 提供API调用、工具函数等功能
 */

// ==================== API 配置 ====================
const API_BASE_URL = '/api/v1';

// ==================== API 调用封装 ====================
/**
 * 发起API请求
 * @param {string} endpoint - API端点
 * @param {string} method - HTTP方法
 * @param {object} data - 请求数据
 * @param {boolean} withAuth - 是否需要认证
 * @returns {Promise} API响应
 */
async function apiRequest(endpoint, method = 'GET', data = null, withAuth = true) {
    const config = {
        method: method,
        headers: {
            'Content-Type': 'application/json'
        }
    };

    if (withAuth) {
        const token = localStorage.getItem('admin_token');
        if (!token) {
            // 未登录，跳转到登录页
            if (window.location.pathname !== '/admin') {
                window.location.href = '/admin';
            }
            throw new Error('未登录');
        }
        config.headers['Authorization'] = `Bearer ${token}`;
    }

    if (data && method !== 'GET') {
        config.body = JSON.stringify(data);
    }

    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, config);

        // 检查认证状态
        if (response.status === 401) {
            localStorage.removeItem('admin_token');
            localStorage.removeItem('admin_username');
            window.location.href = '/admin';
            throw new Error('认证失败，请重新登录');
        }

        const result = await response.json();
        return result;

    } catch (error) {
        console.error('API请求失败:', error);
        throw error;
    }
}

// ==================== 工具函数 ====================

/**
 * 显示成功消息
 * @param {string} message - 消息内容
 */
function showSuccess(message) {
    alert(`✅ ${message}`);
}

/**
 * 显示错误消息
 * @param {string} message - 消息内容
 */
function showError(message) {
    alert(`❌ ${message}`);
}

/**
 * 显示确认对话框
 * @param {string} message - 确认消息
 * @returns {boolean} 用户是否确认
 */
function showConfirm(message) {
    return confirm(`⚠️ ${message}`);
}

/**
 * 格式化日期时间
 * @param {string} datetime - 日期时间字符串
 * @returns {string} 格式化后的日期时间
 */
function formatDateTime(datetime) {
    if (!datetime) return '-';
    const date = new Date(datetime);
    return date.toLocaleString('zh-CN');
}

/**
 * 格式化数字
 * @param {number} num - 数字
 * @returns {string} 格式化后的数字
 */
function formatNumber(num) {
    if (num === null || num === undefined) return '-';
    return new Intl.NumberFormat('zh-CN').format(num);
}

// ==================== 表单验证 ====================

/**
 * 验证必填字段
 * @param {string} value - 字段值
 * @param {string} fieldName - 字段名称
 * @returns {boolean} 是否有效
 */
function validateRequired(value, fieldName) {
    if (!value || value.trim() === '') {
        showError(`${fieldName}不能为空`);
        return false;
    }
    return true;
}

/**
 * 验证URL格式
 * @param {string} url - URL地址
 * @returns {boolean} 是否有效
 */
function validateUrl(url) {
    if (!url) return true; // 可选字段
    try {
        new URL(url);
        return true;
    } catch {
        showError('请输入有效的URL地址');
        return false;
    }
}

/**
 * 验证邮箱格式
 * @param {string} email - 邮箱地址
 * @returns {boolean} 是否有效
 */
function validateEmail(email) {
    if (!email) return true; // 可选字段
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
        showError('请输入有效的邮箱地址');
        return false;
    }
    return true;
}

// ==================== 加载状态管理 ====================

/**
 * 设置加载状态
 * @param {boolean} loading - 是否加载中
 * @param {string} elementId - 按钮元素ID
 */
function setLoading(loading, elementId) {
    const button = document.getElementById(elementId);
    if (button) {
        button.disabled = loading;
        button.textContent = loading ? '加载中...' : button.dataset.originalText || button.textContent;
    }
}

/**
 * 保存按钮原始文本
 * @param {string} elementId - 按钮元素ID
 */
function saveButtonText(elementId) {
    const button = document.getElementById(elementId);
    if (button && !button.dataset.originalText) {
        button.dataset.originalText = button.textContent;
    }
}

// ==================== 数据导出 ====================

/**
 * 导出数据为CSV文件
 * @param {array} data - 数据数组
 * @param {string} filename - 文件名
 */
function exportToCSV(data, filename) {
    if (!data || data.length === 0) {
        showError('没有数据可以导出');
        return;
    }

    // 获取表头
    const headers = Object.keys(data[0]);

    // 构建CSV内容
    const csvContent = [
        headers.join(','),
        ...data.map(row => headers.map(header => {
            const value = row[header];
            // 处理包含逗号或引号的值
            if (typeof value === 'string' && (value.includes(',') || value.includes('"'))) {
                return `"${value.replace(/"/g, '""')}"`;
            }
            return value || '';
        }).join(','))
    ].join('\n');

    // 创建下载链接
    const blob = new Blob(['﻿' + csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);

    link.setAttribute('href', url);
    link.setAttribute('download', `${filename}.csv`);
    link.style.visibility = 'hidden';

    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// ==================== 分页工具 ====================

/**
 * 分页信息计算
 * @param {number} total - 总数量
 * @param {number} page - 当前页
 * @param {number} limit - 每页数量
 * @returns {object} 分页信息
 */
function calculatePagination(total, page, limit) {
    const totalPages = Math.ceil(total / limit);
    const startItem = (page - 1) * limit + 1;
    const endItem = Math.min(page * limit, total);

    return {
        totalPages,
        startItem,
        endItem,
        hasNextPage: page < totalPages,
        hasPrevPage: page > 1
    };
}

// ==================== 文件上传工具 ====================

/**
 * 文件大小格式化
 * @param {number} bytes - 文件大小（字节）
 * @returns {string} 格式化后的文件大小
 */
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';

    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));

    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

/**
 * 验证文件类型
 * @param {File} file - 文件对象
 * @param {array} allowedTypes - 允许的文件类型数组
 * @returns {boolean} 是否有效
 */
function validateFileType(file, allowedTypes) {
    const fileExtension = file.name.split('.').pop().toLowerCase();
    return allowedTypes.includes(fileExtension);
}

/**
 * 验证文件大小
 * @param {File} file - 文件对象
 * @param {number} maxSize - 最大文件大小（字节）
 * @returns {boolean} 是否有效
 */
function validateFileSize(file, maxSize) {
    return file.size <= maxSize;
}

// ==================== 搜索功能 ====================

/**
 * 防抖函数
 * @param {function} func - 要执行的函数
 * @param {number} delay - 延迟时间（毫秒）
 * @returns {function} 防抖后的函数
 */
function debounce(func, delay) {
    let timeoutId;
    return function(...args) {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => func.apply(this, args), delay);
    };
}

/**
 * 高亮搜索关键词
 * @param {string} text - 原始文本
 * @param {string} keyword - 关键词
 * @returns {string} 高亮后的HTML
 */
function highlightKeyword(text, keyword) {
    if (!keyword) return text;

    const regex = new RegExp(`(${keyword})`, 'gi');
    return text.replace(regex, '<mark style="background: yellow; padding: 2px 4px; border-radius: 2px;">$1</mark>');
}

// ==================== 页面初始化 ====================

/**
 * 页面加载完成后执行
 * @param {function} callback - 回调函数
 */
function onDocumentReady(callback) {
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', callback);
    } else {
        callback();
    }
}

/**
 * 检查登录状态
 * @returns {boolean} 是否已登录
 */
function isLoggedIn() {
    return !!localStorage.getItem('admin_token');
}

/**
 * 获取当前用户信息
 * @returns {object} 用户信息
 */
function getCurrentUser() {
    return {
        token: localStorage.getItem('admin_token'),
        username: localStorage.getItem('admin_username')
    };
}

// ==================== 错误处理 ====================

/**
 * 处理API错误
 * @param {object} error - 错误对象
 * @param {string} defaultMessage - 默认错误消息
 */
function handleApiError(error, defaultMessage = '操作失败') {
    console.error('API错误:', error);

    if (error.message) {
        showError(error.message);
    } else {
        showError(defaultMessage);
    }
}

/**
 * 显示Toast消息
 * @param {string} message - 消息内容
 * @param {string} type - 消息类型 (success/error/warning/info)
 * @param {number} duration - 显示时长（毫秒）
 */
function showToast(message, type = 'info', duration = 3000) {
    // 简单实现，后续可以升级为更好的Toast组件
    const toast = document.createElement('div');
    toast.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : '#3b82f6'};
        color: white;
        padding: 12px 20px;
        border-radius: 6px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        z-index: 10000;
        animation: slideIn 0.3s ease-out;
    `;
    toast.textContent = message;

    document.body.appendChild(toast);

    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease-in';
        setTimeout(() => {
            document.body.removeChild(toast);
        }, 300);
    }, duration);
}

// 添加动画样式
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }

    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// ==================== 导出 ====================
// 将函数导出供其他模块使用
window.AdminUtils = {
    apiRequest,
    showSuccess,
    showError,
    showConfirm,
    formatDateTime,
    formatNumber,
    validateRequired,
    validateUrl,
    validateEmail,
    setLoading,
    saveButtonText,
    exportToCSV,
    calculatePagination,
    formatFileSize,
    validateFileType,
    validateFileSize,
    debounce,
    highlightKeyword,
    onDocumentReady,
    isLoggedIn,
    getCurrentUser,
    handleApiError,
    showToast
};
