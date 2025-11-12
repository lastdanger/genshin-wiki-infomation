"""
原神圣遗物完整列表 - 截止到6.1版本（月之二）

按稀有度分类
"""

# 5星圣遗物套装
FIVE_STAR_ARTIFACTS = [
    # 6.x 版本新增（空月之歌）
    "穹境示现之夜",  # 6.1
    "纺月的夜歌",    # 6.1
    "深廊终曲",      # 6.0
    "长夜之誓",      # 6.0

    # 5.x 版本
    "烬城勇者绘卷",  # 5.3
    "黑曜秘典",      # 5.3
    "未竟的遐思",    # 5.2
    "谐律异想断章",  # 5.1
    "回声之林夜话",  # 5.0
    "昔时之歌",      # 5.0

    # 4.x 版本（枫丹）
    "逐影猎人",
    "黄金剧团",
    "水仙之梦",
    "花海甘露之光",
    "乐园遗落之花",
    "沙上楼阁史话",

    # 3.x 版本（须弥）
    "深林的记忆",
    "饰金之梦",
    "金缚之梦",
    "来歆余响",
    "辰砂往生录",

    # 2.x 版本（稻妻）
    "绝缘之旗印",
    "华馆梦醒形骸记",
    "海染砗磲",
    "平息鸣雷的尊者",
    "追忆之注连",

    # 1.x 版本及以前
    "逆飞的流星",
    "苍白之火",
    "染血的骑士道",
    "冰风迷途的勇士",
    "炽烈的炎之魔女",
    "翠绿之影",
    "渡过烈火的贤人",
    "被怜爱的少女",
    "沉沦之心",
    "千岩牢固",
    "悠古的磐岩",

    # 副本/世界BOSS常驻
    "角斗士的终幕礼",
    "流浪大地的乐团",
    "逆飞的流星",
]

# 4星圣遗物套装
FOUR_STAR_ARTIFACTS = [
    # 副本4星套装
    "勇士之心",
    "守护之心",
    "教官",
    "赌徒",
    "流放者",
    "武人",
    "学者",
    "战狂",
    "游医",
    "祝圣秘礼",  # 4-5星套装
]

# 3星圣遗物套装
THREE_STAR_ARTIFACTS = [
    "冒险家",
    "幸运儿",
    "行者之心",
    "奇迹",
    "勇士之心",  # 3-4星套装
    "守护之心",  # 3-4星套装
]

def get_all_artifacts():
    """获取所有圣遗物套装列表"""
    return FIVE_STAR_ARTIFACTS + FOUR_STAR_ARTIFACTS + THREE_STAR_ARTIFACTS

def get_artifacts_by_rarity(rarity: int):
    """按稀有度获取圣遗物列表"""
    if rarity == 5:
        return FIVE_STAR_ARTIFACTS
    elif rarity == 4:
        return FOUR_STAR_ARTIFACTS
    elif rarity == 3:
        return THREE_STAR_ARTIFACTS
    return []

def get_latest_artifacts(version: str = "6.1"):
    """获取最新版本的圣遗物"""
    if version == "6.1":
        return ["穹境示现之夜", "纺月的夜歌"]
    elif version == "6.0":
        return ["深廊终曲", "长夜之誓"]
    elif version == "5.3":
        return ["烬城勇者绘卷", "黑曜秘典"]
    return []
