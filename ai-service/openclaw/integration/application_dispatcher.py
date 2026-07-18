import logging
from typing import Dict, Any

from openclaw.integration.dashboard_adapter import DashboardAdapter
from openclaw.integration.menu_adapter import MenuAdapter
from openclaw.integration.supplier_adapter import SupplierAdapter
from openclaw.integration.reports_adapter import ReportsAdapter

logger = logging.getLogger("app.openclaw")

class ApplicationDispatcher:
    """
    Coordinates and executes data transformations using module-specific adapters.
    """
    def __init__(self):
        self.dashboard_adapter = DashboardAdapter()
        self.menu_adapter = MenuAdapter()
        self.supplier_adapter = SupplierAdapter()
        self.reports_adapter = ReportsAdapter()

    def dispatch(self, action_plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Translates a Restaurant Action Plan into module payloads.
        """
        logger.info("Application Dispatcher: Processing Restaurant Action Plan.")
        
        logger.info("Application Dispatcher: Preparing Dashboard Payload...")
        dashboard_payload = self.dashboard_adapter.adapt(action_plan)

        logger.info("Application Dispatcher: Preparing Menu Payload...")
        menu_payload = self.menu_adapter.adapt(action_plan)

        logger.info("Application Dispatcher: Preparing Supplier Payload...")
        supplier_payload = self.supplier_adapter.adapt(action_plan)

        logger.info("Application Dispatcher: Preparing Reports Payload...")
        reports_payload = self.reports_adapter.adapt(action_plan)

        logger.info("Application Dispatcher: Dispatch completed successfully.")
        
        return {
            "dashboard": dashboard_payload,
            "menu": menu_payload,
            "supplier": supplier_payload,
            "reports": reports_payload,
            "status": "published"
        }
