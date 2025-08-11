#!/usr/bin/env python3
"""
Scraping tool for Amciu Day recipes.
Creates sample Polish recipes for development and testing.
"""

import json
import sys
import time
from pathlib import Path
from typing import List, Dict

# Add shared package to path
sys.path.append(str(Path(__file__).parent.parent.parent / "packages" / "shared"))
from normalization import normalize_ingredient


def create_expanded_recipes(count: int = 500) -> List[Dict]:
    """Create expanded set of Polish recipes."""
    import random
    
    # Base recipe templates with variations
    base_recipes = {
        "breakfast": [
        # Breakfast recipes
        {
            "title": "Naleśniki z serem",
            "source": "centrumrespo.pl",
            "url": "https://centrumrespo.pl/przepis/nalesniki-z-serem",
            "meal_type": "breakfast",
            "time_minutes": 25,
            "image_url": None,
            "tags": ["polska kuchnia", "tradycyjne", "słodkie"],
            "steps_excerpt": "Klasyczne naleśniki z twarogiem. Idealne na śniadanie dla całej rodziny.",
            "ingredients": ["mąka", "mleko", "jajka", "ser biały", "cukier", "sól", "masło"]
        },
        {
            "title": "Owsianka z owocami",
            "source": "kwestiasmaku.com",
            "url": "https://kwestiasmaku.com/przepis/owsianka-owocami",
            "meal_type": "breakfast",
            "time_minutes": 10,
            "image_url": None,
            "tags": ["zdrowe", "owoce", "śniadanie"],
            "steps_excerpt": "Zdrowa owsianka z sezonowymi owocami. Pełnowartościowe śniadanie.",
            "ingredients": ["płatki owsiane", "mleko", "miód", "jabłko", "banany", "jagody", "orzechy"]
        },
        {
            "title": "Jajecznica z ziemniakami",
            "source": "centrumrespo.pl",
            "url": "https://centrumrespo.pl/przepis/jajecznica-ziemniaki",
            "meal_type": "breakfast",
            "time_minutes": 20,
            "image_url": None,
            "tags": ["tradycyjne", "jajka", "ziemniaki"],
            "steps_excerpt": "Syta jajecznica z gotowanymi ziemniakami. Klasyczne śniadanie na ciepło.",
            "ingredients": ["jajka", "ziemniaki", "cebula", "masło", "szynka", "szczypiorek", "sól", "pieprz"]
        },
        {
            "title": "Tosty z awokado",
            "source": "kwestiasmaku.com",
            "url": "https://kwestiasmaku.com/przepis/tosty-awokado",
            "meal_type": "breakfast",
            "time_minutes": 10,
            "image_url": None,
            "tags": ["zdrowe", "awokado", "szybkie"],
            "steps_excerpt": "Modne tosty z awokado i jajkiem. Zdrowe i syte śniadanie.",
            "ingredients": ["chleb pełnoziarnisty", "awokado", "jajko", "cytryna", "pomidor", "sól", "pieprz", "rukola"]
        },
        {
            "title": "Pancakes amerykańskie",
            "source": "centrumrespo.pl",
            "url": "https://centrumrespo.pl/przepis/pancakes-amerykanskie",
            "meal_type": "breakfast",
            "time_minutes": 20,
            "image_url": None,
            "tags": ["słodkie", "amerykańskie", "puszyste"],
            "steps_excerpt": "Puszyste pancakes jak z amerykańskiego filmu. Idealne na leniwą niedzielę.",
            "ingredients": ["mąka", "mleko", "jajka", "cukier", "proszek do pieczenia", "masło", "syrop klonowy", "jagody"]
        },

        # Lunch recipes
        {
            "title": "Kotlet schabowy z ziemniakami",
            "source": "kwestiasmaku.com",
            "url": "https://kwestiasmaku.com/przepis/kotlet-schabowy",
            "meal_type": "lunch",
            "time_minutes": 45,
            "image_url": None,
            "tags": ["polska kuchnia", "mięso", "obiad"],
            "steps_excerpt": "Tradycyjny kotlet schabowy w panierce, podawany z ziemniakami i mizerią.",
            "ingredients": ["schab", "jajka", "mąka", "bułka tarta", "ziemniaki", "ogórek kiszony", "sól", "pieprz"]
        },
        {
            "title": "Pierogi ruskie",
            "source": "centrumrespo.pl",
            "url": "https://centrumrespo.pl/przepis/pierogi-ruskie",
            "meal_type": "lunch",
            "time_minutes": 60,
            "image_url": None,
            "tags": ["polska kuchnia", "tradycyjne", "ziemniaki"],
            "steps_excerpt": "Klasyczne pierogi z nadzieniem ziemniaczano-serowym. Prawdziwa polska tradycja.",
            "ingredients": ["mąka", "jajka", "ziemniaki", "ser biały", "cebula", "masło", "śmietana", "sól"]
        },
        {
            "title": "Gulasz węgierski",
            "source": "kwestiasmaku.com",
            "url": "https://kwestiasmaku.com/przepis/gulasz-wegierski",
            "meal_type": "lunch",
            "time_minutes": 90,
            "image_url": None,
            "tags": ["mięso", "papryka", "długo gotowane"],
            "steps_excerpt": "Aromatyczny gulasz z wołowiną i papryką. Długo duszony dla pełni smaku.",
            "ingredients": ["wołowina", "cebula", "papryka czerwona", "pomidory", "papryka słodka", "czosnek", "bulion", "sól"]
        },
        {
            "title": "Ryba w cieście",
            "source": "centrumrespo.pl",
            "url": "https://centrumrespo.pl/przepis/ryba-ciescie",
            "meal_type": "lunch",
            "time_minutes": 35,
            "image_url": None,
            "tags": ["ryba", "smażone", "tradycyjne"],
            "steps_excerpt": "Chrupiąca ryba w cieście naleśnikowym. Klasyczne danie na piątek.",
            "ingredients": ["filet z ryby", "mąka", "jajka", "mleko", "olej", "cytryna", "sól", "pieprz", "koper"]
        },
        {
            "title": "Kotlety mielone",
            "source": "kwestiasmaku.com",
            "url": "https://kwestiasmaku.com/przepis/kotlety-mielone",
            "meal_type": "lunch",
            "time_minutes": 30,
            "image_url": None,
            "tags": ["mięso mielone", "tradycyjne", "obiad"],
            "steps_excerpt": "Soczyste kotlety mielone z cebulą i bułką. Domowy smak z dzieciństwa.",
            "ingredients": ["mięso mielone", "jajka", "bułka", "mleko", "cebula", "czosnek", "pietruszka", "sól", "pieprz"]
        },

        # Snack recipes
        {
            "title": "Kanapki z pastą jajeczną",
            "source": "centrumrespo.pl",
            "url": "https://centrumrespo.pl/przepis/kanapki-pasta-jajeczna",
            "meal_type": "snack",
            "time_minutes": 15,
            "image_url": None,
            "tags": ["szybkie danie", "przekąska", "jajka"],
            "steps_excerpt": "Proste i syte kanapki z domową pastą jajeczną. Idealne na drugie śniadanie.",
            "ingredients": ["jajka", "chleb", "masło", "majonezy", "szczypiorek", "sól", "pieprz"]
        },
        {
            "title": "Smoothie zielone",
            "source": "kwestiasmaku.com",
            "url": "https://kwestiasmaku.com/przepis/smoothie-zielone",
            "meal_type": "snack",
            "time_minutes": 5,
            "image_url": None,
            "tags": ["zdrowe", "warzywa", "napój"],
            "steps_excerpt": "Odżywczy napój pełen witamin. Idealny na przekąskę między posiłkami.",
            "ingredients": ["szpinak", "banan", "jabłko", "ogórek", "imbir", "cytryna", "woda"]
        },
        {
            "title": "Muffiny z jagodami",
            "source": "centrumrespo.pl",
            "url": "https://centrumrespo.pl/przepis/muffiny-jagody",
            "meal_type": "snack",
            "time_minutes": 30,
            "image_url": None,
            "tags": ["słodkie", "owoce", "pieczenie"],
            "steps_excerpt": "Puszyste muffiny z świeżymi jagodami. Idealne na popołudniową przekąskę.",
            "ingredients": ["mąka", "cukier", "jajka", "masło", "mleko", "jagody", "proszek do pieczenia", "wanilia"]
        },
        {
            "title": "Hummus z warzywami",
            "source": "kwestiasmaku.com",
            "url": "https://kwestiasmaku.com/przepis/hummus-warzywa",
            "meal_type": "snack",
            "time_minutes": 15,
            "image_url": None,
            "tags": ["zdrowe", "warzywa", "wegańskie"],
            "steps_excerpt": "Kremowy hummus z tahini podawany z paluszkami warzyw. Zdrowa przekąska.",
            "ingredients": ["ciecierzyca", "tahini", "czosnek", "cytryna", "oliwa", "marchew", "papryka", "ogórek", "sól"]
        },
        {
            "title": "Ciasteczka owsiane",
            "source": "centrumrespo.pl",
            "url": "https://centrumrespo.pl/przepis/ciasteczka-owsiane",
            "meal_type": "snack",
            "time_minutes": 25,
            "image_url": None,
            "tags": ["słodkie", "owsiane", "pieczenie"],
            "steps_excerpt": "Chrupiące ciasteczka owsiane z rodzynkami. Idealne do herbaty.",
            "ingredients": ["płatki owsiane", "mąka", "masło", "cukier", "jajko", "rodzynki", "cynamon", "proszek do pieczenia"]
        },

        # Dinner recipes
        {
            "title": "Sałatka grecka",
            "source": "kwestiasmaku.com",
            "url": "https://kwestiasmaku.com/przepis/salatka-grecka",
            "meal_type": "dinner",
            "time_minutes": 20,
            "image_url": None,
            "tags": ["zdrowe", "warzywa", "kolacja"],
            "steps_excerpt": "Świeża sałatka grecka z fetą i oliwkami. Lekka kolacja pełna witamin.",
            "ingredients": ["pomidory", "ogórek", "papryka", "cebula", "ser feta", "oliwki", "oliwa", "oregano"]
        },
        {
            "title": "Zupa krem z brokułów",
            "source": "centrumrespo.pl",
            "url": "https://centrumrespo.pl/przepis/zupa-krem-brokulow",
            "meal_type": "dinner",
            "time_minutes": 35,
            "image_url": None,
            "tags": ["zdrowe", "warzywa", "zupa"],
            "steps_excerpt": "Kremowa zupa z brokułów z dodatkiem śmietany. Lekka i syta kolacja.",
            "ingredients": ["brokuły", "cebula", "czosnek", "bulion warzywny", "śmietana", "masło", "sól", "pieprz"]
        },
        {
            "title": "Wrap z kurczakiem",
            "source": "kwestiasmaku.com",
            "url": "https://kwestiasmaku.com/przepis/wrap-kurczak",
            "meal_type": "dinner",
            "time_minutes": 25,
            "image_url": None,
            "tags": ["kurczak", "warzywa", "szybkie"],
            "steps_excerpt": "Kolorowy wrap z grillowanym kurczakiem i świeżymi warzywami. Lekka kolacja.",
            "ingredients": ["tortilla", "kurczak", "sałata", "pomidor", "ogórek", "papryka", "sos czosnkowy", "ser"]
        },
        {
            "title": "Risotto z grzybami",
            "source": "centrumrespo.pl",
            "url": "https://centrumrespo.pl/przepis/risotto-grzyby",
            "meal_type": "dinner",
            "time_minutes": 40,
            "image_url": None,
            "tags": ["ryż", "grzyby", "kremowe"],
            "steps_excerpt": "Kremowe risotto z grzybami leśnymi. Elegancka kolacja o bogatym smaku.",
            "ingredients": ["ryż arborio", "grzyby", "cebula", "czosnek", "wino białe", "bulion", "parmezan", "masło", "pietruszka"]
        },
        {
            "title": "Łosoś z warzywami",
            "source": "kwestiasmaku.com",
            "url": "https://kwestiasmaku.com/przepis/losos-warzywa",
            "meal_type": "dinner",
            "time_minutes": 35,
            "image_url": None,
            "tags": ["ryba", "zdrowe", "pieczone"],
            "steps_excerpt": "Pieczony łosoś z kolorową mieszanką warzyw. Zdrowa i elegancka kolacja.",
            "ingredients": ["łosoś", "brokuły", "marchew", "cukinia", "papryka", "oliwa", "cytryna", "czosnek", "tymianek"]
        }
    ]
    
    return recipes


def normalize_recipes(recipes: List[Dict]) -> List[Dict]:
    """Normalize ingredients in recipes."""
    for recipe in recipes:
        normalized_ingredients = []
        for ingredient in recipe.get('ingredients', []):
            normalized = normalize_ingredient(ingredient)
            normalized_ingredients.append(normalized)
        
        recipe['ingredients'] = recipe.get('ingredients', [])
        recipe['normalized_ingredients'] = normalized_ingredients
    
    return recipes


def main():
    """Main scraping function."""
    print("Creating sample recipes for Amciu Day...")
    
    recipes = create_sample_recipes()
    recipes = normalize_recipes(recipes)
    
    # Save to JSON
    output_dir = Path(__file__).parent / "out"
    output_dir.mkdir(exist_ok=True)
    
    output_file = output_dir / "recipes.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            "recipes": recipes,
            "count": len(recipes),
            "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }, f, ensure_ascii=False, indent=2)
    
    print(f"Created {len(recipes)} recipes and saved to {output_file}")
    
    # Show meal type distribution
    meal_counts = {}
    for recipe in recipes:
        meal_type = recipe.get('meal_type', 'unknown')
        meal_counts[meal_type] = meal_counts.get(meal_type, 0) + 1
    
    print("\nMeal type distribution:")
    for meal_type, count in meal_counts.items():
        print(f"  {meal_type}: {count}")


if __name__ == "__main__":
    main()