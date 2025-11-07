"""
角色信息 API 路由

提供角色列表查询、详情查看、技能查询、搜索等功能
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import get_db
from src.services.character_service import CharacterService
from src.schemas.character import (
    Character, CharacterDetail, CharacterSkill, CharacterQueryParams,
    CharacterStats, PopularCharacter, CharacterCreate, CharacterUpdate
)
from src.utils.exceptions import (
    NotFoundError, ValidationException, DatabaseException,
    to_http_exception
)
from src.utils.logging import LoggerMixin

router = APIRouter()
logger = LoggerMixin()


async def get_character_service(db: AsyncSession = Depends(get_db)) -> CharacterService:
    """获取角色服务实例"""
    return CharacterService(db)


@router.get(
    "/",
    response_model=dict,
    summary="获取角色列表",
    description="支持分页、过滤、排序的角色列表查询"
)
async def get_characters(
    # 分页参数
    page: int = Query(1, ge=1, description="页码"),
    per_page: int = Query(20, ge=1, le=100, description="每页数量"),

    # 过滤参数
    element: Optional[str] = Query(None, description="元素类型过滤"),
    weapon_type: Optional[str] = Query(None, description="武器类型过滤"),
    rarity: Optional[int] = Query(None, ge=4, le=5, description="稀有度过滤"),
    region: Optional[str] = Query(None, description="地区过滤"),
    search: Optional[str] = Query(None, min_length=1, description="搜索关键词"),

    # 排序参数
    sort_by: str = Query("name", description="排序字段"),
    sort_order: str = Query("asc", pattern="^(asc|desc)$", description="排序方向"),

    character_service: CharacterService = Depends(get_character_service)
):
    """
    获取角色列表（分页）

    支持多种过滤条件和排序方式：
    - 按元素类型、武器类型、稀有度、地区过滤
    - 支持关键词搜索（名称、描述、称号等）
    - 支持多种排序字段和方向
    """
    try:
        # 构建查询参数
        query_params = CharacterQueryParams(
            page=page,
            per_page=per_page,
            element=element,
            weapon_type=weapon_type,
            rarity=rarity,
            region=region,
            search=search,
            sort_by=sort_by,
            sort_order=sort_order
        )

        # 获取角色列表
        characters, total = await character_service.get_character_list(query_params)

        # 计算分页信息
        total_pages = (total + per_page - 1) // per_page
        has_next = page < total_pages
        has_prev = page > 1

        return {
            "success": True,
            "data": {
                "characters": [char.to_dict() for char in characters],
                "pagination": {
                    "page": page,
                    "per_page": per_page,
                    "total": total,
                    "total_pages": total_pages,
                    "has_next": has_next,
                    "has_prev": has_prev
                }
            },
            "message": f"成功获取角色列表，共 {total} 个角色"
        }

    except ValidationException as e:
        raise to_http_exception(e)
    except DatabaseException as e:
        raise to_http_exception(e)
    except Exception as e:
        logger.log_error("获取角色列表失败", error=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": "获取角色列表失败",
                "message": "服务器内部错误，请稍后重试"
            }
        )


@router.get(
    "/{character_id}",
    response_model=dict,
    summary="获取角色详情",
    description="获取指定角色的完整信息，包括技能和天赋"
)
async def get_character_detail(
    character_id: int = Path(..., gt=0, description="角色ID"),
    include_skills: bool = Query(True, description="是否包含技能信息"),
    include_talents: bool = Query(True, description="是否包含天赋信息"),
    character_service: CharacterService = Depends(get_character_service)
):
    """
    获取角色详情

    返回指定角色的完整信息，包括：
    - 基础属性和描述
    - 技能列表（可选）
    - 天赋列表（可选）
    """
    try:
        # 获取角色基础信息
        character = await character_service.get_character_by_id(
            character_id,
            include_relations=include_skills or include_talents
        )

        # 构建响应数据
        character_data = character.to_dict()

        # 添加技能信息
        if include_skills:
            skills = await character_service.get_character_skills(character_id)
            character_data["skills"] = [skill.to_dict() for skill in skills]

        # 添加天赋信息
        if include_talents and hasattr(character, 'talents'):
            character_data["talents"] = [talent.to_dict() for talent in character.talents]

        return {
            "success": True,
            "data": character_data,
            "message": f"成功获取角色 {character.name} 的详情"
        }

    except NotFoundError as e:
        raise to_http_exception(e)
    except DatabaseException as e:
        raise to_http_exception(e)
    except Exception as e:
        logger.log_error("获取角色详情失败", error=e, character_id=character_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": "获取角色详情失败",
                "message": "服务器内部错误，请稍后重试"
            }
        )


@router.get(
    "/{character_id}/skills",
    response_model=dict,
    summary="获取角色技能",
    description="获取指定角色的技能信息"
)
async def get_character_skills(
    character_id: int = Path(..., gt=0, description="角色ID"),
    skill_type: Optional[str] = Query(None, description="技能类型过滤"),
    character_service: CharacterService = Depends(get_character_service)
):
    """
    获取角色技能列表

    返回指定角色的技能信息，可按技能类型过滤：
    - normal_attack: 普通攻击
    - elemental_skill: 元素战技
    - elemental_burst: 元素爆发
    - passive: 固有天赋
    """
    try:
        skills = await character_service.get_character_skills(character_id, skill_type)

        # 按技能类型分组
        skills_by_type = {}
        for skill in skills:
            skill_type_key = skill.skill_type
            if skill_type_key not in skills_by_type:
                skills_by_type[skill_type_key] = []
            skills_by_type[skill_type_key].append(skill.to_dict())

        return {
            "success": True,
            "data": {
                "character_id": character_id,
                "skills": [skill.to_dict() for skill in skills],
                "skills_by_type": skills_by_type,
                "total_skills": len(skills)
            },
            "message": f"成功获取角色技能，共 {len(skills)} 个技能"
        }

    except NotFoundError as e:
        raise to_http_exception(e)
    except DatabaseException as e:
        raise to_http_exception(e)
    except Exception as e:
        logger.log_error("获取角色技能失败", error=e, character_id=character_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": "获取角色技能失败",
                "message": "服务器内部错误，请稍后重试"
            }
        )


@router.get(
    "/search/",
    response_model=dict,
    summary="搜索角色",
    description="根据关键词搜索角色"
)
async def search_characters(
    query: str = Query(..., min_length=1, description="搜索关键词"),
    limit: int = Query(20, ge=1, le=50, description="返回结果数量限制"),
    character_service: CharacterService = Depends(get_character_service)
):
    """
    搜索角色

    支持以下字段的模糊匹配：
    - 角色名称（中文/英文）
    - 角色称号
    - 所属组织
    - 命座名称
    """
    try:
        results = await character_service.search_characters(query, limit)

        return {
            "success": True,
            "data": {
                "query": query,
                "results": [char.to_dict() for char in results],
                "total_found": len(results)
            },
            "message": f"搜索完成，找到 {len(results)} 个匹配的角色"
        }

    except DatabaseException as e:
        raise to_http_exception(e)
    except Exception as e:
        logger.log_error("角色搜索失败", error=e, query=query)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": "角色搜索失败",
                "message": "服务器内部错误，请稍后重试"
            }
        )


@router.get(
    "/stats/",
    response_model=dict,
    summary="获取角色统计信息",
    description="获取角色数据的统计信息"
)
async def get_character_stats(
    character_service: CharacterService = Depends(get_character_service)
):
    """
    获取角色统计信息

    返回各种维度的角色统计数据：
    - 总角色数量
    - 按元素类型分组统计
    - 按武器类型分组统计
    - 按稀有度分组统计
    - 按地区分组统计
    """
    try:
        stats = await character_service.get_character_stats()

        return {
            "success": True,
            "data": stats.to_dict() if hasattr(stats, 'to_dict') else stats.__dict__,
            "message": "成功获取角色统计信息"
        }

    except DatabaseException as e:
        raise to_http_exception(e)
    except Exception as e:
        logger.log_error("获取角色统计失败", error=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": "获取角色统计失败",
                "message": "服务器内部错误，请稍后重试"
            }
        )


@router.get(
    "/filters/",
    response_model=dict,
    summary="获取可用过滤选项",
    description="获取角色列表API可用的所有过滤选项"
)
async def get_filter_options():
    """
    获取角色过滤选项

    返回所有可用的过滤选项，用于前端构建过滤UI
    """
    try:
        filters = CharacterService.get_available_filters()

        return {
            "success": True,
            "data": {
                "filters": filters,
                "sort_options": {
                    "fields": ["name", "rarity", "element", "created_at"],
                    "orders": ["asc", "desc"]
                }
            },
            "message": "成功获取过滤选项"
        }

    except Exception as e:
        logger.log_error("获取过滤选项失败", error=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": "获取过滤选项失败",
                "message": "服务器内部错误，请稍后重试"
            }
        )


# 管理员端点（未来实现）
@router.post(
    "/",
    response_model=dict,
    summary="创建角色",
    description="创建新角色（管理员功能）",
    include_in_schema=False  # 暂时隐藏，Phase 4实现
)
async def create_character(
    character_data: CharacterCreate,
    character_service: CharacterService = Depends(get_character_service)
):
    """创建新角色（管理员功能，Phase 4实现）"""
    try:
        character = await character_service.create_character(character_data)

        return {
            "success": True,
            "data": character.to_dict(),
            "message": f"成功创建角色 {character.name}"
        }

    except ValidationException as e:
        raise to_http_exception(e)
    except DatabaseException as e:
        raise to_http_exception(e)
    except Exception as e:
        logger.log_error("创建角色失败", error=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": "创建角色失败",
                "message": "服务器内部错误，请稍后重试"
            }
        )


@router.put(
    "/{character_id}",
    response_model=dict,
    summary="更新角色",
    description="更新角色信息（管理员功能）",
    include_in_schema=False  # 暂时隐藏，Phase 4实现
)
async def update_character(
    character_id: int = Path(..., gt=0, description="角色ID"),
    character_data: CharacterUpdate = ...,
    character_service: CharacterService = Depends(get_character_service)
):
    """更新角色信息（管理员功能，Phase 4实现）"""
    try:
        character = await character_service.update_character(character_id, character_data)

        return {
            "success": True,
            "data": character.to_dict(),
            "message": f"成功更新角色 {character.name}"
        }

    except NotFoundError as e:
        raise to_http_exception(e)
    except ValidationException as e:
        raise to_http_exception(e)
    except DatabaseException as e:
        raise to_http_exception(e)
    except Exception as e:
        logger.log_error("更新角色失败", error=e, character_id=character_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": "更新角色失败",
                "message": "服务器内部错误，请稍后重试"
            }
        )


@router.delete(
    "/{character_id}",
    response_model=dict,
    summary="删除角色",
    description="删除指定角色（管理员功能）",
    include_in_schema=False  # 暂时隐藏，Phase 4实现
)
async def delete_character(
    character_id: int = Path(..., gt=0, description="角色ID"),
    character_service: CharacterService = Depends(get_character_service)
):
    """删除角色（管理员功能，Phase 4实现）"""
    try:
        success = await character_service.delete_character(character_id)

        if success:
            return {
                "success": True,
                "data": {"character_id": character_id},
                "message": "角色删除成功"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "success": False,
                    "error": "删除角色失败",
                    "message": "未知错误"
                }
            )

    except NotFoundError as e:
        raise to_http_exception(e)
    except DatabaseException as e:
        raise to_http_exception(e)
    except Exception as e:
        logger.log_error("删除角色失败", error=e, character_id=character_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": "删除角色失败",
                "message": "服务器内部错误，请稍后重试"
            }
        )