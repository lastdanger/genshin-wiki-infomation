"""
原神圣遗物数据爬虫

从B站游戏Wiki抓取圣遗物套装信息
URL模式: https://wiki.biligame.com/ys/{圣遗物套装名}
"""

import logging
import re
from typing import Any, Dict, List, Optional
from urllib.parse import quote

from bs4 import BeautifulSoup, Tag

from .base_scraper import BaseScraper, ScraperConfig

logger = logging.getLogger(__name__)


class ArtifactScraper(BaseScraper):
    """
    原神圣遗物套装数据爬虫

    提取内容:
    - 套装名称（中文和英文）
    - 稀有度
    - 套装效果（2件套、4件套效果）
    - 描述
    """

    BILIBILI_BASE_URL = "https://wiki.biligame.com/ys"

    def __init__(self, config: Optional[ScraperConfig] = None):
        """初始化圣遗物爬虫"""
        super().__init__(config)
        self._artifact_cache: Dict[str, Dict[str, Any]] = {}

        if not hasattr(self, '_stats'):
            self._stats = {
                "requests": 0,
                "errors": 0,
                "success_rate": 100.0,
            }

    async def scrape(self, artifact_set_names: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        爬取指定圣遗物套装的数据

        Args:
            artifact_set_names: 圣遗物套装名称列表（中文）。如果为None，使用默认列表

        Returns:
            圣遗物套装数据字典列表
        """
        if artifact_set_names is None:
            artifact_set_names = self._get_default_artifact_list()

        logger.info(f"Starting artifact scraping for {len(artifact_set_names)} sets...")

        artifacts = []
        for set_name in artifact_set_names:
            try:
                artifact_data = await self.scrape_artifact_set(set_name)
                if artifact_data:
                    artifacts.append(artifact_data)
                    logger.info(f"✅ Scraped: {set_name}")
                else:
                    logger.warning(f"⚠️  No data for: {set_name}")
            except Exception as e:
                logger.error(f"❌ Error scraping {set_name}: {e}", exc_info=True)
                self._stats["errors"] += 1

        logger.info(f"Successfully scraped {len(artifacts)}/{len(artifact_set_names)} artifact sets")
        return artifacts

    def _get_default_artifact_list(self) -> List[str]:
        """获取默认圣遗物套装列表（截止到6.1版本的所有圣遗物）"""
        import os
        import sys
        from pathlib import Path

        # 优先使用环境变量
        env_artifacts = os.getenv("SCRAPER_ARTIFACTS")
        if env_artifacts:
            return [name.strip() for name in env_artifacts.split(",")]

        # 导入圣遗物列表配置
        try:
            # 添加config目录到路径
            config_path = Path(__file__).parent.parent.parent / "config"
            sys.path.insert(0, str(config_path))

            from artifacts_list import get_all_artifacts
            return get_all_artifacts()
        except ImportError:
            logger.warning("无法导入圣遗物列表配置，使用默认列表")
            # 降级到5星套装列表
            return [
                # 6.x 版本（空月之歌）
                "穹境示现之夜", "纺月的夜歌", "深廊终曲", "长夜之誓",

                # 5.x 版本
                "烬城勇者绘卷", "黑曜秘典", "未竟的遐思", "谐律异想断章",
                "回声之林夜话", "昔时之歌",

                # 4.x 版本（枫丹）
                "逐影猎人", "黄金剧团", "水仙之梦", "花海甘露之光",
                "乐园遗落之花", "沙上楼阁史话",

                # 3.x 版本（须弥）
                "深林的记忆", "饰金之梦", "金缚之梦", "来歆余响", "辰砂往生录",

                # 2.x 版本（稻妻）
                "绝缘之旗印", "华馆梦醒形骸记", "海染砗磲", "平息鸣雷的尊者", "追忆之注连",

                # 1.x 及以前版本
                "炽烈的炎之魔女", "翠绿之影", "冰风迷途的勇士", "渡过烈火的贤人",
                "被怜爱的少女", "苍白之火", "染血的骑士道", "沉沦之心",
                "千岩牢固", "悠古的磐岩", "逆飞的流星",

                # 常驻套装
                "角斗士的终幕礼", "流浪大地的乐团",
            ]

    async def scrape_artifact_set(self, set_name: str) -> Optional[Dict[str, Any]]:
        """
        Scrape single artifact set data from wiki page.

        Args:
            set_name: Artifact set name in Chinese

        Returns:
            Artifact set data dictionary or None if failed
        """
        encoded_name = quote(set_name)
        url = f"{self.BILIBILI_BASE_URL}/{encoded_name}"

        logger.debug(f"Fetching artifact set page: {url}")

        html = await self.fetch(url)
        if not html:
            logger.error(f"Failed to fetch page for {set_name}")
            return None

        soup = self.parse_html(html)
        if not soup:
            logger.error(f"Failed to parse HTML for {set_name}")
            return None

        try:
            artifact_data = self._extract_artifact_data(soup, set_name)
            return artifact_data
        except Exception as e:
            logger.error(f"Failed to extract data for {set_name}: {e}", exc_info=True)
            return None

    def _extract_artifact_data(self, soup: BeautifulSoup, set_name: str) -> Dict[str, Any]:
        """Extract artifact set data from parsed HTML."""
        data = {
            "name": set_name,
            "name_en": None,
            "max_rarity": 5,  # Default to 5-star
            "tags": [],  # 新增：套装TAG
            "two_piece_bonus": None,
            "four_piece_bonus": None,
            "description": None,
            "pieces": [],  # 新增：部件列表
        }

        # 查找属性容器 (div.attribute)
        attribute_div = soup.find("div", class_="attribute")
        if not attribute_div:
            logger.warning(f"No attribute div found for {set_name}")
            return data

        # 提取基础信息（稀有度、TAG等）
        self._extract_basic_info(attribute_div, data)

        # 查找套装效果表格 (table.effect)
        effect_table = attribute_div.find("table", class_="effect")
        if effect_table:
            self._extract_set_bonuses_from_table(effect_table, data)
        else:
            logger.warning(f"No effect table found for {set_name}")

        # Extract description
        self._extract_description(soup, data)

        # Extract English name
        self._extract_english_name(data)

        # Extract pieces information (新增：提取部件信息)
        self._extract_pieces(soup, data)

        return data

    def _extract_basic_info(self, attribute_div: Tag, data: Dict[str, Any]) -> None:
        """Extract basic artifact set info from attribute div."""
        # 提取稀有度 - 从 div.star 中的图片alt提取
        star_div = attribute_div.find("div", class_="star")
        if star_div:
            # 查找所有星级图片
            star_images = star_div.find_all("img")
            max_rarity = 1
            for img in star_images:
                alt = img.get("alt", "")
                # 提取 "圣遗物套装-5星.png" 中的数字
                match = re.search(r"(\d+)星", alt)
                if match:
                    rarity = int(match.group(1))
                    max_rarity = max(max_rarity, rarity)
            if max_rarity > 1:
                data["max_rarity"] = max_rarity

        # 提取套装名称（英文名）- 如果有的话
        name_div = attribute_div.find("div", class_="name")
        if name_div:
            full_name = name_div.get_text(strip=True)
            data["full_name"] = full_name

        # 提取套装TAG - 从 div.tag 中提取（新增）
        tag_div = attribute_div.find("div", class_="tag")
        if tag_div:
            tag_text = tag_div.get_text(strip=True)
            # 文本格式: "TAG：元素伤害、火"
            if "TAG：" in tag_text or "TAG:" in tag_text:
                # 移除"TAG："前缀，按"、"或","分割
                tag_content = tag_text.replace("TAG：", "").replace("TAG:", "").strip()
                tags = [tag.strip() for tag in re.split(r"[、,]", tag_content) if tag.strip()]
                data["tags"] = tags
                logger.debug(f"Found tags: {tags}")

    def _extract_set_bonuses_from_table(self, table: Tag, data: Dict[str, Any]) -> None:
        """Extract 2-piece and 4-piece set bonuses from effect table."""
        rows = table.find_all("tr")

        for row in rows:
            cells = row.find_all("td")
            if len(cells) >= 2:
                piece_count = cells[0].get_text(strip=True)
                effect_text = cells[1].get_text(strip=True)

                # 2件套效果
                if "2件套" in piece_count or "二件套" in piece_count:
                    data["two_piece_bonus"] = effect_text[:300]
                    logger.debug(f"Found 2-piece bonus: {effect_text[:50]}...")

                # 4件套效果
                elif "4件套" in piece_count or "四件套" in piece_count:
                    data["four_piece_bonus"] = effect_text[:500]
                    logger.debug(f"Found 4-piece bonus: {effect_text[:50]}...")

    def _extract_description(self, soup: BeautifulSoup, data: Dict[str, Any]) -> None:
        """Extract artifact set description."""
        content_div = soup.find("div", class_="mw-parser-output")
        if not content_div:
            return

        paragraphs = content_div.find_all("p", recursive=False)
        for p in paragraphs:
            text = p.get_text(strip=True)
            if text and len(text) >= 20:
                # Skip if it looks like set bonus description
                if "件套" not in text:
                    data["description"] = text[:200]
                    break

    def _extract_english_name(self, data: Dict[str, Any]) -> None:
        """Extract English name from full_name field."""
        full_name = data.get("full_name", "")
        if not full_name:
            return

        match = re.search(r"\(([A-Za-z\s']+)\)|（([A-Za-z\s']+)）", full_name)
        if match:
            name_en = match.group(1) or match.group(2)
            data["name_en"] = name_en.strip()

    def _extract_pieces(self, soup: BeautifulSoup, data: Dict[str, Any]) -> None:
        """Extract artifact piece information (花、羽、沙、杯、冠)."""
        # 查找所有部件容器 (div.bili-list-style)
        piece_divs = soup.find_all("div", class_="bili-list-style")

        if not piece_divs:
            logger.warning("No piece information found")
            return

        # 查找部件背景故事 (div.story)
        intext_div = soup.find("div", class_="intext")
        story_divs = []
        if intext_div:
            story_divs = intext_div.find_all("div", class_="story")

        pieces = []
        for i, piece_div in enumerate(piece_divs):
            icon_div = piece_div.find("div", class_="icon")
            if not icon_div:
                continue

            main_div = icon_div.find("div", class_="main")
            if not main_div:
                continue

            # 提取部件名称（中文）
            up_div = main_div.find("div", class_="up")
            piece_name = up_div.get_text(strip=True) if up_div else None

            # 提取部位（中文）
            down_div = main_div.find("div", class_="down")
            slot_cn = down_div.get_text(strip=True) if down_div else None

            # 将中文部位映射到英文
            slot_map = {
                "生之花": "flower",
                "死之羽": "plume",
                "时之沙": "sands",
                "空之杯": "goblet",
                "理之冠": "circlet"
            }
            slot = slot_map.get(slot_cn, slot_cn)

            # 提取背景故事（如果有）
            lore = None
            if i < len(story_divs):
                lore = story_divs[i].get_text(strip=True)

            piece_data = {
                "slot": slot,
                "slot_cn": slot_cn,
                "piece_name": piece_name,
                "piece_name_en": None,  # 英文名暂无，可后续添加
                "lore": lore,
            }

            pieces.append(piece_data)
            logger.debug(f"Extracted piece: {slot_cn} - {piece_name}")

        data["pieces"] = pieces
        logger.info(f"Extracted {len(pieces)} artifact pieces")

    def get_stats(self) -> Dict[str, Any]:
        """Get scraping statistics."""
        return self._stats.copy()
