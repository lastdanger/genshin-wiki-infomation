"""
原神武器完整列表 - 截止到6.1版本（月之二）

按武器类型和稀有度分类
"""

# 5星武器
FIVE_STAR_WEAPONS = {
    "单手剑": [
        # 限定武器
        "苍古自由之誓", "雾切之回光", "波乱月白经津", "圣显之钥", "裁叶萃光",
        "静水流涌之辉", "有乐御簾切", "赦罪", "苍耀",
        # 常驻武器
        "风鹰剑", "天空之刃", "斫峰之刃", "磐岩结绿",
    ],
    "双手剑": [
        # 限定武器
        "无工之剑", "松籁响起之时", "苇海信标", "裁断", "焚曜千阳",
        # 常驻武器
        "狼的末路", "天空之傲", "赤角石溃杵",
    ],
    "长柄武器": [
        # 限定武器
        "护摩之杖", "薙草之稻光", "贯虹之槊", "息灾", "赤沙之杖",
        "支离轮光", "香韵奏者", "血染荒城",
        # 常驻武器
        "和璞鸢", "天空之脊",
    ],
    "弓": [
        # 限定武器
        "终末嗟叹之诗", "飞雷之弦振", "若水", "猎人之径", "最初的大魔术", "白雨心弦",
        # 常驻武器
        "天空之翼", "阿莫斯之弓", "冬极白星",
    ],
    "法器": [
        # 限定武器
        "神乐之真意", "千夜浮梦", "图莱杜拉的回忆", "万世流涌大典", "鹤鸣余音",
        "金流监督", "祭星者之望", "纺夜天镜", "溢彩心念", "寝正月初晴", "真语秘匣",
        # 常驻武器
        "天空之卷", "四风原典",
    ],
}

# 4星武器
FOUR_STAR_WEAPONS = {
    "单手剑": [
        # 限定/活动武器
        "辰砂之纺锤", "东花坊时雨", "船坞长剑", "原木刀", "峡湾长歌",
        "笼钓瓶一心", "西风剑", "祭礼剑", "匣里龙吟",
        # 锻造武器
        "天目影打刀", "铁蜂刺", "试作斩岩", "天目影打刀", "腐殖之剑",
        # 其他
        "黑剑", "磐岩结绿", "暗巷闪光", "降临之剑", "黎明神剑",
    ],
    "双手剑": [
        # 限定/活动武器
        "恶王丸", "玛海菈的水色", "便携动力锯", "饰铁之花", "沙海守望",
        "森林王器", "西风大剑", "祭礼大剑", "钟剑",
        # 锻造武器
        "桂木斩长正", "古华·试作", "雪葬的星银", "衔珠海皇",
        # 其他
        "螭骨剑", "千岩古剑", "黑岩斩刀", "白影剑", "雨裁",
    ],
    "长柄武器": [
        # 限定/活动武器
        "「渔获」", "风信之锋", "勘探钻机", "沙海守望", "破浪长枪",
        "西风长枪", "匣里灭辰", "喜多院十文字",
        # 锻造武器
        "星镰·试作", "流月针", "龙脊长枪", "试作星镰", "风信之锋",
        # 其他
        "黑缨枪", "决斗之枪", "黑岩刺枪", "千岩长枪",
    ],
    "弓": [
        # 限定/活动武器
        "落霞", "风花之颂", "曚云之月", "掠食者", "烈阳之嗣",
        "西风猎弓", "祭礼弓", "绝弦", "弓藏",
        # 锻造武器
        "钢轮弓", "试作澹月", "破魔之弓", "竭泽",
        # 其他
        "静谧之弦", "苍翠猎弓", "黑岩战弓", "幽夜华尔兹", "暗巷猎手",
    ],
    "法器": [
        # 限定/活动武器
        "证誓之明瞳", "遗祀玉珑", "流浪的晚星", "盈满之实", "无垠蔚蓝之歌",
        "嘟嘟可故事集", "西风秘典", "祭礼残章", "匣里日月", "昭心",
        # 锻造武器
        "试作金珀", "万国诸海图谱", "忍冬之果", "纯水流华",
        # 其他
        "暗巷的酒与诗", "黑岩绯玉", "流浪乐章", "白辰之环",
    ],
}

# 3星武器
THREE_STAR_WEAPONS = {
    "单手剑": [
        "黎明神剑", "旅行剑", "冷刃", "吃虎鱼刀", "飞天御剑", "暗铁剑",
    ],
    "双手剑": [
        "沐浴龙血的剑", "铁影阔剑", "飞天大御剑", "以理服人", "白铁大剑", "石英大剑",
    ],
    "长柄武器": [
        "黑缨枪", "钺矛", "白缨枪",
    ],
    "弓": [
        "弹弓", "神射手之誓", "反曲弓", "鸦羽弓", "信使",
    ],
    "法器": [
        "魔导绪论", "讨龙英杰譚", "翡翠宝珠", "甲级宝珏", "异世界行记",
    ],
}

def get_all_weapons():
    """获取所有武器列表（不分类）"""
    all_weapons = []
    for weapons in FIVE_STAR_WEAPONS.values():
        all_weapons.extend(weapons)
    for weapons in FOUR_STAR_WEAPONS.values():
        all_weapons.extend(weapons)
    for weapons in THREE_STAR_WEAPONS.values():
        all_weapons.extend(weapons)
    return all_weapons

def get_weapons_by_rarity(rarity: int):
    """按稀有度获取武器列表"""
    if rarity == 5:
        weapons = []
        for w_list in FIVE_STAR_WEAPONS.values():
            weapons.extend(w_list)
        return weapons
    elif rarity == 4:
        weapons = []
        for w_list in FOUR_STAR_WEAPONS.values():
            weapons.extend(w_list)
        return weapons
    elif rarity == 3:
        weapons = []
        for w_list in THREE_STAR_WEAPONS.values():
            weapons.extend(w_list)
        return weapons
    return []

def get_weapons_by_type(weapon_type: str):
    """按武器类型获取武器列表"""
    weapons = []
    if weapon_type in FIVE_STAR_WEAPONS:
        weapons.extend(FIVE_STAR_WEAPONS[weapon_type])
    if weapon_type in FOUR_STAR_WEAPONS:
        weapons.extend(FOUR_STAR_WEAPONS[weapon_type])
    if weapon_type in THREE_STAR_WEAPONS:
        weapons.extend(THREE_STAR_WEAPONS[weapon_type])
    return weapons
