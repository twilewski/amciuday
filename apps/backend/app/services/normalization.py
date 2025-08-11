import json
import os
from typing import Dict, List

def load_synonyms() -> Dict[str, List[str]]:
    shared_dir = os.path.join(os.path.dirname(__file__), "../../../..", "packages", "shared")
    with open(os.path.join(shared_dir, 'ingredients.json'), 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data['synonyms']

SYNONYMS = load_synonyms()

def normalize_ingredient(name: str) -> str:
    """Normalize ingredient name to canonical form."""
    normalized = name.lower().strip()
    
    for base, synonyms in SYNONYMS.items():
        if normalized in synonyms or base == normalized:
            return base
    
    if normalized.endswith('y') and len(normalized) > 2:
        return normalized[:-1]
    if normalized.endswith('i') and len(normalized) > 2:
        return normalized[:-1]
    if normalized.endswith('ów') and len(normalized) > 3:
        return normalized[:-2]
    
    return normalized