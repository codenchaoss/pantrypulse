import time
import logging
from typing import Dict, Any, List

from openclaw.integration.application_dispatcher import ApplicationDispatcher
from openclaw.operations.print_queue import PrintQueue
from openclaw.operations.workflow_status import WorkflowStatusTracker
from openclaw.operations.execution_log import ExecutionLogger

logger = logging.getLogger("app.openclaw")

class WorkflowCompletionManager:
    """
    OpenClaw Completion Manager.
    Post-processes the generated Restaurant Action Plan, publishes payloads,
    and enqueues the print job safely.
    """
    def __init__(self):
        self.dispatcher = ApplicationDispatcher()
        self.print_queue = PrintQueue()
        self.status_tracker = WorkflowStatusTracker()
        self.execution_logger = ExecutionLogger()

    def complete_workflow(self, action_plan: Dict[str, Any], workflow_id: str = None) -> Dict[str, Any]:
        """
        Coordinates the workflow completion step.
        """
        start_time = time.time()
        
        # 1. Resolve workflow ID and update state
        w_id = workflow_id or self.status_tracker.create_workflow()
        self.status_tracker.update_status(w_id, "RUNNING")
        self.execution_logger.initialize_log(w_id)
        
        logger.info(f"Completion Manager: Initiating completion for run {w_id}")
        warnings = list(action_plan.get("warnings", []))
        
        # 2. Dispatch payload
        logger.info("Completion Manager: Triggering Application Dispatcher...")
        dispatch_start = time.time()
        dispatched_data = self.dispatcher.dispatch(action_plan)
        dispatch_duration = (time.time() - dispatch_start) * 1000
        self.execution_logger.log_step(w_id, "application-dispatch", dispatch_duration, "success")
        
        # 3. Process Print Job
        print_job_info = None
        menu_specials = dispatched_data.get("menu", {}).get("menu_specials", [])
        
        if menu_specials:
            logger.info("Completion Manager: Menu specials detected. Enqueuing print job...")
            print_start = time.time()
            try:
                # Prepare documents for printing
                documents = []
                for spec in menu_specials:
                    documents.append({
                        "type": "menu_special",
                        "title": spec.get("dish"),
                        "price": spec.get("selling_price"),
                        "description": spec.get("description")
                    })
                
                job = self.print_queue.enqueue(documents)
                print_job_info = {
                    "job_id": job["job_id"],
                    "status": job["status"]
                }
                print_duration = (time.time() - print_start) * 1000
                self.execution_logger.log_step(w_id, "print-queue", print_duration, "success")
            except Exception as e:
                logger.error(f"Completion Manager: Printing failed: {str(e)}")
                warnings.append(f"Simulated Print Queue failed: {str(e)}")
                self.execution_logger.log_step(w_id, "print-queue", 0.0, "failed", [str(e)])
        
        # 4. Resolve Final Lifecycle Status
        workflow_status = "COMPLETED"
        if warnings or action_plan.get("workflow_status") == "partial_success":
            workflow_status = "PARTIAL_SUCCESS"
            
        self.status_tracker.update_status(w_id, workflow_status, warnings)
        
        total_duration = (time.time() - start_time) * 1000
        self.execution_logger.finalize_log(w_id, total_duration)
        
        logger.info(f"Completion Manager: Workflow completed. Final Status: {workflow_status}")
        
        return {
            "workflow_id": w_id,
            "status": workflow_status.lower(),
            "dashboard": dispatched_data.get("status", "error"),
            "menu": dispatched_data.get("status", "error"),
            "supplier": dispatched_data.get("status", "error"),
            "reports": dispatched_data.get("status", "error"),
            "print_job": print_job_info,
            "warnings": warnings
        }
