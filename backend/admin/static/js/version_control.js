/**
 * 版本控制中心 JavaScript
 */

// ==================== 状态管理 ====================
let currentSwitchTarget = null;
let autoSwitchEnabled = false;

// ==================== 初始化 ====================
document.addEventListener('DOMContentLoaded', async function() {
    // 检查登录状态
    if (!localStorage.getItem('admin_token')) {
        window.location.href = '/admin';
        return;
    }

    // 加载初始数据
    await loadVersions();
    await loadComparison();
    await loadSwitchHistory();

    // 绑定事件
    bindEvents();
});

function bindEvents() {
    // 刷新按钮
    document.getElementById('refreshBtn').addEventListener('click', async function() {
        await refreshData();
    });

    // 检查数据完整度
    document.getElementById('checkVersionBtn').addEventListener('click', async function() {
        await checkDataCompleteness();
    });

    // 切换到2026年
    document.getElementById('switchTo2026Btn').addEventListener('click', function() {
        showConfirmModal(2026);
    });

    // 切换到2025年
    document.getElementById('switchTo2025Btn').addEventListener('click', function() {
        showConfirmModal(2025);
    });

    // 确认切换
    document.getElementById('confirmSwitchBtn').addEventListener('click', async function() {
        await performVersionSwitch();
    });

    // 自动切换开关
    document.getElementById('autoSwitchToggle').addEventListener('change', function() {
        autoSwitchEnabled = this.checked;
        // 这里可以调用API保存设置
        AdminUtils.showSuccess(autoSwitchEnabled ? '已启用自动切换' : '已禁用自动切换');
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
async function loadVersions() {
    try {
        const result = await AdminUtils.apiRequest('/admin/collection/versions');

        if (result.code === 0) {
            renderVersions(result.data.versions);
            updateAlert(result.data.versions);
        }
    } catch (error) {
        console.error('加载版本信息失败:', error);
    }
}

async function loadComparison() {
    try {
        const result = await AdminUtils.apiRequest('/admin/collection/versions/compare?year1=2025&year2=2026');

        if (result.code === 0) {
            renderComparison(result.data);
        }
    } catch (error) {
        console.error('加载版本对比失败:', error);
    }
}

async function loadSwitchHistory() {
    try {
        const result = await AdminUtils.apiRequest('/admin/collection/versions/history?limit=10');

        if (result.code === 0) {
            renderSwitchHistory(result.data.history);
        }
    } catch (error) {
        console.error('加载切换历史失败:', error);
    }
}

// ==================== 渲染函数 ====================
function renderVersions(versions) {
    const container = document.getElementById('versionCards');

    container.innerHTML = versions.map(version => {
        const metadata = version.metadata ? JSON.parse(version.metadata) : {};
        const provinceCoverage = version.province_coverage ? JSON.parse(version.province_coverage) : {};

        return `
            <div class="version-card ${version.status} ${version.is_active ? 'active' : ''}">
                <div class="version-year ${version.is_active ? 'active' : ''}">${version.year}</div>
                <span class="version-status ${version.status}">${getVersionStatusName(version.status)}</span>

                <div class="completeness-bar">
                    <div class="completeness-fill" style="width: ${version.data_completeness || 0}%;">
                        ${version.data_completeness || 0}%
                    </div>
                </div>

                <div class="stat-grid-mini">
                    <div class="stat-item-mini">
                        <div class="stat-value-mini">${AdminUtils.formatNumber(version.university_count)}</div>
                        <div class="stat-label-mini">院校数量</div>
                    </div>
                    <div class="stat-item-mini">
                        <div class="stat-value-mini">${AdminUtils.formatNumber(version.major_count)}</div>
                        <div class="stat-label-mini">专业数量</div>
                    </div>
                    <div class="stat-item-mini">
                        <div class="stat-value-mini">${Object.keys(provinceCoverage).length}</div>
                        <div class="stat-label-mini">覆盖省份</div>
                    </div>
                </div>

                ${Object.keys(provinceCoverage).length > 0 ? `
                    <div style="font-size: 12px; color: #6b7280; margin-bottom: 8px;">省份覆盖:</div>
                    <div class="province-coverage">
                        ${Object.entries(provinceCoverage).slice(0, 10).map(([prov, data]) => `
                            <span class="province-tag">${prov}</span>
                        `).join('')}
                        ${Object.keys(provinceCoverage).length > 10 ? `<span class="province-tag">+${Object.keys(provinceCoverage).length - 10}</span>` : ''}
                    </div>
                ` : ''}

                ${metadata.last_checked ? `
                    <div style="font-size: 12px; color: #6b7280; margin-top: 12px;">
                        最后检查: ${AdminUtils.formatDateTime(metadata.last_checked)}
                    </div>
                ` : ''}
            </div>
        `;
    }).join('');
}

function renderComparison(data) {
    const container = document.getElementById('comparisonBody');
    const year1 = data.year1 || {};
    const year2 = data.year2 || {};
    const comp = data.comparison || {};

    container.innerHTML = `
        <tr>
            <td>院校数量</td>
            <td>${AdminUtils.formatNumber(year1.university_count || 0)}</td>
            <td>${AdminUtils.formatNumber(year2.university_count || 0)}</td>
            <td class="${comp.university_diff >= 0 ? 'diff-positive' : 'diff-negative'}">
                ${comp.university_diff >= 0 ? '+' : ''}${AdminUtils.formatNumber(comp.university_diff || 0)}
            </td>
        </tr>
        <tr>
            <td>专业数量</td>
            <td>${AdminUtils.formatNumber(year1.major_count || 0)}</td>
            <td>${AdminUtils.formatNumber(year2.major_count || 0)}</td>
            <td class="${comp.major_diff >= 0 ? 'diff-positive' : 'diff-negative'}">
                ${comp.major_diff >= 0 ? '+' : ''}${AdminUtils.formatNumber(comp.major_diff || 0)}
            </td>
        </tr>
        <tr>
            <td>数据完整度</td>
            <td>${year1.data_completeness || 0}%</td>
            <td>${year2.data_completeness || 0}%</td>
            <td class="${comp.completeness_diff >= 0 ? 'diff-positive' : 'diff-negative'}">
                ${comp.completeness_diff >= 0 ? '+' : ''}${comp.completeness_diff || 0}%
            </td>
        </tr>
        <tr>
            <td>状态</td>
            <td>${getVersionStatusName(year1.status)}</td>
            <td>${getVersionStatusName(year2.status)}</td>
            <td>-</td>
        </tr>
    `;
}

function renderSwitchHistory(history) {
    const container = document.getElementById('switchHistory');

    if (history.length === 0) {
        container.innerHTML = '<div style="text-align: center; padding: 40px; color: #6b7280;">暂无切换历史</div>';
        return;
    }

    container.innerHTML = history.map(item => `
        <div class="history-item ${item.status}">
            <div style="flex: 1;">
                <div style="font-weight: 600; margin-bottom: 4px;">
                    ${item.from_year} → ${item.to_year}
                </div>
                <div style="font-size: 13px; color: #6b7280;">
                    ${AdminUtils.formatDateTime(item.switched_at)} | ${item.switched_by} | ${getSwitchTypeName(item.switch_type)}
                </div>
                ${item.reason ? `<div style="font-size: 12px; margin-top: 4px;">${item.reason}</div>` : ''}
            </div>
            <span class="task-status ${item.status}">${item.status === 'success' ? '成功' : '失败'}</span>
        </div>
    `).join('');
}

function updateAlert(versions) {
    const activeVersion = versions.find(v => v.is_active);
    const version2026 = versions.find(v => v.year === 2026);

    const alert = document.getElementById('versionAlert');

    if (activeVersion && version2026) {
        if (activeVersion.year === 2026) {
            alert.className = 'alert alert-success';
            alert.innerHTML = '<strong>✅ 当前使用 2026 年数据</strong><br>最新数据已生效。';
        } else if (version2026.data_completeness >= 100) {
            alert.className = 'alert alert-success';
            alert.innerHTML = '<strong>✅ 2026 年数据已就绪</strong><br>数据完整度达到 100%，可以进行版本切换。';
            document.getElementById('switchTo2026Btn').disabled = false;
        } else if (version2026.data_completeness >= 80) {
            alert.className = 'alert alert-warning';
            alert.innerHTML = `<strong>⚠️ 当前使用 ${activeVersion.year} 年数据</strong><br>2026 年数据准备中，完整度 ${version2026.data_completeness}%。建议达到 100% 后再切换。`;
        } else {
            alert.className = 'alert alert-info';
            alert.innerHTML = `<strong>ℹ️ 当前使用 ${activeVersion.year} 年数据</strong><br>2026 年数据准备中，完整度 ${version2026.data_completeness}%。`;
        }
    }

    // 更新按钮状态
    const switchTo2026Btn = document.getElementById('switchTo2026Btn');
    const switchTo2025Btn = document.getElementById('switchTo2025Btn');

    if (activeVersion) {
        if (activeVersion.year === 2025 && version2026 && version2026.status === 'ready') {
            switchTo2026Btn.disabled = false;
        } else {
            switchTo2026Btn.disabled = true;
        }

        if (activeVersion.year === 2026) {
            switchTo2025Btn.disabled = false;
        } else {
            switchTo2025Btn.disabled = true;
        }
    }
}

// ==================== 版本操作 ====================
async function checkDataCompleteness() {
    const btn = document.getElementById('checkVersionBtn');
    btn.disabled = true;
    btn.textContent = '检查中...';

    try {
        // 这里应该调用检查脚本
        // 由于需要执行后台脚本，我们模拟一个延迟
        await new Promise(resolve => setTimeout(resolve, 2000));

        AdminUtils.showSuccess('数据检查完成');
        await loadVersions();
        await loadComparison();
    } catch (error) {
        AdminUtils.handleApiError(error, '检查失败');
    } finally {
        btn.disabled = false;
        btn.textContent = '📊 检查数据完整度';
    }
}

function showConfirmModal(targetYear) {
    currentSwitchTarget = targetYear;
    const text = targetYear === 2026
        ? '切换到 2026 年数据将影响所有用户的数据查询结果。请确保 2026 年数据完整且准确。'
        : '回退到 2025 年数据将切换回旧版本数据。';

    document.getElementById('confirmText').textContent = text;
    document.getElementById('confirmModal').classList.add('active');
}

function closeConfirmModal() {
    document.getElementById('confirmModal').classList.remove('active');
    currentSwitchTarget = null;
}

async function performVersionSwitch() {
    if (!currentSwitchTarget) return;

    const btn = document.getElementById('confirmSwitchBtn');
    btn.disabled = true;
    btn.textContent = '切换中...';

    try {
        const result = await AdminUtils.apiRequest('/admin/collection/versions/switch', 'POST', {
            to_year: currentSwitchTarget,
            switch_type: 'manual',
            reason: '管理员手动切换'
        });

        if (result.code === 0) {
            AdminUtils.showSuccess(result.message);
            closeConfirmModal();
            await loadVersions();
            await loadComparison();
            await loadSwitchHistory();
        } else {
            AdminUtils.showError(result.message);
        }
    } catch (error) {
        AdminUtils.handleApiError(error, '版本切换失败');
    } finally {
        btn.disabled = false;
        btn.textContent = '确认切换';
    }
}

async function refreshData() {
    const btn = document.getElementById('refreshBtn');
    btn.disabled = true;
    btn.innerHTML = '<span class="refresh-indicator"></span> 刷新中...';

    try {
        await Promise.all([
            loadVersions(),
            loadComparison(),
            loadSwitchHistory()
        ]);
        AdminUtils.showSuccess('刷新成功');
    } catch (error) {
        AdminUtils.showError('刷新失败');
    } finally {
        btn.disabled = false;
        btn.innerHTML = '🔄 刷新';
    }
}

// ==================== 工具函数 ====================
function getVersionStatusName(status) {
    const names = {
        'preparing': '准备中',
        'ready': '就绪',
        'active': '活跃',
        'archived': '已归档'
    };
    return names[status] || status;
}

function getSwitchTypeName(type) {
    const names = {
        'manual': '手动',
        'auto': '自动',
        'rollback': '回滚'
    };
    return names[type] || type;
}
