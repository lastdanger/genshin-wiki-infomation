"""
角色相关的 Pydantic Schemas

定义角色数据的请求和响应格式
"""
from datetime import date, datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator

from src.schemas.base import EntityBase, BaseQueryParams, ElementFilter, RarityFilter, WeaponTypeFilter


# ===== 基础数据结构 =====

class BaseStats(BaseModel):
    """基础属性数据"""
    hp: int = Field(..., ge=0, description="生命值")
    atk: int = Field(..., ge=0, description="攻击力")
    def_: int = Field(..., ge=0, alias="def", description="防御力")

    class Config:
        validate_by_name = True


class AscensionStats(BaseModel):
    """突破属性数据"""
    stat: str = Field(..., description="属性名称")
    value: float = Field(..., ge=0, description="属性数值")


# ===== 技能相关 Schemas =====

class CharacterSkillBase(BaseModel):
    """角色技能基础信息"""
    skill_type: str = Field(
        ...,
        pattern="^(normal_attack|elemental_skill|elemental_burst|passive)$",
        description="技能类型"
    )
    name: str = Field(..., min_length=1, max_length=150, description="技能名称")
    description: str = Field(..., min_length=1, description="技能描述")
    scaling_stats: Dict[str, Any] = Field(default_factory=dict, description="技能倍率配置")
    cooldown: Optional[int] = Field(None, ge=0, le=300, description="冷却时间（秒）")
    energy_cost: Optional[int] = Field(None, ge=0, le=200, description="能量消耗")
    level_scaling: List[Dict[str, Any]] = Field(default_factory=list, description="等级数值变化")


class CharacterSkillCreate(CharacterSkillBase):
    """创建角色技能的请求数据"""
    character_id: int = Field(..., gt=0, description="角色ID")


class CharacterSkillUpdate(BaseModel):
    """更新角色技能的请求数据"""
    name: Optional[str] = Field(None, min_length=1, max_length=150, description="技能名称")
    description: Optional[str] = Field(None, min_length=1, description="技能描述")
    scaling_stats: Optional[Dict[str, Any]] = Field(None, description="技能倍率配置")
    cooldown: Optional[int] = Field(None, ge=0, le=300, description="冷却时间（秒）")
    energy_cost: Optional[int] = Field(None, ge=0, le=200, description="能量消耗")
    level_scaling: Optional[List[Dict[str, Any]]] = Field(None, description="等级数值变化")


class CharacterSkill(EntityBase, CharacterSkillBase):
    """角色技能响应数据"""
    character_id: int = Field(..., description="角色ID")
    display_name: str = Field(..., description="显示名称")
    skill_type_display: str = Field(..., description="技能类型显示名")
    has_cooldown: bool = Field(..., description="是否有冷却时间")
    has_energy_cost: bool = Field(..., description="是否需要能量")
    max_level: int = Field(..., description="最大等级")


# ===== 天赋相关 Schemas =====

class CharacterTalentBase(BaseModel):
    """角色天赋基础信息"""
    talent_type: str = Field(
        ...,
        pattern="^(passive|ascension|constellation)$",
        description="天赋类型"
    )
    name: str = Field(..., min_length=1, max_length=150, description="天赋名称")
    description: str = Field(..., min_length=1, description="天赋描述")
    unlock_condition: str = Field(..., min_length=1, max_length=100, description="解锁条件")
    unlock_level: Optional[int] = Field(None, ge=1, le=6, description="解锁等级或层数")
    effects: Dict[str, Any] = Field(default_factory=dict, description="天赋效果配置")


class CharacterTalentCreate(CharacterTalentBase):
    """创建角色天赋的请求数据"""
    character_id: int = Field(..., gt=0, description="角色ID")


class CharacterTalentUpdate(BaseModel):
    """更新角色天赋的请求数据"""
    name: Optional[str] = Field(None, min_length=1, max_length=150, description="天赋名称")
    description: Optional[str] = Field(None, min_length=1, description="天赋描述")
    unlock_condition: Optional[str] = Field(None, min_length=1, max_length=100, description="解锁条件")
    unlock_level: Optional[int] = Field(None, ge=1, le=6, description="解锁等级或层数")
    effects: Optional[Dict[str, Any]] = Field(None, description="天赋效果配置")


class CharacterTalent(EntityBase, CharacterTalentBase):
    """角色天赋响应数据"""
    character_id: int = Field(..., description="角色ID")
    display_name: str = Field(..., description="显示名称")
    talent_type_display: str = Field(..., description="天赋类型显示名")
    unlock_display: str = Field(..., description="解锁条件显示文本")
    is_passive: bool = Field(..., description="是否为固有天赋")
    is_ascension: bool = Field(..., description="是否为突破天赋")
    is_constellation: bool = Field(..., description="是否为命座天赋")


# ===== 角色主体 Schemas =====

