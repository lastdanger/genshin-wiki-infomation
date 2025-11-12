"""
完整爬取脚本 - 爬取所有武器和圣遗物数据

执行流程：
1. 爬取所有武器数据并存储到数据库
2. 爬取所有圣遗物数据并存储到数据库
3. 输出统计信息
"""

import asyncio
import logging
import time
from datetime import datetime

from src.db.session import get_db
from src.scrapers.weapon_scraper import WeaponScraper
from src.scrapers.artifact_scraper import ArtifactScraper
from src.scrapers.data_storage import DataStorageService

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def scrape_all_weapons():
    """爬取所有武器数据"""
    logger.info("=" * 80)
    logger.info("开始爬取武器数据")
    logger.info("=" * 80)

    start_time = time.time()

    # 初始化爬虫（不传参数，使用默认完整列表）
    scraper = WeaponScraper()
    weapons = await scraper.scrape()  # 不传参数，获取所有武器

    elapsed_time = time.time() - start_time
    logger.info(f"武器爬取完成，耗时: {elapsed_time:.2f}秒")
    logger.info(f"成功爬取: {len(weapons)} 个武器")

    # 存储到数据库
    if weapons:
        logger.info("\n开始存储武器数据到数据库...")
        async for db in get_db():
            storage_service = DataStorageService(db)
            stats = await storage_service.store_weapons(weapons)

            logger.info(f"武器存储完成:")
            logger.info(f"  新增: {stats['created']}")
            logger.info(f"  更新: {stats['updated']}")
            logger.info(f"  跳过: {stats['skipped']}")
            logger.info(f"  错误: {stats['errors']}")
            break

    return len(weapons), stats if weapons else {"created": 0, "updated": 0, "skipped": 0, "errors": 0}


async def scrape_all_artifacts():
    """爬取所有圣遗物数据"""
    logger.info("\n" + "=" * 80)
    logger.info("开始爬取圣遗物数据")
    logger.info("=" * 80)

    start_time = time.time()

    # 初始化爬虫（不传参数，使用默认完整列表）
    scraper = ArtifactScraper()
    artifacts = await scraper.scrape()  # 不传参数，获取所有圣遗物

    elapsed_time = time.time() - start_time
    logger.info(f"圣遗物爬取完成，耗时: {elapsed_time:.2f}秒")
    logger.info(f"成功爬取: {len(artifacts)} 个圣遗物套装")

    # 存储到数据库
    if artifacts:
        logger.info("\n开始存储圣遗物数据到数据库...")
        async for db in get_db():
            storage_service = DataStorageService(db)
            stats = await storage_service.store_artifacts(artifacts)

            logger.info(f"圣遗物存储完成:")
            logger.info(f"  新增: {stats['created']}")
            logger.info(f"  更新: {stats['updated']}")
            logger.info(f"  跳过: {stats['skipped']}")
            logger.info(f"  错误: {stats['errors']}")
            break

    return len(artifacts), stats if artifacts else {"created": 0, "updated": 0, "skipped": 0, "errors": 0}


async def main():
    """主函数 - 执行完整爬取流程"""
    overall_start = time.time()

    print("\n" + "=" * 80)
    print("原神Wiki数据爬取 - 完整爬取任务")
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    # 1. 爬取武器
    weapon_count, weapon_stats = await scrape_all_weapons()

    # 2. 爬取圣遗物
    artifact_count, artifact_stats = await scrape_all_artifacts()

    # 3. 输出总结
    overall_elapsed = time.time() - overall_start

    print("\n" + "=" * 80)
    print("爬取任务完成")
    print("=" * 80)
    print(f"\n总耗时: {overall_elapsed:.2f}秒 ({overall_elapsed/60:.2f}分钟)")
    print(f"\n武器数据:")
    print(f"  爬取数量: {weapon_count}")
    print(f"  新增: {weapon_stats['created']}")
    print(f"  更新: {weapon_stats['updated']}")
    print(f"  跳过: {weapon_stats['skipped']}")
    print(f"  错误: {weapon_stats['errors']}")

    print(f"\n圣遗物数据:")
    print(f"  爬取数量: {artifact_count}")
    print(f"  新增: {artifact_stats['created']}")
    print(f"  更新: {artifact_stats['updated']}")
    print(f"  跳过: {artifact_stats['skipped']}")
    print(f"  错误: {artifact_stats['errors']}")

    print(f"\n结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
