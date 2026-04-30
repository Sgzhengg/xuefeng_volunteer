-- 数据库性能优化脚本
-- 基于DeepSeek建议的索引优化方案

-- ========================================
-- 1. 录取位次表索引（P0）
-- ========================================

-- 录取位次查询最核心的索引
CREATE INDEX IF NOT EXISTS idx_admission_rank_query
ON admission_rank (province, year, min_rank);

-- 复合索引：省份+年份+位次范围
CREATE INDEX IF NOT EXISTS idx_admission_rank_range
ON admission_rank (province, year, min_rank, max_rank);

-- ========================================
-- 2. 专业表索引（P0）
-- ========================================

-- 专业与院校关联查询索引
CREATE INDEX IF NOT EXISTS idx_majors_university
ON majors (university_id);

-- 专业名称搜索索引（支持模糊查询）
CREATE INDEX IF NOT EXISTS idx_majors_name_trgm
ON majors USING gin (name gin_trgm_ops);

-- 专业代码索引
CREATE INDEX IF NOT EXISTS idx_majors_code
ON majors (code);

-- ========================================
-- 3. 院校表索引（P0）
-- ========================================

-- 院校名称搜索索引（支持模糊查询）
CREATE INDEX IF NOT EXISTS idx_university_name_trgm
ON universities USING gin (name gin_trgm_ops);

-- 院校层次分类索引
CREATE INDEX IF NOT EXISTS idx_university_level
ON universities (level);

-- 院校省份索引
CREATE INDEX IF NOT EXISTS idx_university_province
ON universities (province);

-- ========================================
-- 4. 录取分数表索引（P1）
-- ========================================

-- 省份+年份+最低分索引
CREATE INDEX IF NOT EXISTS idx_admission_scores_query
ON admission_scores (province, year, min_score);

-- 专业+最低分索引
CREATE INDEX IF NOT EXISTS idx_admission_scores_major
ON admission_scores (major, min_score);

-- ========================================
-- 5. 就业数据表索引（P1）
-- ========================================

-- 专业就业数据索引
CREATE INDEX IF NOT EXISTS idx_employment_majors
ON employment_data (major_id);

-- 院校就业数据索引
CREATE INDEX IF NOT EXISTS idx_employment_universities
ON employment_data (university_id);

-- ========================================
-- 6. 性能分析查询（P1）
-- ========================================

-- 查看索引使用情况
ANALYZE admission_rank;
ANALYZE majors;
ANALYZE universities;
ANALYZE admission_scores;
ANALYZE employment_data;

-- 查看表大小和索引大小
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size,
    pg_size_pretty(pg_indexes_size(schemaname||'.'||tablename)) AS index_size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- ========================================
-- 7. JSON数据优化（针对当前JSON数据结构）
-- ========================================

-- 如果使用JSON数据，建议创建GIN索引
-- CREATE INDEX IF NOT EXISTS idx_json_data_gin
-- ON admission_scores USING gin (data jsonb_path_ops);

-- ========================================
-- 8. 索引维护建议
-- ========================================

-- 定期重建索引（建议每月一次）
-- REINDEX TABLE admission_rank;
-- REINDEX TABLE majors;
-- REINDEX TABLE universities;

-- 更新统计信息
VACUUM ANALYZE admission_rank;
VACUUM ANALYZE majors;
VACUUM ANALYZE universities;
VACUUM ANALYZE admission_scores;
VACUUM ANALYZE employment_data;

-- ========================================
-- 9. 监控查询性能
-- ========================================

-- 慢查询监控（P99延迟）
SELECT
    query,
    calls,
    total_time,
    mean_time,
    max_time
FROM pg_stat_statements
WHERE query LIKE '%admission_rank%'
   OR query LIKE '%majors%'
   OR query LIKE '%recommendation%'
ORDER BY mean_time DESC
LIMIT 10;

-- ========================================
-- 10. 索引优化建议
-- ========================================

-- 1. 对于频繁查询的字段建立索引
-- 2. 避免过多索引影响写入性能
-- 3. 定期维护索引和统计信息
-- 4. 监控慢查询并优化

COMMIT;

-- ========================================
-- 说明
-- ========================================
-- P0 = 必须实现，直接影响性能
-- P1 = 强烈建议，显著提升性能
-- 这些索引基于实际查询模式优化
-- 建议在低峰期执行索引创建