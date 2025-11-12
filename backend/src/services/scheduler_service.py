"""
定时任务调度服务

使用 APScheduler 实现定时爬取任务
"""
import logging
import asyncio
from datetime import datetime
from typing import Dict, List, Optional
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.job import Job

from src.db.session import get_db
from src.scrapers.weapon_scraper import WeaponScraper
from src.scrapers.artifact_scraper import ArtifactScraper
from src.scrapers.data_storage import DataStorageService

logger = logging.getLogger(__name__)


class SchedulerService:
    """定时任务调度服务"""

    def __init__(self):
        """初始化调度器"""
        self.scheduler = AsyncIOScheduler()
        self.job_history: List[Dict] = []  # 任务执行历史
        self.max_history = 100  # 最多保留100条历史记录

    def start(self):
        """启动调度器"""
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("定时任务调度器已启动")

    def shutdown(self):
        """关闭调度器"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("定时任务调度器已关闭")

    def is_running(self) -> bool:
        """检查调度器是否运行中"""
        return self.scheduler.running

    async def _scrape_weapons_job(self):
        """武器爬取任务"""
        job_id = "scrape_weapons"
        start_time = datetime.now()

        logger.info(f"[{job_id}] 开始执行武器爬取任务")

        try:
            # 初始化爬虫
            scraper = WeaponScraper()
            weapons = await scraper.scrape()

            # 存储到数据库
            stats = {"created": 0, "updated": 0, "skipped": 0, "errors": 0}
            if weapons:
                async for db in get_db():
                    storage_service = DataStorageService(db)
                    stats = await storage_service.store_weapons(weapons)
                    break

            elapsed = (datetime.now() - start_time).total_seconds()

            # 记录历史
            self._add_history({
                "job_id": job_id,
                "job_name": "武器数据爬取",
                "start_time": start_time.isoformat(),
                "end_time": datetime.now().isoformat(),
                "elapsed_seconds": elapsed,
                "status": "success",
                "stats": {
                    "scraped_count": len(weapons),
                    **stats
                }
            })

            logger.info(f"[{job_id}] 任务完成 - 爬取: {len(weapons)}, 新增: {stats['created']}, 更新: {stats['updated']}, 耗时: {elapsed:.2f}秒")

        except Exception as e:
            elapsed = (datetime.now() - start_time).total_seconds()
            logger.error(f"[{job_id}] 任务失败: {str(e)}", exc_info=True)

            # 记录失败历史
            self._add_history({
                "job_id": job_id,
                "job_name": "武器数据爬取",
                "start_time": start_time.isoformat(),
                "end_time": datetime.now().isoformat(),
                "elapsed_seconds": elapsed,
                "status": "failed",
                "error": str(e)
            })

    async def _scrape_artifacts_job(self):
        """圣遗物爬取任务"""
        job_id = "scrape_artifacts"
        start_time = datetime.now()

        logger.info(f"[{job_id}] 开始执行圣遗物爬取任务")

        try:
            # 初始化爬虫
            scraper = ArtifactScraper()
            artifacts = await scraper.scrape()

            # 存储到数据库
            stats = {"created": 0, "updated": 0, "skipped": 0, "errors": 0}
            if artifacts:
                async for db in get_db():
                    storage_service = DataStorageService(db)
                    stats = await storage_service.store_artifacts(artifacts)
                    break

            elapsed = (datetime.now() - start_time).total_seconds()

            # 记录历史
            self._add_history({
                "job_id": job_id,
                "job_name": "圣遗物数据爬取",
                "start_time": start_time.isoformat(),
                "end_time": datetime.now().isoformat(),
                "elapsed_seconds": elapsed,
                "status": "success",
                "stats": {
                    "scraped_count": len(artifacts),
                    **stats
                }
            })

            logger.info(f"[{job_id}] 任务完成 - 爬取: {len(artifacts)}, 新增: {stats['created']}, 更新: {stats['updated']}, 耗时: {elapsed:.2f}秒")

        except Exception as e:
            elapsed = (datetime.now() - start_time).total_seconds()
            logger.error(f"[{job_id}] 任务失败: {str(e)}", exc_info=True)

            # 记录失败历史
            self._add_history({
                "job_id": job_id,
                "job_name": "圣遗物数据爬取",
                "start_time": start_time.isoformat(),
                "end_time": datetime.now().isoformat(),
                "elapsed_seconds": elapsed,
                "status": "failed",
                "error": str(e)
            })

    async def _scrape_all_job(self):
        """完整爬取任务（武器+圣遗物）"""
        job_id = "scrape_all"
        start_time = datetime.now()

        logger.info(f"[{job_id}] 开始执行完整爬取任务")

        try:
            # 先爬取武器
            await self._scrape_weapons_job()

            # 再爬取圣遗物
            await self._scrape_artifacts_job()

            elapsed = (datetime.now() - start_time).total_seconds()

            logger.info(f"[{job_id}] 完整爬取任务完成，总耗时: {elapsed:.2f}秒")

        except Exception as e:
            elapsed = (datetime.now() - start_time).total_seconds()
            logger.error(f"[{job_id}] 完整爬取任务失败: {str(e)}", exc_info=True)

    def _add_history(self, record: Dict):
        """添加任务执行历史"""
        self.job_history.insert(0, record)  # 最新的记录在前

        # 保持历史记录数量限制
        if len(self.job_history) > self.max_history:
            self.job_history = self.job_history[:self.max_history]

    def add_weapons_job(self, cron: str = "0 2 * * *", job_id: str = "weapons_daily"):
        """
        添加武器爬取定时任务

        Args:
            cron: Cron表达式，默认每天凌晨2点执行
            job_id: 任务ID
        """
        trigger = CronTrigger.from_crontab(cron)

        self.scheduler.add_job(
            self._scrape_weapons_job,
            trigger=trigger,
            id=job_id,
            name="武器数据定时爬取",
            replace_existing=True,
            max_instances=1  # 同一时间只允许一个实例运行
        )

        logger.info(f"已添加武器爬取定时任务: {job_id}, cron: {cron}")

    def add_artifacts_job(self, cron: str = "0 3 * * *", job_id: str = "artifacts_daily"):
        """
        添加圣遗物爬取定时任务

        Args:
            cron: Cron表达式，默认每天凌晨3点执行
            job_id: 任务ID
        """
        trigger = CronTrigger.from_crontab(cron)

        self.scheduler.add_job(
            self._scrape_artifacts_job,
            trigger=trigger,
            id=job_id,
            name="圣遗物数据定时爬取",
            replace_existing=True,
            max_instances=1
        )

        logger.info(f"已添加圣遗物爬取定时任务: {job_id}, cron: {cron}")

    def add_full_scrape_job(self, cron: str = "0 2 * * 0", job_id: str = "full_scrape_weekly"):
        """
        添加完整爬取定时任务

        Args:
            cron: Cron表达式，默认每周日凌晨2点执行
            job_id: 任务ID
        """
        trigger = CronTrigger.from_crontab(cron)

        self.scheduler.add_job(
            self._scrape_all_job,
            trigger=trigger,
            id=job_id,
            name="完整数据定时爬取",
            replace_existing=True,
            max_instances=1
        )

        logger.info(f"已添加完整爬取定时任务: {job_id}, cron: {cron}")

    def add_interval_job(self, job_type: str, hours: int = 24, job_id: Optional[str] = None):
        """
        添加间隔执行任务

        Args:
            job_type: 任务类型 (weapons/artifacts/all)
            hours: 间隔小时数
            job_id: 任务ID，默认自动生成
        """
        if job_id is None:
            job_id = f"{job_type}_interval_{hours}h"

        trigger = IntervalTrigger(hours=hours)

        job_func_map = {
            "weapons": self._scrape_weapons_job,
            "artifacts": self._scrape_artifacts_job,
            "all": self._scrape_all_job
        }

        if job_type not in job_func_map:
            raise ValueError(f"Invalid job_type: {job_type}. Must be one of: {list(job_func_map.keys())}")

        job_name_map = {
            "weapons": "武器数据间隔爬取",
            "artifacts": "圣遗物数据间隔爬取",
            "all": "完整数据间隔爬取"
        }

        self.scheduler.add_job(
            job_func_map[job_type],
            trigger=trigger,
            id=job_id,
            name=job_name_map[job_type],
            replace_existing=True,
            max_instances=1
        )

        logger.info(f"已添加{job_name_map[job_type]}任务: {job_id}, 间隔: {hours}小时")

    def remove_job(self, job_id: str) -> bool:
        """
        移除指定任务

        Args:
            job_id: 任务ID

        Returns:
            是否成功移除
        """
        try:
            self.scheduler.remove_job(job_id)
            logger.info(f"已移除任务: {job_id}")
            return True
        except Exception as e:
            logger.error(f"移除任务失败: {job_id}, 错误: {str(e)}")
            return False

    def pause_job(self, job_id: str) -> bool:
        """暂停任务"""
        try:
            self.scheduler.pause_job(job_id)
            logger.info(f"已暂停任务: {job_id}")
            return True
        except Exception as e:
            logger.error(f"暂停任务失败: {job_id}, 错误: {str(e)}")
            return False

    def resume_job(self, job_id: str) -> bool:
        """恢复任务"""
        try:
            self.scheduler.resume_job(job_id)
            logger.info(f"已恢复任务: {job_id}")
            return True
        except Exception as e:
            logger.error(f"恢复任务失败: {job_id}, 错误: {str(e)}")
            return False

    def get_job(self, job_id: str) -> Optional[Dict]:
        """获取任务详情"""
        job = self.scheduler.get_job(job_id)
        if job:
            return self._job_to_dict(job)
        return None

    def get_all_jobs(self) -> List[Dict]:
        """获取所有任务列表"""
        jobs = self.scheduler.get_jobs()
        return [self._job_to_dict(job) for job in jobs]

    def _job_to_dict(self, job: Job) -> Dict:
        """转换Job对象为字典"""
        next_run_time = job.next_run_time.isoformat() if job.next_run_time else None

        return {
            "id": job.id,
            "name": job.name,
            "next_run_time": next_run_time,
            "trigger": str(job.trigger),
            "pending": job.pending
        }

    def get_job_history(self, limit: int = 20) -> List[Dict]:
        """获取任务执行历史"""
        return self.job_history[:limit]

    async def run_job_now(self, job_type: str):
        """
        立即执行一次任务（不影响定时任务）

        Args:
            job_type: 任务类型 (weapons/artifacts/all)
        """
        job_func_map = {
            "weapons": self._scrape_weapons_job,
            "artifacts": self._scrape_artifacts_job,
            "all": self._scrape_all_job
        }

        if job_type not in job_func_map:
            raise ValueError(f"Invalid job_type: {job_type}")

        logger.info(f"手动触发任务: {job_type}")
        await job_func_map[job_type]()


# 全局调度器实例
scheduler_service = SchedulerService()
