from typing import List, Set, Optional
from sqlmodel import Session, select
from app.models.models import Recipe, Preferences, SpinHistory
import random


def get_preferences(session: Session) -> Preferences:
    """Get user preferences, create default if not exists."""
    prefs = session.get(Preferences, 1)
    if not prefs:
        prefs = Preferences(id=1, liked_ids=[], banned_ids=[])
        session.add(prefs)
        session.commit()
        session.refresh(prefs)
    return prefs


def count_extra_ingredients(recipe: Recipe, liked_ids: Set[int]) -> int:
    """Count how many recipe ingredients are not in the liked list."""
    if not recipe.normalized_ingredient_ids:
        return 0
    
    extra_count = 0
    for ingredient_id in recipe.normalized_ingredient_ids:
        if ingredient_id not in liked_ids:
            extra_count += 1
    
    return extra_count


def has_banned_ingredients(recipe: Recipe, banned_ids: Set[int]) -> bool:
    """Check if recipe contains any banned ingredients."""
    if not recipe.normalized_ingredient_ids or not banned_ids:
        return False
    
    return any(ingredient_id in banned_ids for ingredient_id in recipe.normalized_ingredient_ids)


def get_recent_recipe_ids(session: Session, meal_type: str, limit: int = 5) -> Set[int]:
    """Get recently spun recipe IDs for the given meal type."""
    statement = (
        select(SpinHistory.recipe_id)
        .where(SpinHistory.meal_type == meal_type)
        .order_by(SpinHistory.spun_at.desc())
        .limit(limit)
    )
    results = session.exec(statement).all()
    return set(results)


def filter_recipes(
    session: Session,
    meal_type: str,
    allow_one_extra: bool,
    hide_recent: bool = False
) -> List[Recipe]:
    """Filter recipes based on meal type and ingredient preferences."""
    statement = select(Recipe).where(Recipe.meal_type == meal_type)
    all_recipes = list(session.exec(statement))
    
    prefs = get_preferences(session)
    liked_ids = set(prefs.liked_ids)
    banned_ids = set(prefs.banned_ids)
    
    recent_ids = get_recent_recipe_ids(session, meal_type) if hide_recent else set()
    
    valid_recipes = []
    
    for recipe in all_recipes:
        if hide_recent and recipe.id in recent_ids:
            continue
            
        if has_banned_ingredients(recipe, banned_ids):
            continue
        
        extra_count = count_extra_ingredients(recipe, liked_ids)
        
        if allow_one_extra:
            if extra_count <= 1:
                valid_recipes.append(recipe)
        else:
            if extra_count == 0:
                valid_recipes.append(recipe)
    
    return valid_recipes


def get_best_matching_recipe(
    session: Session,
    meal_type: str,
    allow_one_extra: bool,
    hide_recent: bool = False
) -> Optional[Recipe]:
    """Get the best matching recipe, fallback to closest match if no perfect match."""
    # First try to get perfect matches
    valid_recipes = filter_recipes(session, meal_type, allow_one_extra, hide_recent)
    
    if valid_recipes:
        return random.choice(valid_recipes)
    
    # If no perfect matches, find the best available recipes
    statement = select(Recipe).where(Recipe.meal_type == meal_type)
    all_recipes = list(session.exec(statement))
    
    if not all_recipes:
        return None
    
    prefs = get_preferences(session)
    liked_ids = set(prefs.liked_ids)
    banned_ids = set(prefs.banned_ids)
    recent_ids = get_recent_recipe_ids(session, meal_type) if hide_recent else set()
    
    # Score recipes by how well they match
    scored_recipes = []
    
    for recipe in all_recipes:
        if hide_recent and recipe.id in recent_ids:
            continue
            
        if has_banned_ingredients(recipe, banned_ids):
            continue  # Never return recipes with banned ingredients
        
        extra_count = count_extra_ingredients(recipe, liked_ids)
        
        # Score: lower extra_count = better score
        score = extra_count
        scored_recipes.append((score, recipe))
    
    if not scored_recipes:
        return None
    
    # Sort by score (best first) and return one of the best matches
    scored_recipes.sort(key=lambda x: x[0])
    best_score = scored_recipes[0][0]
    
    # Get all recipes with the best score
    best_recipes = [recipe for score, recipe in scored_recipes if score == best_score]
    
    return random.choice(best_recipes)


def get_match_quality(extra_count: int, allow_one_extra: bool) -> str:
    """Determine match quality based on extra ingredients count."""
    if extra_count == 0:
        return "perfect"
    elif extra_count == 1 and allow_one_extra:
        return "good"
    elif extra_count <= 3:
        return "acceptable" 
    else:
        return "poor"


def get_random_recipe(
    session: Session,
    meal_type: str,
    allow_one_extra: bool,
    hide_recent: bool = False
) -> Optional[Recipe]:
    """Get a random recipe matching the criteria (legacy function)."""
    return get_best_matching_recipe(session, meal_type, allow_one_extra, hide_recent)