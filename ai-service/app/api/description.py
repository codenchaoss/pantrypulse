import logging
from fastapi import APIRouter, Depends
from app.schemas.request import DescriptionRequest
from app.schemas.response import ApiResponse, DescriptionResponseData
from app.services.description_service import DescriptionService

router = APIRouter()
logger = logging.getLogger("app.api")

def get_description_service() -> DescriptionService:
    return DescriptionService()

@router.post("/description", response_model=ApiResponse[DescriptionResponseData])
def generate_menu_descriptions(request: DescriptionRequest, service: DescriptionService = Depends(get_description_service)):
    """
    Exposes menu description generation. Receives target dishes list and drafts elegant description text.
    """
    logger.info(f"DescriptionController: Received request for description menu generation, item count: {len(request.dishes)}")
    
    dishes_list = [item.model_dump() for item in request.dishes]
    result = service.generate_descriptions(dishes_list)
    
    response_data = DescriptionResponseData(
        descriptions=result.get("descriptions", [])
    )
    return ApiResponse(data=response_data)
