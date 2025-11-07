"""
武器数据模型

存储武器基础信息、属性和相关数据
"""
from sqlalchemy import Column, String, Integer, Text, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from src.models.base import BaseModel


class Weapon(BaseModel):
    """
    武器模型

    存储原神武器的基础信息、属性、特效等数据
    """

    __tablename__ = "weapons"

    # 基础信息
    name = Column(
        String(100),
        nullable=False,
        unique=True,
        comment="武器名称（中文）"
    )
    name_en = Column(
        String(100),
        nullable=True,
        comment="武器英文名"
    )

    # 武器属性
    weapon_type = Column(
        String(30),
        nullable=False,
        comment="武器类型（Sword, Claymore, Polearm, Bow, Catalyst）"
    )
    rarity = Column(
        Integer,
        nullable=False,
        comment="星级稀有度（3-5星）"
    )

    # 基础属性
    base_attack = Column(
        Integer,
        nullable=False,
        comment="基础攻击力"
    )
    secondary_stat = Column(
        String(50),
        nullable=True,
        comment="副属性类型（攻击力%、暴击率%、元素充能效率%等）"
    )
    secondary_stat_value = Column(
        String(20),
        nullable=True,
        comment="副属性数值"
    )

    # 描述信息
    description = Column(
        Text,
        nullable=True,
        comment="武器描述"
    )
    lore = Column(
        Text,
        nullable=True,
        comment="武器背景故事"
    )

    # 武器特效
    passive_name = Column(
        String(100),
        nullable=True,
        comment="被动技能名称"
    )
    passive_description = Column(
        Text,
        nullable=True,
        comment="被动技能描述"
    )
    passive_stats = Column(
        JSONB,
        nullable=True,
        comment="被动技能数值（JSON格式）"
    )

    # 获取方式
    source = Column(
        String(50),
        nullable=True,
        comment="获取方式（祈愿、锻造、活动、商店等）"
    )

    # 突破材料信息
    ascension_materials = Column(
        JSONB,
        nullable=True,
        comment="突破材料信息（JSON格式）"
    )

    # 等级范围
    max_level = Column(
        Integer,
        default=90,
        comment="武器最大等级"
    )

    # 属性成长
    stat_progression = Column(
        JSONB,
        nullable=True,
        comment="属性成长数据（JSON格式，包含不同等级的属性值）"
    )

    # 索引
    __table_args__ = (
        Index('idx_weapons_type_rarity', 'weapon_type', 'rarity'),
        Index('idx_weapons_source', 'source'),
        Index('idx_weapons_name', 'name'),
    )

    # 关系定义（未来可能添加武器精炼材料等）
    # refinement_materials = relationship("WeaponRefinementMaterial", back_populates="weapon")

    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'name': self.name,
            'name_en': self.name_en,
            'weapon_type': self.weapon_type,
            'rarity': self.rarity,
            'base_attack': self.base_attack,
            'secondary_stat': self.secondary_stat,
            'secondary_stat_value': self.secondary_stat_value,
            'description': self.description,
            'lore': self.lore,
            'passive_name': self.passive_name,
            'passive_description': self.passive_description,
            'passive_stats': self.passive_stats,
            'source': self.source,
            'ascension_materials': self.ascension_materials,
            'max_level': self.max_level,
            'stat_progression': self.stat_progression,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            # 计算属性
            'rarity_display': '★' * (self.rarity or 0),
            'weapon_type_display': self.get_weapon_type_display(),
            'is_five_star': self.rarity == 5,
            'is_four_star': self.rarity == 4,
        }

    def get_weapon_type_display(self):
        """获取武器类型的中文显示名"""
        weapon_type_names = {
            'Sword': '单手剑',
            'Claymore': '双手剑',
            'Polearm': '长柄武器',
            'Bow': '弓',
            'Catalyst': '法器'
        }
        return weapon_type_names.get(self.weapon_type, self.weapon_type)

    @classmethod
    def get_weapon_types(cls):
        """获取所有武器类型"""
        return ['Sword', 'Claymore', 'Polearm', 'Bow', 'Catalyst']

    @classmethod
    def get_sources(cls):
        """获取所有获取方式"""
        return ['祈愿', '锻造', '活动', '商店', '任务奖励', '成就奖励']

    @classmethod
    def get_rarities(cls):
        """获取所有稀有度"""
        return [3, 4, 5]

    def __repr__(self):
        return f"<Weapon(id={self.id}, name='{self.name}', type='{self.weapon_type}', rarity={self.rarity})>"