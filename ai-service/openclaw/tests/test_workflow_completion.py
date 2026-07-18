import sys
import os
import time
import unittest
from unittest.mock import patch, MagicMock

# Ensure the app and openclaw folders are on the python path
current_dir = os.path.dirname(os.path.abspath(__file__))
openclaw_dir = os.path.dirname(current_dir)
ai_service_dir = os.path.dirname(openclaw_dir)
sys.path.append(ai_service_dir)

from openclaw.operations.print_queue import PrintQueue
from openclaw.operations.workflow_status import WorkflowStatusTracker
from openclaw.operations.execution_log import ExecutionLogger
from openclaw.operations.completion_manager import WorkflowCompletionManager

class TestWorkflowCompletion(unittest.TestCase):
    
    def setUp(self):
        self.print_queue = PrintQueue()
        self.status_tracker = WorkflowStatusTracker()
        self.execution_logger = ExecutionLogger()
        self.manager = WorkflowCompletionManager()
        
        # Reset singletons
        self.print_queue.clear()
        self.status_tracker.clear()
        self.execution_logger.clear()

    def test_01_print_queue_management(self):
        """Verify enqueuing, getting status, and listing print jobs."""
        docs = [{"type": "menu_special", "title": "Chicken Soup", "price": 200}]
        
        # 1. Enqueue job
        job = self.print_queue.enqueue(docs)
        self.assertEqual(job["status"], "queued")
        self.assertEqual(len(job["documents"]), 1)
        job_id = job["job_id"]

        # 2. Get status
        status_info = self.print_queue.get_status(job_id)
        self.assertEqual(status_info["status"], "queued")

        # 3. List jobs
        all_jobs = self.print_queue.list_jobs()
        self.assertEqual(len(all_jobs), 1)
        self.assertEqual(all_jobs[0]["job_id"], job_id)
        print("✓ Test 1: Simulated Print Queue management - PASS")

    def test_02_workflow_status_transitions(self):
        """Verify lifecycle state transitions (PENDING -> RUNNING -> COMPLETED)."""
        # 1. Create run
        w_id = self.status_tracker.create_workflow()
        status_info = self.status_tracker.get_status(w_id)
        self.assertEqual(status_info["status"], "PENDING")

        # 2. Start running
        self.status_tracker.update_status(w_id, "RUNNING")
        status_info = self.status_tracker.get_status(w_id)
        self.assertEqual(status_info["status"], "RUNNING")

        # 3. Complete run
        self.status_tracker.update_status(w_id, "COMPLETED")
        status_info = self.status_tracker.get_status(w_id)
        self.assertEqual(status_info["status"], "COMPLETED")
        self.assertIsNotNone(status_info["completed_at"])
        print("✓ Test 2: Workflow status lifecycle transitions - PASS")

    def test_03_execution_logging(self):
        """Verify execution logs record step durations and warnings."""
        w_id = "test-wflow"
        self.execution_logger.initialize_log(w_id)
        
        self.execution_logger.log_step(w_id, "optimize", 15.0, "success")
        self.execution_logger.log_step(w_id, "print", 5.0, "failed", ["No paper"])
        self.execution_logger.finalize_log(w_id, 20.0)

        logs = self.execution_logger.get_log(w_id)
        self.assertEqual(logs["duration_ms"], 20)
        self.assertEqual(len(logs["steps"]), 2)
        self.assertEqual(logs["steps"][0]["skill"], "optimize")
        self.assertEqual(logs["steps"][1]["status"], "failed")
        self.assertEqual(logs["steps"][1]["warnings"], ["No paper"])
        print("✓ Test 3: Operational execution logging - PASS")

    def test_04_completion_manager_success(self):
        """Verify that completion manager enqueues print jobs and updates status."""
        plan = {
            "optimization": {"recommended_dishes": [], "purchase_required": False},
            "recipe": {"recipes": []},
            "menu": {
                "special_menu": [{"dish": "Butter Chicken", "priority": "HIGH", "preparation_time": 20}]
            },
            "pricing": [{"dish": "Butter Chicken", "ingredient_cost": 150.0, "recommended_price": 400, "estimated_profit": 250, "profit_margin": 60, "pricing_strategy": "Standard", "market_position": "Mid-range", "price_confidence": 95}],
            "description": {"descriptions": [{"dish": "Butter Chicken", "description": "Spicy Butter Chicken"}]},
            "supplier": [],
            "warnings": [],
            "workflow_status": "completed"
        }

        # Run completion manager
        result = self.manager.complete_workflow(plan)

        # Assert correct publishing status
        self.assertEqual(result["status"], "completed")
        self.assertEqual(result["dashboard"], "published")
        self.assertEqual(result["menu"], "published")
        self.assertIsNotNone(result["print_job"])
        
        # Verify print queue contains the job
        job_id = result["print_job"]["job_id"]
        job_status = self.print_queue.get_status(job_id)
        self.assertEqual(job_status["status"], "queued")
        self.assertEqual(len(job_status["documents"]), 1)
        self.assertEqual(job_status["documents"][0]["title"], "Butter Chicken")
        print("✓ Test 4: Completion manager success path - PASS")

    def test_05_completion_manager_partial_failure(self):
        """Verify that printer failures set status as PARTIAL_SUCCESS and do not crash."""
        # Simulated action plan
        plan = {
            "optimization": None,
            "recipe": None,
            "menu": {"special_menu": [{"dish": "Spicy Rice"}]},
            "pricing": [],
            "description": None,
            "supplier": [],
            "warnings": ["Pricing offline"],
            "workflow_status": "partial_success"
        }

        # Mock print queue enqueue to raise exception
        with patch.object(self.print_queue, "enqueue", side_effect=RuntimeError("Printer Offline")):
            result = self.manager.complete_workflow(plan)

        # Confirm partial success status
        self.assertEqual(result["status"], "partial_success")
        self.assertIsNone(result["print_job"])
        self.assertIn("Printer Offline", result["warnings"][-1])
        print("✓ Test 5: Print failure graceful fallback - PASS")

def run_tests():
    print("==================================================")
    print("KitchenSync OpenClaw Workflow Completion Verification")
    print("==================================================")
    
    suite = unittest.TestLoader().loadTestsFromTestCase(TestWorkflowCompletion)
    runner = unittest.TextTestRunner(verbosity=0)
    result = runner.run(suite)
    
    print("==================================================")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("FINAL STATUS: PASS")
        sys.exit(0)
    else:
        print("FINAL STATUS: FAIL")
        sys.exit(1)

if __name__ == "__main__":
    run_tests()
