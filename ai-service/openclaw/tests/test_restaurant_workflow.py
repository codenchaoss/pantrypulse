import sys
import os
import json
import unittest
from unittest.mock import patch, MagicMock

# Ensure the app and openclaw folders are on the python path
current_dir = os.path.dirname(os.path.abspath(__file__))
openclaw_dir = os.path.dirname(current_dir)
ai_service_dir = os.path.dirname(openclaw_dir)
sys.path.append(ai_service_dir)

from openclaw.workflows.restaurant_workflow import RestaurantWorkflowOrchestrator

class TestRestaurantWorkflow(unittest.TestCase):
    
    def setUp(self):
        self.orchestrator = RestaurantWorkflowOrchestrator(base_url="http://127.0.0.1:8000")

    @patch("openclaw.services.gateway.KitchenSyncGateway.trigger_inventory_optimization")
    @patch("openclaw.services.gateway.KitchenSyncGateway.trigger_recipe_recommendation")
    @patch("openclaw.services.gateway.KitchenSyncGateway.trigger_menu_generation")
    @patch("openclaw.services.gateway.KitchenSyncGateway.trigger_pricing_suggestions")
    @patch("openclaw.services.gateway.KitchenSyncGateway.trigger_description_generation")
    @patch("openclaw.services.gateway.KitchenSyncGateway.trigger_supplier_messaging")
    def test_01_full_workflow_success(
        self, mock_supplier, mock_desc, mock_pricing, mock_menu, mock_recipe, mock_opt
    ):
        """Verify successful sequential execution and aggregation of all 6 skills."""
        # 1. Mock outputs
        mock_opt.return_value = {"recommended_dishes": [{"dish": "Chicken Curry", "servings": 20}], "purchase_required": False}
        mock_recipe.return_value = {"recipes": [{"recipe_name": "Chicken Curry"}]}
        mock_menu.return_value = {"special_menu": [{"dish": "Chicken Curry", "priority": "HIGH"}]}
        mock_pricing.return_value = {"dish": "Chicken Curry", "recommended_price": 450}
        mock_desc.return_value = {"descriptions": [{"dish": "Chicken Curry", "description": "Tasty"}]}
        mock_supplier.return_value = {"supplier_name": "Fresh Foods", "message": "Draft"}

        # 2. Input inventory
        inventory = [
            {"ingredient": "Chicken", "quantity": 1.5, "unit": "kg", "expiry_days": 1},
            {"ingredient": "Rice", "quantity": 10.0, "unit": "kg", "expiry_days": 5}
        ]

        # 3. Trigger orchestrator
        result = self.orchestrator.execute_workflow(inventory)

        # 4. Assert correct parameters propagation
        # Optimization triggered with inventory
        mock_opt.assert_called_once_with(inventory)
        # Recipe recommendations triggered with extracted list
        mock_recipe.assert_called_once_with(["Chicken", "Rice"])
        # Menu specials planner triggered with unit strings
        mock_menu.assert_called_once_with([
            {"ingredient": "Chicken", "quantity": "1.5 kg", "expiry_days": 1},
            {"ingredient": "Rice", "quantity": "10.0 kg", "expiry_days": 5}
        ])
        # Pricing suggestions triggered for the generated special
        mock_pricing.assert_called_once_with("Chicken Curry", 150.0)
        # Description generated for the special
        mock_desc.assert_called_once_with([{"dish": "Chicken Curry", "category": "Main Course"}])
        # Supplier messaging triggered ONLY for low-stock item (Chicken, quantity <= 2.0)
        mock_supplier.assert_called_once_with(
            supplier_name="Fresh Foods Inc",
            ingredient="Chicken",
            qty="20 kg",
            date="Tomorrow"
        )

        # 5. Assert aggregated plan matches schemas
        self.assertEqual(result["workflow_status"], "completed")
        self.assertEqual(result["optimization"]["recommended_dishes"][0]["dish"], "Chicken Curry")
        self.assertEqual(result["recipe"]["recipes"][0]["recipe_name"], "Chicken Curry")
        self.assertEqual(result["menu"]["special_menu"][0]["dish"], "Chicken Curry")
        self.assertEqual(result["pricing"][0]["recommended_price"], 450)
        self.assertEqual(result["description"]["descriptions"][0]["description"], "Tasty")
        self.assertEqual(result["supplier"][0]["supplier_name"], "Fresh Foods")
        self.assertEqual(len(result["warnings"]), 0)
        print("✓ Test 1: Full sequential orchestration pipeline - PASS")

    @patch("openclaw.services.gateway.KitchenSyncGateway.trigger_inventory_optimization")
    @patch("openclaw.services.gateway.KitchenSyncGateway.trigger_recipe_recommendation")
    @patch("openclaw.services.gateway.KitchenSyncGateway.trigger_menu_generation")
    @patch("openclaw.services.gateway.KitchenSyncGateway.trigger_pricing_suggestions")
    @patch("openclaw.services.gateway.KitchenSyncGateway.trigger_description_generation")
    @patch("openclaw.services.gateway.KitchenSyncGateway.trigger_supplier_messaging")
    def test_02_partial_workflow_failure(
        self, mock_supplier, mock_desc, mock_pricing, mock_menu, mock_recipe, mock_opt
    ):
        """Verify that individual skill failures do not crash the orchestrator."""
        # 1. Mock outputs
        mock_opt.return_value = {"recommended_dishes": [], "purchase_required": False}
        mock_recipe.side_effect = RuntimeError("Recipe Database is offline.")
        mock_menu.return_value = {"special_menu": []}
        
        # 2. Input inventory
        inventory = [{"ingredient": "Chicken", "quantity": 10.0, "unit": "kg", "expiry_days": 1}]

        # 3. Trigger orchestrator (should NOT crash)
        result = self.orchestrator.execute_workflow(inventory)

        # 4. Assert partial success and warnings capture
        self.assertEqual(result["workflow_status"], "partial_success")
        self.assertIsNone(result["recipe"]) # Failed step is empty
        self.assertEqual(len(result["warnings"]), 1)
        self.assertIn("Recipe Database is offline", result["warnings"][0])
        print("✓ Test 2: Step failure-tolerance and partial status - PASS")

def run_tests():
    print("==================================================")
    print("KitchenSync OpenClaw Workflow Verification")
    print("==================================================")
    
    suite = unittest.TestLoader().loadTestsFromTestCase(TestRestaurantWorkflow)
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
