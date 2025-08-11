import pytest
from unittest.mock import patch, mock_open
import json
import os
from app.services.normalization import normalize_ingredient, load_synonyms, SYNONYMS


class TestLoadSynonyms:
    """Test suite for load_synonyms function."""

    @patch('app.services.normalization.os.path.join')
    @patch('builtins.open', new_callable=mock_open)
    @patch('app.services.normalization.json.load')
    def test_load_synonyms_success(self, mock_json_load, mock_file_open, mock_path_join):
        """Test successful loading of synonyms from JSON file."""
        # Mock the file system paths
        mock_path_join.return_value = "/path/to/ingredients.json"
        
        # Mock the JSON content
        mock_synonyms_data = {
            "synonyms": {
                "pomidor": ["pomidory", "pomidora"],
                "cebula": ["cebule", "cebuli"]
            }
        }
        mock_json_load.return_value = mock_synonyms_data
        
        result = load_synonyms()
        
        assert result == mock_synonyms_data["synonyms"]
        mock_file_open.assert_called_once_with("/path/to/ingredients.json", 'r', encoding='utf-8')
        mock_json_load.assert_called_once()

    @patch('app.services.normalization.os.path.join')
    @patch('builtins.open', side_effect=FileNotFoundError("File not found"))
    def test_load_synonyms_file_not_found(self, mock_file_open, mock_path_join):
        """Test handling of missing ingredients.json file."""
        mock_path_join.return_value = "/path/to/ingredients.json"
        
        with pytest.raises(FileNotFoundError):
            load_synonyms()

    @patch('app.services.normalization.os.path.join')
    @patch('builtins.open', new_callable=mock_open, read_data='{"invalid": "json"')
    @patch('app.services.normalization.json.load', side_effect=json.JSONDecodeError("Invalid JSON", "", 0))
    def test_load_synonyms_invalid_json(self, mock_json_load, mock_file_open, mock_path_join):
        """Test handling of invalid JSON in ingredients file."""
        mock_path_join.return_value = "/path/to/ingredients.json"
        
        with pytest.raises(json.JSONDecodeError):
            load_synonyms()


