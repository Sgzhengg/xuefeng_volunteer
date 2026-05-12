"""
定时任务调度器
支持定时数据采集、版本检查等任务
"""
import asyncio
import logging
from datetime import datetime, time
from typing import Callable, Optional, Dict, List
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class ScheduleType(str, Enum):
    """调度类型"""
    ONCE = "once"  # 一次性任务
    DAILY = "daily"  # 每天执行
    WEEKLY = "weekly"  # 每周执行
    INTERVAL = "interval"  # 间隔执行
    CRON = "cron"  # cron表达式（简化版）


@dataclass
class ScheduledTask:
    """定时任务"""
    task_id: str
    name: str
    func: Callable
    schedule_type: ScheduleType
    enabled: bool = True

    # 执行时间配置
    run_at: Optional[time] = None  # 每天执行时间
    interval_seconds: Optional[int] = None  # 间隔秒数
    weekday: Optional[int] = None  # 星期几（0-6）

    # 状态
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    run_count: int = 0

    # 任务参数
    args: tuple = ()
    kwargs: dict = None

    def __post_init__(self):
        if self.kwargs is None:
            self.kwargs = {}


class TaskScheduler:
    """任务调度器"""

    def __init__(self):
        self.tasks: Dict[str, ScheduledTask] = {}
        self._running = False
        self._task: Optional[asyncio.Task] = None

    def add_task(
        self,
        task_id: str,
        name: str,
        func: Callable,
        schedule_type: ScheduleType = ScheduleType.DAILY,
        run_at: Optional[time] = None,
        interval_seconds: Optional[int] = None,
        weekday: Optional[int] = None,
        enabled: bool = True,
        args: tuple = (),
        kwargs: dict = None
    ) -> ScheduledTask:
        """
        添加定时任务

        Args:
            task_id: 任务ID
            name: 任务名称
            func: 执行函数
            schedule_type: 调度类型
            run_at: 执行时间（每天/每周）
            interval_seconds: 间隔秒数
            weekday: 星期几（0-6，仅weekly模式）
            enabled: 是否启用
            args: 位置参数
            kwargs: 关键字参数

        Returns:
            ScheduledTask: 添加的任务
        """
        task = ScheduledTask(
            task_id=task_id,
            name=name,
            func=func,
            schedule_type=schedule_type,
            run_at=run_at,
            interval_seconds=interval_seconds,
            weekday=weekday,
            enabled=enabled,
            args=args,
            kwargs=kwargs or {}
        )

        # 计算下次执行时间
        task.next_run = self._calculate_next_run(task)

        self.tasks[task_id] = task
        logger.info(f"添加定时任务: {name} ({task_id}), 下次执行: {task.next_run}")

        return task

    def remove_task(self, task_id: str) -> bool:
        """移除任务"""
        if task_id in self.tasks:
            del self.tasks[task_id]
            logger.info(f"移除定时任务: {task_id}")
            return True
        return False

    def enable_task(self, task_id: str) -> bool:
        """启用任务"""
        if task_id in self.tasks:
            self.tasks[task_id].enabled = True
            self.tasks[task_id].next_run = self._calculate_next_run(self.tasks[task_id])
            logger.info(f"启用定时任务: {task_id}")
            return True
        return False

    def disable_task(self, task_id: str) -> bool:
        """禁用任务"""
        if task_id in self.tasks:
            self.tasks[task_id].enabled = False
            self.tasks[task_id].next_run = None
            logger.info(f"禁用定时任务: {task_id}")
            return True
        return False

    def _calculate_next_run(self, task: ScheduledTask) -> Optional[datetime]:
        """计算下次执行时间"""
        if not task.enabled:
            return None

        now = datetime.now()

        if task.schedule_type == ScheduleType.INTERVAL and task.interval_seconds:
            return datetime.fromtimestamp(now.timestamp() + task.interval_seconds)

        elif task.schedule_type == ScheduleType.DAILY and task.run_at:
            next_run = now.replace(
                hour=task.run_at.hour,
                minute=task.run_at.minute,
                second=task.run_at.second,
                microsecond=0
            )
            if next_run <= now:
                # 今天的时间已过，明天执行
                from datetime import timedelta
                next_run += timedelta(days=1)
            return next_run

        elif task.schedule_type == ScheduleType.WEEKLY and task.run_at and task.weekday is not None:
            next_run = now.replace(
                hour=task.run_at.hour,
                minute=task.run_at.minute,
                second=task.run_at.second,
                microsecond=0
            )
            # 计算到下一个指定星期几的天数
            days_ahead = task.weekday - now.weekday()
            if days_ahead <= 0 or (days_ahead == 0 and next_run <= now):
                days_ahead += 7
            from datetime import timedelta
            next_run += timedelta(days=days_ahead)
            return next_run

        return None

    async def _run_task(self, task: ScheduledTask):
        """执行任务"""
        logger.info(f"执行定时任务: {task.name} ({task.task_id})")
        task.last_run = datetime.now()
        task.run_count += 1

        try:
            if asyncio.iscoroutinefunction(task.func):
                await task.func(*task.args, **task.kwargs)
            else:
                task.func(*task.args, **task.kwargs)
            logger.info(f"定时任务执行成功: {task.name}")
        except Exception as e:
            logger.error(f"定时任务执行失败: {task.name}, 错误: {e}")

        # 计算下次执行时间
        task.next_run = self._calculate_next_run(task)

    async def _scheduler_loop(self):
        """调度循环"""
        logger.info("任务调度器启动")

        while self._running:
            now = datetime.now()

            # 检查需要执行的任务
            for task in self.tasks.values():
                if task.enabled and task.next_run and now >= task.next_run:
                    # 在后台执行任务，不阻塞调度器
                    asyncio.create_task(self._run_task(task))

            # 每秒检查一次
            await asyncio.sleep(1)

        logger.info("任务调度器停止")

    async def start(self):
        """启动调度器"""
        if self._running:
            logger.warning("调度器已在运行")
            return

        self._running = True
        self._task = asyncio.create_task(self._scheduler_loop())

    async def stop(self):
        """停止调度器"""
        if not self._running:
            return

        self._running = False

        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    def get_task_status(self, task_id: str) -> Optional[Dict]:
        """获取任务状态"""
        if task_id in self.tasks:
            task = self.tasks[task_id]
            return {
                "task_id": task.task_id,
                "name": task.name,
                "enabled": task.enabled,
                "schedule_type": task.schedule_type.value,
                "last_run": task.last_run.isoformat() if task.last_run else None,
                "next_run": task.next_run.isoformat() if task.next_run else None,
                "run_count": task.run_count
            }
        return None

    def get_all_tasks_status(self) -> List[Dict]:
        """获取所有任务状态"""
        return [self.get_task_status(tid) for tid in self.tasks.keys()]


