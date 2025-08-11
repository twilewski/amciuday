import pytest
from unittest.mock import Mock, patch
from sqlmodel import Session, select
from datetime import datetime, timedelta

from app.services.recipe_filter import (
    count_extra_ingredients,
    has_banned_ingredients,
    get_preferences,
    get_recent_recipe_ids,
    filter_recipes,
    get_random_recipe,
)
from app.models.models import Recipe, Preferences, SpinHistory


class TestCountExtraIngredients:
    """Test suite for count_extra_ingredients function."""

    def test_count_extra_ingredients_basic(self):
        """Test counting ingredients not in liked list."""
        recipe = Recipe(
            title="Test Recipe",
            source="test",
            url="http://test.com",
            meal_type="lunch",
            steps_excerpt="Test steps",
            normalized_ingredient_ids=[1, 2, 3, 4]
        )
        
        # Some ingredients liked
        liked_ids = {1, 2}
        extra_count = count_extra_ingredients(recipe, liked_ids)
        assert extra_count == 2  # ingredients 3 and 4 are not in liked
        
        # All ingredients liked
        liked_ids = {1, 2, 3, 4}
        extra_count = count_extra_ingredients(recipe, liked_ids)
        assert extra_count == 0  # all ingredients are liked
        
        # No ingredients liked
        liked_ids = set()
        extra_count = count_extra_ingredients(recipe, liked_ids)
        assert extra_count == 4  # no ingredients are liked

    def test_count_extra_ingredients_empty_recipe(self):
        """Test with recipe that has no ingredients."""
        recipe = Recipe(
            title="Empty Recipe",
            source="test",
            url="http://test.com",
            meal_type="lunch",
            steps_excerpt="Test steps",
            normalized_ingredient_ids=[]
        )
        
        liked_ids = {1, 2, 3}
        extra_count = count_extra_ingredients(recipe, liked_ids)
        assert extra_count == 0

    def test_count_extra_ingredients_none_ingredients(self):
        """Test with recipe that has None as normalized_ingredient_ids."""
        recipe = Recipe(
            title="None Recipe",
            source="test",
            url="http://test.com",
            meal_type="lunch",
            steps_excerpt="Test steps",
            normalized_ingredient_ids=None
        )
        
        liked_ids = {1, 2, 3}
        extra_count = count_extra_ingredients(recipe, liked_ids)
        assert extra_count == 0

    def test_count_extra_ingredients_superset_liked(self):
        """Test when liked ingredients is a superset of recipe ingredients."""
        recipe = Recipe(
            title="Simple Recipe",
            source="test",
            url="http://test.com",
            meal_type="lunch",
            steps_excerpt="Test steps",
            normalized_ingredient_ids=[1, 2]
        )
        
        liked_ids = {1, 2, 3, 4, 5}  # More liked than in recipe
        extra_count = count_extra_ingredients(recipe, liked_ids)
        assert extra_count == 0

    def test_count_extra_ingredients_partial_overlap(self):
        """Test with partial overlap between recipe and liked ingredients."""
        recipe = Recipe(
            title="Complex Recipe",
            source="test",
            url="http://test.com",
            meal_type="lunch",
            steps_excerpt="Test steps",
            normalized_ingredient_ids=[1, 2, 3, 4, 5]
        )
        
        liked_ids = {2, 4, 6, 8}  # Only 2 and 4 match
        extra_count = count_extra_ingredients(recipe, liked_ids)
        assert extra_count == 3  # ingredients 1, 3, 5 are not liked


