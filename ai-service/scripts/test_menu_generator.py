import sys
import os
import unittest
from unittest.mock import patch, MagicMock
from fastapi import HTTPException

# Ensure the app directory is on the python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from app.services.menu_service import MenuService

class TestMenuGenerator(unittest.TestCase):
    
    def setUp(self):
        self.service = MenuService()

    def test_01_request_validation(self):
        """Verify that invalid inventory parameters throw correct HTTP 400 exceptions."""
        # Empty inventory list
        with self.assertRaises(HTTPException) as context:
            self.service.generate_menu([])
        self.assertEqual(context.exception.status_code, 400)
        self.assertIn("cannot be empty", context.exception.detail)
        
        # Missing ingredient name
        with self.assertRaises(HTTPException) as context2:
            self.service.generate_menu([{"ingredient": "", "quantity": "2kg", "expiry_days": 1}])
        self.assertEqual(context2.exception.status_code, 400)
        self.assertIn("valid ingredient name", context2.exception.detail)
        
        # Negative expiry days
        with self.assertRaises(HTTPException) as context3:
            self.service.generate_menu([{"ingredient": "Chicken", "quantity": "2kg", "expiry_days": -5}])
        self.assertEqual(context3.exception.status_code, 400)
        self.assertIn("cannot be negative", context3.exception.detail)
        print("✓ Test 1: Request and parameter validations - PASS")

    @patch("app.services.menu_service.KnowledgeRetriever.retrieve")
    @patch("app.services.menu_service.LLMRouter.generate")
    def test_02_expiry_prioritization(self, mock_router, mock_retrieve):
        """Verify that menu items are prioritized based on matched ingredients expiration dates."""
        mock_retrieve.return_value = [
            {"source": "recipes.json", "title": "Salmon Steak", "content": "Cook salmon"}
        ]
        
        # Mock LLM returning Salmon Steak
        mock_router.return_value = {
            "status": "success",
            "provider": "gemini",
            "response": (
                '{"special_menu": [{'
                '"dish": "Salmon Steak",'
                '"reason": "Uses salmon",'
                '"matched_inventory": ["Salmon"],'
                '"estimated_profit": 500,'
                '"priority": "LOW",'
                '"preparation_time": 20,'
                '"difficulty": "Easy",'
                '"confidence": 95'
                '}]}'
            )
        }
        
        # User inventory: Salmon expires in 1 day (should override LLM "LOW" to "HIGH")
        inventory = [{"ingredient": "Salmon", "quantity": "5kg", "expiry_days": 1}]
        result = self.service.generate_menu(inventory)
        
        self.assertEqual(len(result["special_menu"]), 1)
        # Assert priority overridden to HIGH programmatically
        self.assertEqual(result["special_menu"][0]["priority"], "HIGH")
        print("✓ Test 2: Inventory expiry priority overriding - PASS")

    @patch("app.services.menu_service.KnowledgeRetriever.retrieve")
    @patch("app.services.menu_service.LLMRouter.generate")
    def test_03_stable_sorting_rules(self, mock_router, mock_retrieve):
        """Verify that daily specials are sorted by Priority weight, profit, and confidence score."""
        mock_retrieve.return_value = [
            {"source": "recipes.json", "title": "R1", "content": "..."}
        ]
        
        # Scrambled dishes from LLM response
        mock_router.return_value = {
            "status": "success",
            "provider": "gemini",
            "response": (
                '{"special_menu": ['
                '{"dish": "Low profit High priority", "matched_inventory": ["expiring_item"], "estimated_profit": 100, "confidence": 90},'
                '{"dish": "High profit Medium priority", "matched_inventory": ["medium_item"], "estimated_profit": 600, "confidence": 90},'
                '{"dish": "High profit High priority", "matched_inventory": ["expiring_item"], "estimated_profit": 500, "confidence": 95},'
                '{"dish": "High profit High priority lower confidence", "matched_inventory": ["expiring_item"], "estimated_profit": 500, "confidence": 80}'
                ']}'
            )
        }
        
        inventory = [
            {"ingredient": "expiring_item", "quantity": "1kg", "expiry_days": 1},
            {"ingredient": "medium_item", "quantity": "1kg", "expiry_days": 4}
        ]
        
        result = self.service.generate_menu(inventory)
        specials = result["special_menu"]
        
        self.assertEqual(len(specials), 4)
        # 1. High profit High priority (HIGH, 500 profit, 95 confidence)
        self.assertEqual(specials[0]["dish"], "High profit High priority")
        # 2. High profit High priority lower confidence (HIGH, 500 profit, 80 confidence)
        self.assertEqual(specials[1]["dish"], "High profit High priority lower confidence")
        # 3. Low profit High priority (HIGH, 100 profit, 90 confidence)
        self.assertEqual(specials[2]["dish"], "Low profit High priority")
        # 4. High profit Medium priority (MEDIUM, 600 profit, 90 confidence)
        self.assertEqual(specials[3]["dish"], "High profit Medium priority")
        print("✓ Test 3: Stable sorting algorithms - PASS")

    @patch("app.services.menu_service.KnowledgeRetriever.retrieve")
    @patch("app.services.menu_service.LLMRouter.generate")
    def test_04_capping_to_five(self, mock_router, mock_retrieve):
        """Verify that final generated daily specials are capped to a maximum of 5 items."""
        mock_retrieve.return_value = [
            {"source": "recipes.json", "title": "R1", "content": "..."}
        ]
        
        # LLM returns 7 items
        mock_router.return_value = {
            "status": "success",
            "response": (
                '{"special_menu": ['
                '{"dish": "D1", "matched_inventory": ["i1"], "estimated_profit": 100, "confidence": 80},'
                '{"dish": "D2", "matched_inventory": ["i1"], "estimated_profit": 200, "confidence": 80},'
                '{"dish": "D3", "matched_inventory": ["i1"], "estimated_profit": 300, "confidence": 80},'
                '{"dish": "D4", "matched_inventory": ["i1"], "estimated_profit": 400, "confidence": 80},'
                '{"dish": "D5", "matched_inventory": ["i1"], "estimated_profit": 500, "confidence": 80},'
                '{"dish": "D6", "matched_inventory": ["i1"], "estimated_profit": 600, "confidence": 80},'
                '{"dish": "D7", "matched_inventory": ["i1"], "estimated_profit": 700, "confidence": 80}'
                ']}'
            )
        }
        
        inventory = [{"ingredient": "i1", "quantity": "1kg", "expiry_days": 10}]
        result = self.service.generate_menu(inventory)
        
        self.assertEqual(len(result["special_menu"]), 5)
        print("✓ Test 4: Maximum specials capping (max 5) - PASS")

    @patch("app.services.menu_service.KnowledgeRetriever.retrieve")
    @patch("app.services.menu_service.LLMRouter.generate")
    def test_05_duplicates_removal(self, mock_router, mock_retrieve):
        """Verify that duplicate dishes are filtered from the output."""
        mock_retrieve.return_value = [
            {"source": "recipes.json", "title": "R1", "content": "..."}
        ]
        
        mock_router.return_value = {
            "status": "success",
            "response": (
                '{"special_menu": ['
                '{"dish": "Pasta", "matched_inventory": ["i1"], "estimated_profit": 100},'
                '{"dish": "PASTA", "matched_inventory": ["i1"], "estimated_profit": 200},'
                '{"dish": "Garlic Rice", "matched_inventory": ["i1"], "estimated_profit": 300}'
                ']}'
            )
        }
        
        inventory = [{"ingredient": "i1", "quantity": "1kg", "expiry_days": 10}]
        result = self.service.generate_menu(inventory)
        
        self.assertEqual(len(result["special_menu"]), 2)
        self.assertEqual(result["special_menu"][0]["dish"], "Garlic Rice") # 300 profit
        self.assertEqual(result["special_menu"][1]["dish"], "Pasta") # 100 profit
        print("✓ Test 5: Duplicate menu specials removal - PASS")

    @patch("app.services.menu_service.KnowledgeRetriever.retrieve")
    @patch("app.services.menu_service.LLMRouter.generate")
    def test_06_parser_fallback(self, mock_router, mock_retrieve):
        """Verify that JSON parser errors trigger safe heuristic database fallbacks."""
        mock_retrieve.return_value = [
            {"source": "recipes.json", "title": "Garlic Butter Chicken", "content": "Cook chicken in butter sauce."}
        ]
        mock_router.return_value = {
            "status": "success",
            "response": "random non-json chat text response"
        }
        
        inventory = [{"ingredient": "Chicken", "quantity": "5kg", "expiry_days": 1}]
        result = self.service.generate_menu(inventory)
        
        self.assertEqual(len(result["special_menu"]), 1)
        self.assertEqual(result["special_menu"][0]["dish"], "Garlic Butter Chicken")
        self.assertEqual(result["special_menu"][0]["priority"], "HIGH")
        print("✓ Test 6: Parsing fallback recovery - PASS")

def run_tests():
    print("==================================================")
    print("KitchenSync Daily Menu Generator Verification")
    print("==================================================")
    
    suite = unittest.TestLoader().loadTestsFromTestCase(TestMenuGenerator)
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
