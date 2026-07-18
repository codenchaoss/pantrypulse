import sys
import os
import unittest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

# Ensure the app directory is on the python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from app.main import app

class TestFastAPILayer(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        
    def test_01_openapi_schema(self):
        """Verify Swagger OpenAPI metadata is accessible and registers correct routes."""
        response = self.client.get("/openapi.json")
        self.assertEqual(response.status_code, 200)
        schema = response.json()
        self.assertEqual(schema["info"]["title"], "KitchenSync AI Service")
        self.assertEqual(schema["info"]["version"], "1.1")
        
        # Verify routes are present in OpenAPI spec
        paths = schema.get("paths", {})
        self.assertIn("/health", paths)
        self.assertIn("/chat", paths)
        self.assertIn("/recipe", paths)
        self.assertIn("/menu", paths)
        self.assertIn("/supplier", paths)
        print("✓ Test 1: Swagger OpenAPI Availability & Paths - PASS")

    def test_02_middleware_headers(self):
        """Verify logging middleware executes and appends request tracking headers."""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertIn("X-Request-ID", response.headers)
        self.assertIn("X-Process-Time-Ms", response.headers)
        print("✓ Test 2: Request ID Middleware headers - PASS")

    def test_03_health_endpoint(self):
        """Verify GET /health returns structured health check status payload."""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertIn("data", data)
        self.assertIn("rag", data["data"])
        self.assertIn("faiss", data["data"])
        self.assertIn("gemini", data["data"])
        self.assertIn("openrouter", data["data"])
        print("✓ Test 3: Health Endpoint payload structure - PASS")

    def test_04_chat_validation_error(self):
        """Verify POST /chat returns HTTP 422 validation schema error on empty question."""
        response = self.client.post("/chat", json={"question": ""})
        self.assertEqual(response.status_code, 422)
        data = response.json()
        self.assertFalse(data["success"])
        self.assertIn("errors", data["data"])
        print("✓ Test 4: Chat input validation handler - PASS")

    @patch("app.services.chatbot_service.LLMRouter.generate")
    @patch("app.services.chatbot_service.KnowledgeRetriever.retrieve")
    def test_05_chat_success(self, mock_retrieve, mock_gen):
        """Verify POST /chat returns structured ApiResponse format on valid request."""
        mock_retrieve.return_value = [
            {"source": "safety.json", "title": "Salmon Temp", "content": "Chill salmon at 4C."}
        ]
        mock_gen.return_value = {
            "status": "success",
            "provider": "gemini",
            "model": "gemini-2.5-flash",
            "response": "Store salmon at 4C.",
            "response_time_ms": 100,
            "fallback_used": False
        }
        response = self.client.post("/chat", json={"question": "How to store salmon?"})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["data"]["answer"], "Store salmon at 4C.")
        self.assertEqual(data["data"]["metadata"]["provider"], "gemini")
        print("✓ Test 5: Chat Endpoint response validation - PASS")

    def test_06_recipe_success(self):
        """Verify POST /recipe returns recommended recipes list."""
        response = self.client.post("/recipe", json={"ingredients": ["Chicken", "Butter"]})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertIn("recipes", data["data"])
        self.assertTrue(len(data["data"]["recipes"]) > 0)
        print("✓ Test 6: Recipe recommendation response schema - PASS")

    def test_07_menu_success(self):
        """Verify POST /menu returns daily specials."""
        payload = {
            "inventory": [
                {"ingredient": "Salmon", "quantity": "5kg", "expiry_days": 1}
            ]
        }
        response = self.client.post("/menu", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertIn("menu", data["data"])
        self.assertTrue(len(data["data"]["menu"]) > 0)
        print("✓ Test 7: Menu generation response schema - PASS")

    def test_08_supplier_success(self):
        """Verify POST /supplier returns formatted message draft."""
        response = self.client.post("/supplier", json={"ingredient": "Salmon", "quantity": "10kg"})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertIn("message", data["data"])
        self.assertIn("Dear Wholesale", data["data"]["message"])
        print("✓ Test 8: Supplier restocking response schema - PASS")

def run_tests():
    print("==================================================")
    print("KitchenSync API & FastAPI Layer Verification Suite")
    print("==================================================")
    
    suite = unittest.TestLoader().loadTestsFromTestCase(TestFastAPILayer)
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
