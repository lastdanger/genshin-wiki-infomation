"""
Celery 后台任务配置和任务定义

提供数据同步、图片处理、定期维护等后台任务
"""
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from celery import Celery
from celery.schedules import crontab
import structlog

from src.config import get_settings
from src.utils.logging import log_scraper_activity, log_cache_operation

settings = get_settings()
logger = structlog.get_logger()

# 创建Celery应用
celery_app = Celery(
    "genshin_info_tasks",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=[
        "src.services.background_tasks",
        "src.services.data_sync_service",
        "src.scrapers.bilibili_scraper",
        "src.scrapers.genshin_api",
    ]
)

# Celery配置
celery_app.conf.update(
    # 时区设置
    timezone="Asia/Shanghai",
    enable_utc=True,

    # 任务设置
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    result_expires=3600,  # 结果过期时间1小时

    # 任务路由
    task_routes={
        "sync_*": {"queue": "sync"},
        "scrape_*": {"queue": "scraping"},
        "process_*": {"queue": "processing"},
        "cleanup_*": {"queue": "maintenance"},
    },

    # 工作进程设置
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    worker_max_tasks_per_child=1000,

    # 任务重试设置
    task_default_retry_delay=60,  # 默认重试延迟60秒
    task_max_retries=3,

    # 定时任务配置
    beat_schedule={
        # 每6小时同步角色数据
        "sync-characters-data": {
            "task": "sync_characters_data",
            "schedule": crontab(minute=0, hour="*/6"),
            "args": (),
        },
        # 每天同步武器数据
        "sync-weapons-data": {
            "task": "sync_weapons_data",
            "schedule": crontab(minute=30, hour=2),  # 凌晨2:30
            "args": (),
        },
        # 每天同步圣遗物数据
        "sync-artifacts-data": {
            "task": "sync_artifacts_data",
            "schedule": crontab(minute=0, hour=3),  # 凌晨3:00
            "args": (),
        },
        # 每天同步怪物数据
        "sync-monsters-data": {
            "task": "sync_monsters_data",
            "schedule": crontab(minute=30, hour=3),  # 凌晨3:30
            "args": (),
        },
        # 每周同步游戏机制数据
        "sync-game-mechanics-data": {
            "task": "sync_game_mechanics_data",
            "schedule": crontab(minute=0, hour=4, day_of_week=1),  # 每周一凌晨4点
            "args": (),
        },
        # 每天清理过期缓存
        "cleanup-expired-cache": {
            "task": "cleanup_expired_cache",
            "schedule": crontab(minute=0, hour=1),  # 凌晨1点
            "args": (),
        },
        # 每小时更新系统统计
        "update-system-stats": {
            "task": "update_system_stats",
            "schedule": crontab(minute=0),  # 每小时整点
            "args": (),
        },
        # 每天备份重要数据
        "backup-data": {
            "task": "backup_critical_data",
            "schedule": crontab(minute=0, hour=5),  # 凌晨5点
            "args": (),
        },
    }
)


# 数据同步任务
@celery_app.task(bind=True, name="sync_characters_data")
def sync_characters_data(self, force_refresh: bool = False):
    """
    同步角色数据任务

    Args:
        force_refresh: 是否强制刷新
    """
    try:
        logger.info("开始同步角色数据", force_refresh=force_refresh)
        log_scraper_activity("characters_sync", "start", force_refresh=force_refresh)

        # 这里会导入和调用实际的同步逻辑
        # 为了避免循环导入，在任务内部导入
        from src.services.data_sync_service import DataSyncService

        async def run_sync():
            sync_service = DataSyncService()
            return await sync_service.sync_characters(force_refresh=force_refresh)

        # 在新的事件循环中运行异步任务
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(run_sync())
            logger.info("角色数据同步完成", result=result)
            log_scraper_activity("characters_sync", "complete", result=result)
            return result
        finally:
            loop.close()

    except Exception as exc:
        logger.error("角色数据同步失败", error=str(exc))
        log_scraper_activity("characters_sync", "error", error=str(exc))
        # 重试机制
        raise self.retry(exc=exc, countdown=60, max_retries=3)


