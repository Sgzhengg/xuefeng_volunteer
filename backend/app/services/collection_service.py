"""
数据采集服务
负责管理数据采集任务、进度跟踪和结果存储
"""
import json
import sqlite3
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Callable
from enum import Enum
import logging

logger = logging.getLogger(__name__)


# 数据目录配置
DATA_DIR = Path("data")
DB_DIR = Path("database")
DB_FILE = DB_DIR / "collection.db"

# 确保目录存在
DATA_DIR.mkdir(exist_ok=True)
DB_DIR.mkdir(exist_ok=True)


class TaskStatus(str, Enum):
    """任务状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskType(str, Enum):
    """任务类型枚举"""
    UNIVERSITIES = "universities"
    ADMISSION_DATA = "admission_data"
    MAJORS = "majors"
    VALIDATION = "validation"


class CollectionService:
    """数据采集服务"""

    def __init__(self, db_path: Path = DB_FILE):
        self.db_path = db_path
        self._init_db()
        self._running_tasks: Dict[int, asyncio.Task] = {}

    def _init_db(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 创建采集任务表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS collection_tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_name VARCHAR(100) NOT NULL,
                task_type VARCHAR(50) NOT NULL,
                year INTEGER NOT NULL,
                province VARCHAR(50),
                status VARCHAR(20) NOT NULL DEFAULT 'pending',
                progress INTEGER DEFAULT 0,
                total_items INTEGER DEFAULT 0,
                processed_items INTEGER DEFAULT 0,
                error_count INTEGER DEFAULT 0,
                started_at TIMESTAMP,
                completed_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                error_message TEXT,
                result_summary TEXT,
                created_by VARCHAR(50) DEFAULT 'admin'
            )
        """)

        # 创建采集日志表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS collection_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER NOT NULL,
                log_level VARCHAR(20) NOT NULL,
                message TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                extra_data TEXT,
                FOREIGN KEY (task_id) REFERENCES collection_tasks(id) ON DELETE CASCADE
            )
        """)

        # 创建版本控制表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS data_versions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                year INTEGER NOT NULL UNIQUE,
                is_active BOOLEAN DEFAULT 0,
                status VARCHAR(50) NOT NULL DEFAULT 'preparing',
                data_completeness INTEGER DEFAULT 0,
                university_count INTEGER DEFAULT 0,
                major_count INTEGER DEFAULT 0,
                province_coverage TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                activated_at TIMESTAMP,
                deactivated_at TIMESTAMP,
                metadata TEXT
            )
        """)

        # 创建版本切换历史表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS version_switch_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                from_year INTEGER NOT NULL,
                to_year INTEGER NOT NULL,
                switch_type VARCHAR(50) NOT NULL,
                status VARCHAR(20) NOT NULL,
                switched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                switched_by VARCHAR(50) DEFAULT 'system',
                reason TEXT,
                rollback_data TEXT,
                error_message TEXT
            )
        """)

        # 创建数据验证记录表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS data_validation_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER,
                year INTEGER NOT NULL,
                validation_type VARCHAR(50) NOT NULL,
                status VARCHAR(20) NOT NULL DEFAULT 'pending',
                total_items INTEGER DEFAULT 0,
                valid_items INTEGER DEFAULT 0,
                invalid_items INTEGER DEFAULT 0,
                issues TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                FOREIGN KEY (task_id) REFERENCES collection_tasks(id) ON DELETE SET NULL
            )
        """)

        # 创建索引
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_collection_tasks_status ON collection_tasks(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_collection_logs_task_id ON collection_logs(task_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_data_versions_active ON data_versions(is_active)")

        # 插入初始版本数据（如果不存在）
        cursor.execute("""
            INSERT OR IGNORE INTO data_versions (year, is_active, status, university_count, major_count, data_completeness, metadata)
            VALUES (2025, 1, 'active', 2800, 45000, 95, '{"data_source": "官方数据", "last_updated": "2025-01-01"}')
        """)
        cursor.execute("""
            INSERT OR IGNORE INTO data_versions (year, is_active, status, university_count, major_count, data_completeness, metadata)
            VALUES (2026, 0, 'preparing', 0, 0, 0, '{"data_source": "待采集", "note": "2026年数据准备中"}')
        """)

        conn.commit()
        conn.close()

    # ==================== 任务管理 ====================

    def create_task(
        self,
        task_name: str,
        task_type: str,
        year: int,
        province: Optional[str] = None,
        created_by: str = "admin"
    ) -> int:
        """创建新的采集任务"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO collection_tasks
            (task_name, task_type, year, province, status, created_by)
            VALUES (?, ?, ?, ?, 'pending', ?)
        """, (task_name, task_type, year, province, created_by))

        task_id = cursor.lastrowid
        conn.commit()
        conn.close()

        self.add_log(task_id, "INFO", f"任务创建成功: {task_name}")

        return task_id

    def get_task(self, task_id: int) -> Optional[Dict]:
        """获取任务详情"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM collection_tasks WHERE id = ?", (task_id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            return dict(row)
        return None

    def list_tasks(
        self,
        status: Optional[str] = None,
        task_type: Optional[str] = None,
        year: Optional[int] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict]:
        """列出任务"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        query = "SELECT * FROM collection_tasks WHERE 1=1"
        params = []

        if status:
            query += " AND status = ?"
            params.append(status)
        if task_type:
            query += " AND task_type = ?"
            params.append(task_type)
        if year:
            query += " AND year = ?"
            params.append(year)

        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    def update_task_status(
        self,
        task_id: int,
        status: TaskStatus,
        progress: Optional[int] = None,
        error_message: Optional[str] = None,
        result_summary: Optional[Dict] = None
    ):
        """更新任务状态"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        updates = ["status = ?", "updated_at = CURRENT_TIMESTAMP"]
        params = [status.value]

        if progress is not None:
            updates.append("progress = ?")
            params.append(progress)

        if error_message:
            updates.append("error_message = ?")
            params.append(error_message)

        if result_summary:
            updates.append("result_summary = ?")
            params.append(json.dumps(result_summary, ensure_ascii=False))

        if status == TaskStatus.RUNNING and not self.get_task(task_id).get("started_at"):
            updates.append("started_at = CURRENT_TIMESTAMP")

        if status in [TaskStatus.SUCCESS, TaskStatus.FAILED, TaskStatus.CANCELLED]:
            updates.append("completed_at = CURRENT_TIMESTAMP")

        params.append(task_id)

        cursor.execute(f"""
            UPDATE collection_tasks
            SET {', '.join(updates)}
            WHERE id = ?
        """, params)

        conn.commit()
        conn.close()

    def update_task_progress(
        self,
        task_id: int,
        processed_items: int,
        total_items: int,
        error_count: int = 0
    ):
        """更新任务进度"""
        progress = int((processed_items / total_items * 100)) if total_items > 0 else 0

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE collection_tasks
            SET progress = ?, processed_items = ?, total_items = ?, error_count = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (progress, processed_items, total_items, error_count, task_id))

        conn.commit()
        conn.close()

    # ==================== 日志管理 ====================

    def add_log(
        self,
        task_id: int,
        level: str,
        message: str,
        extra_data: Optional[Dict] = None
    ):
        """添加日志"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        extra_json = json.dumps(extra_data, ensure_ascii=False) if extra_data else None

        cursor.execute("""
            INSERT INTO collection_logs (task_id, log_level, message, extra_data)
            VALUES (?, ?, ?, ?)
        """, (task_id, level, message, extra_json))

        conn.commit()
        conn.close()

    def get_logs(self, task_id: int, limit: int = 100) -> List[Dict]:
        """获取任务日志"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM collection_logs
            WHERE task_id = ?
            ORDER BY created_at DESC
            LIMIT ?
        """, (task_id, limit))

        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    # ==================== 版本管理 ====================

    def get_version(self, year: int) -> Optional[Dict]:
        """获取指定年份的版本信息"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM data_versions WHERE year = ?", (year,))
        row = cursor.fetchone()
        conn.close()

        if row:
            return dict(row)
        return None

    def get_active_version(self) -> Optional[Dict]:
        """获取当前活跃的版本"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM data_versions WHERE is_active = 1")
        row = cursor.fetchone()
        conn.close()

        if row:
            return dict(row)
        return None

    def list_versions(self) -> List[Dict]:
        """列出所有版本"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM data_versions ORDER BY year DESC")
        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    def update_version(
        self,
        year: int,
        status: Optional[str] = None,
        data_completeness: Optional[int] = None,
        university_count: Optional[int] = None,
        major_count: Optional[int] = None,
        province_coverage: Optional[Dict] = None,
        metadata: Optional[Dict] = None
    ):
        """更新版本信息"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        updates = []
        params = []

        if status:
            updates.append("status = ?")
            params.append(status)

        if data_completeness is not None:
            updates.append("data_completeness = ?")
            params.append(data_completeness)

        if university_count is not None:
            updates.append("university_count = ?")
            params.append(university_count)

        if major_count is not None:
            updates.append("major_count = ?")
            params.append(major_count)

        if province_coverage:
            updates.append("province_coverage = ?")
            params.append(json.dumps(province_coverage, ensure_ascii=False))

        if metadata:
            updates.append("metadata = ?")
            params.append(json.dumps(metadata, ensure_ascii=False))

        if updates:
            params.append(year)
            cursor.execute(f"""
                UPDATE data_versions
                SET {', '.join(updates)}
                WHERE year = ?
            """, params)
            conn.commit()

        conn.close()

    def switch_version(
        self,
        to_year: int,
        switch_type: str = "manual",
        switched_by: str = "admin",
        reason: Optional[str] = None
    ) -> Dict:
        """切换数据版本"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # 获取当前活跃版本
            cursor.execute("SELECT year FROM data_versions WHERE is_active = 1")
            current = cursor.fetchone()
            from_year = current[0] if current else None

            if from_year == to_year:
                return {"success": False, "message": f"版本 {to_year} 已经是当前活跃版本"}

            # 获取目标版本状态
            cursor.execute("SELECT status FROM data_versions WHERE year = ?", (to_year,))
            target = cursor.fetchone()

            if not target:
                return {"success": False, "message": f"版本 {to_year} 不存在"}

            if target[0] != "ready" and target[0] != "active":
                return {"success": False, "message": f"版本 {to_year} 状态为 {target[0]}，无法切换"}

            # 保存回退数据
            rollback_data = json.dumps({"from_year": from_year, "to_year": to_year})

            # 更新版本状态
            now = datetime.now().isoformat()

            # 停用旧版本
            cursor.execute("""
                UPDATE data_versions
                SET is_active = 0, deactivated_at = ?
                WHERE year = ?
            """, (now, from_year))

            # 激活新版本
            cursor.execute("""
                UPDATE data_versions
                SET is_active = 1, activated_at = ?, status = 'active'
                WHERE year = ?
            """, (now, to_year))

            # 记录切换历史
            cursor.execute("""
                INSERT INTO version_switch_history
                (from_year, to_year, switch_type, status, switched_by, reason, rollback_data)
                VALUES (?, ?, ?, 'success', ?, ?, ?)
            """, (from_year, to_year, switch_type, switched_by, reason, rollback_data))

            conn.commit()
            conn.close()

            logger.info(f"版本切换成功: {from_year} -> {to_year}")

            return {
                "success": True,
                "message": f"成功切换到版本 {to_year}",
                "from_year": from_year,
                "to_year": to_year
            }

        except Exception as e:
            conn.rollback()
            conn.close()

            # 记录失败历史
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO version_switch_history
                (from_year, to_year, switch_type, status, switched_by, reason, error_message)
                VALUES (?, ?, ?, 'failed', ?, ?, ?)
            """, (from_year, to_year, switch_type, switched_by, reason, str(e)))
            conn.commit()
            conn.close()

            logger.error(f"版本切换失败: {e}")

            return {
                "success": False,
                "message": f"版本切换失败: {str(e)}"
            }

    def get_switch_history(self, limit: int = 20) -> List[Dict]:
        """获取版本切换历史"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM version_switch_history
            ORDER BY switched_at DESC
            LIMIT ?
        """, (limit,))

        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    # ==================== 数据统计 ====================

    def get_stats(self) -> Dict:
        """获取采集统计信息"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 任务统计
        cursor.execute("""
            SELECT status, COUNT(*) as count
            FROM collection_tasks
            GROUP BY status
        """)
        task_stats = {row[0]: row[1] for row in cursor.fetchall()}

        # 版本统计
        cursor.execute("SELECT COUNT(*) FROM data_versions")
        version_count = cursor.fetchone()[0]

        cursor.execute("SELECT year FROM data_versions WHERE is_active = 1")
        active_year = cursor.fetchone()

        # 今日任务
        cursor.execute("""
            SELECT COUNT(*) FROM collection_tasks
            WHERE DATE(created_at) = DATE('now')
        """)
        today_tasks = cursor.fetchone()[0]

        conn.close()

        return {
            "task_stats": task_stats,
            "version_count": version_count,
            "active_year": active_year[0] if active_year else None,
            "today_tasks": today_tasks
        }


# 全局服务实例
_collection_service: Optional[CollectionService] = None


def get_collection_service() -> CollectionService:
    """获取采集服务单例"""
    global _collection_service
    if _collection_service is None:
        _collection_service = CollectionService()
    return _collection_service