class CharacterBase(BaseModel):
    """角色基础信息"""
    name: str = Field(..., min_length=1, max_length=100, description="角色姓名（中文）")
    name_en: Optional[str] = Field(None, max_length=100, description="角色英文名")
    element: str = Field(
        ...,
        pattern="^(Pyro|Hydro|Anemo|Electro|Dendro|Cryo|Geo)$",
        description="元素类型"
    )
    weapon_type: str = Field(
        ...,
        pattern="^(Sword|Claymore|Polearm|Bow|Catalyst)$",
        description="武器类型"
    )
    rarity: int = Field(..., ge=4, le=5, description="稀有度（4或5星）")
    region: Optional[str] = Field(
        None,
        pattern="^(Mondstadt|Liyue|Inazuma|Sumeru|Fontaine|Natlan|Snezhnaya)$",
        description="地区"
    )
    base_stats: BaseStats = Field(..., description="基础属性")
    ascension_stats: Optional[AscensionStats] = Field(None, description="突破属性")
    description: Optional[str] = Field(None, max_length=2000, description="角色描述")
    birthday: Optional[date] = Field(None, description="生日")
    constellation_name: Optional[str] = Field(None, max_length=100, description="命座名称")
    title: Optional[str] = Field(None, max_length=200, description="角色称号")
    affiliation: Optional[str] = Field(None, max_length=100, description="所属组织")

    @validator('name')
    def validate_name_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('角色名称不能为空')
        return v.strip()


class CharacterCreate(CharacterBase):
    """创建角色的请求数据"""
    pass


class CharacterUpdate(BaseModel):
    """更新角色的请求数据"""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="角色姓名（中文）")
    name_en: Optional[str] = Field(None, max_length=100, description="角色英文名")
    element: Optional[str] = Field(None, pattern="^(Pyro|Hydro|Anemo|Electro|Dendro|Cryo|Geo)$", description="元素类型")
    weapon_type: Optional[str] = Field(None, pattern="^(Sword|Claymore|Polearm|Bow|Catalyst)$", description="武器类型")
    rarity: Optional[int] = Field(None, ge=4, le=5, description="稀有度（4或5星）")
    region: Optional[str] = Field(None, pattern="^(Mondstadt|Liyue|Inazuma|Sumeru|Fontaine|Natlan|Snezhnaya)$", description="地区")
    base_stats: Optional[BaseStats] = Field(None, description="基础属性")
    ascension_stats: Optional[AscensionStats] = Field(None, description="突破属性")
    description: Optional[str] = Field(None, max_length=2000, description="角色描述")
    birthday: Optional[date] = Field(None, description="生日")
    constellation_name: Optional[str] = Field(None, max_length=100, description="命座名称")
    title: Optional[str] = Field(None, max_length=200, description="角色称号")
    affiliation: Optional[str] = Field(None, max_length=100, description="所属组织")


class Character(EntityBase, CharacterBase):
    """角色完整响应数据"""
    display_name: str = Field(..., description="显示名称")
    hp: int = Field(..., description="生命值")
    attack: int = Field(..., description="攻击力")
    defense: int = Field(..., description="防御力")
    ascension_stat_name: str = Field(..., description="突破属性名称")
    ascension_stat_value: float = Field(..., description="突破属性数值")


class CharacterDetail(Character):
    """角色详情响应数据（包含关联信息）"""
    skills: List[CharacterSkill] = Field(default_factory=list, description="技能列表")
    talents: List[CharacterTalent] = Field(default_factory=list, description="天赋列表")


# ===== 查询参数 Schemas =====

class CharacterQueryParams(BaseQueryParams, ElementFilter, RarityFilter, WeaponTypeFilter):
    """角色查询参数"""
    region: Optional[str] = Field(
        None,
        pattern="^(Mondstadt|Liyue|Inazuma|Sumeru|Fontaine|Natlan|Snezhnaya)$",
        description="地区过滤"
    )


class CharacterSkillQueryParams(BaseQueryParams):
    """角色技能查询参数"""
    character_id: Optional[int] = Field(None, gt=0, description="角色ID过滤")
    skill_type: Optional[str] = Field(
        None,
        pattern="^(normal_attack|elemental_skill|elemental_burst|passive)$",
        description="技能类型过滤"
    )


# ===== 统计和聚合 Schemas =====

class CharacterStats(BaseModel):
    """角色统计信息"""
    total_characters: int = Field(..., ge=0, description="角色总数")
    by_element: Dict[str, int] = Field(..., description="按元素分组统计")
    by_weapon_type: Dict[str, int] = Field(..., description="按武器类型分组统计")
    by_rarity: Dict[str, int] = Field(..., description="按稀有度分组统计")
    by_region: Dict[str, int] = Field(..., description="按地区分组统计")


class PopularCharacter(BaseModel):
    """热门角色信息"""
    character: Character = Field(..., description="角色基础信息")
    view_count: int = Field(..., ge=0, description="查看次数")
    last_viewed: datetime = Field(..., description="最后查看时间")


# ===== 批量操作 Schemas =====

class CharacterBulkCreate(BaseModel):
    """批量创建角色"""
    characters: List[CharacterCreate] = Field(..., min_items=1, max_items=50, description="角色数据列表")


class CharacterBulkUpdate(BaseModel):
    """批量更新角色"""
    updates: List[Dict[str, Any]] = Field(..., min_items=1, max_items=50, description="更新数据列表")

    @validator('updates')
    def validate_updates_format(cls, v):
        for update in v:
            if 'id' not in update:
                raise ValueError('每个更新项必须包含id字段')
            if not isinstance(update['id'], int) or update['id'] <= 0:
                raise ValueError('id必须是正整数')
        return v