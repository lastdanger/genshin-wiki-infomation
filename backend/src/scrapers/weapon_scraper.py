"""
原神武器数据爬虫

从B站游戏Wiki抓取武器信息
URL模式: https://wiki.biligame.com/ys/{武器中文名}
"""

import logging
import re
from typing import Any, Dict, List, Optional
from urllib.parse import quote

from bs4 import BeautifulSoup, Tag

from .base_scraper import BaseScraper, ScraperConfig

logger = logging.getLogger(__name__)


class WeaponScraper(BaseScraper):
    """
    原神武器数据爬虫

    提取内容:
    - 基础信息（名称、类型、稀有度）
    - 属性（基础攻击力、副属性）
    - 被动技能信息
    - 描述
    """

    BILIBILI_BASE_URL = "https://wiki.biligame.com/ys"

    # 武器类型映射（中文到英文）
    WEAPON_MAP = {
        "单手剑": "Sword",
        "双手剑": "Claymore",
        "长柄武器": "Polearm",
        "弓": "Bow",
        "弓箭": "Bow",
        "法器": "Catalyst",
    }

    def __init__(self, config: Optional[ScraperConfig] = None):
        """初始化武器爬虫"""
        super().__init__(config)
        self._weapon_cache: Dict[str, Dict[str, Any]] = {}

        if not hasattr(self, '_stats'):
            self._stats = {
                "requests": 0,
                "errors": 0,
                "success_rate": 100.0,
            }

    async def scrape(self, weapon_names: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        爬取指定武器的数据

        Args:
            weapon_names: 武器名称列表（中文）。如果为None，使用默认列表

        Returns:
            武器数据字典列表
        """
        if weapon_names is None:
            weapon_names = self._get_default_weapon_list()

        logger.info(f"Starting weapon scraping for {len(weapon_names)} weapons...")

        weapons = []
        for weapon_name in weapon_names:
            try:
                weapon_data = await self.scrape_weapon(weapon_name)
                if weapon_data:
                    weapons.append(weapon_data)
                    logger.info(f"✅ Scraped: {weapon_name}")
                else:
                    logger.warning(f"⚠️  No data for: {weapon_name}")
            except Exception as e:
                logger.error(f"❌ Error scraping {weapon_name}: {e}", exc_info=True)
                self._stats["errors"] += 1

        logger.info(f"Successfully scraped {len(weapons)}/{len(weapon_names)} weapons")
        return weapons

    def _get_default_weapon_list(self) -> List[str]:
        """获取默认武器列表（截止到6.1版本的所有武器）"""
        import os
        import sys
        from pathlib import Path

        # 优先使用环境变量
        env_weapons = os.getenv("SCRAPER_WEAPONS")
        if env_weapons:
            return [name.strip() for name in env_weapons.split(",")]

        # 导入武器列表配置
        try:
            # 添加config目录到路径
            config_path = Path(__file__).parent.parent.parent / "config"
            sys.path.insert(0, str(config_path))

            from weapons_list import get_all_weapons
            return get_all_weapons()
        except ImportError:
            logger.warning("无法导入武器列表配置，使用默认列表")
            # 降级到5星武器列表
            return [
                # 单手剑
                "苍古自由之誓", "雾切之回光", "波乱月白经津", "圣显之钥", "裁叶萃光",
                "静水流涌之辉", "有乐御簾切", "赦罪", "苍耀",
                "风鹰剑", "天空之刃", "斫峰之刃", "磐岩结绿",

                # 双手剑
                "无工之剑", "松籁响起之时", "苇海信标", "裁断", "焚曜千阳",
                "狼的末路", "天空之傲", "赤角石溃杵",

                # 长柄武器
                "护摩之杖", "薙草之稻光", "贯虹之槊", "息灾", "赤沙之杖",
                "支离轮光", "香韵奏者", "血染荒城",
                "和璞鸢", "天空之脊",

                # 弓
                "终末嗟叹之诗", "飞雷之弦振", "若水", "猎人之径", "最初的大魔术", "白雨心弦",
                "天空之翼", "阿莫斯之弓", "冬极白星",

                # 法器
                "神乐之真意", "千夜浮梦", "图莱杜拉的回忆", "万世流涌大典", "鹤鸣余音",
                "金流监督", "祭星者之望", "纺夜天镜", "溢彩心念", "寝正月初晴", "真语秘匣",
                "天空之卷", "四风原典",
            ]

    async def scrape_weapon(self, weapon_name: str) -> Optional[Dict[str, Any]]:
        """
        Scrape single weapon data from wiki page.

        Args:
            weapon_name: Weapon name in Chinese

        Returns:
            Weapon data dictionary or None if failed
        """
        encoded_name = quote(weapon_name)
        url = f"{self.BILIBILI_BASE_URL}/{encoded_name}"

        logger.debug(f"Fetching weapon page: {url}")

        html = await self.fetch(url)
        if not html:
            logger.error(f"Failed to fetch page for {weapon_name}")
            return None

        soup = self.parse_html(html)
        if not soup:
            logger.error(f"Failed to parse HTML for {weapon_name}")
            return None

        try:
            weapon_data = self._extract_weapon_data(soup, weapon_name)
            return weapon_data
        except Exception as e:
            logger.error(f"Failed to extract data for {weapon_name}: {e}", exc_info=True)
            return None

    def _extract_weapon_data(self, soup: BeautifulSoup, weapon_name: str) -> Dict[str, Any]:
        """从解析的HTML中提取武器数据"""
        data = {
            "name": weapon_name,
            "name_en": None,
            "weapon_type": None,
            "rarity": None,
            "base_attack": None,
            "secondary_stat": None,
            "secondary_stat_value": None,
            "description": None,
            "passive_name": None,
            "passive_description": None,
            "passive_stats": None,
            "source": None,
        }

        # 查找YSCard容器来提取基础信息
        ys_cards = soup.find_all("div", class_="YSCard")
        if not ys_cards:
            logger.warning(f"No YSCard found for {weapon_name}")
            return data

        # 从第一个YSCard提取基础信息
        self._extract_basic_info(ys_cards[0], data)

        # 查找武器数据表格 (YS-WeaponData)
        weapon_data_card = soup.find("div", class_="YS-WeaponData")
        if weapon_data_card:
            data_table = weapon_data_card.find("table", class_="YS-DataTable")
            if data_table:
                self._extract_stats(data_table, data)

        # 提取被动技能和精炼数据
        self._extract_passive_skill(soup, data)

        # 提取描述
        self._extract_description(soup, data)

        # 提取英文名
        self._extract_english_name(data)

        return data

    def _extract_basic_info(self, card: Tag, data: Dict[str, Any]) -> None:
        """从YSCard容器中提取武器基础信息"""
        # 查找card-title1来提取稀有度（通过★数量）
        card_title = card.find("div", class_="card-title1")
        if card_title:
            title_text = card_title.get_text()
            star_count = title_text.count("★")
            if star_count > 0:
                data["rarity"] = star_count

        # 查找card-title2来提取副属性类型
        card_title2 = card.find("div", class_="card-title2")
        if card_title2:
            # 在card-title2的p标签中找到副属性名称
            p_tag = card_title2.find("p")
            if p_tag:
                stat_text = p_tag.get_text(strip=True)
                # 文本格式: "攻击力 48-674 /// 物理伤害加成 9.0%-41.3%"
                # 提取 "///" 后面的副属性名称部分
                if "///" in stat_text:
                    parts = stat_text.split("///")
                    if len(parts) >= 2:
                        # 取第二部分并提取属性名（去掉数值）
                        secondary_part = parts[1].strip()
                        # 使用正则提取属性名（中文部分）
                        match = re.match(r"([^\d]+)", secondary_part)
                        if match:
                            stat_name = match.group(1).strip()
                            data["secondary_stat"] = self._normalize_stat_name(stat_name)

        # 查找内容区域的所有div和p标签来提取文本信息
        content = card.get_text(strip=True)

        # 提取武器类型 - 查找包含武器类型关键词的文本
        for weapon_cn, weapon_en in self.WEAPON_MAP.items():
            if weapon_cn in content:
                data["weapon_type"] = weapon_en
                break

        # 提取描述文本（通常在YSCard的段落中）
        paragraphs = card.find_all("p")
        for p in paragraphs:
            text = p.get_text(strip=True)
            if text and len(text) >= 20 and "突破" not in text and "材料" not in text:
                if not data.get("description"):
                    data["description"] = text[:200]

    def _extract_stats(self, table: Tag, data: Dict[str, Any]) -> None:
        """从YS-DataTable中提取武器属性数据"""
        rows = table.find_all("tr")
        if len(rows) < 2:
            return

        # 第一行是表头
        headers = [th.get_text(strip=True) for th in rows[0].find_all(["th", "td"])]

        # 找到90级的数据行
        target_row = None
        for row in rows:
            cells = row.find_all("td")
            if cells and len(cells) >= 3:
                level_text = cells[0].get_text(strip=True)
                if "90" in level_text:
                    target_row = row
                    break

        if not target_row:
            return

        cells = target_row.find_all("td")
        if len(cells) < 3:
            return

        # 表格结构: 等级 | 基础攻击力(突破前) | 基础攻击力(突破后) | 副属性
        # 90级行: <td><b>90级</b></td><td>674</td><td>-</td><td>41.3%</td>
        try:
            # 提取基础攻击力（第2列，即cells[1]）
            atk_text = cells[1].get_text(strip=True)
            if atk_text and atk_text != "-":
                match = re.search(r"(\d+)", atk_text)
                if match:
                    data["base_attack"] = int(match.group(1))
        except Exception as e:
            logger.debug(f"Failed to parse base attack: {e}")

        # 提取副属性（最后一列）
        try:
            stat_cell = cells[-1]
            stat_text = stat_cell.get_text(strip=True)
            # 解析数值
            match = re.search(r"([\d.]+)%?", stat_text)
            if match:
                data["secondary_stat_value"] = match.group(1)

                # 如果还没有副属性类型,从表头推断
                if not data.get("secondary_stat") and len(headers) >= 4:
                    stat_header = headers[3]  # 第4列表头
                    data["secondary_stat"] = self._normalize_stat_name(stat_header)
        except Exception as e:
            logger.debug(f"Failed to parse secondary stat: {e}")

    def _normalize_stat_name(self, stat_header: str) -> str:
        """Normalize Chinese stat names to English."""
        stat_map = {
            "攻击力": "ATK%",
            "暴击率": "CRIT Rate",
            "暴击伤害": "CRIT DMG",
            "元素充能效率": "Energy Recharge",
            "元素精通": "Elemental Mastery",
            "物理伤害": "Physical DMG Bonus",
            "生命值": "HP%",
            "防御力": "DEF%",
        }

        for cn_name, en_name in stat_map.items():
            if cn_name in stat_header:
                return en_name

        return stat_header

    def _extract_description(self, soup: BeautifulSoup, data: Dict[str, Any]) -> None:
        """Extract weapon description."""
        content_div = soup.find("div", class_="mw-parser-output")
        if not content_div:
            return

        paragraphs = content_div.find_all("p", recursive=False)
        for p in paragraphs:
            text = p.get_text(strip=True)
            if text and len(text) >= 20:
                data["description"] = text[:200]
                break

    def _extract_english_name(self, data: Dict[str, Any]) -> None:
        """Extract English name from full_name field."""
        full_name = data.get("full_name", "")
        if not full_name:
            return

        match = re.search(r"\(([A-Za-z\s]+)\)|（([A-Za-z\s]+)）", full_name)
        if match:
            name_en = match.group(1) or match.group(2)
            data["name_en"] = name_en.strip()

    def _extract_passive_skill(self, soup: BeautifulSoup, data: Dict[str, Any]) -> None:
        """
        提取武器被动技能名称、描述和精炼数据

        被动技能通常在card-title2 div中，格式为: "武器技能 - 技能名称"
        精炼数据格式示例: 8%/10%/12%/14%/16% 或 28%/35%/42%/49%/56%
        """
        # 查找所有card-title2元素 (可能包含武器技能)
        title_divs = soup.find_all("div", class_="card-title2")

        for title_div in title_divs:
            title_text = title_div.get_text(strip=True)

            # 查找包含"武器技能"的标题
            if "武器技能" in title_text:
                # 提取技能名称
                # 格式: "武器技能 - 西风之鹰的抗争"
                skill_match = re.search(r'武器技能\s*[-－—]\s*(.+)', title_text)
                if skill_match:
                    skill_name = skill_match.group(1).strip()
                    if skill_name and len(skill_name) < 50:
                        data["passive_name"] = skill_name

                # 查找紧随其后的div（包含技能描述）
                next_div = title_div.find_next_sibling("div")
                if next_div:
                    desc_text = next_div.get_text(strip=True)

                    # 检查是否包含精炼数值
                    refinement_pattern = r'(\d+(?:\.\d+)?%?)(?:/\d+(?:\.\d+)?%?){4}'
                    if re.search(refinement_pattern, desc_text):
                        data["passive_description"] = desc_text[:500]  # 限制长度
                        # 提取精炼数据
                        data["passive_stats"] = self._parse_refinement_data(desc_text)
                        break

        # 如果没有从card-title2找到,尝试从YSCard查找
        if not data.get("passive_description"):
            self._extract_passive_from_yscard(soup, data)

        # 最后尝试从页面主要内容区域查找
        if not data.get("passive_description"):
            self._extract_passive_from_content(soup, data)

    def _parse_refinement_data(self, description: str) -> Dict[str, Any]:
        """
        从被动技能描述中解析精炼等级数据

        精炼数据格式示例:
        - "20%/25%/30%/35%/40%" -> refinement levels
        - "0.8%/1%/1.2%/1.4%/1.6%" -> refinement levels
        - "12秒/11秒/10秒/9秒/8秒" -> refinement levels
        """
        refinement_data = {"refinement_levels": []}

        # 查找所有5值精炼数值模式
        # 匹配格式: 数字/数字/数字/数字/数字(可能带%或秒等单位)
        refinement_pattern = r'(\d+(?:\.\d+)?%?)(?:/\d+(?:\.\d+)?%?){4}'

        matches = re.findall(refinement_pattern, description)

        stat_index = 0
        remaining_desc = description

        for match_text in matches:
            # 重新在剩余文本中查找完整匹配
            full_match = re.search(refinement_pattern, remaining_desc)
            if full_match:
                full_text = full_match.group(0)
                values = full_text.split('/')

                if len(values) == 5:  # 确认是5个精炼等级
                    # 创建精炼等级数据
                    refinement_level = {
                        "rank_1": values[0].strip(),
                        "rank_2": values[1].strip(),
                        "rank_3": values[2].strip(),
                        "rank_4": values[3].strip(),
                        "rank_5": values[4].strip(),
                    }

                    # 尝试识别这个数值的含义(从前后文)
                    context_before = remaining_desc[:full_match.start()][-50:]
                    stat_name = self._guess_stat_name(context_before, values[0])
                    if stat_name:
                        refinement_level["stat_name"] = stat_name

                    refinement_data["refinement_levels"].append(refinement_level)
                    stat_index += 1

                    # 移除已匹配的部分以继续查找其他数值
                    remaining_desc = remaining_desc[full_match.end():]
                else:
                    break

        # 如果找到精炼数据,添加到主字典中
        if refinement_data["refinement_levels"]:
            return refinement_data

        return {}

    def _guess_stat_name(self, context: str, first_value: str) -> Optional[str]:
        """根据上下文推测数值的含义"""
        # 常见的属性关键词映射
        stat_keywords = {
            "生命值": "hp",
            "攻击力": "atk",
            "防御力": "def",
            "暴击率": "crit_rate",
            "暴击伤害": "crit_dmg",
            "元素充能": "energy_recharge",
            "元素精通": "elemental_mastery",
            "伤害加成": "dmg_bonus",
            "伤害提升": "dmg_bonus",
            "持续时间": "duration",
            "冷却时间": "cooldown",
        }

        for keyword, stat_name in stat_keywords.items():
            if keyword in context:
                return stat_name

        # 根据单位推测
        if '秒' in first_value:
            return "duration"
        elif '%' in first_value:
            return "percentage"

        return None

    def _extract_passive_from_yscard(self, soup: BeautifulSoup, data: Dict[str, Any]) -> None:
        """从YSCard元素中提取被动技能信息（后备方案）"""
        ys_cards = soup.find_all("div", class_="YSCard")

        for card in ys_cards:
            card_text = card.get_text(strip=True)

            # 查找包含"武器技能"的文本
            if "武器技能" in card_text or "被动" in card_text:
                # 提取技能名称
                skill_match = re.search(r'武器技能\s*[-－—]\s*([^\n]+)', card_text)
                if skill_match and not data.get("passive_name"):
                    skill_name = skill_match.group(1).strip()
                    # 移除可能的属性文本
                    skill_name = re.sub(r'(攻击力|生命值|暴击|元素|伤害|效果).*', '', skill_name).strip()
                    if skill_name and len(skill_name) < 50:
                        data["passive_name"] = skill_name

                # 查找包含精炼数值的描述
                refinement_pattern = r'(\d+(?:\.\d+)?%?)(?:/\d+(?:\.\d+)?%?){4}'
                if re.search(refinement_pattern, card_text):
                    # 提取技能描述部分
                    desc_match = re.search(r'武器技能\s*[-－—]\s*[^\n]*\n?(.*?)(?=技能解析|武器介绍|武器类型|实装版本|\Z)', card_text, re.DOTALL)
                    if desc_match:
                        desc_text = desc_match.group(1).strip()
                        data["passive_description"] = desc_text[:500]
                        data["passive_stats"] = self._parse_refinement_data(desc_text)
                        break

    def _extract_passive_from_content(self, soup: BeautifulSoup, data: Dict[str, Any]) -> None:
        """从页面主要内容区域提取被动技能信息（最后的后备方案）"""
        content_div = soup.find("div", class_="mw-parser-output")
        if not content_div:
            return

        # 查找所有段落
        paragraphs = content_div.find_all("p", recursive=False)
        for p in paragraphs:
            text = p.get_text(strip=True)
            # 寻找包含精炼数值的段落
            if re.search(r'\d+(?:\.\d+)?%/\d+(?:\.\d+)?%', text) and len(text) > 30:
                if not data.get("passive_description"):
                    data["passive_description"] = text
                    data["passive_stats"] = self._parse_refinement_data(text)
                    break

    def get_stats(self) -> Dict[str, Any]:
        """Get scraping statistics."""
        return self._stats.copy()
