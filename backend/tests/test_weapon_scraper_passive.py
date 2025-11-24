"""
Unit tests for weapon scraper passive skill extraction
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from src.scrapers.weapon_scraper import WeaponScraper


class TestWeaponScraperPassive:
    """Test weapon scraper passive skill extraction"""

    def test_parse_refinement_data_single_stat(self):
        """Test parsing refinement data with single stat"""
        scraper = WeaponScraper()

        description = "造成的伤害提高20%/24%/28%/32%/36%。"
        result = scraper._parse_refinement_data(description)

        assert 'refinement_levels' in result
        assert len(result['refinement_levels']) == 1

        level = result['refinement_levels'][0]
        assert level['rank_1'] == '20%'
        assert level['rank_2'] == '24%'
        assert level['rank_3'] == '28%'
        assert level['rank_4'] == '32%'
        assert level['rank_5'] == '36%'

    def test_parse_refinement_data_multiple_stats(self):
        """Test parsing refinement data with multiple stats"""
        scraper = WeaponScraper()

        description = "攻击力提高20%/25%/30%/35%/40%；恢复等同于攻击力的100%/115%/130%/145%/160%生命值。"
        result = scraper._parse_refinement_data(description)

        assert 'refinement_levels' in result
        assert len(result['refinement_levels']) == 2

        # First stat
        level1 = result['refinement_levels'][0]
        assert level1['rank_1'] == '20%'
        assert level1['rank_5'] == '40%'
        assert level1.get('stat_name') == 'atk'

        # Second stat
        level2 = result['refinement_levels'][1]
        assert level2['rank_1'] == '100%'
        assert level2['rank_5'] == '160%'
        assert level2.get('stat_name') == 'atk'

    def test_parse_refinement_data_with_duration(self):
        """Test parsing refinement data with duration (seconds)"""
        scraper = WeaponScraper()

        description = "该效果每30/26/22/19/16秒只能触发一次。"
        result = scraper._parse_refinement_data(description)

        assert 'refinement_levels' in result
        assert len(result['refinement_levels']) == 1

        level = result['refinement_levels'][0]
        assert level['rank_1'] == '30'
        assert level['rank_5'] == '16'
        assert level.get('stat_name') == 'cooldown'

    def test_parse_refinement_data_decimal_values(self):
        """Test parsing refinement data with decimal values"""
        scraper = WeaponScraper()

        description = "获得攻击力加成0.8%/1%/1.2%/1.4%/1.6%。"
        result = scraper._parse_refinement_data(description)

        assert 'refinement_levels' in result
        assert len(result['refinement_levels']) == 1

        level = result['refinement_levels'][0]
        assert level['rank_1'] == '0.8%'
        assert level['rank_2'] == '1%'
        assert level['rank_5'] == '1.6%'
        assert level.get('stat_name') == 'atk'

    def test_guess_stat_name_attack(self):
        """Test guessing stat name for attack"""
        scraper = WeaponScraper()

        context = "攻击力提高"
        stat_name = scraper._guess_stat_name(context, "20%")
        assert stat_name == "atk"

    def test_guess_stat_name_hp(self):
        """Test guessing stat name for HP"""
        scraper = WeaponScraper()

        context = "生命值提升"
        stat_name = scraper._guess_stat_name(context, "20%")
        assert stat_name == "hp"

    def test_guess_stat_name_crit_rate(self):
        """Test guessing stat name for crit rate"""
        scraper = WeaponScraper()

        context = "暴击率提高"
        stat_name = scraper._guess_stat_name(context, "8%")
        assert stat_name == "crit_rate"

    def test_guess_stat_name_crit_dmg(self):
        """Test guessing stat name for crit damage"""
        scraper = WeaponScraper()

        context = "暴击伤害提高"
        stat_name = scraper._guess_stat_name(context, "16%")
        assert stat_name == "crit_dmg"

    def test_guess_stat_name_duration(self):
        """Test guessing stat name for duration (seconds)"""
        scraper = WeaponScraper()

        context = "该效果"
        stat_name = scraper._guess_stat_name(context, "30秒")
        assert stat_name == "duration"

    def test_guess_stat_name_default_percentage(self):
        """Test guessing stat name defaults to percentage for unknown context"""
        scraper = WeaponScraper()

        context = "某种未知效果"
        stat_name = scraper._guess_stat_name(context, "50%")
        assert stat_name == "percentage"

    def test_parse_refinement_data_no_refinement(self):
        """Test parsing text without refinement data"""
        scraper = WeaponScraper()

        description = "这是一个简单的描述，没有精炼数值。"
        result = scraper._parse_refinement_data(description)

        assert result == {}

    def test_parse_refinement_data_incomplete_values(self):
        """Test parsing refinement data with incomplete values (not 5 ranks)"""
        scraper = WeaponScraper()

        # Only 3 values instead of 5
        description = "效果提高20%/30%/40%。"
        result = scraper._parse_refinement_data(description)

        # Should not match because it's not 5 refinement ranks
        assert result == {}


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