class TestNormalizeIngredient:
    """Test suite for normalize_ingredient function."""

    def test_normalize_ingredient_synonyms_exact_match(self):
        """Test normalization using exact synonym matching."""
        # Test with mocked SYNONYMS to avoid dependency on actual file
        with patch('app.services.normalization.SYNONYMS', {
            "pomidor": ["pomidory", "pomidora", "pomidorów"],
            "cebula": ["cebule", "cebuli", "cebulę"],
            "czosnek": ["ząbek czosnku", "ząbki czosnku"]
        }):
            assert normalize_ingredient("pomidory") == "pomidor"
            assert normalize_ingredient("pomidora") == "pomidor"
            assert normalize_ingredient("pomidorów") == "pomidor"
            assert normalize_ingredient("cebule") == "cebula"
            assert normalize_ingredient("cebuli") == "cebula"
            assert normalize_ingredient("cebulę") == "cebula"

    def test_normalize_ingredient_synonyms_base_word(self):
        """Test normalization when input is already the base word."""
        with patch('app.services.normalization.SYNONYMS', {
            "pomidor": ["pomidory", "pomidora"],
            "cebula": ["cebule", "cebuli"]
        }):
            assert normalize_ingredient("pomidor") == "pomidor"
            assert normalize_ingredient("cebula") == "cebula"

    def test_normalize_ingredient_synonyms_case_insensitive(self):
        """Test normalization is case insensitive."""
        with patch('app.services.normalization.SYNONYMS', {
            "pomidor": ["pomidory", "pomidora"],
            "cebula": ["cebule", "cebuli"]
        }):
            assert normalize_ingredient("Pomidory") == "pomidor"
            assert normalize_ingredient("POMIDORA") == "pomidor"
            assert normalize_ingredient("CebuLe") == "cebula"
            assert normalize_ingredient("CEBULI") == "cebula"

    def test_normalize_ingredient_multi_word_synonyms(self):
        """Test normalization with multi-word synonyms."""
        with patch('app.services.normalization.SYNONYMS', {
            "czosnek": ["ząbek czosnku", "ząbki czosnku"],
            "masło": ["masło orzechowe", "masło extra"]
        }):
            assert normalize_ingredient("ząbek czosnku") == "czosnek"
            assert normalize_ingredient("ząbki czosnku") == "czosnek"
            assert normalize_ingredient("Ząbek Czosnku") == "czosnek"

    def test_normalize_ingredient_whitespace_handling(self):
        """Test that whitespace is properly handled."""
        with patch('app.services.normalization.SYNONYMS', {
            "pomidor": ["pomidory", "pomidora"]
        }):
            assert normalize_ingredient("  pomidor  ") == "pomidor"
            assert normalize_ingredient("\t pomidory \n") == "pomidor"
            assert normalize_ingredient("   pomidora   ") == "pomidor"

    def test_normalize_ingredient_polish_singularization_y_ending(self):
        """Test Polish singularization rules for words ending with 'y'."""
        with patch('app.services.normalization.SYNONYMS', {}):
            # Words ending with 'y' should have 'y' removed if length > 2
            assert normalize_ingredient("ziemniaky") == "ziemniak"
            assert normalize_ingredient("owocy") == "owoc"
            assert normalize_ingredient("warzywy") == "warzy"
            
            # Short words should not be modified
            assert normalize_ingredient("ty") == "ty"
            assert normalize_ingredient("my") == "my"

    def test_normalize_ingredient_polish_singularization_i_ending(self):
        """Test Polish singularization rules for words ending with 'i'."""
        with patch('app.services.normalization.SYNONYMS', {}):
            # Words ending with 'i' should have 'i' removed if length > 2
            assert normalize_ingredient("spaghetti") == "spaghett"
            assert normalize_ingredient("pierogi") == "pierog"
            assert normalize_ingredient("kiwi") == "kiw"  # Still applies even if semantically wrong
            
            # Very short words should not be modified
            assert normalize_ingredient("wi") == "wi"
            assert normalize_ingredient("i") == "i"

    def test_normalize_ingredient_polish_singularization_ow_ending(self):
        """Test Polish singularization rules for words ending with 'ów'."""
        with patch('app.services.normalization.SYNONYMS', {}):
            # Words ending with 'ów' should have 'ów' removed if length > 3
            assert normalize_ingredient("jogurtów") == "jogurt"
            assert normalize_ingredient("serków") == "serk"
            assert normalize_ingredient("chlebów") == "chleb"
            
            # Short words should not be modified
            assert normalize_ingredient("ów") == "ów"
            assert normalize_ingredient("tów") == "tów"

    def test_normalize_ingredient_complex_polish_words(self):
        """Test normalization with complex Polish ingredient names."""
        with patch('app.services.normalization.SYNONYMS', {}):
            # Test combinations of rules
            assert normalize_ingredient("kabaczki") == "kabaczk"  # 'i' ending
            assert normalize_ingredient("cukinię") == "cukinie"   # 'ę' not handled, no rule
            assert normalize_ingredient("bakłażany") == "bakłażan"  # 'y' ending

    def test_normalize_ingredient_no_rule_applies(self):
        """Test normalization when no rules apply."""
        with patch('app.services.normalization.SYNONYMS', {}):
            # Words that don't match any synonym or singularization rule
            assert normalize_ingredient("nieznany_składnik") == "nieznany_składnik"
            assert normalize_ingredient("exotic_ingredient") == "exotic_ingredient"
            assert normalize_ingredient("składnik123") == "składnik123"
            assert normalize_ingredient("mix-ingredient") == "mix-ingredient"

    def test_normalize_ingredient_empty_and_special_inputs(self):
        """Test normalization with empty and special inputs."""
        with patch('app.services.normalization.SYNONYMS', {}):
            assert normalize_ingredient("") == ""
            assert normalize_ingredient(" ") == ""  # Just whitespace
            assert normalize_ingredient("   ") == ""  # Multiple whitespaces
            assert normalize_ingredient("\t\n") == ""  # Tab and newline

    def test_normalize_ingredient_numbers_and_special_chars(self):
        """Test normalization with numbers and special characters."""
        with patch('app.services.normalization.SYNONYMS', {}):
            assert normalize_ingredient("składnik1") == "składnik1"
            assert normalize_ingredient("składnik-2") == "składnik-2"
            assert normalize_ingredient("składnik_3") == "składnik_3"
            assert normalize_ingredient("100g mąki") == "100g mąki"

    def test_normalize_ingredient_priority_synonyms_over_rules(self):
        """Test that synonym matching has priority over singularization rules."""
        with patch('app.services.normalization.SYNONYMS', {
            "ser": ["sery", "sera", "serów"]  # 'sery' ends with 'y' but should use synonym
        }):
            # Should use synonym matching, not singularization rule
            assert normalize_ingredient("sery") == "ser"
            assert normalize_ingredient("sera") == "ser"
            assert normalize_ingredient("serów") == "ser"

    def test_normalize_ingredient_multiple_singularization_attempts(self):
        """Test that only one singularization rule is applied."""
        with patch('app.services.normalization.SYNONYMS', {}):
            # Word ends with 'ów' - should only apply ów rule, not subsequent rules
            assert normalize_ingredient("testów") == "test"
            
            # If a word theoretically could match multiple rules, only first applicable is used
            word_ending_y = "testy"  # ends with 'y'
            assert normalize_ingredient(word_ending_y) == "test"

    def test_normalize_ingredient_unicode_characters(self):
        """Test normalization with Polish Unicode characters."""
        with patch('app.services.normalization.SYNONYMS', {
            "żurawina": ["żurawiny", "żurawin"]
        }):
            assert normalize_ingredient("żurawiny") == "żurawina"
            assert normalize_ingredient("śledzio") == "śledzio"  # No rule applies

    def test_normalize_ingredient_edge_case_lengths(self):
        """Test edge cases around minimum lengths for singularization rules."""
        with patch('app.services.normalization.SYNONYMS', {}):
            # Test boundary conditions for length checks
            assert normalize_ingredient("ay") == "ay"      # length 2, no change for 'y' rule
            assert normalize_ingredient("aay") == "aa"     # length 3, 'y' rule applies
            assert normalize_ingredient("ai") == "ai"      # length 2, no change for 'i' rule
            assert normalize_ingredient("aai") == "aa"     # length 3, 'i' rule applies
            assert normalize_ingredient("aów") == "aów"    # length 3, no change for 'ów' rule
            assert normalize_ingredient("aaów") == "aa"    # length 4, 'ów' rule applies


