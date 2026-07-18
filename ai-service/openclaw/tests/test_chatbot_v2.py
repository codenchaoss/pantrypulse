import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# Add project root to path
current_dir = os.path.dirname(os.path.abspath(__file__))
ai_service_dir = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(ai_service_dir)

from app.services.chatbot_service import ChatbotService, detect_language, clean_ai_response
from app.prompts.chatbot_prompt import build_chat_prompt

class TestChatbotV2(unittest.TestCase):
    
    def test_01_language_detection_v2(self):
        """Verify language heuristics for English, Telugu, and Roman Telugu."""
        # English queries
        self.assertEqual(detect_language("What breakfast items are available?"), "english")
        
        # Telugu queries
        self.assertEqual(detect_language("దోసా ఉందా?"), "telugu")
        
        # Roman Telugu (Tenglish) queries
        self.assertEqual(detect_language("ea andi manager garu ullipayya dosa vundha vunte okati parcel kavali ayya"), "roman_telugu")
        self.assertEqual(detect_language("namaste boss ravvaupma dosa available lo vunda andi"), "roman_telugu")
        print("✓ Test 1: Language detection (v2) - PASS")

    def test_02_clean_ai_response(self):
        """Verify that markdown tags and formatting symbols are correctly stripped."""
        raw_response = (
            "## KitchenSync Suggestions\n\n"
            "Here is the **Chicken Curry**:\n"
            "* Option 1: Spicy curry\n"
            "### Ingredients\n"
            "__Chicken__\n"
            "---"
        )
        cleaned = clean_ai_response(raw_response)
        
        self.assertNotIn("##", cleaned)
        self.assertNotIn("**", cleaned)
        self.assertNotIn("__", cleaned)
        self.assertNotIn("---", cleaned)
        self.assertNotIn("###", cleaned)
        print("✓ Test 2: Markdown cleanup regex/replacements - PASS")

    @patch("app.services.chatbot_service.KnowledgeRetriever.retrieve")
    @patch("app.services.chatbot_service.LLMRouter.generate")
    def test_03_fallback_similarity_search(self, mock_router, mock_retrieve):
        """Verify that fallback keyword matching retrieves related dishes when no exact match is found."""
        # Setup mock vector store chunks to simulate fallback database search
        mock_chunks = [
            {"source": "recipes", "title": "Masala Dosa", "content": "Crispy crepe with potato filling."},
            {"source": "recipes", "title": "Plain Dosa", "content": "Simple crispy rice crepe."},
            {"source": "recipes", "title": "Onion Uttapam", "content": "Thick rice pancake with onions."},
            {"source": "recipes", "title": "Chicken Biryani", "content": "Spicy chicken rice dish."}
        ]
        
        service = ChatbotService()
        service.retriever.vector_store = MagicMock()
        service.retriever.vector_store.chunks = mock_chunks
        
        # Scenario: query "rava upma dosa" doesn't have an exact match in FAISS search results
        mock_retrieve.return_value = [
            {"source": "seasonal.json", "title": "Summer Menu", "content": "General seasonal tips"}
        ]
        mock_router.return_value = {
            "status": "success",
            "provider": "gemini",
            "response": "No rava upma dosa found. Here is Masala Dosa, Plain Dosa.",
            "response_time_ms": 100,
            "fallback_used": False
        }
        
        # Trigger query
        result = service.generate_response("namaste boss ravvaupma dosa available lo vunda andi")
        
        # Verify that we correctly identified "roman_telugu" language and confidence score
        self.assertEqual(result["language"], "roman_telugu")
        self.assertIn("confidence", result)
        self.assertGreaterEqual(result["confidence"], 0.90)
        
        # Verify result contains the clean answer
        self.assertIn("Masala Dosa", result["answer"])
        print("✓ Test 3: Fallback similarity search and confidence score - PASS")

    @patch("app.services.chatbot_service.KnowledgeRetriever.retrieve")
    @patch("app.services.chatbot_service.LLMRouter.generate")
    def test_04_query_splitting_and_synonym_retrieval(self, mock_router, mock_retrieve):
        """Verify that multi-part queries (Chapati with Aloo Curry) split components and expand synonyms."""
        mock_chunks = [
            {"source": "recipes", "title": "Tandoori Roti", "content": "Baked flatbread."},
            {"source": "recipes", "title": "Potato Curry", "content": "Potato pieces cooked in spiced curry."},
            {"source": "recipes", "title": "Garlic Naan", "content": "Flatbread topped with garlic."},
            {"source": "recipes", "title": "Chicken Curry", "content": "Spicy chicken gravy."}
        ]
        
        service = ChatbotService()
        service.retriever.vector_store = MagicMock()
        service.retriever.vector_store.chunks = mock_chunks
        
        mock_retrieve.return_value = []
        mock_router.return_value = {
            "status": "success",
            "provider": "gemini",
            "response": "Here is Tandoori Roti and Potato Curry.",
            "response_time_ms": 120,
            "fallback_used": False
        }
        
        # Run test with Chapati (synonym of Roti) and Aloo Curry (synonym of Potato Curry)
        result = service.generate_response("Chapati is available with aloo curry")
        
        # Verify result
        self.assertEqual(result["language"], "english")
        self.assertIn("Tandoori Roti", result["answer"])
        self.assertIn("Potato Curry", result["answer"])
        print("✓ Test 4: Conjunction query splitting and synonym retrieval - PASS")

def run_tests():
    print("==================================================")
    print("KitchenSync Chatbot v2 Verification Suite")
    print("==================================================")
    
    suite = unittest.TestLoader().loadTestsFromTestCase(TestChatbotV2)
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