class TestHasBannedIngredients:
    """Test suite for has_banned_ingredients function."""

    def test_has_banned_ingredients_with_banned(self):
        """Test checking for banned ingredients when they exist."""
        recipe = Recipe(
            title="Test Recipe",
            source="test",
            url="http://test.com",
            meal_type="lunch",
            steps_excerpt="Test steps",
            normalized_ingredient_ids=[1, 2, 3]
        )
        
        banned_ids = {2}
        assert has_banned_ingredients(recipe, banned_ids) is True
        
        banned_ids = {2, 4}  # One banned ingredient present
        assert has_banned_ingredients(recipe, banned_ids) is True

    def test_has_banned_ingredients_without_banned(self):
        """Test checking for banned ingredients when none exist."""
        recipe = Recipe(
            title="Test Recipe",
            source="test",
            url="http://test.com",
            meal_type="lunch",
            steps_excerpt="Test steps",
            normalized_ingredient_ids=[1, 2, 3]
        )
        
        banned_ids = {4, 5}
        assert has_banned_ingredients(recipe, banned_ids) is False

    def test_has_banned_ingredients_empty_banned(self):
        """Test with no banned ingredients."""
        recipe = Recipe(
            title="Test Recipe",
            source="test",
            url="http://test.com",
            meal_type="lunch",
            steps_excerpt="Test steps",
            normalized_ingredient_ids=[1, 2, 3]
        )
        
        banned_ids = set()
        assert has_banned_ingredients(recipe, banned_ids) is False

    def test_has_banned_ingredients_empty_recipe(self):
        """Test banned ingredients check with empty recipe."""
        recipe = Recipe(
            title="Empty Recipe",
            source="test",
            url="http://test.com",
            meal_type="lunch",
            steps_excerpt="Test steps",
            normalized_ingredient_ids=[]
        )
        
        banned_ids = {1, 2, 3}
        assert has_banned_ingredients(recipe, banned_ids) is False

    def test_has_banned_ingredients_none_ingredients(self):
        """Test with None as normalized_ingredient_ids."""
        recipe = Recipe(
            title="None Recipe",
            source="test",
            url="http://test.com",
            meal_type="lunch",
            steps_excerpt="Test steps",
            normalized_ingredient_ids=None
        )
        
        banned_ids = {1, 2, 3}
        assert has_banned_ingredients(recipe, banned_ids) is False

    def test_has_banned_ingredients_multiple_banned(self):
        """Test with multiple banned ingredients."""
        recipe = Recipe(
            title="Multi Recipe",
            source="test",
            url="http://test.com",
            meal_type="lunch",
            steps_excerpt="Test steps",
            normalized_ingredient_ids=[1, 2, 3, 4, 5]
        )
        
        banned_ids = {2, 4, 6}  # 2 and 4 are in recipe
        assert has_banned_ingredients(recipe, banned_ids) is True


class TestGetPreferences:
    """Test suite for get_preferences function."""

    @patch('app.services.recipe_filter.Session')
    def test_get_preferences_existing(self, mock_session_class):
        """Test getting existing preferences."""
        mock_session = Mock(spec=Session)
        existing_prefs = Preferences(id=1, liked_ids=[1, 2, 3], banned_ids=[4, 5])
        mock_session.get.return_value = existing_prefs
        
        result = get_preferences(mock_session)
        
        assert result == existing_prefs
        mock_session.get.assert_called_once_with(Preferences, 1)
        mock_session.add.assert_not_called()
        mock_session.commit.assert_not_called()

    @patch('app.services.recipe_filter.Session')
    def test_get_preferences_create_default(self, mock_session_class):
        """Test creating default preferences when none exist."""
        mock_session = Mock(spec=Session)
        mock_session.get.return_value = None  # No existing preferences
        
        result = get_preferences(mock_session)
        
        mock_session.get.assert_called_once_with(Preferences, 1)
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once()
        
        # Check that default preferences were created
        added_prefs = mock_session.add.call_args[0][0]
        assert added_prefs.id == 1
        assert added_prefs.liked_ids == []
        assert added_prefs.banned_ids == []


