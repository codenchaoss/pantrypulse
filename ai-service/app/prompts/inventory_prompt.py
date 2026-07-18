from typing import List, Dict, Any
from app.prompts.system_prompt import build_system_prompt

def build_inventory_prompt(
    inventory: List[Dict[str, Any]], 
    dishes_context: str, 
    context: str
) -> str:
    """
    Constructs the prompt for ingredient optimization and minimizing waste.
    """
    system_rules = build_system_prompt()
    
    inv_strs = []
    for item in inventory:
        ingredient = item.get("ingredient", "unknown")
        quantity = item.get("quantity", 0)
        unit = item.get("unit", "kg")
        expiry = item.get("expiry_days", 0)
        inv_strs.append(f"- {ingredient}: Stock={quantity} {unit}, Expiry={expiry} days")
    inv_block = "\n".join(inv_strs) if inv_strs else "No expiring inventory reported."
    
    prompt = (
        f"{system_rules}\n\n"
        "=== INVENTORY OPTIMIZATION & WASTE REDUCTION RULES ===\n"
        "1. Analyze the expiring inventory list and comparable restaurant context below.\n"
        "2. Review the candidate dishes that can be prepared: \n"
        f"{dishes_context}\n\n"
        "3. Provide optimization recommendation details. Suggest servings for each dish to minimize food waste.\n"
        "4. Enforce these specific rules for recommended dishes:\n"
        "   - Use clean, restaurant-friendly menu names (e.g. 'Garlic Bread with Tomato & Provolone' instead of 'Cherry Tomatoes On Provolone Garlic Bread Recipe', 'Cheesy Tomato Pie' instead of 'Chunky Tomato Cheese Pie').\n"
        "   - Assign 'HIGH' priority to dishes using ingredients expiring within 1 to 2 days.\n"
        "5. Return the response strictly in a structured JSON format containing these keys:\n"
        "   - 'recommended_dishes' (list of objects, each containing 'dish' (str), 'servings' (int), and 'priority' (str: 'HIGH' | 'MEDIUM' | 'LOW'))\n"
        "   - 'purchase_required' (bool, true if inventory is insufficient and restocking is required, else false)\n"
        "   - 'purchase_items' (list of objects, each containing 'ingredient' (str) and 'required_quantity' (str, e.g. '10 kg') for items running low or needing replenishment)\n"
        "   - 'reason' (str, a detailed BOH manager explanation of the optimization plan. You MUST explicitly state the actual ingredient expiry days (e.g. 'Tomatoes expire in 1 day and cheese in 2 days, so preparing tomato- and cheese-based dishes immediately will minimize waste and maximize revenue.'))\n"
        "   - 'language' (str, the language utilized for the reason text: 'English', 'Telugu', or 'Tenglish')\n"
        "6. Ensure the 'message' draft or 'reason' text strictly matches the detected language key.\n"
        "7. Output ONLY a valid JSON object starting with { and ending with }. Do NOT include any markdown formatting wrappers like ```json or any other text before/after the JSON.\n\n"
        
        "=== RETRIEVED RESTAURANT KNOWLEDGE ===\n"
        f"{context}\n\n"
        
        "=== EXPIRING INVENTORY TO OPTIMIZE ===\n"
        f"{inv_block}\n\n"
        
        "Structured JSON Inventory Optimization Plan:"
    )
    return prompt
