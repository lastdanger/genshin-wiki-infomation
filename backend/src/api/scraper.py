"""
Scraper management API endpoints.

Provides endpoints to:
- Trigger character data scraping manually
- Check scraper status
- View scraping statistics
- Configure scraper settings
"""

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.session import get_db
from ..scrapers.character_scraper import CharacterScraper
from ..scrapers.base_scraper import ScraperConfig
from ..scrapers.data_storage import DataStorageService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/scraper")


# Request/Response models
class ScraperRequest(BaseModel):
    """Request model for triggering scraper with optional character list."""

    character_names: Optional[List[str]] = Field(
        None,
        description="Optional list of character names (Chinese) to scrape. If not provided, will scrape all characters.",
        example=["琴", "迪卢克", "莫娜", "温迪"]
    )


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
    request: Optional[ScraperRequest] = None,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    手动触发角色数据爬取。

    爬取流程：
    1. 从数据源爬取角色列表（可指定或使用默认全部角色）
    2. 爬取每个角色的详细信息
    3. 存储到数据库（增量更新）

    Args:
        request: 可选的请求体，包含要爬取的角色列表
            - 如果提供 character_names，则只爬取指定角色
            - 如果不提供，则爬取所有默认角色（76个）

    Returns:
        任务状态信息

    Example:
        ```bash
        # 爬取所有角色
        curl -X POST http://localhost:8002/api/scraper/characters/trigger

        # 爬取指定角色
        curl -X POST http://localhost:8002/api/scraper/characters/trigger \\
          -H "Content-Type: application/json" \\
          -d '{"character_names": ["琴", "迪卢克", "莫娜"]}'
        ```
    """
    if _scraper_status["is_running"]:
        raise HTTPException(
            status_code=409,
            detail="Scraper is already running. Please wait for it to complete."
        )

    # Extract character names from request
    character_names = request.character_names if request else None

    # Add scraping task to background
    background_tasks.add_task(run_character_scraping, db, character_names)

    character_count = len(character_names) if character_names else "all (76)"

    return {
        "success": True,
        "message": f"Character scraping task started in background for {character_count} characters",
        "status": "started",
        "character_count": len(character_names) if character_names else 76,
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


async def run_character_scraping(db: AsyncSession, character_names: Optional[List[str]] = None):
    """
    执行角色数据爬取的后台任务。

    Args:
        db: Database session
        character_names: Optional list of character names to scrape.
                        If None, will scrape all default characters.
    """
    from datetime import datetime

    character_count = len(character_names) if character_names else "all"
    logger.info(f"Starting character scraping task for {character_count} characters...")

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
            # Pass character_names parameter
            characters = await scraper.scrape(character_names)

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
                "requested_characters": len(character_names) if character_names else "all",
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