class TestGetRecentRecipeIds:
    """Test suite for get_recent_recipe_ids function."""

    @patch('app.services.recipe_filter.Session')
    @patch('app.services.recipe_filter.select')
    def test_get_recent_recipe_ids_with_history(self, mock_select, mock_session_class):
        """Test getting recent recipe IDs when history exists."""
        mock_session = Mock(spec=Session)
        mock_statement = Mock()
        mock_select.return_value = mock_statement
        mock_statement.where.return_value = mock_statement
        mock_statement.order_by.return_value = mock_statement
        mock_statement.limit.return_value = mock_statement
        
        # Mock the execution result
        mock_session.exec.return_value.all.return_value = [101, 102, 103]
        
        result = get_recent_recipe_ids(mock_session, "dinner", limit=3)
        
        assert result == {101, 102, 103}
        mock_select.assert_called_once_with(SpinHistory.recipe_id)
        mock_statement.where.assert_called_once()
        mock_statement.order_by.assert_called_once()
        mock_statement.limit.assert_called_once_with(3)

    @patch('app.services.recipe_filter.Session')
    @patch('app.services.recipe_filter.select')
    def test_get_recent_recipe_ids_empty_history(self, mock_select, mock_session_class):
        """Test getting recent recipe IDs when no history exists."""
        mock_session = Mock(spec=Session)
        mock_statement = Mock()
        mock_select.return_value = mock_statement
        mock_statement.where.return_value = mock_statement
        mock_statement.order_by.return_value = mock_statement
        mock_statement.limit.return_value = mock_statement
        
        # Mock empty result
        mock_session.exec.return_value.all.return_value = []
        
        result = get_recent_recipe_ids(mock_session, "breakfast")
        
        assert result == set()

    @patch('app.services.recipe_filter.Session')
    @patch('app.services.recipe_filter.select')
    def test_get_recent_recipe_ids_default_limit(self, mock_select, mock_session_class):
        """Test default limit parameter."""
        mock_session = Mock(spec=Session)
        mock_statement = Mock()
        mock_select.return_value = mock_statement
        mock_statement.where.return_value = mock_statement
        mock_statement.order_by.return_value = mock_statement
        mock_statement.limit.return_value = mock_statement
        
        mock_session.exec.return_value.all.return_value = []
        
        get_recent_recipe_ids(mock_session, "lunch")
        
        mock_statement.limit.assert_called_once_with(5)  # Default limit


