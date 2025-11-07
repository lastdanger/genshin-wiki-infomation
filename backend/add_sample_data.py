#!/usr/bin/env python3
"""
添加示例数据到原神游戏信息网站数据库

包含示例角色、技能、天赋等数据
"""
import asyncio
import sys
import os
from datetime import date
from typing import Dict, Any

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath('.'))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.db.session import AsyncSessionLocal
from src.models.character import Character
from src.models.character_skill import CharacterSkill
from src.models.character_talent import CharacterTalent
import structlog

logger = structlog.get_logger()


async def add_sample_characters():
    """添加示例角色数据"""

    # 示例角色数据
    characters_data = [
        {
            "name": "甘雨",
            "name_en": "Ganyu",
            "element": "Cryo",
            "weapon_type": "Bow",
            "rarity": 5,
            "region": "Liyue",
            "base_stats": {
                "hp": 9797,
                "atk": 335,
                "def": 630
            },
            "ascension_stats": {
                "stat": "CRIT DMG",
                "value": 38.4
            },
            "description": "璃月七星的秘书，身上流淌着麒麟的血脉。",
            "birthday": date(2024, 12, 2),
            "constellation_name": "仙麟座",
            "title": "循循守月",
            "affiliation": "璃月七星"
        },
        {
            "name": "胡桃",
            "name_en": "Hu Tao",
            "element": "Pyro",
            "weapon_type": "Polearm",
            "rarity": 5,
            "region": "Liyue",
            "base_stats": {
                "hp": 15552,
                "atk": 106,
                "def": 876
            },
            "ascension_stats": {
                "stat": "CRIT DMG",
                "value": 38.4
            },
            "description": "「往生堂」七十七代堂主，年纪轻轻就已经掌握了火化的门道。",
            "birthday": date(2024, 7, 15),
            "constellation_name": "彼岸蝶座",
            "title": "雪霁梅香",
            "affiliation": "往生堂"
        },
        {
            "name": "钟离",
            "name_en": "Zhongli",
            "element": "Geo",
            "weapon_type": "Polearm",
            "rarity": 5,
            "region": "Liyue",
            "base_stats": {
                "hp": 14695,
                "atk": 251,
                "def": 738
            },
            "ascension_stats": {
                "stat": "Geo DMG Bonus",
                "value": 28.8
            },
            "description": "被「往生堂」请来的神秘客卿，样貌俊美、举止高雅，拥有远超常人的学识。",
            "birthday": date(2024, 12, 31),
            "constellation_name": "岩王帝君座",
            "title": "尘世闲游",
            "affiliation": "往生堂"
        },
        {
            "name": "温迪",
            "name_en": "Venti",
            "element": "Anemo",
            "weapon_type": "Bow",
            "rarity": 5,
            "region": "Mondstadt",
            "base_stats": {
                "hp": 10531,
                "atk": 263,
                "def": 669
            },
            "ascension_stats": {
                "stat": "Energy Recharge",
                "value": 32.0
            },
            "description": "蒙德城自由的吟游诗人，喜欢酒与音乐，也喜欢苹果。",
            "birthday": date(2024, 6, 16),
            "constellation_name": "歌仙座",
            "title": "风色诗人",
            "affiliation": "蒙德城"
        },
        {
            "name": "雷电将军",
            "name_en": "Raiden Shogun",
            "element": "Electro",
            "weapon_type": "Polearm",
            "rarity": 5,
            "region": "Inazuma",
            "base_stats": {
                "hp": 12907,
                "atk": 337,
                "def": 789
            },
            "ascension_stats": {
                "stat": "Energy Recharge",
                "value": 32.0
            },
            "description": "稻妻的最高统治者，掌控着雷电与永恒。",
            "birthday": date(2024, 6, 26),
            "constellation_name": "天下人座",
            "title": "一心净土",
            "affiliation": "稻妻幕府"
        }
    ]

    async with AsyncSessionLocal() as session:
        try:
            logger.info("开始添加示例角色数据...")

            for char_data in characters_data:
                # 检查角色是否已存在
                result = await session.execute(
                    select(Character).where(Character.name == char_data["name"])
                )
                existing = result.scalar_one_or_none()
                if existing:
                    logger.info(f"角色 {char_data['name']} 已存在，跳过")
                    continue

                # 创建角色实例
                character = Character(
                    name=char_data["name"],
                    name_en=char_data.get("name_en"),
                    element=char_data["element"],
                    weapon_type=char_data["weapon_type"],
                    rarity=char_data["rarity"],
                    region=char_data.get("region"),
                    base_stats=char_data["base_stats"],
                    ascension_stats=char_data.get("ascension_stats"),
                    description=char_data.get("description"),
                    birthday=char_data.get("birthday"),
                    constellation_name=char_data.get("constellation_name"),
                    title=char_data.get("title"),
                    affiliation=char_data.get("affiliation")
                )

                session.add(character)
                logger.info(f"添加角色: {char_data['name']}")

            await session.commit()
            logger.info(f"成功添加 {len(characters_data)} 个角色数据")

        except Exception as e:
            await session.rollback()
            logger.error("添加角色数据失败", error=str(e))
            raise


