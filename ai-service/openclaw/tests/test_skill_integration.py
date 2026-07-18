import sys
import os
import json
import unittest
from unittest.mock import patch, MagicMock
import httpx

# Ensure the app and openclaw folders are on the python path
current_dir = os.path.dirname(os.path.abspath(__file__))
openclaw_dir = os.path.dirname(current_dir)
ai_service_dir = os.path.dirname(openclaw_dir)
sys.path.append(ai_service_dir)

from openclaw.services.gateway import KitchenSyncGateway
from openclaw.models.schemas import (
    RecipeSkillRequest, RecipeSkillResponse,
    MenuSkillRequest, MenuSkillResponse,
    PricingSkillRequest, PricingSkillResponse,
    DescriptionSkillRequest, DescriptionSkillResponse,
    SupplierSkillRequest, SupplierSkillResponse,
    OptimizationSkillRequest, OptimizationSkillResponse
)

class TestOpenClawSkillIntegration(unittest.TestCase):
    
    def setUp(self):
        self.gateway = KitchenSyncGateway(base_url="http://127.0.0.1:8000")

    @patch("httpx.Client.post")
    def test_01_recipe_skill_integration(self, mock_post):
        """Verify Recipe Skill payload mapping and response validation."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "data": {
                "recipes": [{
                    "recipe_id": "r1",
                    "recipe_name": "Garlic Butter Chicken",
                    "description": "Premium dish",
                    "matched_ingredients": ["Chicken", "Butter"],
                    "missing_ingredients": ["Garlic"],
                    "match_percentage": 66,
                    "preparation_time_minutes": 25,
                    "difficulty": "Easy",
                    "estimated_calories": 450,
                    "reason_for_recommendation": "High profit margins"
                }]
            }
        }
        mock_post.return_value = mock_response
        
        # Trigger Gateway Client
        result = self.gateway.trigger_recipe_recommendation(["Chicken", "Butter"])
        
        # Check mock call properties
        mock_post.assert_called_once_with("http://127.0.0.1:8000/recipe", json={"ingredients": ["Chicken", "Butter"]})
        
        # Verify schema mapping
        validated = RecipeSkillResponse(**result)
        self.assertEqual(len(validated.recipes), 1)
        self.assertEqual(validated.recipes[0].recipe_name, "Garlic Butter Chicken")
        print("✓ Test 1: Recipe Skill endpoint integration - PASS")

    @patch("httpx.Client.post")
    def test_02_menu_skill_integration(self, mock_post):
        """Verify Menu Skill payload mapping and response validation."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "data": {
                "special_menu": [{
                    "dish": "Chicken Soup",
                    "reason": "Expiring Chicken",
                    "matched_inventory": ["Chicken"],
                    "estimated_profit": 200,
                    "priority": "HIGH",
                    "preparation_time": 20,
                    "difficulty": "Easy",
                    "confidence": 95
                }]
            }
        }
        mock_post.return_value = mock_response
        
        inventory = [{"ingredient": "Chicken", "quantity": "5 kg", "expiry_days": 1}]
        result = self.gateway.trigger_menu_generation(inventory)
        
        mock_post.assert_called_once_with("http://127.0.0.1:8000/menu", json={"inventory": inventory})
        
        validated = MenuSkillResponse(**result)
        self.assertEqual(len(validated.special_menu), 1)
        self.assertEqual(validated.special_menu[0].dish, "Chicken Soup")
        print("✓ Test 2: Menu Skill endpoint integration - PASS")

    @patch("httpx.Client.post")
    def test_03_pricing_skill_integration(self, mock_post):
        """Verify Pricing Skill payload mapping and response validation."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "data": {
                "dish": "Butter Chicken",
                "ingredient_cost": 210.0,
                "recommended_price": 500,
                "estimated_profit": 290,
                "profit_margin": 58,
                "pricing_strategy": "Standard",
                "market_position": "Mid-range",
                "price_confidence": 95
            }
        }
        mock_post.return_value = mock_response
        
        result = self.gateway.trigger_pricing_suggestions("Butter Chicken", 210.0)
        
        mock_post.assert_called_once_with("http://127.0.0.1:8000/pricing", json={"dish": "Butter Chicken", "ingredient_cost": 210.0})
        
        validated = PricingSkillResponse(**result)
        self.assertEqual(validated.recommended_price, 500)
        self.assertEqual(validated.pricing_strategy, "Standard")
        print("✓ Test 3: Pricing Skill endpoint integration - PASS")

    @patch("httpx.Client.post")
    def test_04_description_skill_integration(self, mock_post):
        """Verify Description Skill payload mapping and response validation."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "data": {
                "descriptions": [{
                    "dish": "Chicken Salad",
                    "description": "Healthy choice",
                    "tone": "Premium",
                    "language": "English"
                }]
            }
        }
        mock_post.return_value = mock_response
        
        dishes = [{"dish": "Chicken Salad", "category": "Salad"}]
        result = self.gateway.trigger_description_generation(dishes)
        
        mock_post.assert_called_once_with("http://127.0.0.1:8000/description", json={"dishes": dishes})
        
        validated = DescriptionSkillResponse(**result)
        self.assertEqual(len(validated.descriptions), 1)
        self.assertEqual(validated.descriptions[0].description, "Healthy choice")
        print("✓ Test 4: Description Skill endpoint integration - PASS")

    @patch("httpx.Client.post")
    def test_05_supplier_skill_integration(self, mock_post):
        """Verify Supplier Skill payload mapping and response validation."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "data": {
                "supplier_name": "Fresh Foods",
                "ingredient": "Chicken",
                "message": "Please send chicken.",
                "language": "English"
            }
        }
        mock_post.return_value = mock_response
        
        result = self.gateway.trigger_supplier_messaging("Fresh Foods", "Chicken", "10 kg", "Tomorrow")
        
        mock_post.assert_called_once_with("http://127.0.0.1:8000/supplier", json={
            "supplier_name": "Fresh Foods",
            "ingredient": "Chicken",
            "required_quantity": "10 kg",
            "required_date": "Tomorrow"
        })
        
        validated = SupplierSkillResponse(**result)
        self.assertEqual(validated.supplier_name, "Fresh Foods")
        print("✓ Test 5: Supplier Skill endpoint integration - PASS")

    @patch("httpx.Client.post")
    def test_06_optimization_skill_integration(self, mock_post):
        """Verify Optimization Skill payload mapping and response validation."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "data": {
                "recommended_dishes": [{"dish": "Butter Chicken", "servings": 20, "profit": 5000, "priority": "HIGH"}],
                "inventory_usage": [{"ingredient": "Chicken", "used_quantity": 7.0, "unit": "kg"}],
                "estimated_revenue": 10000,
                "waste_saved": 7.0,
                "remaining_inventory": [{"ingredient": "Chicken", "remaining_quantity": 3.0, "unit": "kg"}],
                "purchase_required": False,
                "reason": "Stock OK",
                "language": "English"
            }
        }
        mock_post.return_value = mock_response
        
        inventory = [{"ingredient": "Chicken", "quantity": 10.0, "unit": "kg", "expiry_days": 1}]
        result = self.gateway.trigger_inventory_optimization(inventory)
        
        mock_post.assert_called_once_with("http://127.0.0.1:8000/optimization", json={"inventory": inventory})
        
        validated = OptimizationSkillResponse(**result)
        self.assertEqual(validated.estimated_revenue, 10000)
        self.assertEqual(len(validated.recommended_dishes), 1)
        print("✓ Test 6: Optimization Skill endpoint integration - PASS")

    @patch("httpx.Client.post")
    def test_07_gateway_error_handling(self, mock_post):
        """Verify that HTTP Status errors and connection failures raise clean standard exceptions."""
        # 1. HTTP 500 error scenario
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        # Mock HTTPStatusError raising behavior
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            message="Internal Server Error",
            request=MagicMock(),
            response=mock_response
        )
        mock_post.return_value = mock_response
        
        with self.assertRaises(RuntimeError) as context:
            self.gateway.trigger_recipe_recommendation(["Chicken"])
        self.assertIn("error code 500", str(context.exception))
        
        # 2. Connection failure scenario
        mock_post.side_effect = httpx.ConnectError("Connection refused")
        with self.assertRaises(ConnectionError) as context2:
            self.gateway.trigger_recipe_recommendation(["Chicken"])
        self.assertIn("Failed to connect", str(context2.exception))
        print("✓ Test 7: Gateway network and REST error handling - PASS")

def run_tests():
    print("==================================================")
    print("KitchenSync OpenClaw Skill Integration Verification")
    print("==================================================")
    
    suite = unittest.TestLoader().loadTestsFromTestCase(TestOpenClawSkillIntegration)
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
