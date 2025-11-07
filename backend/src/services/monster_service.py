"""
怪物业务服务

提供怪物数据的增删改查、搜索、统计等业务逻辑
"""
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime

from sqlalchemy import select, func, or_, and_, desc, asc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload

from src.models.monster import Monster
from src.schemas.monster import (
    MonsterCreate, MonsterUpdate, MonsterQueryParams,
    MonsterStats, PopularMonsterFamily
)
from src.utils.logging import LoggerMixin, log_database_operation
from src.utils.exceptions import NotFoundError, ValidationException, DatabaseException
from src.utils.validators import validate_page_params


class MonsterService(LoggerMixin):
    """
    怪物业务服务类

    提供怪物相关的所有业务逻辑操作
    """

    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    # ===== 基础CRUD操作 =====

    async def get_monster_list(
        self,
        params: MonsterQueryParams
    ) -> Tuple[List[Monster], int]:
        """
        获取怪物列表（分页）

        Args:
            params: 查询参数

        Returns:
            (怪物列表, 总数)
        """
        try:
            # 验证分页参数
            page, per_page = validate_page_params(params.page, params.per_page)

            # 构建查询
            query = select(Monster)

            # 应用过滤条件
            if params.category:
                query = query.where(Monster.category == params.category)
            if params.family:
                query = query.where(Monster.family == params.family)
            if params.element:
                query = query.where(Monster.element == params.element)
            if params.level:
                query = query.where(Monster.level == params.level)
            if params.world_level:
                query = query.where(Monster.world_level == params.world_level)
            if params.region:
                # 检查地区是否在regions数组中
                query = query.where(Monster.regions.contains([params.region]))
            if params.search:
                # 使用PostgreSQL全文搜索
                search_term = f"%{params.search}%"
                query = query.where(
                    or_(
                        Monster.name.ilike(search_term),
                        Monster.name_en.ilike(search_term),
                        Monster.category.ilike(search_term),
                        Monster.family.ilike(search_term),
                        Monster.description.ilike(search_term),
                        Monster.behavior.ilike(search_term)
                    )
                )

            # 应用排序
            if params.sort_by == "name":
                order_col = Monster.name
            elif params.sort_by == "category":
                order_col = Monster.category
            elif params.sort_by == "family":
                order_col = Monster.family
            elif params.sort_by == "level":
                order_col = Monster.level
            elif params.sort_by == "world_level":
                order_col = Monster.world_level
            elif params.sort_by == "created_at":
                order_col = Monster.created_at
            else:
                order_col = Monster.id

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

            # 执行查询
            result = await self.db.execute(query)
            monsters = result.scalars().all()

            log_database_operation(
                "select", "monsters",
                filters=params.model_dump(exclude_unset=True) if hasattr(params, 'model_dump') else params.__dict__,
                total=total
            )

            return list(monsters), total

        except Exception as e:
            params_data = params.model_dump() if hasattr(params, 'model_dump') else params.__dict__
            self.log_error("获取怪物列表失败", error=e, params=params_data)
            raise DatabaseException("获取怪物列表失败") from e

    async def get_monster_by_id(
        self,
        monster_id: int
    ) -> Monster:
        """
        根据ID获取怪物详情

        Args:
            monster_id: 怪物ID

        Returns:
            怪物对象

        Raises:
            NotFoundError: 怪物不存在
        """
        try:
            query = select(Monster).where(Monster.id == monster_id)
            result = await self.db.execute(query)
            monster = result.scalar_one_or_none()

            if not monster:
                raise NotFoundError("怪物", monster_id)

            log_database_operation("select", "monsters", id=monster_id)
            return monster

        except NotFoundError:
            raise
        except Exception as e:
            self.log_error("获取怪物详情失败", error=e, monster_id=monster_id)
            raise DatabaseException("获取怪物详情失败") from e

    async def create_monster(self, monster_data: MonsterCreate) -> Monster:
        """
        创建新怪物

        Args:
            monster_data: 怪物创建数据

        Returns:
            创建的怪物对象
        """
        try:
            # 检查怪物名称是否已存在
            existing = await self._check_monster_name_exists(monster_data.name)
            if existing:
                raise ValidationException("name", f"怪物名称 '{monster_data.name}' 已存在")

            # 创建怪物对象
            monster_dict = monster_data.model_dump() if hasattr(monster_data, 'model_dump') else monster_data.__dict__
            monster = Monster(**monster_dict)
            self.db.add(monster)

            await self.db.commit()
            await self.db.refresh(monster)

            log_database_operation("insert", "monsters", id=monster.id)
            self.log_info("怪物创建成功", monster_id=monster.id, name=monster.name)

            # 清除相关缓存
            await self._invalidate_monster_cache()

            return monster

        except (ValidationException, DatabaseException):
            raise
        except Exception as e:
            await self.db.rollback()
            monster_dict = monster_data.model_dump() if hasattr(monster_data, 'model_dump') else monster_data.__dict__
            self.log_error("创建怪物失败", error=e, data=monster_dict)
            raise DatabaseException("创建怪物失败") from e

    async def update_monster(
        self,
        monster_id: int,
        monster_data: MonsterUpdate
    ) -> Monster:
        """
        更新怪物信息

        Args:
            monster_id: 怪物ID
            monster_data: 更新数据

        Returns:
            更新后的怪物对象
        """
        try:
            monster = await self.get_monster_by_id(monster_id)

            # 更新字段
            update_data = monster_data.model_dump(exclude_unset=True) if hasattr(monster_data, 'model_dump') else monster_data.__dict__
            for field, value in update_data.items():
                if hasattr(monster, field):
                    setattr(monster, field, value)

            await self.db.commit()
            await self.db.refresh(monster)

            log_database_operation("update", "monsters", id=monster_id)
            self.log_info("怪物更新成功", monster_id=monster_id, updates=update_data)

            # 清除相关缓存
            await self._invalidate_monster_cache(monster_id)

            return monster

        except NotFoundError:
            raise
        except Exception as e:
            await self.db.rollback()
            self.log_error("更新怪物失败", error=e, monster_id=monster_id)
            raise DatabaseException("更新怪物失败") from e

    async def delete_monster(self, monster_id: int) -> bool:
        """
        删除怪物

        Args:
            monster_id: 怪物ID

        Returns:
            删除是否成功
        """
        try:
            monster = await self.get_monster_by_id(monster_id)

            await self.db.delete(monster)
            await self.db.commit()

            log_database_operation("delete", "monsters", id=monster_id)
            self.log_info("怪物删除成功", monster_id=monster_id)

            # 清除相关缓存
            await self._invalidate_monster_cache(monster_id)

            return True

        except NotFoundError:
            raise
        except Exception as e:
            await self.db.rollback()
            self.log_error("删除怪物失败", error=e, monster_id=monster_id)
            raise DatabaseException("删除怪物失败") from e

    # ===== 搜索功能 =====

    async def search_monsters(
        self,
        query: str,
        limit: int = 20
    ) -> List[Monster]:
        """
        搜索怪物

        Args:
            query: 搜索关键词
            limit: 结果数量限制

        Returns:
            匹配的怪物列表
        """
        try:
            if not query or len(query.strip()) < 2:
                return []

            search_term = f"%{query.strip()}%"

            # 构建搜索查询
            sql_query = select(Monster).where(
                or_(
                    Monster.name.ilike(search_term),
                    Monster.name_en.ilike(search_term),
                    Monster.category.ilike(search_term),
                    Monster.family.ilike(search_term),
                    Monster.description.ilike(search_term),
                    Monster.behavior.ilike(search_term),
                    Monster.lore.ilike(search_term)
                )
            ).limit(limit)

            result = await self.db.execute(sql_query)
            monsters = result.scalars().all()

            self.log_info("怪物搜索完成", query=query, results_count=len(monsters))
            return list(monsters)

        except Exception as e:
            self.log_error("怪物搜索失败", error=e, query=query)
            raise DatabaseException("怪物搜索失败") from e

    # ===== 分类相关功能 =====

    async def get_monsters_by_category(
        self,
        category: str,
        limit: int = 20
    ) -> List[Monster]:
        """
        根据怪物类别获取怪物列表

        Args:
            category: 怪物类别
            limit: 数量限制

        Returns:
            怪物列表
        """
        try:
            query = select(Monster).where(
                Monster.category == category
            ).order_by(Monster.level, desc(Monster.created_at)).limit(limit)

            result = await self.db.execute(query)
            monsters = result.scalars().all()

            self.log_info("按类别获取怪物列表成功", category=category, count=len(monsters))
            return list(monsters)

        except Exception as e:
            self.log_error("按类别获取怪物列表失败", error=e, category=category)
            raise DatabaseException("按类别获取怪物列表失败") from e

    async def get_monsters_by_family(
        self,
        family: str,
        limit: int = 20
    ) -> List[Monster]:
        """
        根据怪物族群获取怪物列表

        Args:
            family: 怪物族群
            limit: 数量限制

        Returns:
            怪物列表
        """
        try:
            query = select(Monster).where(
                Monster.family == family
            ).order_by(Monster.level, desc(Monster.created_at)).limit(limit)

            result = await self.db.execute(query)
            monsters = result.scalars().all()

            self.log_info("按族群获取怪物列表成功", family=family, count=len(monsters))
            return list(monsters)

        except Exception as e:
            self.log_error("按族群获取怪物列表失败", error=e, family=family)
            raise DatabaseException("按族群获取怪物列表失败") from e

    async def get_monsters_by_element(
        self,
        element: str,
        limit: int = 20
    ) -> List[Monster]:
        """
        根据元素类型获取怪物列表

        Args:
            element: 元素类型
            limit: 数量限制

        Returns:
            怪物列表
        """
        try:
            query = select(Monster).where(
                Monster.element == element
            ).order_by(Monster.level, desc(Monster.created_at)).limit(limit)

            result = await self.db.execute(query)
            monsters = result.scalars().all()

            self.log_info("按元素获取怪物列表成功", element=element, count=len(monsters))
            return list(monsters)

        except Exception as e:
            self.log_error("按元素获取怪物列表失败", error=e, element=element)
            raise DatabaseException("按元素获取怪物列表失败") from e

    async def get_monsters_by_region(
        self,
        region: str,
        limit: int = 20
    ) -> List[Monster]:
        """
        根据地区获取怪物列表

        Args:
            region: 地区
            limit: 数量限制

        Returns:
            怪物列表
        """
        try:
            query = select(Monster).where(
                Monster.regions.contains([region])
            ).order_by(Monster.level, desc(Monster.created_at)).limit(limit)

            result = await self.db.execute(query)
            monsters = result.scalars().all()

            self.log_info("按地区获取怪物列表成功", region=region, count=len(monsters))
            return list(monsters)

        except Exception as e:
            self.log_error("按地区获取怪物列表失败", error=e, region=region)
            raise DatabaseException("按地区获取怪物列表失败") from e

    async def get_monsters_by_level_range(
        self,
        min_level: int,
        max_level: int,
        limit: int = 20
    ) -> List[Monster]:
        """
        根据等级范围获取怪物列表

        Args:
            min_level: 最小等级
            max_level: 最大等级
            limit: 数量限制

        Returns:
            怪物列表
        """
        try:
            query = select(Monster).where(
                and_(
                    Monster.level >= min_level,
                    Monster.level <= max_level
                )
            ).order_by(Monster.level).limit(limit)

            result = await self.db.execute(query)
            monsters = result.scalars().all()

            self.log_info(
                "按等级范围获取怪物列表成功",
                min_level=min_level, max_level=max_level, count=len(monsters)
            )
            return list(monsters)

        except Exception as e:
            self.log_error(
                "按等级范围获取怪物列表失败",
                error=e, min_level=min_level, max_level=max_level
            )
            raise DatabaseException("按等级范围获取怪物列表失败") from e

    # ===== 统计功能 =====

    async def get_monster_stats(self) -> MonsterStats:
        """获取怪物统计信息"""
        try:
            # 总数统计
            total_query = select(func.count(Monster.id))
            total_result = await self.db.execute(total_query)
            total_count = total_result.scalar()

            # 按类别分组统计
            category_query = select(
                Monster.category,
                func.count(Monster.id)
            ).group_by(Monster.category)
            category_result = await self.db.execute(category_query)
            by_category = dict(category_result.fetchall())

            # 按族群分组统计
            family_query = select(
                Monster.family,
                func.count(Monster.id)
            ).group_by(Monster.family)
            family_result = await self.db.execute(family_query)
            by_family = dict(family_result.fetchall())

            # 按元素分组统计
            element_query = select(
                Monster.element,
                func.count(Monster.id)
            ).where(Monster.element.is_not(None)).group_by(Monster.element)
            element_result = await self.db.execute(element_query)
            by_element = dict(element_result.fetchall())

            # 按等级范围分组统计
            level_ranges = {
                "1-20": (1, 20),
                "21-40": (21, 40),
                "41-60": (41, 60),
                "61-80": (61, 80),
                "81-100": (81, 100)
            }
            by_level_range = {}
            for range_name, (min_level, max_level) in level_ranges.items():
                level_query = select(func.count(Monster.id)).where(
                    and_(Monster.level >= min_level, Monster.level <= max_level)
                )
                level_result = await self.db.execute(level_query)
                by_level_range[range_name] = level_result.scalar()

            # 按地区统计（需要处理JSONB数组）
            # 这里简化处理，实际可能需要更复杂的JSONB查询
            region_query = select(Monster.regions).where(Monster.regions.is_not(None))
            region_result = await self.db.execute(region_query)
            by_region = {}
            for (regions,) in region_result.fetchall():
                if regions:
                    for region in regions:
                        by_region[region] = by_region.get(region, 0) + 1

            stats = MonsterStats(
                total_monsters=total_count,
                by_category=by_category,
                by_family=by_family,
                by_element=by_element,
                by_level_range=by_level_range,
                by_region=by_region
            )

            self.log_info("怪物统计信息获取成功", total=total_count)
            return stats

        except Exception as e:
            self.log_error("获取怪物统计失败", error=e)
            raise DatabaseException("获取怪物统计失败") from e

    # ===== 辅助方法 =====

    async def _check_monster_name_exists(self, name: str) -> bool:
        """检查怪物名称是否已存在"""
        query = select(Monster.id).where(Monster.name == name)
        result = await self.db.execute(query)
        return result.scalar_one_or_none() is not None

    async def _invalidate_monster_cache(self, monster_id: Optional[int] = None):
        """清除怪物相关缓存 - TODO: Implement caching"""
        # TODO: Implement cache invalidation when cache is properly configured
        pass

    @classmethod
    def get_available_filters(cls) -> Dict[str, List[str]]:
        """获取可用的过滤选项"""
        return {
            "categories": Monster.get_categories(),
            "families": Monster.get_families(),
            "elements": Monster.get_elements(),
            "regions": Monster.get_regions()
        }