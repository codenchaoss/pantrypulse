from typing import Dict, Any, List

class DashboardAdapter:
    """
    Transforms the Restaurant Action Plan into the Dashboard module payload.
    """
    @staticmethod
    def adapt(plan: Dict[str, Any]) -> Dict[str, Any]:
        opt = plan.get("optimization") or {}
        rec = plan.get("recipe") or {}
        
        # Extract optimization summary
        opt_summary = {
            "dishes_count": len(opt.get("recommended_dishes", [])),
            "waste_saved_kg": opt.get("waste_saved", 0.0),
            "revenue_projection": opt.get("estimated_revenue", 0),
            "purchase_required": opt.get("purchase_required", False)
        }
        
        # Extract recipe details
        recipes = []
        for r in rec.get("recipes", []):
            recipes.append({
                "recipe_name": r.get("recipe_name"),
                "match_percentage": r.get("match_percentage", 0),
                "difficulty": r.get("difficulty", "Medium")
            })

        return {
            "optimization_summary": opt_summary,
            "recommended_recipes": recipes,
            "workflow_status": plan.get("workflow_status", "unknown"),
            "warnings_count": len(plan.get("warnings", [])),
            "warnings_list": plan.get("warnings", [])
        }
