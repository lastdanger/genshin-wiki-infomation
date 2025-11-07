"""
圣遗物相关的 Pydantic Schemas

定义圣遗物数据的请求和响应格式
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator

from src.schemas.base import EntityBase, BaseQueryParams


# ===== 基础数据结构 =====

class ArtifactMainStat(BaseModel):
    """圣遗物主属性数据"""
    stat_type: str = Field(..., description="主属性类型")
    stat_value: str = Field(..., description="主属性数值")

class ArtifactSubStat(BaseModel):
    """圣遗物副属性数据"""
    stat_type: str = Field(..., description="副属性类型")
    stat_value: str = Field(..., description="副属性数值")

class ArtifactSetEffect(BaseModel):
    """圣遗物套装效果数据"""
    pieces_count: int = Field(..., ge=2, le=4, description="套装件数（2或4）")
    effect_name: str = Field(..., description="套装效果名称")
    effect_description: str = Field(..., description="套装效果描述")


# ===== 查询参数 =====

class ArtifactQueryParams(BaseQueryParams):
    """圣遗物查询参数"""
    set_name: Optional[str] = Field(None, description="套装名称过滤")
    slot: Optional[str] = Field(None, description="部位过滤")
    rarity: Optional[int] = Field(None, ge=3, le=5, description="稀有度过滤")
    source: Optional[str] = Field(None, description="获取方式过滤")
    main_stat_type: Optional[str] = Field(None, description="主属性类型过滤")
    search: Optional[str] = Field(None, min_length=1, max_length=100, description="搜索关键词")
    sort_by: str = Field("name", description="排序字段")
    sort_order: str = Field("asc", pattern="^(asc|desc)$", description="排序方向")

    @validator('slot')
    def validate_slot(cls, v):
        if v is not None:
            allowed_slots = ['flower', 'plume', 'sands', 'goblet', 'circlet']
            if v not in allowed_slots:
                raise ValueError(f'圣遗物部位必须是: {", ".join(allowed_slots)}')
        return v

    @validator('main_stat_type')
    def validate_main_stat_type(cls, v):
        if v is not None:
            allowed_stats = [
                'HP', 'ATK', 'DEF', 'HP%', 'ATK%', 'DEF%',
                'Energy Recharge', 'Elemental Mastery', 'CRIT Rate', 'CRIT DMG',
                'Healing Bonus', 'Pyro DMG Bonus', 'Hydro DMG Bonus',
                'Anemo DMG Bonus', 'Electro DMG Bonus', 'Dendro DMG Bonus',
                'Cryo DMG Bonus', 'Geo DMG Bonus', 'Physical DMG Bonus'
            ]
            if v not in allowed_stats:
                raise ValueError(f'主属性类型必须是: {", ".join(allowed_stats)}')
        return v


# ===== 创建请求 =====

class ArtifactCreate(BaseModel):
    """创建圣遗物的请求数据"""
    name: str = Field(..., min_length=1, max_length=100, description="圣遗物名称（中文）")
    name_en: Optional[str] = Field(None, max_length=100, description="圣遗物英文名")
    set_name: str = Field(..., min_length=1, max_length=100, description="套装名称")
    set_name_en: Optional[str] = Field(None, max_length=100, description="套装英文名")

    # 圣遗物部位
    slot: str = Field(..., description="圣遗物部位")

    # 稀有度
    rarity: int = Field(..., ge=3, le=5, description="星级稀有度（3-5星）")

    # 描述信息
    description: Optional[str] = Field(None, description="圣遗物描述")
    lore: Optional[str] = Field(None, description="圣遗物背景故事")

    # 主属性
    main_stat_type: str = Field(..., description="主属性类型")
    main_stat_value: str = Field(..., description="主属性数值")

    # 副属性（可选）
    sub_stats: Optional[List[Dict[str, Any]]] = Field(default_factory=list, description="副属性列表")

    # 套装效果
    set_effects: Dict[str, Any] = Field(..., description="套装效果（2件套和4件套）")

    # 获取方式
    source: Optional[str] = Field(None, description="获取方式")
    domain_name: Optional[str] = Field(None, max_length=100, description="副本名称")

    # 属性成长
    stat_progression: Optional[Dict[str, Any]] = Field(default_factory=dict, description="属性成长数据")

    # 最大等级
    max_level: int = Field(20, ge=1, le=20, description="最大等级")

    # 是否为套装件
    is_set_piece: bool = Field(True, description="是否为套装圣遗物")

    @validator('slot')
    def validate_slot(cls, v):
        allowed_slots = ['flower', 'plume', 'sands', 'goblet', 'circlet']
        if v not in allowed_slots:
            raise ValueError(f'圣遗物部位必须是: {", ".join(allowed_slots)}')
        return v

    @validator('main_stat_type')
    def validate_main_stat_type(cls, v):
        allowed_stats = [
            'HP', 'ATK', 'DEF', 'HP%', 'ATK%', 'DEF%',
            'Energy Recharge', 'Elemental Mastery', 'CRIT Rate', 'CRIT DMG',
            'Healing Bonus', 'Pyro DMG Bonus', 'Hydro DMG Bonus',
            'Anemo DMG Bonus', 'Electro DMG Bonus', 'Dendro DMG Bonus',
            'Cryo DMG Bonus', 'Geo DMG Bonus', 'Physical DMG Bonus'
        ]
        if v not in allowed_stats:
            raise ValueError(f'主属性类型必须是: {", ".join(allowed_stats)}')
        return v

    @validator('source')
    def validate_source(cls, v):
        if v is not None:
            allowed_sources = ['副本', '世界BOSS', '周本BOSS', '活动', '商店', '合成']
            if v not in allowed_sources:
                raise ValueError(f'获取方式必须是: {", ".join(allowed_sources)}')
        return v


# ===== 更新请求 =====

class ArtifactUpdate(BaseModel):
    """更新圣遗物的请求数据"""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="圣遗物名称（中文）")
    name_en: Optional[str] = Field(None, max_length=100, description="圣遗物英文名")
    set_name: Optional[str] = Field(None, min_length=1, max_length=100, description="套装名称")
    set_name_en: Optional[str] = Field(None, max_length=100, description="套装英文名")

    # 圣遗物部位
    slot: Optional[str] = Field(None, description="圣遗物部位")

    # 稀有度
    rarity: Optional[int] = Field(None, ge=3, le=5, description="星级稀有度（3-5星）")

    # 描述信息
    description: Optional[str] = Field(None, description="圣遗物描述")
    lore: Optional[str] = Field(None, description="圣遗物背景故事")

    # 主属性
    main_stat_type: Optional[str] = Field(None, description="主属性类型")
    main_stat_value: Optional[str] = Field(None, description="主属性数值")

    # 副属性
    sub_stats: Optional[List[Dict[str, Any]]] = Field(None, description="副属性列表")

    # 套装效果
    set_effects: Optional[Dict[str, Any]] = Field(None, description="套装效果")

    # 获取方式
    source: Optional[str] = Field(None, description="获取方式")
    domain_name: Optional[str] = Field(None, max_length=100, description="副本名称")

    # 属性成长
    stat_progression: Optional[Dict[str, Any]] = Field(None, description="属性成长数据")

    # 最大等级
    max_level: Optional[int] = Field(None, ge=1, le=20, description="最大等级")

    # 是否为套装件
    is_set_piece: Optional[bool] = Field(None, description="是否为套装圣遗物")

    @validator('slot')
    def validate_slot(cls, v):
        if v is not None:
            allowed_slots = ['flower', 'plume', 'sands', 'goblet', 'circlet']
            if v not in allowed_slots:
                raise ValueError(f'圣遗物部位必须是: {", ".join(allowed_slots)}')
        return v

    @validator('main_stat_type')
    def validate_main_stat_type(cls, v):
        if v is not None:
            allowed_stats = [
                'HP', 'ATK', 'DEF', 'HP%', 'ATK%', 'DEF%',
                'Energy Recharge', 'Elemental Mastery', 'CRIT Rate', 'CRIT DMG',
                'Healing Bonus', 'Pyro DMG Bonus', 'Hydro DMG Bonus',
                'Anemo DMG Bonus', 'Electro DMG Bonus', 'Dendro DMG Bonus',
                'Cryo DMG Bonus', 'Geo DMG Bonus', 'Physical DMG Bonus'
            ]
            if v not in allowed_stats:
                raise ValueError(f'主属性类型必须是: {", ".join(allowed_stats)}')
        return v

    @validator('source')
    def validate_source(cls, v):
        if v is not None:
            allowed_sources = ['副本', '世界BOSS', '周本BOSS', '活动', '商店', '合成']
            if v not in allowed_sources:
                raise ValueError(f'获取方式必须是: {", ".join(allowed_sources)}')
        return v


# ===== 响应 =====

class ArtifactResponse(EntityBase):
    """圣遗物响应数据"""
    name: str
    name_en: Optional[str]
    set_name: str
    set_name_en: Optional[str]
    slot: str
    slot_display: str
    rarity: int
    rarity_display: str
    description: Optional[str]
    lore: Optional[str]
    main_stat_type: str
    main_stat_value: str
    main_stat_display: str
    sub_stats: Optional[List[Dict[str, Any]]]
    set_effects: Dict[str, Any]
    source: Optional[str]
    domain_name: Optional[str]
    stat_progression: Optional[Dict[str, Any]]
    max_level: int
    is_set_piece: bool
    is_five_star: bool
    is_four_star: bool

    @classmethod
    def from_orm(cls, artifact):
        """从ORM模型创建响应对象"""
        if hasattr(artifact, 'to_dict'):
            data = artifact.to_dict()
        else:
            data = {
                'id': artifact.id,
                'name': artifact.name,
                'name_en': artifact.name_en,
                'set_name': artifact.set_name,
                'set_name_en': artifact.set_name_en,
                'slot': artifact.slot,
                'slot_display': artifact.get_slot_display(),
                'rarity': artifact.rarity,
                'rarity_display': artifact.get_rarity_display(),
                'description': artifact.description,
                'lore': artifact.lore,
                'main_stat_type': artifact.main_stat_type,
                'main_stat_value': artifact.main_stat_value,
                'main_stat_display': artifact.get_main_stat_display(),
                'sub_stats': artifact.sub_stats,
                'set_effects': artifact.set_effects,
                'source': artifact.source,
                'domain_name': artifact.domain_name,
                'stat_progression': artifact.stat_progression,
                'max_level': artifact.max_level,
                'is_set_piece': artifact.is_set_piece,
                'is_five_star': artifact.is_five_star(),
                'is_four_star': artifact.is_four_star(),
                'created_at': artifact.created_at.isoformat() if artifact.created_at else None,
                'updated_at': artifact.updated_at.isoformat() if artifact.updated_at else None,
            }

        return cls(**data)


# ===== 统计数据 =====

class ArtifactStats(BaseModel):
    """圣遗物统计信息"""
    total_artifacts: int = Field(..., description="圣遗物总数")
    by_set: Dict[str, int] = Field(..., description="按套装统计")
    by_slot: Dict[str, int] = Field(..., description="按部位统计")
    by_rarity: Dict[str, int] = Field(..., description="按稀有度统计")
    by_source: Dict[str, int] = Field(..., description="按获取方式统计")


class PopularArtifactSet(BaseModel):
    """热门圣遗物套装"""
    set_name: str
    artifact_count: int = Field(0, description="套装件数")
    usage_count: int = Field(0, description="使用次数")


# ===== 列表响应 =====

class ArtifactListResponse(BaseModel):
    """圣遗物列表响应"""
    success: bool = True
    data: Dict[str, Any] = Field(..., description="响应数据")
    message: str = "操作成功"

    @classmethod
    def create_success(cls, artifacts: List, total: int, page: int, per_page: int, **kwargs):
        """创建成功响应"""
        return cls(
            success=True,
            data={
                "artifacts": [ArtifactResponse.from_orm(artifact) for artifact in artifacts],
                "total": total,
                "page": page,
                "per_page": per_page,
                "pages": (total + per_page - 1) // per_page,
                **kwargs
            },
            message="获取圣遗物列表成功"
        )


class ArtifactDetailResponse(BaseModel):
    """圣遗物详情响应"""
    success: bool = True
    data: ArtifactResponse
    message: str = "操作成功"

    @classmethod
    def create_success(cls, artifact, message: str = "获取圣遗物详情成功"):
        """创建成功响应"""
        return cls(
            success=True,
            data=ArtifactResponse.from_orm(artifact),
            message=message
        )


class ArtifactSearchResponse(BaseModel):
    """圣遗物搜索响应"""
    success: bool = True
    data: Dict[str, Any]
    message: str = "操作成功"

    @classmethod
    def create_success(cls, artifacts: List, query: str):
        """创建搜索成功响应"""
        return cls(
            success=True,
            data={
                "results": [ArtifactResponse.from_orm(artifact) for artifact in artifacts],
                "query": query,
                "total": len(artifacts)
            },
            message="搜索完成"
        )


class ArtifactSetResponse(BaseModel):
    """圣遗物套装响应"""
    success: bool = True
    data: Dict[str, Any]
    message: str = "操作成功"

    @classmethod
    def create_success(cls, set_name: str, artifacts: List):
        """创建套装成功响应"""
        return cls(
            success=True,
            data={
                "set_name": set_name,
                "artifacts": [ArtifactResponse.from_orm(artifact) for artifact in artifacts],
                "total_pieces": len(artifacts),
                "complete_set": len(artifacts) >= 4
            },
            message="获取套装信息成功"
        )