"""
怪物相关的 Pydantic Schemas

定义怪物数据的请求和响应格式
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator

from src.schemas.base import EntityBase, BaseQueryParams


# ===== 基础数据结构 =====

class MonsterStat(BaseModel):
    """怪物属性数据"""
    hp: int = Field(..., ge=0, description="生命值")
    atk: int = Field(..., ge=0, description="攻击力")
    def_: int = Field(..., ge=0, alias="def", description="防御力")
    elemental_mastery: int = Field(0, ge=0, description="元素精通")


class MonsterResistance(BaseModel):
    """怪物元素抗性数据"""
    pyro: float = Field(0.0, ge=-100.0, le=100.0, description="火元素抗性")
    hydro: float = Field(0.0, ge=-100.0, le=100.0, description="水元素抗性")
    anemo: float = Field(0.0, ge=-100.0, le=100.0, description="风元素抗性")
    electro: float = Field(0.0, ge=-100.0, le=100.0, description="雷元素抗性")
    dendro: float = Field(0.0, ge=-100.0, le=100.0, description="草元素抗性")
    cryo: float = Field(0.0, ge=-100.0, le=100.0, description="冰元素抗性")
    geo: float = Field(0.0, ge=-100.0, le=100.0, description="岩元素抗性")
    physical: float = Field(0.0, ge=-100.0, le=100.0, description="物理抗性")


class MonsterAbility(BaseModel):
    """怪物技能数据"""
    name: str = Field(..., description="技能名称")
    description: str = Field(..., description="技能描述")
    damage_type: Optional[str] = Field(None, description="伤害类型")
    element: Optional[str] = Field(None, description="元素属性")


class MonsterDrop(BaseModel):
    """怪物掉落物数据"""
    item_name: str = Field(..., description="物品名称")
    item_type: Optional[str] = Field(None, description="物品类型")
    drop_rate: float = Field(..., ge=0.0, le=100.0, description="掉落率（百分比）")
    quantity_min: int = Field(1, ge=1, description="最小掉落数量")
    quantity_max: int = Field(1, ge=1, description="最大掉落数量")


# ===== 查询参数 =====

class MonsterQueryParams(BaseQueryParams):
    """怪物查询参数"""
    category: Optional[str] = Field(None, description="怪物类别过滤")
    family: Optional[str] = Field(None, description="怪物族群过滤")
    element: Optional[str] = Field(None, description="元素属性过滤")
    level: Optional[int] = Field(None, ge=1, le=100, description="等级过滤")
    world_level: Optional[int] = Field(None, ge=0, le=8, description="世界等级过滤")
    region: Optional[str] = Field(None, description="地区过滤")
    search: Optional[str] = Field(None, min_length=1, max_length=100, description="搜索关键词")
    sort_by: str = Field("name", description="排序字段")
    sort_order: str = Field("asc", pattern="^(asc|desc)$", description="排序方向")

    @validator('category')
    def validate_category(cls, v):
        if v is not None:
            allowed_categories = [
                '普通怪物', '精英怪物', '周本Boss', '世界Boss',
                '深渊法师', '无相系列', '古岩龙蜥', '遗迹系列',
                '愚人众', '其他'
            ]
            if v not in allowed_categories:
                raise ValueError(f'怪物类别必须是: {", ".join(allowed_categories)}')
        return v

    @validator('family')
    def validate_family(cls, v):
        if v is not None:
            allowed_families = [
                '史莱姆', '丘丘人', '深渊法师', '深渊咏者', '遗迹守卫',
                '遗迹猎者', '愚人众先遣队', '无相系列', '魔偶剑鬼',
                '飘浮灵', '蕈兽', '镀金旅团', '兽境猎犬', '其他'
            ]
            if v not in allowed_families:
                raise ValueError(f'怪物族群必须是: {", ".join(allowed_families)}')
        return v

    @validator('element')
    def validate_element(cls, v):
        if v is not None:
            allowed_elements = ['Pyro', 'Hydro', 'Anemo', 'Electro', 'Dendro', 'Cryo', 'Geo', 'Physical']
            if v not in allowed_elements:
                raise ValueError(f'元素属性必须是: {", ".join(allowed_elements)}')
        return v

    @validator('region')
    def validate_region(cls, v):
        if v is not None:
            allowed_regions = ['Mondstadt', 'Liyue', 'Inazuma', 'Sumeru', 'Fontaine', 'Natlan', 'Snezhnaya']
            if v not in allowed_regions:
                raise ValueError(f'地区必须是: {", ".join(allowed_regions)}')
        return v


# ===== 创建请求 =====

class MonsterCreate(BaseModel):
    """创建怪物的请求数据"""
    name: str = Field(..., min_length=1, max_length=100, description="怪物名称（中文）")
    name_en: Optional[str] = Field(None, max_length=100, description="怪物英文名")

    # 怪物分类
    category: str = Field(..., description="怪物类别")
    family: str = Field(..., description="怪物族群")
    element: Optional[str] = Field(None, description="元素属性")

    # 等级信息
    level: int = Field(..., ge=1, le=100, description="怪物等级")
    world_level: Optional[int] = Field(None, ge=0, le=8, description="世界等级要求")

    # 战斗属性
    base_stats: Dict[str, Any] = Field(..., description="基础属性")

    # 抗性信息
    resistances: Optional[Dict[str, Any]] = Field(default_factory=dict, description="元素抗性")

    # 描述信息
    description: Optional[str] = Field(None, description="怪物描述")
    lore: Optional[str] = Field(None, description="怪物背景故事")
    behavior: Optional[str] = Field(None, description="行为特点")

    # 位置信息
    regions: Optional[List[str]] = Field(default_factory=list, description="出现地区列表")
    locations: Optional[List[Dict[str, Any]]] = Field(default_factory=list, description="具体位置信息")

    # 技能和能力
    abilities: Optional[List[Dict[str, Any]]] = Field(default_factory=list, description="技能列表")

    # 掉落物信息
    drops: Optional[List[Dict[str, Any]]] = Field(default_factory=list, description="掉落物列表")

    # 特殊机制
    weak_points: Optional[List[str]] = Field(default_factory=list, description="弱点信息")
    immunities: Optional[List[str]] = Field(default_factory=list, description="免疫效果列表")

    # 战斗相关
    aggro_range: Optional[float] = Field(None, ge=0.0, le=100.0, description="仇恨范围（米）")
    respawn_time: Optional[int] = Field(None, ge=0, description="重生时间（秒）")

    # 奖励信息
    exp_reward: Optional[int] = Field(None, ge=0, description="击败经验奖励")
    mora_reward: Optional[int] = Field(None, ge=0, description="摩拉奖励")

    # 是否激活状态
    is_active: bool = Field(True, description="是否在游戏中激活")

    @validator('category')
    def validate_category(cls, v):
        allowed_categories = [
            '普通怪物', '精英怪物', '周本Boss', '世界Boss',
            '深渊法师', '无相系列', '古岩龙蜥', '遗迹系列',
            '愚人众', '其他'
        ]
        if v not in allowed_categories:
            raise ValueError(f'怪物类别必须是: {", ".join(allowed_categories)}')
        return v

    @validator('family')
    def validate_family(cls, v):
        allowed_families = [
            '史莱姆', '丘丘人', '深渊法师', '深渊咏者', '遗迹守卫',
            '遗迹猎者', '愚人众先遣队', '无相系列', '魔偶剑鬼',
            '飘浮灵', '蕈兽', '镀金旅团', '兽境猎犬', '其他'
        ]
        if v not in allowed_families:
            raise ValueError(f'怪物族群必须是: {", ".join(allowed_families)}')
        return v

    @validator('element')
    def validate_element(cls, v):
        if v is not None:
            allowed_elements = ['Pyro', 'Hydro', 'Anemo', 'Electro', 'Dendro', 'Cryo', 'Geo', 'Physical']
            if v not in allowed_elements:
                raise ValueError(f'元素属性必须是: {", ".join(allowed_elements)}')
        return v


# ===== 更新请求 =====

class MonsterUpdate(BaseModel):
    """更新怪物的请求数据"""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="怪物名称（中文）")
    name_en: Optional[str] = Field(None, max_length=100, description="怪物英文名")

    # 怪物分类
    category: Optional[str] = Field(None, description="怪物类别")
    family: Optional[str] = Field(None, description="怪物族群")
    element: Optional[str] = Field(None, description="元素属性")

    # 等级信息
    level: Optional[int] = Field(None, ge=1, le=100, description="怪物等级")
    world_level: Optional[int] = Field(None, ge=0, le=8, description="世界等级要求")

    # 战斗属性
    base_stats: Optional[Dict[str, Any]] = Field(None, description="基础属性")

    # 抗性信息
    resistances: Optional[Dict[str, Any]] = Field(None, description="元素抗性")

    # 描述信息
    description: Optional[str] = Field(None, description="怪物描述")
    lore: Optional[str] = Field(None, description="怪物背景故事")
    behavior: Optional[str] = Field(None, description="行为特点")

    # 位置信息
    regions: Optional[List[str]] = Field(None, description="出现地区列表")
    locations: Optional[List[Dict[str, Any]]] = Field(None, description="具体位置信息")

    # 技能和能力
    abilities: Optional[List[Dict[str, Any]]] = Field(None, description="技能列表")

    # 掉落物信息
    drops: Optional[List[Dict[str, Any]]] = Field(None, description="掉落物列表")

    # 特殊机制
    weak_points: Optional[List[str]] = Field(None, description="弱点信息")
    immunities: Optional[List[str]] = Field(None, description="免疫效果列表")

    # 战斗相关
    aggro_range: Optional[float] = Field(None, ge=0.0, le=100.0, description="仇恨范围（米）")
    respawn_time: Optional[int] = Field(None, ge=0, description="重生时间（秒）")

    # 奖励信息
    exp_reward: Optional[int] = Field(None, ge=0, description="击败经验奖励")
    mora_reward: Optional[int] = Field(None, ge=0, description="摩拉奖励")

    # 是否激活状态
    is_active: Optional[bool] = Field(None, description="是否在游戏中激活")

    @validator('category')
    def validate_category(cls, v):
        if v is not None:
            allowed_categories = [
                '普通怪物', '精英怪物', '周本Boss', '世界Boss',
                '深渊法师', '无相系列', '古岩龙蜥', '遗迹系列',
                '愚人众', '其他'
            ]
            if v not in allowed_categories:
                raise ValueError(f'怪物类别必须是: {", ".join(allowed_categories)}')
        return v

    @validator('family')
    def validate_family(cls, v):
        if v is not None:
            allowed_families = [
                '史莱姆', '丘丘人', '深渊法师', '深渊咏者', '遗迹守卫',
                '遗迹猎者', '愚人众先遣队', '无相系列', '魔偶剑鬼',
                '飘浮灵', '蕈兽', '镀金旅团', '兽境猎犬', '其他'
            ]
            if v not in allowed_families:
                raise ValueError(f'怪物族群必须是: {", ".join(allowed_families)}')
        return v

    @validator('element')
    def validate_element(cls, v):
        if v is not None:
            allowed_elements = ['Pyro', 'Hydro', 'Anemo', 'Electro', 'Dendro', 'Cryo', 'Geo', 'Physical']
            if v not in allowed_elements:
                raise ValueError(f'元素属性必须是: {", ".join(allowed_elements)}')
        return v


# ===== 响应 =====

class MonsterResponse(EntityBase):
    """怪物响应数据"""
    name: str
    name_en: Optional[str]
    category: str
    family: str
    element: Optional[str]
    level: int
    world_level: Optional[int]
    base_stats: Dict[str, Any]
    resistances: Optional[Dict[str, Any]]
    description: Optional[str]
    lore: Optional[str]
    behavior: Optional[str]
    regions: Optional[List[str]]
    locations: Optional[List[Dict[str, Any]]]
    abilities: Optional[List[Dict[str, Any]]]
    drops: Optional[List[Dict[str, Any]]]
    weak_points: Optional[List[str]]
    immunities: Optional[List[str]]
    aggro_range: Optional[float]
    respawn_time: Optional[int]
    exp_reward: Optional[int]
    mora_reward: Optional[int]
    is_active: bool

    # 计算属性
    hp: int
    attack: int
    defense: int
    elemental_mastery: int
    total_drops: int
    ability_count: int
    is_boss: bool
    is_elite: bool

    @classmethod
    def from_orm(cls, monster):
        """从ORM模型创建响应对象"""
        # Extract base stats
        base_stats = monster.base_stats or {}

        data = {
            'id': monster.id,
            'name': monster.name,
            'name_en': monster.name_en,
            'category': monster.category,
            'family': monster.family,
            'element': monster.element,
            'level': monster.level,
            'world_level': monster.world_level,
            'base_stats': monster.base_stats,
            'resistances': monster.resistances,
            'description': monster.description,
            'lore': monster.lore,
            'behavior': monster.behavior,
            'regions': monster.regions,
            'locations': monster.locations,
            'abilities': monster.abilities,
            'drops': monster.drops,
            'weak_points': monster.weak_points,
            'immunities': monster.immunities,
            'aggro_range': monster.aggro_range,
            'respawn_time': monster.respawn_time,
            'exp_reward': monster.exp_reward,
            'mora_reward': monster.mora_reward,
            'is_active': monster.is_active,
            # Computed properties
            'hp': monster.hp,
            'attack': monster.attack,
            'defense': monster.defense,
            'elemental_mastery': monster.elemental_mastery,
            'total_drops': monster.total_drops,
            'ability_count': monster.ability_count,
            'is_boss': monster.category in ['周本Boss', '世界Boss'],
            'is_elite': monster.category == '精英怪物',
            'created_at': monster.created_at.isoformat() if monster.created_at else None,
            'updated_at': monster.updated_at.isoformat() if monster.updated_at else None,
        }

        return cls(**data)


# ===== 统计数据 =====

class MonsterStats(BaseModel):
    """怪物统计信息"""
    total_monsters: int = Field(..., description="怪物总数")
    by_category: Dict[str, int] = Field(..., description="按类别统计")
    by_family: Dict[str, int] = Field(..., description="按族群统计")
    by_element: Dict[str, int] = Field(..., description="按元素统计")
    by_level_range: Dict[str, int] = Field(..., description="按等级范围统计")
    by_region: Dict[str, int] = Field(..., description="按地区统计")


class PopularMonsterFamily(BaseModel):
    """热门怪物族群"""
    family_name: str
    monster_count: int = Field(0, description="族群怪物数量")
    encounter_rate: float = Field(0.0, description="遭遇率")


# ===== 列表响应 =====

class MonsterListResponse(BaseModel):
    """怪物列表响应"""
    success: bool = True
    data: Dict[str, Any] = Field(..., description="响应数据")
    message: str = "操作成功"

    @classmethod
    def create_success(cls, monsters: List, total: int, page: int, per_page: int, **kwargs):
        """创建成功响应"""
        return cls(
            success=True,
            data={
                "monsters": [MonsterResponse.from_orm(monster) for monster in monsters],
                "total": total,
                "page": page,
                "per_page": per_page,
                "pages": (total + per_page - 1) // per_page,
                "has_next": page * per_page < total,
                "has_prev": page > 1,
                **kwargs
            },
            message="获取怪物列表成功"
        )


class MonsterDetailResponse(BaseModel):
    """怪物详情响应"""
    success: bool = True
    data: MonsterResponse
    message: str = "操作成功"

    @classmethod
    def create_success(cls, monster, message: str = "获取怪物详情成功"):
        """创建成功响应"""
        return cls(
            success=True,
            data=MonsterResponse.from_orm(monster),
            message=message
        )


class MonsterSearchResponse(BaseModel):
    """怪物搜索响应"""
    success: bool = True
    data: Dict[str, Any]
    message: str = "操作成功"

    @classmethod
    def create_success(cls, monsters: List, query: str):
        """创建搜索成功响应"""
        return cls(
            success=True,
            data={
                "results": [MonsterResponse.from_orm(monster) for monster in monsters],
                "query": query,
                "total": len(monsters)
            },
            message="搜索完成"
        )


class MonsterFamilyResponse(BaseModel):
    """怪物族群响应"""
    success: bool = True
    data: Dict[str, Any]
    message: str = "操作成功"

    @classmethod
    def create_success(cls, family_name: str, monsters: List):
        """创建族群成功响应"""
        return cls(
            success=True,
            data={
                "family_name": family_name,
                "monsters": [MonsterResponse.from_orm(monster) for monster in monsters],
                "total_monsters": len(monsters)
            },
            message="获取族群信息成功"
        )