/**
 * 数据采集中心 JavaScript
 */

// ==================== 状态管理 ====================
let refreshInterval = null;
let isRefreshing = false;

// ==================== 初始化 ====================
document.addEventListener('DOMContentLoaded', async function() {
    // 检查登录状态
    if (!localStorage.getItem('admin_token')) {
        window.location.href = '/admin';
        return;
    }

    // 加载初始数据
    await loadStats();
    await loadTasks();

    // 设置自动刷新（每5秒）
    refreshInterval = setInterval(async () => {
        if (!isRefreshing) {
            await loadStats();
            await loadTasks(false); // 静默刷新
        }
    }, 5000);

    // 绑定事件
    bindEvents();
});

function bindEvents() {
    // 刷新按钮
    document.getElementById('refreshBtn').addEventListener('click', async function() {
        await refreshData();
    });

    // 创建任务按钮
    document.getElementById('createTaskBtn').addEventListener('click', async function() {
        await createTask();
    });

    // 状态筛选
    document.getElementById('filterStatus').addEventListener('change', async function() {
        await loadTasks();
    });

    // 退出登录
    document.getElementById('logoutBtn').addEventListener('click', function() {
        if (confirm('确定要退出登录吗？')) {
            localStorage.removeItem('admin_token');
            localStorage.removeItem('admin_username');
            window.location.href = '/admin';
        }
    });
}

// ==================== 数据加载 ====================
async function loadStats() {
    try {
        const result = await AdminUtils.apiRequest('/admin/collection/stats');

        if (result.code === 0) {
            const stats = result.data;
            document.getElementById('totalTasks').textContent = stats.task_stats?.pending || 0 + stats.task_stats?.running || 0 + stats.task_stats?.success || 0 + stats.task_stats?.failed || 0;
            document.getElementById('successTasks').textContent = stats.task_stats?.success || 0;
            document.getElementById('runningTasks').textContent = stats.task_stats?.running || 0;
            document.getElementById('failedTasks').textContent = stats.task_stats?.failed || 0;
            document.getElementById('adminUsername').textContent = localStorage.getItem('admin_username') || '管理员';
        }
    } catch (error) {
        console.error('加载统计数据失败:', error);
    }
}

async function loadTasks(showLoading = true) {
    const filterStatus = document.getElementById('filterStatus').value;

    try {
        const result = await AdminUtils.apiRequest(
            `/admin/collection/tasks?status=${filterStatus}&limit=50`
        );

        if (result.code === 0) {
            renderTasks(result.data.tasks);
        }
    } catch (error) {
        console.error('加载任务列表失败:', error);
        if (showLoading) {
            AdminUtils.showError('加载任务列表失败');
        }
    }
}

// ==================== 渲染函数 ====================
function renderTasks(tasks) {
    const container = document.getElementById('taskList');

    if (tasks.length === 0) {
        container.innerHTML = `
            <div style="text-align: center; padding: 40px; color: #6b7280;">
                <div style="font-size: 48px; margin-bottom: 16px;">📭</div>
                <div>暂无采集任务</div>
            </div>
        `;
        return;
    }

    container.innerHTML = tasks.map(task => `
        <div class="version-card" style="margin-bottom: 16px;">
            <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 12px;">
                <div>
                    <div style="font-weight: 600; font-size: 16px; margin-bottom: 4px;">${task.task_name}</div>
                    <div style="font-size: 13px; color: #6b7280;">
                        类型: ${getTaskTypeName(task.task_type)} | 年份: ${task.year}
                        ${task.province ? ` | 省份: ${task.province}` : ''}
                    </div>
                </div>
                <span class="task-status ${task.status}">${getTaskStatusName(task.status)}</span>
            </div>

            ${task.status === 'running' || task.status === 'pending' ? `
                <div style="margin-bottom: 12px;">
                    <div style="display: flex; justify-content: space-between; font-size: 12px; margin-bottom: 4px;">
                        <span>进度: ${task.processed_items || 0} / ${task.total_items || 0}</span>
                        <span>${task.progress || 0}%</span>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-bar-fill" style="width: ${task.progress || 0}%"></div>
                    </div>
                </div>
            ` : ''}

            <div style="display: flex; justify-content: space-between; align-items: center; font-size: 12px; color: #6b7280;">
                <div>
                    创建时间: ${AdminUtils.formatDateTime(task.created_at)}
                    ${task.completed_at ? ` | 完成时间: ${AdminUtils.formatDateTime(task.completed_at)}` : ''}
                </div>
                <div style="display: flex; gap: 8px;">
                    <button class="btn btn-secondary" style="padding: 6px 12px; font-size: 12px;" onclick="viewLogs(${task.id})">
                        📋 日志
                    </button>
                    ${task.status === 'pending' || task.status === 'running' ? `
                        <button class="btn btn-danger" style="padding: 6px 12px; font-size: 12px;" onclick="cancelTask(${task.id})">
                            ✕ 取消
                        </button>
                    ` : ''}
                    ${task.status === 'failed' || task.status === 'success' ? `
                        <button class="btn btn-danger" style="padding: 6px 12px; font-size: 12px;" onclick="deleteTask(${task.id})">
                            🗑️ 删除
                        </button>
                    ` : ''}
                </div>
            </div>

            ${task.error_message ? `
                <div style="margin-top: 12px; padding: 8px 12px; background: #fef2f2; border-radius: 6px; font-size: 12px; color: #dc2626;">
                    ❌ ${task.error_message}
                </div>
            ` : ''}
        </div>
    `).join('');
}

