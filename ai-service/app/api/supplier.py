import logging
from fastapi import APIRouter, Depends
from app.schemas.request import SupplierRequest
from app.schemas.response import ApiResponse, SupplierResponseData
from app.services.supplier_service import SupplierService

router = APIRouter()
logger = logging.getLogger("app.api")

def get_supplier_service() -> SupplierService:
    return SupplierService()

@router.post("/supplier", response_model=ApiResponse[SupplierResponseData])
def generate_supplier_message(request: SupplierRequest, service: SupplierService = Depends(get_supplier_service)):
    """
    Exposes supplier message drafting. Drafts professional purchase requests for low-stock items.
    """
    logger.info(f"SupplierController: Received supplier replenishment request for {request.required_quantity} of {request.ingredient}")
    result = service.generate_supplier_message(
        ingredient=request.ingredient,
        quantity=request.required_quantity,
        supplier_name=request.supplier_name,
        required_date=request.required_date,
        ingredients=request.ingredients,
        restaurant_name=request.restaurant_name,
        contact_person=request.contact_person,
        supplier_email=request.supplier_email,
        supplier_phone=request.supplier_phone,
        urgency_level=request.urgency_level,
        language_preference=request.language_preference
    )
    
    response_data = SupplierResponseData(
        supplier_name=result.get("supplier_name", ""),
        ingredient=result.get("ingredient", ""),
        message=result.get("message", ""),
        language=result.get("language", ""),
        subject=result.get("subject"),
        order_id=result.get("order_id"),
        urgency=result.get("urgency")
    )
    return ApiResponse(data=response_data)
