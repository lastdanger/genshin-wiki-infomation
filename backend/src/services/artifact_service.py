"""
圣遗物业务服务

提供圣遗物数据的增删改查、搜索、统计等业务逻辑
"""
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime

from sqlalchemy import select, func, or_, and_, desc, asc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload

from src.models.artifact import Artifact
from src.schemas.artifact import (
    ArtifactCreate, ArtifactUpdate, ArtifactQueryParams,
    ArtifactStats, PopularArtifactSet
)
from src.utils.logging import LoggerMixin, log_database_operation
from src.utils.exceptions import NotFoundError, ValidationException, DatabaseException
from src.utils.validators import validate_page_params


class ArtifactService(LoggerMixin):
    """
    圣遗物业务服务类

    提供圣遗物相关的所有业务逻辑操作
    """

    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    # ===== 基础CRUD操作 =====

    async def get_artifact_list(
        self,
        params: ArtifactQueryParams
    ) -> Tuple[List[Artifact], int]:
        """
        获取圣遗物列表（分页）

        Args:
            params: 查询参数

        Returns:
            (圣遗物列表, 总数)
        """
        try:
            # 验证分页参数
            page, per_page = validate_page_params(params.page, params.per_page)

            # 构建查询
            query = select(Artifact)

            # 应用过滤条件
            if params.set_name:
                query = query.where(Artifact.set_name == params.set_name)
            if params.slot:
                query = query.where(Artifact.slot == params.slot)
            if params.rarity:
                query = query.where(Artifact.rarity == params.rarity)
            if params.source:
                query = query.where(Artifact.source == params.source)
            if params.main_stat_type:
                query = query.where(Artifact.main_stat_type == params.main_stat_type)
            if params.search:
                # 使用PostgreSQL全文搜索
                search_term = f"%{params.search}%"
                query = query.where(
                    or_(
                        Artifact.name.ilike(search_term),
                        Artifact.name_en.ilike(search_term),
                        Artifact.set_name.ilike(search_term),
                        Artifact.description.ilike(search_term),
                        Artifact.main_stat_type.ilike(search_term)
                    )
                )

            # 应用排序
            if params.sort_by == "name":
                order_col = Artifact.name
            elif params.sort_by == "set_name":
                order_col = Artifact.set_name
            elif params.sort_by == "rarity":
                order_col = Artifact.rarity
            elif params.sort_by == "slot":
                order_col = Artifact.slot
            elif params.sort_by == "main_stat_type":
                order_col = Artifact.main_stat_type
            elif params.sort_by == "created_at":
                order_col = Artifact.created_at
            else:
                order_col = Artifact.id

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
            artifacts = result.scalars().all()

            log_database_operation(
                "select", "artifacts",
                filters=params.model_dump(exclude_unset=True) if hasattr(params, 'model_dump') else params.__dict__,
                total=total
            )

            return list(artifacts), total

        except Exception as e:
            params_data = params.model_dump() if hasattr(params, 'model_dump') else params.__dict__
            self.log_error("获取圣遗物列表失败", error=e, params=params_data)
            raise DatabaseException("获取圣遗物列表失败") from e

    async def get_artifact_by_id(
        self,
        artifact_id: int
    ) -> Artifact:
        """
        根据ID获取圣遗物详情

        Args:
            artifact_id: 圣遗物ID

        Returns:
            圣遗物对象

        Raises:
            NotFoundError: 圣遗物不存在
        """
        try:
            query = select(Artifact).where(Artifact.id == artifact_id)
            result = await self.db.execute(query)
            artifact = result.scalar_one_or_none()

            if not artifact:
                raise NotFoundError("圣遗物", artifact_id)

            log_database_operation("select", "artifacts", id=artifact_id)
            return artifact

        except NotFoundError:
            raise
        except Exception as e:
            self.log_error("获取圣遗物详情失败", error=e, artifact_id=artifact_id)
            raise DatabaseException("获取圣遗物详情失败") from e

    async def create_artifact(self, artifact_data: ArtifactCreate) -> Artifact:
        """
        创建新圣遗物

        Args:
            artifact_data: 圣遗物创建数据

        Returns:
            创建的圣遗物对象
        """
        try:
            # 检查圣遗物名称是否已存在
            existing = await self._check_artifact_name_exists(artifact_data.name)
            if existing:
                raise ValidationException("name", f"圣遗物名称 '{artifact_data.name}' 已存在")

            # 创建圣遗物对象
            artifact_dict = artifact_data.model_dump() if hasattr(artifact_data, 'model_dump') else artifact_data.__dict__
            artifact = Artifact(**artifact_dict)
            self.db.add(artifact)

            await self.db.commit()
            await self.db.refresh(artifact)

            log_database_operation("insert", "artifacts", id=artifact.id)
            self.log_info("圣遗物创建成功", artifact_id=artifact.id, name=artifact.name)

            # 清除相关缓存
            await self._invalidate_artifact_cache()

            return artifact

        except (ValidationException, DatabaseException):
            raise
        except Exception as e:
            await self.db.rollback()
            artifact_dict = artifact_data.model_dump() if hasattr(artifact_data, 'model_dump') else artifact_data.__dict__
            self.log_error("创建圣遗物失败", error=e, data=artifact_dict)
            raise DatabaseException("创建圣遗物失败") from e

    async def update_artifact(
        self,
        artifact_id: int,
        artifact_data: ArtifactUpdate
    ) -> Artifact:
        """
        更新圣遗物信息

        Args:
            artifact_id: 圣遗物ID
            artifact_data: 更新数据

        Returns:
            更新后的圣遗物对象
        """
        try:
            artifact = await self.get_artifact_by_id(artifact_id)

            # 更新字段
            update_data = artifact_data.model_dump(exclude_unset=True) if hasattr(artifact_data, 'model_dump') else artifact_data.__dict__
            for field, value in update_data.items():
                if hasattr(artifact, field):
                    setattr(artifact, field, value)

            await self.db.commit()
            await self.db.refresh(artifact)

            log_database_operation("update", "artifacts", id=artifact_id)
            self.log_info("圣遗物更新成功", artifact_id=artifact_id, updates=update_data)

            # 清除相关缓存
            await self._invalidate_artifact_cache(artifact_id)

            return artifact

        except NotFoundError:
            raise
        except Exception as e:
            await self.db.rollback()
            self.log_error("更新圣遗物失败", error=e, artifact_id=artifact_id)
            raise DatabaseException("更新圣遗物失败") from e

    async def delete_artifact(self, artifact_id: int) -> bool:
        """
        删除圣遗物

        Args:
            artifact_id: 圣遗物ID

        Returns:
            删除是否成功
        """
        try:
            artifact = await self.get_artifact_by_id(artifact_id)

            await self.db.delete(artifact)
            await self.db.commit()

            log_database_operation("delete", "artifacts", id=artifact_id)
            self.log_info("圣遗物删除成功", artifact_id=artifact_id)

            # 清除相关缓存
            await self._invalidate_artifact_cache(artifact_id)

            return True

        except NotFoundError:
            raise
        except Exception as e:
            await self.db.rollback()
            self.log_error("删除圣遗物失败", error=e, artifact_id=artifact_id)
            raise DatabaseException("删除圣遗物失败") from e

    # ===== 搜索功能 =====

    async def search_artifacts(
        self,
        query: str,
        limit: int = 20
    ) -> List[Artifact]:
        """
        搜索圣遗物

        Args:
            query: 搜索关键词
            limit: 结果数量限制

        Returns:
            匹配的圣遗物列表
        """
        try:
            if not query or len(query.strip()) < 2:
                return []

            search_term = f"%{query.strip()}%"

            # 构建搜索查询
            sql_query = select(Artifact).where(
                or_(
                    Artifact.name.ilike(search_term),
                    Artifact.name_en.ilike(search_term),
                    Artifact.set_name.ilike(search_term),
                    Artifact.description.ilike(search_term),
                    Artifact.main_stat_type.ilike(search_term),
                    Artifact.slot.ilike(search_term)
                )
            ).limit(limit)

            result = await self.db.execute(sql_query)
            artifacts = result.scalars().all()

            self.log_info("圣遗物搜索完成", query=query, results_count=len(artifacts))
            return list(artifacts)

        except Exception as e:
            self.log_error("圣遗物搜索失败", error=e, query=query)
            raise DatabaseException("圣遗物搜索失败") from e

    # ===== 套装相关功能 =====

    async def get_artifacts_by_set(
        self,
        set_name: str,
        limit: int = 20
    ) -> List[Artifact]:
        """
        根据套装名称获取圣遗物列表

        Args:
            set_name: 套装名称
            limit: 数量限制

        Returns:
            圣遗物列表
        """
        try:
            query = select(Artifact).where(
                Artifact.set_name == set_name
            ).order_by(Artifact.slot, desc(Artifact.rarity)).limit(limit)

            result = await self.db.execute(query)
            artifacts = result.scalars().all()

            self.log_info("按套装获取圣遗物列表成功", set_name=set_name, count=len(artifacts))
            return list(artifacts)

        except Exception as e:
            self.log_error("按套装获取圣遗物列表失败", error=e, set_name=set_name)
            raise DatabaseException("按套装获取圣遗物列表失败") from e

    async def get_artifacts_by_slot(
        self,
        slot: str,
        limit: int = 20
    ) -> List[Artifact]:
        """
        根据部位获取圣遗物列表

        Args:
            slot: 圣遗物部位
            limit: 数量限制

        Returns:
            圣遗物列表
        """
        try:
            query = select(Artifact).where(
                Artifact.slot == slot
            ).order_by(desc(Artifact.rarity), Artifact.set_name).limit(limit)

            result = await self.db.execute(query)
            artifacts = result.scalars().all()

            self.log_info("按部位获取圣遗物列表成功", slot=slot, count=len(artifacts))
            return list(artifacts)

        except Exception as e:
            self.log_error("按部位获取圣遗物列表失败", error=e, slot=slot)
            raise DatabaseException("按部位获取圣遗物列表失败") from e

    # ===== 统计功能 =====

    async def get_artifact_stats(self) -> ArtifactStats:
        """获取圣遗物统计信息"""
        try:
            # 总数统计
            total_query = select(func.count(Artifact.id))
            total_result = await self.db.execute(total_query)
            total_count = total_result.scalar()

            # 按套装分组统计
            set_query = select(
                Artifact.set_name,
                func.count(Artifact.id)
            ).group_by(Artifact.set_name)
            set_result = await self.db.execute(set_query)
            by_set = dict(set_result.fetchall())

            # 按部位分组统计
            slot_query = select(
                Artifact.slot,
                func.count(Artifact.id)
            ).group_by(Artifact.slot)
            slot_result = await self.db.execute(slot_query)
            by_slot = dict(slot_result.fetchall())

            # 按稀有度分组统计
            rarity_query = select(
                Artifact.rarity,
                func.count(Artifact.id)
            ).group_by(Artifact.rarity)
            rarity_result = await self.db.execute(rarity_query)
            by_rarity = {str(k): v for k, v in rarity_result.fetchall()}

            # 按获取方式分组统计
            source_query = select(
                Artifact.source,
                func.count(Artifact.id)
            ).where(Artifact.source.is_not(None)).group_by(Artifact.source)
            source_result = await self.db.execute(source_query)
            by_source = dict(source_result.fetchall())

            stats = ArtifactStats(
                total_artifacts=total_count,
                by_set=by_set,
                by_slot=by_slot,
                by_rarity=by_rarity,
                by_source=by_source
            )

            self.log_info("圣遗物统计信息获取成功", total=total_count)
            return stats

        except Exception as e:
            self.log_error("获取圣遗物统计失败", error=e)
            raise DatabaseException("获取圣遗物统计失败") from e

    # ===== 辅助方法 =====

    async def _check_artifact_name_exists(self, name: str) -> bool:
        """检查圣遗物名称是否已存在"""
        query = select(Artifact.id).where(Artifact.name == name)
        result = await self.db.execute(query)
        return result.scalar_one_or_none() is not None

    async def _invalidate_artifact_cache(self, artifact_id: Optional[int] = None):
        """清除圣遗物相关缓存 - TODO: Implement caching"""
        # TODO: Implement cache invalidation when cache is properly configured
        pass

    @classmethod
    def get_available_filters(cls) -> Dict[str, List[str]]:
        """获取可用的过滤选项"""
        return {
            "slots": Artifact.get_artifact_slots(),
            "main_stat_types": Artifact.get_main_stat_types(),
            "sub_stat_types": Artifact.get_sub_stat_types(),
            "sources": Artifact.get_sources(),
            "rarities": Artifact.get_rarities()
        }