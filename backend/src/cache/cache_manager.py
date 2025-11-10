"""
缓存管理器

提供高级缓存操作、装饰器和缓存策略
"""
import asyncio
import hashlib
import json
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Union
from datetime import timedelta

import structlog

from src.cache.redis_client import get_redis
from src.config import get_settings
from src.utils.logging import log_cache_operation

logger = structlog.get_logger()
settings = get_settings()


class CacheManager:
    """缓存管理器"""

    def __init__(self):
        self.redis = get_redis()
        self.default_ttl = settings.redis_cache_ttl
        # 缓存统计
        self._stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "deletes": 0,
        }

    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        """
        生成缓存键

        Args:
            prefix: 键前缀
            *args: 位置参数
            **kwargs: 关键字参数

        Returns:
            生成的缓存键
        """
        # 创建参数字符串
        params = []
        if args:
            params.extend(str(arg) for arg in args)
        if kwargs:
            # 排序确保一致性
            params.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))

        param_str = "|".join(params)

        # 如果参数太长，使用哈希
        if len(param_str) > 100:
            param_hash = hashlib.md5(param_str.encode()).hexdigest()[:16]
            return f"genshin:{prefix}:{param_hash}"
        else:
            return f"genshin:{prefix}:{param_str}"

    async def get_or_set(
        self,
        key: str,
        func: Callable,
        ttl: Optional[int] = None,
        *args,
        **kwargs
    ) -> Any:
        """
        获取缓存或执行函数并设置缓存

        Args:
            key: 缓存键
            func: 要执行的函数
            ttl: 过期时间
            *args: 函数位置参数
            **kwargs: 函数关键字参数

        Returns:
            缓存值或函数执行结果
        """
        # 尝试从缓存获取
        cached_value = await self.redis.get(key)
        if cached_value is not None:
            self._stats["hits"] += 1
            log_cache_operation("hit", key)
            return cached_value

        # 缓存未命中，执行函数
        self._stats["misses"] += 1
        log_cache_operation("miss", key)

        if asyncio.iscoroutinefunction(func):
            result = await func(*args, **kwargs)
        else:
            result = func(*args, **kwargs)

        # 设置缓存
        cache_ttl = ttl or self.default_ttl
        await self.redis.set(key, result, cache_ttl)
        self._stats["sets"] += 1
        log_cache_operation("set", key, ttl=cache_ttl)

        return result

    async def invalidate_pattern(self, pattern: str) -> int:
        """
        根据模式清除缓存

        Args:
            pattern: 缓存键模式

        Returns:
            删除的键数量
        """
        full_pattern = f"genshin:{pattern}"
        deleted_count = await self.redis.clear_pattern(full_pattern)
        log_cache_operation("invalidate_pattern", full_pattern, count=deleted_count)
        return deleted_count

    async def invalidate_entity(self, entity_type: str, entity_id: Optional[int] = None) -> int:
        """
        清除实体相关的缓存

        Args:
            entity_type: 实体类型
            entity_id: 实体ID（可选）

        Returns:
            删除的键数量
        """
        if entity_id:
            pattern = f"{entity_type}:*{entity_id}*"
        else:
            pattern = f"{entity_type}:*"

        return await self.invalidate_pattern(pattern)

    async def warm_up_cache(self, cache_config: Dict[str, Dict]) -> None:
        """
        预热缓存

        Args:
            cache_config: 缓存配置字典
        """
        logger.info("开始缓存预热")

        for cache_name, config in cache_config.items():
            try:
                func = config['function']
                ttl = config.get('ttl', self.default_ttl)
                key = config.get('key', cache_name)

                await self.get_or_set(key, func, ttl)
                logger.debug("缓存预热成功", cache_name=cache_name)

            except Exception as e:
                logger.error("缓存预热失败", cache_name=cache_name, error=str(e))

        logger.info("缓存预热完成")

    def get_stats(self) -> Dict[str, Any]:
        """
        获取缓存统计信息

        Returns:
            统计信息字典
        """
        total_requests = self._stats["hits"] + self._stats["misses"]
        hit_rate = (
            (self._stats["hits"] / total_requests * 100)
            if total_requests > 0
            else 0
        )

        return {
            "hits": self._stats["hits"],
            "misses": self._stats["misses"],
            "sets": self._stats["sets"],
            "deletes": self._stats["deletes"],
            "total_requests": total_requests,
            "hit_rate": round(hit_rate, 2),
        }

    def reset_stats(self) -> None:
        """重置统计信息"""
        self._stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "deletes": 0,
        }
        logger.info("缓存统计已重置")


