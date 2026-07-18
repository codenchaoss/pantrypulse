from typing import Dict, Any, List

class MenuAdapter:
    """
    Transforms the Restaurant Action Plan into the AI Menu Planner module payload.
    """
    @staticmethod
    def adapt(plan: Dict[str, Any]) -> Dict[str, Any]:
        menu = plan.get("menu") or {}
        pricing_list = plan.get("pricing") or []
        descriptions_list = (plan.get("description") or {}).get("descriptions", [])
        
        # Build mapping dictionaries
        prices_by_dish = {p.get("dish"): p for p in pricing_list if p.get("dish")}
        descs_by_dish = {d.get("dish"): d.get("description") for d in descriptions_list if d.get("dish")}
        
        specials = []
        for item in menu.get("special_menu", []):
            dish_name = item.get("dish")
            price_info = prices_by_dish.get(dish_name, {})
            
            specials.append({
                "dish": dish_name,
                "priority": item.get("priority", "MEDIUM"),
                "preparation_time_minutes": item.get("preparation_time", 30),
                "description": descs_by_dish.get(dish_name, "Tasty daily special dish."),
                "ingredient_cost": price_info.get("ingredient_cost", 150.0),
                "selling_price": price_info.get("recommended_price", 400),
                "estimated_profit": price_info.get("estimated_profit", 250),
                "margin_percentage": price_info.get("profit_margin", 60),
                "roi_tier": price_info.get("category", "MEDIUM")
            })

        return {
            "menu_specials": specials,
            "specials_count": len(specials),
            "optimized_at_status": plan.get("workflow_status", "unknown")
        }
