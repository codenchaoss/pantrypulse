import logging
from fastapi import APIRouter, Depends
from typing import List, Optional
from pydantic import BaseModel, Field

# FastAPI schemas
from app.schemas.request import OptimizationRequest
from app.schemas.response import (
    ApiResponse, OptimizationResponseData, RecipeResponseData, MenuResponseData,
    PricingResponseData, DescriptionResponseData, SupplierResponseData
)

# OpenClaw orchestrator
from openclaw.workflows.workflow_manager import OpenClawWorkflowManager

router = APIRouter()
logger = logging.getLogger("app.api")

class OrchestrationResponseData(BaseModel):
    optimization: Optional[OptimizationResponseData] = Field(None, description="Optimization skill data")
    recipe: Optional[RecipeResponseData] = Field(None, description="Recipe skill suggestions")
    menu: Optional[MenuResponseData] = Field(None, description="Menu specials planning suggestions")
    pricing: List[PricingResponseData] = Field(default_factory=list, description="Pricing recommendations list")
    description: Optional[DescriptionResponseData] = Field(None, description="Menu description data")
    supplier: List[SupplierResponseData] = Field(default_factory=list, description=" replenishment order messages list")
    warnings: List[str] = Field(default_factory=list, description="Warnings generated during step triggers")
    workflow_status: str = Field(..., description="Status of the workflow execution (completed | partial_success)")

def get_workflow_manager() -> OpenClawWorkflowManager:
    # Trigger requests on local host
    return OpenClawWorkflowManager(base_url="http://127.0.0.1:8000")

@router.post("/orchestrate", response_model=ApiResponse[OrchestrationResponseData])
def trigger_orchestration(
    request: OptimizationRequest,
    manager: OpenClawWorkflowManager = Depends(get_workflow_manager)
):
    """
    Exposes workflow orchestration. Accepts inventory event updates and triggers all 6 skills in sequence.
    """
    logger.info(f"OrchestrateController: Triggering BOH workflows for {len(request.inventory)} inventory items.")
    
    # Translate inventory pydantic items to dictionary
    inventory_items = [item.dict() for item in request.inventory]
    result = manager.run_restaurant_optimization_workflow(inventory_items)
    
    response_data = OrchestrationResponseData(
        optimization=result.get("optimization"),
        recipe=result.get("recipe"),
        menu=result.get("menu"),
        pricing=result.get("pricing", []),
        description=result.get("description"),
        supplier=result.get("supplier", []),
        warnings=result.get("warnings", []),
        workflow_status=result.get("workflow_status", "completed")
    )
    return ApiResponse(data=response_data)
