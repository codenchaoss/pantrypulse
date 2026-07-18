import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# Ensure the app directory is on the python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from app.core import config
from app.llm.prompt_builder import PromptBuilder
from app.llm.output_parser import OutputParser
from app.llm.gemini_client import GeminiClient
from app.llm.openrouter_client import OpenRouterClient
from app.llm.llm_router import LLMRouter

class TestLLMLayer(unittest.TestCase):
    
    def test_01_configuration_loading(self):
        """Verify configuration variables are successfully loaded."""
        self.assertIsNotNone(config.PRIMARY_PROVIDER, "PRIMARY_PROVIDER should be defined")
        self.assertIsNotNone(config.FALLBACK_PROVIDER, "FALLBACK_PROVIDER should be defined")
        self.assertIsNotNone(config.PRIMARY_MODEL, "PRIMARY_MODEL should be defined")
        self.assertIsNotNone(config.FALLBACK_MODEL, "FALLBACK_MODEL should be defined")
        
        # Keys can be empty strings but should be defined
        self.assertIsInstance(config.GEMINI_API_KEY, str)
        self.assertIsInstance(config.OPENROUTER_API_KEY, str)
        print("✓ Test 1: Configuration Loading - PASS")

    def test_02_prompt_builder(self):
        """Verify PromptBuilder constructs correct templates including context, question, and metadata."""
        query = "How to store chicken?"
        chunks = [
            {"source": "safety.json", "title": "Poultry Storage", "content": "Keep chicken at or below 40F."}
        ]
        meta = {"user_role": "head_chef"}
        
        prompt = PromptBuilder.build_prompt(query, chunks, meta)
        self.assertIn("KitchenSync AI", prompt)
        self.assertIn("Keep chicken at or below 40F.", prompt)
        self.assertIn("How to store chicken?", prompt)
        self.assertIn("user_role", prompt)
        print("✓ Test 2: Prompt Builder Formatting - PASS")

    def test_03_output_parser_normalization(self):
        """Verify OutputParser enforces uniform schema for both success and fallback."""
        success_out = OutputParser.format_output(
            response="Test response",
            provider="gemini",
            model="gemini-2.5-flash",
            response_time_ms=1200,
            fallback_used=False
        )
        self.assertEqual(success_out["status"], "success")
        self.assertEqual(success_out["provider"], "gemini")
        self.assertEqual(success_out["model"], "gemini-2.5-flash")
        self.assertEqual(success_out["response"], "Test response")
        self.assertEqual(success_out["response_time_ms"], 1200)
        self.assertFalse(success_out["fallback_used"])

        fallback_out = OutputParser.format_output(
            response="Fallback response",
            provider="openrouter",
            model="meta-llama/llama-3.1-8b-instruct",
            response_time_ms=1500,
            fallback_used=True
        )
        self.assertEqual(fallback_out["status"], "success")
        self.assertEqual(fallback_out["provider"], "openrouter")
        self.assertEqual(fallback_out["model"], "meta-llama/llama-3.1-8b-instruct")
        self.assertEqual(fallback_out["response"], "Fallback response")
        self.assertEqual(fallback_out["response_time_ms"], 1500)
        self.assertTrue(fallback_out["fallback_used"])
        print("✓ Test 3: Output Parser Normalization - PASS")

    @patch("httpx.post")
    def test_04_gemini_client_success(self, mock_post):
        """Verify GeminiClient returns successful structured responses."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "candidates": [
                {
                    "content": {
                        "parts": [{"text": "Gemini answer text"}]
                    }
                }
            ]
        }
        mock_post.return_value = mock_response

        client = GeminiClient(api_key="dummy_key")
        result = client.generate("Hello Gemini")
        
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["text"], "Gemini answer text")
        self.assertIsNone(result["error"])
        print("✓ Test 4: Gemini Client Success - PASS")

    @patch("httpx.post")
    def test_05_gemini_client_quota_exhausted(self, mock_post):
        """Verify GeminiClient handles 429 quota exhausted error gracefully."""
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_response.json.return_value = {
            "error": {"message": "Resource has been exhausted (e.g. queries per minute)."}
        }
        mock_post.return_value = mock_response

        client = GeminiClient(api_key="dummy_key")
        result = client.generate("Hello Gemini")
        
        self.assertEqual(result["status"], "error")
        self.assertIn("HTTP 429", result["error"])
        print("✓ Test 5: Gemini Client Quota/Rate Limit Handling - PASS")

    @patch("httpx.post")
    def test_06_openrouter_client_success(self, mock_post):
        """Verify OpenRouterClient returns successful OpenAI-compatible structured responses."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {"content": "OpenRouter answer text"}
                }
            ]
        }
        mock_post.return_value = mock_response

        client = OpenRouterClient(api_key="dummy_key")
        result = client.generate("Hello OpenRouter")
        
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["text"], "OpenRouter answer text")
        self.assertIsNone(result["error"])
        print("✓ Test 6: OpenRouter Client Success - PASS")

    @patch("app.llm.gemini_client.GeminiClient.generate")
    def test_07_router_success_first_attempt(self, mock_gemini_generate):
        """Verify LLMRouter succeeds on the first try using the primary provider."""
        mock_gemini_generate.return_value = {
            "status": "success",
            "text": "Success on first try",
            "error": None
        }

        router = LLMRouter()
        result = router.generate("Test query")
        
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["provider"], "gemini")
        self.assertEqual(result["response"], "Success on first try")
        self.assertFalse(result["fallback_used"])
        self.assertEqual(mock_gemini_generate.call_count, 1)
        print("✓ Test 7: Router Success on Initial Attempt - PASS")

    @patch("app.llm.gemini_client.GeminiClient.generate")
    def test_08_router_retry_logic(self, mock_gemini_generate):
        """Verify LLMRouter retry logic works up to 2 retry attempts (3 calls total)."""
        # 1st call fails, 2nd call succeeds
        mock_gemini_generate.side_effect = [
            {"status": "error", "text": "", "error": "Transient Network Error"},
            {"status": "success", "text": "Success on second try", "error": None}
        ]

        router = LLMRouter()
        result = router.generate("Test query")
        
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["provider"], "gemini")
        self.assertEqual(result["response"], "Success on second try")
        self.assertFalse(result["fallback_used"])
        self.assertEqual(mock_gemini_generate.call_count, 2)
        print("✓ Test 8: Router Retry Logic - PASS")

    @patch("app.llm.openrouter_client.OpenRouterClient.generate")
    @patch("app.llm.gemini_client.GeminiClient.generate")
    def test_09_router_fallback_logic(self, mock_gemini_generate, mock_openrouter_generate):
        """Verify LLMRouter switches to fallback provider if primary fails 3 times."""
        # Gemini fails all 3 attempts
        mock_gemini_generate.return_value = {
            "status": "error",
            "text": "",
            "error": "Persistent Quota Error"
        }
        # OpenRouter succeeds
        mock_openrouter_generate.return_value = {
            "status": "success",
            "text": "Success on fallback",
            "error": None
        }

        router = LLMRouter()
        result = router.generate("Test query")
        
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["provider"], "openrouter")
        self.assertEqual(result["response"], "Success on fallback")
        self.assertTrue(result["fallback_used"])
        self.assertEqual(mock_gemini_generate.call_count, 3)
        self.assertEqual(mock_openrouter_generate.call_count, 1)
        print("✓ Test 9: Router Fallback Activation - PASS")

def run_tests():
    print("==================================================")
    print("KitchenSync LLM Layer Verification Suite")
    print("==================================================")
    
    suite = unittest.TestLoader().loadTestsFromTestCase(TestLLMLayer)
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