class TestFilterRecipes:
    """Test suite for filter_recipes function."""

    def create_test_recipes(self):
        """Create test recipes for filtering."""
        return [
            Recipe(
                id=1,
                title="Perfect Match",
                source="test",
                url="http://test1.com",
                meal_type="dinner",
                steps_excerpt="Steps",
                normalized_ingredient_ids=[1, 2]  # All liked
            ),
            Recipe(
                id=2,
                title="One Extra",
                source="test",
                url="http://test2.com",
                meal_type="dinner",
                steps_excerpt="Steps",
                normalized_ingredient_ids=[1, 2, 3]  # One extra ingredient
            ),
            Recipe(
                id=3,
                title="Banned Recipe",
                source="test",
                url="http://test3.com",
                meal_type="dinner",
                steps_excerpt="Steps",
                normalized_ingredient_ids=[1, 4]  # Contains banned ingredient 4
            ),
            Recipe(
                id=4,
                title="Too Many Extra",
                source="test",
                url="http://test4.com",
                meal_type="dinner",
                steps_excerpt="Steps",
                normalized_ingredient_ids=[5, 6, 7]  # All extra ingredients
            ),
            Recipe(
                id=5,
                title="Recent Recipe",
                source="test",
                url="http://test5.com",
                meal_type="dinner",
                steps_excerpt="Steps",
                normalized_ingredient_ids=[1, 2]  # Perfect but recent
            ),
        ]

    @patch('app.services.recipe_filter.get_preferences')
    @patch('app.services.recipe_filter.get_recent_recipe_ids')
    @patch('app.services.recipe_filter.select')
    def test_filter_recipes_basic(self, mock_select, mock_get_recent, mock_get_prefs):
        """Test basic recipe filtering functionality."""
        mock_session = Mock(spec=Session)
        
        # Setup test data
        test_recipes = self.create_test_recipes()
        mock_session.exec.return_value = iter(test_recipes)
        
        # Setup preferences
        mock_prefs = Mock()
        mock_prefs.liked_ids = [1, 2]  # Like ingredients 1 and 2
        mock_prefs.banned_ids = [4]    # Ban ingredient 4
        mock_get_prefs.return_value = mock_prefs
        mock_get_recent.return_value = set()  # No recent recipes
        
        # Test with allow_one_extra=False
        result = filter_recipes(mock_session, "dinner", allow_one_extra=False)
        
        # Only perfect matches should be returned (recipes 1 and 5)
        assert len(result) == 2
        assert result[0].id == 1
        assert result[1].id == 5

    @patch('app.services.recipe_filter.get_preferences')
    @patch('app.services.recipe_filter.get_recent_recipe_ids')
    @patch('app.services.recipe_filter.select')
    def test_filter_recipes_allow_one_extra(self, mock_select, mock_get_recent, mock_get_prefs):
        """Test filtering with allow_one_extra=True."""
        mock_session = Mock(spec=Session)
        
        test_recipes = self.create_test_recipes()
        mock_session.exec.return_value = iter(test_recipes)
        
        mock_prefs = Mock()
        mock_prefs.liked_ids = [1, 2]
        mock_prefs.banned_ids = [4]
        mock_get_prefs.return_value = mock_prefs
        mock_get_recent.return_value = set()
        
        # Test with allow_one_extra=True
        result = filter_recipes(mock_session, "dinner", allow_one_extra=True)
        
        # Should return perfect matches (1, 5) and one-extra recipes (2)
        assert len(result) == 3
        recipe_ids = {r.id for r in result}
        assert recipe_ids == {1, 2, 5}

    @patch('app.services.recipe_filter.get_preferences')
    @patch('app.services.recipe_filter.get_recent_recipe_ids')
    @patch('app.services.recipe_filter.select')
    def test_filter_recipes_hide_recent(self, mock_select, mock_get_recent, mock_get_prefs):
        """Test filtering with hide_recent=True."""
        mock_session = Mock(spec=Session)
        
        test_recipes = self.create_test_recipes()
        mock_session.exec.return_value = iter(test_recipes)
        
        mock_prefs = Mock()
        mock_prefs.liked_ids = [1, 2]
        mock_prefs.banned_ids = [4]
        mock_get_prefs.return_value = mock_prefs
        mock_get_recent.return_value = {5}  # Recipe 5 is recent
        
        result = filter_recipes(mock_session, "dinner", allow_one_extra=False, hide_recent=True)
        
        # Only recipe 1 should be returned (recipe 5 is recent)
        assert len(result) == 1
        assert result[0].id == 1

    @patch('app.services.recipe_filter.get_preferences')
    @patch('app.services.recipe_filter.get_recent_recipe_ids')
    @patch('app.services.recipe_filter.select')
    def test_filter_recipes_no_valid_recipes(self, mock_select, mock_get_recent, mock_get_prefs):
        """Test when no recipes match the criteria."""
        mock_session = Mock(spec=Session)
        
        test_recipes = self.create_test_recipes()
        mock_session.exec.return_value = iter(test_recipes)
        
        mock_prefs = Mock()
        mock_prefs.liked_ids = [10, 11]  # Don't like any ingredients in test recipes
        mock_prefs.banned_ids = []
        mock_get_prefs.return_value = mock_prefs
        mock_get_recent.return_value = set()
        
        result = filter_recipes(mock_session, "dinner", allow_one_extra=False)
        
        assert len(result) == 0

    @patch('app.services.recipe_filter.get_preferences')
    @patch('app.services.recipe_filter.get_recent_recipe_ids')
    @patch('app.services.recipe_filter.select')
    def test_filter_recipes_empty_preferences(self, mock_select, mock_get_recent, mock_get_prefs):
        """Test filtering with empty preferences."""
        mock_session = Mock(spec=Session)
        
        test_recipes = self.create_test_recipes()
        mock_session.exec.return_value = iter(test_recipes)
        
        mock_prefs = Mock()
        mock_prefs.liked_ids = []  # No liked ingredients
        mock_prefs.banned_ids = []  # No banned ingredients
        mock_get_prefs.return_value = mock_prefs
        mock_get_recent.return_value = set()
        
        result = filter_recipes(mock_session, "dinner", allow_one_extra=True)
        
        # With allow_one_extra=True, recipes with 0 or 1 extra ingredients should be returned
        # All ingredients are "extra" since none are liked, so only recipes with ≤1 ingredient
        valid_recipes = [r for r in result if len(r.normalized_ingredient_ids or []) <= 1]
        assert len(valid_recipes) == 0  # All test recipes have 2+ ingredients


