"""
圣遗物信息 API 路由

提供圣遗物的增删改查、搜索、统计等 API 接口
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import get_db
from src.services.artifact_service import ArtifactService
from src.schemas.artifact import (
    ArtifactCreate, ArtifactUpdate, ArtifactQueryParams, ArtifactResponse,
    ArtifactListResponse, ArtifactDetailResponse, ArtifactSearchResponse, ArtifactStats,
    ArtifactSetResponse
)
from src.utils.exceptions import NotFoundError, ValidationException, DatabaseException
from src.utils.logging import LoggerMixin

router = APIRouter()


def get_artifact_service(db: AsyncSession = Depends(get_db)) -> ArtifactService:
    """获取圣遗物服务实例"""
    return ArtifactService(db)


@router.get("/", response_model=ArtifactListResponse)
async def get_artifacts(
    page: int = Query(1, ge=1, description="页码"),
    per_page: int = Query(20, ge=1, le=100, description="每页数量"),
    set_name: Optional[str] = Query(None, description="套装名称过滤"),
    slot: Optional[str] = Query(None, description="部位过滤"),
    rarity: Optional[int] = Query(None, ge=3, le=5, description="稀有度过滤"),
    source: Optional[str] = Query(None, description="获取方式过滤"),
    main_stat_type: Optional[str] = Query(None, description="主属性类型过滤"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    sort_by: str = Query("name", description="排序字段"),
    sort_order: str = Query("asc", regex="^(asc|desc)$", description="排序方向"),
    artifact_service: ArtifactService = Depends(get_artifact_service)
):
    """
    获取圣遗物列表

    支持分页、过滤、搜索和排序功能
    """
    try:
        params = ArtifactQueryParams(
            page=page,
            per_page=per_page,
            set_name=set_name,
            slot=slot,
            rarity=rarity,
            source=source,
            main_stat_type=main_stat_type,
            search=search,
            sort_by=sort_by,
            sort_order=sort_order
        )

        artifacts, total = await artifact_service.get_artifact_list(params)

        return ArtifactListResponse.create_success(
            artifacts=artifacts,
            total=total,
            page=page,
            per_page=per_page
        )

    except ValidationException as e:
        raise HTTPException(status_code=422, detail=str(e))
    except DatabaseException as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="获取圣遗物列表失败")


@router.get("/{artifact_id}", response_model=ArtifactDetailResponse)
async def get_artifact(
    artifact_id: int = Path(..., gt=0, description="圣遗物ID"),
    artifact_service: ArtifactService = Depends(get_artifact_service)
):
    """
    获取圣遗物详情

    根据圣遗物ID获取详细信息
    """
    try:
        artifact = await artifact_service.get_artifact_by_id(artifact_id)
        return ArtifactDetailResponse.create_success(artifact)

    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DatabaseException as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="获取圣遗物详情失败")


@router.post("/", response_model=ArtifactDetailResponse, status_code=201)
async def create_artifact(
    artifact_data: ArtifactCreate,
    artifact_service: ArtifactService = Depends(get_artifact_service)
):
    """
    创建新圣遗物

    创建一个新的圣遗物条目
    """
    try:
        artifact = await artifact_service.create_artifact(artifact_data)
        return ArtifactDetailResponse.create_success(artifact, "圣遗物创建成功")

    except ValidationException as e:
        raise HTTPException(status_code=422, detail=str(e))
    except DatabaseException as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="创建圣遗物失败")


@router.put("/{artifact_id}", response_model=ArtifactDetailResponse)
async def update_artifact(
    artifact_data: ArtifactUpdate,
    artifact_id: int = Path(..., gt=0, description="圣遗物ID"),
    artifact_service: ArtifactService = Depends(get_artifact_service)
):
    """
    更新圣遗物信息

    根据圣遗物ID更新圣遗物详细信息
    """
    try:
        artifact = await artifact_service.update_artifact(artifact_id, artifact_data)
        return ArtifactDetailResponse.create_success(artifact, "圣遗物更新成功")

    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationException as e:
        raise HTTPException(status_code=422, detail=str(e))
    except DatabaseException as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="更新圣遗物失败")


@router.delete("/{artifact_id}", response_model=dict)
async def delete_artifact(
    artifact_id: int = Path(..., gt=0, description="圣遗物ID"),
    artifact_service: ArtifactService = Depends(get_artifact_service)
):
    """
    删除圣遗物

    根据圣遗物ID删除圣遗物条目
    """
    try:
        success = await artifact_service.delete_artifact(artifact_id)
        return {
            "success": success,
            "message": "圣遗物删除成功"
        }

    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DatabaseException as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="删除圣遗物失败")


@router.get("/search/", response_model=ArtifactSearchResponse)
async def search_artifacts(
    q: str = Query(..., min_length=2, description="搜索关键词"),
    limit: int = Query(20, ge=1, le=50, description="返回结果数量限制"),
    artifact_service: ArtifactService = Depends(get_artifact_service)
):
    """
    搜索圣遗物

    根据关键词搜索圣遗物
    """
    try:
        artifacts = await artifact_service.search_artifacts(q, limit)
        return ArtifactSearchResponse.create_success(artifacts, q)

    except ValidationException as e:
        raise HTTPException(status_code=422, detail=str(e))
    except DatabaseException as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="搜索圣遗物失败")


@router.get("/stats/overview", response_model=ArtifactStats)
async def get_artifact_stats(
    artifact_service: ArtifactService = Depends(get_artifact_service)
):
    """
    获取圣遗物统计信息

    返回圣遗物的各项统计数据
    """
    try:
        stats = await artifact_service.get_artifact_stats()
        return stats

    except DatabaseException as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="获取圣遗物统计失败")


@router.get("/set/{set_name}", response_model=ArtifactSetResponse)
async def get_artifacts_by_set(
    set_name: str = Path(..., description="套装名称"),
    limit: int = Query(20, ge=1, le=50, description="返回结果数量限制"),
    artifact_service: ArtifactService = Depends(get_artifact_service)
):
    """
    根据套装名称获取圣遗物列表

    返回指定套装的圣遗物列表
    """
    try:
        artifacts = await artifact_service.get_artifacts_by_set(set_name, limit)
        return ArtifactSetResponse.create_success(set_name, artifacts)

    except ValidationException as e:
        raise HTTPException(status_code=422, detail=str(e))
    except DatabaseException as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="获取套装圣遗物失败")


@router.get("/slot/{slot}", response_model=ArtifactListResponse)
async def get_artifacts_by_slot(
    slot: str = Path(..., description="圣遗物部位"),
    limit: int = Query(20, ge=1, le=50, description="返回结果数量限制"),
    artifact_service: ArtifactService = Depends(get_artifact_service)
):
    """
    根据部位获取圣遗物列表

    返回指定部位的圣遗物列表
    """
    try:
        artifacts = await artifact_service.get_artifacts_by_slot(slot, limit)
        return ArtifactListResponse.create_success(
            artifacts=artifacts,
            total=len(artifacts),
            page=1,
            per_page=limit,
            slot=slot
        )

    except ValidationException as e:
        raise HTTPException(status_code=422, detail=str(e))
    except DatabaseException as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="获取圣遗物列表失败")


@router.get("/filters/options")
async def get_artifact_filter_options(
    artifact_service: ArtifactService = Depends(get_artifact_service)
):
    """
    获取圣遗物过滤选项

    返回可用的过滤选项，用于前端筛选功能
    """
    try:
        filters = artifact_service.get_available_filters()
        return {
            "success": True,
            "data": filters,
            "message": "获取过滤选项成功"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail="获取过滤选项失败")