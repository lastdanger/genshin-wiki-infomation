"""
基础 Pydantic Schemas

定义通用的响应格式、分页、查询参数等基础 Schema
"""
from datetime import datetime
from typing import Any, Dict, Generic, List, Optional, TypeVar, Union
from pydantic import BaseModel, Field, validator

# 泛型类型变量
T = TypeVar('T')


class BaseSchema(BaseModel):
    """基础 Schema 类"""

    class Config:
        # 允许从 ORM 对象创建
        from_attributes = True
        # 使用枚举值而不是名称
        use_enum_values = True
        # 允许字段别名
        validate_by_name = True
        # JSON 编码器配置
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class EntityBase(BaseSchema):
    """实体基础类，包含通用字段"""

    id: int = Field(..., description="实体ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")


class TimestampMixin(BaseSchema):
    """时间戳混入类"""

    created_at: Optional[datetime] = Field(None, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")


# API 响应格式
class APIResponse(BaseModel, Generic[T]):
    """通用API响应格式"""

    success: bool = Field(..., description="请求是否成功")
    data: Optional[T] = Field(None, description="响应数据")
    message: Optional[str] = Field(None, description="响应消息")
    error: Optional[str] = Field(None, description="错误信息")

    @validator('error', always=True)
    def validate_error(cls, v, values):
        """验证错误信息与成功状态的一致性"""
        if not values.get('success') and not v:
            raise ValueError('失败响应必须包含错误信息')
        return v


class PaginationInfo(BaseModel):
    """分页信息"""

    page: int = Field(..., ge=1, description="当前页码")
    per_page: int = Field(..., ge=1, le=100, description="每页数量")
    total: int = Field(..., ge=0, description="总记录数")
    total_pages: int = Field(..., ge=0, description="总页数")
    has_next: bool = Field(..., description="是否有下一页")
    has_prev: bool = Field(..., description="是否有上一页")

    @validator('total_pages', always=True)
    def calculate_total_pages(cls, v, values):
        """计算总页数"""
        total = values.get('total', 0)
        per_page = values.get('per_page', 1)
        return (total + per_page - 1) // per_page if total > 0 else 0

    @validator('has_next', always=True)
    def calculate_has_next(cls, v, values):
        """计算是否有下一页"""
        page = values.get('page', 1)
        total_pages = values.get('total_pages', 0)
        return page < total_pages

    @validator('has_prev', always=True)
    def calculate_has_prev(cls, v, values):
        """计算是否有上一页"""
        page = values.get('page', 1)
        return page > 1


class PaginatedResponse(BaseModel, Generic[T]):
    """分页响应格式"""

    success: bool = Field(True, description="请求是否成功")
    data: List[T] = Field(..., description="数据列表")
    pagination: PaginationInfo = Field(..., description="分页信息")
    message: Optional[str] = Field(None, description="响应消息")


# 查询参数基础类
class BaseQueryParams(BaseModel):
    """基础查询参数"""

    page: int = Field(1, ge=1, description="页码")
    per_page: int = Field(50, ge=1, le=100, description="每页数量")
    search: Optional[str] = Field(None, max_length=100, description="搜索关键词")
    sort_by: Optional[str] = Field("id", description="排序字段")
    sort_order: Optional[str] = Field("desc", pattern="^(asc|desc)$", description="排序方向")

    @validator('search')
    def validate_search(cls, v):
        """验证搜索关键词"""
        if v:
            # 清理搜索字符串
            v = v.strip()
            if len(v) < 2:
                raise ValueError('搜索关键词至少需要2个字符')
        return v


class ElementFilter(BaseModel):
    """元素过滤器"""

    element: Optional[str] = Field(
        None,
        pattern="^(Pyro|Hydro|Anemo|Electro|Dendro|Cryo|Geo)$",
        description="元素类型"
    )


class RarityFilter(BaseModel):
    """稀有度过滤器"""

    rarity: Optional[int] = Field(None, ge=1, le=5, description="稀有度")


class WeaponTypeFilter(BaseModel):
    """武器类型过滤器"""

    weapon_type: Optional[str] = Field(
        None,
        pattern="^(Sword|Claymore|Polearm|Bow|Catalyst)$",
        description="武器类型"
    )


# 搜索相关
class SearchResult(BaseModel):
    """搜索结果项"""

    type: str = Field(..., description="结果类型")
    id: int = Field(..., description="实体ID")
    name: str = Field(..., description="名称")
    description: Optional[str] = Field(None, description="描述")
    thumbnail: Optional[str] = Field(None, description="缩略图URL")
    match_score: float = Field(..., ge=0, le=1, description="匹配分数")
    highlights: Optional[Dict[str, List[str]]] = Field(None, description="高亮片段")


class SearchResponse(BaseModel):
    """搜索响应"""

    success: bool = Field(True)
    results: List[SearchResult] = Field(..., description="搜索结果")
    total: int = Field(..., description="总结果数")
    query: str = Field(..., description="搜索查询")
    took: float = Field(..., description="搜索用时(秒)")


# 统计信息
class EntityCount(BaseModel):
    """实体计数"""

    name: str = Field(..., description="实体名称")
    count: int = Field(..., ge=0, description="数量")
    last_updated: Optional[datetime] = Field(None, description="最后更新时间")


class SystemStats(BaseModel):
    """系统统计信息"""

    characters_count: int = Field(..., ge=0, description="角色数量")
    weapons_count: int = Field(..., ge=0, description="武器数量")
    artifacts_count: int = Field(..., ge=0, description="圣遗物套装数量")
    monsters_count: int = Field(..., ge=0, description="怪物数量")
    game_mechanics_count: int = Field(..., ge=0, description="游戏机制数量")
    images_count: int = Field(..., ge=0, description="图片数量")
    total_entities: int = Field(..., ge=0, description="总实体数")
    last_sync: Optional[datetime] = Field(None, description="最后同步时间")


# 数据源状态
class DataSourceStatus(BaseModel):
    """数据源状态"""

    source_name: str = Field(..., description="数据源名称")
    status: str = Field(..., pattern="^(online|offline|error)$", description="状态")
    last_sync: Optional[datetime] = Field(None, description="最后同步时间")
    next_sync: Optional[datetime] = Field(None, description="下次同步时间")
    error_message: Optional[str] = Field(None, description="错误信息")
    sync_count: int = Field(0, ge=0, description="同步次数")
    success_rate: float = Field(1.0, ge=0, le=1, description="成功率")


class HealthCheck(BaseModel):
    """健康检查响应"""

    status: str = Field(..., description="服务状态")
    version: str = Field(..., description="版本号")
    timestamp: datetime = Field(..., description="检查时间")
    database: bool = Field(..., description="数据库连接状态")
    redis: bool = Field(..., description="Redis连接状态")
    external_apis: Dict[str, bool] = Field(..., description="外部API状态")
    uptime: float = Field(..., description="运行时间(秒)")


# 错误响应
class ErrorDetail(BaseModel):
    """错误详情"""

    code: str = Field(..., description="错误代码")
    message: str = Field(..., description="错误消息")
    field: Optional[str] = Field(None, description="相关字段")
    details: Optional[Dict[str, Any]] = Field(None, description="详细信息")


class ErrorResponse(BaseModel):
    """错误响应格式"""

    success: bool = Field(False, description="请求失败")
    error: str = Field(..., description="错误信息")
    code: Optional[str] = Field(None, description="错误代码")
    details: Optional[Dict[str, Any]] = Field(None, description="详细信息")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="错误时间")


# 批量操作
class BulkOperation(BaseModel):
    """批量操作请求"""

    operation: str = Field(..., pattern="^(create|update|delete)$", description="操作类型")
    ids: List[int] = Field(..., min_items=1, max_items=100, description="实体ID列表")
    data: Optional[Dict[str, Any]] = Field(None, description="操作数据")


class BulkOperationResult(BaseModel):
    """批量操作结果"""

    success: bool = Field(..., description="操作是否成功")
    processed: int = Field(..., ge=0, description="已处理数量")
    errors: List[ErrorDetail] = Field(default_factory=list, description="错误列表")
    results: Optional[List[Dict[str, Any]]] = Field(None, description="操作结果详情")