export type MealType = "breakfast" | "lunch" | "snack" | "dinner";

export interface Recipe {
  id: number;
  title: string;
  source: string;
  url: string;
  meal_type: MealType;
  time_minutes?: number;
  image_url?: string;
  tags: string[];
  steps_excerpt: string;
  normalized_ingredient_ids: number[];
}

export interface Ingredient {
  id: number;
  name: string;
  normalized: string;
}

export interface RecipeIngredient {
  recipe_id: number;
  ingredient_id: number;
  amount_text: string;
}

export interface SpinHistoryEntry {
  id: number;
  recipe_id: number;
  meal_type: MealType;
  allow_one_extra: boolean;
  spun_at: string;
}