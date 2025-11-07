"""
怪物模型

存储原神怪物的基础信息、属性、技能和掉落物等数据
"""
from sqlalchemy import Column, String, Integer, Text, Float, Boolean, Index
from sqlalchemy.dialects.postgresql import JSONB

from src.models.base import BaseModel


class Monster(BaseModel):
    """
    怪物模型

    存储怪物的基础信息、战斗属性、技能、掉落物等数据
    """

    __tablename__ = "monsters"

    # 基础信息
    name = Column(String(100), nullable=False, comment="怪物名称（中文）")
    name_en = Column(String(100), nullable=True, comment="怪物英文名")

    # 怪物分类
    category = Column(String(50), nullable=False, comment="怪物类别（普通怪物、精英怪物、Boss等）")
    family = Column(String(50), nullable=False, comment="怪物族群（史莱姆、丘丘人、深渊法师等）")
    element = Column(String(20), nullable=True, comment="元素属性（Pyro, Hydro, Anemo等）")

    # 等级信息
    level = Column(Integer, nullable=False, comment="怪物等级")
    world_level = Column(Integer, nullable=True, comment="世界等级要求")

    # 战斗属性（JSONB格式存储）
    base_stats = Column(
        JSONB,
        nullable=False,
        comment="基础属性 {hp: int, atk: int, def: int, elemental_mastery: int}"
    )

    # 抗性信息
    resistances = Column(
        JSONB,
        nullable=True,
        comment="元素抗性 {pyro: float, hydro: float, anemo: float, electro: float, dendro: float, cryo: float, geo: float, physical: float}"
    )

    # 描述信息
    description = Column(Text, nullable=True, comment="怪物描述")
    lore = Column(Text, nullable=True, comment="怪物背景故事")
    behavior = Column(Text, nullable=True, comment="行为特点")

    # 位置信息
    regions = Column(JSONB, nullable=True, comment="出现地区列表")
    locations = Column(JSONB, nullable=True, comment="具体位置信息")

    # 技能和能力
    abilities = Column(
        JSONB,
        nullable=True,
        comment="技能列表 [{name: str, description: str, damage_type: str, element: str}]"
    )

    # 掉落物信息
    drops = Column(
        JSONB,
        nullable=True,
        comment="掉落物列表 [{item_name: str, drop_rate: float, quantity_min: int, quantity_max: int}]"
    )

    # 特殊机制
    weak_points = Column(JSONB, nullable=True, comment="弱点信息")
    immunities = Column(JSONB, nullable=True, comment="免疫效果列表")

    # 战斗相关
    aggro_range = Column(Float, nullable=True, comment="仇恨范围（米）")
    respawn_time = Column(Integer, nullable=True, comment="重生时间（秒）")

    # 奖励信息
    exp_reward = Column(Integer, nullable=True, comment="击败经验奖励")
    mora_reward = Column(Integer, nullable=True, comment="摩拉奖励")

    # 是否激活状态
    is_active = Column(Boolean, default=True, comment="是否在游戏中激活")

    # 数据库索引
    __table_args__ = (
        Index('idx_monsters_category', 'category'),
        Index('idx_monsters_family', 'family'),
        Index('idx_monsters_element', 'element'),
        Index('idx_monsters_level', 'level'),
        Index('idx_monsters_world_level', 'world_level'),
        # 全文搜索索引
        Index(
            'idx_monsters_search',
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
        return f"<Monster(id={self.id}, name='{self.name}', category='{self.category}', level={self.level})>"

    @property
    def display_name(self) -> str:
        """显示名称（优先中文名）"""
        return self.name or self.name_en or f"Monster #{self.id}"

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
    def elemental_mastery(self) -> int:
        """元素精通"""
        return self.base_stats.get('elemental_mastery', 0) if self.base_stats else 0

    @property
    def total_drops(self) -> int:
        """掉落物总数"""
        return len(self.drops) if self.drops else 0

    @property
    def ability_count(self) -> int:
        """技能数量"""
        return len(self.abilities) if self.abilities else 0

    def get_resistance(self, element: str) -> float:
        """获取特定元素的抗性值"""
        if not self.resistances:
            return 0.0
        return self.resistances.get(element.lower(), 0.0)

    def has_weakness(self, element: str) -> bool:
        """检查是否对特定元素有弱点"""
        return self.get_resistance(element) < 0

    def is_immune_to(self, effect: str) -> bool:
        """检查是否对特定效果免疫"""
        if not self.immunities:
            return False
        return effect.lower() in [immunity.lower() for immunity in self.immunities]

    def get_drops_by_type(self, item_type: str = None) -> list:
        """根据类型筛选掉落物"""
        if not self.drops:
            return []

        if item_type is None:
            return self.drops

        return [drop for drop in self.drops if drop.get('type', '').lower() == item_type.lower()]

    def to_dict(self) -> dict:
        """转换为字典"""
        result = super().to_dict()

        # 添加计算属性
        result['total_drops'] = self.total_drops
        result['ability_count'] = self.ability_count

        return result

    @classmethod
    def get_categories(cls) -> list:
        """获取所有怪物类别"""
        return [
            '普通怪物',
            '精英怪物',
            '周本Boss',
            '世界Boss',
            '深渊法师',
            '无相系列',
            '古岩龙蜥',
            '遗迹系列',
            '愚人众',
            '其他'
        ]

    @classmethod
    def get_families(cls) -> list:
        """获取所有怪物族群"""
        return [
            '史莱姆',
            '丘丘人',
            '深渊法师',
            '深渊咏者',
            '遗迹守卫',
            '遗迹猎者',
            '愚人众先遣队',
            '无相系列',
            '魔偶剑鬼',
            '飘浮灵',
            '蕈兽',
            '镀金旅团',
            '兽境猎犬',
            '其他'
        ]

    @classmethod
    def get_elements(cls) -> list:
        """获取所有元素类型"""
        return ['Pyro', 'Hydro', 'Anemo', 'Electro', 'Dendro', 'Cryo', 'Geo', 'Physical']

    @classmethod
    def get_regions(cls) -> list:
        """获取所有地区"""
        return ['Mondstadt', 'Liyue', 'Inazuma', 'Sumeru', 'Fontaine', 'Natlan', 'Snezhnaya']