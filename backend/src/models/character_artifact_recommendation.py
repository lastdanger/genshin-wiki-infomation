"""
角色圣遗物推荐关联模型（占位符）

将在Phase 5 (圣遗物功能) 完整实现
"""
from sqlalchemy import Column, String, Integer, Text, ForeignKey, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from src.models.base import BaseModel


class CharacterArtifactRecommendation(BaseModel):
    """角色圣遗物推荐模型（基础结构）"""

    __tablename__ = "character_artifact_recommendations"

    character_id = Column(Integer, ForeignKey('characters.id', ondelete='CASCADE'), nullable=False)
    artifact_id = Column(Integer, nullable=False, comment="圣遗物套装ID（待实现）")
    rating = Column(Integer, nullable=False, comment="推荐等级1-5星")
    explanation = Column(Text, nullable=False, comment="推荐理由")
    main_stats_priority = Column(JSONB, nullable=False, comment="主词条优先级")
    sub_stats_priority = Column(JSONB, nullable=False, comment="副词条优先级")
    build_type = Column(String(20), nullable=False, comment="配装类型")

    # 关联关系（待完整实现）
    character = relationship("Character", back_populates="artifact_recommendations")

    __table_args__ = (
        Index('idx_char_artifact_rec_char_id', 'character_id'),
    )