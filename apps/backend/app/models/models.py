from typing import List, Optional
from sqlmodel import SQLModel, Field, Relationship, JSON, Column
from datetime import datetime


class Ingredient(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    normalized: str = Field(index=True, unique=True)
    
    recipe_ingredients: List["RecipeIngredient"] = Relationship(back_populates="ingredient")


class Recipe(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(index=True)
    source: str
    url: str
    meal_type: str = Field(index=True)
    time_minutes: Optional[int] = None
    image_url: Optional[str] = None
    tags: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    steps_excerpt: str
    normalized_ingredient_ids: List[int] = Field(default_factory=list, sa_column=Column(JSON))
    
    recipe_ingredients: List["RecipeIngredient"] = Relationship(back_populates="recipe")
    spin_history: List["SpinHistory"] = Relationship(back_populates="recipe")


class RecipeIngredient(SQLModel, table=True):
    recipe_id: int = Field(foreign_key="recipe.id", primary_key=True)
    ingredient_id: int = Field(foreign_key="ingredient.id", primary_key=True)
    amount_text: str
    
    recipe: Recipe = Relationship(back_populates="recipe_ingredients")
    ingredient: Ingredient = Relationship(back_populates="recipe_ingredients")


class Preferences(SQLModel, table=True):
    id: int = Field(default=1, primary_key=True)
    liked_ids: List[int] = Field(default_factory=list, sa_column=Column(JSON))
    banned_ids: List[int] = Field(default_factory=list, sa_column=Column(JSON))


class SpinHistory(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    recipe_id: int = Field(foreign_key="recipe.id")
    meal_type: str = Field(index=True)
    allow_one_extra: bool
    spun_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    
    recipe: Recipe = Relationship(back_populates="spin_history")