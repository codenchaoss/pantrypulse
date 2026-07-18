import sys
import os
import unittest
from unittest.mock import patch, MagicMock
from fastapi import HTTPException

# Ensure the app directory is on the python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from app.services.description_service import DescriptionService, detect_language

class TestDescriptionGenerator(unittest.TestCase):
    
    def setUp(self):
        self.service = DescriptionService()

    def test_01_request_validation(self):
        """Verify that empty arrays or blank names trigger validation errors."""
        # Empty array
        with self.assertRaises(HTTPException) as context:
            self.service.generate_descriptions([])
        self.assertEqual(context.exception.status_code, 400)
        self.assertIn("cannot be empty", context.exception.detail)
        
        # Blank dish name
        with self.assertRaises(HTTPException) as context2:
            self.service.generate_descriptions([{"dish": "   ", "category": "Main Course"}])
        self.assertEqual(context2.exception.status_code, 400)
        self.assertIn("Dish name cannot be empty", context2.exception.detail)
        print("✓ Test 1: Request and dish validation - PASS")

    def test_02_language_propagation(self):
        """Verify script language detection mappings for English, Telugu, and Tenglish."""
        self.assertEqual(detect_language("Butter Chicken"), "english")
        self.assertEqual(detect_language("సాల్మన్ ఫ్రై"), "telugu")
        self.assertEqual(detect_language("Chicken fry ela cheyyali"), "tenglish")
        print("✓ Test 2: Language propagation and script heuristics - PASS")

    @patch("app.services.description_service.KnowledgeRetriever.retrieve")
    @patch("app.services.description_service.LLMRouter.generate")
    def test_03_order_preservation_and_deduplication(self, mock_router, mock_retrieve):
        """Verify that duplicates are stripped and original request sorting is preserved."""
        mock_retrieve.return_value = [
            {"source": "recipes.json", "title": "D1", "content": "..."}
        ]
        
        # Scrambled dishes response from LLM, missing D2
        mock_router.return_value = {
            "status": "success",
            "provider": "gemini",
            "response": (
                '{"descriptions": ['
                '{"dish": "D3", "description": "Desc three", "tone": "Premium", "language": "english"},'
                '{"dish": "D1", "description": "Desc one", "tone": "Premium", "language": "english"}'
                ']}'
            )
        }
        
        # Duplicate D1 in input list
        input_dishes = [
            {"dish": "D1", "category": "C1"},
            {"dish": "D2", "category": "C2"},
            {"dish": "D3", "category": "C3"},
            {"dish": "D1", "category": "C1"}
        ]
        
        result = self.service.generate_descriptions(input_dishes)
        descriptions = result["descriptions"]
        
        # Ordering must match input order (size: 4 items as requested, D1 duplicated at the end)
        self.assertEqual(len(descriptions), 4)
        
        # Check ordering: D1 -> D2 -> D3 -> D1
        self.assertEqual(descriptions[0]["dish"], "D1")
        self.assertEqual(descriptions[0]["description"], "Desc one")
        
        self.assertEqual(descriptions[1]["dish"], "D2")
        # D2 was missing from LLM result, should trigger heuristic fallback description
        self.assertIn("Savor our delicious and premium D2", descriptions[1]["description"])
        
        self.assertEqual(descriptions[2]["dish"], "D3")
        self.assertEqual(descriptions[2]["description"], "Desc three")
        
        self.assertEqual(descriptions[3]["dish"], "D1")
        self.assertEqual(descriptions[3]["description"], "Desc one")
        print("✓ Test 3: Deduplication and stable input order preservation - PASS")

    @patch("app.services.description_service.KnowledgeRetriever.retrieve")
    @patch("app.services.description_service.LLMRouter.generate")
    def test_04_json_schema_output(self, mock_router, mock_retrieve):
        """Verify response schema alignment mapping of output descriptions."""
        mock_retrieve.return_value = [
            {"source": "recipes.json", "title": "Garlic Butter Chicken", "content": "..."}
        ]
        
        mock_router.return_value = {
            "status": "success",
            "provider": "gemini",
            "response": (
                '{"descriptions": [{'
                '"dish": "Garlic Butter Chicken",'
                '"description": "Tender chicken cooked in rich garlic butter sauce with aromatic garden herbs.",'
                '"tone": "Premium",'
                '"language": "english"'
                '}]}'
            )
        }
        
        result = self.service.generate_descriptions([{"dish": "Garlic Butter Chicken"}])
        self.assertEqual(len(result["descriptions"]), 1)
        item = result["descriptions"][0]
        
        self.assertEqual(item["dish"], "Garlic Butter Chicken")
        self.assertEqual(item["description"], "Tender chicken cooked in rich garlic butter sauce with aromatic garden herbs.")
        self.assertEqual(item["tone"], "Premium")
        self.assertEqual(item["language"], "english")
        print("✓ Test 4: JSON response schema matching - PASS")

    @patch("app.services.description_service.KnowledgeRetriever.retrieve")
    @patch("app.services.description_service.LLMRouter.generate")
    def test_05_fallback_descriptions_recovery(self, mock_router, mock_retrieve):
        """Verify that JSON parser errors trigger fallback descriptions and prevent crashes."""
        mock_retrieve.return_value = [
            {"source": "recipes.json", "title": "Special Seafood Salad", "content": "Toss fresh lobster and shrimp."}
        ]
        mock_router.return_value = {
            "status": "success",
            "response": "plain conversational model text response"
        }
        
        result = self.service.generate_descriptions([{"dish": "Special Seafood Salad", "category": "Seafood"}])
        
        # Falling back to dynamic summary
        self.assertEqual(len(result["descriptions"]), 1)
        self.assertEqual(result["descriptions"][0]["dish"], "Special Seafood Salad")
        self.assertIn("lobst", result["descriptions"][0]["description"].lower())
        print("✓ Test 5: Parsing fallback recovery - PASS")

def run_tests():
    print("==================================================")
    print("KitchenSync Menu Description Generator Verification")
    print("==================================================")
    
    suite = unittest.TestLoader().loadTestsFromTestCase(TestDescriptionGenerator)
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
