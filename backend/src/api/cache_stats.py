"""
缓存统计 API 路由

提供缓存监控和管理接口
"""
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from src.cache.cache_manager import cache_manager
from src.cache.redis_client import get_redis

router = APIRouter()


@router.get(
    "/stats",
    summary="获取缓存统计信息",
    description="获取缓存命中率、请求统计等信息"
)
async def get_cache_stats():
    """
    获取缓存统计信息

    Returns:
        缓存统计数据，包括：
        - hits: 缓存命中次数
        - misses: 缓存未命中次数
        - total_requests: 总请求次数
        - hit_rate: 命中率（百分比）
    """
    stats = cache_manager.get_stats()

    # 获取 Redis 服务器信息
    redis_client = get_redis()
    redis_info = await redis_client.get_info()

    return {
        "success": True,
        "data": {
            "cache_stats": stats,
            "redis_info": {
                "used_memory": redis_info.get("used_memory_human", "N/A"),
                "connected_clients": redis_info.get("connected_clients", 0),
                "uptime_in_days": redis_info.get("uptime_in_days", 0),
                "total_commands_processed": redis_info.get("total_commands_processed", 0),
            }
        },
        "message": "缓存统计信息获取成功"
    }


@router.post(
    "/stats/reset",
    summary="重置缓存统计",
    description="重置缓存命中率等统计信息"
)
async def reset_cache_stats():
    """
    重置缓存统计信息

    仅重置应用层的统计计数器，不影响 Redis 数据
    """
    cache_manager.reset_stats()

    return {
        "success": True,
        "message": "缓存统计已重置"
    }


@router.delete(
    "/clear",
    summary="清除所有缓存",
    description="清除所有应用缓存（谨慎使用）",
    status_code=status.HTTP_200_OK
)
async def clear_all_cache():
    """
    清除所有缓存

    **警告**: 此操作会清除所有缓存数据，可能导致短期性能下降
    """
    redis_client = get_redis()
    deleted_count = await redis_client.clear_pattern("genshin:*")

    return {
        "success": True,
        "data": {
            "deleted_count": deleted_count
        },
        "message": f"已清除 {deleted_count} 个缓存键"
    }


@router.delete(
    "/clear/{pattern}",
    summary="按模式清除缓存",
    description="根据指定模式清除缓存"
)
async def clear_cache_by_pattern(pattern: str):
    """
    按模式清除缓存

    Args:
        pattern: 缓存键模式（支持通配符 *）

    Examples:
        - `characters:*` - 清除所有角色相关缓存
        - `weapons:list:*` - 清除所有武器列表缓存
        - `*:detail:123` - 清除ID为123的所有详情缓存
    """
    deleted_count = await cache_manager.invalidate_pattern(pattern)

    return {
        "success": True,
        "data": {
            "pattern": pattern,
            "deleted_count": deleted_count
        },
        "message": f"已清除匹配模式 '{pattern}' 的 {deleted_count} 个缓存键"
    }


@router.get(
    "/health",
    summary="检查缓存服务健康状态",
    description="检查 Redis 连接状态"
)
async def check_cache_health():
    """
    检查缓存服务健康状态

    Returns:
        Redis 连接状态和服务信息
    """
    redis_client = get_redis()

    try:
        # 尝试 ping Redis
        await redis_client.client.ping()
        is_healthy = True
        message = "Redis 服务正常"
    except Exception as e:
        is_healthy = False
        message = f"Redis 服务异常: {str(e)}"

    return {
        "success": is_healthy,
        "data": {
            "healthy": is_healthy,
            "service": "Redis",
        },
        "message": message
    }
