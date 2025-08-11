import synonymsData from './ingredients.json';

export function normalizeIngredient(name: string): string {
  const normalized = name.toLowerCase().trim();
  
  // Check if this is a synonym and map to base form
  for (const [base, synonyms] of Object.entries(synonymsData.synonyms)) {
    if (synonyms.includes(normalized) || base === normalized) {
      return base;
    }
  }
  
  // Basic singularization (very simple Polish rules)
  if (normalized.endsWith('y') && normalized.length > 2) {
    return normalized.slice(0, -1);
  }
  if (normalized.endsWith('i') && normalized.length > 2) {
    return normalized.slice(0, -1);
  }
  if (normalized.endsWith('ów') && normalized.length > 3) {
    return normalized.slice(0, -2);
  }
  
  return normalized;
}