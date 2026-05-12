-- ============================================
-- 数据采集与版本控制相关表
-- 创建日期: 2026-05-12
-- 描述: 支持数据采集任务管理和版本切换
-- ============================================

-- 采集任务表
CREATE TABLE IF NOT EXISTS collection_tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_name VARCHAR(100) NOT NULL,
    task_type VARCHAR(50) NOT NULL,  -- 'universities', 'admission_data', 'majors'
    year INTEGER NOT NULL,
    province VARCHAR(50),
    status VARCHAR(20) NOT NULL DEFAULT 'pending',  -- 'pending', 'running', 'success', 'failed', 'cancelled'
    progress INTEGER DEFAULT 0,  -- 0-100
    total_items INTEGER DEFAULT 0,
    processed_items INTEGER DEFAULT 0,
    error_count INTEGER DEFAULT 0,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    error_message TEXT,
    result_summary TEXT,  -- JSON格式的结果摘要
    created_by VARCHAR(50) DEFAULT 'admin'
);

-- 采集日志表
CREATE TABLE IF NOT EXISTS collection_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL,
    log_level VARCHAR(20) NOT NULL,  -- 'INFO', 'WARNING', 'ERROR', 'DEBUG'
    message TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    extra_data TEXT,  -- JSON格式的额外数据
    FOREIGN KEY (task_id) REFERENCES collection_tasks(id) ON DELETE CASCADE
);

-- 版本控制表
CREATE TABLE IF NOT EXISTS data_versions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    year INTEGER NOT NULL UNIQUE,
    is_active BOOLEAN DEFAULT 0,  -- 是否为当前活跃版本
    status VARCHAR(50) NOT NULL DEFAULT 'preparing',  -- 'preparing', 'ready', 'active', 'archived'
    data completeness INTEGER DEFAULT 0,  -- 数据完整度百分比
    university_count INTEGER DEFAULT 0,
    major_count INTEGER DEFAULT 0,
    province_coverage TEXT,  -- JSON格式，包含各省份的数据状态
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    activated_at TIMESTAMP,
    deactivated_at TIMESTAMP,
    metadata TEXT  -- JSON格式的元数据
);

-- 版本切换历史表
CREATE TABLE IF NOT EXISTS version_switch_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    from_year INTEGER NOT NULL,
    to_year INTEGER NOT NULL,
    switch_type VARCHAR(50) NOT NULL,  -- 'manual', 'auto', 'rollback'
    status VARCHAR(20) NOT NULL,  -- 'success', 'failed', 'partial'
    switched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    switched_by VARCHAR(50) DEFAULT 'system',
    reason TEXT,
    rollback_data TEXT,  -- JSON格式，用于回退
    error_message TEXT
);

-- 数据验证记录表
CREATE TABLE IF NOT EXISTS data_validation_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER,
    year INTEGER NOT NULL,
    validation_type VARCHAR(50) NOT NULL,  -- 'completeness', 'accuracy', 'consistency'
    status VARCHAR(20) NOT NULL DEFAULT 'pending',  -- 'pending', 'running', 'passed', 'failed'
    total_items INTEGER DEFAULT 0,
    valid_items INTEGER DEFAULT 0,
    invalid_items INTEGER DEFAULT 0,
    issues TEXT,  -- JSON格式的问题列表
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES collection_tasks(id) ON DELETE SET NULL
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_collection_tasks_status ON collection_tasks(status);
CREATE INDEX IF NOT EXISTS idx_collection_tasks_type ON collection_tasks(task_type);
CREATE INDEX IF NOT EXISTS idx_collection_tasks_year ON collection_tasks(year);
CREATE INDEX IF NOT EXISTS idx_collection_logs_task_id ON collection_logs(task_id);
CREATE INDEX IF NOT EXISTS idx_collection_logs_level ON collection_logs(log_level);
CREATE INDEX IF NOT EXISTS idx_data_versions_active ON data_versions(is_active);
CREATE INDEX IF NOT EXISTS idx_data_versions_status ON data_versions(status);
CREATE INDEX IF NOT EXISTS idx_version_switch_history_year ON version_switch_history(from_year, to_year);
CREATE INDEX IF NOT EXISTS idx_data_validation_task ON data_validation_records(task_id);

-- 插入初始版本数据
INSERT OR IGNORE INTO data_versions (year, is_active, status, university_count, major_count, data_completeness, metadata) VALUES
    (2025, 1, 'active', 2800, 45000, 95, '{"data_source": "官方数据", "last_updated": "2025-01-01"}'),
    (2026, 0, 'preparing', 0, 0, 0, '{"data_source": "待采集", "note": "2026年数据准备中"}');
