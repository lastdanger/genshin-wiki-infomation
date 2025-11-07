#!/usr/bin/env python3
"""
添加武器示例数据
"""
import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath('.'))

from sqlalchemy.ext.asyncio import AsyncSession
from src.db.session import AsyncSessionLocal
from src.services.weapon_service import WeaponService
from src.schemas.weapon import WeaponCreate
import structlog

logger = structlog.get_logger()

# 示例武器数据
SAMPLE_WEAPONS = [
    {
        "name": "护摩之杖",
        "name_en": "Staff of Homa",
        "weapon_type": "Polearm",
        "rarity": 5,
        "base_attack": 46,
        "secondary_stat": "暴击伤害%",
        "secondary_stat_value": "14.4%",
        "description": "在璃月匠人手中诞生的长枪，赤红的刀锋中蕴含着等同烈火的力量。",
        "lore": "「护摩」意为守护死者灵魂的烈火。在璃月的传统中，护摩之火能够燃烧一切邪祟，护送逝者的灵魂前往来世。",
        "passive_name": "无羁的朱赤之蝶",
        "passive_description": "生命值提升20%。此外，基于装备该武器的角色生命值上限的0.8%，获得攻击力加成。当装备该武器的角色生命值低于50%时，进一步获得1%基于生命值上限的攻击力加成。",
        "passive_stats": {
            "hp_bonus": 20,
            "atk_bonus_per_hp": 0.8,
            "low_hp_bonus": 1.0
        },
        "source": "祈愿",
        "max_level": 90,
        "ascension_materials": [
            {
                "level_range": "20-40",
                "materials": {
                    "凛风奔狼的断牙": 5,
                    "地脉的旧枝": 5,
                    "史莱姆凝液": 3
                },
                "mora_cost": 10000
            }
        ],
        "stat_progression": {
            "level_20": {"base_attack": 122, "secondary_stat_value": "25.1%"},
            "level_40": {"base_attack": 235, "secondary_stat_value": "36.5%"},
            "level_50": {"base_attack": 308, "secondary_stat_value": "42.2%"},
            "level_60": {"base_attack": 382, "secondary_stat_value": "47.9%"},
            "level_70": {"base_attack": 457, "secondary_stat_value": "53.6%"},
            "level_80": {"base_attack": 532, "secondary_stat_value": "59.3%"},
            "level_90": {"base_attack": 608, "secondary_stat_value": "66.2%"}
        }
    },
    {
        "name": "雷电将军的薙草之稻光",
        "name_en": "Engulfing Lightning",
        "weapon_type": "Polearm",
        "rarity": 5,
        "base_attack": 46,
        "secondary_stat": "元素充能效率%",
        "secondary_stat_value": "12.0%",
        "description": "闪电般的薙刀，是将军斩断一切野心与执念的象征。",
        "lore": "雷电将军的武器，蕴含着永恒的意志，如闪电般迅捷，如雷鸣般威严。",
        "passive_name": "嗜魔刀气",
        "passive_description": "攻击力获得基于元素充能效率超出100%部分的28%提升，至多通过这种方式获得80%攻击力提升。施放元素爆发后，获得「嗜魔」效果：无视敌人30%的防御力，该效果持续12秒。",
        "passive_stats": {
            "atk_bonus_per_er": 28,
            "max_atk_bonus": 80,
            "def_ignore": 30,
            "duration": 12
        },
        "source": "祈愿",
        "max_level": 90
    },
    {
        "name": "天空之脊",
        "name_en": "Skyward Spine",
        "weapon_type": "Polearm",
        "rarity": 5,
        "base_attack": 48,
        "secondary_stat": "元素充能效率%",
        "secondary_stat_value": "8.0%",
        "description": "象征风龙权威的长枪，其锋锐程度不逊色于能够洞穿天空的利齿。",
        "lore": "属于四风之龙的武器。细长的枪身如苍穹一般深邃，枪尖闪烁着星辰的光芒。",
        "passive_name": "斫断黑翼的利齿",
        "passive_description": "暴击率提升8%；普通攻击速度提升12%；普通攻击与重击命中敌人时，有50%概率触发真空刃，在小范围内造成额外40%攻击力的伤害。该效果每2秒只能触发一次。",
        "source": "祈愿",
        "max_level": 90
    },
    {
        "name": "和璞鸢",
        "name_en": "Primordial Jade Winged-Spear",
        "weapon_type": "Polearm",
        "rarity": 5,
        "base_attack": 48,
        "secondary_stat": "暴击率%",
        "secondary_stat_value": "4.8%",
        "description": "以坚硬的璞玉精雕细琢而成的仪仗用长枪，轻盈锐利。",
        "lore": "用最纯净的璞玉打造的长枪，是璃月港工匠技艺的集大成者，也是权力与地位的象征。",
        "passive_name": "化鹏",
        "passive_description": "命中敌人时，自身攻击力提升3.2%，持续6秒，最高可以叠加7层。该效果每0.3秒最多触发一次。拥有满层效果时，伤害提升12%。",
        "source": "祈愿",
        "max_level": 90
    },
    {
        "name": "狼的末路",
        "name_en": "Wolf's Gravestone",
        "weapon_type": "Claymore",
        "rarity": 5,
        "base_attack": 46,
        "secondary_stat": "攻击力%",
        "secondary_stat_value": "10.8%",
        "description": "从前在蒙德平原上游荡的大剑。厚重如岩的剑身上，仿佛还能感受到野狼的嚎叫。",
        "lore": "据说这把大剑曾是某位骑士团大团长的爱剑，在与群狼搏斗中沾染了狼王的血。",
        "passive_name": "如狼般狩猎者",
        "passive_description": "攻击力提升20%；攻击命中生命值低于30%的敌人时，队伍中所有成员的攻击力提升40%，持续12秒。该效果30秒只能触发一次。",
        "source": "祈愿",
        "max_level": 90
    },
    {
        "name": "无工之剑",
        "name_en": "The Unforged",
        "weapon_type": "Claymore",
        "rarity": 5,
        "base_attack": 46,
        "secondary_stat": "攻击力%",
        "secondary_stat_value": "10.8%",
        "description": "沉重厚实的大剑，由稀有金属锻造而成，削铁如泥。",
        "lore": "璃月匠人的杰作，用最坚硬的金属锻造，未经开锋便已锋利无比。",
        "passive_name": "金璋君临",
        "passive_description": "护盾强效提升20%。攻击命中敌人后，攻击力提升4%，持续8秒，最多叠加5层。该效果每0.3秒只能触发一次。此外，处于护盾保护下时，该效果的攻击力提升效果提高100%。",
        "source": "祈愿",
        "max_level": 90
    },
    {
        "name": "阿莫斯之弓",
        "name_en": "Amos' Bow",
        "weapon_type": "Bow",
        "rarity": 5,
        "base_attack": 46,
        "secondary_stat": "攻击力%",
        "secondary_stat_value": "10.8%",
        "description": "属于阿莫斯的弓，做工精细，威力强劲。",
        "lore": "阿莫斯是古代德卡拉庇安时期的传奇射手，这把弓见证了那个时代的风与自由。",
        "passive_name": "矢志不移",
        "passive_description": "普通攻击和重击造成的伤害提升12%；普通攻击或重击的箭矢发射后，伤害每经过0.1秒提升8%，至多提升5次。",
        "source": "祈愿",
        "max_level": 90
    },
    {
        "name": "终末嗟叹之诗",
        "name_en": "Elegy for the End",
        "weapon_type": "Bow",
        "rarity": 5,
        "base_attack": 46,
        "secondary_stat": "元素充能效率%",
        "secondary_stat_value": "12.0%",
        "description": "造型如竖琴一般的长弓，能够演奏出终末的乐章。",
        "lore": "这把弓拥有如竖琴般优美的造型，据说能演奏出催人泪下的哀歌。",
        "passive_name": "离别的思念之歌",
        "passive_description": "元素精通提升60点；元素战技或元素爆发命中敌人时，角色获得追思效果，攻击力提升20%，持续12秒，至多叠加2层。该效果每0.2秒至多触发一次。拥有2层追思效果时，队伍中所有角色元素精通提升100点，攻击力提升20%。",
        "source": "祈愿",
        "max_level": 90
    },
    {
        "name": "天空之刃",
        "name_en": "Skyward Blade",
        "weapon_type": "Sword",
        "rarity": 5,
        "base_attack": 46,
        "secondary_stat": "元素充能效率%",
        "secondary_stat_value": "12.0%",
        "description": "象征风龙权威的长剑，伴随长空的鸣啸，撕裂凝滞的长风与苍云。",
        "lore": "属于四风之龙的武器之一，轻如鸿毛却锋利如风刃。",
        "passive_name": "穿云侧月",
        "passive_description": "暴击率提升4%；施放元素爆发时，获得破空之势：移动速度提升10%，攻击速度提升10%，普通攻击与重击造成的伤害提升20%，持续12秒。",
        "source": "祈愿",
        "max_level": 90
    },
    {
        "name": "磐岩结绿",
        "name_en": "Summit Shaper",
        "weapon_type": "Sword",
        "rarity": 5,
        "base_attack": 46,
        "secondary_stat": "攻击力%",
        "secondary_stat_value": "10.8%",
        "description": "削切岩石如削切豆腐的利剑。金色的护手闪闪发光。",
        "lore": "璃月的名匠以最坚硬的岩石为材料锻造的宝剑，锋利程度超乎想象。",
        "passive_name": "金璋皇极",
        "passive_description": "护盾强效提升20%；攻击命中敌人后，攻击力提升4%，持续8秒，最多叠加5层。该效果每0.3秒只能触发一次。此外，处于护盾保护下时，该效果的攻击力提升效果提高100%。",
        "source": "祈愿",
        "max_level": 90
    },
    {
        "name": "天空之卷",
        "name_en": "Skyward Atlas",
        "weapon_type": "Catalyst",
        "rarity": 5,
        "base_attack": 48,
        "secondary_stat": "攻击力%",
        "secondary_stat_value": "7.2%",
        "description": "详尽记录了天空与大地间万事万物的厚重魔导器。",
        "lore": "属于四风之龙的法器，记载着古老的魔法知识和天空的秘密。",
        "passive_name": "万千浮游",
        "passive_description": "元素伤害加成提升12%；普通攻击命中时，有50%的概率获得高天流云的青睐，在15秒内主动寻找附近的敌人进行攻击，造成160%攻击力的伤害。该效果每30秒只能触发一次。",
        "source": "祈愿",
        "max_level": 90
    },
    {
        "name": "尘世之锁",
        "name_en": "Memory of Dust",
        "weapon_type": "Catalyst",
        "rarity": 5,
        "base_attack": 46,
        "secondary_stat": "攻击力%",
        "secondary_stat_value": "10.8%",
        "description": "能够封存岁月与历史的黄金法器，坚硬的外表下流转着温柔的光泽。",
        "lore": "以黄金打造的法器，据说能够封存记忆与时光，是璃月古老的珍宝。",
        "passive_name": "金璋护体",
        "passive_description": "护盾强效提升20%；攻击命中敌人后，攻击力提升4%，持续8秒，最多叠加5层。该效果每0.3秒只能触发一次。此外，处于护盾保护下时，该效果的攻击力提升效果提高100%。",
        "source": "祈愿",
        "max_level": 90
    },
    {
        "name": "龙脊长枪",
        "name_en": "Dragonspine Spear",
        "weapon_type": "Polearm",
        "rarity": 4,
        "base_attack": 41,
        "secondary_stat": "物理伤害加成%",
        "secondary_stat_value": "15.0%",
        "description": "以古老龙骨为枪杆制成的长枪，蕴含着冰霜的力量。",
        "lore": "在龙脊雪山的严寒中锻造而成，枪身散发着永不消融的寒气。",
        "passive_name": "霜葬",
        "passive_description": "攻击命中敌人后，会在敌人脚下生成霜花，造成80%攻击力的范围冰元素伤害。该效果每10秒只能触发一次。",
        "source": "锻造",
        "max_level": 90
    },
    {
        "name": "原木刀",
        "name_en": "Sapwood Blade",
        "weapon_type": "Sword",
        "rarity": 4,
        "base_attack": 44,
        "secondary_stat": "元素充能效率%",
        "secondary_stat_value": "6.7%",
        "description": "由坚韧木材制成的训练用木剑，经过特殊工艺处理。",
        "lore": "须弥学院学者们使用的训练武器，虽是木制但经过特殊工艺强化。",
        "passive_name": "森林的教诲",
        "passive_description": "触发燃烧、原激化、超激化、蔓激化、绽放、超绽放或烈绽放后，将在角色周围产生至多存在10秒的「种识之叶」。拾取种识之叶的角色元素精通提升60点，持续12秒。每20秒至多通过这种方式触发一次。角色处于队伍后台时也能触发。",
        "source": "锻造",
        "max_level": 90
    },
    {
        "name": "黑剑",
        "name_en": "The Black Sword",
        "weapon_type": "Sword",
        "rarity": 4,
        "base_attack": 42,
        "secondary_stat": "暴击率%",
        "secondary_stat_value": "6.0%",
        "description": "一柄古老的长剑，整体呈黑色，剑身上刻着神秘的符文。",
        "lore": "蒙德地区流传的古老兵器，据说拥有神秘的诅咒力量。",
        "passive_name": "正义",
        "passive_description": "普通攻击和重击造成的伤害提升20%；此外，普通攻击和重击暴击时，回复等同于攻击力60%的生命值。该效果每5秒只能触发一次。",
        "source": "商店",
        "max_level": 90
    }
]


async def add_sample_weapons():
    """添加示例武器数据"""
    try:
        logger.info("开始添加武器示例数据...")

        # 获取数据库会话
        async with AsyncSessionLocal() as session:
            weapon_service = WeaponService(session)

            success_count = 0
            for weapon_data in SAMPLE_WEAPONS:
                try:
                    # 创建武器对象
                    weapon_create = WeaponCreate(**weapon_data)
                    weapon = await weapon_service.create_weapon(weapon_create)

                    logger.info(f"成功添加武器: {weapon.name}")
                    success_count += 1

                except Exception as e:
                    logger.error(f"添加武器失败: {weapon_data['name']}", error=str(e))
                    continue

            logger.info(f"武器示例数据添加完成，成功添加 {success_count}/{len(SAMPLE_WEAPONS)} 个武器")
            return success_count

    except Exception as e:
        logger.error("添加武器示例数据失败", error=str(e))
        raise


async def main():
    """主函数"""
    try:
        count = await add_sample_weapons()
        print(f"✅ 成功添加 {count} 个武器示例数据！")
    except Exception as e:
        print(f"❌ 添加武器示例数据失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())