from typing import List, Dict, Any
from app.prompts.system_prompt import build_system_prompt

def build_description_prompt(dishes: List[Dict[str, Any]], context: str) -> str:
    """
    Constructs the prompt for drafting premium restaurant menu descriptions.
    """
    system_rules = build_system_prompt()
    
    dishes_strs = []
    for item in dishes:
        name = item.get("dish", "")
        cat = item.get("category", "")
        cat_str = f" (Category: {cat})" if cat else ""
        dishes_strs.append(f"- {name}{cat_str}")
    dishes_block = "\n".join(dishes_strs)
    
    prompt = (
        f"{system_rules}\n\n"
        "=== MENU DESCRIPTION RULES ===\n"
        "1. Write an elegant, appealing, and mouth-watering restaurant-quality culinary description for the given menu items.\n"
        "2. Keep each description short (exactly 30 to 60 words).\n"
        "3. Highlight flavor profiles, cooking methods, and premium texture while avoiding emojis, marketing hype, or false health claims.\n"
        "4. Return recommendations strictly in a structured JSON format containing the 'descriptions' list.\n"
        "5. Each item in the 'descriptions' list must strictly contain these keys:\n"
        "   - 'dish' (str, matching the input dish name exactly)\n"
        "   - 'description' (str, the generated menu description)\n"
        "   - 'tone' (str, e.g. 'Premium')\n"
        "   - 'language' (str, e.g. 'English', 'Telugu', or 'Tenglish')\n"
        "6. Output ONLY a valid JSON object starting with { and ending with }. Do NOT include any markdown formatting wrappers like ```json or any other text before/after the JSON.\n"
        "7. Ensure descriptions are original and do not copy metadata titles, website references, links, or blog headers from the context.\n\n"
        
        "=== RETRIEVED RECIPE KNOWLEDGE ===\n"
        f"{context}\n\n"
        
        "=== TARGET DISHES ===\n"
        f"{dishes_block}\n\n"
        
        "Structured JSON Descriptions:"
    )
    return prompt
