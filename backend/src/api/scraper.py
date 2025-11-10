"""
Scraper management API endpoints.

Provides endpoints to:
- Trigger character data scraping manually
- Check scraper status
- View scraping statistics
- Configure scraper settings
"""

import logging
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.session import get_db
from ..scrapers.character_scraper import CharacterScraper
from ..scrapers.base_scraper import ScraperConfig
from ..scrapers.data_storage import DataStorageService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/scraper")


# Global scraper status
_scraper_status = {
    "is_running": False,
    "current_task": None,
    "last_run": None,
    "last_result": None,
}


@router.post("/characters/trigger", summary="手动触发角色数据爬取")
async def trigger_character_scraping(
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    手动触发角色数据爬取。

    爬取流程：
    1. 从数据源爬取角色列表
    2. 爬取每个角色的详细信息
    3. 存储到数据库（增量更新）

    Returns:
        任务状态信息
    """
    if _scraper_status["is_running"]:
        raise HTTPException(
            status_code=409,
            detail="Scraper is already running. Please wait for it to complete."
        )

    # Add scraping task to background
    background_tasks.add_task(run_character_scraping, db)

    return {
        "success": True,
        "message": "Character scraping task started in background",
        "status": "started",
    }


@router.get("/status", summary="获取爬虫状态")
async def get_scraper_status() -> Dict[str, Any]:
    """
    获取爬虫当前状态。

    Returns:
        爬虫状态信息，包括是否正在运行、最后运行时间、最后结果等
    """
    return {
        "success": True,
        "data": _scraper_status.copy()
    }


@router.get("/stats", summary="获取爬虫统计信息")
async def get_scraper_stats() -> Dict[str, Any]:
    """
    获取爬虫的统计信息。

    Returns:
        统计信息，包括爬取次数、成功率、数据更新情况等
    """
    last_result = _scraper_status.get("last_result", {})

    return {
        "success": True,
        "data": {
            "last_run": _scraper_status.get("last_run"),
            "is_running": _scraper_status.get("is_running"),
            "last_result": last_result,
        }
    }


@router.get("/config", summary="获取爬虫配置")
async def get_scraper_config() -> Dict[str, Any]:
    """
    获取当前爬虫配置。

    Returns:
        爬虫配置信息
    """
    config = ScraperConfig()

    return {
        "success": True,
        "data": {
            "requests_per_second": config.requests_per_second,
            "max_retries": config.max_retries,
            "timeout_seconds": config.timeout_seconds,
            "respect_robots_txt": config.respect_robots_txt,
        }
    }


async def run_character_scraping(db: AsyncSession):
    """
    执行角色数据爬取的后台任务。

    Args:
        db: Database session
    """
    from datetime import datetime

    logger.info("Starting character scraping task...")

    _scraper_status["is_running"] = True
    _scraper_status["current_task"] = "characters"
    _scraper_status["last_run"] = datetime.utcnow().isoformat()

    try:
        # Initialize scraper
        config = ScraperConfig(
            requests_per_second=1.0,
            max_retries=3,
            timeout_seconds=30,
        )
        scraper = CharacterScraper(config)

        # Initialize storage service
        storage = DataStorageService(db)

        # Run scraping
        async with scraper:
            logger.info("Scraping character data...")
            characters = await scraper.scrape()

            logger.info(f"Scraped {len(characters)} characters")
            scraper_stats = scraper.get_stats()

            # Store data
            logger.info("Storing character data...")
            storage_stats = await storage.store_characters(characters)

            # Update status
            _scraper_status["last_result"] = {
                "success": True,
                "scraper_stats": scraper_stats,
                "storage_stats": storage_stats,
                "total_characters": len(characters),
            }

            logger.info(f"Character scraping completed successfully. Stats: {scraper_stats}, {storage_stats}")

    except Exception as e:
        logger.error(f"Error during character scraping: {e}", exc_info=True)
        _scraper_status["last_result"] = {
            "success": False,
            "error": str(e),
        }

    finally:
        _scraper_status["is_running"] = False
        _scraper_status["current_task"] = None
