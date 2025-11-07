"""
角色武器推荐关联模型（占位符）

将在Phase 4 (武器功能) 完整实现
"""
from sqlalchemy import Column, String, Integer, Text, ForeignKey, Index
from sqlalchemy.orm import relationship

from src.models.base import BaseModel


class CharacterWeaponRecommendation(BaseModel):
    """角色武器推荐模型（基础结构）"""

    __tablename__ = "character_weapon_recommendations"

    character_id = Column(Integer, ForeignKey('characters.id', ondelete='CASCADE'), nullable=False)
    weapon_id = Column(Integer, nullable=False, comment="武器ID（待实现）")
    rating = Column(Integer, nullable=False, comment="推荐等级1-5星")
    explanation = Column(Text, nullable=False, comment="推荐理由")
    build_type = Column(String(20), nullable=False, comment="配装类型")

    # 关联关系（待完整实现）
    character = relationship("Character", back_populates="weapon_recommendations")

    __table_args__ = (
        Index('idx_char_weapon_rec_char_id', 'character_id'),
    )