from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime


class IngredientCreate(BaseModel):
    name: str


class IngredientResponse(BaseModel):
    id: int
    name: str
    normalized: str


class RecipeResponse(BaseModel):
    id: int
    title: str
    source: str
    url: str
    meal_type: str
    time_minutes: Optional[int]
    image_url: Optional[str]
    tags: List[str]
    steps_excerpt: str


class RecipeMatchResponse(RecipeResponse):
    """Recipe response with matching information."""
    extra_ingredients_count: int
    total_ingredients_count: int
    match_quality: str  # "perfect", "good", "acceptable"


class RecipeWithIngredients(RecipeResponse):
    ingredients: List[IngredientResponse]


class SpinHistoryResponse(BaseModel):
    id: int
    recipe: RecipeResponse
    meal_type: str
    allow_one_extra: bool
    spun_at: datetime


class SeedRecipe(BaseModel):
    title: str
    source: str
    url: str
    meal_type: str
    time_minutes: Optional[int] = None
    image_url: Optional[str] = None
    tags: List[str] = []
    steps_excerpt: str
    ingredients: List[str]