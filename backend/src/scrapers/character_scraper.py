"""
Character data scraper for Genshin Impact.

Scrapes character information from individual character pages on Bilibili Game Wiki.
URL pattern: https://wiki.biligame.com/ys/{角色中文名}
"""

import logging
import re
from typing import Any, Dict, List, Optional
from urllib.parse import quote

from bs4 import BeautifulSoup, Tag

from .base_scraper import BaseScraper, ScraperConfig

logger = logging.getLogger(__name__)


class CharacterScraper(BaseScraper):
    """
    Scraper for Genshin Impact character data.

    Uses individual character URLs to extract:
    - Basic info (name, rarity, element, weapon type, region)
    - Stats (HP, ATK, DEF, ascension bonus)
    - Description
    """

    # Data source URLs
    BILIBILI_BASE_URL = "https://wiki.biligame.com/ys"

    # Element mapping (Chinese to English)
    ELEMENT_MAP = {
        "火": "Pyro",
        "火元素": "Pyro",
        "水": "Hydro",
        "水元素": "Hydro",
        "风": "Anemo",
        "风元素": "Anemo",
        "雷": "Electro",
        "雷元素": "Electro",
        "草": "Dendro",
        "草元素": "Dendro",
        "冰": "Cryo",
        "冰元素": "Cryo",
        "岩": "Geo",
        "岩元素": "Geo",
    }

    # Weapon type mapping (Chinese to English)
    WEAPON_MAP = {
        "单手剑": "Sword",
        "单手剑武器使用": "Sword",
        "双手剑": "Claymore",
        "双手剑武器使用": "Claymore",
        "长柄武器": "Polearm",
        "长柄武器武器使用": "Polearm",
        "弓": "Bow",
        "弓武器使用": "Bow",
        "弓箭武器使用": "Bow",
        "法器": "Catalyst",
        "法器武器使用": "Catalyst",
    }

    # Region mapping (Chinese to English)
    REGION_MAP = {
        "蒙德": "Mondstadt",
        "璃月": "Liyue",
        "稻妻": "Inazuma",
        "须弥": "Sumeru",
        "枫丹": "Fontaine",
        "纳塔": "Natlan",
        "至冬": "Snezhnaya",
    }

    def __init__(self, config: Optional[ScraperConfig] = None):
        """Initialize character scraper."""
        super().__init__(config)
        self._character_cache: Dict[str, Dict[str, Any]] = {}

        # Initialize stats if parent didn't
        if not hasattr(self, '_stats'):
            self._stats = {
                "requests": 0,
                "errors": 0,
                "success_rate": 100.0,
            }

    async def scrape(self, character_names: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Scrape character data for specified characters.

        Args:
            character_names: List of character names (Chinese) to scrape.
                           If None, will use the default production list (all characters).

        Returns:
            List of character dictionaries with complete information
        """
        if character_names is None:
            # Production default: all characters (5.2 version)
            character_names = self._get_default_character_list()

        logger.info(f"Starting character scraping for {len(character_names)} characters...")

        characters = []
        for char_name in character_names:
            try:
                char_data = await self.scrape_character(char_name)
                if char_data:
                    characters.append(char_data)
                    logger.info(f"✅ Scraped: {char_name}")
                else:
                    logger.warning(f"⚠️  No data for: {char_name}")
            except Exception as e:
                logger.error(f"❌ Error scraping {char_name}: {e}", exc_info=True)
                self._stats["errors"] += 1

        logger.info(f"Successfully scraped {len(characters)}/{len(character_names)} characters")
        return characters

    def _get_default_character_list(self) -> List[str]:
        """
        Get the default character list for production.

        Returns all characters from version 5.2, organized by region.
        To customize, either:
        1. Modify this method
        2. Pass character_names parameter to scrape()
        3. Use environment variable SCRAPER_CHARACTERS
        4. Configure via database (if enabled)
        """
        import os

        # Check environment variable first
        env_characters = os.getenv("SCRAPER_CHARACTERS")
        if env_characters:
            return [name.strip() for name in env_characters.split(",")]

        # Default: all characters by region (Genshin Impact 5.2)
        return [
            # 蒙德 (Mondstadt) - 5星
            "琴", "迪卢克", "莫娜", "温迪", "可莉", "优菈", "阿贝多",

            # 蒙德 (Mondstadt) - 4星
            "班尼特", "砂糖", "菲谢尔", "芭芭拉", "雷泽", "诺艾尔", "罗莎莉亚", "米卡",

            # 璃月 (Liyue) - 5星
            "刻晴", "魈", "甘雨", "胡桃", "钟离", "七七",

            # 璃月 (Liyue) - 4星
            "香菱", "行秋", "北斗", "凝光", "辛焱", "重云", "烟绯", "云堇", "瑶瑶", "嘉明",

            # 稻妻 (Inazuma) - 5星
            "雷电将军", "神里绫华", "宵宫", "珊瑚宫心海", "荒瀧一斗", "八重神子", "神里绫人",

            # 稻妻 (Inazuma) - 4星
            "早柚", "九条裟罗", "托马", "五郎", "久岐忍", "鹿野院平藏", "绮良良",

            # 须弥 (Sumeru) - 5星
            "纳西妲", "提纳里", "赛诺", "妮露", "流浪者", "艾尔海森", "迪希雅",

            # 须弥 (Sumeru) - 4星
            "柯莱", "多莉", "坎蒂丝", "莱依拉", "珐露珊", "卡维", "白术",

            # 枫丹 (Fontaine) - 5星
            "那维莱特", "芙宁娜", "莱欧斯利", "娜维娅", "克洛琳德", "阿蕾奇诺", "希格雯",

            # 枫丹 (Fontaine) - 4星
            "琳妮特", "菲米尼", "夏沃蕾", "夏洛蒂", "嘉维尔", "艾梅莉埃",

            # 纳塔 (Natlan) - 5星
            "玛拉妮", "基尼奇", "希诺宁",

            # 纳塔 (Natlan) - 4星
            "卡齐娜",

            # 其他 (Starter characters)
            "旅行者", "安柏", "凯亚", "丽莎",
        ]

    async def scrape_character(self, char_name: str) -> Optional[Dict[str, Any]]:
        """
        Scrape single character data from their wiki page.

        Args:
            char_name: Character name in Chinese (e.g., "琴", "雷电将军")

        Returns:
            Character data dictionary or None if scraping failed
        """
        # Build character URL
        encoded_name = quote(char_name)
        url = f"{self.BILIBILI_BASE_URL}/{encoded_name}"

        logger.debug(f"Fetching character page: {url}")

        # Fetch HTML
        html = await self.fetch(url)
        if not html:
            logger.error(f"Failed to fetch page for {char_name}")
            return None

        # Parse HTML
        soup = self.parse_html(html)
        if not soup:
            logger.error(f"Failed to parse HTML for {char_name}")
            return None

        # Extract character data
        try:
            char_data = self._extract_character_data(soup, char_name)
            return char_data
        except Exception as e:
            logger.error(f"Failed to extract data for {char_name}: {e}", exc_info=True)
            return None

    def _extract_character_data(self, soup: BeautifulSoup, char_name: str) -> Dict[str, Any]:
        """
        Extract character data from parsed HTML.

        Args:
            soup: BeautifulSoup object
            char_name: Character name

        Returns:
            Character data dictionary
        """
        data = {
            "name": char_name,
            "name_en": None,
            "rarity": None,
            "element": None,
            "weapon_type": None,
            "region": None,
            "description": None,
            "base_stats": {},
            "ascension_stats": {},
        }

        # Find all wikitable tables
        tables = soup.find_all("table", class_="wikitable")

        if not tables:
            logger.warning(f"No wikitable found for {char_name}")
            return data

        # Extract from first table (basic info)
        if len(tables) >= 1:
            self._extract_basic_info(tables[0], data)

        # Extract from second table (stats)
        if len(tables) >= 2:
            self._extract_stats(tables[1], data)

        # Extract description
        self._extract_description(soup, data)

        # Extract English name from full name
        self._extract_english_name(data)

        # Handle special cases (Traveler)
        self._handle_special_characters(data, char_name)

        return data

    def _extract_basic_info(self, table: Tag, data: Dict[str, Any]) -> None:
        """Extract basic character info from the first wikitable."""
        rows = table.find_all("tr")

        for row in rows:
            th = row.find("th")
            td = row.find("td")

            if not th or not td:
                continue

            label = th.get_text(strip=True)
            value = td.get_text(strip=True)

            # Extract based on label
            if "全名" in label or "本名" in label:
                data["full_name"] = value

            elif "所属地区" in label:
                # Map Chinese region to English
                data["region"] = self.REGION_MAP.get(value, value)

            elif "神之眼" in label or "神之心" in label or "古龙大权" in label:
                # Extract element (remove "元素" suffix)
                element_zh = value.replace("元素", "").strip()
                data["element"] = self.ELEMENT_MAP.get(element_zh, element_zh)

            elif "武器类型" in label:
                # Map weapon type
                data["weapon_type"] = self.WEAPON_MAP.get(value, value)

            elif "稀有度" in label:
                # Try to extract rarity from alt text or image filename
                # Format: "5星.png" or "4星.png"
                stars = td.find_all("img")
                rarity = None

                if stars:
                    # Check first image's alt or src
                    img = stars[0]
                    alt = img.get("alt", "")
                    src = img.get("src", "")

                    # Try to extract from alt text (e.g., "5星.png")
                    match = re.search(r"(\d+)星", alt)
                    if match:
                        rarity = int(match.group(1))
                    else:
                        # Try to extract from src filename
                        match = re.search(r"(\d+)星", src)
                        if match:
                            rarity = int(match.group(1))

                if not rarity:
                    # Fallback: count ★ symbols in text
                    star_count = value.count("★") or value.count("☆")
                    if star_count > 0:
                        rarity = star_count

                if rarity:
                    data["rarity"] = rarity

    def _extract_stats(self, table: Tag, data: Dict[str, Any]) -> None:
        """Extract character stats from the second wikitable."""
        # Find all rows (including header)
        all_rows = table.find_all("tr")

        if len(all_rows) < 2:
            return

        # First row is header with stat names
        header_row = all_rows[0]
        headers = [th.get_text(strip=True) for th in header_row.find_all("th")]

        # Skip second row (it's "突破前/突破后" row)
        # Data rows start from index 2
        data_rows = all_rows[2:] if len(all_rows) > 2 else []

        if not data_rows:
            return

        # Find level 90 row (last row usually)
        target_row = None

        for row in reversed(data_rows):  # Search from end
            cells = row.find_all("td")
            if cells:
                level_text = cells[0].get_text(strip=True)
                # Match "90" exactly
                if level_text == "90" or level_text == "90级":
                    target_row = row
                    break

        # Fallback to last data row
        if not target_row and data_rows:
            target_row = data_rows[-1]

        if not target_row:
            return

        cells = target_row.find_all("td")

        # For level 90 row, cells structure is:
        # [level, hp, '-', atk, '-', def, '-', bonus_stat, '-']
        # We need to extract: cells[1]=HP, cells[3]=ATK, cells[5]=DEF, cells[7]=bonus

        # Map headers to cell indices (skip "-" cells)
        cell_index = 1  # Start after level cell

        for i, header in enumerate(headers):
            if i == 0:  # Skip "等级" header
                continue

            if cell_index >= len(cells):
                break

            # Get cell value
            value_text = cells[cell_index].get_text(strip=True)

            # Skip to next valid cell (skip "-" cells)
            # For 90 level row: indices 1, 3, 5, 7 have values
            cell_index += 2  # Skip current + "-" cell

            # Skip if "-" or empty
            if not value_text or value_text == "-":
                continue

            # Try to extract numeric value
            try:
                # Remove percentage signs, commas, spaces
                value_clean = value_text.replace("%", "").replace(",", "").replace("，", "").replace(" ", "")
                # Extract number
                match = re.search(r"([\d.]+)", value_clean)
                if match:
                    num_str = match.group(1)
                    value = float(num_str) if "." in num_str else int(num_str)
                else:
                    continue
            except Exception as e:
                logger.debug(f"Failed to parse value '{value_text}' for header '{header}': {e}")
                continue

            # Map header to field
            header_lower = header.lower()

            if "生命" in header or "hp" in header_lower:
                data["base_stats"]["hp"] = value
            elif "攻击" in header or "atk" in header_lower or "attack" in header_lower:
                data["base_stats"]["atk"] = value
            elif "防御" in header or "def" in header_lower or "defense" in header_lower:
                data["base_stats"]["def"] = value
            elif "暴击率" in header or ("暴击" in header and "率" in header):
                data["ascension_stats"]["stat"] = "crit_rate"
                data["ascension_stats"]["value"] = value
            elif "暴击伤害" in header or ("暴击" in header and "伤" in header):
                data["ascension_stats"]["stat"] = "crit_dmg"
                data["ascension_stats"]["value"] = value
            elif "元素充能" in header or "energy" in header_lower:
                data["ascension_stats"]["stat"] = "energy_recharge"
                data["ascension_stats"]["value"] = value
            elif "治疗" in header or "heal" in header_lower:
                data["ascension_stats"]["stat"] = "healing_bonus"
                data["ascension_stats"]["value"] = value
            elif "元素精通" in header or "mastery" in header_lower:
                data["ascension_stats"]["stat"] = "elemental_mastery"
                data["ascension_stats"]["value"] = int(value)
            elif "物理伤害" in header:
                data["ascension_stats"]["stat"] = "physical_dmg_bonus"
                data["ascension_stats"]["value"] = value
            elif "元素伤害" in header or "伤害加成" in header:
                # Generic elemental damage bonus
                data["ascension_stats"]["stat"] = "elemental_dmg_bonus"
                data["ascension_stats"]["value"] = value

    def _extract_description(self, soup: BeautifulSoup, data: Dict[str, Any]) -> None:
        """Extract character description from page content."""
        content_div = soup.find("div", class_="mw-parser-output")

        if not content_div:
            return

        # Find first meaningful paragraph
        paragraphs = content_div.find_all("p", recursive=False)

        for p in paragraphs:
            text = p.get_text(strip=True)

            # Skip empty or very short paragraphs
            if not text or len(text) < 20:
                continue

            # Skip paragraphs that are just navigation or metadata
            if any(skip in text for skip in ["第", "章", "幕", "====", "CV", "配音"]):
                continue

            # Found a good description
            data["description"] = text[:200]  # Limit to 200 chars
            break

    def _extract_english_name(self, data: Dict[str, Any]) -> None:
        """Extract English name from full_name field."""
        full_name = data.get("full_name", "")

        if not full_name:
            return

        # Look for English name in parentheses
        # Format: "琴·古恩希尔德（Jean Gunnhildr）"
        match = re.search(r"\(([A-Za-z\s]+)\)|（([A-Za-z\s]+)）", full_name)

        if match:
            # Get the first non-empty group
            name_en = match.group(1) or match.group(2)
            data["name_en"] = name_en.strip()

    def _handle_special_characters(self, data: Dict[str, Any], char_name: str) -> None:
        """
        Handle special character cases (e.g., Traveler with no fixed element).

        Args:
            data: Character data dictionary
            char_name: Character name
        """
        # Traveler (旅行者) doesn't have a fixed element, set to Anemo as default
        if char_name == "旅行者":
            if not data.get("element"):
                data["element"] = "Anemo"  # Default to Anemo (wind element)
                logger.info(f"Setting default element 'Anemo' for {char_name}")

            # Set English name if missing
            if not data.get("name_en"):
                data["name_en"] = "Traveler"

            # Set region if missing
            if not data.get("region"):
                data["region"] = "其他"

    def get_stats(self) -> Dict[str, Any]:
        """
        Get scraping statistics.

        Returns:
            Statistics dictionary
        """
        return self._stats.copy()
