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
from ..models.weapon import Weapon
from ..models.artifact import Artifact
from ..models.artifact_set import ArtifactSet

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
            "atk": scraped_stats.get("atk"),  # Fixed: scraper uses 'atk' not 'attack'
            "def": scraped_stats.get("def"),  # Fixed: scraper uses 'def' not 'defense'
        }

        # Prepare ascension_stats from scraped data
        ascension_stats = char_data.get("ascension_stats", {})
        if not ascension_stats:
            ascension_stats = None

        character = Character(
            name=char_data["name"],
            name_en=char_data.get("name_en"),  # Added: include English name
            rarity=char_data.get("rarity"),
            element=char_data.get("element"),
            weapon_type=char_data.get("weapon_type"),
            region=char_data.get("region"),
            description=char_data.get("description"),
            base_stats=base_stats,
            ascension_stats=ascension_stats if ascension_stats else None,
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
        if new_data.get("name_en"):
            existing.name_en = new_data["name_en"]
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
                "atk": scraped_stats.get("atk"),  # Fixed: scraper uses 'atk' not 'attack'
                "def": scraped_stats.get("def"),  # Fixed: scraper uses 'def' not 'defense'
            }

        # Update ascension stats
        ascension_stats = new_data.get("ascension_stats", {})
        if ascension_stats:
            existing.ascension_stats = ascension_stats

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

    # ===== Weapon Storage Methods =====

    async def store_weapons(self, weapons: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Store weapon data in database with incremental update.

        Args:
            weapons: List of weapon dictionaries from scraper

        Returns:
            Statistics dict with counts
        """
        logger.info(f"Storing {len(weapons)} weapons...")
        self.reset_stats()

        for weapon_data in weapons:
            try:
                await self._store_single_weapon(weapon_data)
            except Exception as e:
                self._stats["errors"] += 1
                logger.error(
                    f"Error storing weapon {weapon_data.get('name')}: {e}",
                    exc_info=True
                )

        await self.db.commit()

        logger.info(
            f"Weapon storage complete. "
            f"Created: {self._stats['created']}, "
            f"Updated: {self._stats['updated']}, "
            f"Skipped: {self._stats['skipped']}, "
            f"Errors: {self._stats['errors']}"
        )

        return self._stats.copy()

    async def _store_single_weapon(self, weapon_data: Dict[str, Any]):
        """Store or update a single weapon."""
        name = weapon_data.get("name")
        if not name:
            logger.warning("Weapon data missing name, skipping")
            self._stats["skipped"] += 1
            return

        stmt = select(Weapon).where(Weapon.name == name)
        result = await self.db.execute(stmt)
        existing_weapon = result.scalar_one_or_none()

        if existing_weapon:
            if self._weapon_has_changes(existing_weapon, weapon_data):
                self._update_weapon(existing_weapon, weapon_data)
                self._stats["updated"] += 1
                logger.info(f"Updated weapon: {name}")
            else:
                self._stats["skipped"] += 1
                logger.debug(f"No changes for weapon: {name}")
        else:
            new_weapon = self._create_weapon(weapon_data)
            self.db.add(new_weapon)
            self._stats["created"] += 1
            logger.info(f"Created new weapon: {name}")

    def _weapon_has_changes(self, existing: Weapon, new_data: Dict[str, Any]) -> bool:
        """Check if weapon data has changes."""
        fields_to_compare = ["rarity", "weapon_type", "base_attack", "description"]
        for field in fields_to_compare:
            new_value = new_data.get(field)
            existing_value = getattr(existing, field, None)
            if new_value is not None and new_value != existing_value:
                return True
        return False

    def _create_weapon(self, weapon_data: Dict[str, Any]) -> Weapon:
        """Create a new Weapon model instance."""
        weapon = Weapon(
            name=weapon_data["name"],
            name_en=weapon_data.get("name_en"),
            weapon_type=weapon_data.get("weapon_type"),
            rarity=weapon_data.get("rarity"),
            base_attack=weapon_data.get("base_attack"),
            secondary_stat=weapon_data.get("secondary_stat"),
            secondary_stat_value=weapon_data.get("secondary_stat_value"),
            description=weapon_data.get("description"),
            passive_name=weapon_data.get("passive_name"),
            passive_description=weapon_data.get("passive_description"),
            source=weapon_data.get("source"),
        )
        return weapon

    def _update_weapon(self, existing: Weapon, new_data: Dict[str, Any]):
        """Update existing weapon with new data."""
        if new_data.get("name_en"):
            existing.name_en = new_data["name_en"]
        if new_data.get("weapon_type"):
            existing.weapon_type = new_data["weapon_type"]
        if new_data.get("rarity"):
            existing.rarity = new_data["rarity"]
        if new_data.get("base_attack"):
            existing.base_attack = new_data["base_attack"]
        if new_data.get("secondary_stat"):
            existing.secondary_stat = new_data["secondary_stat"]
        if new_data.get("secondary_stat_value"):
            existing.secondary_stat_value = new_data["secondary_stat_value"]
        if new_data.get("description"):
            existing.description = new_data["description"]
        if new_data.get("passive_name"):
            existing.passive_name = new_data["passive_name"]
        if new_data.get("passive_description"):
            existing.passive_description = new_data["passive_description"]
        if new_data.get("source"):
            existing.source = new_data["source"]

        existing.updated_at = datetime.utcnow()

    # ===== Artifact Set Storage Methods (New) =====

    async def store_artifacts(self, artifacts: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Store artifact set and piece data in database with incremental update.

        Args:
            artifacts: List of artifact set dictionaries from scraper
                Each dict contains:
                - Set info: name, tags, max_rarity, two_piece_bonus, four_piece_bonus
                - Pieces: list of 5 pieces with slot, slot_cn, piece_name, lore

        Returns:
            Statistics dict with counts
        """
        logger.info(f"Storing {len(artifacts)} artifact sets...")
        self.reset_stats()

        for artifact_data in artifacts:
            try:
                await self._store_single_artifact_set(artifact_data)
            except Exception as e:
                self._stats["errors"] += 1
                logger.error(
                    f"Error storing artifact {artifact_data.get('name')}: {e}",
                    exc_info=True
                )

        await self.db.commit()

        logger.info(
            f"Artifact storage complete. "
            f"Created: {self._stats['created']}, "
            f"Updated: {self._stats['updated']}, "
            f"Skipped: {self._stats['skipped']}, "
            f"Errors: {self._stats['errors']}"
        )

        return self._stats.copy()

    async def _store_single_artifact_set(self, artifact_data: Dict[str, Any]):
        """Store or update a single artifact set with its pieces."""
        set_name = artifact_data.get("name")
        if not set_name:
            logger.warning("Artifact data missing name, skipping")
            self._stats["skipped"] += 1
            return

        # Check if artifact set already exists
        stmt = select(ArtifactSet).where(ArtifactSet.set_name == set_name)
        result = await self.db.execute(stmt)
        existing_set = result.scalar_one_or_none()

        if existing_set:
            # Update existing set
            if self._artifact_set_has_changes(existing_set, artifact_data):
                self._update_artifact_set(existing_set, artifact_data)
                self._stats["updated"] += 1
                logger.info(f"Updated artifact set: {set_name}")
            else:
                self._stats["skipped"] += 1
                logger.debug(f"No changes for artifact set: {set_name}")
        else:
            # Create new set
            new_set = self._create_artifact_set(artifact_data)
            self.db.add(new_set)

            pieces_count = len(artifact_data.get("pieces", []))
            self._stats["created"] += 1
            logger.info(f"Created new artifact set: {set_name} with {pieces_count} pieces")

    def _artifact_set_has_changes(self, existing: ArtifactSet, new_data: Dict[str, Any]) -> bool:
        """Check if artifact set data has changes."""
        # Check rarity
        if new_data.get("max_rarity") and new_data["max_rarity"] != existing.max_rarity:
            return True

        # Check tags
        new_tags = new_data.get("tags", [])
        existing_tags = existing.tags or []
        if set(new_tags) != set(existing_tags):
            return True

        # Check description
        if new_data.get("description") and new_data["description"] != existing.description:
            return True

        # Check set effects
        if new_data.get("two_piece_bonus") and new_data["two_piece_bonus"] != existing.two_piece_bonus:
            return True
        if new_data.get("four_piece_bonus") and new_data["four_piece_bonus"] != existing.four_piece_bonus:
            return True

        # Check if pieces data has changed
        new_pieces = new_data.get("pieces", [])
        if len(new_pieces) != len(existing.pieces):
            return True

        return False

    def _create_artifact_set(self, artifact_data: Dict[str, Any]) -> ArtifactSet:
        """Create a new ArtifactSet model instance."""
        artifact_set = ArtifactSet(
            set_name=artifact_data["name"],
            set_name_en=artifact_data.get("name_en"),
            tags=artifact_data.get("tags", []),
            max_rarity=artifact_data.get("max_rarity", 5),
            two_piece_bonus=artifact_data.get("two_piece_bonus"),
            four_piece_bonus=artifact_data.get("four_piece_bonus"),
            description=artifact_data.get("description"),
            source=artifact_data.get("source"),
            domain_name=artifact_data.get("domain_name"),
            pieces=artifact_data.get("pieces", []),  # 直接存储为JSONB
        )
        return artifact_set

    def _update_artifact_set(self, existing: ArtifactSet, new_data: Dict[str, Any]):
        """Update existing artifact set with new data."""
        if new_data.get("name_en"):
            existing.set_name_en = new_data["name_en"]

        if new_data.get("tags"):
            existing.tags = new_data["tags"]

        if new_data.get("max_rarity"):
            existing.max_rarity = new_data["max_rarity"]

        if new_data.get("two_piece_bonus"):
            existing.two_piece_bonus = new_data["two_piece_bonus"]

        if new_data.get("four_piece_bonus"):
            existing.four_piece_bonus = new_data["four_piece_bonus"]

        if new_data.get("description"):
            existing.description = new_data["description"]

        if new_data.get("source"):
            existing.source = new_data["source"]

        if new_data.get("domain_name"):
            existing.domain_name = new_data["domain_name"]

        # Update pieces (直接更新JSONB字段)
        if new_data.get("pieces"):
            existing.pieces = new_data["pieces"]

        existing.updated_at = datetime.utcnow()
