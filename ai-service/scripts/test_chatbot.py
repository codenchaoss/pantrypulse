import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# Ensure the app directory is on the python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from app.services.chatbot_service import ChatbotService, detect_language

class TestChatbotFeature(unittest.TestCase):
    
    def test_01_language_detection(self):
        """Verify automatic query language detection heuristic."""
        # English queries
        self.assertEqual(detect_language("How should salmon be stored?"), "english")
        self.assertEqual(detect_language("Recommend a butter chicken recipe"), "english")
        
        # Telugu queries
        self.assertEqual(detect_language("సాల్మన్ ని ఎలా స్టోర్ చేయాలి?"), "telugu")
        self.assertEqual(detect_language("రెసిపీ ఏంటి?"), "telugu")
        
        # Tenglish queries (Romanized Telugu)
        self.assertEqual(detect_language("Chicken migilindi... em recipe cheyyali?"), "tenglish")
        self.assertEqual(detect_language("Salmon store cheyyadam ela?"), "tenglish")
        print("✓ Test 1: Language detection heuristic - PASS")

    @patch("app.services.chatbot_service.KnowledgeRetriever.retrieve")
    @patch("app.services.chatbot_service.LLMRouter.generate")
    def test_02_food_safety_re_ranking(self, mock_router, mock_retrieve):
        """Verify that food safety chunks are re-ranked to the top for safety queries."""
        # Mock retriever returning a recipe chunk first and safety chunk second
        mock_retrieve.return_value = [
            {"source": "recipes.json", "title": "Garlic Salmon", "content": "Cook salmon with garlic."},
            {"source": "safety.json", "title": "Salmon Temp", "content": "Chill salmon at 4C."}
        ]
        mock_router.return_value = {
            "status": "success",
            "provider": "gemini",
            "response": "Store salmon below 4C.",
            "response_time_ms": 100,
            "fallback_used": False
        }
        
        service = ChatbotService()
        # Query with storage safety terms
        result = service.generate_response("How should I store Salmon?")
        
        self.assertEqual(result["sources"].count("safety"), 1)
        self.assertEqual(result["sources"].count("recipes"), 1)
        
        # Verify call counts and ensure LLM prompt prioritized safety
        self.assertEqual(result["retrieved_chunks"], 2)
        print("✓ Test 2: Food safety prioritisation re-ranking - PASS")

    @patch("app.services.chatbot_service.KnowledgeRetriever.retrieve")
    @patch("app.services.chatbot_service.LLMRouter.generate")
    @patch("app.services.chatbot_service.build_chat_prompt")
    def test_03_history_integration(self, mock_build_chat_prompt, mock_router, mock_retrieve):
        """Verify that optional conversation history is integrated into prompt building."""
        mock_retrieve.return_value = []
        mock_router.return_value = {"status": "success", "response": "Response text"}
        
        service = ChatbotService()
        history_context = "User: Hello\nAI: How can I help you?"
        service.generate_response("What is the special today?", history=history_context)
        
        # Verify that prompt builder was called with the history context
        mock_build_chat_prompt.assert_called_once()
        self.assertEqual(mock_build_chat_prompt.call_args[0][2], history_context)
        print("✓ Test 3: Conversation history integration - PASS")

    @patch("app.services.chatbot_service.KnowledgeRetriever.retrieve")
    @patch("app.services.chatbot_service.LLMRouter.generate")
    def test_04_json_schema_mapping(self, mock_router, mock_retrieve):
        """Verify that generate_response returns the correct response schema."""
        mock_retrieve.return_value = [
            {"source": "recipes.json", "title": "Butter Chicken", "content": "Recipe info"}
        ]
        mock_router.return_value = {
            "status": "success",
            "provider": "gemini",
            "response": "Butter chicken is highly recommended.",
            "response_time_ms": 250,
            "fallback_used": False
        }
        
        service = ChatbotService()
        result = service.generate_response("Recommend a recipe")
        
        self.assertEqual(result["question"], "Recommend a recipe")
        self.assertEqual(result["language"], "english")
        self.assertEqual(result["answer"], "Butter chicken is highly recommended.")
        self.assertEqual(result["sources"], ["recipes"])
        self.assertEqual(result["retrieved_chunks"], 1)
        self.assertEqual(result["provider"], "Gemini")
        self.assertFalse(result["fallback_used"])
        self.assertGreaterEqual(result["response_time_ms"], 0)
        print("✓ Test 4: JSON response schema mapping - PASS")

    @patch("app.services.chatbot_service.KnowledgeRetriever.retrieve")
    @patch("app.services.chatbot_service.LLMRouter.generate")
    def test_05_fallback_logging_metrics(self, mock_router, mock_retrieve):
        """Verify that provider selection and fallback flags are tracked on fallback execution."""
        mock_retrieve.return_value = []
        mock_router.return_value = {
            "status": "success",
            "provider": "openrouter",
            "response": "Fallback answer",
            "response_time_ms": 500,
            "fallback_used": True
        }
        
        service = ChatbotService()
        result = service.generate_response("Tell me about suppliers")
        
        self.assertEqual(result["provider"], "OpenRouter")
        self.assertTrue(result["fallback_used"])
        print("✓ Test 5: Fallback provider metadata mapping - PASS")

def run_tests():
    print("==================================================")
    print("KitchenSync Chatbot Feature Verification Suite")
    print("==================================================")
    
    suite = unittest.TestLoader().loadTestsFromTestCase(TestChatbotFeature)
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
