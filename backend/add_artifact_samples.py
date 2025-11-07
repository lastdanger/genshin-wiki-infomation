#!/usr/bin/env python3
"""
添加圣遗物示例数据

添加热门原神圣遗物套装的示例数据到数据库中
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(__file__))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from src.models.artifact import Artifact
from src.config import get_settings

# 圣遗物示例数据
ARTIFACT_SAMPLES = [
    # 绝缘之旗印套装
    {
        "name": "明威之镡", "name_en": "Magnificent Tsuba", "set_name": "绝缘之旗印", "set_name_en": "Emblem of Severed Fate",
        "slot": "flower", "rarity": 5, "main_stat_type": "HP", "main_stat_value": "4780",
        "description": "华美的刀镡，曾经是某位将军的爱刀配件。", "lore": "雷鸣般的怒吼与咆哮永远伴随着雷电将军的威仪。",
        "sub_stats": [
            {"stat_type": "CRIT Rate", "stat_value": "3.9%"},
            {"stat_type": "CRIT DMG", "stat_value": "7.8%"},
            {"stat_type": "ATK%", "stat_value": "5.8%"},
            {"stat_type": "Energy Recharge", "stat_value": "6.5%"}
        ],
        "set_effects": {
            "2": {"name": "攻击的意志", "description": "元素充能效率提高20%"},
            "4": {"name": "绝缘的觉悟", "description": "基于元素充能效率的25%，提高元素爆发造成的伤害。通过这种方式，元素爆发造成的伤害提升最多可以达到75%"}
        },
        "source": "副本", "domain_name": "椛染之庭", "max_level": 20, "is_set_piece": True
    },
    {
        "name": "切落之羽", "name_en": "Sundered Feather", "set_name": "绝缘之旗印", "set_name_en": "Emblem of Severed Fate",
        "slot": "plume", "rarity": 5, "main_stat_type": "ATK", "main_stat_value": "311",
        "description": "被利刃切断的羽毛，象征着决心与牺牲。", "lore": "在雷电的审判下，一切不洁都将被净化。",
        "sub_stats": [
            {"stat_type": "HP%", "stat_value": "5.8%"},
            {"stat_type": "DEF%", "stat_value": "7.3%"},
            {"stat_type": "CRIT DMG", "stat_value": "14.0%"},
            {"stat_type": "Elemental Mastery", "stat_value": "23"}
        ],
        "set_effects": {
            "2": {"name": "攻击的意志", "description": "元素充能效率提高20%"},
            "4": {"name": "绝缘的觉悟", "description": "基于元素充能效率的25%，提高元素爆发造成的伤害。通过这种方式，元素爆发造成的伤害提升最多可以达到75%"}
        },
        "source": "副本", "domain_name": "椛染之庭", "max_level": 20, "is_set_piece": True
    },
    {
        "name": "雷云之笼", "name_en": "Storm Cage", "set_name": "绝缘之旗印", "set_name_en": "Emblem of Severed Fate",
        "slot": "sands", "rarity": 5, "main_stat_type": "Energy Recharge", "main_stat_value": "51.8%",
        "description": "缚锁雷云的神器，蕴含着无穷的雷霆之力。", "lore": "雷电将军的权威如同牢笼，束缚着一切妄图挑战的存在。",
        "sub_stats": [
            {"stat_type": "CRIT Rate", "stat_value": "7.0%"},
            {"stat_type": "ATK", "stat_value": "33"},
            {"stat_type": "HP%", "stat_value": "4.7%"},
            {"stat_type": "CRIT DMG", "stat_value": "12.4%"}
        ],
        "set_effects": {
            "2": {"name": "攻击的意志", "description": "元素充能效率提高20%"},
            "4": {"name": "绝缘的觉悟", "description": "基于元素充能效率的25%，提高元素爆发造成的伤害。通过这种方式，元素爆发造成的伤害提升最多可以达到75%"}
        },
        "source": "副本", "domain_name": "椛染之庭", "max_level": 20, "is_set_piece": True
    },
    {
        "name": "绯花之壶", "name_en": "Scarlet Vessel", "set_name": "绝缘之旗印", "set_name_en": "Emblem of Severed Fate",
        "slot": "goblet", "rarity": 5, "main_stat_type": "Electro DMG Bonus", "main_stat_value": "46.6%",
        "description": "盛放绯花的壶器，记录着永恒的美丽。", "lore": "即使在最严酷的雷电下，绯花依然绽放着不屈的美丽。",
        "sub_stats": [
            {"stat_type": "HP", "stat_value": "299"},
            {"stat_type": "CRIT Rate", "stat_value": "6.2%"},
            {"stat_type": "Energy Recharge", "stat_value": "11.0%"},
            {"stat_type": "CRIT DMG", "stat_value": "21.0%"}
        ],
        "set_effects": {
            "2": {"name": "攻击的意志", "description": "元素充能效率提高20%"},
            "4": {"name": "绝缘的觉悟", "description": "基于元素充能效率的25%，提高元素爆发造成的伤害。通过这种方式，元素爆发造成的伤害提升最多可以达到75%"}
        },
        "source": "副本", "domain_name": "椛染之庭", "max_level": 20, "is_set_piece": True
    },
    {
        "name": "华饰之兜", "name_en": "Ornate Kabuto", "set_name": "绝缘之旗印", "set_name_en": "Emblem of Severed Fate",
        "slot": "circlet", "rarity": 5, "main_stat_type": "CRIT DMG", "main_stat_value": "62.2%",
        "description": "华美的武士头盔，象征着荣誉与勇气。", "lore": "真正的武士，即使面对死亡也不会退缩半步。",
        "sub_stats": [
            {"stat_type": "ATK%", "stat_value": "14.0%"},
            {"stat_type": "HP%", "stat_value": "4.7%"},
            {"stat_type": "Energy Recharge", "stat_value": "6.5%"},
            {"stat_type": "Elemental Mastery", "stat_value": "42"}
        ],
        "set_effects": {
            "2": {"name": "攻击的意志", "description": "元素充能效率提高20%"},
            "4": {"name": "绝缘的觉悟", "description": "基于元素充能效率的25%，提高元素爆发造成的伤害。通过这种方式，元素爆发造成的伤害提升最多可以达到75%"}
        },
        "source": "副本", "domain_name": "椛染之庭", "max_level": 20, "is_set_piece": True
    },

    # 华馆梦醒套装
    {
        "name": "荣花之期", "name_en": "Flowering Moment", "set_name": "华馆梦醒", "set_name_en": "Husk of Opulent Dreams",
        "slot": "flower", "rarity": 5, "main_stat_type": "HP", "main_stat_value": "4780",
        "description": "盛开的华美花朵，象征着梦想的绽放。", "lore": "在华丽的梦境中，一切美好都能成为现实。",
        "sub_stats": [
            {"stat_type": "DEF%", "stat_value": "7.3%"},
            {"stat_type": "CRIT Rate", "stat_value": "3.5%"},
            {"stat_type": "Energy Recharge", "stat_value": "4.5%"},
            {"stat_type": "CRIT DMG", "stat_value": "15.5%"}
        ],
        "set_effects": {
            "2": {"name": "华馆的共鸣", "description": "防御力提高30%"},
            "4": {"name": "梦醒的华彩", "description": "装备此圣遗物套装的角色在以下情况下，将获得「问答」效果：在场上用岩元素攻击命中敌人后，获得1层，每0.3秒最多触发一次；在场下时，每3秒获得1层。问答最多叠加4层，每层能够提供6%防御力与6%岩元素伤害加成。每6秒，若未通过上述方式获得问答效果，将损失1层"}
        },
        "source": "副本", "domain_name": "椛染之庭", "max_level": 20, "is_set_piece": True
    },
    {
        "name": "华馆之羽", "name_en": "Plume of Luxury", "set_name": "华馆梦醒", "set_name_en": "Husk of Opulent Dreams",
        "slot": "plume", "rarity": 5, "main_stat_type": "ATK", "main_stat_value": "311",
        "description": "华贵的羽毛装饰，显示着主人的身份。", "lore": "即使是梦境中的羽毛，也闪烁着真实的光芒。",
        "sub_stats": [
            {"stat_type": "HP%", "stat_value": "4.1%"},
            {"stat_type": "DEF%", "stat_value": "13.1%"},
            {"stat_type": "CRIT Rate", "stat_value": "7.0%"},
            {"stat_type": "ATK%", "stat_value": "5.8%"}
        ],
        "set_effects": {
            "2": {"name": "华馆的共鸣", "description": "防御力提高30%"},
            "4": {"name": "梦醒的华彩", "description": "装备此圣遗物套装的角色在以下情况下，将获得「问答」效果：在场上用岩元素攻击命中敌人后，获得1层，每0.3秒最多触发一次；在场下时，每3秒获得1层。问答最多叠加4层，每层能够提供6%防御力与6%岩元素伤害加成。每6秒，若未通过上述方式获得问答效果，将损失1层"}
        },
        "source": "副本", "domain_name": "椛染之庭", "max_level": 20, "is_set_piece": True
    },
    {
        "name": "众生之谣", "name_en": "Song of Life", "set_name": "华馆梦醒", "set_name_en": "Husk of Opulent Dreams",
        "slot": "sands", "rarity": 5, "main_stat_type": "DEF%", "main_stat_value": "58.3%",
        "description": "记录众生故事的古老乐谱。", "lore": "在华美的梦境中，每个生命都有自己的旋律。",
        "sub_stats": [
            {"stat_type": "CRIT DMG", "stat_value": "6.2%"},
            {"stat_type": "Energy Recharge", "stat_value": "10.4%"},
            {"stat_type": "HP", "stat_value": "508"},
            {"stat_type": "CRIT Rate", "stat_value": "3.9%"}
        ],
        "set_effects": {
            "2": {"name": "华馆的共鸣", "description": "防御力提高30%"},
            "4": {"name": "梦醒的华彩", "description": "装备此圣遗物套装的角色在以下情况下，将获得「问答」效果：在场上用岩元素攻击命中敌人后，获得1层，每0.3秒最多触发一次；在场下时，每3秒获得1层。问答最多叠加4层，每层能够提供6%防御力与6%岩元素伤害加成。每6秒，若未通过上述方式获得问答效果，将损失1层"}
        },
        "source": "副本", "domain_name": "椛染之庭", "max_level": 20, "is_set_piece": True
    },
    {
        "name": "梦醒之瓢", "name_en": "Calabash of Awakening", "set_name": "华馆梦醒", "set_name_en": "Husk of Opulent Dreams",
        "slot": "goblet", "rarity": 5, "main_stat_type": "Geo DMG Bonus", "main_stat_value": "46.6%",
        "description": "醒梦的神器，能够分辨真实与虚幻。", "lore": "当梦境结束时，真正的考验才刚刚开始。",
        "sub_stats": [
            {"stat_type": "ATK%", "stat_value": "4.7%"},
            {"stat_type": "DEF%", "stat_value": "16.8%"},
            {"stat_type": "HP%", "stat_value": "4.7%"},
            {"stat_type": "CRIT Rate", "stat_value": "7.4%"}
        ],
        "set_effects": {
            "2": {"name": "华馆的共鸣", "description": "防御力提高30%"},
            "4": {"name": "梦醒的华彩", "description": "装备此圣遗物套装的角色在以下情况下，将获得「问答」效果：在场上用岩元素攻击命中敌人后，获得1层，每0.3秒最多触发一次；在场下时，每3秒获得1层。问答最多叠加4层，每层能够提供6%防御力与6%岩元素伤害加成。每6秒，若未通过上述方式获得问答效果，将损失1层"}
        },
        "source": "副本", "domain_name": "椛染之庭", "max_level": 20, "is_set_piece": True
    },
    {
        "name": "形骸之笠", "name_en": "Skeletal Hat", "set_name": "华馆梦醒", "set_name_en": "Husk of Opulent Dreams",
        "slot": "circlet", "rarity": 5, "main_stat_type": "CRIT Rate", "main_stat_value": "31.1%",
        "description": "空洞的帽饰，仿佛能看透一切虚妄。", "lore": "真正的强者，不会被华美的外表所迷惑。",
        "sub_stats": [
            {"stat_type": "DEF%", "stat_value": "19.0%"},
            {"stat_type": "ATK", "stat_value": "18"},
            {"stat_type": "HP%", "stat_value": "11.1%"},
            {"stat_type": "Energy Recharge", "stat_value": "5.8%"}
        ],
        "set_effects": {
            "2": {"name": "华馆的共鸣", "description": "防御力提高30%"},
            "4": {"name": "梦醒的华彩", "description": "装备此圣遗物套装的角色在以下情况下，将获得「问答」效果：在场上用岩元素攻击命中敌人后，获得1层，每0.3秒最多触发一次；在场下时，每3秒获得1层。问答最多叠加4层，每层能够提供6%防御力与6%岩元素伤害加成。每6秒，若未通过上述方式获得问答效果，将损失1层"}
        },
        "source": "副本", "domain_name": "椛染之庭", "max_level": 20, "is_set_piece": True
    },

    # 千岩牢固套装
    {
        "name": "千岩长枪", "name_en": "Flower of Creviced Cliff", "set_name": "千岩牢固", "set_name_en": "Tenacity of the Millelith",
        "slot": "flower", "rarity": 5, "main_stat_type": "HP", "main_stat_value": "4780",
        "description": "坚固如岩的长枪，象征着千岩军的意志。", "lore": "千岩军的忠诚如山岩般坚固，永不动摇。",
        "sub_stats": [
            {"stat_type": "ATK%", "stat_value": "10.5%"},
            {"stat_type": "CRIT DMG", "stat_value": "13.2%"},
            {"stat_type": "Energy Recharge", "stat_value": "5.2%"},
            {"stat_type": "Elemental Mastery", "stat_value": "21"}
        ],
        "set_effects": {
            "2": {"name": "坚韧不移", "description": "生命值提高20%"},
            "4": {"name": "千岩的护卫", "description": "元素战技命中敌人后，使队伍中附近的所有角色攻击力提高20%，护盾强效提高30%，持续3秒。该效果每0.5秒至多触发一次。装备此圣遗物套装的角色处于队伍后台时，依然能触发该效果"}
        },
        "source": "副本", "domain_name": "岭上胡光", "max_level": 20, "is_set_piece": True
    },
    {
        "name": "嵯峨群峰", "name_en": "Feather of Jagged Peaks", "set_name": "千岩牢固", "set_name_en": "Tenacity of the Millelith",
        "slot": "plume", "rarity": 5, "main_stat_type": "ATK", "main_stat_value": "311",
        "description": "群峰之羽，记录着璃月的壮丽山河。", "lore": "璃月的山峰见证了千岩军的荣耀与牺牲。",
        "sub_stats": [
            {"stat_type": "HP%", "stat_value": "16.3%"},
            {"stat_type": "DEF", "stat_value": "23"},
            {"stat_type": "CRIT Rate", "stat_value": "2.7%"},
            {"stat_type": "CRIT DMG", "stat_value": "12.4%"}
        ],
        "set_effects": {
            "2": {"name": "坚韧不移", "description": "生命值提高20%"},
            "4": {"name": "千岩的护卫", "description": "元素战技命中敌人后，使队伍中附近的所有角色攻击力提高20%，护盾强效提高30%，持续3秒。该效果每0.5秒至多触发一次。装备此圣遗物套装的角色处于队伍后台时，依然能触发该效果"}
        },
        "source": "副本", "domain_name": "岭上胡光", "max_level": 20, "is_set_piece": True
    },
    {
        "name": "旧时之歌", "name_en": "Heart of Comradeship", "set_name": "千岩牢固", "set_name_en": "Tenacity of the Millelith",
        "slot": "sands", "rarity": 5, "main_stat_type": "HP%", "main_stat_value": "46.6%",
        "description": "古老的战歌，激励着后代的勇士。", "lore": "千岩军的战歌回响在璃月的每一个角落。",
        "sub_stats": [
            {"stat_type": "ATK%", "stat_value": "4.7%"},
            {"stat_type": "DEF%", "stat_value": "6.6%"},
            {"stat_type": "CRIT Rate", "stat_value": "10.9%"},
            {"stat_type": "Energy Recharge", "stat_value": "4.5%"}
        ],
        "set_effects": {
            "2": {"name": "坚韧不移", "description": "生命值提高20%"},
            "4": {"name": "千岩的护卫", "description": "元素战技命中敌人后，使队伍中附近的所有角色攻击力提高20%，护盾强效提高30%，持续3秒。该效果每0.5秒至多触发一次。装备此圣遗物套装的角色处于队伍后台时，依然能触发该效果"}
        },
        "source": "副本", "domain_name": "岭上胡光", "max_level": 20, "is_set_piece": True
    },
    {
        "name": "金铜时晷", "name_en": "Goblet of Thundering Deep", "set_name": "千岩牢固", "set_name_en": "Tenacity of the Millelith",
        "slot": "goblet", "rarity": 5, "main_stat_type": "HP%", "main_stat_value": "46.6%",
        "description": "精制的时计，记录着璃月的辉煌历史。", "lore": "时间见证了千岩军的成长与蜕变。",
        "sub_stats": [
            {"stat_type": "DEF%", "stat_value": "5.8%"},
            {"stat_type": "CRIT DMG", "stat_value": "21.8%"},
            {"stat_type": "ATK", "stat_value": "35"},
            {"stat_type": "Energy Recharge", "stat_value": "4.5%"}
        ],
        "set_effects": {
            "2": {"name": "坚韧不移", "description": "生命值提高20%"},
            "4": {"name": "千岩的护卫", "description": "元素战技命中敌人后，使队伍中附近的所有角色攻击力提高20%，护盾强效提高30%，持续3秒。该效果每0.5秒至多触发一次。装备此圣遗物套装的角色处于队伍后台时，依然能触发该效果"}
        },
        "source": "副本", "domain_name": "岭上胡光", "max_level": 20, "is_set_piece": True
    },
    {
        "name": "将帅兜鍪", "name_en": "Crown of Loyalty", "set_name": "千岩牢固", "set_name_en": "Tenacity of the Millelith",
        "slot": "circlet", "rarity": 5, "main_stat_type": "HP%", "main_stat_value": "46.6%",
        "description": "将军的头盔，象征着领导力与责任。", "lore": "真正的将军，会为了部下的安全而战斗到最后。",
        "sub_stats": [
            {"stat_type": "ATK%", "stat_value": "8.7%"},
            {"stat_type": "DEF%", "stat_value": "7.3%"},
            {"stat_type": "CRIT Rate", "stat_value": "7.8%"},
            {"stat_type": "CRIT DMG", "stat_value": "5.4%"}
        ],
        "set_effects": {
            "2": {"name": "坚韧不移", "description": "生命值提高20%"},
            "4": {"name": "千岩的护卫", "description": "元素战技命中敌人后，使队伍中附近的所有角色攻击力提高20%，护盾强效提高30%，持续3秒。该效果每0.5秒至多触发一次。装备此圣遗物套装的角色处于队伍后台时，依然能触发该效果"}
        },
        "source": "副本", "domain_name": "岭上胡光", "max_level": 20, "is_set_piece": True
    }
]

async def add_artifact_samples():
    """添加圣遗物示例数据"""
    try:
        # 获取配置并创建数据库引擎和会话
        settings = get_settings()
        engine = create_async_engine(settings.database_url, echo=False)
        AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

        async with AsyncSessionLocal() as db:
            print("开始添加圣遗物示例数据...")

            for i, artifact_data in enumerate(ARTIFACT_SAMPLES, 1):
                # 检查圣遗物是否已存在
                existing_query = text("""
                SELECT id FROM artifacts
                WHERE name = :name AND set_name = :set_name AND slot = :slot
                """)
                result = await db.execute(
                    existing_query,
                    {
                        "name": artifact_data["name"],
                        "set_name": artifact_data["set_name"],
                        "slot": artifact_data["slot"]
                    }
                )
                existing = result.fetchone()

                if existing:
                    print(f"  {i:2d}. 跳过 {artifact_data['name']} ({artifact_data['set_name']} - {artifact_data['slot']}) - 已存在")
                    continue

                # 创建新圣遗物记录
                artifact = Artifact(**artifact_data)
                db.add(artifact)

                print(f"  {i:2d}. 添加 {artifact_data['name']} ({artifact_data['set_name']} - {artifact_data['slot']})")

            # 提交事务
            await db.commit()
            print(f"\n✅ 成功添加 {len(ARTIFACT_SAMPLES)} 个圣遗物示例数据！")

        await engine.dispose()

    except Exception as e:
        print(f"❌ 添加圣遗物示例数据失败: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(add_artifact_samples())