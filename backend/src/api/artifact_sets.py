"""
圣遗物套装 API 路由

提供圣遗物套装的查询、搜索、统计等 API 接口
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from src.db.session import get_db
from src.models.artifact_set import ArtifactSet

router = APIRouter()


@router.get("/")
async def get_artifact_sets(
    page: int = Query(1, ge=1, description="页码"),
    per_page: int = Query(20, ge=1, le=100, description="每页数量"),
    rarity: Optional[int] = Query(None, ge=3, le=5, description="稀有度过滤"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    db: AsyncSession = Depends(get_db)
):
    """
    获取圣遗物套装列表

    支持分页、过滤、搜索功能
    """
    try:
        # 构建查询
        stmt = select(ArtifactSet)

        # 应用过滤条件
        if rarity:
            stmt = stmt.where(ArtifactSet.max_rarity == rarity)

        if search:
            stmt = stmt.where(
                ArtifactSet.set_name.ilike(f"%{search}%")
            )

        # 获取总数
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_result = await db.execute(count_stmt)
        total = total_result.scalar()

        # 应用分页
        offset = (page - 1) * per_page
        stmt = stmt.offset(offset).limit(per_page)

        # 执行查询
        result = await db.execute(stmt)
        artifact_sets = result.scalars().all()

        # 转换为字典
        sets_data = [art_set.to_dict() for art_set in artifact_sets]

        return {
            "success": True,
            "data": {
                "artifact_sets": sets_data,
                "total": total,
                "page": page,
                "per_page": per_page,
                "total_pages": (total + per_page - 1) // per_page
            },
            "message": f"成功获取{len(sets_data)}个圣遗物套装"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取圣遗物套装列表失败: {str(e)}")


@router.get("/stats/overview")
async def get_artifact_set_stats(
    db: AsyncSession = Depends(get_db)
):
    """
    获取圣遗物套装统计信息

    返回圣遗物套装的各项统计数据
    """
    try:
        # 总数
        total_stmt = select(func.count(ArtifactSet.id))
        total_result = await db.execute(total_stmt)
        total = total_result.scalar()

        # 按稀有度统计
        rarity_stmt = select(
            ArtifactSet.max_rarity,
            func.count(ArtifactSet.id)
        ).group_by(ArtifactSet.max_rarity)
        rarity_result = await db.execute(rarity_stmt)
        by_rarity = {str(rarity): count for rarity, count in rarity_result}

        # 按获取方式统计
        source_stmt = select(
            ArtifactSet.source,
            func.count(ArtifactSet.id)
        ).group_by(ArtifactSet.source).where(ArtifactSet.source.isnot(None))
        source_result = await db.execute(source_stmt)
        by_source = {source: count for source, count in source_result}

        return {
            "total_artifact_sets": total,
            "by_rarity": by_rarity,
            "by_source": by_source
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取统计信息失败: {str(e)}")


@router.get("/{set_id}")
async def get_artifact_set(
    set_id: int = Path(..., gt=0, description="套装ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    获取圣遗物套装详情

    根据套装ID获取详细信息,包括所有部件
    """
    try:
        stmt = select(ArtifactSet).where(ArtifactSet.id == set_id)
        result = await db.execute(stmt)
        artifact_set = result.scalar_one_or_none()

        if not artifact_set:
            raise HTTPException(status_code=404, detail=f"未找到ID为{set_id}的圣遗物套装")

        return {
            "success": True,
            "data": artifact_set.to_dict(),
            "message": "成功获取圣遗物套装详情"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取圣遗物套装详情失败: {str(e)}")


@router.get("/name/{set_name}")
async def get_artifact_set_by_name(
    set_name: str = Path(..., description="套装名称"),
    db: AsyncSession = Depends(get_db)
):
    """
    根据套装名称获取圣遗物套装详情

    根据套装中文名称获取详细信息,包括所有部件
    """
    try:
        stmt = select(ArtifactSet).where(ArtifactSet.set_name == set_name)
        result = await db.execute(stmt)
        artifact_set = result.scalar_one_or_none()

        if not artifact_set:
            raise HTTPException(status_code=404, detail=f"未找到名为'{set_name}'的圣遗物套装")

        return {
            "success": True,
            "data": artifact_set.to_dict(),
            "message": "成功获取圣遗物套装详情"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取圣遗物套装详情失败: {str(e)}")


@router.get("/rarity/{rarity}")
async def get_artifact_sets_by_rarity(
    rarity: int = Path(..., ge=3, le=5, description="稀有度"),
    limit: int = Query(50, ge=1, le=100, description="返回结果数量限制"),
    db: AsyncSession = Depends(get_db)
):
    """
    根据稀有度获取圣遗物套装列表

    返回指定稀有度的圣遗物套装列表
    """
    try:
        stmt = select(ArtifactSet).where(ArtifactSet.max_rarity == rarity).limit(limit)
        result = await db.execute(stmt)
        artifact_sets = result.scalars().all()

        sets_data = [art_set.to_dict() for art_set in artifact_sets]

        return {
            "success": True,
            "data": {
                "artifact_sets": sets_data,
                "total": len(sets_data),
                "rarity": rarity
            },
            "message": f"成功获取{len(sets_data)}个{rarity}星圣遗物套装"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取圣遗物套装列表失败: {str(e)}")


@router.get("/search/")
async def search_artifact_sets(
    q: str = Query(..., min_length=2, description="搜索关键词"),
    limit: int = Query(20, ge=1, le=50, description="返回结果数量限制"),
    db: AsyncSession = Depends(get_db)
):
    """
    搜索圣遗物套装

    根据关键词搜索圣遗物套装名称
    """
    try:
        stmt = select(ArtifactSet).where(
            ArtifactSet.set_name.ilike(f"%{q}%")
        ).limit(limit)

        result = await db.execute(stmt)
        artifact_sets = result.scalars().all()

        sets_data = [art_set.to_dict() for art_set in artifact_sets]

        return {
            "success": True,
            "data": {
                "artifact_sets": sets_data,
                "total": len(sets_data),
                "query": q
            },
            "message": f"搜索到{len(sets_data)}个相关圣遗物套装"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"搜索圣遗物套装失败: {str(e)}")
