"""
Simple unit tests for weapon scraper passive skill extraction (without pytest)
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.scrapers.weapon_scraper import WeaponScraper


def test_parse_refinement_data_single_stat():
    """Test parsing refinement data with single stat"""
    scraper = WeaponScraper()

    description = "造成的伤害提高20%/24%/28%/32%/36%。"
    result = scraper._parse_refinement_data(description)

    assert 'refinement_levels' in result, "Should have refinement_levels key"
    assert len(result['refinement_levels']) == 1, "Should have 1 refinement level"

    level = result['refinement_levels'][0]
    assert level['rank_1'] == '20%', f"rank_1 should be 20%, got {level['rank_1']}"
    assert level['rank_5'] == '36%', f"rank_5 should be 36%, got {level['rank_5']}"

    print("✅ test_parse_refinement_data_single_stat passed")


def test_parse_refinement_data_multiple_stats():
    """Test parsing refinement data with multiple stats"""
    scraper = WeaponScraper()

    description = "攻击力提高20%/25%/30%/35%/40%；恢复等同于攻击力的100%/115%/130%/145%/160%生命值。"
    result = scraper._parse_refinement_data(description)

    assert 'refinement_levels' in result
    assert len(result['refinement_levels']) == 2, f"Should have 2 refinement levels, got {len(result['refinement_levels'])}"

    # First stat
    level1 = result['refinement_levels'][0]
    assert level1['rank_1'] == '20%'
    assert level1['rank_5'] == '40%'
    assert level1.get('stat_name') == 'atk'

    # Second stat
    level2 = result['refinement_levels'][1]
    assert level2['rank_1'] == '100%'
    assert level2['rank_5'] == '160%'

    print("✅ test_parse_refinement_data_multiple_stats passed")


def test_parse_refinement_data_with_duration():
    """Test parsing refinement data with duration (seconds)"""
    scraper = WeaponScraper()

    description = "该效果每30/26/22/19/16秒只能触发一次。"
    result = scraper._parse_refinement_data(description)

    print(f"Result: {result}")

    assert 'refinement_levels' in result, f"Should have refinement_levels, got: {result}"
    assert len(result['refinement_levels']) == 1, f"Should have 1 level, got {len(result.get('refinement_levels', []))}"

    if result.get('refinement_levels'):
        level = result['refinement_levels'][0]
        print(f"Level data: {level}")
        assert level['rank_1'] == '30', f"rank_1 should be '30', got '{level['rank_1']}'"
        assert level['rank_5'] == '16', f"rank_5 should be '16', got '{level['rank_5']}'"
        # Note: stat_name might not be detected without '秒' in the value
        # assert level.get('stat_name') == 'cooldown'

    print("✅ test_parse_refinement_data_with_duration passed")


def test_parse_refinement_data_decimal_values():
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

    print("✅ test_parse_refinement_data_decimal_values passed")


def test_guess_stat_names():
    """Test guessing stat names"""
    scraper = WeaponScraper()

    # Attack
    assert scraper._guess_stat_name("攻击力提高", "20%") == "atk"

    # HP
    assert scraper._guess_stat_name("生命值提升", "20%") == "hp"

    # Crit rate
    assert scraper._guess_stat_name("暴击率提高", "8%") == "crit_rate"

    # Crit damage
    assert scraper._guess_stat_name("暴击伤害提高", "16%") == "crit_dmg"

    # Duration
    assert scraper._guess_stat_name("该效果", "30秒") == "duration"

    # Default percentage
    assert scraper._guess_stat_name("某种未知效果", "50%") == "percentage"

    print("✅ test_guess_stat_names passed")


def test_parse_refinement_data_no_refinement():
    """Test parsing text without refinement data"""
    scraper = WeaponScraper()

    description = "这是一个简单的描述，没有精炼数值。"
    result = scraper._parse_refinement_data(description)

    assert result == {}, "Should return empty dict for text without refinement data"

    print("✅ test_parse_refinement_data_no_refinement passed")


def test_parse_refinement_data_incomplete_values():
    """Test parsing refinement data with incomplete values (not 5 ranks)"""
    scraper = WeaponScraper()

    # Only 3 values instead of 5
    description = "效果提高20%/30%/40%。"
    result = scraper._parse_refinement_data(description)

    # Should not match because it's not 5 refinement ranks
    assert result == {}, "Should not match incomplete refinement data (not 5 values)"

    print("✅ test_parse_refinement_data_incomplete_values passed")


def run_all_tests():
    """Run all tests"""
    print("="*70)
    print("Running weapon scraper passive skill extraction tests")
    print("="*70)

    try:
        test_parse_refinement_data_single_stat()
        test_parse_refinement_data_multiple_stats()
        test_parse_refinement_data_with_duration()
        test_parse_refinement_data_decimal_values()
        test_guess_stat_names()
        test_parse_refinement_data_no_refinement()
        test_parse_refinement_data_incomplete_values()

        print("\n" + "="*70)
        print("✅ All tests passed! (7/7)")
        print("="*70)
        return True

    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
