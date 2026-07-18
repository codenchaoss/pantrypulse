from typing import List, Dict, Any
from app.prompts.system_prompt import build_system_prompt

def build_menu_prompt(inventory: List[Dict[str, Any]], context: str) -> str:
    """
    Constructs the prompt for daily menu recommendations based on expiring stock and profit margins.
    """
    system_rules = build_system_prompt()
    
    inv_strs = []
    for item in inventory:
        ingredient = item.get("ingredient", "unknown")
        quantity = item.get("quantity", "unknown")
        expiry = item.get("expiry_days", "unknown")
        inv_strs.append(f"- {ingredient}: Quantity={quantity}, Expires in={expiry} days")
    inv_block = "\n".join(inv_strs) if inv_strs else "No expiring inventory reported."
    
    prompt = (
        f"{system_rules}\n\n"
        "=== DAILY MENU OPTIMIZATION RULES ===\n"
        "1. Generate highly appealing, restaurant-quality daily specials.\n"
        "2. Prioritize inventory items that are closest to expiry (e.g. expiry_days is low) to eliminate food waste.\n"
        "3. Select recipes that yield high margins.\n"
        "4. Return recommendations strictly in a structured JSON format containing the 'special_menu' list (maximum of 5 menu items).\n"
        "5. Each item in the 'special_menu' list must strictly contain these keys:\n"
        "   - 'dish' (str, name of the menu dish)\n"
        "   - 'reason' (str, explanation of why this dish was chosen and how it utilizes expiring stock)\n"
        "   - 'matched_inventory' (list of str, ingredients utilized from expiring inventory)\n"
        "   - 'required_ingredients' (list of str, all ingredients required by the recipe)\n"
        "   - 'estimated_profit' (int, estimated profit margin in rupees, e.g. 450)\n"
        "   - 'priority' (str, priority based on inventory urgency: 'HIGH', 'MEDIUM', 'LOW')\n"
        "   - 'preparation_time' (int, prep time in minutes)\n"
        "   - 'difficulty' (str, e.g. 'Easy', 'Medium', 'Hard')\n"
        "   - 'confidence' (int, confidence score out of 100 representing recipe compatibility and feasibility)\n"
        "6. Rank the specials by priority (urgency of expiring ingredients) and profit.\n"
        "7. Output ONLY a valid JSON object starting with { and ending with }. Do NOT include any markdown formatting wrappers like ```json or any other text before/after the JSON.\n\n"
        
        "=== RETRIEVED MENU & RECIPE KNOWLEDGE ===\n"
        f"{context}\n\n"
        
        "=== EXPIRING INVENTORY STATUS ===\n"
        f"{inv_block}\n\n"
        
        "Structured JSON Daily Menu Specials:"
    )
    return prompt
