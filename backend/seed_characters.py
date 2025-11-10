"""
填充测试角色数据
由于目标网站使用动态加载，暂时使用静态测试数据
"""
import asyncio
from sqlalchemy import select
from src.db.session import AsyncSessionLocal
from src.models.character import Character
from datetime import datetime

# 原神角色测试数据（5星和部分4星）
TEST_CHARACTERS = [
    # 蒙德 5星
    {
        "name": "琴",
        "name_en": "Jean",
        "element": "Anemo",
        "weapon_type": "Sword",
        "rarity": 5,
        "region": "Mondstadt",
        "description": "西风骑士团代理团长，守护蒙德的蒲公英骑士。",
        "base_stats": {"hp": 14695, "atk": 239, "def": 769},
        "ascension_stats": {"stat": "healing_bonus", "value": 22.2},
    },
    {
        "name": "迪卢克",
        "name_en": "Diluc",
        "element": "Pyro",
        "weapon_type": "Claymore",
        "rarity": 5,
        "region": "Mondstadt",
        "description": "晨曦酒庄的主人，蒙德的守护者。",
        "base_stats": {"hp": 12981, "atk": 335, "def": 784},
        "ascension_stats": {"stat": "crit_rate", "value": 19.2},
    },
    {
        "name": "莫娜",
        "name_en": "Mona",
        "element": "Hydro",
        "weapon_type": "Catalyst",
        "rarity": 5,
        "region": "Mondstadt",
        "description": "神秘的占星术士，拥有预知未来的能力。",
        "base_stats": {"hp": 10409, "atk": 287, "def": 653},
        "ascension_stats": {"stat": "energy_recharge", "value": 32.0},
    },
    {
        "name": "温迪",
        "name_en": "Venti",
        "element": "Anemo",
        "weapon_type": "Bow",
        "rarity": 5,
        "region": "Mondstadt",
        "description": "吟游诗人，风神巴巴托斯的化身。",
        "base_stats": {"hp": 10531, "atk": 263, "def": 669},
        "ascension_stats": {"stat": "energy_recharge", "value": 32.0},
    },

    # 璃月 5星
    {
        "name": "刻晴",
        "name_en": "Keqing",
        "element": "Electro",
        "weapon_type": "Sword",
        "rarity": 5,
        "region": "Liyue",
        "description": "璃月七星之玉衡星，雷霆万钧的武艺高手。",
        "base_stats": {"hp": 13103, "atk": 323, "def": 799},
        "ascension_stats": {"stat": "crit_dmg", "value": 38.4},
    },
    {
        "name": "魈",
        "name_en": "Xiao",
        "element": "Anemo",
        "weapon_type": "Polearm",
        "rarity": 5,
        "region": "Liyue",
        "description": "守护璃月的仙人，三眼五显仙人。",
        "base_stats": {"hp": 12736, "atk": 349, "def": 799},
        "ascension_stats": {"stat": "crit_rate", "value": 19.2},
    },
    {
        "name": "甘雨",
        "name_en": "Ganyu",
        "element": "Cryo",
        "weapon_type": "Bow",
        "rarity": 5,
        "region": "Liyue",
        "description": "璃月七星秘书，半仙之体的弓箭手。",
        "base_stats": {"hp": 9797, "atk": 335, "def": 630},
        "ascension_stats": {"stat": "crit_dmg", "value": 38.4},
    },
    {
        "name": "胡桃",
        "name_en": "Hu Tao",
        "element": "Pyro",
        "weapon_type": "Polearm",
        "rarity": 5,
        "region": "Liyue",
        "description": "往生堂第七十七代堂主，行事古灵精怪。",
        "base_stats": {"hp": 15552, "atk": 106, "def": 876},
        "ascension_stats": {"stat": "crit_dmg", "value": 38.4},
    },

    # 稻妻 5星
    {
        "name": "雷电将军",
        "name_en": "Raiden Shogun",
        "element": "Electro",
        "weapon_type": "Polearm",
        "rarity": 5,
        "region": "Inazuma",
        "description": "稻妻的雷神，永恒的追求者。",
        "base_stats": {"hp": 12907, "atk": 337, "def": 789},
        "ascension_stats": {"stat": "energy_recharge", "value": 32.0},
    },
    {
        "name": "神里绫华",
        "name_en": "Kamisato Ayaka",
        "element": "Cryo",
        "weapon_type": "Sword",
        "rarity": 5,
        "region": "Inazuma",
        "description": "社奉行神里家的大小姐，白鹭公主。",
        "base_stats": {"hp": 12858, "atk": 342, "def": 784},
        "ascension_stats": {"stat": "crit_dmg", "value": 38.4},
    },

    # 须弥 5星
    {
        "name": "纳西妲",
        "name_en": "Nahida",
        "element": "Dendro",
        "weapon_type": "Catalyst",
        "rarity": 5,
        "region": "Sumeru",
        "description": "须弥的草神，智慧之神。",
        "base_stats": {"hp": 10360, "atk": 299, "def": 630},
        "ascension_stats": {"stat": "elemental_mastery", "value": 115},
    },

    # 枫丹 5星
    {
        "name": "那维莱特",
        "name_en": "Neuvillette",
        "element": "Hydro",
        "weapon_type": "Catalyst",
        "rarity": 5,
        "region": "Fontaine",
        "description": "枫丹的最高审判官，水龙。",
        "base_stats": {"hp": 14695, "atk": 208, "def": 576},
        "ascension_stats": {"stat": "crit_dmg", "value": 38.4},
    },

    # 4星角色
    {
        "name": "香菱",
        "name_en": "Xiangling",
        "element": "Pyro",
        "weapon_type": "Polearm",
        "rarity": 4,
        "region": "Liyue",
        "description": "万民堂的厨师，烹饪达人。",
        "base_stats": {"hp": 10875, "atk": 225, "def": 669},
        "ascension_stats": {"stat": "elemental_mastery", "value": 96},
    },
    {
        "name": "班尼特",
        "name_en": "Bennett",
        "element": "Pyro",
        "weapon_type": "Sword",
        "rarity": 4,
        "region": "Mondstadt",
        "description": "蒙德冒险家协会的冒险少年。",
        "base_stats": {"hp": 12397, "atk": 191, "def": 771},
        "ascension_stats": {"stat": "energy_recharge", "value": 26.7},
    },
    {
        "name": "行秋",
        "name_en": "Xingqiu",
        "element": "Hydro",
        "weapon_type": "Sword",
        "rarity": 4,
        "region": "Liyue",
        "description": "飞云商会二少爷，喜爱读书。",
        "base_stats": {"hp": 10222, "atk": 202, "def": 758},
        "ascension_stats": {"stat": "atk_percent", "value": 24.0},
    },
    {
        "name": "砂糖",
        "name_en": "Sucrose",
        "element": "Anemo",
        "weapon_type": "Catalyst",
        "rarity": 4,
        "region": "Mondstadt",
        "description": "炼金术师，对生物学研究充满热情。",
        "base_stats": {"hp": 9244, "atk": 170, "def": 703},
        "ascension_stats": {"stat": "anemo_dmg_bonus", "value": 24.0},
    },
    {
        "name": "菲谢尔",
        "name_en": "Fischl",
        "element": "Electro",
        "weapon_type": "Bow",
        "rarity": 4,
        "region": "Mondstadt",
        "description": "自称断罪皇女的调查员。",
        "base_stats": {"hp": 9189, "atk": 244, "def": 594},
        "ascension_stats": {"stat": "atk_percent", "value": 24.0},
    },
]


