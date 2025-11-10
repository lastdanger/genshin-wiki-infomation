"""
Character data scraper for Genshin Impact.

Scrapes character information from:
- Bilibili Game Wiki: https://wiki.biligame.com/ys/角色筛选
- HomdGCat Wiki: https://homdgcat.wiki/gi/char
"""

import logging
import re
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin

from bs4 import BeautifulSoup, Tag

from .base_scraper import BaseScraper, ScraperConfig

logger = logging.getLogger(__name__)


class CharacterScraper(BaseScraper):
    """
    Scraper for Genshin Impact character data.

    Collects:
    - Character list (name, rarity, element, weapon type)
    - Character details (stats, skills, talents, constellations)
    - Ascension materials
    """

    # Data source URLs
    BILIBILI_BASE_URL = "https://wiki.biligame.com/ys"
    BILIBILI_CHARACTER_LIST_URL = f"{BILIBILI_BASE_URL}/角色筛选"
    HOMDGCAT_BASE_URL = "https://homdgcat.wiki/gi"
    HOMDGCAT_CHARACTER_URL = f"{HOMDGCAT_BASE_URL}/char"

    # Element mapping (Chinese to English)
    ELEMENT_MAP = {
        "火": "Pyro",
        "水": "Hydro",
        "风": "Anemo",
        "雷": "Electro",
        "草": "Dendro",
        "冰": "Cryo",
        "岩": "Geo",
    }

    # Weapon type mapping
    WEAPON_MAP = {
        "单手剑": "Sword",
        "双手剑": "Claymore",
        "长柄武器": "Polearm",
        "法器": "Catalyst",
        "弓": "Bow",
    }

    def __init__(self, config: Optional[ScraperConfig] = None):
        """Initialize character scraper."""
        super().__init__(config)
        self._character_cache: Dict[str, Dict[str, Any]] = {}

    async def scrape(self) -> List[Dict[str, Any]]:
        """
        Scrape all character data.

        Returns:
            List of character dictionaries with complete information
        """
        logger.info("Starting character scraping...")

        # Step 1: Get character list
        character_list = await self.scrape_character_list()
        logger.info(f"Found {len(character_list)} characters")

        # Step 2: Get details for each character
        characters_with_details = []
        for char_data in character_list:
            try:
                details = await self.scrape_character_details(char_data)
                if details:
                    characters_with_details.append(details)
                    logger.info(f"Scraped details for {details['name']}")
            except Exception as e:
                logger.error(
                    f"Error scraping details for {char_data.get('name')}: {e}",
                    exc_info=True
                )

        logger.info(f"Successfully scraped {len(characters_with_details)} characters")
        return characters_with_details

    async def scrape_character_list(self) -> List[Dict[str, Any]]:
        """
        Scrape character list from Bilibili Wiki.

        Returns:
            List of basic character info (name, rarity, element, weapon)
        """
        logger.info(f"Fetching character list from {self.BILIBILI_CHARACTER_LIST_URL}")

        html = await self.fetch(self.BILIBILI_CHARACTER_LIST_URL)
        if not html:
            logger.error("Failed to fetch character list")
            return []

        soup = self.parse_html(html)
        if not soup:
            logger.error("Failed to parse character list HTML")
            return []

        characters = []

        # Find character table/cards
        # Note: The actual structure depends on the website's HTML
        # This is a template that needs to be adjusted based on actual site structure
        character_elements = soup.select(".character-card, .role-box, tr.character-row")

        if not character_elements:
            logger.warning("No character elements found with default selectors")
            # Try alternative selectors
            character_elements = soup.find_all("div", class_=re.compile(r"character|role|char"))

        for element in character_elements:
            try:
                char_data = self._parse_character_list_item(element)
                if char_data:
                    characters.append(char_data)
            except Exception as e:
                logger.warning(f"Error parsing character element: {e}")
                continue

        return characters

    def _parse_character_list_item(self, element: Tag) -> Optional[Dict[str, Any]]:
        """
        Parse a single character from the list.

        Args:
            element: BeautifulSoup Tag element

        Returns:
            Dictionary with basic character info, or None if parsing fails
        """
        try:
            # Extract character name
            name_element = element.select_one(".name, .character-name, a[title]")
            if not name_element:
                return None

            name = name_element.get_text(strip=True)
            if not name:
                return None

            # Extract detail page URL
            detail_url = None
            link = element.find("a", href=True)
            if link:
                detail_url = urljoin(self.BILIBILI_BASE_URL, link["href"])

            # Extract rarity (星级)
            rarity = None
            rarity_element = element.select_one(".rarity, .star, [class*='star']")
            if rarity_element:
                rarity_text = rarity_element.get_text(strip=True)
                # Extract number from text like "5星" or "★★★★★"
                rarity_match = re.search(r"(\d)", rarity_text)
                if rarity_match:
                    rarity = int(rarity_match.group(1))
                else:
                    # Count stars
                    rarity = rarity_text.count("★")

            # Extract element (元素)
            element_type = None
            element_elem = element.select_one(".element, .attr, [class*='element']")
            if element_elem:
                element_text = element_elem.get_text(strip=True)
                element_type = self.ELEMENT_MAP.get(element_text, element_text)

            # Extract weapon type (武器类型)
            weapon_type = None
            weapon_elem = element.select_one(".weapon, .weapon-type, [class*='weapon']")
            if weapon_elem:
                weapon_text = weapon_elem.get_text(strip=True)
                weapon_type = self.WEAPON_MAP.get(weapon_text, weapon_text)

            # Extract region (国家/地区)
            region = None
            region_elem = element.select_one(".region, .nation, [class*='region']")
            if region_elem:
                region = region_elem.get_text(strip=True)

            character_data = {
                "name": name,
                "rarity": rarity,
                "element": element_type,
                "weapon_type": weapon_type,
                "region": region,
                "detail_url": detail_url,
            }

            return character_data

        except Exception as e:
            logger.warning(f"Error parsing character list item: {e}")
            return None

    async def scrape_character_details(
        self, basic_info: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Scrape detailed information for a single character.

        Args:
            basic_info: Basic character info from character list

        Returns:
            Complete character data with details
        """
        detail_url = basic_info.get("detail_url")
        if not detail_url:
            logger.warning(f"No detail URL for {basic_info.get('name')}")
            return basic_info

        logger.info(f"Fetching details for {basic_info['name']} from {detail_url}")

        html = await self.fetch(detail_url)
        if not html:
            logger.error(f"Failed to fetch details for {basic_info['name']}")
            return basic_info

        soup = self.parse_html(html)
        if not soup:
            logger.error(f"Failed to parse details HTML for {basic_info['name']}")
            return basic_info

        # Start with basic info
        character_data = basic_info.copy()

        # Extract additional details
        character_data.update({
            "description": self._extract_description(soup),
            "base_stats": self._extract_base_stats(soup),
            "skills": self._extract_skills(soup),
            "talents": self._extract_talents(soup),
            "constellations": self._extract_constellations(soup),
            "ascension_materials": self._extract_ascension_materials(soup),
        })

        return character_data

    def _extract_description(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract character description."""
        try:
            desc_element = soup.select_one(".description, .intro, .character-desc")
            if desc_element:
                return desc_element.get_text(strip=True)
        except Exception as e:
            logger.warning(f"Error extracting description: {e}")
        return None

    def _extract_base_stats(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract character base stats (HP, ATK, DEF)."""
        stats = {
            "hp": None,
            "attack": None,
            "defense": None,
            "crit_rate": None,
            "crit_dmg": None,
        }

        try:
            # Look for stats table
            stats_table = soup.select_one(".stats-table, table.character-stats")
            if stats_table:
                rows = stats_table.find_all("tr")
                for row in rows:
                    cells = row.find_all(["th", "td"])
                    if len(cells) >= 2:
                        stat_name = cells[0].get_text(strip=True)
                        stat_value = cells[1].get_text(strip=True)

                        # Parse stat values
                        value_match = re.search(r"([\d,]+\.?\d*)", stat_value)
                        if value_match:
                            value = float(value_match.group(1).replace(",", ""))

                            if "生命值" in stat_name or "HP" in stat_name.upper():
                                stats["hp"] = value
                            elif "攻击力" in stat_name or "ATK" in stat_name.upper():
                                stats["attack"] = value
                            elif "防御力" in stat_name or "DEF" in stat_name.upper():
                                stats["defense"] = value
                            elif "暴击率" in stat_name or "CRIT Rate" in stat_name:
                                stats["crit_rate"] = value
                            elif "暴击伤害" in stat_name or "CRIT DMG" in stat_name:
                                stats["crit_dmg"] = value

        except Exception as e:
            logger.warning(f"Error extracting base stats: {e}")

        return stats

    def _extract_skills(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract character skills (Normal Attack, Elemental Skill, Elemental Burst)."""
        skills = []

        try:
            skill_sections = soup.select(".skill-section, .talent-section, div[id*='skill']")

            for section in skill_sections:
                skill_name = None
                skill_desc = None
                skill_type = None

                # Extract skill name
                name_elem = section.select_one("h2, h3, .skill-name, .talent-name")
                if name_elem:
                    skill_name = name_elem.get_text(strip=True)

                # Extract skill description
                desc_elem = section.select_one("p, .skill-desc, .talent-desc")
                if desc_elem:
                    skill_desc = desc_elem.get_text(strip=True)

                # Determine skill type
                if skill_name:
                    if "普通攻击" in skill_name or "Normal Attack" in skill_name:
                        skill_type = "normal_attack"
                    elif "元素战技" in skill_name or "Elemental Skill" in skill_name:
                        skill_type = "elemental_skill"
                    elif "元素爆发" in skill_name or "Elemental Burst" in skill_name:
                        skill_type = "elemental_burst"

                if skill_name and skill_desc:
                    skills.append({
                        "name": skill_name,
                        "type": skill_type,
                        "description": skill_desc,
                    })

        except Exception as e:
            logger.warning(f"Error extracting skills: {e}")

        return skills

    def _extract_talents(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract character passive talents."""
        talents = []

        try:
            talent_sections = soup.select(".passive-talent, div[id*='passive']")

            for section in talent_sections:
                talent_name = section.select_one("h3, .talent-name")
                talent_desc = section.select_one("p, .talent-desc")

                if talent_name and talent_desc:
                    talents.append({
                        "name": talent_name.get_text(strip=True),
                        "description": talent_desc.get_text(strip=True),
                    })

        except Exception as e:
            logger.warning(f"Error extracting talents: {e}")

        return talents

    def _extract_constellations(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract character constellations (命之座)."""
        constellations = []

        try:
            const_sections = soup.select(".constellation, div[id*='constellation']")

            for i, section in enumerate(const_sections, 1):
                const_name = section.select_one("h3, .constellation-name")
                const_desc = section.select_one("p, .constellation-desc")

                if const_name and const_desc:
                    constellations.append({
                        "level": i,
                        "name": const_name.get_text(strip=True),
                        "description": const_desc.get_text(strip=True),
                    })

        except Exception as e:
            logger.warning(f"Error extracting constellations: {e}")

        return constellations

    def _extract_ascension_materials(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract ascension materials."""
        materials = []

        try:
            material_sections = soup.select(".material, .ascension-material, table.materials")

            for section in material_sections:
                rows = section.find_all("tr")

                for row in rows:
                    cells = row.find_all(["th", "td"])
                    if len(cells) >= 2:
                        material_name = cells[0].get_text(strip=True)
                        quantity_text = cells[1].get_text(strip=True)

                        # Extract quantity
                        quantity_match = re.search(r"(\d+)", quantity_text)
                        quantity = int(quantity_match.group(1)) if quantity_match else None

                        if material_name and quantity:
                            materials.append({
                                "name": material_name,
                                "quantity": quantity,
                            })

        except Exception as e:
            logger.warning(f"Error extracting ascension materials: {e}")

        return materials
