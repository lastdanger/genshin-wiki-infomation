"""
健康检查 API 路由

提供应用健康状态监控和系统信息查询
"""
import time
import psutil
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from src.db.session import get_db
from src.config import get_settings
from src.cache.redis_client import get_redis
from src.utils.logging import LoggerMixin

router = APIRouter()
logger = LoggerMixin()
settings = get_settings()


@router.get(
    "/health",
    summary="基础健康检查",
    description="检查应用基本运行状态"
)
async def health_check():
    """
    基础健康检查

    返回应用的基本运行状态
    """
    return {
        "success": True,
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "1.0.0",
        "message": "原神游戏信息网站 API 运行正常"
    }


@router.get(
    "/health/detailed",
    summary="详细健康检查",
    description="检查应用及其依赖服务的详细状态"
)
async def detailed_health_check(db: AsyncSession = Depends(get_db)):
    """
    详细健康检查

    检查应用及其所有依赖服务的状态：
    - 数据库连接
    - Redis连接
    - 系统资源使用情况
    """
    health_data = {
        "success": True,
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "1.0.0",
        "services": {},
        "system": {}
    }

    # 检查数据库连接
    try:
        start_time = time.time()
        await db.execute(text("SELECT 1"))
        db_response_time = time.time() - start_time

        health_data["services"]["database"] = {
            "status": "healthy",
            "response_time_ms": round(db_response_time * 1000, 2),
            "message": "数据库连接正常"
        }
    except Exception as e:
        health_data["services"]["database"] = {
            "status": "unhealthy",
            "error": str(e),
            "message": "数据库连接失败"
        }
        health_data["status"] = "degraded"
        logger.log_error("数据库健康检查失败", error=e)

    # 检查Redis连接
    try:
        redis_client = get_redis()
        start_time = time.time()
        await redis_client.client.ping()
        redis_response_time = time.time() - start_time

        health_data["services"]["redis"] = {
            "status": "healthy",
            "response_time_ms": round(redis_response_time * 1000, 2),
            "message": "Redis连接正常"
        }
    except Exception as e:
        health_data["services"]["redis"] = {
            "status": "unhealthy",
            "error": str(e),
            "message": "Redis连接失败"
        }
        health_data["status"] = "degraded"
        logger.log_error("Redis健康检查失败", error=e)

    # 系统资源信息
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')

        health_data["system"] = {
            "cpu_usage_percent": cpu_percent,
            "memory": {
                "total_mb": round(memory.total / 1024 / 1024, 2),
                "available_mb": round(memory.available / 1024 / 1024, 2),
                "usage_percent": memory.percent
            },
            "disk": {
                "total_gb": round(disk.total / 1024 / 1024 / 1024, 2),
                "free_gb": round(disk.free / 1024 / 1024 / 1024, 2),
                "usage_percent": round((disk.used / disk.total) * 100, 2)
            }
        }

        # 检查资源使用是否过高
        if cpu_percent > 90 or memory.percent > 90:
            health_data["status"] = "degraded"

    except Exception as e:
        logger.log_error("系统资源检查失败", error=e)

    # 如果有服务不健康，返回503状态码
    if health_data["status"] == "degraded":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=health_data
        )

    return health_data


@router.get(
    "/status",
    summary="应用状态信息",
    description="获取应用的详细状态和配置信息"
)
async def get_status():
    """
    获取应用状态信息

    返回应用的配置和运行状态信息
    """
    return {
        "success": True,
        "data": {
            "application": {
                "name": "原神游戏信息网站 API",
                "version": "1.0.0",
                "environment": settings.environment,
                "debug": settings.debug,
                "timezone": "UTC"
            },
            "runtime": {
                "start_time": datetime.now(timezone.utc).isoformat(),
                "python_version": "3.11+",
                "framework": "FastAPI",
                "database": "PostgreSQL",
                "cache": "Redis"
            },
            "features": {
                "character_system": True,
                "weapon_system": False,  # Phase 5 实现
                "artifact_system": False,  # Phase 6 实现
                "monster_system": False,  # Phase 5 实现
                "image_system": False,  # Phase 7 实现
                "user_system": False,  # Phase 4 实现
                "data_sync": False  # Phase 8 实现
            }
        },
        "message": "状态信息获取成功"
    }


@router.get(
    "/ping",
    summary="简单连接测试",
    description="最简单的连接测试接口"
)
async def ping():
    """简单的ping接口，用于快速连接测试"""
    return {"pong": True, "timestamp": datetime.now(timezone.utc).isoformat()}