async def add_sample_skills():
    """添加示例技能数据"""

    async with AsyncSessionLocal() as session:
        try:
            # 获取甘雨角色
            result = await session.execute(
                select(Character).where(Character.name == '甘雨')
            )
            ganyu = result.scalar_one_or_none()
            if not ganyu:
                logger.warning("未找到甘雨角色，跳过技能添加")
                return

            ganyu_id = ganyu.id

            # 甘雨的技能数据
            skills_data = [
                {
                    "character_id": ganyu_id,
                    "skill_type": "normal_attack",
                    "name": "流天射术",
                    "description": "普通攻击：进行至多6段的连续弓箭射击。\n重击：进行更加精准的瞄准射击，会根据蓄力时间附加不同的效果。",
                    "scaling_stats": {
                        "normal_1": "31.7%",
                        "normal_2": "35.6%",
                        "normal_3": "45.5%",
                        "normal_4": "45.5%",
                        "normal_5": "48.2%",
                        "normal_6": "57.6%",
                        "charged_1": "43.9%",
                        "charged_2": "124%"
                    }
                },
                {
                    "character_id": ganyu_id,
                    "skill_type": "elemental_skill",
                    "name": "山泽麟迹",
                    "description": "甘雨迅速后退，并留下一朵冰莲。冰莲会持续嘲讽周围的敌人，吸引攻击；冰莲的耐久度按比例继承甘雨的生命值上限。",
                    "cooldown": 10,
                    "scaling_stats": {
                        "skill_dmg": "132%",
                        "inherited_hp": "120%"
                    }
                },
                {
                    "character_id": ganyu_id,
                    "skill_type": "elemental_burst",
                    "name": "降众天华",
                    "description": "凝聚大气中的霜雪，召唤退魔的冰灵珠。存在期间内，冰灵珠会持续降下冰棱，攻击范围内的敌人。",
                    "cooldown": 15,
                    "energy_cost": 60,
                    "scaling_stats": {
                        "icicle_dmg": "70.3%"
                    }
                }
            ]

            logger.info(f"开始为甘雨(ID: {ganyu_id})添加技能数据...")

            for skill_data in skills_data:
                # 检查技能是否已存在
                result = await session.execute(
                    select(CharacterSkill).where(
                        CharacterSkill.character_id == skill_data["character_id"],
                        CharacterSkill.skill_type == skill_data["skill_type"]
                    )
                )
                existing = result.scalar_one_or_none()
                if existing:
                    logger.info(f"技能 {skill_data['skill_type']} 已存在，跳过")
                    continue

                # 创建技能实例
                skill = CharacterSkill(
                    character_id=skill_data["character_id"],
                    skill_type=skill_data["skill_type"],
                    name=skill_data["name"],
                    description=skill_data["description"],
                    cooldown=skill_data.get("cooldown"),
                    energy_cost=skill_data.get("energy_cost"),
                    scaling_stats=skill_data["scaling_stats"]
                )

                session.add(skill)
                logger.info(f"添加技能: {skill_data['name']}")

            await session.commit()
            logger.info("成功添加甘雨技能数据")

        except Exception as e:
            await session.rollback()
            logger.error("添加技能数据失败", error=str(e))
            raise


async def main():
    """主函数"""
    try:
        logger.info("开始添加示例数据...")

        # 添加角色数据
        await add_sample_characters()

        # 添加技能数据
        await add_sample_skills()

        logger.info("✅ 示例数据添加完成！")
        print("✅ 示例数据添加成功！")
        print("\n可以通过以下方式查看：")
        print("- 前端: http://localhost:3001")
        print("- API: http://localhost:8002/api/characters")
        print("- API文档: http://localhost:8002/api/docs")

    except Exception as e:
        logger.error("添加示例数据失败", error=str(e))
        print(f"❌ 添加数据失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())