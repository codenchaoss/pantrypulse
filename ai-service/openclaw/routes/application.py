import logging
from fastapi import APIRouter, Depends
from typing import Dict, Any

from app.schemas.response import ApiResponse
from openclaw.api.orchestrate import OrchestrationResponseData
from openclaw.workflows.workflow_manager import OpenClawWorkflowManager

router = APIRouter()
logger = logging.getLogger("app.api")

def get_workflow_manager() -> OpenClawWorkflowManager:
    return OpenClawWorkflowManager(base_url="http://127.0.0.1:8000")

@router.post("/workflow/publish", response_model=ApiResponse[Dict[str, Any]])
def publish_workflow(
    plan: OrchestrationResponseData,
    manager: OpenClawWorkflowManager = Depends(get_workflow_manager)
):
    """
    Publishes the Restaurant Action Plan. Translates the plan into module-specific payloads.
    """
    logger.info("ApplicationRouter: Exposing workflow publish trigger.")
    plan_dict = plan.dict()
    output = manager.publish_workflow_result(plan_dict)
    return ApiResponse(data=output)

@router.post("/application/update", response_model=ApiResponse[Dict[str, Any]])
def update_application(
    plan: OrchestrationResponseData,
    manager: OpenClawWorkflowManager = Depends(get_workflow_manager)
):
    """
    Hook endpoint to trigger application module updates with the Restaurant Action Plan.
    """
    logger.info("ApplicationRouter: Exposing application update trigger hook.")
    plan_dict = plan.dict()
    output = manager.publish_workflow_result(plan_dict)
    return ApiResponse(data=output)
