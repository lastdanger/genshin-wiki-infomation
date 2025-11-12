#!/usr/bin/env python3
"""
角色列表管理脚本

用途：
1. 查看当前配置的角色列表
2. 添加/删除角色
3. 导入/导出角色列表
4. 验证角色名是否有效
"""

import sys
import json
from pathlib import Path
from typing import List

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.scrapers.character_scraper import CharacterScraper


# 完整角色数据库（原神 5.2 版本）
GENSHIN_CHARACTERS = {
    "蒙德": {
        "5星": ["琴", "迪卢克", "莫娜", "温迪", "可莉", "优菈", "阿贝多"],
        "4星": ["班尼特", "砂糖", "菲谢尔", "芭芭拉", "雷泽", "诺艾尔", "罗莎莉亚", "米卡"],
    },
    "璃月": {
        "5星": ["刻晴", "魈", "甘雨", "胡桃", "钟离", "七七"],
        "4星": ["香菱", "行秋", "北斗", "凝光", "辛焱", "重云", "烟绯", "云堇", "瑶瑶", "嘉明"],
    },
    "稻妻": {
        "5星": ["雷电将军", "神里绫华", "宵宫", "珊瑚宫心海", "荒瀧一斗", "八重神子", "神里绫人"],
        "4星": ["早柚", "九条裟罗", "托马", "五郎", "久岐忍", "鹿野院平藏", "绮良良"],
    },
    "须弥": {
        "5星": ["纳西妲", "提纳里", "赛诺", "妮露", "流浪者", "艾尔海森", "迪希雅"],
        "4星": ["柯莱", "多莉", "坎蒂丝", "莱依拉", "珐露珊", "卡维", "白术"],
    },
    "枫丹": {
        "5星": ["那维莱特", "芙宁娜", "莱欧斯利", "娜维娅", "克洛琳德", "阿蕾奇诺", "希格雯"],
        "4星": ["琳妮特", "菲米尼", "夏沃蕾", "夏洛蒂", "嘉维尔", "艾梅莉埃"],
    },
    "纳塔": {
        "5星": ["玛拉妮", "基尼奇", "希诺宁"],
        "4星": ["卡齐娜"],
    },
    "其他": {
        "4星": ["旅行者", "安柏", "凯亚", "丽莎"],
    }
}


def get_all_character_names() -> List[str]:
    """获取所有角色名"""
    all_names = []
    for region in GENSHIN_CHARACTERS.values():
        for rarity in region.values():
            all_names.extend(rarity)
    return all_names


def get_character_info(name: str) -> dict:
    """获取角色信息"""
    for region_name, region_data in GENSHIN_CHARACTERS.items():
        for rarity, characters in region_data.items():
            if name in characters:
                return {
                    "name": name,
                    "region": region_name,
                    "rarity": rarity,
                }
    return None


def list_all_characters():
    """列出所有角色"""
    print("=" * 80)
    print("原神角色列表（5.2 版本）")
    print("=" * 80)

    total_5_star = 0
    total_4_star = 0

    for region_name, region_data in GENSHIN_CHARACTERS.items():
        print(f"\n【{region_name}】")
        for rarity, characters in region_data.items():
            count = len(characters)
            if "5星" in rarity:
                total_5_star += count
            else:
                total_4_star += count

            print(f"  {rarity} ({count}个): {', '.join(characters)}")

    print(f"\n总计：5星 {total_5_star} 个，4星 {total_4_star} 个，共 {total_5_star + total_4_star} 个角色")


def get_current_config() -> List[str]:
    """读取当前配置的角色列表"""
    scraper_file = Path(__file__).parent.parent / "src" / "scrapers" / "character_scraper.py"

    if not scraper_file.exists():
        print(f"错误：找不到文件 {scraper_file}")
        return []

    # 简单解析（实际项目可以用 ast 模块）
    with open(scraper_file, "r", encoding="utf-8") as f:
        content = f.read()

    # 查找 character_names = [ ... ] 部分
    import re
    match = re.search(r'character_names = \[(.*?)\]', content, re.DOTALL)

    if not match:
        print("警告：无法解析当前配置")
        return []

    # 提取角色名
    names_str = match.group(1)
    names = re.findall(r'"([^"]+)"', names_str)

    return names


def show_current_config():
    """显示当前配置"""
    names = get_current_config()

    if not names:
        print("当前没有配置角色列表")
        return

    print("=" * 80)
    print("当前配置的角色列表")
    print("=" * 80)
    print(f"共 {len(names)} 个角色\n")

    # 按地区分类显示
    by_region = {}
    for name in names:
        info = get_character_info(name)
        if info:
            region = info["region"]
            if region not in by_region:
                by_region[region] = []
            by_region[region].append(f"{name}({info['rarity']})")
        else:
            if "未知" not in by_region:
                by_region["未知"] = []
            by_region["未知"].append(name)

    for region, chars in by_region.items():
        print(f"【{region}】({len(chars)}个): {', '.join(chars)}")


