"""
武器业务服务

提供武器数据的增删改查、搜索、统计等业务逻辑
"""
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime

from sqlalchemy import select, func, or_, and_, desc, asc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload

from src.models.weapon import Weapon
from src.schemas.weapon import (
    WeaponCreate, WeaponUpdate, WeaponQueryParams,
    WeaponStats, PopularWeapon
)
from src.utils.logging import LoggerMixin, log_database_operation
from src.utils.exceptions import NotFoundError, ValidationException, DatabaseException
from src.utils.validators import validate_page_params
# from src.cache.cache_manager import cached, cache_invalidate, CacheKeys  # TODO: Implement cache keys


class WeaponService(LoggerMixin):
    """
    武器业务服务类

    提供武器相关的所有业务逻辑操作
    """

    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    # ===== 基础CRUD操作 =====

    async def get_weapon_list(
        self,
        params: WeaponQueryParams
    ) -> Tuple[List[Weapon], int]:
        """
        获取武器列表（分页）

        Args:
            params: 查询参数

        Returns:
            (武器列表, 总数)
        """
        try:
            # 验证分页参数
            page, per_page = validate_page_params(params.page, params.per_page)

            # 构建查询
            query = select(Weapon)

            # 应用过滤条件
            if params.weapon_type:
                query = query.where(Weapon.weapon_type == params.weapon_type)
            if params.rarity:
                query = query.where(Weapon.rarity == params.rarity)
            if params.source:
                query = query.where(Weapon.source == params.source)
            if params.search:
                # 使用PostgreSQL全文搜索
                search_term = f"%{params.search}%"
                query = query.where(
                    or_(
                        Weapon.name.ilike(search_term),
                        Weapon.name_en.ilike(search_term),
                        Weapon.description.ilike(search_term),
                        Weapon.passive_name.ilike(search_term)
                    )
                )

            # 应用排序
            if params.sort_by == "name":
                order_col = Weapon.name
            elif params.sort_by == "rarity":
                order_col = Weapon.rarity
            elif params.sort_by == "weapon_type":
                order_col = Weapon.weapon_type
            elif params.sort_by == "base_attack":
                order_col = Weapon.base_attack
            elif params.sort_by == "created_at":
                order_col = Weapon.created_at
            else:
                order_col = Weapon.id

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
            weapons = result.scalars().all()

            log_database_operation(
                "select", "weapons",
                filters=params.model_dump(exclude_unset=True) if hasattr(params, 'model_dump') else params.__dict__,
                total=total
            )

            return list(weapons), total

        except Exception as e:
            params_data = params.model_dump() if hasattr(params, 'model_dump') else params.__dict__
            self.log_error("获取武器列表失败", error=e, params=params_data)
            raise DatabaseException("获取武器列表失败") from e

    async def get_weapon_by_id(
        self,
        weapon_id: int
    ) -> Weapon:
        """
        根据ID获取武器详情

        Args:
            weapon_id: 武器ID

        Returns:
            武器对象

        Raises:
            NotFoundError: 武器不存在
        """
        try:
            query = select(Weapon).where(Weapon.id == weapon_id)
            result = await self.db.execute(query)
            weapon = result.scalar_one_or_none()

            if not weapon:
                raise NotFoundError("武器", weapon_id)

            log_database_operation("select", "weapons", id=weapon_id)
            return weapon

        except NotFoundError:
            raise
        except Exception as e:
            self.log_error("获取武器详情失败", error=e, weapon_id=weapon_id)
            raise DatabaseException("获取武器详情失败") from e

    async def create_weapon(self, weapon_data: WeaponCreate) -> Weapon:
        """
        创建新武器

        Args:
            weapon_data: 武器创建数据

        Returns:
            创建的武器对象
        """
        try:
            # 检查武器名称是否已存在
            existing = await self._check_weapon_name_exists(weapon_data.name)
            if existing:
                raise ValidationException("name", f"武器名称 '{weapon_data.name}' 已存在")

            # 创建武器对象
            weapon_dict = weapon_data.model_dump() if hasattr(weapon_data, 'model_dump') else weapon_data.__dict__
            weapon = Weapon(**weapon_dict)
            self.db.add(weapon)

            await self.db.commit()
            await self.db.refresh(weapon)

            log_database_operation("insert", "weapons", id=weapon.id)
            self.log_info("武器创建成功", weapon_id=weapon.id, name=weapon.name)

            # 清除相关缓存
            await self._invalidate_weapon_cache()

            return weapon

        except (ValidationException, DatabaseException):
            raise
        except Exception as e:
            await self.db.rollback()
            weapon_dict = weapon_data.model_dump() if hasattr(weapon_data, 'model_dump') else weapon_data.__dict__
            self.log_error("创建武器失败", error=e, data=weapon_dict)
            raise DatabaseException("创建武器失败") from e

    async def update_weapon(
        self,
        weapon_id: int,
        weapon_data: WeaponUpdate
    ) -> Weapon:
        """
        更新武器信息

        Args:
            weapon_id: 武器ID
            weapon_data: 更新数据

        Returns:
            更新后的武器对象
        """
        try:
            weapon = await self.get_weapon_by_id(weapon_id)

            # 更新字段
            update_data = weapon_data.model_dump(exclude_unset=True) if hasattr(weapon_data, 'model_dump') else weapon_data.__dict__
            for field, value in update_data.items():
                if hasattr(weapon, field):
                    setattr(weapon, field, value)

            await self.db.commit()
            await self.db.refresh(weapon)

            log_database_operation("update", "weapons", id=weapon_id)
            self.log_info("武器更新成功", weapon_id=weapon_id, updates=update_data)

            # 清除相关缓存
            await self._invalidate_weapon_cache(weapon_id)

            return weapon

        except NotFoundError:
            raise
        except Exception as e:
            await self.db.rollback()
            self.log_error("更新武器失败", error=e, weapon_id=weapon_id)
            raise DatabaseException("更新武器失败") from e

    async def delete_weapon(self, weapon_id: int) -> bool:
        """
        删除武器

        Args:
            weapon_id: 武器ID

        Returns:
            删除是否成功
        """
        try:
            weapon = await self.get_weapon_by_id(weapon_id)

            await self.db.delete(weapon)
            await self.db.commit()

            log_database_operation("delete", "weapons", id=weapon_id)
            self.log_info("武器删除成功", weapon_id=weapon_id)

            # 清除相关缓存
            await self._invalidate_weapon_cache(weapon_id)

            return True

        except NotFoundError:
            raise
        except Exception as e:
            await self.db.rollback()
            self.log_error("删除武器失败", error=e, weapon_id=weapon_id)
            raise DatabaseException("删除武器失败") from e

    # ===== 搜索功能 =====

    # @cached(ttl=300, key_prefix="weapon_search")  # TODO: Enable caching
    async def search_weapons(
        self,
        query: str,
        limit: int = 20
    ) -> List[Weapon]:
        """
        搜索武器

        Args:
            query: 搜索关键词
            limit: 结果数量限制

        Returns:
            匹配的武器列表
        """
        try:
            if not query or len(query.strip()) < 2:
                return []

            search_term = f"%{query.strip()}%"

            # 构建搜索查询
            sql_query = select(Weapon).where(
                or_(
                    Weapon.name.ilike(search_term),
                    Weapon.name_en.ilike(search_term),
                    Weapon.description.ilike(search_term),
                    Weapon.passive_name.ilike(search_term),
                    Weapon.weapon_type.ilike(search_term)
                )
            ).limit(limit)

            result = await self.db.execute(sql_query)
            weapons = result.scalars().all()

            self.log_info("武器搜索完成", query=query, results_count=len(weapons))
            return list(weapons)

        except Exception as e:
            self.log_error("武器搜索失败", error=e, query=query)
            raise DatabaseException("武器搜索失败") from e

    # ===== 统计功能 =====

    # @cached(ttl=1800, key_prefix="weapon_stats")  # TODO: Enable caching
    async def get_weapon_stats(self) -> WeaponStats:
        """获取武器统计信息"""
        try:
            # 总数统计
            total_query = select(func.count(Weapon.id))
            total_result = await self.db.execute(total_query)
            total_count = total_result.scalar()

            # 按武器类型分组统计
            type_query = select(
                Weapon.weapon_type,
                func.count(Weapon.id)
            ).group_by(Weapon.weapon_type)
            type_result = await self.db.execute(type_query)
            by_type = dict(type_result.fetchall())

            # 按稀有度分组统计
            rarity_query = select(
                Weapon.rarity,
                func.count(Weapon.id)
            ).group_by(Weapon.rarity)
            rarity_result = await self.db.execute(rarity_query)
            by_rarity = {str(k): v for k, v in rarity_result.fetchall()}

            # 按获取方式分组统计
            source_query = select(
                Weapon.source,
                func.count(Weapon.id)
            ).where(Weapon.source.is_not(None)).group_by(Weapon.source)
            source_result = await self.db.execute(source_query)
            by_source = dict(source_result.fetchall())

            stats = WeaponStats(
                total_weapons=total_count,
                by_type=by_type,
                by_rarity=by_rarity,
                by_source=by_source
            )

            self.log_info("武器统计信息获取成功", total=total_count)
            return stats

        except Exception as e:
            self.log_error("获取武器统计失败", error=e)
            raise DatabaseException("获取武器统计失败") from e

    # ===== 武器类型相关 =====

    async def get_weapons_by_type(
        self,
        weapon_type: str,
        limit: int = 20
    ) -> List[Weapon]:
        """
        根据武器类型获取武器列表

        Args:
            weapon_type: 武器类型
            limit: 数量限制

        Returns:
            武器列表
        """
        try:
            query = select(Weapon).where(
                Weapon.weapon_type == weapon_type
            ).order_by(desc(Weapon.rarity), Weapon.name).limit(limit)

            result = await self.db.execute(query)
            weapons = result.scalars().all()

            self.log_info("按类型获取武器列表成功", weapon_type=weapon_type, count=len(weapons))
            return list(weapons)

        except Exception as e:
            self.log_error("按类型获取武器列表失败", error=e, weapon_type=weapon_type)
            raise DatabaseException("按类型获取武器列表失败") from e

    async def get_weapons_by_rarity(
        self,
        rarity: int,
        limit: int = 20
    ) -> List[Weapon]:
        """
        根据稀有度获取武器列表

        Args:
            rarity: 稀有度
            limit: 数量限制

        Returns:
            武器列表
        """
        try:
            query = select(Weapon).where(
                Weapon.rarity == rarity
            ).order_by(Weapon.weapon_type, Weapon.name).limit(limit)

            result = await self.db.execute(query)
            weapons = result.scalars().all()

            self.log_info("按稀有度获取武器列表成功", rarity=rarity, count=len(weapons))
            return list(weapons)

        except Exception as e:
            self.log_error("按稀有度获取武器列表失败", error=e, rarity=rarity)
            raise DatabaseException("按稀有度获取武器列表失败") from e

    # ===== 辅助方法 =====

    async def _check_weapon_name_exists(self, name: str) -> bool:
        """检查武器名称是否已存在"""
        query = select(Weapon.id).where(Weapon.name == name)
        result = await self.db.execute(query)
        return result.scalar_one_or_none() is not None

    async def _invalidate_weapon_cache(self, weapon_id: Optional[int] = None):
        """清除武器相关缓存 - TODO: Implement caching"""
        # TODO: Implement cache invalidation when cache is properly configured
        pass

    @classmethod
    def get_available_filters(cls) -> Dict[str, List[str]]:
        """获取可用的过滤选项"""
        return {
            "weapon_types": Weapon.get_weapon_types(),
            "sources": Weapon.get_sources(),
            "rarities": Weapon.get_rarities()
        }