import logging
from fastapi import APIRouter, Depends
from app.schemas.request import PricingRequest
from app.schemas.response import ApiResponse, PricingResponseData
from app.services.pricing_service import PricingService

router = APIRouter()
logger = logging.getLogger("app.api")

def get_pricing_service() -> PricingService:
    return PricingService()

@router.post("/pricing", response_model=ApiResponse[PricingResponseData])
def suggest_pricing(request: PricingRequest, service: PricingService = Depends(get_pricing_service)):
    """
    Exposes profit-based pricing suggestions. Receives dish and raw ingredient cost, estimating selling options.
    """
    logger.info(f"PricingController: Received request for pricing suggestions for dish: '{request.dish}' | Cost: {request.ingredient_cost}")
    
    result = service.generate_pricing_suggestion(request.dish, request.ingredient_cost)
    
    response_data = PricingResponseData(
        dish=result.get("dish", ""),
        ingredient_cost=result.get("ingredient_cost", 0.0),
        recommended_price=result.get("recommended_price", 0),
        estimated_profit=result.get("estimated_profit", 0),
        profit_margin=result.get("profit_margin", 0),
        category=result.get("category", "LOW"),
        reason=result.get("reason", "")
    )
    return ApiResponse(data=response_data)
