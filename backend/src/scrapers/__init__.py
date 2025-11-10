"""
Web scraper module for Genshin Impact data collection.

This module provides scrapers for collecting character, weapon, artifact,
and monster data from various sources including:
- Bilibili Game Wiki
- HoYoLAB Wiki
- Other community databases
"""

from .base_scraper import BaseScraper, ScraperConfig
from .character_scraper import CharacterScraper

__all__ = [
    "BaseScraper",
    "ScraperConfig",
    "CharacterScraper",
]
