#!/usr/bin/env python3
"""
添加怪物示例数据

添加热门原神怪物的示例数据到数据库中
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(__file__))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from src.models.monster import Monster
from src.config import get_settings

# 怪物示例数据
MONSTER_SAMPLES = [
    # 史莱姆族群
    {
        "name": "大型火史莱姆", "name_en": "Large Pyro Slime", "category": "普通怪物", "family": "史莱姆",
        "element": "Pyro", "level": 30, "world_level": 2,
        "base_stats": {"hp": 8500, "atk": 420, "def": 180, "elemental_mastery": 0},
        "resistances": {"pyro": 50.0, "hydro": -50.0, "anemo": 10.0, "electro": 10.0, "dendro": 10.0, "cryo": -30.0, "geo": 10.0, "physical": 10.0},
        "description": "一只巨大的火元素史莱姆，身体呈现火红色，散发着灼热的气息。",
        "lore": "史莱姆是最常见的元素生物之一，它们由纯粹的元素能量构成，拥有简单的意识。",
        "behavior": "会向敌人发射火弹攻击，当生命值较低时会变得更加狂暴。",
        "regions": ["Mondstadt", "Liyue", "Inazuma"],
        "locations": [
            {"region": "Mondstadt", "area": "风起地", "coordinates": "明冠峡"},
            {"region": "Liyue", "area": "璃月港周边", "coordinates": "石门"}
        ],
        "abilities": [
            {"name": "火弹射击", "description": "发射炽热的火弹攻击敌人", "damage_type": "元素伤害", "element": "Pyro"},
            {"name": "爆炸冲撞", "description": "身体膨胀后向敌人冲撞并爆炸", "damage_type": "元素伤害", "element": "Pyro"}
        ],
        "drops": [
            {"item_name": "史莱姆凝液", "item_type": "素材", "drop_rate": 100.0, "quantity_min": 2, "quantity_max": 3},
            {"item_name": "史莱姆清液", "item_type": "素材", "drop_rate": 50.0, "quantity_min": 1, "quantity_max": 2},
            {"item_name": "史莱姆原浆", "item_type": "素材", "drop_rate": 15.0, "quantity_min": 1, "quantity_max": 1}
        ],
        "weak_points": ["冰元素攻击"], "immunities": ["燃烧"],
        "aggro_range": 8.0, "respawn_time": 180,
        "exp_reward": 200, "mora_reward": 100, "is_active": True
    },
    {
        "name": "雷音权现", "name_en": "Thunder Manifestation", "category": "世界Boss", "family": "无相系列",
        "element": "Electro", "level": 60, "world_level": 5,
        "base_stats": {"hp": 142800, "atk": 850, "def": 650, "elemental_mastery": 200},
        "resistances": {"pyro": 10.0, "hydro": 10.0, "anemo": 10.0, "electro": 70.0, "dendro": 10.0, "cryo": 10.0, "geo": 10.0, "physical": 30.0},
        "description": "由纯粹雷元素构成的强大生物，外形如同雷鸟，拥有操控雷电的能力。",
        "lore": "雷音权现是雷元素的化身，据说是由强烈的雷电风暴中诞生的神秘存在。",
        "behavior": "会召唤雷电攻击，能够飞行并进行空中打击，拥有多种雷电技能。",
        "regions": ["Inazuma"],
        "locations": [
            {"region": "Inazuma", "area": "鸣神岛", "coordinates": "无相雷电讨伐领域"}
        ],
        "abilities": [
            {"name": "雷电冲击", "description": "发射强力的雷电光束", "damage_type": "元素伤害", "element": "Electro"},
            {"name": "雷网束缚", "description": "在地面生成雷电网格", "damage_type": "元素伤害", "element": "Electro"},
            {"name": "天雷降临", "description": "从天空召唤雷电攻击", "damage_type": "元素伤害", "element": "Electro"},
            {"name": "雷鸟冲撞", "description": "化身雷鸟进行高速冲撞", "damage_type": "物理伤害", "element": "Electro"}
        ],
        "drops": [
            {"item_name": "雷霆数珠", "item_type": "突破素材", "drop_rate": 100.0, "quantity_min": 1, "quantity_max": 1},
            {"item_name": "最胜紫晶块", "item_type": "突破素材", "drop_rate": 30.0, "quantity_min": 1, "quantity_max": 2},
            {"item_name": "最胜紫晶碎屑", "item_type": "突破素材", "drop_rate": 70.0, "quantity_min": 2, "quantity_max": 3}
        ],
        "weak_points": ["元素反应", "弱点核心"], "immunities": ["感电", "雷元素异常状态"],
        "aggro_range": 15.0, "respawn_time": 180,
        "exp_reward": 800, "mora_reward": 600, "is_active": True
    },
    {
        "name": "丘丘人射手", "name_en": "Hilichurl Shooter", "category": "普通怪物", "family": "丘丘人",
        "element": None, "level": 25, "world_level": 1,
        "base_stats": {"hp": 3200, "atk": 290, "def": 120, "elemental_mastery": 0},
        "resistances": {"pyro": 10.0, "hydro": 10.0, "anemo": 10.0, "electro": 10.0, "dendro": 10.0, "cryo": 10.0, "geo": 10.0, "physical": 30.0},
        "description": "手持弓箭的丘丘人，能够进行远程攻击，是丘丘人部落的重要战力。",
        "lore": "丘丘人是提瓦特大陆上古老的种族，拥有自己的文化和语言。",
        "behavior": "会保持距离进行弓箭攻击，被近身时会后退并继续射击。",
        "regions": ["Mondstadt", "Liyue", "Inazuma", "Sumeru"],
        "locations": [
            {"region": "Mondstadt", "area": "达达乌帕谷", "coordinates": "丘丘人营地"},
            {"region": "Liyue", "area": "石门", "coordinates": "废墟遗址"}
        ],
        "abilities": [
            {"name": "箭矢射击", "description": "发射普通箭矢攻击敌人", "damage_type": "物理伤害", "element": None},
            {"name": "蓄力射击", "description": "蓄力发射威力更强的箭矢", "damage_type": "物理伤害", "element": None}
        ],
        "drops": [
            {"item_name": "破损的面具", "item_type": "素材", "drop_rate": 100.0, "quantity_min": 1, "quantity_max": 2},
            {"item_name": "污秽的面具", "item_type": "素材", "drop_rate": 25.0, "quantity_min": 1, "quantity_max": 1},
            {"item_name": "箭簇", "item_type": "素材", "drop_rate": 60.0, "quantity_min": 1, "quantity_max": 3}
        ],
        "weak_points": ["头部"], "immunities": [],
        "aggro_range": 12.0, "respawn_time": 120,
        "exp_reward": 150, "mora_reward": 75, "is_active": True
    },
    {
        "name": "深渊法师·水", "name_en": "Abyss Mage (Hydro)", "category": "精英怪物", "family": "深渊法师",
        "element": "Hydro", "level": 45, "world_level": 3,
        "base_stats": {"hp": 18500, "atk": 520, "def": 280, "elemental_mastery": 150},
        "resistances": {"pyro": -30.0, "hydro": 50.0, "anemo": 10.0, "electro": 10.0, "dendro": 10.0, "cryo": 10.0, "geo": 10.0, "physical": 10.0},
        "description": "掌握水元素魔法的深渊法师，被水元素护盾保护，拥有强大的魔法攻击能力。",
        "lore": "深渊法师是深渊教团的重要成员，拥有古老而邪恶的魔法力量。",
        "behavior": "会生成水元素护盾保护自己，使用各种水元素魔法攻击敌人。",
        "regions": ["Mondstadt", "Liyue", "Inazuma"],
        "locations": [
            {"region": "Mondstadt", "area": "风龙废墟", "coordinates": "深渊法师据点"},
            {"region": "Liyue", "area": "层岩巨渊", "coordinates": "地下洞穴"}
        ],
        "abilities": [
            {"name": "水弹术", "description": "发射水元素弹丸攻击", "damage_type": "元素伤害", "element": "Hydro"},
            {"name": "水元素护盾", "description": "生成水元素护盾保护自身", "damage_type": "防护", "element": "Hydro"},
            {"name": "水波冲击", "description": "产生水波向四周扩散", "damage_type": "元素伤害", "element": "Hydro"},
            {"name": "瞬移", "description": "短距离瞬间移动", "damage_type": "位移", "element": None}
        ],
        "drops": [
            {"item_name": "地脉的旧枝", "item_type": "素材", "drop_rate": 100.0, "quantity_min": 2, "quantity_max": 3},
            {"item_name": "地脉的枯叶", "item_type": "素材", "drop_rate": 50.0, "quantity_min": 1, "quantity_max": 2},
            {"item_name": "混沌装置", "item_type": "素材", "drop_rate": 30.0, "quantity_min": 1, "quantity_max": 1}
        ],
        "weak_points": ["护盾破除"], "immunities": ["潮湿"],
        "aggro_range": 10.0, "respawn_time": 300,
        "exp_reward": 400, "mora_reward": 250, "is_active": True
    },
    {
        "name": "遗迹守卫", "name_en": "Ruin Guard", "category": "精英怪物", "family": "遗迹守卫",
        "element": None, "level": 50, "world_level": 4,
        "base_stats": {"hp": 45000, "atk": 680, "def": 450, "elemental_mastery": 0},
        "resistances": {"pyro": 10.0, "hydro": 10.0, "anemo": 10.0, "electro": 10.0, "dendro": 10.0, "cryo": 10.0, "geo": 10.0, "physical": 70.0},
        "description": "古代遗迹中的自动战斗机械，拥有强大的物理攻击力和高防御力。",
        "lore": "遗迹守卫是古代文明留下的自动防御装置，至今仍在忠实地执行着守护任务。",
        "behavior": "会发射导弹攻击，进行旋转攻击，攻击弱点时会暂时失效。",
        "regions": ["Mondstadt", "Liyue", "Inazuma", "Sumeru"],
        "locations": [
            {"region": "Liyue", "area": "归离原", "coordinates": "古代遗迹"},
            {"region": "Mondstadt", "area": "千风神殿", "coordinates": "遗迹深处"}
        ],
        "abilities": [
            {"name": "导弹齐射", "description": "发射多枚导弹进行轰炸", "damage_type": "物理伤害", "element": None},
            {"name": "旋转攻击", "description": "原地旋转并用拳头攻击", "damage_type": "物理伤害", "element": None},
            {"name": "冲撞攻击", "description": "向前冲撞造成大量伤害", "damage_type": "物理伤害", "element": None},
            {"name": "跺地震击", "description": "跺地产生冲击波", "damage_type": "物理伤害", "element": None}
        ],
        "drops": [
            {"item_name": "混沌装置", "item_type": "突破素材", "drop_rate": 100.0, "quantity_min": 1, "quantity_max": 2},
            {"item_name": "混沌回路", "item_type": "突破素材", "drop_rate": 40.0, "quantity_min": 1, "quantity_max": 1},
            {"item_name": "混沌炉心", "item_type": "突破素材", "drop_rate": 10.0, "quantity_min": 1, "quantity_max": 1}
        ],
        "weak_points": ["眼部核心"], "immunities": ["物理异常状态"],
        "aggro_range": 12.0, "respawn_time": 300,
        "exp_reward": 500, "mora_reward": 350, "is_active": True
    },
    {
        "name": "愚人众火铳重卫", "name_en": "Fatui Pyro Agent", "category": "精英怪物", "family": "愚人众先遣队",
        "element": "Pyro", "level": 55, "world_level": 5,
        "base_stats": {"hp": 28000, "atk": 720, "def": 320, "elemental_mastery": 100},
        "resistances": {"pyro": 50.0, "hydro": -20.0, "anemo": 10.0, "electro": 10.0, "dendro": -10.0, "cryo": -50.0, "geo": 10.0, "physical": 20.0},
        "description": "至冬国愚人众的精英战士，装备有火元素武器，战斗技巧高超。",
        "lore": "愚人众是至冬国的军事组织，其成员都是训练有素的战士。",
        "behavior": "会进入隐身状态发动偷袭，使用火焰攻击，配合其他愚人众成员作战。",
        "regions": ["Mondstadt", "Liyue", "Inazuma"],
        "locations": [
            {"region": "Mondstadt", "area": "龙脊雪山", "coordinates": "愚人众营地"},
            {"region": "Liyue", "area": "璃月港", "coordinates": "愚人众据点"}
        ],
        "abilities": [
            {"name": "隐身突袭", "description": "进入隐身状态并发动突然攻击", "damage_type": "物理伤害", "element": "Pyro"},
            {"name": "火焰斩击", "description": "使用火焰附魔的武器攻击", "damage_type": "元素伤害", "element": "Pyro"},
            {"name": "火焰冲刺", "description": "带着火焰向敌人冲刺", "damage_type": "元素伤害", "element": "Pyro"},
            {"name": "爆炸刀刃", "description": "投掷爆炸性的火焰刀刃", "damage_type": "元素伤害", "element": "Pyro"}
        ],
        "drops": [
            {"item_name": "新兵的徽记", "item_type": "突破素材", "drop_rate": 100.0, "quantity_min": 2, "quantity_max": 3},
            {"item_name": "士官的徽记", "item_type": "突破素材", "drop_rate": 40.0, "quantity_min": 1, "quantity_max": 1},
            {"item_name": "尉官的徽记", "item_type": "突破素材", "drop_rate": 15.0, "quantity_min": 1, "quantity_max": 1}
        ],
        "weak_points": ["冰元素攻击"], "immunities": ["燃烧"],
        "aggro_range": 10.0, "respawn_time": 240,
        "exp_reward": 450, "mora_reward": 300, "is_active": True
    },
    {
        "name": "古岩龙蜥", "name_en": "Geovishap", "category": "精英怪物", "family": "古岩龙蜥",
        "element": "Geo", "level": 65, "world_level": 6,
        "base_stats": {"hp": 55000, "atk": 850, "def": 680, "elemental_mastery": 50},
        "resistances": {"pyro": 10.0, "hydro": 10.0, "anemo": 10.0, "electro": 10.0, "dendro": 10.0, "cryo": 10.0, "geo": 70.0, "physical": 30.0},
        "description": "古老的岩元素生物，拥有坚硬的外壳和强大的岩元素攻击能力。",
        "lore": "龙蜥是提瓦特大陆的古老生物，据说与岩元素之神有着某种联系。",
        "behavior": "会钻入地下发动攻击，创造岩元素障壁，使用滚动攻击。",
        "regions": ["Liyue", "Inazuma"],
        "locations": [
            {"region": "Liyue", "area": "南天门", "coordinates": "岩元素富集区"},
            {"region": "Liyue", "area": "孤云阁", "coordinates": "海岸洞穴"}
        ],
        "abilities": [
            {"name": "地底突袭", "description": "钻入地下后突然冲出攻击", "damage_type": "物理伤害", "element": "Geo"},
            {"name": "岩柱冲击", "description": "召唤岩柱从地面升起", "damage_type": "元素伤害", "element": "Geo"},
            {"name": "滚动冲撞", "description": "蜷缩成球状进行滚动攻击", "damage_type": "物理伤害", "element": "Geo"},
            {"name": "岩甲护身", "description": "生成岩元素护盾保护自己", "damage_type": "防护", "element": "Geo"}
        ],
        "drops": [
            {"item_name": "坚牢黄玉碎屑", "item_type": "突破素材", "drop_rate": 70.0, "quantity_min": 2, "quantity_max": 3},
            {"item_name": "坚牢黄玉断片", "item_type": "突破素材", "drop_rate": 40.0, "quantity_min": 1, "quantity_max": 2},
            {"item_name": "幼岩龙蜥之角", "item_type": "特殊素材", "drop_rate": 100.0, "quantity_min": 1, "quantity_max": 1}
        ],
        "weak_points": ["重击打断"], "immunities": ["结晶反应免疫"],
        "aggro_range": 8.0, "respawn_time": 300,
        "exp_reward": 600, "mora_reward": 400, "is_active": True
    },
    {
        "name": "飘浮灵", "name_en": "Specter", "category": "普通怪物", "family": "飘浮灵",
        "element": "Anemo", "level": 40, "world_level": 3,
        "base_stats": {"hp": 12000, "atk": 380, "def": 200, "elemental_mastery": 120},
        "resistances": {"pyro": -20.0, "hydro": 10.0, "anemo": 50.0, "electro": 10.0, "dendro": 10.0, "cryo": 10.0, "geo": 10.0, "physical": -50.0},
        "description": "由风元素构成的飘浮生物，能够在空中自由移动，攻击方式多变。",
        "lore": "飘浮灵是稻妻地区特有的元素生物，与当地的雷电环境密切相关。",
        "behavior": "会在空中飘浮移动，发射元素攻击，死亡时会产生爆炸。",
        "regions": ["Inazuma"],
        "locations": [
            {"region": "Inazuma", "area": "鸣神岛", "coordinates": "雷电环绕区域"},
            {"region": "Inazuma", "area": "海祇岛", "coordinates": "珊瑚宫周边"}
        ],
        "abilities": [
            {"name": "风弹射击", "description": "发射风元素弹丸攻击", "damage_type": "元素伤害", "element": "Anemo"},
            {"name": "旋风吸引", "description": "产生旋风吸引敌人", "damage_type": "元素伤害", "element": "Anemo"},
            {"name": "死亡爆炸", "description": "死亡时产生元素爆炸", "damage_type": "元素伤害", "element": "Anemo"}
        ],
        "drops": [
            {"item_name": "飘浮晶化核", "item_type": "特殊素材", "drop_rate": 100.0, "quantity_min": 1, "quantity_max": 2},
            {"item_name": "飘浮浓缩物", "item_type": "素材", "drop_rate": 60.0, "quantity_min": 1, "quantity_max": 2}
        ],
        "weak_points": ["火元素攻击"], "immunities": ["风压抗性"],
        "aggro_range": 10.0, "respawn_time": 120,
        "exp_reward": 300, "mora_reward": 180, "is_active": True
    },
    {
        "name": "蕈兽·草", "name_en": "Fungi (Dendro)", "category": "普通怪物", "family": "蕈兽",
        "element": "Dendro", "level": 35, "world_level": 2,
        "base_stats": {"hp": 9500, "atk": 340, "def": 160, "elemental_mastery": 80},
        "resistances": {"pyro": -30.0, "hydro": 10.0, "anemo": 10.0, "electro": 10.0, "dendro": 50.0, "cryo": 10.0, "geo": 10.0, "physical": 10.0},
        "description": "由草元素能量聚集形成的蕈类生物，拥有治愈和攻击双重能力。",
        "lore": "蕈兽是须弥地区的原生生物，与当地的植被生态系统密切相关。",
        "behavior": "会释放草元素孢子攻击，能够治疗同伴，在草元素环境中活跃。",
        "regions": ["Sumeru"],
        "locations": [
            {"region": "Sumeru", "area": "须弥城", "coordinates": "雨林深处"},
            {"region": "Sumeru", "area": "道成林", "coordinates": "蕈兽栖息地"}
        ],
        "abilities": [
            {"name": "孢子喷射", "description": "喷射草元素孢子攻击敌人", "damage_type": "元素伤害", "element": "Dendro"},
            {"name": "治愈光环", "description": "为周围同伴提供治疗", "damage_type": "治疗", "element": "Dendro"},
            {"name": "根须束缚", "description": "从地下伸出根须束缚敌人", "damage_type": "控制", "element": "Dendro"}
        ],
        "drops": [
            {"item_name": "蕈兽孢子", "item_type": "特殊素材", "drop_rate": 100.0, "quantity_min": 2, "quantity_max": 3},
            {"item_name": "荧光孢粉", "item_type": "素材", "drop_rate": 50.0, "quantity_min": 1, "quantity_max": 2},
            {"item_name": "孢囊晶化核", "item_type": "素材", "drop_rate": 25.0, "quantity_min": 1, "quantity_max": 1}
        ],
        "weak_points": ["火元素攻击"], "immunities": ["草元素异常状态"],
        "aggro_range": 6.0, "respawn_time": 180,
        "exp_reward": 250, "mora_reward": 150, "is_active": True
    },
    {
        "name": "镀金旅团·斧兵", "name_en": "Gilded Brigade Axeman", "category": "精英怪物", "family": "镀金旅团",
        "element": None, "level": 48, "world_level": 4,
        "base_stats": {"hp": 22000, "atk": 580, "def": 260, "elemental_mastery": 0},
        "resistances": {"pyro": 10.0, "hydro": 10.0, "anemo": 10.0, "electro": 10.0, "dendro": 10.0, "cryo": 10.0, "geo": 10.0, "physical": 25.0},
        "description": "镀金旅团的重装战士，手持大斧，拥有强大的物理攻击力。",
        "lore": "镀金旅团是须弥地区的雇佣兵组织，以金钱为目标进行各种任务。",
        "behavior": "会使用大斧进行重击攻击，拥有冲锋技能，攻击力强但速度较慢。",
        "regions": ["Sumeru"],
        "locations": [
            {"region": "Sumeru", "area": "阿如村", "coordinates": "镀金旅团据点"},
            {"region": "Sumeru", "area": "赤王陵", "coordinates": "沙漠遗迹"}
        ],
        "abilities": [
            {"name": "重斧劈砍", "description": "使用大斧进行强力攻击", "damage_type": "物理伤害", "element": None},
            {"name": "旋风斩", "description": "360度旋转攻击周围敌人", "damage_type": "物理伤害", "element": None},
            {"name": "冲锋突击", "description": "向前冲锋并发动攻击", "damage_type": "物理伤害", "element": None}
        ],
        "drops": [
            {"item_name": "褪色红绸", "item_type": "特殊素材", "drop_rate": 100.0, "quantity_min": 1, "quantity_max": 2},
            {"item_name": "镶边红绸", "item_type": "特殊素材", "drop_rate": 40.0, "quantity_min": 1, "quantity_max": 1},
            {"item_name": "金织红绸", "item_type": "特殊素材", "drop_rate": 15.0, "quantity_min": 1, "quantity_max": 1}
        ],
        "weak_points": ["背部"], "immunities": [],
        "aggro_range": 8.0, "respawn_time": 240,
        "exp_reward": 380, "mora_reward": 220, "is_active": True
    }
]

async def add_monster_samples():
    """添加怪物示例数据到数据库"""
    try:
        settings = get_settings()

        # 创建数据库引擎
        engine = create_async_engine(settings.database_url)
        async_session = sessionmaker(engine, class_=AsyncSession)

        async with async_session() as session:
            print("🔍 检查现有怪物数据...")

            # 检查是否已有怪物数据
            result = await session.execute(text("SELECT COUNT(*) FROM monsters"))
            count = result.scalar()

            if count > 0:
                print(f"⚠️  数据库中已有 {count} 个怪物，跳过示例数据添加")
                return

            print(f"📦 准备添加 {len(MONSTER_SAMPLES)} 个怪物示例数据...")

            # 添加示例数据
            for monster_data in MONSTER_SAMPLES:
                monster = Monster(**monster_data)
                session.add(monster)
                print(f"   ✓ 添加怪物: {monster_data['name']}")

            # 提交事务
            await session.commit()
            print(f"✅ 成功添加 {len(MONSTER_SAMPLES)} 个怪物示例数据！")

    except Exception as e:
        print(f"❌ 添加怪物示例数据失败: {str(e)}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    print("🚀 开始添加怪物示例数据...")
    asyncio.run(add_monster_samples())
    print("🎉 怪物示例数据添加完成！")