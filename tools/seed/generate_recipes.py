#!/usr/bin/env python3
"""
Expanded recipe generator for Amciu Day.
Generates 500 Polish recipes with variations.
"""

import json
import random
import sys
import time
from pathlib import Path
from typing import List, Dict, Tuple

# Add shared package to path
sys.path.append(str(Path(__file__).parent.parent.parent / "packages" / "shared"))
from normalization import normalize_ingredient


# Recipe templates with variations
RECIPE_TEMPLATES = {
    "breakfast": [
        {
            "base_title": "Naleśniki",
            "variations": ["z serem", "z dżemem", "z jabłkami", "z jogurtem", "z nutellą", "z bananem", "z śmietaną", "z twarogiem"],
            "base_ingredients": ["mąka", "mleko", "jajka", "sól"],
            "variable_ingredients": {
                "z serem": ["ser biały", "cukier"],
                "z dżemem": ["dżem", "masło"],
                "z jabłkami": ["jabłka", "cynamon", "cukier"],
                "z jogurtem": ["jogurt", "miód"],
                "z nutellą": ["nutella"],
                "z bananem": ["banan", "miód"],
                "z śmietaną": ["śmietana", "cukier"],
                "z twarogiem": ["twaróg", "cukier", "wanilia"]
            },
            "time_range": (15, 30),
            "tags": ["polska kuchnia", "słodkie", "tradycyjne"]
        },
        {
            "base_title": "Jajecznica",
            "variations": ["z szynką", "z ziemniakami", "z pomidorami", "z pieczarkami", "z cebulą", "z szczypiorkiem", "z papryką"],
            "base_ingredients": ["jajka", "masło", "sól", "pieprz"],
            "variable_ingredients": {
                "z szynką": ["szynka"],
                "z ziemniakami": ["ziemniaki", "cebula"],
                "z pomidorami": ["pomidory"],
                "z pieczarkami": ["pieczarki"],
                "z cebulą": ["cebula"],
                "z szczypiorkiem": ["szczypiorek"],
                "z papryką": ["papryka"]
            },
            "time_range": (10, 25),
            "tags": ["jajka", "szybkie", "syte"]
        },
        {
            "base_title": "Owsianka",
            "variations": ["z owocami", "z orzechami", "z miodem", "z jabłkami", "z jagodami", "z bananami"],
            "base_ingredients": ["płatki owsiane", "mleko", "sól"],
            "variable_ingredients": {
                "z owocami": ["jabłko", "banan", "jagody"],
                "z orzechami": ["orzechy", "miód"],
                "z miodem": ["miód"],
                "z jabłkami": ["jabłko", "cynamon"],
                "z jagodami": ["jagody", "miód"],
                "z bananami": ["banan", "orzechy"]
            },
            "time_range": (5, 15),
            "tags": ["zdrowe", "śniadanie", "owoce"]
        },
        {
            "base_title": "Tosty",
            "variations": ["z awokado", "z szynką", "z serem", "francuskie", "z pastą jajeczną", "z pomidorami"],
            "base_ingredients": ["chleb", "masło"],
            "variable_ingredients": {
                "z awokado": ["awokado", "cytryna", "sól"],
                "z szynką": ["szynka", "ser"],
                "z serem": ["ser", "pomidor"],
                "francuskie": ["jajka", "mleko", "cukier"],
                "z pastą jajeczną": ["jajka", "majoner", "szczypiorek"],
                "z pomidorami": ["pomidory", "oregano"]
            },
            "time_range": (5, 20),
            "tags": ["szybkie", "śniadanie"]
        }
    ],
    
    "lunch": [
        {
            "base_title": "Kotlet schabowy",
            "variations": ["z ziemniakami", "z frytkami", "z ryżem", "z mizerią", "po wiedeńsku"],
            "base_ingredients": ["schab", "jajka", "mąka", "bułka tarta", "olej", "sól", "pieprz"],
            "variable_ingredients": {
                "z ziemniakami": ["ziemniaki"],
                "z frytkami": ["ziemniaki", "olej"],
                "z ryżem": ["ryż"],
                "z mizerią": ["ogórek", "śmietana"],
                "po wiedeńsku": ["cytryna"]
            },
            "time_range": (30, 60),
            "tags": ["polska kuchnia", "mięso", "obiad"]
        },
        {
            "base_title": "Pierogi",
            "variations": ["ruskie", "z mięsem", "z kapustą i grzybami", "z jagodami", "z serem", "z ziemniakami"],
            "base_ingredients": ["mąka", "jajka", "woda", "sól"],
            "variable_ingredients": {
                "ruskie": ["ziemniaki", "ser biały", "cebula"],
                "z mięsem": ["mięso mielone", "cebula", "pieprz"],
                "z kapustą i grzybami": ["kapusta", "grzyby", "cebula"],
                "z jagodami": ["jagody", "cukier"],
                "z serem": ["ser biały", "cukier"],
                "z ziemniakami": ["ziemniaki", "cebula", "masło"]
            },
            "time_range": (45, 90),
            "tags": ["polska kuchnia", "tradycyjne"]
        },
        {
            "base_title": "Zupa",
            "variations": ["żurek", "pomidorowa", "ogórkowa", "rosół", "krupnik", "grochówka", "barszcz"],
            "base_ingredients": ["woda", "sól", "pieprz"],
            "variable_ingredients": {
                "żurek": ["żurek", "kiełbasa", "czosnek", "jajka"],
                "pomidorowa": ["pomidory", "ryż", "śmietana"],
                "ogórkowa": ["ogórki kiszone", "ziemniaki", "kiełbasa"],
                "rosół": ["kurczak", "marchew", "pietruszka", "cebula"],
                "krupnik": ["kasza pęczak", "ziemniaki", "marchew"],
                "grochówka": ["groch", "kiełbasa", "marchew"],
                "barszcz": ["barszcz", "czosnek", "słonina"]
            },
            "time_range": (30, 120),
            "tags": ["zupa", "tradycyjne", "gorące"]
        }
    ],
    
    "snack": [
        {
            "base_title": "Kanapki",
            "variations": ["z pastą jajeczną", "z tuńczykiem", "z szynką", "z serem", "z awokado", "z łososiem"],
            "base_ingredients": ["chleb", "masło"],
            "variable_ingredients": {
                "z pastą jajeczną": ["jajka", "majoner", "szczypiorek"],
                "z tuńczykiem": ["tuńczyk", "pomidor", "sałata"],
                "z szynką": ["szynka", "ser", "pomidor"],
                "z serem": ["ser", "ogórek"],
                "z awokado": ["awokado", "cytryna"],
                "z łososiem": ["łosoś", "koper"]
            },
            "time_range": (5, 15),
            "tags": ["szybkie", "przekąska"]
        },
        {
            "base_title": "Smoothie",
            "variations": ["zielone", "owocowe", "z jagodami", "z bananem", "z mango"],
            "base_ingredients": ["woda"],
            "variable_ingredients": {
                "zielone": ["szpinak", "jabłko", "banan", "cytryna"],
                "owocowe": ["jabłko", "banan", "pomarańcza"],
                "z jagodami": ["jagody", "jogurt", "miód"],
                "z bananem": ["banan", "mleko", "miód"],
                "z mango": ["mango", "jogurt", "limonka"]
            },
            "time_range": (3, 8),
            "tags": ["zdrowe", "napój", "owoce"]
        }
    ],
    
    "dinner": [
        {
            "base_title": "Sałatka",
            "variations": ["grecka", "cezar", "z tuńczykiem", "owocowa", "warzywna", "z kurczakiem"],
            "base_ingredients": ["sałata", "oliwa", "sól"],
            "variable_ingredients": {
                "grecka": ["pomidory", "ogórek", "ser feta", "oliwki"],
                "cezar": ["kurczak", "parmezan", "grzanki", "sos cezar"],
                "z tuńczykiem": ["tuńczyk", "jajka", "pomidory"],
                "owocowa": ["jabłko", "winogrona", "orzechy"],
                "warzywna": ["pomidor", "ogórek", "papryka"],
                "z kurczakiem": ["kurczak", "pomidor", "ser"]
            },
            "time_range": (10, 25),
            "tags": ["lekkie", "warzywa", "kolacja"]
        },
        {
            "base_title": "Wrap",
            "variations": ["z kurczakiem", "z warzywami", "z tuńczykiem", "z łososiem"],
            "base_ingredients": ["tortilla"],
            "variable_ingredients": {
                "z kurczakiem": ["kurczak", "sałata", "pomidor", "sos"],
                "z warzywami": ["papryka", "ogórek", "pomidor", "hummus"],
                "z tuńczykiem": ["tuńczyk", "sałata", "majoner"],
                "z łososiem": ["łosoś", "awokado", "rukola"]
            },
            "time_range": (10, 20),
            "tags": ["szybkie", "lekkie"]
        }
    ]
}

