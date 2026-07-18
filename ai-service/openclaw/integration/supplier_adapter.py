from typing import Dict, Any, List

class SupplierAdapter:
    """
    Transforms the Restaurant Action Plan into the Supplier Module payload.
    """
    @staticmethod
    def adapt(plan: Dict[str, Any]) -> Dict[str, Any]:
        supplier_list = plan.get("supplier") or []
        opt = plan.get("optimization") or {}
        
        drafts = []
        for s in supplier_list:
            drafts.append({
                "supplier_name": s.get("supplier_name", "Generic Supplier"),
                "ingredient": s.get("ingredient"),
                "suggested_message": s.get("message"),
                "language": s.get("language", "English")
            })

        purchase_required = opt.get("purchase_required", False)
        
        return {
            "supplier_replenishment_drafts": drafts,
            "purchase_required_flag": purchase_required,
            "drafts_count": len(drafts),
            "status": "pending_review"
        }
