import logging
from fastapi import APIRouter, Depends
from app.schemas.request import OptimizationRequest
from app.schemas.response import ApiResponse, OptimizationResponseData
from app.services.inventory_optimizer_service import InventoryOptimizerService

router = APIRouter()
logger = logging.getLogger("app.api")

_optimizer_service_instance = None

def get_optimizer_service() -> InventoryOptimizerService:
    global _optimizer_service_instance
    if _optimizer_service_instance is None:
        _optimizer_service_instance = InventoryOptimizerService()
    return _optimizer_service_instance

@router.post("/optimization", response_model=ApiResponse[OptimizationResponseData])
def optimize_inventory(request: OptimizationRequest, service: InventoryOptimizerService = Depends(get_optimizer_service)):
    """
    Exposes flagship ingredient usage and food waste optimization planning.
    Receives current inventory counts and compiles production priorities.
    """
    logger.info(f"OptimizationController: Received replenishment optimization request for {len(request.inventory)} items")
    
    # Translate schema models to dictionary representations
    inventory_items = [item.dict() for item in request.inventory]
    result = service.optimize_inventory(inventory_items)
    
    unit_val = request.inventory[0].unit if request.inventory else "kg"
    
    response_data = OptimizationResponseData(
        recommended_dishes=result.get("recommended_dishes", []),
        inventory_usage=result.get("inventory_usage", []),
        estimated_revenue=result.get("estimated_revenue", 0),
        currency=result.get("currency", "INR"),
        waste_saved={
            "value": result.get("waste_saved", 0.0),
            "unit": unit_val
        },
        remaining_inventory=result.get("remaining_inventory", []),
        purchase_required=result.get("purchase_required", False),
        purchase_items=result.get("purchase_items", []),
        reason=result.get("reason", ""),
        language=result.get("language", "English")
    )
    return ApiResponse(data=response_data)
