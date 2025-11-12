"""
SQLAlchemy 数据模型

导入所有数据模型，确保它们能被SQLAlchemy识别并创建表
"""

# 导入基础模型
from .base import Base, TimestampMixin, BaseModel

# 导入所有数据模型
from .character import Character
from .character_skill import CharacterSkill
from .character_talent import CharacterTalent
from .character_weapon_recommendation import CharacterWeaponRecommendation
from .character_artifact_recommendation import CharacterArtifactRecommendation
from .weapon import Weapon
from .artifact import Artifact
from .artifact_set import ArtifactSet
from .monster import Monster
from .image import Image

# 确保所有模型都被导入，这样 Base.metadata.create_all() 才能找到它们
__all__ = [
    "Base",
    "TimestampMixin",
    "BaseModel",
    "Character",
    "CharacterSkill",
    "CharacterTalent",
    "CharacterWeaponRecommendation",
    "CharacterArtifactRecommendation",
    "Weapon",
    "Artifact",
    "ArtifactSet",
    "Monster",
    "Image",
]