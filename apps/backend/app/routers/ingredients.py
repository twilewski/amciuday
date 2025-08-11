from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.db import get_session
from app.models.models import Ingredient, Preferences
from app.models.schemas import IngredientCreate, IngredientResponse
from app.services.normalization import normalize_ingredient

router = APIRouter(prefix="/api/ingredients", tags=["ingredients"])


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


def get_preferences(session: Session) -> Preferences:
    """Get user preferences, create default if not exists."""
    prefs = session.get(Preferences, 1)
    if not prefs:
        prefs = Preferences(id=1, liked_ids=[], banned_ids=[])
        session.add(prefs)
        session.commit()
        session.refresh(prefs)
    return prefs


@router.get("/liked", response_model=List[IngredientResponse])
def get_liked_ingredients(session: Session = Depends(get_session)):
    """Get all liked ingredients."""
    prefs = get_preferences(session)
    
    if not prefs.liked_ids:
        return []
    
    statement = select(Ingredient).where(Ingredient.id.in_(prefs.liked_ids))
    ingredients = session.exec(statement).all()
    
    return [
        IngredientResponse(id=ing.id, name=ing.name, normalized=ing.normalized)
        for ing in ingredients
    ]


@router.post("/liked", response_model=IngredientResponse)
def add_liked_ingredient(
    ingredient_data: IngredientCreate,
    session: Session = Depends(get_session)
):
    """Add ingredient to liked list."""
    ingredient = get_or_create_ingredient(session, ingredient_data.name)
    prefs = get_preferences(session)
    
    if ingredient.id not in prefs.liked_ids:
        # Create new list to trigger SQLModel dirty tracking
        prefs.liked_ids = prefs.liked_ids + [ingredient.id]
        session.add(prefs)
        session.commit()
        session.refresh(prefs)
    
    return IngredientResponse(
        id=ingredient.id,
        name=ingredient.name,
        normalized=ingredient.normalized
    )


@router.delete("/liked/{ingredient_id}")
def remove_liked_ingredient(
    ingredient_id: int,
    session: Session = Depends(get_session)
):
    """Remove ingredient from liked list."""
    prefs = get_preferences(session)
    
    if ingredient_id in prefs.liked_ids:
        # Create new list to trigger SQLModel dirty tracking
        prefs.liked_ids = [id for id in prefs.liked_ids if id != ingredient_id]
        session.add(prefs)
        session.commit()
        session.refresh(prefs)
    
    return {"message": "Ingredient removed from liked list"}


@router.get("/banned", response_model=List[IngredientResponse])
def get_banned_ingredients(session: Session = Depends(get_session)):
    """Get all banned ingredients."""
    prefs = get_preferences(session)
    
    if not prefs.banned_ids:
        return []
    
    statement = select(Ingredient).where(Ingredient.id.in_(prefs.banned_ids))
    ingredients = session.exec(statement).all()
    
    return [
        IngredientResponse(id=ing.id, name=ing.name, normalized=ing.normalized)
        for ing in ingredients
    ]


@router.post("/banned", response_model=IngredientResponse)
def add_banned_ingredient(
    ingredient_data: IngredientCreate,
    session: Session = Depends(get_session)
):
    """Add ingredient to banned list."""
    ingredient = get_or_create_ingredient(session, ingredient_data.name)
    prefs = get_preferences(session)
    
    if ingredient.id not in prefs.banned_ids:
        # Create new list to trigger SQLModel dirty tracking
        prefs.banned_ids = prefs.banned_ids + [ingredient.id]
        session.add(prefs)
        session.commit()
        session.refresh(prefs)
    
    return IngredientResponse(
        id=ingredient.id,
        name=ingredient.name,
        normalized=ingredient.normalized
    )


@router.delete("/banned/{ingredient_id}")
def remove_banned_ingredient(
    ingredient_id: int,
    session: Session = Depends(get_session)
):
    """Remove ingredient from banned list."""
    prefs = get_preferences(session)
    
    if ingredient_id in prefs.banned_ids:
        # Create new list to trigger SQLModel dirty tracking
        prefs.banned_ids = [id for id in prefs.banned_ids if id != ingredient_id]
        session.add(prefs)
        session.commit()
        session.refresh(prefs)
    
    return {"message": "Ingredient removed from banned list"}