def validate_characters(names: List[str]) -> dict:
    """验证角色名是否有效"""
    all_valid = get_all_character_names()

    valid = []
    invalid = []

    for name in names:
        if name in all_valid:
            valid.append(name)
        else:
            invalid.append(name)

    return {
        "valid": valid,
        "invalid": invalid,
        "total": len(names),
        "valid_count": len(valid),
        "invalid_count": len(invalid),
    }


def generate_config(filter_type: str = "all") -> List[str]:
    """
    生成角色配置

    Args:
        filter_type: 过滤类型
            - "all": 所有角色
            - "5star": 只要5星
            - "4star": 只要4星
            - "mondstadt": 蒙德
            - "liyue": 璃月
            - "inazuma": 稻妻
            - "sumeru": 须弥
            - "fontaine": 枫丹
            - "natlan": 纳塔
    """
    characters = []

    if filter_type == "all":
        characters = get_all_character_names()

    elif filter_type == "5star":
        for region_data in GENSHIN_CHARACTERS.values():
            characters.extend(region_data.get("5星", []))

    elif filter_type == "4star":
        for region_data in GENSHIN_CHARACTERS.values():
            characters.extend(region_data.get("4星", []))

    else:
        # 按地区
        region_map = {
            "mondstadt": "蒙德",
            "liyue": "璃月",
            "inazuma": "稻妻",
            "sumeru": "须弥",
            "fontaine": "枫丹",
            "natlan": "纳塔",
        }

        region_name = region_map.get(filter_type.lower())
        if region_name and region_name in GENSHIN_CHARACTERS:
            for chars in GENSHIN_CHARACTERS[region_name].values():
                characters.extend(chars)

    return characters


def export_config(filename: str, characters: List[str]):
    """导出角色列表到文件"""
    output_file = Path(filename)

    # 验证角色
    validation = validate_characters(characters)

    config = {
        "characters": characters,
        "metadata": {
            "total": validation["total"],
            "valid": validation["valid_count"],
            "invalid": validation["invalid_count"],
            "invalid_names": validation["invalid"],
        }
    }

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

    print(f"✅ 已导出到 {output_file}")
    print(f"   共 {validation['total']} 个角色（有效 {validation['valid_count']} 个，无效 {validation['invalid_count']} 个）")


def import_config(filename: str) -> List[str]:
    """从文件导入角色列表"""
    input_file = Path(filename)

    if not input_file.exists():
        print(f"错误：文件不存在 {input_file}")
        return []

    with open(input_file, "r", encoding="utf-8") as f:
        config = json.load(f)

    characters = config.get("characters", [])
    print(f"✅ 从 {input_file} 导入了 {len(characters)} 个角色")

    return characters


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="原神角色列表管理工具")

    subparsers = parser.add_subparsers(dest="command", help="子命令")

    # list - 列出所有角色
    subparsers.add_parser("list", help="列出所有可用角色")

    # current - 查看当前配置
    subparsers.add_parser("current", help="查看当前配置的角色列表")

    # generate - 生成配置
    generate_parser = subparsers.add_parser("generate", help="生成角色配置")
    generate_parser.add_argument(
        "--filter",
        choices=["all", "5star", "4star", "mondstadt", "liyue", "inazuma", "sumeru", "fontaine", "natlan"],
        default="all",
        help="过滤条件"
    )
    generate_parser.add_argument("--output", "-o", help="输出文件（可选）")

    # validate - 验证角色名
    validate_parser = subparsers.add_parser("validate", help="验证角色名是否有效")
    validate_parser.add_argument("names", nargs="+", help="角色名列表")

    # export - 导出配置
    export_parser = subparsers.add_parser("export", help="导出当前配置到文件")
    export_parser.add_argument("filename", help="输出文件名")

    # import - 导入配置
    import_parser = subparsers.add_parser("import", help="从文件导入配置")
    import_parser.add_argument("filename", help="输入文件名")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # 执行命令
    if args.command == "list":
        list_all_characters()

    elif args.command == "current":
        show_current_config()

    elif args.command == "generate":
        characters = generate_config(args.filter)
        print(f"✅ 生成了 {len(characters)} 个角色")
        print(f"   {', '.join(characters[:10])}{'...' if len(characters) > 10 else ''}")

        if args.output:
            export_config(args.output, characters)

    elif args.command == "validate":
        validation = validate_characters(args.names)

        print(f"验证结果：")
        print(f"  有效: {validation['valid_count']} / {validation['total']}")

        if validation['invalid']:
            print(f"  无效角色: {', '.join(validation['invalid'])}")

    elif args.command == "export":
        current = get_current_config()
        export_config(args.filename, current)

    elif args.command == "import":
        characters = import_config(args.filename)
        if characters:
            print(f"导入的角色: {', '.join(characters[:10])}{'...' if len(characters) > 10 else ''}")


if __name__ == "__main__":
    main()