// ==================== 任务操作 ====================
async function createTask() {
    const taskName = document.getElementById('taskName').value.trim();
    const taskType = document.getElementById('taskType').value;
    const taskYear = parseInt(document.getElementById('taskYear').value);
    const taskProvince = document.getElementById('taskProvince').value || null;

    // 验证
    if (!taskName) {
        AdminUtils.showError('请输入任务名称');
        return;
    }

    const btn = document.getElementById('createTaskBtn');
    btn.disabled = true;
    btn.textContent = '创建中...';

    try {
        const result = await AdminUtils.apiRequest('/admin/collection/tasks', 'POST', {
            task_name: taskName,
            task_type: taskType,
            year: taskYear,
            province: taskProvince
        });

        if (result.code === 0) {
            AdminUtils.showSuccess('任务创建成功');
            document.getElementById('taskName').value = '';
            await loadTasks();
            await loadStats();
        } else {
            AdminUtils.showError(result.message);
        }
    } catch (error) {
        AdminUtils.handleApiError(error, '创建任务失败');
    } finally {
        btn.disabled = false;
        btn.textContent = '创建任务';
    }
}

async function cancelTask(taskId) {
    if (!AdminUtils.showConfirm('确定要取消此任务吗？')) {
        return;
    }

    try {
        const result = await AdminUtils.apiRequest(`/admin/collection/tasks/${taskId}/cancel`, 'POST');

        if (result.code === 0) {
            AdminUtils.showSuccess('任务已取消');
            await loadTasks();
            await loadStats();
        } else {
            AdminUtils.showError(result.message);
        }
    } catch (error) {
        AdminUtils.handleApiError(error, '取消任务失败');
    }
}

async function deleteTask(taskId) {
    if (!AdminUtils.showConfirm('确定要删除此任务吗？此操作不可恢复。')) {
        return;
    }

    try {
        const result = await AdminUtils.apiRequest(`/admin/collection/tasks/${taskId}`, 'DELETE');

        if (result.code === 0) {
            AdminUtils.showSuccess('任务已删除');
            await loadTasks();
            await loadStats();
        } else {
            AdminUtils.showError(result.message);
        }
    } catch (error) {
        AdminUtils.handleApiError(error, '删除任务失败');
    }
}

async function viewLogs(taskId) {
    try {
        const result = await AdminUtils.apiRequest(`/admin/collection/tasks/${taskId}/logs?limit=100`);

        if (result.code === 0) {
            const logs = result.data.logs;
            const container = document.getElementById('logContent');

            if (logs.length === 0) {
                container.innerHTML = '<div style="text-align: center; padding: 20px; color: #6b7280;">暂无日志</div>';
            } else {
                container.innerHTML = logs.reverse().map(log => `
                    <div class="log-entry ${log.log_level}">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                            <span style="font-weight: 600;">${log.log_level}</span>
                            <span style="color: #6b7280;">${AdminUtils.formatDateTime(log.created_at)}</span>
                        </div>
                        <div>${log.message}</div>
                    </div>
                `).join('');
            }

            document.getElementById('logModal').classList.add('active');
        }
    } catch (error) {
        AdminUtils.handleApiError(error, '加载日志失败');
    }
}

function closeLogModal() {
    document.getElementById('logModal').classList.remove('active');
}

// ==================== 工具函数 ====================
async function refreshData() {
    if (isRefreshing) return;

    isRefreshing = true;
    const btn = document.getElementById('refreshBtn');
    const icon = document.getElementById('refreshIcon');

    icon.innerHTML = '<span class="refresh-indicator"></span>';

    try {
        await Promise.all([
            loadStats(),
            loadTasks()
        ]);
        AdminUtils.showSuccess('刷新成功');
    } catch (error) {
        AdminUtils.showError('刷新失败');
    } finally {
        icon.textContent = '🔄';
        isRefreshing = false;
    }
}

function getTaskTypeName(type) {
    const names = {
        'universities': '院校数据',
        'admission_data': '录取数据',
        'majors': '专业数据',
        'validation': '数据验证'
    };
    return names[type] || type;
}

function getTaskStatusName(status) {
    const names = {
        'pending': '待执行',
        'running': '运行中',
        'success': '成功',
        'failed': '失败',
        'cancelled': '已取消'
    };
    return names[status] || status;
}

// ==================== 清理 ====================
window.addEventListener('beforeunload', function() {
    if (refreshInterval) {
        clearInterval(refreshInterval);
    }
});