# Additional ingredients that can be randomly added
OPTIONAL_INGREDIENTS = [
    "oliwa", "ocet", "cukier", "sól", "pieprz", "czosnek", "cebula", "pietruszka", 
    "koper", "oregano", "bazylia", "tymianek", "rozmaryn", "cynamon", "wanilia"
]

# Polish sources for variety
SOURCES = [
    "kwestiasmaku.com", "aniagotuje.pl", "przepisy.pl", "gotujmy.pl", 
    "smaker.pl", "kuchniaiwypieki.pl", "mojegotowanie.pl", "beszamel.se.pl"
]


def generate_recipe(template: Dict, meal_type: str, recipe_id: int) -> Dict:
    """Generate a single recipe from template."""
    variation = random.choice(template["variations"])
    
    # Build ingredients list
    ingredients = template["base_ingredients"].copy()
    if variation in template["variable_ingredients"]:
        ingredients.extend(template["variable_ingredients"][variation])
    
    # Sometimes add optional ingredients
    if random.random() < 0.3:
        ingredients.append(random.choice(OPTIONAL_INGREDIENTS))
    
    # Generate cooking time
    time_min, time_max = template["time_range"]
    cooking_time = random.randint(time_min, time_max)
    
    # Create title and URL
    full_title = f"{template['base_title']} {variation}"
    url_slug = full_title.lower().replace(" ", "-").replace("ą", "a").replace("ę", "e").replace("ł", "l").replace("ć", "c").replace("ś", "s").replace("ź", "z").replace("ż", "z").replace("ń", "n")
    
    recipe = {
        "title": full_title.title(),
        "source": random.choice(SOURCES),
        "url": f"https://{random.choice(SOURCES)}/przepis/{url_slug}",
        "meal_type": meal_type,
        "time_minutes": cooking_time,
        "image_url": None,
        "tags": template["tags"].copy(),
        "steps_excerpt": f"Przepis na {full_title.lower()}. Idealny na {meal_type}.",
        "ingredients": list(set(ingredients))  # Remove duplicates
    }
    
    # Add some variety to tags
    if random.random() < 0.4:
        extra_tags = ["domowe", "szybkie", "łatwe", "smaczne", "rodzinne"]
        recipe["tags"].append(random.choice(extra_tags))
    
    return recipe