# ==================== 预定义任务 ====================

async def daily_data_collection():
    """每日数据采集任务"""
    from app.services.collection_service import get_collection_service

    service = get_collection_service()
    logger.info("执行每日数据采集检查")

    # 检查2026年数据状态
    version = service.get_version(2026)
    if version and version.get("status") == "preparing":
        logger.info("2026年数据准备中，继续采集")
        # 这里可以触发具体的采集任务
    else:
        logger.info("2026年数据已就绪或未初始化")


async def auto_version_check():
    """自动版本检查任务"""
    from app.services.collection_service import get_collection_service

    service = get_collection_service()
    logger.info("执行自动版本检查")

    version_2026 = service.get_version(2026)
    if version_2026:
        completeness = version_2026.get("data_completeness", 0)

        # 如果数据完整度达到100%且状态为ready，可以考虑自动切换
        if completeness >= 100 and version_2026.get("status") == "ready":
            logger.info("2026年数据已就绪，可以考虑切换版本")
            # 这里可以根据配置决定是否自动切换


# ==================== 全局调度器实例 =================---

_scheduler: Optional[TaskScheduler] = None


def get_scheduler() -> TaskScheduler:
    """获取调度器单例"""
    global _scheduler
    if _scheduler is None:
        _scheduler = TaskScheduler()

        # 添加预定义任务
        from datetime import time

        # 每日数据采集检查（凌晨2点执行）
        _scheduler.add_task(
            task_id="daily_collection",
            name="每日数据采集检查",
            func=daily_data_collection,
            schedule_type=ScheduleType.DAILY,
            run_at=time(2, 0),
            enabled=False  # 默认禁用，需要手动启用
        )

        # 每日版本检查（上午8点执行）
        _scheduler.add_task(
            task_id="daily_version_check",
            name="每日版本检查",
            func=auto_version_check,
            schedule_type=ScheduleType.DAILY,
            run_at=time(8, 0),
            enabled=False  # 默认禁用
        )

    return _scheduler


async def start_scheduler():
    """启动调度器"""
    scheduler = get_scheduler()
    await scheduler.start()


async def stop_scheduler():
    """停止调度器"""
    global _scheduler
    if _scheduler:
        await _scheduler.stop()
