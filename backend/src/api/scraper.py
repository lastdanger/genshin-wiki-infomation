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
from ..scrapers.weapon_scraper import WeaponScraper
from ..scrapers.artifact_scraper import ArtifactScraper
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


class WeaponScraperRequest(BaseModel):
    """武器爬虫请求模型"""

    weapon_names: Optional[List[str]] = Field(
        None,
        description="可选的武器名称列表（中文）。如果不提供，将爬取所有默认武器",
        example=["风鹰剑", "天空之刃", "狼的末路"]
    )


class ArtifactScraperRequest(BaseModel):
    """圣遗物爬虫请求模型"""

    artifact_set_names: Optional[List[str]] = Field(
        None,
        description="可选的圣遗物套装名称列表（中文）。如果不提供，将爬取所有默认套装",
        example=["炽烈的炎之魔女", "绝缘之旗印", "深林的记忆"]
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


@router.post("/weapons/trigger", summary="手动触发武器数据爬取")
async def trigger_weapon_scraping(
    background_tasks: BackgroundTasks,
    request: Optional[WeaponScraperRequest] = None,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    手动触发武器数据爬取

    爬取流程：
    1. 从数据源爬取武器列表（可指定或使用默认武器列表）
    2. 爬取每个武器的详细信息
    3. 存储到数据库（增量更新）

    Args:
        request: 可选的请求体，包含要爬取的武器列表
            - 如果提供 weapon_names，则只爬取指定武器
            - 如果不提供，则爬取所有默认武器（42个5星武器）

    Returns:
        任务状态信息
    """
    if _scraper_status["is_running"]:
        raise HTTPException(
            status_code=409,
            detail="Scraper is already running. Please wait for it to complete."
        )

    weapon_names = request.weapon_names if request else None
    background_tasks.add_task(run_weapon_scraping, db, weapon_names)

    weapon_count = len(weapon_names) if weapon_names else "all (42)"

    return {
        "success": True,
        "message": f"Weapon scraping task started in background for {weapon_count} weapons",
        "status": "started",
        "weapon_count": len(weapon_names) if weapon_names else 42,
    }


async def run_weapon_scraping(db: AsyncSession, weapon_names: Optional[List[str]] = None):
    """执行武器数据爬取的后台任务"""
    from datetime import datetime

    weapon_count = len(weapon_names) if weapon_names else "all"
    logger.info(f"Starting weapon scraping task for {weapon_count} weapons...")

    _scraper_status["is_running"] = True
    _scraper_status["current_task"] = "weapons"
    _scraper_status["last_run"] = datetime.utcnow().isoformat()

    try:
        config = ScraperConfig(
            requests_per_second=1.0,
            max_retries=3,
            timeout_seconds=30,
        )
        scraper = WeaponScraper(config)
        storage = DataStorageService(db)

        async with scraper:
            logger.info("Scraping weapon data...")
            weapons = await scraper.scrape(weapon_names)

            logger.info(f"Scraped {len(weapons)} weapons")
            scraper_stats = scraper.get_stats()

            logger.info("Storing weapon data...")
            storage_stats = await storage.store_weapons(weapons)

            _scraper_status["last_result"] = {
                "success": True,
                "scraper_stats": scraper_stats,
                "storage_stats": storage_stats,
                "total_weapons": len(weapons),
                "requested_weapons": len(weapon_names) if weapon_names else "all",
            }

            logger.info(f"Weapon scraping completed successfully. Stats: {scraper_stats}, {storage_stats}")

    except Exception as e:
        logger.error(f"Error during weapon scraping: {e}", exc_info=True)
        _scraper_status["last_result"] = {
            "success": False,
            "error": str(e),
        }

    finally:
        _scraper_status["is_running"] = False
        _scraper_status["current_task"] = None


@router.post("/artifacts/trigger", summary="手动触发圣遗物数据爬取")
async def trigger_artifact_scraping(
    background_tasks: BackgroundTasks,
    request: Optional[ArtifactScraperRequest] = None,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    手动触发圣遗物数据爬取

    爬取流程：
    1. 从数据源爬取圣遗物套装列表（可指定或使用默认套装列表）
    2. 爬取每个套装的详细信息
    3. 存储到数据库（增量更新）

    Args:
        request: 可选的请求体，包含要爬取的套装列表
            - 如果提供 artifact_set_names，则只爬取指定套装
            - 如果不提供，则爬取所有默认套装（28个5星套装）

    Returns:
        任务状态信息
    """
    if _scraper_status["is_running"]:
        raise HTTPException(
            status_code=409,
            detail="Scraper is already running. Please wait for it to complete."
        )

    artifact_set_names = request.artifact_set_names if request else None
    background_tasks.add_task(run_artifact_scraping, db, artifact_set_names)

    artifact_count = len(artifact_set_names) if artifact_set_names else "all (28)"

    return {
        "success": True,
        "message": f"Artifact scraping task started in background for {artifact_count} sets",
        "status": "started",
        "artifact_count": len(artifact_set_names) if artifact_set_names else 28,
    }


async def run_artifact_scraping(db: AsyncSession, artifact_set_names: Optional[List[str]] = None):
    """执行圣遗物数据爬取的后台任务"""
    from datetime import datetime

    artifact_count = len(artifact_set_names) if artifact_set_names else "all"
    logger.info(f"Starting artifact scraping task for {artifact_count} sets...")

    _scraper_status["is_running"] = True
    _scraper_status["current_task"] = "artifacts"
    _scraper_status["last_run"] = datetime.utcnow().isoformat()

    try:
        config = ScraperConfig(
            requests_per_second=1.0,
            max_retries=3,
            timeout_seconds=30,
        )
        scraper = ArtifactScraper(config)
        storage = DataStorageService(db)

        async with scraper:
            logger.info("Scraping artifact data...")
            artifacts = await scraper.scrape(artifact_set_names)

            logger.info(f"Scraped {len(artifacts)} artifact sets")
            scraper_stats = scraper.get_stats()

            logger.info("Storing artifact data...")
            storage_stats = await storage.store_artifacts(artifacts)

            _scraper_status["last_result"] = {
                "success": True,
                "scraper_stats": scraper_stats,
                "storage_stats": storage_stats,
                "total_artifacts": len(artifacts),
                "requested_artifacts": len(artifact_set_names) if artifact_set_names else "all",
            }

            logger.info(f"Artifact scraping completed successfully. Stats: {scraper_stats}, {storage_stats}")

    except Exception as e:
        logger.error(f"Error during artifact scraping: {e}", exc_info=True)
        _scraper_status["last_result"] = {
            "success": False,
            "error": str(e),
        }

    finally:
        _scraper_status["is_running"] = False
        _scraper_status["current_task"] = None
