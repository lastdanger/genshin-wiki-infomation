"""
圣遗物套装模型

存储原神圣遗物套装的完整信息（包括套装和所有部件）
"""
from sqlalchemy import Column, String, Integer, Text, Index
from sqlalchemy.dialects.postgresql import JSONB

from src.models.base import BaseModel


class ArtifactSet(BaseModel):
    """
    圣遗物套装模型

    存储套装完整信息，包括套装效果和5个部件的详细信息
    """

    __tablename__ = "artifact_sets"

    # 基础信息
    set_name = Column(String(100), nullable=False, unique=True, comment="套装名称（中文）")
    set_name_en = Column(String(100), nullable=True, comment="套装英文名")

    # 套装TAG（如：元素类、充能类、物理类等）
    tags = Column(JSONB, nullable=True, comment="套装标签列表（JSON格式）")

    # 稀有度
    max_rarity = Column(Integer, nullable=False, default=5, comment="最高星级稀有度（3-5星）")

    # 套装效果
    two_piece_bonus = Column(Text, nullable=True, comment="2件套效果描述")
    four_piece_bonus = Column(Text, nullable=True, comment="4件套效果描述")

    # 描述信息
    description = Column(Text, nullable=True, comment="套装描述")

    # 获取方式
    source = Column(String(50), nullable=True, comment="获取方式（副本、世界BOSS等）")
    domain_name = Column(String(100), nullable=True, comment="副本名称")

    # 部件信息（JSONB格式存储5个部件）
    # 格式: [
    #   {
    #     "slot": "flower",
    #     "slot_cn": "生之花",
    #     "piece_name": "魔女的炎之花",
    #     "piece_name_en": null,
    #     "lore": "背景故事..."
    #   },
    #   ... (共5个部件)
    # ]
    pieces = Column(JSONB, nullable=True, comment="圣遗物部件列表（包含5个部件的详细信息）")

    def __repr__(self):
        return f"<ArtifactSet(id={self.id}, set_name='{self.set_name}', max_rarity={self.max_rarity})>"

    @classmethod
    def get_sources(cls):
        """获取获取方式列表"""
        return ['副本', '世界BOSS', '周本BOSS', '活动', '商店', '合成']

    @classmethod
    def get_rarities(cls):
        """获取稀有度列表"""
        return [3, 4, 5]

    def get_rarity_display(self):
        """获取稀有度显示"""
        return '★' * (self.max_rarity or 0)

    def is_five_star(self):
        """是否为五星套装"""
        return self.max_rarity == 5

    def is_four_star(self):
        """是否为四星套装"""
        return self.max_rarity == 4

    def has_two_piece_bonus(self):
        """是否有2件套效果"""
        return bool(self.two_piece_bonus)

    def has_four_piece_bonus(self):
        """是否有4件套效果"""
        return bool(self.four_piece_bonus)

    def get_piece_by_slot(self, slot: str):
        """根据部位获取部件信息"""
        if not self.pieces:
            return None
        for piece in self.pieces:
            if piece.get('slot') == slot:
                return piece
        return None

    def get_pieces_count(self):
        """获取部件数量"""
        return len(self.pieces) if self.pieces else 0

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'set_name': self.set_name,
            'set_name_en': self.set_name_en,
            'tags': self.tags,
            'max_rarity': self.max_rarity,
            'rarity_display': self.get_rarity_display(),
            'two_piece_bonus': self.two_piece_bonus,
            'four_piece_bonus': self.four_piece_bonus,
            'description': self.description,
            'source': self.source,
            'domain_name': self.domain_name,
            'is_five_star': self.is_five_star(),
            'is_four_star': self.is_four_star(),
            'has_two_piece_bonus': self.has_two_piece_bonus(),
            'has_four_piece_bonus': self.has_four_piece_bonus(),
            'pieces': self.pieces or [],
            'pieces_count': self.get_pieces_count(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    # 数据库索引
    __table_args__ = (
        Index('idx_artifact_sets_name', 'set_name'),
        Index('idx_artifact_sets_rarity', 'max_rarity'),
        Index('idx_artifact_sets_source', 'source'),
    )
