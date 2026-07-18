import logging
from fastapi import APIRouter, Depends
from app.schemas.request import MenuRequest
from app.schemas.response import ApiResponse, MenuResponseData
from app.services.menu_service import MenuService

router = APIRouter()
logger = logging.getLogger("app.api")

def get_menu_service() -> MenuService:
    return MenuService()

@router.post("/menu", response_model=ApiResponse[MenuResponseData])
def generate_menu(request: MenuRequest, service: MenuService = Depends(get_menu_service)):
    """
    Exposes menu generation. Analyzes expiring stock, cost/profit ratios, and suggests menu specials.
    """
    logger.info(f"MenuController: Received menu special request for stock items count: {len(request.inventory)}")
    
    inventory_list = [item.model_dump() for item in request.inventory]
    result = service.generate_menu(inventory_list, recipes=request.recipes)
    
    response_data = MenuResponseData(
        special_menu=result.get("special_menu", [])
    )
    return ApiResponse(data=response_data)
