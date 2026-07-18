import sys
import os
import json
import unittest

# Ensure the app and openclaw folders are on the python path
current_dir = os.path.dirname(os.path.abspath(__file__))
openclaw_dir = os.path.dirname(current_dir)
ai_service_dir = os.path.dirname(openclaw_dir)
sys.path.append(ai_service_dir)

from openclaw.integration.application_dispatcher import ApplicationDispatcher

class TestApplicationIntegration(unittest.TestCase):
    
    def setUp(self):
        self.dispatcher = ApplicationDispatcher()

    def test_01_full_action_plan_dispatch(self):
        """Verify successful dispatching and payload formatting under a complete action plan."""
        # Simulated Complete Restaurant Action Plan
        full_plan = {
            "optimization": {
                "recommended_dishes": [{"dish": "Paneer Tikka", "servings": 15, "profit": 3000, "priority": "HIGH"}],
                "inventory_usage": [{"ingredient": "Paneer", "used_quantity": 5.0, "unit": "kg"}],
                "estimated_revenue": 6000,
                "currency": "INR",
                "waste_saved": {"value": 5.0, "unit": "kg"},
                "remaining_inventory": [{"ingredient": "Paneer", "remaining_quantity": 2.0, "unit": "kg"}],
                "purchase_required": True,
                "purchase_items": [{"ingredient": "Paneer", "required_quantity": "10.0 kg"}],
                "reason": "Optimize Paneer",
                "language": "English"
            },
            "recipe": {
                "recipes": [{
                    "recipe_id": "r1",
                    "recipe_name": "Paneer Tikka",
                    "description": "Grilled cottage cheese",
                    "matched_ingredients": ["Paneer"],
                    "missing_ingredients": [],
                    "match_percentage": 100,
                    "preparation_time_minutes": 20,
                    "difficulty": "Easy",
                    "estimated_calories": 300,
                    "reason_for_recommendation": "High profit"
                }]
            },
            "menu": {
                "special_menu": [{
                    "dish": "Paneer Tikka",
                    "reason": "Expiring stock",
                    "matched_inventory": ["Paneer"],
                    "estimated_profit": 200,
                    "priority": "HIGH",
                    "preparation_time": 20,
                    "difficulty": "Easy",
                    "confidence": 95
                }]
            },
            "pricing": [{
                "dish": "Paneer Tikka",
                "ingredient_cost": 150.0,
                "recommended_price": 350,
                "estimated_profit": 200,
                "profit_margin": 57,
                "pricing_strategy": "Standard",
                "market_position": "Mid-range",
                "price_confidence": 95
            }],
            "description": {
                "descriptions": [{
                    "dish": "Paneer Tikka",
                    "description": "Soft grilled cottage cheese marinated in tandoori spices.",
                    "tone": "Premium",
                    "language": "English"
                }]
            },
            "supplier": [{
                "supplier_name": "Dairy Supplier",
                "ingredient": "Paneer",
                "message": "Order 10 kg Paneer.",
                "language": "English"
            }],
            "warnings": [],
            "workflow_status": "completed"
        }

        # Trigger dispatcher
        output = self.dispatcher.dispatch(full_plan)

        # 1. Assert status and base envelope keys
        self.assertEqual(output["status"], "published")
        self.assertIn("dashboard", output)
        self.assertIn("menu", output)
        self.assertIn("supplier", output)
        self.assertIn("reports", output)

        # 2. Assert Dashboard Payload
        dash = output["dashboard"]
        self.assertEqual(dash["workflow_status"], "completed")
        self.assertEqual(dash["warnings_count"], 0)
        self.assertEqual(dash["optimization_summary"]["waste_saved_kg"], 5.0)
        self.assertEqual(dash["recommended_recipes"][0]["recipe_name"], "Paneer Tikka")
        print("✓ Test 1: Dashboard payload formatting - PASS")

        # 3. Assert Menu Payload
        menu_p = output["menu"]
        self.assertEqual(menu_p["specials_count"], 1)
        spec = menu_p["menu_specials"][0]
        self.assertEqual(spec["dish"], "Paneer Tikka")
        self.assertEqual(spec["description"], "Soft grilled cottage cheese marinated in tandoori spices.")
        self.assertEqual(spec["selling_price"], 350)
        self.assertEqual(spec["roi_tier"], "HIGH")
        print("✓ Test 2: AI Menu Planner payload formatting - PASS")

        # 4. Assert Supplier Payload
        supp = output["supplier"]
        self.assertEqual(supp["drafts_count"], 1)
        self.assertTrue(supp["purchase_required_flag"])
        self.assertEqual(supp["supplier_replenishment_drafts"][0]["supplier_name"], "Dairy Supplier")
        print("✓ Test 3: Supplier payload formatting - PASS")

        # 5. Assert Reports Payload
        rep = output["reports"]
        self.assertEqual(rep["optimization_summary"]["waste_saved_kg"], 5.0)
        self.assertIn("Paneer Tikka", rep["menu_specials_list"])
        self.assertEqual(rep["financial_summary"]["total_estimated_profit"], 200)
        print("✓ Test 4: Reports payload formatting - PASS")

    def test_02_partial_action_plan_dispatch(self):
        """Verify that empty, partial, or missing optional blocks are handled gracefully."""
        # Simulated Partial Plan (failed step 2 and pricing)
        partial_plan = {
            "optimization": None,
            "recipe": None,
            "menu": {
                "special_menu": [{"dish": "Paneer Tikka", "priority": "HIGH"}]
            },
            "pricing": [],
            "description": None,
            "supplier": [],
            "warnings": ["Pricing service offline"],
            "workflow_status": "partial_success"
        }

        # Trigger dispatcher (must NOT crash)
        output = self.dispatcher.dispatch(partial_plan)

        # Assert status remains published
        self.assertEqual(output["status"], "published")
        
        # Verify dashboard defaults
        dash = output["dashboard"]
        self.assertEqual(dash["workflow_status"], "partial_success")
        self.assertEqual(dash["warnings_count"], 1)
        self.assertEqual(dash["optimization_summary"]["waste_saved_kg"], 0.0)
        self.assertEqual(len(dash["recommended_recipes"]), 0)

        # Verify menu fallback defaults
        menu_p = output["menu"]
        self.assertEqual(menu_p["specials_count"], 1)
        spec = menu_p["menu_specials"][0]
        self.assertEqual(spec["dish"], "Paneer Tikka")
        self.assertEqual(spec["description"], "Tasty daily special dish.") # Default fallback copy
        self.assertEqual(spec["selling_price"], 400) # Default pricing fallback
        self.assertEqual(spec["roi_tier"], "MEDIUM") # Default ROI category tier
        print("✓ Test 5: Fault-tolerance under partial data plans - PASS")

def run_tests():
    print("==================================================")
    print("KitchenSync OpenClaw Application Integration Verification")
    print("==================================================")
    
    suite = unittest.TestLoader().loadTestsFromTestCase(TestApplicationIntegration)
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
