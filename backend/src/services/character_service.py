"""
角色业务服务

提供角色数据的增删改查、搜索、统计等业务逻辑
"""
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime

from sqlalchemy import select, func, or_, and_, desc, asc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload

from src.models.character import Character
from src.models.character_skill import CharacterSkill
from src.models.character_talent import CharacterTalent
from src.schemas.character import (
    CharacterCreate, CharacterUpdate, CharacterQueryParams,
    CharacterStats, PopularCharacter
)
from src.utils.logging import LoggerMixin, log_database_operation
from src.utils.exceptions import NotFoundError, ValidationException, DatabaseException
from src.utils.validators import validate_character_data, validate_page_params
# from src.cache.cache_manager import cached, cache_invalidate, CacheKeys  # TODO: Implement cache


class CharacterService(LoggerMixin):
    """
    角色业务服务类

    提供角色相关的所有业务逻辑操作
    """

    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    # ===== 基础CRUD操作 =====

    async def get_character_list(
        self,
        params: CharacterQueryParams
    ) -> Tuple[List[Character], int]:
        """
        获取角色列表（分页）

        Args:
            params: 查询参数

        Returns:
            (角色列表, 总数)
        """
        try:
            # 验证分页参数
            page, per_page = validate_page_params(params.page, params.per_page)

            # 构建查询
            query = select(Character)

            # 应用过滤条件
            if params.element:
                query = query.where(Character.element == params.element)
            if params.weapon_type:
                query = query.where(Character.weapon_type == params.weapon_type)
            if params.rarity:
                query = query.where(Character.rarity == params.rarity)
            if params.region:
                query = query.where(Character.region == params.region)
            if params.search:
                # 使用PostgreSQL全文搜索
                search_term = f"%{params.search}%"
                query = query.where(
                    or_(
                        Character.name.ilike(search_term),
                        Character.name_en.ilike(search_term),
                        Character.description.ilike(search_term),
                        Character.title.ilike(search_term)
                    )
                )

            # 应用排序
            if params.sort_by == "name":
                order_col = Character.name
            elif params.sort_by == "rarity":
                order_col = Character.rarity
            elif params.sort_by == "element":
                order_col = Character.element
            elif params.sort_by == "created_at":
                order_col = Character.created_at
            else:
                order_col = Character.id

            if params.sort_order == "asc":
                query = query.order_by(asc(order_col))
            else:
                query = query.order_by(desc(order_col))

            # 获取总数
            count_query = select(func.count()).select_from(query.subquery())
            total_result = await self.db.execute(count_query)
            total = total_result.scalar()

            # 应用分页
            offset = (page - 1) * per_page
            query = query.offset(offset).limit(per_page)

            # 预加载关联数据
            query = query.options(
                selectinload(Character.skills),
                selectinload(Character.talents)
            )

            # 执行查询
            result = await self.db.execute(query)
            characters = result.scalars().all()

            log_database_operation(
                "select", "characters",
                filters=params.model_dump(exclude_unset=True) if hasattr(params, 'model_dump') else params.__dict__,
                total=total
            )

            return list(characters), total

        except Exception as e:
            params_data = params.model_dump() if hasattr(params, 'model_dump') else params.__dict__
            self.log_error("获取角色列表失败", error=e, params=params_data)
            raise DatabaseException("获取角色列表失败") from e

    async def get_character_by_id(
        self,
        character_id: int,
        include_relations: bool = True
    ) -> Character:
        """
        根据ID获取角色详情

        Args:
            character_id: 角色ID
            include_relations: 是否包含关联数据

        Returns:
            角色对象

        Raises:
            NotFoundError: 角色不存在
        """
        try:
            query = select(Character).where(Character.id == character_id)

            if include_relations:
                query = query.options(
                    selectinload(Character.skills),
                    selectinload(Character.talents)
                )

            result = await self.db.execute(query)
            character = result.scalar_one_or_none()

            if not character:
                raise NotFoundError("角色", character_id)

            log_database_operation("select", "characters", id=character_id)
            return character

        except NotFoundError:
            raise
        except Exception as e:
            self.log_error("获取角色详情失败", error=e, character_id=character_id)
            raise DatabaseException("获取角色详情失败") from e

    async def create_character(self, character_data: CharacterCreate) -> Character:
        """
        创建新角色

        Args:
            character_data: 角色创建数据

        Returns:
            创建的角色对象
        """
        try:
            # 验证数据
            char_data = character_data.model_dump() if hasattr(character_data, 'model_dump') else character_data.__dict__
            validation_result = validate_character_data(char_data)
            if not validation_result:
                raise ValidationException(
                    "character_data",
                    "; ".join(validation_result.errors)
                )

            # 检查角色名称是否已存在
            existing = await self._check_character_name_exists(character_data.name)
            if existing:
                raise ValidationException("name", f"角色名称 '{character_data.name}' 已存在")

            # 创建角色对象
            character = Character(**char_data)
            self.db.add(character)

            await self.db.commit()
            await self.db.refresh(character)

            log_database_operation("insert", "characters", id=character.id)
            self.log_info("角色创建成功", character_id=character.id, name=character.name)

            # 清除相关缓存
            await self._invalidate_character_cache()

            return character

        except (ValidationException, DatabaseException):
            raise
        except Exception as e:
            await self.db.rollback()
            char_data = character_data.model_dump() if hasattr(character_data, 'model_dump') else character_data.__dict__
            self.log_error("创建角色失败", error=e, data=char_data)
            raise DatabaseException("创建角色失败") from e

    async def update_character(
        self,
        character_id: int,
        character_data: CharacterUpdate
    ) -> Character:
        """
        更新角色信息

        Args:
            character_id: 角色ID
            character_data: 更新数据

        Returns:
            更新后的角色对象
        """
        try:
            character = await self.get_character_by_id(character_id, include_relations=False)

            # 更新字段
            update_data = character_data.model_dump(exclude_unset=True) if hasattr(character_data, 'model_dump') else character_data.__dict__
            for field, value in update_data.items():
                if hasattr(character, field):
                    setattr(character, field, value)

            await self.db.commit()
            await self.db.refresh(character)

            log_database_operation("update", "characters", id=character_id)
            self.log_info("角色更新成功", character_id=character_id, updates=update_data)

            # 清除相关缓存
            await self._invalidate_character_cache(character_id)

            return character

        except NotFoundError:
            raise
        except Exception as e:
            await self.db.rollback()
            self.log_error("更新角色失败", error=e, character_id=character_id)
            raise DatabaseException("更新角色失败") from e

    async def delete_character(self, character_id: int) -> bool:
        """
        删除角色

        Args:
            character_id: 角色ID

        Returns:
            删除是否成功
        """
        try:
            character = await self.get_character_by_id(character_id, include_relations=False)

            await self.db.delete(character)
            await self.db.commit()

            log_database_operation("delete", "characters", id=character_id)
            self.log_info("角色删除成功", character_id=character_id)

            # 清除相关缓存
            await self._invalidate_character_cache(character_id)

            return True

        except NotFoundError:
            raise
        except Exception as e:
            await self.db.rollback()
            self.log_error("删除角色失败", error=e, character_id=character_id)
            raise DatabaseException("删除角色失败") from e

    # ===== 技能相关操作 =====

    async def get_character_skills(
        self,
        character_id: int,
        skill_type: Optional[str] = None
    ) -> List[CharacterSkill]:
        """获取角色技能列表"""
        try:
            # 验证角色存在
            await self.get_character_by_id(character_id, include_relations=False)

            query = select(CharacterSkill).where(CharacterSkill.character_id == character_id)

            if skill_type:
                query = query.where(CharacterSkill.skill_type == skill_type)

            # 按技能类型排序
            query = query.order_by(CharacterSkill.skill_type, CharacterSkill.id)

            result = await self.db.execute(query)
            skills = result.scalars().all()

            log_database_operation("select", "character_skills", character_id=character_id)
            return list(skills)

        except NotFoundError:
            raise
        except Exception as e:
            self.log_error("获取角色技能失败", error=e, character_id=character_id)
            raise DatabaseException("获取角色技能失败") from e

    # ===== 搜索功能 =====

    # @cached(ttl=300, key_prefix="character_search")  # TODO: Enable caching
    async def search_characters(
        self,
        query: str,
        limit: int = 20
    ) -> List[Character]:
        """
        搜索角色

        Args:
            query: 搜索关键词
            limit: 结果数量限制

        Returns:
            匹配的角色列表
        """
        try:
            if not query or len(query.strip()) < 2:
                return []

            search_term = f"%{query.strip()}%"

            # 构建搜索查询
            sql_query = select(Character).where(
                or_(
                    Character.name.ilike(search_term),
                    Character.name_en.ilike(search_term),
                    Character.title.ilike(search_term),
                    Character.affiliation.ilike(search_term),
                    Character.constellation_name.ilike(search_term)
                )
            ).limit(limit)

            result = await self.db.execute(sql_query)
            characters = result.scalars().all()

            self.log_info("角色搜索完成", query=query, results_count=len(characters))
            return list(characters)

        except Exception as e:
            self.log_error("角色搜索失败", error=e, query=query)
            raise DatabaseException("角色搜索失败") from e

    # ===== 统计功能 =====

    # @cached(ttl=1800, key_prefix="character_stats")  # TODO: Enable caching
    async def get_character_stats(self) -> CharacterStats:
        """获取角色统计信息"""
        try:
            # 总数统计
            total_query = select(func.count(Character.id))
            total_result = await self.db.execute(total_query)
            total_count = total_result.scalar()

            # 按元素分组统计
            element_query = select(
                Character.element,
                func.count(Character.id)
            ).group_by(Character.element)
            element_result = await self.db.execute(element_query)
            by_element = dict(element_result.fetchall())

            # 按武器类型分组统计
            weapon_query = select(
                Character.weapon_type,
                func.count(Character.id)
            ).group_by(Character.weapon_type)
            weapon_result = await self.db.execute(weapon_query)
            by_weapon_type = dict(weapon_result.fetchall())

            # 按稀有度分组统计
            rarity_query = select(
                Character.rarity,
                func.count(Character.id)
            ).group_by(Character.rarity)
            rarity_result = await self.db.execute(rarity_query)
            by_rarity = {str(k): v for k, v in rarity_result.fetchall()}

            # 按地区分组统计
            region_query = select(
                Character.region,
                func.count(Character.id)
            ).where(Character.region.is_not(None)).group_by(Character.region)
            region_result = await self.db.execute(region_query)
            by_region = dict(region_result.fetchall())

            stats = CharacterStats(
                total_characters=total_count,
                by_element=by_element,
                by_weapon_type=by_weapon_type,
                by_rarity=by_rarity,
                by_region=by_region
            )

            self.log_info("角色统计信息获取成功", total=total_count)
            return stats

        except Exception as e:
            self.log_error("获取角色统计失败", error=e)
            raise DatabaseException("获取角色统计失败") from e

    # ===== 辅助方法 =====

    async def _check_character_name_exists(self, name: str) -> bool:
        """检查角色名称是否已存在"""
        query = select(Character.id).where(Character.name == name)
        result = await self.db.execute(query)
        return result.scalar_one_or_none() is not None

    async def _invalidate_character_cache(self, character_id: Optional[int] = None):
        """清除角色相关缓存 - 暂时禁用"""
        # TODO: Implement cache invalidation when cache system is ready
        pass
        # from src.cache.cache_manager import cache_manager

        # # 清除列表缓存
        # await cache_manager.invalidate_pattern(f"{CacheKeys.CHARACTER_LIST}:*")
        # await cache_manager.invalidate_pattern(f"{CacheKeys.CHARACTER_SEARCH}:*")

        # # 清除特定角色缓存
        # if character_id:
        #     await cache_manager.invalidate_pattern(f"{CacheKeys.CHARACTER_DETAIL}:*{character_id}*")
        #     await cache_manager.invalidate_pattern(f"{CacheKeys.CHARACTER_SKILLS}:*{character_id}*")

        # # 清除统计缓存
        # await cache_manager.invalidate_pattern("character_stats:*")

    @classmethod
    def get_available_filters(cls) -> Dict[str, List[str]]:
        """获取可用的过滤选项"""
        return {
            "elements": Character.get_element_types(),
            "weapon_types": Character.get_weapon_types(),
            "regions": Character.get_regions(),
            "rarities": [4, 5]
        }