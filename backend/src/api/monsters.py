"""
怪物信息 API 路由

提供怪物的增删改查、搜索、统计等 API 接口
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import get_db
from src.services.monster_service import MonsterService
from src.schemas.monster import (
    MonsterCreate, MonsterUpdate, MonsterQueryParams, MonsterResponse,
    MonsterListResponse, MonsterDetailResponse, MonsterSearchResponse, MonsterStats,
    MonsterFamilyResponse
)
from src.utils.exceptions import NotFoundError, ValidationException, DatabaseException
from src.utils.logging import LoggerMixin

router = APIRouter()


def get_monster_service(db: AsyncSession = Depends(get_db)) -> MonsterService:
    """获取怪物服务实例"""
    return MonsterService(db)


@router.get("/", response_model=MonsterListResponse)
async def get_monsters(
    page: int = Query(1, ge=1, description="页码"),
    per_page: int = Query(20, ge=1, le=100, description="每页数量"),
    category: Optional[str] = Query(None, description="怪物类别过滤"),
    family: Optional[str] = Query(None, description="怪物族群过滤"),
    element: Optional[str] = Query(None, description="元素属性过滤"),
    level: Optional[int] = Query(None, ge=1, le=100, description="等级过滤"),
    world_level: Optional[int] = Query(None, ge=0, le=8, description="世界等级过滤"),
    region: Optional[str] = Query(None, description="地区过滤"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    sort_by: str = Query("name", description="排序字段"),
    sort_order: str = Query("asc", regex="^(asc|desc)$", description="排序方向"),
    monster_service: MonsterService = Depends(get_monster_service)
):
    """
    获取怪物列表

    支持分页、过滤、搜索和排序功能
    """
    try:
        params = MonsterQueryParams(
            page=page,
            per_page=per_page,
            category=category,
            family=family,
            element=element,
            level=level,
            world_level=world_level,
            region=region,
            search=search,
            sort_by=sort_by,
            sort_order=sort_order
        )

        monsters, total = await monster_service.get_monster_list(params)

        return MonsterListResponse.create_success(
            monsters=monsters,
            total=total,
            page=page,
            per_page=per_page
        )

    except ValidationException as e:
        raise HTTPException(status_code=422, detail=str(e))
    except DatabaseException as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="获取怪物列表失败")


@router.get("/{monster_id}", response_model=MonsterDetailResponse)
async def get_monster(
    monster_id: int = Path(..., gt=0, description="怪物ID"),
    monster_service: MonsterService = Depends(get_monster_service)
):
    """
    获取怪物详情

    根据怪物ID获取详细信息
    """
    try:
        monster = await monster_service.get_monster_by_id(monster_id)
        return MonsterDetailResponse.create_success(monster)

    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DatabaseException as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="获取怪物详情失败")


@router.post("/", response_model=MonsterDetailResponse, status_code=201)
async def create_monster(
    monster_data: MonsterCreate,
    monster_service: MonsterService = Depends(get_monster_service)
):
    """
    创建新怪物

    创建一个新的怪物条目
    """
    try:
        monster = await monster_service.create_monster(monster_data)
        return MonsterDetailResponse.create_success(monster, "怪物创建成功")

    except ValidationException as e:
        raise HTTPException(status_code=422, detail=str(e))
    except DatabaseException as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="创建怪物失败")


@router.put("/{monster_id}", response_model=MonsterDetailResponse)
async def update_monster(
    monster_data: MonsterUpdate,
    monster_id: int = Path(..., gt=0, description="怪物ID"),
    monster_service: MonsterService = Depends(get_monster_service)
):
    """
    更新怪物信息

    根据怪物ID更新怪物详细信息
    """
    try:
        monster = await monster_service.update_monster(monster_id, monster_data)
        return MonsterDetailResponse.create_success(monster, "怪物更新成功")

    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationException as e:
        raise HTTPException(status_code=422, detail=str(e))
    except DatabaseException as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="更新怪物失败")


@router.delete("/{monster_id}", response_model=dict)
async def delete_monster(
    monster_id: int = Path(..., gt=0, description="怪物ID"),
    monster_service: MonsterService = Depends(get_monster_service)
):
    """
    删除怪物

    根据怪物ID删除怪物条目
    """
    try:
        success = await monster_service.delete_monster(monster_id)
        return {
            "success": success,
            "message": "怪物删除成功"
        }

    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DatabaseException as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="删除怪物失败")


@router.get("/search/", response_model=MonsterSearchResponse)
async def search_monsters(
    q: str = Query(..., min_length=2, description="搜索关键词"),
    limit: int = Query(20, ge=1, le=50, description="返回结果数量限制"),
    monster_service: MonsterService = Depends(get_monster_service)
):
    """
    搜索怪物

    根据关键词搜索怪物
    """
    try:
        monsters = await monster_service.search_monsters(q, limit)
        return MonsterSearchResponse.create_success(monsters, q)

    except ValidationException as e:
        raise HTTPException(status_code=422, detail=str(e))
    except DatabaseException as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="搜索怪物失败")


@router.get("/stats/overview", response_model=MonsterStats)
async def get_monster_stats(
    monster_service: MonsterService = Depends(get_monster_service)
):
    """
    获取怪物统计信息

    返回怪物的各项统计数据
    """
    try:
        stats = await monster_service.get_monster_stats()
        return stats

    except DatabaseException as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="获取怪物统计失败")


@router.get("/category/{category}", response_model=MonsterListResponse)
async def get_monsters_by_category(
    category: str = Path(..., description="怪物类别"),
    limit: int = Query(20, ge=1, le=50, description="返回结果数量限制"),
    monster_service: MonsterService = Depends(get_monster_service)
):
    """
    根据类别获取怪物列表

    返回指定类别的怪物列表
    """
    try:
        monsters = await monster_service.get_monsters_by_category(category, limit)
        return MonsterListResponse.create_success(
            monsters=monsters,
            total=len(monsters),
            page=1,
            per_page=limit,
            category=category
        )

    except ValidationException as e:
        raise HTTPException(status_code=422, detail=str(e))
    except DatabaseException as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="获取怪物列表失败")


@router.get("/family/{family}", response_model=MonsterFamilyResponse)
async def get_monsters_by_family(
    family: str = Path(..., description="怪物族群"),
    limit: int = Query(20, ge=1, le=50, description="返回结果数量限制"),
    monster_service: MonsterService = Depends(get_monster_service)
):
    """
    根据族群获取怪物列表

    返回指定族群的怪物列表
    """
    try:
        monsters = await monster_service.get_monsters_by_family(family, limit)
        return MonsterFamilyResponse.create_success(family, monsters)

    except ValidationException as e:
        raise HTTPException(status_code=422, detail=str(e))
    except DatabaseException as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="获取族群怪物失败")


@router.get("/element/{element}", response_model=MonsterListResponse)
async def get_monsters_by_element(
    element: str = Path(..., description="元素类型"),
    limit: int = Query(20, ge=1, le=50, description="返回结果数量限制"),
    monster_service: MonsterService = Depends(get_monster_service)
):
    """
    根据元素类型获取怪物列表

    返回指定元素类型的怪物列表
    """
    try:
        monsters = await monster_service.get_monsters_by_element(element, limit)
        return MonsterListResponse.create_success(
            monsters=monsters,
            total=len(monsters),
            page=1,
            per_page=limit,
            element=element
        )

    except ValidationException as e:
        raise HTTPException(status_code=422, detail=str(e))
    except DatabaseException as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="获取怪物列表失败")


@router.get("/region/{region}", response_model=MonsterListResponse)
async def get_monsters_by_region(
    region: str = Path(..., description="地区名称"),
    limit: int = Query(20, ge=1, le=50, description="返回结果数量限制"),
    monster_service: MonsterService = Depends(get_monster_service)
):
    """
    根据地区获取怪物列表

    返回指定地区的怪物列表
    """
    try:
        monsters = await monster_service.get_monsters_by_region(region, limit)
        return MonsterListResponse.create_success(
            monsters=monsters,
            total=len(monsters),
            page=1,
            per_page=limit,
            region=region
        )

    except ValidationException as e:
        raise HTTPException(status_code=422, detail=str(e))
    except DatabaseException as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="获取怪物列表失败")


@router.get("/level/range", response_model=MonsterListResponse)
async def get_monsters_by_level_range(
    min_level: int = Query(..., ge=1, le=100, description="最小等级"),
    max_level: int = Query(..., ge=1, le=100, description="最大等级"),
    limit: int = Query(20, ge=1, le=50, description="返回结果数量限制"),
    monster_service: MonsterService = Depends(get_monster_service)
):
    """
    根据等级范围获取怪物列表

    返回指定等级范围内的怪物列表
    """
    try:
        if min_level > max_level:
            raise HTTPException(status_code=422, detail="最小等级不能大于最大等级")

        monsters = await monster_service.get_monsters_by_level_range(min_level, max_level, limit)
        return MonsterListResponse.create_success(
            monsters=monsters,
            total=len(monsters),
            page=1,
            per_page=limit,
            level_range=f"{min_level}-{max_level}"
        )

    except ValidationException as e:
        raise HTTPException(status_code=422, detail=str(e))
    except DatabaseException as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="获取怪物列表失败")


@router.get("/filters/options")
async def get_monster_filter_options(
    monster_service: MonsterService = Depends(get_monster_service)
):
    """
    获取怪物过滤选项

    返回可用的过滤选项，用于前端筛选功能
    """
    try:
        filters = monster_service.get_available_filters()
        return {
            "success": True,
            "data": filters,
            "message": "获取过滤选项成功"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail="获取过滤选项失败")