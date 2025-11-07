"""
武器相关的 Pydantic Schemas

定义武器数据的请求和响应格式
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator

from src.schemas.base import EntityBase, BaseQueryParams


# ===== 基础数据结构 =====

class WeaponStats(BaseModel):
    """武器属性数据"""
    base_attack: int = Field(..., ge=0, description="基础攻击力")
    secondary_stat: Optional[str] = Field(None, description="副属性类型")
    secondary_stat_value: Optional[str] = Field(None, description="副属性数值")


class WeaponPassive(BaseModel):
    """武器被动技能数据"""
    name: str = Field(..., min_length=1, max_length=100, description="被动技能名称")
    description: str = Field(..., min_length=1, description="被动技能描述")
    stats: Optional[Dict[str, Any]] = Field(default_factory=dict, description="被动技能数值配置")


class WeaponAscensionMaterial(BaseModel):
    """武器突破材料数据"""
    level_range: str = Field(..., description="等级范围")
    materials: Dict[str, int] = Field(..., description="材料需求")
    mora_cost: int = Field(..., ge=0, description="摩拉消耗")


# ===== 查询参数 =====

class WeaponQueryParams(BaseQueryParams):
    """武器查询参数"""
    weapon_type: Optional[str] = Field(None, description="武器类型过滤")
    rarity: Optional[int] = Field(None, ge=3, le=5, description="稀有度过滤")
    source: Optional[str] = Field(None, description="获取方式过滤")
    search: Optional[str] = Field(None, max_length=100, description="搜索关键词")
    sort_by: str = Field("name", description="排序字段")
    sort_order: str = Field("asc", pattern="^(asc|desc)$", description="排序方向")

    @validator('weapon_type')
    def validate_weapon_type(cls, v):
        if v is not None and v != '':  # 允许空字符串
            allowed_types = ['Sword', 'Claymore', 'Polearm', 'Bow', 'Catalyst']
            if v not in allowed_types:
                raise ValueError(f'武器类型必须是: {", ".join(allowed_types)}')
        return v if v != '' else None  # 将空字符串转换为None

    @validator('search')
    def validate_search(cls, v):
        if v == '':  # 将空字符串转换为None
            return None
        return v


# ===== 创建请求 =====

class WeaponCreate(BaseModel):
    """创建武器的请求数据"""
    name: str = Field(..., min_length=1, max_length=100, description="武器名称（中文）")
    name_en: Optional[str] = Field(None, max_length=100, description="武器英文名")
    weapon_type: str = Field(..., description="武器类型")
    rarity: int = Field(..., ge=3, le=5, description="星级稀有度（3-5星）")

    # 基础属性
    base_attack: int = Field(..., ge=0, description="基础攻击力")
    secondary_stat: Optional[str] = Field(None, description="副属性类型")
    secondary_stat_value: Optional[str] = Field(None, description="副属性数值")

    # 描述信息
    description: Optional[str] = Field(None, description="武器描述")
    lore: Optional[str] = Field(None, description="武器背景故事")

    # 武器特效
    passive_name: Optional[str] = Field(None, max_length=100, description="被动技能名称")
    passive_description: Optional[str] = Field(None, description="被动技能描述")
    passive_stats: Optional[Dict[str, Any]] = Field(default_factory=dict, description="被动技能数值")

    # 获取方式
    source: Optional[str] = Field(None, description="获取方式")

    # 突破材料信息
    ascension_materials: Optional[List[Dict[str, Any]]] = Field(default_factory=list, description="突破材料信息")

    # 等级范围
    max_level: int = Field(90, ge=1, le=90, description="武器最大等级")

    # 属性成长
    stat_progression: Optional[Dict[str, Any]] = Field(default_factory=dict, description="属性成长数据")

    @validator('weapon_type')
    def validate_weapon_type(cls, v):
        allowed_types = ['Sword', 'Claymore', 'Polearm', 'Bow', 'Catalyst']
        if v not in allowed_types:
            raise ValueError(f'武器类型必须是: {", ".join(allowed_types)}')
        return v

    @validator('source')
    def validate_source(cls, v):
        if v is not None:
            allowed_sources = ['祈愿', '锻造', '活动', '商店', '任务奖励', '成就奖励']
            if v not in allowed_sources:
                raise ValueError(f'获取方式必须是: {", ".join(allowed_sources)}')
        return v


# ===== 更新请求 =====

class WeaponUpdate(BaseModel):
    """更新武器的请求数据"""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="武器名称（中文）")
    name_en: Optional[str] = Field(None, max_length=100, description="武器英文名")
    weapon_type: Optional[str] = Field(None, description="武器类型")
    rarity: Optional[int] = Field(None, ge=3, le=5, description="星级稀有度（3-5星）")

    # 基础属性
    base_attack: Optional[int] = Field(None, ge=0, description="基础攻击力")
    secondary_stat: Optional[str] = Field(None, description="副属性类型")
    secondary_stat_value: Optional[str] = Field(None, description="副属性数值")

    # 描述信息
    description: Optional[str] = Field(None, description="武器描述")
    lore: Optional[str] = Field(None, description="武器背景故事")

    # 武器特效
    passive_name: Optional[str] = Field(None, max_length=100, description="被动技能名称")
    passive_description: Optional[str] = Field(None, description="被动技能描述")
    passive_stats: Optional[Dict[str, Any]] = Field(None, description="被动技能数值")

    # 获取方式
    source: Optional[str] = Field(None, description="获取方式")

    # 突破材料信息
    ascension_materials: Optional[List[Dict[str, Any]]] = Field(None, description="突破材料信息")

    # 等级范围
    max_level: Optional[int] = Field(None, ge=1, le=90, description="武器最大等级")

    # 属性成长
    stat_progression: Optional[Dict[str, Any]] = Field(None, description="属性成长数据")

    @validator('weapon_type')
    def validate_weapon_type(cls, v):
        if v is not None:
            allowed_types = ['Sword', 'Claymore', 'Polearm', 'Bow', 'Catalyst']
            if v not in allowed_types:
                raise ValueError(f'武器类型必须是: {", ".join(allowed_types)}')
        return v

    @validator('source')
    def validate_source(cls, v):
        if v is not None:
            allowed_sources = ['祈愿', '锻造', '活动', '商店', '任务奖励', '成就奖励']
            if v not in allowed_sources:
                raise ValueError(f'获取方式必须是: {", ".join(allowed_sources)}')
        return v


# ===== 响应 =====

class WeaponResponse(EntityBase):
    """武器响应数据"""
    name: str
    name_en: Optional[str]
    weapon_type: str
    rarity: int

    # 基础属性
    base_attack: int
    secondary_stat: Optional[str]
    secondary_stat_value: Optional[str]

    # 描述信息
    description: Optional[str]
    lore: Optional[str]

    # 武器特效
    passive_name: Optional[str]
    passive_description: Optional[str]
    passive_stats: Optional[Dict[str, Any]]

    # 获取方式
    source: Optional[str]

    # 突破材料信息
    ascension_materials: Optional[List[Dict[str, Any]]]

    # 等级范围
    max_level: int

    # 属性成长
    stat_progression: Optional[Dict[str, Any]]

    # 计算属性
    rarity_display: str
    weapon_type_display: str
    is_five_star: bool
    is_four_star: bool

    @classmethod
    def from_orm(cls, weapon):
        """从ORM模型创建响应对象"""
        if hasattr(weapon, 'to_dict'):
            data = weapon.to_dict()
        else:
            data = {
                'id': weapon.id,
                'name': weapon.name,
                'name_en': weapon.name_en,
                'weapon_type': weapon.weapon_type,
                'rarity': weapon.rarity,
                'base_attack': weapon.base_attack,
                'secondary_stat': weapon.secondary_stat,
                'secondary_stat_value': weapon.secondary_stat_value,
                'description': weapon.description,
                'lore': weapon.lore,
                'passive_name': weapon.passive_name,
                'passive_description': weapon.passive_description,
                'passive_stats': weapon.passive_stats,
                'source': weapon.source,
                'ascension_materials': weapon.ascension_materials,
                'max_level': weapon.max_level,
                'stat_progression': weapon.stat_progression,
                'created_at': weapon.created_at.isoformat() if weapon.created_at else None,
                'updated_at': weapon.updated_at.isoformat() if weapon.updated_at else None,
                'rarity_display': '★' * (weapon.rarity or 0),
                'weapon_type_display': weapon.get_weapon_type_display(),
                'is_five_star': weapon.rarity == 5,
                'is_four_star': weapon.rarity == 4,
            }

        return cls(**data)


# ===== 统计数据 =====

class WeaponStats(BaseModel):
    """武器统计信息"""
    total_weapons: int = Field(..., description="武器总数")
    by_type: Dict[str, int] = Field(..., description="按武器类型统计")
    by_rarity: Dict[str, int] = Field(..., description="按稀有度统计")
    by_source: Dict[str, int] = Field(..., description="按获取方式统计")


class PopularWeapon(BaseModel):
    """热门武器"""
    weapon_id: int
    name: str
    weapon_type: str
    rarity: int
    usage_count: int = Field(0, description="使用次数")


# ===== 列表响应 =====

class WeaponListResponse(BaseModel):
    """武器列表响应"""
    success: bool = True
    data: Dict[str, Any] = Field(..., description="响应数据")
    message: str = "操作成功"

    @classmethod
    def create_success(cls, weapons: List, total: int, page: int, per_page: int, **kwargs):
        """创建成功响应"""
        return cls(
            success=True,
            data={
                "weapons": [WeaponResponse.from_orm(weapon) for weapon in weapons],
                "total": total,
                "page": page,
                "per_page": per_page,
                "pages": (total + per_page - 1) // per_page,
                **kwargs
            },
            message="获取武器列表成功"
        )


class WeaponDetailResponse(BaseModel):
    """武器详情响应"""
    success: bool = True
    data: WeaponResponse
    message: str = "操作成功"

    @classmethod
    def create_success(cls, weapon, message: str = "获取武器详情成功"):
        """创建成功响应"""
        return cls(
            success=True,
            data=WeaponResponse.from_orm(weapon),
            message=message
        )


class WeaponSearchResponse(BaseModel):
    """武器搜索响应"""
    success: bool = True
    data: Dict[str, Any]
    message: str = "操作成功"

    @classmethod
    def create_success(cls, weapons: List, query: str):
        """创建搜索成功响应"""
        return cls(
            success=True,
            data={
                "results": [WeaponResponse.from_orm(weapon) for weapon in weapons],
                "query": query,
                "total": len(weapons)
            },
            message="搜索完成"
        )