async def seed_database():
    """填充数据库"""
    print("=== 开始填充角色数据 ===\n")

    stats = {
        "created": 0,
        "skipped": 0,
        "errors": 0,
    }

    async with AsyncSessionLocal() as session:
        try:
            for char_data in TEST_CHARACTERS:
                try:
                    # 检查是否已存在
                    stmt = select(Character).where(Character.name == char_data["name"])
                    result = await session.execute(stmt)
                    existing = result.scalar_one_or_none()

                    if existing:
                        print(f"⏭️  跳过 {char_data['name']} (已存在)")
                        stats["skipped"] += 1
                        continue

                    # 创建新角色
                    character = Character(**char_data)
                    session.add(character)
                    await session.flush()

                    print(f"✅ 创建 {char_data['name']:8} | {char_data['element']:8} | {char_data['weapon_type']:10} | {char_data['rarity']}星")
                    stats["created"] += 1

                except Exception as e:
                    print(f"❌ 创建 {char_data.get('name', 'Unknown')} 失败: {e}")
                    stats["errors"] += 1

            await session.commit()

            print("\n=== 填充完成 ===")
            print(f"创建: {stats['created']}")
            print(f"跳过: {stats['skipped']}")
            print(f"错误: {stats['errors']}")

        except Exception as e:
            print(f"\n❌ 数据库操作失败: {e}")
            await session.rollback()


if __name__ == "__main__":
    asyncio.run(seed_database())
