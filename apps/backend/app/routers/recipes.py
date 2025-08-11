from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from app.db import get_session
from app.models.models import Recipe, SpinHistory, RecipeIngredient, Ingredient
from app.models.schemas import RecipeResponse, RecipeWithIngredients, RecipeMatchResponse
from app.services.recipe_filter import get_best_matching_recipe, count_extra_ingredients, get_preferences, get_match_quality
from datetime import datetime

router = APIRouter(prefix="/api/recipes", tags=["recipes"])


@router.get("/random", response_model=RecipeMatchResponse)
def get_random_recipe_endpoint(
    meal: str = Query(..., description="Meal type: breakfast, lunch, snack, dinner"),
    allow_one_extra: bool = Query(False, description="Allow one ingredient not in liked list"),
    hide_recent: bool = Query(True, description="Hide recently spun recipes"),
    session: Session = Depends(get_session)
):
    """Get the best matching recipe and add to spin history."""
    if meal not in ["breakfast", "lunch", "snack", "dinner"]:
        raise HTTPException(status_code=400, detail="Invalid meal type")
    
    recipe = get_best_matching_recipe(session, meal, allow_one_extra, hide_recent)
    
    if not recipe:
        raise HTTPException(status_code=404, detail="No recipes found for this meal type")
    
    # Calculate match information
    prefs = get_preferences(session)
    liked_ids = set(prefs.liked_ids)
    extra_count = count_extra_ingredients(recipe, liked_ids)
    total_ingredients = len(recipe.normalized_ingredient_ids) if recipe.normalized_ingredient_ids else 0
    match_quality = get_match_quality(extra_count, allow_one_extra)
    
    # Add to spin history
    history_entry = SpinHistory(
        recipe_id=recipe.id,
        meal_type=meal,
        allow_one_extra=allow_one_extra,
        spun_at=datetime.utcnow()
    )
    session.add(history_entry)
    session.commit()
    
    return RecipeMatchResponse(
        id=recipe.id,
        title=recipe.title,
        source=recipe.source,
        url=recipe.url,
        meal_type=recipe.meal_type,
        time_minutes=recipe.time_minutes,
        image_url=recipe.image_url,
        tags=recipe.tags,
        steps_excerpt=recipe.steps_excerpt,
        extra_ingredients_count=extra_count,
        total_ingredients_count=total_ingredients,
        match_quality=match_quality
    )


@router.get("/{recipe_id}", response_model=RecipeWithIngredients)
def get_recipe_by_id(
    recipe_id: int,
    session: Session = Depends(get_session)
):
    """Get a specific recipe with its ingredients."""
    recipe = session.get(Recipe, recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    
    # Get recipe ingredients
    statement = (
        select(RecipeIngredient, Ingredient)
        .join(Ingredient)
        .where(RecipeIngredient.recipe_id == recipe_id)
    )
    results = session.exec(statement).all()
    
    ingredients = [
        {
            "id": ingredient.id,
            "name": ingredient.name,
            "normalized": ingredient.normalized
        }
        for _, ingredient in results
    ]
    
    return RecipeWithIngredients(
        id=recipe.id,
        title=recipe.title,
        source=recipe.source,
        url=recipe.url,
        meal_type=recipe.meal_type,
        time_minutes=recipe.time_minutes,
        image_url=recipe.image_url,
        tags=recipe.tags,
        steps_excerpt=recipe.steps_excerpt,
        ingredients=ingredients
    )