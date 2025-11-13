"""
定时任务调度 API 路由

提供定时任务的管理、监控等 API 接口
"""
from typing import Optional
from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel, Field

from src.services.scheduler_service import scheduler_service

router = APIRouter()


class JobCreate(BaseModel):
    """创建任务请求"""
    job_type: str = Field(..., description="任务类型: weapons/artifacts/all")
    schedule_type: str = Field(..., description="调度类型: cron/interval")
    cron: Optional[str] = Field(None, description="Cron表达式（schedule_type=cron时必需）")
    interval_hours: Optional[int] = Field(None, description="间隔小时数（schedule_type=interval时必需）")
    job_id: Optional[str] = Field(None, description="自定义任务ID")


class JobTrigger(BaseModel):
    """手动触发任务请求"""
    job_type: str = Field(..., description="任务类型: weapons/artifacts/all")


@router.get("/status")
async def get_scheduler_status():
    """
    获取调度器状态

    返回调度器是否运行中
    """
    is_running = scheduler_service.is_running()
    return {
        "success": True,
        "data": {
            "running": is_running,
            "status": "running" if is_running else "stopped"
        },
        "message": "调度器运行中" if is_running else "调度器已停止"
    }


@router.post("/start")
async def start_scheduler():
    """
    启动调度器

    启动定时任务调度器
    """
    try:
        if scheduler_service.is_running():
            return {
                "success": True,
                "message": "调度器已在运行中"
            }

        scheduler_service.start()
        return {
            "success": True,
            "message": "调度器已启动"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"启动调度器失败: {str(e)}")


@router.post("/stop")
async def stop_scheduler():
    """
    停止调度器

    停止定时任务调度器（所有任务将停止执行）
    """
    try:
        if not scheduler_service.is_running():
            return {
                "success": True,
                "message": "调度器已停止"
            }

        scheduler_service.shutdown()
        return {
            "success": True,
            "message": "调度器已停止"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"停止调度器失败: {str(e)}")


