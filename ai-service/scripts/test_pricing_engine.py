import sys
import os
import unittest
from unittest.mock import patch, MagicMock
from fastapi import HTTPException

# Ensure the app directory is on the python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from app.services.pricing_service import PricingService, detect_language

class TestPricingEngine(unittest.TestCase):
    
    def setUp(self):
        self.service = PricingService()

    def test_01_request_validation(self):
        """Verify that empty names or negative costs trigger correct HTTP 400 validation exceptions."""
        # Empty dish name
        with self.assertRaises(HTTPException) as context:
            self.service.generate_pricing_suggestion("", 150.0)
        self.assertEqual(context.exception.status_code, 400)
        self.assertIn("cannot be empty", context.exception.detail)
        
        # Negative cost
        with self.assertRaises(HTTPException) as context2:
            self.service.generate_pricing_suggestion("Butter Chicken", -50.0)
        self.assertEqual(context2.exception.status_code, 400)
        self.assertIn("cannot be negative", context2.exception.detail)
        print("✓ Test 1: Request parameter validations - PASS")

    def test_02_language_heuristics(self):
        """Verify language heuristics for English, Telugu, and Romanized Tenglish."""
        self.assertEqual(detect_language("Chicken Curry"), "english")
        self.assertEqual(detect_language("సలాడ్ ధర ఎంత"), "telugu")
        self.assertEqual(detect_language("Fried Rice cheyyali recipe"), "tenglish")
        print("✓ Test 2: Language propagation script checks - PASS")

    @patch("app.services.pricing_service.KnowledgeRetriever.retrieve")
    @patch("app.services.pricing_service.LLMRouter.generate")
    def test_03_calculations_and_categories(self, mock_router, mock_retrieve):
        """Verify that profit, margins, and profit categories are calculated programmatically."""
        mock_retrieve.return_value = []
        
        # Scenario A: Margin of 60% (HIGH)
        # Cost: 200, Price: 500 -> Profit: 300 -> Margin: (300/500)*100 = 60%
        mock_router.return_value = {
            "status": "success",
            "provider": "gemini",
            "response": '{"dish": "Premium Steak", "recommended_price": 500, "reason": "Premium cut", "language": "english"}'
        }
        res_a = self.service.generate_pricing_suggestion("Premium Steak", 200.0)
        self.assertEqual(res_a["estimated_profit"], 300)
        self.assertEqual(res_a["profit_margin"], 60)
        self.assertEqual(res_a["category"], "HIGH")
        
        # Scenario B: Margin of 50% (MEDIUM)
        # Cost: 250, Price: 500 -> Profit: 250 -> Margin: (250/500)*100 = 50%
        mock_router.return_value = {
            "status": "success",
            "provider": "gemini",
            "response": '{"dish": "Burger", "recommended_price": 500, "reason": "Gourmet burger", "language": "english"}'
        }
        res_b = self.service.generate_pricing_suggestion("Burger", 250.0)
        self.assertEqual(res_b["estimated_profit"], 250)
        self.assertEqual(res_b["profit_margin"], 50)
        self.assertEqual(res_b["category"], "MEDIUM")
        
        # Scenario C: Margin of 30% (LOW)
        # Cost: 350, Price: 500 -> Profit: 150 -> Margin: (150/500)*100 = 30%
        mock_router.return_value = {
            "status": "success",
            "provider": "gemini",
            "response": '{"dish": "Salad", "recommended_price": 500, "reason": "Fresh greens", "language": "english"}'
        }
        res_c = self.service.generate_pricing_suggestion("Salad", 350.0)
        self.assertEqual(res_c["estimated_profit"], 150)
        self.assertEqual(res_c["profit_margin"], 30)
        self.assertEqual(res_c["category"], "LOW")
        print("✓ Test 3: Profit, margin, and category calculations - PASS")

    @patch("app.services.pricing_service.KnowledgeRetriever.retrieve")
    @patch("app.services.pricing_service.LLMRouter.generate")
    @patch("app.services.pricing_service.build_pricing_prompt")
    def test_04_prompt_parameters(self, mock_build_prompt, mock_router, mock_retrieve):
        """Verify prompt builder parameter mapping."""
        mock_retrieve.return_value = []
        mock_router.return_value = {"status": "success", "response": "{}"}
        
        self.service.generate_pricing_suggestion("Samosa", 10.0)
        
        mock_build_prompt.assert_called_once()
        args = mock_build_prompt.call_args[0]
        self.assertEqual(args[0], "Samosa")
        self.assertEqual(args[1], 10.0)
        print("✓ Test 4: Prompt builder parameters - PASS")

    @patch("app.services.pricing_service.KnowledgeRetriever.retrieve")
    @patch("app.services.pricing_service.LLMRouter.generate")
    def test_05_parser_fallback(self, mock_router, mock_retrieve):
        """Verify that JSON parser errors trigger standard 3x markup fallbacks."""
        mock_retrieve.return_value = []
        # Non-JSON chat response
        mock_router.return_value = {
            "status": "success",
            "response": "Sure, here is the suggested selling price: 300 rupees."
        }
        
        # Cost: 100 -> markup 3x -> price: 300 -> profit: 200 -> margin: 66% -> Category: HIGH
        result = self.service.generate_pricing_suggestion("Paneer Tikka", 100.0)
        
        self.assertEqual(result["recommended_price"], 300)
        self.assertEqual(result["estimated_profit"], 200)
        self.assertEqual(result["profit_margin"], 66)
        self.assertEqual(result["category"], "HIGH")
        self.assertIn("BOH 3x markup", result["reason"])
        print("✓ Test 5: Parsing fallback recovery - PASS")

def run_tests():
    print("==================================================")
    print("KitchenSync Profit Suggestion Engine Verification")
    print("==================================================")
    
    suite = unittest.TestLoader().loadTestsFromTestCase(TestPricingEngine)
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
