from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.db import get_session
from app.models.models import Recipe, Ingredient, RecipeIngredient
from app.models.schemas import SeedRecipe
from app.services.normalization import normalize_ingredient
import json
import os
from app.core.settings import settings

router = APIRouter(prefix="/api/import", tags=["seed"])


def get_or_create_ingredient(session: Session, name: str) -> Ingredient:
    """Get existing ingredient or create new one."""
    normalized = normalize_ingredient(name)
    
    # Check if ingredient already exists
    statement = select(Ingredient).where(Ingredient.normalized == normalized)
    existing = session.exec(statement).first()
    
    if existing:
        return existing
    
    # Create new ingredient
    ingredient = Ingredient(name=name, normalized=normalized)
    session.add(ingredient)
    session.commit()
    session.refresh(ingredient)
    return ingredient


@router.post("/seed")
def import_seed_data(
    recipes: List[SeedRecipe] = None,
    session: Session = Depends(get_session)
):
    """Import seed recipes from JSON data or file."""
    
    # If no recipes provided in body, try to load from file
    if recipes is None:
        if not os.path.exists(settings.seed_json):
            raise HTTPException(status_code=400, detail=f"Seed file not found: {settings.seed_json}")
        
        try:
            with open(settings.seed_json, 'r', encoding='utf-8') as f:
                seed_data = json.load(f)
                if isinstance(seed_data, dict) and 'recipes' in seed_data:
                    recipes_data = seed_data['recipes']
                else:
                    recipes_data = seed_data
                
                recipes = [SeedRecipe(**recipe) for recipe in recipes_data]
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to parse seed file: {str(e)}")
    
    imported_count = 0
    
    for seed_recipe in recipes:
        # Check if recipe already exists
        statement = select(Recipe).where(Recipe.url == seed_recipe.url)
        existing = session.exec(statement).first()
        
        if existing:
            continue  # Skip existing recipes
        
        # Create ingredients and get their IDs
        ingredient_ids = []
        for ingredient_name in seed_recipe.ingredients:
            ingredient = get_or_create_ingredient(session, ingredient_name)
            ingredient_ids.append(ingredient.id)
        
        # Create recipe
        recipe = Recipe(
            title=seed_recipe.title,
            source=seed_recipe.source,
            url=seed_recipe.url,
            meal_type=seed_recipe.meal_type,
            time_minutes=seed_recipe.time_minutes,
            image_url=seed_recipe.image_url,
            tags=seed_recipe.tags,
            steps_excerpt=seed_recipe.steps_excerpt,
            normalized_ingredient_ids=ingredient_ids
        )
        session.add(recipe)
        session.commit()
        session.refresh(recipe)
        
        # Create recipe-ingredient relationships
        for i, ingredient_name in enumerate(seed_recipe.ingredients):
            ingredient = get_or_create_ingredient(session, ingredient_name)
            recipe_ingredient = RecipeIngredient(
                recipe_id=recipe.id,
                ingredient_id=ingredient.id,
                amount_text=ingredient_name  # Use original text as amount
            )
            session.add(recipe_ingredient)
        
        session.commit()
        imported_count += 1
    
    return {
        "message": f"Successfully imported {imported_count} recipes",
        "total_processed": len(recipes)
    }