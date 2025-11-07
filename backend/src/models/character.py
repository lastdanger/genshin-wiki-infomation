"""
角色数据模型

存储角色基础信息、属性和相关数据
"""
from sqlalchemy import Column, String, Integer, Text, Date, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from src.models.base import BaseModel


class Character(BaseModel):
    """
    角色模型

    存储原神角色的基础信息、属性、描述等数据
    """

    __tablename__ = "characters"

    # 基础信息
    name = Column(
        String(100),
        nullable=False,
        unique=True,
        comment="角色姓名（中文）"
    )
    name_en = Column(
        String(100),
        nullable=True,
        comment="角色英文名"
    )

    # 游戏属性
    element = Column(
        String(20),
        nullable=False,
        comment="元素类型（Pyro, Hydro, Anemo等）"
    )
    weapon_type = Column(
        String(30),
        nullable=False,
        comment="武器类型（Sword, Claymore, Polearm等）"
    )
    rarity = Column(
        Integer,
        nullable=False,
        comment="星级稀有度（4或5星）"
    )
    region = Column(
        String(50),
        nullable=True,
        comment="地区（Liyue, Mondstadt等）"
    )

    # 角色属性 (JSONB格式存储)
    base_stats = Column(
        JSONB,
        nullable=False,
        comment="基础属性 {hp: int, atk: int, def: int}"
    )
    ascension_stats = Column(
        JSONB,
        nullable=True,
        comment="突破属性 {stat: str, value: float}"
    )

    # 描述信息
    description = Column(
        Text,
        nullable=True,
        comment="角色描述"
    )
    birthday = Column(
        Date,
        nullable=True,
        comment="生日"
    )
    constellation_name = Column(
        String(100),
        nullable=True,
        comment="命座名称"
    )
    title = Column(
        String(200),
        nullable=True,
        comment="角色称号"
    )
    affiliation = Column(
        String(100),
        nullable=True,
        comment="所属组织或势力"
    )

    # 关联关系
    skills = relationship(
        "CharacterSkill",
        back_populates="character",
        cascade="all, delete-orphan",
        lazy="selectin"  # 优化查询性能
    )
    talents = relationship(
        "CharacterTalent",
        back_populates="character",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    weapon_recommendations = relationship(
        "CharacterWeaponRecommendation",
        back_populates="character",
        cascade="all, delete-orphan"
    )
    artifact_recommendations = relationship(
        "CharacterArtifactRecommendation",
        back_populates="character",
        cascade="all, delete-orphan"
    )
    images = relationship(
        "Image",
        primaryjoin="and_(Character.id == foreign(Image.entity_id), Image.entity_type == 'character')",
        cascade="all, delete-orphan",
        viewonly=True
    )

    # 数据库索引
    __table_args__ = (
        Index('idx_characters_element', 'element'),
        Index('idx_characters_weapon_type', 'weapon_type'),
        Index('idx_characters_rarity', 'rarity'),
        Index('idx_characters_region', 'region'),
        # 全文搜索索引（中文支持）
        Index(
            'idx_characters_search',
            'name',
            'description',
            postgresql_using='gin',
            postgresql_ops={
                'name': 'gin_trgm_ops',
                'description': 'gin_trgm_ops'
            }
        ),
    )

    def __repr__(self):
        return f"<Character(id={self.id}, name='{self.name}', element='{self.element}', rarity={self.rarity})>"

    @property
    def display_name(self) -> str:
        """显示名称（优先中文名）"""
        return self.name or self.name_en or f"Character #{self.id}"

    @property
    def hp(self) -> int:
        """生命值"""
        return self.base_stats.get('hp', 0) if self.base_stats else 0

    @property
    def attack(self) -> int:
        """攻击力"""
        return self.base_stats.get('atk', 0) if self.base_stats else 0

    @property
    def defense(self) -> int:
        """防御力"""
        return self.base_stats.get('def', 0) if self.base_stats else 0

    @property
    def ascension_stat_name(self) -> str:
        """突破属性名称"""
        return self.ascension_stats.get('stat', '') if self.ascension_stats else ''

    @property
    def ascension_stat_value(self) -> float:
        """突破属性数值"""
        return self.ascension_stats.get('value', 0.0) if self.ascension_stats else 0.0

    def to_dict(self) -> dict:
        """转换为字典（包含关联数据）"""
        result = super().to_dict()

        # 添加技能信息
        if hasattr(self, 'skills') and self.skills:
            result['skills'] = [skill.to_dict() for skill in self.skills]

        # 添加天赋信息
        if hasattr(self, 'talents') and self.talents:
            result['talents'] = [talent.to_dict() for talent in self.talents]

        return result

    @classmethod
    def get_element_types(cls) -> list:
        """获取所有元素类型"""
        return ['Pyro', 'Hydro', 'Anemo', 'Electro', 'Dendro', 'Cryo', 'Geo']

    @classmethod
    def get_weapon_types(cls) -> list:
        """获取所有武器类型"""
        return ['Sword', 'Claymore', 'Polearm', 'Bow', 'Catalyst']

    @classmethod
    def get_regions(cls) -> list:
        """获取所有地区"""
        return ['Mondstadt', 'Liyue', 'Inazuma', 'Sumeru', 'Fontaine', 'Natlan', 'Snezhnaya']