@celery_app.task(bind=True, name="sync_weapons_data")
def sync_weapons_data(self, force_refresh: bool = False):
    """同步武器数据任务"""
    try:
        logger.info("开始同步武器数据", force_refresh=force_refresh)
        log_scraper_activity("weapons_sync", "start", force_refresh=force_refresh)

        from src.services.data_sync_service import DataSyncService

        async def run_sync():
            sync_service = DataSyncService()
            return await sync_service.sync_weapons(force_refresh=force_refresh)

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(run_sync())
            logger.info("武器数据同步完成", result=result)
            return result
        finally:
            loop.close()

    except Exception as exc:
        logger.error("武器数据同步失败", error=str(exc))
        raise self.retry(exc=exc, countdown=60, max_retries=3)


@celery_app.task(bind=True, name="sync_artifacts_data")
def sync_artifacts_data(self, force_refresh: bool = False):
    """同步圣遗物数据任务"""
    try:
        logger.info("开始同步圣遗物数据", force_refresh=force_refresh)
        log_scraper_activity("artifacts_sync", "start", force_refresh=force_refresh)

        from src.services.data_sync_service import DataSyncService

        async def run_sync():
            sync_service = DataSyncService()
            return await sync_service.sync_artifacts(force_refresh=force_refresh)

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(run_sync())
            logger.info("圣遗物数据同步完成", result=result)
            return result
        finally:
            loop.close()

    except Exception as exc:
        logger.error("圣遗物数据同步失败", error=str(exc))
        raise self.retry(exc=exc, countdown=60, max_retries=3)


@celery_app.task(bind=True, name="sync_monsters_data")
def sync_monsters_data(self, force_refresh: bool = False):
    """同步怪物数据任务"""
    try:
        logger.info("开始同步怪物数据", force_refresh=force_refresh)
        log_scraper_activity("monsters_sync", "start", force_refresh=force_refresh)

        from src.services.data_sync_service import DataSyncService

        async def run_sync():
            sync_service = DataSyncService()
            return await sync_service.sync_monsters(force_refresh=force_refresh)

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(run_sync())
            logger.info("怪物数据同步完成", result=result)
            return result
        finally:
            loop.close()

    except Exception as exc:
        logger.error("怪物数据同步失败", error=str(exc))
        raise self.retry(exc=exc, countdown=60, max_retries=3)


@celery_app.task(bind=True, name="sync_game_mechanics_data")
def sync_game_mechanics_data(self, force_refresh: bool = False):
    """同步游戏机制数据任务"""
    try:
        logger.info("开始同步游戏机制数据", force_refresh=force_refresh)
        log_scraper_activity("game_mechanics_sync", "start", force_refresh=force_refresh)

        from src.services.data_sync_service import DataSyncService

        async def run_sync():
            sync_service = DataSyncService()
            return await sync_service.sync_game_mechanics(force_refresh=force_refresh)

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(run_sync())
            logger.info("游戏机制数据同步完成", result=result)
            return result
        finally:
            loop.close()

    except Exception as exc:
        logger.error("游戏机制数据同步失败", error=str(exc))
        raise self.retry(exc=exc, countdown=60, max_retries=3)


# 图片处理任务
@celery_app.task(bind=True, name="process_uploaded_image")
def process_uploaded_image(self, image_id: int):
    """
    处理上传的图片任务

    Args:
        image_id: 图片ID
    """
    try:
        logger.info("开始处理上传图片", image_id=image_id)

        from src.services.image_service import ImageService

        async def run_process():
            image_service = ImageService()
            return await image_service.process_uploaded_image(image_id)

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(run_process())
            logger.info("图片处理完成", image_id=image_id, result=result)
            return result
        finally:
            loop.close()

    except Exception as exc:
        logger.error("图片处理失败", image_id=image_id, error=str(exc))
        raise self.retry(exc=exc, countdown=30, max_retries=2)


