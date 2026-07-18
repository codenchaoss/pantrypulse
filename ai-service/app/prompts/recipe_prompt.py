from typing import List
from app.prompts.system_prompt import build_system_prompt

def build_recipe_prompt(ingredients: List[str], context: str) -> str:
    """
    Constructs the prompt for recipe recommendations.
    """
    system_rules = build_system_prompt()
    ingredients_str = ", ".join(ingredients)
    
    prompt = (
        f"{system_rules}\n\n"
        "=== RECIPE RECOMMENDATION RULES ===\n"
        "1. Recommend a maximum of 3 recipes based on the available ingredients and retrieved recipes in context.\n"
        "2. Return the recommendations strictly in a structured JSON format containing the 'recipes' list.\n"
        "3. Each recipe object in the 'recipes' list must strictly contain these keys:\n"
        "   - 'recipe_id' (str, unique identifier from retrieved context (e.g., REC001) or R100X style if not found)\n"
        "   - 'recipe_name' (str)\n"
        "   - 'description' (str, brief culinary description. Avoid website names, scrapings, urls, or author bios)\n"
        "   - 'matched_ingredients' (list of str, ingredients provided by user that are used)\n"
        "   - 'missing_ingredients' (list of str, ingredients required by the recipe but missing from user's list)\n"
        "   - 'match_percentage' (int, match percentage based on matched/total ingredients)\n"
        "   - 'preparation_time_minutes' (int, prep time in minutes)\n"
        "   - 'difficulty' (str, e.g. 'Easy', 'Medium', 'Hard')\n"
        "   - 'estimated_calories' (int, calories count per serving)\n"
        "   - 'reason_for_recommendation' (str, explain why this recipe was recommended and how it helps minimize BOH waste)\n"
        "4. Rank the recommendations by match percentage (descending) and simplicity.\n"
        "5. Output ONLY a valid JSON object starting with { and ending with }. Do NOT include any markdown formatting wrappers like ```json or any other text before/after the JSON.\n\n"
        
        "=== RETRIEVED RECIPES KNOWLEDGE ===\n"
        f"{context}\n\n"
        
        "=== AVAILABLE INGREDIENTS ===\n"
        f"Available: {ingredients_str}\n\n"
        
        "Structured JSON Recommendations:"
    )
    return prompt
