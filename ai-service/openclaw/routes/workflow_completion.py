import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

from app.schemas.response import ApiResponse
from openclaw.api.orchestrate import OrchestrationResponseData
from openclaw.operations.completion_manager import WorkflowCompletionManager
from openclaw.operations.print_queue import PrintQueue
from openclaw.operations.workflow_status import WorkflowStatusTracker

router = APIRouter()
logger = logging.getLogger("app.api")

class WorkflowCompletionResponse(BaseModel):
    workflow_id: str
    status: str
    dashboard: str
    menu: str
    supplier: str
    reports: str
    print_job: Optional[Dict[str, Any]] = None
    warnings: List[str]

def get_completion_manager() -> WorkflowCompletionManager:
    return WorkflowCompletionManager()

def get_status_tracker() -> WorkflowStatusTracker:
    return WorkflowStatusTracker()

def get_print_queue() -> PrintQueue:
    return PrintQueue()

@router.post("/workflow/complete", response_model=ApiResponse[WorkflowCompletionResponse])
def complete_workflow(
    plan: OrchestrationResponseData,
    workflow_id: Optional[str] = Query(None, description="Optional workflow ID mapping"),
    manager: WorkflowCompletionManager = Depends(get_completion_manager)
):
    """
    Finalizes the workflow. Dispatches payloads to adapters and registers a print job.
    """
    logger.info("OperationsRouter: Triggering workflow completion.")
    plan_dict = plan.dict()
    output = manager.complete_workflow(plan_dict, workflow_id)
    return ApiResponse(data=output)

@router.get("/workflow/status/{workflow_id}", response_model=ApiResponse[Dict[str, Any]])
def get_workflow_status(
    workflow_id: str,
    tracker: WorkflowStatusTracker = Depends(get_status_tracker)
):
    """
    Fetches the lifecycle state of a specific workflow run.
    """
    logger.info(f"OperationsRouter: Querying status for {workflow_id}")
    status = tracker.get_status(workflow_id)
    if not status:
        raise HTTPException(status_code=404, detail="Workflow run not found")
    return ApiResponse(data=status)

@router.get("/print/jobs", response_model=ApiResponse[List[Dict[str, Any]]])
def list_print_jobs(
    queue: PrintQueue = Depends(get_print_queue)
):
    """
    Lists all queued simulated print jobs.
    """
    logger.info("OperationsRouter: Listing all print jobs.")
    jobs = queue.list_jobs()
    return ApiResponse(data=jobs)

@router.get("/print/jobs/{job_id}", response_model=ApiResponse[Dict[str, Any]])
def get_print_job(
    job_id: str,
    queue: PrintQueue = Depends(get_print_queue)
):
    """
    Queries details of a specific queued print job.
    """
    logger.info(f"OperationsRouter: Querying print job {job_id}")
    job = queue.get_status(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Print job not found")
        
    response_job = dict(job)
    response_job["document"] = "Restaurant Action Plan"
    response_job["pages"] = 1
    return ApiResponse(data=response_job)