@celery_app.task(bind=True, name="generate_thumbnails")
def generate_thumbnails(self, image_id: int, sizes: List[tuple] = None):
    """
    生成缩略图任务

    Args:
        image_id: 图片ID
        sizes: 缩略图尺寸列表 [(width, height), ...]
    """
    try:
        if sizes is None:
            sizes = [(150, 150), (300, 300), (600, 600)]

        logger.info("开始生成缩略图", image_id=image_id, sizes=sizes)

        from src.services.image_service import ImageService

        async def run_generate():
            image_service = ImageService()
            return await image_service.generate_thumbnails(image_id, sizes)

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(run_generate())
            logger.info("缩略图生成完成", image_id=image_id, result=result)
            return result
        finally:
            loop.close()

    except Exception as exc:
        logger.error("缩略图生成失败", image_id=image_id, error=str(exc))
        raise self.retry(exc=exc, countdown=30, max_retries=2)


# 维护任务
@celery_app.task(name="cleanup_expired_cache")
def cleanup_expired_cache():
    """清理过期缓存任务"""
    try:
        logger.info("开始清理过期缓存")
        log_cache_operation("cleanup", "start")

        from src.cache.cache_manager import cache_manager

        async def run_cleanup():
            # 清理过期的搜索结果
            search_count = await cache_manager.invalidate_pattern("search:*")
            # 清理过期的临时数据
            temp_count = await cache_manager.invalidate_pattern("temp:*")
            return {"search_cleared": search_count, "temp_cleared": temp_count}

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(run_cleanup())
            logger.info("过期缓存清理完成", result=result)
            log_cache_operation("cleanup", "complete", result=result)
            return result
        finally:
            loop.close()

    except Exception as exc:
        logger.error("清理过期缓存失败", error=str(exc))
        return {"error": str(exc)}


@celery_app.task(name="update_system_stats")
def update_system_stats():
    """更新系统统计信息任务"""
    try:
        logger.info("开始更新系统统计")

        from src.services.stats_service import StatsService
        from src.cache.cache_manager import cache_manager

        async def run_update():
            stats_service = StatsService()
            stats = await stats_service.get_system_stats()

            # 更新缓存
            await cache_manager.redis.set(
                "genshin:stats:system",
                stats,
                1800  # 30分钟缓存
            )
            return stats

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(run_update())
            logger.info("系统统计更新完成", result=result)
            return result
        finally:
            loop.close()

    except Exception as exc:
        logger.error("系统统计更新失败", error=str(exc))
        return {"error": str(exc)}


@celery_app.task(name="backup_critical_data")
def backup_critical_data():
    """备份关键数据任务"""
    try:
        logger.info("开始备份关键数据")

        from src.services.backup_service import BackupService

        async def run_backup():
            backup_service = BackupService()
            return await backup_service.create_daily_backup()

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(run_backup())
            logger.info("关键数据备份完成", result=result)
            return result
        finally:
            loop.close()

    except Exception as exc:
        logger.error("数据备份失败", error=str(exc))
        return {"error": str(exc)}


# 手动触发任务的辅助函数
def trigger_data_sync(entity_type: str, force_refresh: bool = False) -> str:
    """
    手动触发数据同步

    Args:
        entity_type: 实体类型 (characters, weapons, artifacts, monsters, game_mechanics)
        force_refresh: 是否强制刷新

    Returns:
        任务ID
    """
    task_map = {
        "characters": sync_characters_data,
        "weapons": sync_weapons_data,
        "artifacts": sync_artifacts_data,
        "monsters": sync_monsters_data,
        "game_mechanics": sync_game_mechanics_data,
    }

    if entity_type not in task_map:
        raise ValueError(f"不支持的实体类型: {entity_type}")

    task = task_map[entity_type]
    result = task.delay(force_refresh=force_refresh)
    logger.info("手动触发数据同步", entity_type=entity_type, task_id=result.id)
    return result.id


def get_task_status(task_id: str) -> Dict:
    """
    获取任务状态

    Args:
        task_id: 任务ID

    Returns:
        任务状态信息
    """
    result = celery_app.AsyncResult(task_id)
    return {
        "task_id": task_id,
        "status": result.status,
        "result": result.result,
        "traceback": result.traceback,
        "ready": result.ready(),
        "successful": result.successful(),
        "failed": result.failed(),
    }