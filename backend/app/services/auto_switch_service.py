"""
自动版本切换服务
当2026年数据准备就绪时自动切换版本
"""
import logging
from datetime import datetime
from typing import Optional

from app.services.collection_service import get_collection_service

logger = logging.getLogger(__name__)


class AutoSwitchService:
    """自动版本切换服务"""

    def __init__(self):
        self.service = get_collection_service()
        self.auto_switch_enabled = False  # 默认关闭自动切换
        self.required_completeness = 100  # 要求100%完整度
        self.confirmation_required = True  # 是否需要人工确认

    def enable_auto_switch(self, required_completeness: int = 100):
        """
        启用自动切换

        Args:
            required_completeness: 要求的数据完整度百分比
        """
        self.auto_switch_enabled = True
        self.required_completeness = required_completeness
        logger.info(f"自动版本切换已启用，要求完整度: {required_completeness}%")

    def disable_auto_switch(self):
        """禁用自动切换"""
        self.auto_switch_enabled = False
        logger.info("自动版本切换已禁用")

    def check_and_switch(self) -> dict:
        """
        检查2026年数据状态并决定是否切换

        Returns:
            切换结果字典
        """
        if not self.auto_switch_enabled:
            return {
                "action": "skipped",
                "reason": "自动切换未启用"
            }

        # 获取当前活跃版本
        current_version = self.service.get_active_version()
        if not current_version:
            return {
                "action": "skipped",
                "reason": "无法获取当前活跃版本"
            }

        current_year = current_version['year']

        # 如果已经是2026年，无需切换
        if current_year >= 2026:
            return {
                "action": "skipped",
                "reason": f"当前已使用 {current_year} 年数据"
            }

        # 检查2026年版本状态
        version_2026 = self.service.get_version(2026)
        if not version_2026:
            return {
                "action": "skipped",
                "reason": "2026年版本不存在"
            }

        # 检查数据完整度
        completeness = version_2026.get('data_completeness', 0)

        if completeness < self.required_completeness:
            return {
                "action": "skipped",
                "reason": f"2026年数据完整度不足 ({completeness}% < {self.required_completeness}%)"
            }

        # 检查版本状态
        if version_2026.get('status') != 'ready':
            return {
                "action": "skipped",
                "reason": f"2026年版本状态为 {version_2026.get('status')}，非就绪状态"
            }

        # 执行切换
        logger.info("开始自动切换到2026年数据...")
        result = self.service.switch_version(
            to_year=2026,
            switch_type="auto",
            switched_by="system",
            reason=f"自动切换：数据完整度达到 {completeness}%"
        )

        if result["success"]:
            logger.info(f"自动版本切换成功: {current_year} -> 2026")
        else:
            logger.error(f"自动版本切换失败: {result.get('message')}")

        return result

    def get_switch_status(self) -> dict:
        """
        获取自动切换状态

        Returns:
            状态信息
        """
        version_2026 = self.service.get_version(2026)
        current_version = self.service.get_active_version()

        return {
            "auto_switch_enabled": self.auto_switch_enabled,
            "required_completeness": self.required_completeness,
            "current_year": current_version['year'] if current_version else None,
            "version_2026": {
                "status": version_2026.get('status') if version_2026 else None,
                "completeness": version_2026.get('data_completeness', 0) if version_2026 else 0,
                "ready_to_switch": self._is_ready_to_switch()
            } if version_2026 else None
        }

    def _is_ready_to_switch(self) -> bool:
        """检查是否准备好切换"""
        version_2026 = self.service.get_version(2026)
        if not version_2026:
            return False

        return (
            self.auto_switch_enabled and
            version_2026.get('data_completeness', 0) >= self.required_completeness and
            version_2026.get('status') == 'ready'
        )


# 全局服务实例
_auto_switch_service: Optional[AutoSwitchService] = None


def get_auto_switch_service() -> AutoSwitchService:
    """获取自动切换服务单例"""
    global _auto_switch_service
    if _auto_switch_service is None:
        _auto_switch_service = AutoSwitchService()
    return _auto_switch_service


async def scheduled_auto_switch_check():
    """定时执行自动切换检查（由调度器调用）"""
    service = get_auto_switch_service()
    logger.info("执行定时自动切换检查")

    result = service.check_and_switch()

    if result.get("action") == "skipped":
        logger.info(f"自动切换跳过: {result.get('reason')}")
    elif result.get("success"):
        logger.info("自动切换执行成功")
    else:
        logger.error(f"自动切换执行失败: {result.get('message', 'Unknown error')}")
