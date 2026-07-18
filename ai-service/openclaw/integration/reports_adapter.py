from datetime import datetime, timezone
from typing import Dict, Any, List

class ReportsAdapter:
    """
    Transforms the Restaurant Action Plan into the Reports module payload.
    """
    @staticmethod
    def adapt(plan: Dict[str, Any]) -> Dict[str, Any]:
        opt = plan.get("optimization") or {}
        menu = plan.get("menu") or {}
        pricing_list = plan.get("pricing") or []
        
        # Calculate summary statistics
        total_profit = sum(p.get("estimated_profit", 0) for p in pricing_list)
        avg_margin = 0
        if pricing_list:
            avg_margin = sum(p.get("profit_margin", 0) for p in pricing_list) // len(pricing_list)

        opt_summary = {
            "waste_saved_kg": opt.get("waste_saved", {}).get("value", 0.0) if isinstance(opt.get("waste_saved"), dict) else opt.get("waste_saved", 0.0),
            "estimated_revenue": opt.get("estimated_revenue", 0)
        }

        generated_specials = [item.get("dish") for item in menu.get("special_menu", []) if item.get("dish")]

        return {
            "report_timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "workflow_execution_metadata": {
                "status": plan.get("workflow_status", "unknown"),
                "warnings": plan.get("warnings", [])
            },
            "financial_summary": {
                "total_estimated_profit": total_profit,
                "average_margin_percentage": avg_margin
            },
            "optimization_summary": opt_summary,
            "menu_specials_list": generated_specials
        }
