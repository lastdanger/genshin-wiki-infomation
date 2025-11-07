"""
圣遗物模型

存储原神圣遗物的基础信息、属性、套装效果等数据
"""
from sqlalchemy import Column, String, Integer, Text, Boolean, Index
from sqlalchemy.dialects.postgresql import JSONB

from src.models.base import BaseModel


class Artifact(BaseModel):
    """
    圣遗物模型

    存储圣遗物的基础信息、属性、套装效果等数据
    """

    __tablename__ = "artifacts"

    # 基础信息
    name = Column(String(100), nullable=False, comment="圣遗物名称（中文）")
    name_en = Column(String(100), nullable=True, comment="圣遗物英文名")
    set_name = Column(String(100), nullable=False, comment="套装名称")
    set_name_en = Column(String(100), nullable=True, comment="套装英文名")

    # 圣遗物部位
    slot = Column(String(30), nullable=False, comment="圣遗物部位（flower, plume, sands, goblet, circlet）")

    # 稀有度
    rarity = Column(Integer, nullable=False, comment="星级稀有度（3-5星）")

    # 描述信息
    description = Column(Text, nullable=True, comment="圣遗物描述")
    lore = Column(Text, nullable=True, comment="圣遗物背景故事")

    # 主属性信息
    main_stat_type = Column(String(50), nullable=False, comment="主属性类型")
    main_stat_value = Column(String(20), nullable=False, comment="主属性数值")

    # 副属性信息
    sub_stats = Column(JSONB, nullable=True, comment="副属性列表（JSON格式）")

    # 套装效果
    set_effects = Column(JSONB, nullable=False, comment="套装效果（2件套和4件套效果）")

    # 获取方式
    source = Column(String(50), nullable=True, comment="获取方式")
    domain_name = Column(String(100), nullable=True, comment="副本名称")

    # 属性成长
    stat_progression = Column(JSONB, nullable=True, comment="属性成长数据")

    # 最大等级
    max_level = Column(Integer, nullable=False, default=20, comment="最大等级")

    # 是否为套装件
    is_set_piece = Column(Boolean, nullable=False, default=True, comment="是否为套装圣遗物")

    def __repr__(self):
        return f"<Artifact(id={self.id}, name='{self.name}', set_name='{self.set_name}', slot='{self.slot}')>"

    @classmethod
    def get_artifact_slots(cls):
        """获取圣遗物部位列表"""
        return ['flower', 'plume', 'sands', 'goblet', 'circlet']

    @classmethod
    def get_slot_names(cls):
        """获取圣遗物部位中文名映射"""
        return {
            'flower': '生之花',
            'plume': '死之羽',
            'sands': '时之沙',
            'goblet': '空之杯',
            'circlet': '理之冠'
        }

    @classmethod
    def get_main_stat_types(cls):
        """获取主属性类型列表"""
        return [
            'HP', 'ATK', 'DEF',  # 固定值
            'HP%', 'ATK%', 'DEF%',  # 百分比
            'Energy Recharge', 'Elemental Mastery',  # 特殊属性
            'CRIT Rate', 'CRIT DMG',  # 暴击属性
            'Healing Bonus',  # 治疗加成
            'Pyro DMG Bonus', 'Hydro DMG Bonus', 'Anemo DMG Bonus',  # 元素伤害加成
            'Electro DMG Bonus', 'Dendro DMG Bonus', 'Cryo DMG Bonus', 'Geo DMG Bonus',
            'Physical DMG Bonus'  # 物理伤害加成
        ]

    @classmethod
    def get_sub_stat_types(cls):
        """获取副属性类型列表"""
        return [
            'HP', 'ATK', 'DEF',  # 固定值
            'HP%', 'ATK%', 'DEF%',  # 百分比
            'Energy Recharge', 'Elemental Mastery',  # 特殊属性
            'CRIT Rate', 'CRIT DMG'  # 暴击属性
        ]

    @classmethod
    def get_sources(cls):
        """获取获取方式列表"""
        return ['副本', '世界BOSS', '周本BOSS', '活动', '商店', '合成']

    @classmethod
    def get_rarities(cls):
        """获取稀有度列表"""
        return [3, 4, 5]

    def get_slot_display(self):
        """获取部位中文显示名"""
        slot_names = self.get_slot_names()
        return slot_names.get(self.slot, self.slot)

    def get_main_stat_display(self):
        """获取主属性显示"""
        stat_names = {
            'HP': '生命值',
            'ATK': '攻击力',
            'DEF': '防御力',
            'HP%': '生命值%',
            'ATK%': '攻击力%',
            'DEF%': '防御力%',
            'Energy Recharge': '元素充能效率',
            'Elemental Mastery': '元素精通',
            'CRIT Rate': '暴击率',
            'CRIT DMG': '暴击伤害',
            'Healing Bonus': '治疗加成',
            'Pyro DMG Bonus': '火元素伤害加成',
            'Hydro DMG Bonus': '水元素伤害加成',
            'Anemo DMG Bonus': '风元素伤害加成',
            'Electro DMG Bonus': '雷元素伤害加成',
            'Dendro DMG Bonus': '草元素伤害加成',
            'Cryo DMG Bonus': '冰元素伤害加成',
            'Geo DMG Bonus': '岩元素伤害加成',
            'Physical DMG Bonus': '物理伤害加成'
        }
        return stat_names.get(self.main_stat_type, self.main_stat_type)

    def get_rarity_display(self):
        """获取稀有度显示"""
        return '★' * (self.rarity or 0)

    def is_five_star(self):
        """是否为五星圣遗物"""
        return self.rarity == 5

    def is_four_star(self):
        """是否为四星圣遗物"""
        return self.rarity == 4

    def has_set_effect(self, pieces_count):
        """检查是否有指定件数的套装效果"""
        if not self.set_effects:
            return False
        return str(pieces_count) in self.set_effects

    def get_set_effect(self, pieces_count):
        """获取指定件数的套装效果"""
        if not self.has_set_effect(pieces_count):
            return None
        return self.set_effects.get(str(pieces_count))

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'name_en': self.name_en,
            'set_name': self.set_name,
            'set_name_en': self.set_name_en,
            'slot': self.slot,
            'slot_display': self.get_slot_display(),
            'rarity': self.rarity,
            'rarity_display': self.get_rarity_display(),
            'description': self.description,
            'lore': self.lore,
            'main_stat_type': self.main_stat_type,
            'main_stat_value': self.main_stat_value,
            'main_stat_display': self.get_main_stat_display(),
            'sub_stats': self.sub_stats,
            'set_effects': self.set_effects,
            'source': self.source,
            'domain_name': self.domain_name,
            'stat_progression': self.stat_progression,
            'max_level': self.max_level,
            'is_set_piece': self.is_set_piece,
            'is_five_star': self.is_five_star(),
            'is_four_star': self.is_four_star(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    # 数据库索引
    __table_args__ = (
        Index('idx_artifacts_set_name', 'set_name'),
        Index('idx_artifacts_slot', 'slot'),
        Index('idx_artifacts_rarity', 'rarity'),
        Index('idx_artifacts_source', 'source'),
        Index('idx_artifacts_main_stat', 'main_stat_type'),
        Index('idx_artifacts_set_slot', 'set_name', 'slot'),  # 复合索引
    )