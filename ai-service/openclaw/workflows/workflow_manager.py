import logging
from typing import List, Dict, Any
from openclaw.workflows.restaurant_workflow import RestaurantWorkflowOrchestrator

logger = logging.getLogger("app.openclaw")

class OpenClawWorkflowManager:
    """
    Manager facade responsible for registering, configuring, and executing OpenClaw workflows.
    """
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url
        self.orchestrator = RestaurantWorkflowOrchestrator(base_url=self.base_url)

    def run_restaurant_optimization_workflow(self, inventory: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Executes the flagship BOH optimization workflow.
        """
        logger.info("OpenClaw Manager: Triggering restaurant optimization workflow.")
        return self.orchestrator.execute_workflow(inventory)

    def publish_workflow_result(self, action_plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Dispatches the completed action plan to application adapters.
        """
        from openclaw.integration.application_dispatcher import ApplicationDispatcher
        dispatcher = ApplicationDispatcher()
        return dispatcher.dispatch(action_plan)
