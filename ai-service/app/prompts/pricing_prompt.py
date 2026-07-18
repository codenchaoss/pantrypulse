from app.prompts.system_prompt import build_system_prompt

def build_pricing_prompt(dish: str, cost: float, context: str) -> str:
    """
    Constructs the prompt for calculating selling prices and profit margins.
    """
    system_rules = build_system_prompt()
    
    prompt = (
        f"{system_rules}\n\n"
        "=== PRICING & PROFIT SUGGESTION RULES ===\n"
        "1. Recommend a highly realistic and profitable selling price for the recipe item based on its cost, cuisine type, popularity, market demand, and retrieved market pricing context.\n"
        "2. Do not use static markup formulas; analyze the dish classification, premium vs economy positioning, and demand popularity.\n"
        "3. Return the response strictly in a structured JSON format containing these keys:\n"
        "   - 'dish' (str, matching the input dish name exactly)\n"
        "   - 'recommended_price' (int, suggested menu price in rupees)\n"
        "   - 'pricing_strategy' (str, e.g. 'Premium', 'Value', or 'Standard' pricing strategy)\n"
        "   - 'market_position' (str, e.g. 'Upscale', 'Budget', or 'Mid-range' market positioning)\n"
        "   - 'price_confidence' (int, confidence score from 0 to 100 for the suggested price)\n"
        "   - 'language' (str, the language detected/used: 'English', 'Telugu', or 'Tenglish')\n"
        "4. Output ONLY a valid JSON object starting with { and ending with }. Do NOT include any markdown formatting wrappers like ```json or any other text before/after the JSON.\n\n"
        
        "=== RETRIEVED FINANCIAL KNOWLEDGE ===\n"
        f"{context}\n\n"
        
        "=== RECIPE DETAIL ===\n"
        f"- Dish: {dish}\n"
        f"- Ingredient Cost: {cost}\n\n"
        
        "Structured JSON Pricing Recommendation:"
    )
    return prompt
