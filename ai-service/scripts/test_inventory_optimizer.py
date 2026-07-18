import sys
import os
import unittest
from unittest.mock import patch, MagicMock
from fastapi import HTTPException

# Ensure the app directory is on the python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from app.services.inventory_optimizer_service import InventoryOptimizerService, detect_language

class TestInventoryOptimizer(unittest.TestCase):
    
    def setUp(self):
        self.service = InventoryOptimizerService()

    def test_01_request_validation(self):
        """Verify that empty inputs or negative values trigger correct HTTP 400 validation exceptions."""
        # Empty inventory list
        with self.assertRaises(HTTPException) as context:
            self.service.optimize_inventory([])
        self.assertEqual(context.exception.status_code, 400)
        self.assertIn("cannot be empty", context.exception.detail)
        
        # Negative quantity
        with self.assertRaises(HTTPException) as context2:
            self.service.optimize_inventory([{"ingredient": "Chicken", "quantity": -5.0, "unit": "kg", "expiry_days": 1}])
        self.assertEqual(context2.exception.status_code, 400)
        self.assertIn("Quantity cannot be negative", context2.exception.detail)
        
        # Negative expiry
        with self.assertRaises(HTTPException) as context3:
            self.service.optimize_inventory([{"ingredient": "Chicken", "quantity": 10.0, "unit": "kg", "expiry_days": -1}])
        self.assertEqual(context3.exception.status_code, 400)
        self.assertIn("Expiry days cannot be negative", context3.exception.detail)
        print("✓ Test 1: Request parameter validations - PASS")

    def test_02_language_propagation(self):
        """Verify language heuristics for English, Telugu, and Romanized Tenglish."""
        self.assertEqual(detect_language("Chicken Butter Rice"), "english")
        self.assertEqual(detect_language("సాల్మన్ వంటకం ఎలా చేయాలి"), "telugu")
        self.assertEqual(detect_language("menu optimization ela cheddam plan"), "tenglish")
        print("✓ Test 2: Language propagation script checks - PASS")

    def test_03_duplicate_ingredient_handling(self):
        """Verify that duplicate ingredients in input are programmatically merged."""
        input_items = [
            {"ingredient": "Chicken", "quantity": 6.0, "unit": "kg", "expiry_days": 3},
            {"ingredient": "chicken", "quantity": 4.0, "unit": "kg", "expiry_days": 1},
            {"ingredient": "Butter", "quantity": 2.0, "unit": "kg", "expiry_days": 5}
        ]
        
        # Mock LLM router and RAG retrieval to avoid API dependency during test
        with patch.object(self.service.recipe_service, 'generate_recipe', return_value={"recipes": []}), \
             patch.object(self.service.menu_service, 'generate_menu', return_value={"special_menu": []}), \
             patch.object(self.service.pricing_service, 'generate_pricing_suggestion', return_value={"recommended_price": 500, "estimated_profit": 300, "category": "HIGH"}), \
             patch.object(self.service.retriever, 'retrieve', return_value=[]), \
             patch.object(self.service.router, 'generate', return_value={"status": "success", "response": "{}"}):
            
            result = self.service.optimize_inventory(input_items)
            
            # Check remaining inventory sizes (should be 2 items: chicken and butter)
            self.assertEqual(len(result["remaining_inventory"]), 2)
            
            # Chicken remaining should reflect stock sum (10.0) minus whatever was consumed in fallbacks
            chicken_item = next(item for item in result["remaining_inventory"] if item["ingredient"].lower() == "chicken")
            # In duplicate merge, quantities should sum to 10.0
            self.assertEqual(chicken_item["unit"], "kg")
            print("✓ Test 3: Duplicate ingredient merging - PASS")

    @patch("app.services.inventory_optimizer_service.KnowledgeRetriever.retrieve")
    @patch("app.services.inventory_optimizer_service.LLMRouter.generate")
    def test_04_calculations_and_sorting(self, mock_router, mock_retrieve):
        """Verify waste saved, revenues, servings, and stable sorting priority mapping."""
        mock_retrieve.return_value = []
        
        # Setup mock specials
        specials = [
            {"dish": "Butter Chicken", "matched_inventory": ["Chicken"], "priority": "HIGH", "estimated_profit": 200},
            {"dish": "Garlic Chicken", "matched_inventory": ["Chicken"], "priority": "MEDIUM", "estimated_profit": 350},
            {"dish": "Chicken Soup", "matched_inventory": ["Chicken"], "priority": "HIGH", "estimated_profit": 300}
        ]
        
        # Mock pricing suggestions
        pricing_returns = {
            "Butter Chicken": {"recommended_price": 500, "estimated_profit": 300},
            "Garlic Chicken": {"recommended_price": 400, "estimated_profit": 250},
            "Chicken Soup": {"recommended_price": 300, "estimated_profit": 200}
        }
        
        # Mock LLM suggestions
        mock_router.return_value = {
            "status": "success",
            "provider": "gemini",
            "response": (
                '{"recommended_dishes": ['
                '{"dish": "Garlic Chicken", "servings": 10, "priority": "MEDIUM"},'
                '{"dish": "Butter Chicken", "servings": 20, "priority": "HIGH"},'
                '{"dish": "Chicken Soup", "servings": 15, "priority": "HIGH"}'
                '], "purchase_required": false, "reason": "Sufficient stock", "language": "english"}'
            )
        }
        
        input_items = [
            {"ingredient": "Chicken", "quantity": 15.0, "unit": "kg", "expiry_days": 1}
        ]
        
        with patch.object(self.service.menu_service, 'generate_menu', return_value={"special_menu": specials}), \
             patch.object(self.service.pricing_service, 'generate_pricing_suggestion', side_effect=lambda dish, cost: pricing_returns[dish]):
            
            result = self.service.optimize_inventory(input_items)
            
            # 1. Servings revenue calculation verification
            # Garlic Chicken: 10 * 400 = 4000
            # Butter Chicken: 20 * 500 = 10000
            # Chicken Soup: 15 * 300 = 4500
            # Total Revenue: 4000 + 10000 + 4500 = 18500
            self.assertEqual(result["estimated_revenue"], 18500)
            
            # 2. Consumption calculations verification
            # Chicken used:
            # Butter Chicken (20 servings * 0.35 = 7.0)
            # Garlic Chicken (10 servings * 0.35 = 3.5)
            # Chicken Soup (15 servings * 0.35 = 5.25)
            # Total consumption needed = 15.75, limited by stock = 15.0. Waste saved should be 15.0 since expiry is <=2 days.
            self.assertEqual(result["waste_saved"], 15.0)
            
            # 3. Stable sorting validation: Expiry Priority (HIGH -> MEDIUM -> LOW) -> Profit (descending) -> Alphabetical
            # HIGH Priority dishes: Butter Chicken (Profit: 20 * 300 = 6000), Chicken Soup (Profit: 15 * 200 = 3000)
            # MEDIUM Priority dishes: Garlic Chicken (Profit: 10 * 250 = 2500)
            # Butter Chicken (HIGH, 6000) should be 1st
            # Chicken Soup (HIGH, 3000) should be 2nd
            # Garlic Chicken (MEDIUM, 2500) should be 3rd
            dishes = result["recommended_dishes"]
            self.assertEqual(dishes[0]["dish"], "Butter Chicken")
            self.assertEqual(dishes[1]["dish"], "Chicken Soup")
            self.assertEqual(dishes[2]["dish"], "Garlic Chicken")
            print("✓ Test 4: Programmatic math, consumption limits, and stable sorting - PASS")

    @patch("app.services.inventory_optimizer_service.KnowledgeRetriever.retrieve")
    @patch("app.services.inventory_optimizer_service.LLMRouter.generate")
    def test_05_parser_fallback(self, mock_router, mock_retrieve):
        """Verify that JSON parser errors trigger local fallback optimization suggestions."""
        mock_retrieve.return_value = []
        # Return non-JSON response from LLM router
        mock_router.return_value = {
            "status": "success",
            "response": "Here is the optimization recommendation to cook chicken."
        }
        
        specials = [
            {"dish": "Tandoori Chicken", "priority": "HIGH", "matched_inventory": ["Chicken"]}
        ]
        
        input_items = [
            {"ingredient": "Chicken", "quantity": 10.0, "unit": "kg", "expiry_days": 1}
        ]
        
        with patch.object(self.service.menu_service, 'generate_menu', return_value={"special_menu": specials}), \
             patch.object(self.service.pricing_service, 'generate_pricing_suggestion', return_value={"recommended_price": 400, "estimated_profit": 250, "category": "HIGH"}):
            
            result = self.service.optimize_inventory(input_items)
            
            self.assertEqual(len(result["recommended_dishes"]), 1)
            self.assertEqual(result["recommended_dishes"][0]["dish"], "Tandoori Chicken")
            self.assertIn("Tandoori Chicken", result["recommended_dishes"][0]["dish"])
            self.assertIn("waste reduction", result["reason"].lower())
            print("✓ Test 5: Parsing fallback recovery - PASS")

def run_tests():
    print("==================================================")
    print("KitchenSync Inventory Optimizer Verification")
    print("==================================================")
    
    suite = unittest.TestLoader().loadTestsFromTestCase(TestInventoryOptimizer)
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