class TestNormalizationIntegration:
    """Integration tests using actual SYNONYMS data structure."""

    def test_normalize_with_real_synonyms_structure(self):
        """Test normalization using a realistic synonyms structure."""
        # This tests the actual behavior without mocking, using realistic data
        realistic_synonyms = {
            "pomidor": ["pomidory", "pomidora", "pomidorów"],
            "cebula": ["cebule", "cebuli", "cebulę"],
            "czosnek": ["ząbek czosnku", "ząbki czosnku"],
            "mąka": ["mąki", "mąkę"],
            "jajko": ["jajka", "jaj"],
            "mleko": ["mleka"],
            "ser": ["sera", "serów"],
            "ziemniak": ["ziemniaki", "ziemniaków", "ziemniaka"],
        }
        
        with patch('app.services.normalization.SYNONYMS', realistic_synonyms):
            # Test various synonym mappings
            assert normalize_ingredient("pomidory") == "pomidor"
            assert normalize_ingredient("CEBULE") == "cebula"
            assert normalize_ingredient("  ząbek czosnku  ") == "czosnek"
            assert normalize_ingredient("ziemniaki") == "ziemniak"
            
            # Test base words
            assert normalize_ingredient("pomidor") == "pomidor"
            assert normalize_ingredient("cebula") == "cebula"
            
            # Test unknown ingredients with singularization
            assert normalize_ingredient("marchewki") == "marchewk"  # 'i' rule
            assert normalize_ingredient("kapusty") == "kapust"      # 'y' rule
            assert normalize_ingredient("ogórków") == "ogórk"       # 'ów' rule

    def test_normalize_complex_ingredient_phrases(self):
        """Test normalization with complex, multi-word ingredient phrases."""
        realistic_synonyms = {
            "czosnek": ["ząbek czosnku", "ząbki czosnku", "główka czosnku"],
            "masło": ["masło extra", "masło orzechowe"],
            "ser": ["ser żółty", "ser biały"]
        }
        
        with patch('app.services.normalization.SYNONYMS', realistic_synonyms):
            assert normalize_ingredient("ząbek czosnku") == "czosnek"
            assert normalize_ingredient("GŁÓWKA CZOSNKU") == "czosnek"
            assert normalize_ingredient("  masło extra  ") == "masło"

    def test_normalize_performance_considerations(self):
        """Test normalization with large synonym dictionary (simulating real-world usage)."""
        # Create a larger synonym dictionary to test performance characteristics
        large_synonyms = {}
        for i in range(100):
            base = f"ingredient_{i}"
            synonyms = [f"{base}_syn_{j}" for j in range(5)]
            large_synonyms[base] = synonyms
        
        with patch('app.services.normalization.SYNONYMS', large_synonyms):
            # Test that lookup still works efficiently
            assert normalize_ingredient("ingredient_0_syn_0") == "ingredient_0"
            assert normalize_ingredient("ingredient_50_syn_2") == "ingredient_50"
            assert normalize_ingredient("unknown_ingredient") == "unknown_ingredient"


