import json
import os
from typing import Dict, List

def load_synonyms() -> Dict[str, List[str]]:
    current_dir = os.path.dirname(__file__)
    with open(os.path.join(current_dir, 'ingredients.json'), 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data['synonyms']

SYNONYMS = load_synonyms()

def normalize_ingredient(name: str) -> str:
    """Normalize ingredient name to canonical form."""
    normalized = name.lower().strip()
    
    # Check if this is a synonym and map to base form
    for base, synonyms in SYNONYMS.items():
        if normalized in synonyms or base == normalized:
            return base
    
    # Basic singularization (very simple Polish rules)
    if normalized.endswith('y') and len(normalized) > 2:
        return normalized[:-1]
    if normalized.endswith('i') and len(normalized) > 2:
        return normalized[:-1]
    if normalized.endswith('ów') and len(normalized) > 3:
        return normalized[:-2]
    
    return normalized