def create_expanded_recipes(count: int = 500) -> List[Dict]:
    """Create expanded set of Polish recipes."""
    recipes = []
    recipe_id = 1
    
    # Calculate distribution
    meal_types = list(RECIPE_TEMPLATES.keys())
    recipes_per_type = count // len(meal_types)
    remainder = count % len(meal_types)
    
    print(f"Generating {count} recipes...")
    
    for i, meal_type in enumerate(meal_types):
        # Add remainder to first meal types
        target_count = recipes_per_type + (1 if i < remainder else 0)
        templates = RECIPE_TEMPLATES[meal_type]
        
        print(f"  {meal_type}: {target_count} recipes")
        
        for _ in range(target_count):
            template = random.choice(templates)
            recipe = generate_recipe(template, meal_type, recipe_id)
            recipes.append(recipe)
            recipe_id += 1
    
    return recipes


def normalize_recipes(recipes: List[Dict]) -> List[Dict]:
    """Normalize ingredients in recipes."""
    for recipe in recipes:
        normalized_ingredients = []
        for ingredient in recipe.get('ingredients', []):
            normalized = normalize_ingredient(ingredient)
            normalized_ingredients.append(normalized)
        
        recipe['normalized_ingredients'] = normalized_ingredients
    
    return recipes


def main():
    """Main generation function."""
    count = 500
    if len(sys.argv) > 1:
        count = int(sys.argv[1])
    
    print(f"Creating {count} Polish recipes for Amciu Day...")
    
    recipes = create_expanded_recipes(count)
    recipes = normalize_recipes(recipes)
    
    # Save to JSON
    output_dir = Path(__file__).parent / "out"
    output_dir.mkdir(exist_ok=True)
    
    output_file = output_dir / "recipes_expanded.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            "recipes": recipes,
            "count": len(recipes),
            "generated_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }, f, ensure_ascii=False, indent=2)
    
    print(f"Generated {len(recipes)} recipes and saved to {output_file}")
    
    # Show statistics
    meal_counts = {}
    ingredient_counts = {}
    
    for recipe in recipes:
        meal_type = recipe.get('meal_type', 'unknown')
        meal_counts[meal_type] = meal_counts.get(meal_type, 0) + 1
        
        for ingredient in recipe.get('ingredients', []):
            ingredient_counts[ingredient] = ingredient_counts.get(ingredient, 0) + 1
    
    print("\nMeal type distribution:")
    for meal_type, count in meal_counts.items():
        print(f"  {meal_type}: {count}")
    
    print(f"\nTotal unique ingredients: {len(ingredient_counts)}")
    print("Most common ingredients:")
    sorted_ingredients = sorted(ingredient_counts.items(), key=lambda x: x[1], reverse=True)
    for ingredient, count in sorted_ingredients[:15]:
        print(f"  {ingredient}: {count} recipes")


if __name__ == "__main__":
    main()