# Test fixtures and utilities
@pytest.fixture
def sample_synonyms():
    """Fixture providing sample synonym data for testing."""
    return {
        "pomidor": ["pomidory", "pomidora", "pomidorów"],
        "cebula": ["cebule", "cebuli", "cebulę"],
        "czosnek": ["ząbek czosnku", "ząbki czosnku"],
        "ser": ["sera", "serów", "ser żółty"]
    }


@pytest.fixture
def mock_synonyms_file_content():
    """Fixture providing mock file content for ingredients.json."""
    return {
        "synonyms": {
            "pomidor": ["pomidory", "pomidora"],
            "cebula": ["cebule", "cebuli"],
            "masło": ["masła"]
        }
    }


class TestNormalizationRegressions:
    """Regression tests for specific normalization issues."""

    def test_regression_empty_synonym_list(self):
        """Test handling of ingredients with empty synonym lists."""
        with patch('app.services.normalization.SYNONYMS', {
            "ingredient": []  # Empty synonym list
        }):
            assert normalize_ingredient("ingredient") == "ingredient"
            assert normalize_ingredient("unknown") == "unknown"

    def test_regression_none_handling(self):
        """Test that None inputs are handled gracefully."""
        with patch('app.services.normalization.SYNONYMS', {}):
            # This might cause AttributeError if not handled properly
            with pytest.raises(AttributeError):
                normalize_ingredient(None)

    def test_regression_numeric_strings(self):
        """Test normalization with numeric strings."""
        with patch('app.services.normalization.SYNONYMS', {}):
            assert normalize_ingredient("123") == "123"
            assert normalize_ingredient("3.14") == "3.14"

    def test_regression_very_long_strings(self):
        """Test normalization with very long ingredient names."""
        with patch('app.services.normalization.SYNONYMS', {}):
            long_ingredient = "bardzo_długa_nazwa_składnika_która_może_powodować_problemy" * 10
            result = normalize_ingredient(long_ingredient)
            # Should handle without errors and apply appropriate rules
            assert isinstance(result, str)
            assert len(result) > 0

    def test_regression_special_unicode_combinations(self):
        """Test with special Unicode character combinations."""
        with patch('app.services.normalization.SYNONYMS', {}):
            assert normalize_ingredient("żółć") == "żółć"
            assert normalize_ingredient("ńą") == "ńą"
            assert normalize_ingredient("ęćż") == "ęćż"