@router.get("/jobs")
async def get_all_jobs():
    """
    获取所有任务列表

    返回当前所有定时任务的信息
    """
    try:
        jobs = scheduler_service.get_all_jobs()
        return {
            "success": True,
            "data": {
                "jobs": jobs,
                "total": len(jobs)
            },
            "message": f"成功获取{len(jobs)}个任务"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取任务列表失败: {str(e)}")


@router.get("/jobs/{job_id}")
async def get_job(job_id: str):
    """
    获取任务详情

    根据任务ID获取任务详细信息
    """
    try:
        job = scheduler_service.get_job(job_id)
        if not job:
            raise HTTPException(status_code=404, detail=f"未找到任务: {job_id}")

        return {
            "success": True,
            "data": job,
            "message": "成功获取任务详情"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取任务详情失败: {str(e)}")


@router.post("/jobs")
async def create_job(job_data: JobCreate):
    """
    创建定时任务

    创建新的定时爬取任务
    """
    try:
        # 验证任务类型
        valid_job_types = ["characters", "weapons", "artifacts", "all"]
        if job_data.job_type not in valid_job_types:
            raise HTTPException(
                status_code=422,
                detail=f"无效的任务类型: {job_data.job_type}. 必须是: {valid_job_types}"
            )

        # 根据调度类型创建任务
        if job_data.schedule_type == "cron":
            if not job_data.cron:
                raise HTTPException(status_code=422, detail="使用cron调度时必须提供cron表达式")

            # 根据任务类型添加任务
            if job_data.job_type == "characters":
                job_id = job_data.job_id or "characters_cron"
                scheduler_service.add_characters_job(cron=job_data.cron, job_id=job_id)
            elif job_data.job_type == "weapons":
                job_id = job_data.job_id or "weapons_cron"
                scheduler_service.add_weapons_job(cron=job_data.cron, job_id=job_id)
            elif job_data.job_type == "artifacts":
                job_id = job_data.job_id or "artifacts_cron"
                scheduler_service.add_artifacts_job(cron=job_data.cron, job_id=job_id)
            else:  # all
                job_id = job_data.job_id or "full_scrape_cron"
                scheduler_service.add_full_scrape_job(cron=job_data.cron, job_id=job_id)

        elif job_data.schedule_type == "interval":
            if not job_data.interval_hours:
                raise HTTPException(status_code=422, detail="使用interval调度时必须提供interval_hours")

            job_id = job_data.job_id
            scheduler_service.add_interval_job(
                job_type=job_data.job_type,
                hours=job_data.interval_hours,
                job_id=job_id
            )
            job_id = job_id or f"{job_data.job_type}_interval_{job_data.interval_hours}h"

        else:
            raise HTTPException(
                status_code=422,
                detail=f"无效的调度类型: {job_data.schedule_type}. 必须是: cron/interval"
            )

        # 获取创建的任务详情
        job = scheduler_service.get_job(job_id)

        return {
            "success": True,
            "data": job,
            "message": f"成功创建任务: {job_id}"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建任务失败: {str(e)}")


@router.delete("/jobs/{job_id}")
async def delete_job(job_id: str):
    """
    删除任务

    根据任务ID删除定时任务
    """
    try:
        success = scheduler_service.remove_job(job_id)
        if not success:
            raise HTTPException(status_code=404, detail=f"未找到任务: {job_id}")

        return {
            "success": True,
            "message": f"成功删除任务: {job_id}"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除任务失败: {str(e)}")


@router.post("/jobs/{job_id}/pause")
async def pause_job(job_id: str):
    """
    暂停任务

    暂停指定的定时任务
    """
    try:
        success = scheduler_service.pause_job(job_id)
        if not success:
            raise HTTPException(status_code=404, detail=f"未找到任务或暂停失败: {job_id}")

        return {
            "success": True,
            "message": f"成功暂停任务: {job_id}"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"暂停任务失败: {str(e)}")


@router.post("/jobs/{job_id}/resume")
async def resume_job(job_id: str):
    """
    恢复任务

    恢复已暂停的定时任务
    """
    try:
        success = scheduler_service.resume_job(job_id)
        if not success:
            raise HTTPException(status_code=404, detail=f"未找到任务或恢复失败: {job_id}")

        return {
            "success": True,
            "message": f"成功恢复任务: {job_id}"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"恢复任务失败: {str(e)}")


@router.post("/jobs/trigger")
async def trigger_job(trigger_data: JobTrigger):
    """
    手动触发任务

    立即执行一次爬取任务（不影响定时任务）
    """
    try:
        valid_job_types = ["characters", "weapons", "artifacts", "all"]
        if trigger_data.job_type not in valid_job_types:
            raise HTTPException(
                status_code=422,
                detail=f"无效的任务类型: {trigger_data.job_type}. 必须是: {valid_job_types}"
            )

        # 异步执行任务
        await scheduler_service.run_job_now(trigger_data.job_type)

        return {
            "success": True,
            "message": f"成功触发{trigger_data.job_type}任务"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"触发任务失败: {str(e)}")


@router.get("/history")
async def get_job_history(
    limit: int = Query(20, ge=1, le=100, description="返回记录数量")
):
    """
    获取任务执行历史

    返回最近的任务执行记录
    """
    try:
        history = scheduler_service.get_job_history(limit)
        return {
            "success": True,
            "data": {
                "history": history,
                "total": len(history)
            },
            "message": f"成功获取{len(history)}条历史记录"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取历史记录失败: {str(e)}")


@router.post("/setup/default")
async def setup_default_jobs():
    """
    设置默认定时任务

    创建默认的定时爬取任务配置：
    - 角色数据：每周日凌晨1点
    - 武器数据：每周日凌晨2点
    - 圣遗物数据：每周日凌晨3点
    """
    try:
        # 添加默认任务（每周日执行）
        scheduler_service.add_characters_job(cron="0 1 * * 0", job_id="characters_weekly")
        scheduler_service.add_weapons_job(cron="0 2 * * 0", job_id="weapons_weekly")
        scheduler_service.add_artifacts_job(cron="0 3 * * 0", job_id="artifacts_weekly")

        # 启动调度器
        if not scheduler_service.is_running():
            scheduler_service.start()

        jobs = scheduler_service.get_all_jobs()

        return {
            "success": True,
            "data": {
                "jobs": jobs,
                "total": len(jobs)
            },
            "message": "成功设置默认定时任务"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"设置默认任务失败: {str(e)}")
