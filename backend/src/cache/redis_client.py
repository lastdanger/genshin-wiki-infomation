"""
Redis 客户端和连接管理

提供 Redis 连接池和基础操作封装
"""
import json
import pickle
from typing import Any, Optional, Union
from datetime import timedelta

import redis.asyncio as aioredis
import structlog
from redis.asyncio.connection import ConnectionPool

from src.config import get_settings
from src.utils.exceptions import ExternalAPIException

logger = structlog.get_logger()
settings = get_settings()


class RedisClient:
    """Redis 异步客户端封装"""

    def __init__(self):
        self._pool: Optional[ConnectionPool] = None
        self._client: Optional[aioredis.Redis] = None

    async def init_connection(self) -> None:
        """初始化Redis连接"""
        try:
            # 解析Redis URL
            self._pool = aioredis.ConnectionPool.from_url(
                settings.redis_url,
                encoding="utf-8",
                decode_responses=False,  # 我们会手动处理编码
                max_connections=20,
                retry_on_timeout=True,
            )

            self._client = aioredis.Redis(connection_pool=self._pool)

            # 测试连接
            await self._client.ping()
            logger.info("Redis连接初始化成功", url=settings.redis_url)

        except Exception as e:
            logger.error("Redis连接初始化失败", error=str(e))
            raise ExternalAPIException("Redis", "连接失败") from e

    async def close_connection(self) -> None:
        """关闭Redis连接"""
        if self._client:
            await self._client.close()
            logger.info("Redis连接已关闭")

    @property
    def client(self) -> aioredis.Redis:
        """获取Redis客户端实例"""
        if not self._client:
            raise RuntimeError("Redis客户端未初始化，请先调用 init_connection()")
        return self._client

    async def get(self, key: str, default: Any = None) -> Any:
        """
        获取缓存值

        Args:
            key: 缓存键
            default: 默认值

        Returns:
            缓存的值或默认值
        """
        try:
            value = await self.client.get(key)
            if value is None:
                return default

            # 尝试反序列化
            try:
                return pickle.loads(value)
            except (pickle.UnpicklingError, TypeError):
                # 回退到字符串
                return value.decode('utf-8') if isinstance(value, bytes) else value

        except Exception as e:
            logger.warning("获取缓存失败", key=key, error=str(e))
            return default

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[Union[int, timedelta]] = None
    ) -> bool:
        """
        设置缓存值

        Args:
            key: 缓存键
            value: 缓存值
            ttl: 过期时间（秒或timedelta对象）

        Returns:
            操作是否成功
        """
        try:
            # 序列化值
            if isinstance(value, (str, int, float, bool)):
                serialized_value = str(value).encode('utf-8')
            else:
                serialized_value = pickle.dumps(value)

            # 设置过期时间
            expire_time = None
            if ttl:
                if isinstance(ttl, timedelta):
                    expire_time = int(ttl.total_seconds())
                else:
                    expire_time = ttl

            result = await self.client.set(key, serialized_value, ex=expire_time)
            return bool(result)

        except Exception as e:
            logger.error("设置缓存失败", key=key, error=str(e))
            return False

    async def delete(self, *keys: str) -> int:
        """
        删除缓存键

        Args:
            keys: 要删除的键列表

        Returns:
            删除的键数量
        """
        try:
            if keys:
                return await self.client.delete(*keys)
            return 0
        except Exception as e:
            logger.error("删除缓存失败", keys=keys, error=str(e))
            return 0

    async def exists(self, *keys: str) -> int:
        """
        检查键是否存在

        Args:
            keys: 要检查的键列表

        Returns:
            存在的键数量
        """
        try:
            return await self.client.exists(*keys)
        except Exception as e:
            logger.error("检查缓存存在性失败", keys=keys, error=str(e))
            return 0

    async def expire(self, key: str, seconds: int) -> bool:
        """
        设置键的过期时间

        Args:
            key: 缓存键
            seconds: 过期时间（秒）

        Returns:
            操作是否成功
        """
        try:
            return await self.client.expire(key, seconds)
        except Exception as e:
            logger.error("设置过期时间失败", key=key, seconds=seconds, error=str(e))
            return False

    async def ttl(self, key: str) -> int:
        """
        获取键的剩余生存时间

        Args:
            key: 缓存键

        Returns:
            剩余秒数，-1表示永不过期，-2表示不存在
        """
        try:
            return await self.client.ttl(key)
        except Exception as e:
            logger.error("获取TTL失败", key=key, error=str(e))
            return -2

    async def clear_pattern(self, pattern: str) -> int:
        """
        删除匹配模式的所有键

        Args:
            pattern: 匹配模式（支持通配符*）

        Returns:
            删除的键数量
        """
        try:
            keys = []
            async for key in self.client.scan_iter(match=pattern):
                keys.append(key)

            if keys:
                return await self.client.delete(*keys)
            return 0

        except Exception as e:
            logger.error("清除缓存模式失败", pattern=pattern, error=str(e))
            return 0

    async def increment(self, key: str, amount: int = 1) -> int:
        """
        原子性递增

        Args:
            key: 缓存键
            amount: 递增量

        Returns:
            递增后的值
        """
        try:
            return await self.client.incrby(key, amount)
        except Exception as e:
            logger.error("递增操作失败", key=key, amount=amount, error=str(e))
            return 0

    async def get_info(self) -> dict:
        """
        获取Redis服务器信息

        Returns:
            服务器信息字典
        """
        try:
            return await self.client.info()
        except Exception as e:
            logger.error("获取Redis信息失败", error=str(e))
            return {}


# 全局Redis客户端实例
redis_client = RedisClient()


async def init_redis() -> None:
    """初始化Redis连接"""
    await redis_client.init_connection()


async def close_redis() -> None:
    """关闭Redis连接"""
    await redis_client.close_connection()


def get_redis() -> RedisClient:
    """获取Redis客户端实例"""
    return redis_client