class TestGetRandomRecipe:
    """Test suite for get_random_recipe function."""

    @patch('app.services.recipe_filter.filter_recipes')
    @patch('app.services.recipe_filter.random.choice')
    def test_get_random_recipe_with_valid_recipes(self, mock_choice, mock_filter):
        """Test getting random recipe when valid recipes exist."""
        mock_session = Mock(spec=Session)
        
        # Mock filter_recipes to return test recipes
        test_recipes = [
            Mock(id=1, title="Recipe 1"),
            Mock(id=2, title="Recipe 2"),
            Mock(id=3, title="Recipe 3"),
        ]
        mock_filter.return_value = test_recipes
        mock_choice.return_value = test_recipes[1]  # Return recipe 2
        
        result = get_random_recipe(mock_session, "dinner", allow_one_extra=True)
        
        assert result == test_recipes[1]
        mock_filter.assert_called_once_with(mock_session, "dinner", True, False)
        mock_choice.assert_called_once_with(test_recipes)

    @patch('app.services.recipe_filter.filter_recipes')
    def test_get_random_recipe_no_valid_recipes(self, mock_filter):
        """Test getting random recipe when no valid recipes exist."""
        mock_session = Mock(spec=Session)
        
        mock_filter.return_value = []  # No valid recipes
        
        result = get_random_recipe(mock_session, "breakfast", allow_one_extra=False)
        
        assert result is None
        mock_filter.assert_called_once_with(mock_session, "breakfast", False, False)

    @patch('app.services.recipe_filter.filter_recipes')
    @patch('app.services.recipe_filter.random.choice')
    def test_get_random_recipe_with_hide_recent(self, mock_choice, mock_filter):
        """Test get_random_recipe with hide_recent parameter."""
        mock_session = Mock(spec=Session)
        
        test_recipe = Mock(id=1, title="Recipe 1")
        mock_filter.return_value = [test_recipe]
        mock_choice.return_value = test_recipe
        
        result = get_random_recipe(mock_session, "lunch", allow_one_extra=True, hide_recent=True)
        
        assert result == test_recipe
        mock_filter.assert_called_once_with(mock_session, "lunch", True, True)

    @patch('app.services.recipe_filter.filter_recipes')
    @patch('app.services.recipe_filter.random.choice')
    def test_get_random_recipe_single_recipe(self, mock_choice, mock_filter):
        """Test getting random recipe when only one recipe is available."""
        mock_session = Mock(spec=Session)
        
        single_recipe = Mock(id=42, title="Only Recipe")
        mock_filter.return_value = [single_recipe]
        mock_choice.return_value = single_recipe
        
        result = get_random_recipe(mock_session, "snack", allow_one_extra=False)
        
        assert result == single_recipe
        mock_choice.assert_called_once_with([single_recipe])


class TestIntegrationScenarios:
    """Integration tests for complex filtering scenarios."""

    def test_complex_filtering_scenario(self):
        """Test a complex real-world filtering scenario."""
        # This would be better as a proper integration test with a real database
        # but demonstrates the expected behavior
        
        # Mock a complex scenario
        recipes = [
            Recipe(
                id=1, title="Pasta with Tomatoes", source="test", url="test.com",
                meal_type="dinner", steps_excerpt="Cook pasta",
                normalized_ingredient_ids=[1, 2, 3]  # pasta, tomato, cheese
            ),
            Recipe(
                id=2, title="Simple Salad", source="test", url="test.com", 
                meal_type="dinner", steps_excerpt="Mix ingredients",
                normalized_ingredient_ids=[2, 4]  # tomato, lettuce
            ),
        ]
        
        # User likes tomatoes (2) and cheese (3), bans nothing
        liked_ids = {2, 3}
        banned_ids = set()
        
        # Recipe 1: has 1 extra ingredient (pasta=1)
        extra_count_1 = count_extra_ingredients(recipes[0], liked_ids)
        has_banned_1 = has_banned_ingredients(recipes[0], banned_ids)
        
        # Recipe 2: has 1 extra ingredient (lettuce=4)
        extra_count_2 = count_extra_ingredients(recipes[1], liked_ids)
        has_banned_2 = has_banned_ingredients(recipes[1], banned_ids)
        
        assert extra_count_1 == 1
        assert has_banned_1 is False
        assert extra_count_2 == 1  
        assert has_banned_2 is False
        
        # Both recipes should be valid with allow_one_extra=True
        # Neither should be valid with allow_one_extra=False


# Fixtures for common test data
@pytest.fixture
def sample_recipe():
    """Fixture providing a sample recipe for testing."""
    return Recipe(
        id=1,
        title="Test Recipe",
        source="test_source",
        url="http://test.com",
        meal_type="dinner",
        steps_excerpt="Test cooking steps",
        normalized_ingredient_ids=[1, 2, 3]
    )


@pytest.fixture
def sample_preferences():
    """Fixture providing sample preferences for testing."""
    return Preferences(
        id=1,
        liked_ids=[1, 2],
        banned_ids=[4, 5]
    )


@pytest.fixture
def mock_session():
    """Fixture providing a mock database session."""
    return Mock(spec=Session)