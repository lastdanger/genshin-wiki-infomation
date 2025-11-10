"""
Data storage service for scraped data.

Handles:
- Saving scraped data to database
- Incremental updates (update only changed data)
- Duplicate detection and merging
- Data validation before storage
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.character import Character

logger = logging.getLogger(__name__)


class DataStorageService:
    """Service for storing scraped data in the database."""

    def __init__(self, db_session: AsyncSession):
        """
        Initialize data storage service.

        Args:
            db_session: Database session for operations
        """
        self.db = db_session
        self._stats = {
            "created": 0,
            "updated": 0,
            "skipped": 0,
            "errors": 0,
        }

    async def store_characters(
        self, characters: List[Dict[str, Any]]
    ) -> Dict[str, int]:
        """
        Store character data in database with incremental update.

        Args:
            characters: List of character dictionaries from scraper

        Returns:
            Statistics dict with counts of created, updated, skipped, errors
        """
        logger.info(f"Storing {len(characters)} characters...")

        for char_data in characters:
            try:
                await self._store_single_character(char_data)
            except Exception as e:
                self._stats["errors"] += 1
                logger.error(
                    f"Error storing character {char_data.get('name')}: {e}",
                    exc_info=True
                )

        await self.db.commit()

        logger.info(
            f"Character storage complete. "
            f"Created: {self._stats['created']}, "
            f"Updated: {self._stats['updated']}, "
            f"Skipped: {self._stats['skipped']}, "
            f"Errors: {self._stats['errors']}"
        )

        return self._stats.copy()

    async def _store_single_character(self, char_data: Dict[str, Any]):
        """
        Store or update a single character.

        Args:
            char_data: Character data dictionary
        """
        name = char_data.get("name")
        if not name:
            logger.warning("Character data missing name, skipping")
            self._stats["skipped"] += 1
            return

        # Check if character already exists
        stmt = select(Character).where(Character.name == name)
        result = await self.db.execute(stmt)
        existing_char = result.scalar_one_or_none()

        if existing_char:
            # Update if data has changed
            if self._character_has_changes(existing_char, char_data):
                self._update_character(existing_char, char_data)
                self._stats["updated"] += 1
                logger.info(f"Updated character: {name}")
            else:
                self._stats["skipped"] += 1
                logger.debug(f"No changes for character: {name}")
        else:
            # Create new character
            new_char = self._create_character(char_data)
            self.db.add(new_char)
            self._stats["created"] += 1
            logger.info(f"Created new character: {name}")

    def _character_has_changes(
        self, existing: Character, new_data: Dict[str, Any]
    ) -> bool:
        """
        Check if character data has changes compared to existing record.

        Args:
            existing: Existing character from database
            new_data: New character data from scraper

        Returns:
            True if there are changes, False otherwise
        """
        # Compare key fields
        fields_to_compare = [
            "rarity",
            "element",
            "weapon_type",
            "region",
            "description",
        ]

        for field in fields_to_compare:
            new_value = new_data.get(field)
            existing_value = getattr(existing, field, None)

            # Handle None values
            if new_value is not None and new_value != existing_value:
                return True

        # Compare stats (if present)
        base_stats = new_data.get("base_stats", {})
        existing_stats = existing.base_stats or {}
        if base_stats:
            if (
                base_stats.get("hp") and base_stats["hp"] != existing_stats.get("hp") or
                base_stats.get("atk") and base_stats["atk"] != existing_stats.get("atk") or
                base_stats.get("def") and base_stats["def"] != existing_stats.get("def")
            ):
                return True

        return False

    def _create_character(self, char_data: Dict[str, Any]) -> Character:
        """
        Create a new Character model instance from scraped data.

        Args:
            char_data: Character data dictionary

        Returns:
            Character model instance
        """
        # Prepare base_stats in the format expected by the model
        scraped_stats = char_data.get("base_stats", {})
        base_stats = {
            "hp": scraped_stats.get("hp"),
            "atk": scraped_stats.get("attack"),
            "def": scraped_stats.get("defense"),
        }

        # Prepare ascension_stats if crit stats are present
        ascension_stats = None
        if scraped_stats.get("crit_rate") or scraped_stats.get("crit_dmg"):
            ascension_stats = {
                "crit_rate": scraped_stats.get("crit_rate"),
                "crit_dmg": scraped_stats.get("crit_dmg"),
            }

        character = Character(
            name=char_data["name"],
            rarity=char_data.get("rarity"),
            element=char_data.get("element"),
            weapon_type=char_data.get("weapon_type"),
            region=char_data.get("region"),
            description=char_data.get("description"),
            base_stats=base_stats,
            ascension_stats=ascension_stats,
        )

        return character

    def _update_character(self, existing: Character, new_data: Dict[str, Any]):
        """
        Update existing character with new data.

        Args:
            existing: Existing character model
            new_data: New character data from scraper
        """
        # Update basic fields
        if new_data.get("rarity"):
            existing.rarity = new_data["rarity"]
        if new_data.get("element"):
            existing.element = new_data["element"]
        if new_data.get("weapon_type"):
            existing.weapon_type = new_data["weapon_type"]
        if new_data.get("region"):
            existing.region = new_data["region"]
        if new_data.get("description"):
            existing.description = new_data["description"]

        # Update stats
        scraped_stats = new_data.get("base_stats", {})
        if scraped_stats:
            existing.base_stats = {
                "hp": scraped_stats.get("hp"),
                "atk": scraped_stats.get("attack"),
                "def": scraped_stats.get("defense"),
            }

            # Update ascension stats
            if scraped_stats.get("crit_rate") or scraped_stats.get("crit_dmg"):
                existing.ascension_stats = {
                    "crit_rate": scraped_stats.get("crit_rate"),
                    "crit_dmg": scraped_stats.get("crit_dmg"),
                }

        existing.updated_at = datetime.utcnow()

    def get_stats(self) -> Dict[str, int]:
        """Get storage statistics."""
        return self._stats.copy()

    def reset_stats(self):
        """Reset statistics counters."""
        self._stats = {
            "created": 0,
            "updated": 0,
            "skipped": 0,
            "errors": 0,
        }
