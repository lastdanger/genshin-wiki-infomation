"""
角色天赋数据模型

存储角色的固有天赋和命座天赋信息
"""
from sqlalchemy import Column, String, Integer, Text, ForeignKey, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from src.models.base import BaseModel


class CharacterTalent(BaseModel):
    """
    角色天赋模型

    存储角色的固有天赋、突破天赋和命座天赋信息
    """

    __tablename__ = "character_talents"

    # 关联字段
    character_id = Column(
        Integer,
        ForeignKey('characters.id', ondelete='CASCADE'),
        nullable=False,
        comment="关联的角色ID"
    )

    # 天赋基础信息
    talent_type = Column(
        String(30),
        nullable=False,
        comment="天赋类型（passive, ascension, constellation）"
    )
    name = Column(
        String(150),
        nullable=False,
        comment="天赋名称"
    )
    description = Column(
        Text,
        nullable=False,
        comment="天赋描述和效果说明"
    )

    # 解锁条件
    unlock_condition = Column(
        String(100),
        nullable=False,
        comment="解锁条件（如：突破1段、命座1层等）"
    )
    unlock_level = Column(
        Integer,
        nullable=True,
        comment="解锁等级或层数"
    )

    # 天赋效果数据 (JSONB格式存储)
    effects = Column(
        JSONB,
        nullable=False,
        default={},
        comment="天赋效果数值和配置 {effect_type: str, values: object}"
    )

    # 关联关系
    character = relationship(
        "Character",
        back_populates="talents",
        lazy="selectin"
    )

    # 数据库索引
    __table_args__ = (
        Index('idx_character_talents_character_id', 'character_id'),
        Index('idx_character_talents_type', 'talent_type'),
        Index('idx_character_talents_character_type', 'character_id', 'talent_type'),
        Index('idx_character_talents_unlock_level', 'unlock_level'),
    )

    def __repr__(self):
        return f"<CharacterTalent(id={self.id}, character_id={self.character_id}, name='{self.name}', type='{self.talent_type}')>"

    @property
    def display_name(self) -> str:
        """显示名称"""
        return self.name or f"Talent #{self.id}"

    @property
    def talent_type_display(self) -> str:
        """天赋类型显示名称"""
        type_map = {
            'passive': '固有天赋',
            'ascension': '突破天赋',
            'constellation': '命座天赋'
        }
        return type_map.get(self.talent_type, self.talent_type)

    @property
    def is_passive(self) -> bool:
        """是否为固有天赋"""
        return self.talent_type == 'passive'

    @property
    def is_ascension(self) -> bool:
        """是否为突破天赋"""
        return self.talent_type == 'ascension'

    @property
    def is_constellation(self) -> bool:
        """是否为命座天赋"""
        return self.talent_type == 'constellation'

    @property
    def unlock_display(self) -> str:
        """解锁条件显示文本"""
        if self.is_constellation and self.unlock_level:
            return f"命座{self.unlock_level}层"
        elif self.is_ascension and self.unlock_level:
            return f"突破{self.unlock_level}段"
        else:
            return self.unlock_condition or "默认解锁"

    def get_effect_value(self, effect_key: str):
        """
        获取特定效果的数值

        Args:
            effect_key: 效果键名

        Returns:
            效果数值，如果不存在返回None
        """
        if not self.effects or not isinstance(self.effects, dict):
            return None

        return self.effects.get(effect_key)

    def get_all_effects(self) -> dict:
        """获取所有效果数据"""
        return self.effects if isinstance(self.effects, dict) else {}

    def to_dict(self) -> dict:
        """转换为字典格式"""
        result = super().to_dict()

        # 添加计算属性
        result.update({
            'display_name': self.display_name,
            'talent_type_display': self.talent_type_display,
            'unlock_display': self.unlock_display,
            'is_passive': self.is_passive,
            'is_ascension': self.is_ascension,
            'is_constellation': self.is_constellation,
        })

        return result

    @classmethod
    def get_talent_types(cls) -> list:
        """获取所有天赋类型"""
        return ['passive', 'ascension', 'constellation']

    @classmethod
    def get_talent_type_order(cls) -> dict:
        """获取天赋类型排序权重"""
        return {
            'passive': 1,
            'ascension': 2,
            'constellation': 3
        }

    @classmethod
    def get_constellation_levels(cls) -> list:
        """获取命座层数列表"""
        return [1, 2, 3, 4, 5, 6]

    @classmethod
    def get_ascension_phases(cls) -> list:
        """获取突破阶段列表"""
        return [1, 2, 3, 4, 5, 6]