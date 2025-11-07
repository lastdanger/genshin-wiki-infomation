"""
武器信息 API 路由

提供武器的增删改查、搜索、统计等 API 接口
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import get_db
from src.services.weapon_service import WeaponService
from src.schemas.weapon import (
    WeaponCreate, WeaponUpdate, WeaponQueryParams, WeaponResponse,
    WeaponListResponse, WeaponDetailResponse, WeaponSearchResponse, WeaponStats
)
from src.utils.exceptions import NotFoundError, ValidationException, DatabaseException
from src.utils.logging import LoggerMixin

router = APIRouter()


def get_weapon_service(db: AsyncSession = Depends(get_db)) -> WeaponService:
    """获取武器服务实例"""
    return WeaponService(db)


@router.get("/", response_model=WeaponListResponse)
async def get_weapons(
    page: int = Query(1, ge=1, description="页码"),
    per_page: int = Query(20, ge=1, le=100, description="每页数量"),
    weapon_type: Optional[str] = Query(None, description="武器类型过滤"),
    rarity: Optional[int] = Query(None, ge=3, le=5, description="稀有度过滤"),
    source: Optional[str] = Query(None, description="获取方式过滤"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    sort_by: str = Query("name", description="排序字段"),
    sort_order: str = Query("asc", regex="^(asc|desc)$", description="排序方向"),
    weapon_service: WeaponService = Depends(get_weapon_service)
):
    """
    获取武器列表

    支持分页、过滤、搜索和排序功能
    """
    try:
        params = WeaponQueryParams(
            page=page,
            per_page=per_page,
            weapon_type=weapon_type,
            rarity=rarity,
            source=source,
            search=search,
            sort_by=sort_by,
            sort_order=sort_order
        )

        weapons, total = await weapon_service.get_weapon_list(params)

        return WeaponListResponse.create_success(
            weapons=weapons,
            total=total,
            page=page,
            per_page=per_page
        )

    except ValidationException as e:
        raise HTTPException(status_code=422, detail=str(e))
    except DatabaseException as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        import traceback
        error_details = f"获取武器列表失败: {str(e)} - {traceback.format_exc()}"
        print(f"武器API错误: {error_details}")  # 临时调试日志
        raise HTTPException(status_code=500, detail=f"获取武器列表失败: {str(e)}")


@router.get("/{weapon_id}", response_model=WeaponDetailResponse)
async def get_weapon(
    weapon_id: int = Path(..., gt=0, description="武器ID"),
    weapon_service: WeaponService = Depends(get_weapon_service)
):
    """
    获取武器详情

    根据武器ID获取详细信息
    """
    try:
        weapon = await weapon_service.get_weapon_by_id(weapon_id)
        return WeaponDetailResponse.create_success(weapon)

    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DatabaseException as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="获取武器详情失败")


@router.post("/", response_model=WeaponDetailResponse, status_code=201)
async def create_weapon(
    weapon_data: WeaponCreate,
    weapon_service: WeaponService = Depends(get_weapon_service)
):
    """
    创建新武器

    创建一个新的武器条目
    """
    try:
        weapon = await weapon_service.create_weapon(weapon_data)
        return WeaponDetailResponse.create_success(weapon, "武器创建成功")

    except ValidationException as e:
        raise HTTPException(status_code=422, detail=str(e))
    except DatabaseException as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="创建武器失败")


@router.put("/{weapon_id}", response_model=WeaponDetailResponse)
async def update_weapon(
    weapon_data: WeaponUpdate,
    weapon_id: int = Path(..., gt=0, description="武器ID"),
    weapon_service: WeaponService = Depends(get_weapon_service)
):
    """
    更新武器信息

    根据武器ID更新武器详细信息
    """
    try:
        weapon = await weapon_service.update_weapon(weapon_id, weapon_data)
        return WeaponDetailResponse.create_success(weapon, "武器更新成功")

    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationException as e:
        raise HTTPException(status_code=422, detail=str(e))
    except DatabaseException as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="更新武器失败")


@router.delete("/{weapon_id}", response_model=dict)
async def delete_weapon(
    weapon_id: int = Path(..., gt=0, description="武器ID"),
    weapon_service: WeaponService = Depends(get_weapon_service)
):
    """
    删除武器

    根据武器ID删除武器条目
    """
    try:
        success = await weapon_service.delete_weapon(weapon_id)
        return {
            "success": success,
            "message": "武器删除成功"
        }

    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DatabaseException as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="删除武器失败")


@router.get("/search/", response_model=WeaponSearchResponse)
async def search_weapons(
    q: str = Query(..., min_length=2, description="搜索关键词"),
    limit: int = Query(20, ge=1, le=50, description="返回结果数量限制"),
    weapon_service: WeaponService = Depends(get_weapon_service)
):
    """
    搜索武器

    根据关键词搜索武器
    """
    try:
        weapons = await weapon_service.search_weapons(q, limit)
        return WeaponSearchResponse.create_success(weapons, q)

    except ValidationException as e:
        raise HTTPException(status_code=422, detail=str(e))
    except DatabaseException as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="搜索武器失败")


@router.get("/stats/overview", response_model=WeaponStats)
async def get_weapon_stats(
    weapon_service: WeaponService = Depends(get_weapon_service)
):
    """
    获取武器统计信息

    返回武器的各项统计数据
    """
    try:
        stats = await weapon_service.get_weapon_stats()
        return stats

    except DatabaseException as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="获取武器统计失败")


@router.get("/type/{weapon_type}", response_model=WeaponListResponse)
async def get_weapons_by_type(
    weapon_type: str = Path(..., description="武器类型"),
    limit: int = Query(20, ge=1, le=50, description="返回结果数量限制"),
    weapon_service: WeaponService = Depends(get_weapon_service)
):
    """
    根据武器类型获取武器列表

    返回指定类型的武器列表
    """
    try:
        weapons = await weapon_service.get_weapons_by_type(weapon_type, limit)
        return WeaponListResponse.create_success(
            weapons=weapons,
            total=len(weapons),
            page=1,
            per_page=limit,
            weapon_type=weapon_type
        )

    except ValidationException as e:
        raise HTTPException(status_code=422, detail=str(e))
    except DatabaseException as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="获取武器列表失败")


@router.get("/rarity/{rarity}", response_model=WeaponListResponse)
async def get_weapons_by_rarity(
    rarity: int = Path(..., ge=3, le=5, description="武器稀有度"),
    limit: int = Query(20, ge=1, le=50, description="返回结果数量限制"),
    weapon_service: WeaponService = Depends(get_weapon_service)
):
    """
    根据稀有度获取武器列表

    返回指定稀有度的武器列表
    """
    try:
        weapons = await weapon_service.get_weapons_by_rarity(rarity, limit)
        return WeaponListResponse.create_success(
            weapons=weapons,
            total=len(weapons),
            page=1,
            per_page=limit,
            rarity=rarity
        )

    except ValidationException as e:
        raise HTTPException(status_code=422, detail=str(e))
    except DatabaseException as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="获取武器列表失败")


@router.get("/filters/options")
async def get_weapon_filter_options(
    weapon_service: WeaponService = Depends(get_weapon_service)
):
    """
    获取武器过滤选项

    返回可用的过滤选项，用于前端筛选功能
    """
    try:
        filters = weapon_service.get_available_filters()
        return {
            "success": True,
            "data": filters,
            "message": "获取过滤选项成功"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail="获取过滤选项失败")