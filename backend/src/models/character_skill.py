"""
角色技能数据模型

存储角色的技能详细信息和数值
"""
from sqlalchemy import Column, String, Integer, Text, ForeignKey, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from src.models.base import BaseModel


class CharacterSkill(BaseModel):
    """
    角色技能模型

    存储角色的普通攻击、元素战技、元素爆发等技能信息
    """

    __tablename__ = "character_skills"

    # 关联字段
    character_id = Column(
        Integer,
        ForeignKey('characters.id', ondelete='CASCADE'),
        nullable=False,
        comment="关联的角色ID"
    )

    # 技能基础信息
    skill_type = Column(
        String(30),
        nullable=False,
        comment="技能类型（normal_attack, elemental_skill, elemental_burst, passive）"
    )
    name = Column(
        String(150),
        nullable=False,
        comment="技能名称"
    )
    description = Column(
        Text,
        nullable=False,
        comment="技能描述"
    )

    # 技能数值和属性 (JSONB格式存储复杂数据)
    scaling_stats = Column(
        JSONB,
        nullable=False,
        default={},
        comment="技能倍率和属性配置 {atk_ratio: float, other_stats: object}"
    )
    cooldown = Column(
        Integer,
        nullable=True,
        comment="冷却时间（秒）"
    )
    energy_cost = Column(
        Integer,
        nullable=True,
        comment="元素爆发能量消耗"
    )

    # 技能等级数据 (JSONB数组格式)
    level_scaling = Column(
        JSONB,
        nullable=False,
        default=[],
        comment="各等级的数值变化 [{level: int, values: object}, ...]"
    )

    # 关联关系
    character = relationship(
        "Character",
        back_populates="skills",
        lazy="selectin"
    )

    # 数据库索引
    __table_args__ = (
        Index('idx_character_skills_character_id', 'character_id'),
        Index('idx_character_skills_type', 'skill_type'),
        Index('idx_character_skills_character_type', 'character_id', 'skill_type'),
    )

    def __repr__(self):
        return f"<CharacterSkill(id={self.id}, character_id={self.character_id}, name='{self.name}', type='{self.skill_type}')>"

    @property
    def display_name(self) -> str:
        """显示名称"""
        return self.name or f"Skill #{self.id}"

    @property
    def skill_type_display(self) -> str:
        """技能类型显示名称"""
        type_map = {
            'normal_attack': '普通攻击',
            'elemental_skill': '元素战技',
            'elemental_burst': '元素爆发',
            'passive': '固有天赋'
        }
        return type_map.get(self.skill_type, self.skill_type)

    @property
    def has_cooldown(self) -> bool:
        """是否有冷却时间"""
        return self.cooldown is not None and self.cooldown > 0

    @property
    def has_energy_cost(self) -> bool:
        """是否需要能量"""
        return self.energy_cost is not None and self.energy_cost > 0

    def get_level_data(self, level: int) -> dict:
        """
        获取指定等级的技能数据

        Args:
            level: 技能等级 (1-15)

        Returns:
            该等级的技能数值数据
        """
        if not self.level_scaling or not isinstance(self.level_scaling, list):
            return {}

        # 查找对应等级的数据
        for level_data in self.level_scaling:
            if level_data.get('level') == level:
                return level_data.get('values', {})

        # 如果没找到，返回第一级数据或空字典
        if self.level_scaling:
            return self.level_scaling[0].get('values', {})
        return {}

    def get_max_level(self) -> int:
        """获取技能最大等级"""
        if not self.level_scaling or not isinstance(self.level_scaling, list):
            return 1

        max_level = 1
        for level_data in self.level_scaling:
            level = level_data.get('level', 1)
            if level > max_level:
                max_level = level

        return max_level

    def to_dict(self) -> dict:
        """转换为字典格式"""
        result = super().to_dict()

        # 添加计算属性
        result.update({
            'display_name': self.display_name,
            'skill_type_display': self.skill_type_display,
            'has_cooldown': self.has_cooldown,
            'has_energy_cost': self.has_energy_cost,
            'max_level': self.get_max_level(),
        })

        return result

    @classmethod
    def get_skill_types(cls) -> list:
        """获取所有技能类型"""
        return ['normal_attack', 'elemental_skill', 'elemental_burst', 'passive']

    @classmethod
    def get_skill_type_order(cls) -> dict:
        """获取技能类型排序权重"""
        return {
            'normal_attack': 1,
            'elemental_skill': 2,
            'elemental_burst': 3,
            'passive': 4
        }