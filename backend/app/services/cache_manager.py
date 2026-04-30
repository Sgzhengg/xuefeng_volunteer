"""
推荐结果缓存管理器
实现高性能的缓存策略，优化系统响应时间
"""

from functools import lru_cache
import hashlib
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import os

class RecommendationCacheManager:
    """推荐缓存管理器"""

    def __init__(self):
        # 缓存开关
        self.cache_enabled = os.getenv("CACHE_ENABLED", "true").lower() == "true"
        self.cache_size = int(os.getenv("CACHE_SIZE", "10000"))

        # 缓存统计
        self.cache_hits = 0
        self.cache_misses = 0

    def get_rank_bucket(self, rank: int, bucket_size: int = 500) -> int:
        """
        将位次分桶，减少缓存碎片
        每500位一桶
        """
        return rank // bucket_size

    def get_subjects_tuple(self, subjects: List[str]) -> Tuple[str, ...]:
        """
        将选科转换为元组，用于缓存键
        """
        return tuple(sorted(subjects))

    def get_preferences_hash(self, preferences: Optional[Dict[str, Any]]) -> str:
        """
        生成偏好设置的哈希值
        """
        if not preferences:
            return "default"

        # 将偏好转换为字符串并哈希
        pref_str = str(sorted(preferences.items()))
        return hashlib.md5(pref_str.encode()).hexdigest()[:8]

    def generate_cache_key(
        self,
        province: str,
        rank_bucket: int,
        subjects_tuple: Tuple[str, ...],
        pref_hash: str
    ) -> str:
        """
        生成缓存键
        格式: {province}_{rank_bucket}_{subjects_hash}_{pref_hash}
        """
        subjects_hash = hashlib.md5(str(subjects_tuple).encode()).hexdigest()[:8]
        return f"{province}_{rank_bucket}_{subjects_hash}_{pref_hash}"

    @lru_cache(maxsize=10000)
    def cached_recommendation(
        self,
        province: str,
        rank_bucket: int,
        subjects_tuple: Tuple[str, ...],
        pref_hash: str,
        score: int,
        target_majors: List[str]
    ) -> Optional[Dict[str, Any]]:
        """
        缓存的推荐结果
        注意：score和target_majors不在缓存键中，用于验证缓存是否适用
        """
        # 这个方法会被LRU缓存自动管理
        # 实际的缓存逻辑在下面的方法中
        pass

    def get_from_cache(
        self,
        province: str,
        rank: int,
        subjects: List[str],
        preferences: Optional[Dict[str, Any]],
        score: int,
        target_majors: List[str]
    ) -> Optional[Dict[str, Any]]:
        """
        从缓存获取推荐结果
        """
        if not self.cache_enabled:
            return None

        rank_bucket = self.get_rank_bucket(rank)
        subjects_tuple = self.get_subjects_tuple(subjects)
        pref_hash = self.get_preferences_hash(preferences)

        cache_key = self.generate_cache_key(
            province, rank_bucket, subjects_tuple, pref_hash
        )

        # 简化的缓存实现（实际应该使用Redis）
        if hasattr(self, '_cache') and cache_key in self._cache:
            self.cache_hits += 1
            cached_data = self._cache[cache_key]

            # 检查缓存是否仍然适用（分数和专业匹配）
            if self._is_cache_applicable(cached_data, score, target_majors):
                return cached_data
            else:
                # 缓存不适用，删除
                del self._cache[cache_key]
                self.cache_misses += 1
                return None

        self.cache_misses += 1
        return None

    def save_to_cache(
        self,
        province: str,
        rank: int,
        subjects: List[str],
        preferences: Optional[Dict[str, Any]],
        score: int,
        target_majors: List[str],
        recommendation: Dict[str, Any]
    ):
        """
        保存推荐结果到缓存
        """
        if not self.cache_enabled:
            return

        rank_bucket = self.get_rank_bucket(rank)
        subjects_tuple = self.get_subjects_tuple(subjects)
        pref_hash = self.get_preferences_hash(preferences)

        cache_key = self.generate_cache_key(
            province, rank_bucket, subjects_tuple, pref_hash
        )

        # 简化的缓存实现
        if not hasattr(self, '_cache'):
            self._cache = {}

        # 限制缓存大小
        if len(self._cache) >= self.cache_size:
            # 删除最旧的缓存项
            oldest_key = next(iter(self._cache))
            del self._cache[oldest_key]

        self._cache[cache_key] = {
            "recommendation": recommendation,
            "score": score,
            "target_majors": target_majors,
            "cached_at": datetime.now().isoformat()
        }

    def _is_cache_applicable(
        self,
        cached_data: Dict[str, Any],
        score: int,
        target_majors: List[str]
    ) -> bool:
        """
        检查缓存是否仍然适用
        """
        # 分数差异不超过10分
        cached_score = cached_data.get("score", 0)
        if abs(cached_score - score) > 10:
            return False

        # 专业列表相同
        cached_majors = cached_data.get("target_majors", [])
        if set(cached_majors) != set(target_majors):
            return False

        return True

    def get_cache_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        total_requests = self.cache_hits + self.cache_misses
        hit_rate = self.cache_hits / total_requests if total_requests > 0 else 0

        return {
            "cache_enabled": self.cache_enabled,
            "cache_size": self.cache_size,
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "hit_rate": f"{hit_rate:.1%}",
            "current_cache_count": len(getattr(self, '_cache', {}))
        }

    def clear_cache(self):
        """清空缓存"""
        if hasattr(self, '_cache'):
            self._cache.clear()
        self.cache_hits = 0
        self.cache_misses = 0


# 全局实例
cache_manager = RecommendationCacheManager()