# 全局缓存管理器实例
cache_manager = CacheManager()


def cached(
    ttl: Optional[Union[int, timedelta]] = None,
    key_prefix: Optional[str] = None,
    invalidate_on_error: bool = False
):
    """
    缓存装饰器

    Args:
        ttl: 缓存过期时间
        key_prefix: 缓存键前缀
        invalidate_on_error: 发生错误时是否清除缓存

    Returns:
        装饰器函数
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # 生成缓存键
            prefix = key_prefix or f"{func.__module__}.{func.__name__}"
            cache_key = cache_manager._generate_key(prefix, *args, **kwargs)

            # 计算TTL
            cache_ttl = None
            if ttl:
                if isinstance(ttl, timedelta):
                    cache_ttl = int(ttl.total_seconds())
                else:
                    cache_ttl = ttl

            try:
                return await cache_manager.get_or_set(
                    cache_key, func, cache_ttl, *args, **kwargs
                )
            except Exception as e:
                if invalidate_on_error:
                    await cache_manager.redis.delete(cache_key)
                    log_cache_operation("invalidate_on_error", cache_key)
                raise e

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # 对于同步函数，需要在异步上下文中运行
            async def async_func():
                return func(*args, **kwargs)

            prefix = key_prefix or f"{func.__module__}.{func.__name__}"
            cache_key = cache_manager._generate_key(prefix, *args, **kwargs)

            cache_ttl = None
            if ttl:
                if isinstance(ttl, timedelta):
                    cache_ttl = int(ttl.total_seconds())
                else:
                    cache_ttl = ttl

            try:
                return asyncio.run(
                    cache_manager.get_or_set(
                        cache_key, async_func, cache_ttl
                    )
                )
            except Exception as e:
                if invalidate_on_error:
                    asyncio.run(cache_manager.redis.delete(cache_key))
                raise e

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


def cache_invalidate(pattern: str):
    """
    缓存失效装饰器

    Args:
        pattern: 要清除的缓存模式

    Returns:
        装饰器函数
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            result = await func(*args, **kwargs)
            # 执行成功后清除相关缓存
            await cache_manager.invalidate_pattern(pattern)
            return result

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            # 执行成功后清除相关缓存
            asyncio.run(cache_manager.invalidate_pattern(pattern))
            return result

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


# 常用缓存键模式
class CacheKeys:
    """缓存键常量"""

    # 角色相关
    CHARACTER_LIST = "characters:list"
    CHARACTER_DETAIL = "characters:detail"
    CHARACTER_SKILLS = "characters:skills"
    CHARACTER_SEARCH = "characters:search"

    # 武器相关
    WEAPON_LIST = "weapons:list"
    WEAPON_DETAIL = "weapons:detail"
    WEAPON_SEARCH = "weapons:search"

    # 圣遗物相关
    ARTIFACT_LIST = "artifacts:list"
    ARTIFACT_DETAIL = "artifacts:detail"
    ARTIFACT_SEARCH = "artifacts:search"

    # 怪物相关
    MONSTER_LIST = "monsters:list"
    MONSTER_DETAIL = "monsters:detail"
    MONSTER_SEARCH = "monsters:search"

    # 游戏机制相关
    GAME_MECHANIC_LIST = "game_mechanics:list"
    GAME_MECHANIC_DETAIL = "game_mechanics:detail"

    # 图片相关
    IMAGE_GALLERY = "images:gallery"
    IMAGE_DETAIL = "images:detail"

    # 搜索相关
    UNIVERSAL_SEARCH = "search:universal"
    SEARCH_SUGGESTIONS = "search:suggestions"

    # 统计相关
    SYSTEM_STATS = "stats:system"
    ENTITY_COUNTS = "stats:counts"

    # 数据源状态
    DATA_SOURCE_STATUS = "datasource:status"


# 缓存预热配置
CACHE_WARMUP_CONFIG = {
    "system_stats": {
        "key": CacheKeys.SYSTEM_STATS,
        "ttl": 1800,  # 30分钟
    },
    "popular_characters": {
        "key": f"{CacheKeys.CHARACTER_LIST}:popular",
        "ttl": 3600,  # 1小时
    },
    "latest_weapons": {
        "key": f"{CacheKeys.WEAPON_LIST}:latest",
        "ttl": 3600,  # 1小时
    },
}