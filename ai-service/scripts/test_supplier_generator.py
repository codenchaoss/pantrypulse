import sys
import os
import unittest
from unittest.mock import patch, MagicMock
from fastapi import HTTPException

# Ensure the app directory is on the python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from app.services.supplier_service import SupplierService, detect_language

class TestSupplierGenerator(unittest.TestCase):
    
    def setUp(self):
        self.service = SupplierService()

    def test_01_request_validation(self):
        """Verify that empty inputs throw correct HTTP 400 validation exceptions."""
        # Empty ingredient
        with self.assertRaises(HTTPException) as context:
            self.service.generate_supplier_message("", "20 kg", "Fresh Foods", "Tomorrow")
        self.assertEqual(context.exception.status_code, 400)
        self.assertIn("Ingredient name cannot be empty", context.exception.detail)
        
        # Empty quantity
        with self.assertRaises(HTTPException) as context2:
            self.service.generate_supplier_message("Chicken", "   ", "Fresh Foods", "Tomorrow")
        self.assertEqual(context2.exception.status_code, 400)
        self.assertIn("quantity cannot be empty", context2.exception.detail)
        
        # Empty date
        with self.assertRaises(HTTPException) as context3:
            self.service.generate_supplier_message("Chicken", "20 kg", "Fresh Foods", "")
        self.assertEqual(context3.exception.status_code, 400)
        self.assertIn("date cannot be empty", context3.exception.detail)
        print("✓ Test 1: Request parameter validations - PASS")

    def test_02_language_propagation(self):
        """Verify language heuristics for English, Telugu, and Romanized Tenglish."""
        self.assertEqual(detect_language("Fresh vendor chicken"), "english")
        self.assertEqual(detect_language("సాల్మన్ సరఫరాదారు"), "telugu")
        self.assertEqual(detect_language("order kalla delivery cheyyali"), "tenglish")
        print("✓ Test 2: Language propagation script checks - PASS")

    @patch("app.services.supplier_service.KnowledgeRetriever.retrieve")
    @patch("app.services.supplier_service.LLMRouter.generate")
    @patch("app.services.supplier_service.build_supplier_prompt")
    def test_03_prompt_compilation(self, mock_build_prompt, mock_router, mock_retrieve):
        """Verify that prompt builder compiles input supplier names, ingredients, quantities, and dates."""
        mock_retrieve.return_value = []
        mock_router.return_value = {"status": "success", "response": "{}"}
        
        self.service.generate_supplier_message("Potato", "50 kg", "Potato Farms Inc", "Friday")
        
        mock_build_prompt.assert_called_once()
        args = mock_build_prompt.call_args[0]
        self.assertEqual(args[0], "Potato Farms Inc")
        self.assertEqual(args[1], "Potato")
        self.assertEqual(args[2], "50 kg")
        self.assertEqual(args[3], "Friday")
        print("✓ Test 3: Prompt builder parameter mapping - PASS")

    @patch("app.services.supplier_service.KnowledgeRetriever.retrieve")
    @patch("app.services.supplier_service.LLMRouter.generate")
    def test_04_json_schema_validation(self, mock_router, mock_retrieve):
        """Verify that successful generation returns valid schema-conforming outputs."""
        mock_retrieve.return_value = [
            {"source": "suppliers.json", "title": "Agro Foods", "content": "Supply onion."}
        ]
        
        mock_router.return_value = {
            "status": "success",
            "provider": "gemini",
            "response": (
                '{"supplier_name": "Agro Foods Pvt Ltd",'
                '"ingredient": "Onion",'
                '"message": "Dear Agro Foods Pvt Ltd,\\n\\nPlease deliver 10 bags of onions by Friday.",'
                '"language": "english"}'
            )
        }
        
        result = self.service.generate_supplier_message("Onion", "10 bags", "Agro Foods Pvt Ltd", "Friday")
        
        self.assertEqual(result["supplier_name"], "Agro Foods Pvt Ltd")
        self.assertEqual(result["ingredient"], "Onion")
        self.assertEqual(result["message"], "Dear Agro Foods Pvt Ltd,\n\nPlease deliver 10 bags of onions by Friday.")
        self.assertEqual(result["language"], "English")
        print("✓ Test 4: JSON response schema matching - PASS")

    @patch("app.services.supplier_service.KnowledgeRetriever.retrieve")
    @patch("app.services.supplier_service.LLMRouter.generate")
    def test_05_generic_supplier_fallback(self, mock_router, mock_retrieve):
        """Verify that empty supplier names default respectfully to generic Dear Supplier."""
        mock_retrieve.return_value = []
        mock_router.return_value = {
            "status": "success",
            "provider": "gemini",
            "response": (
                '{"supplier_name": "Supplier",'
                '"ingredient": "Salt",'
                '"message": "Dear Supplier,\\n\\nWe need 5 kg of salt by tomorrow.",'
                '"language": "english"}'
            )
        }
        
        # Passing None for supplier name
        result = self.service.generate_supplier_message("Salt", "5 kg", None, "Tomorrow")
        self.assertEqual(result["supplier_name"], "Supplier")
        self.assertIn("Dear Supplier", result["message"])
        print("✓ Test 5: Generic vendor fallback naming - PASS")

    @patch("app.services.supplier_service.KnowledgeRetriever.retrieve")
    @patch("app.services.supplier_service.LLMRouter.generate")
    def test_06_parsing_error_fallback(self, mock_router, mock_retrieve):
        """Verify that JSON parser errors trigger fallback template generation."""
        mock_retrieve.return_value = []
        # LLM returns unparsable text
        mock_router.return_value = {
            "status": "success",
            "response": "Here is the email draft to order 20kg chicken."
        }
        
        result = self.service.generate_supplier_message("Chicken", "20 kg", "Fresh Foods", "Tomorrow")
        
        self.assertEqual(result["supplier_name"], "Fresh Foods")
        # Assert fallback template was drafted
        self.assertIn("Dear Fresh Foods", result["message"])
        self.assertIn("20 kg of Chicken", result["message"])
        self.assertIn("Tomorrow", result["message"])
        print("✓ Test 6: Parsing error fallback handling - PASS")

def run_tests():
    print("==================================================")
    print("KitchenSync Supplier Message Generator Verification")
    print("==================================================")
    
    suite = unittest.TestLoader().loadTestsFromTestCase(TestSupplierGenerator)
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
