import unittest
from unittest.mock import MagicMock, patch
from app.llm.provider_manager import ProviderManager
from app.llm.provider_registry import ProviderRegistry

class TestProviderManager(unittest.TestCase):
    def setUp(self):
        self.manager = ProviderManager()

    def test_provider_manager_initialization(self):
        # Registry has all 7 providers
        self.assertEqual(len(self.manager.registry.priority_order), 7)
        self.assertIn("gemini", self.manager.registry.priority_order)
        self.assertIn("grok", self.manager.registry.priority_order)
        self.assertIn("openrouter", self.manager.registry.priority_order)

    @patch("app.llm.provider_registry.ProviderRegistry.get_active_providers_in_order")
    def test_routing_first_successful_provider(self, mock_active):
        mock_active.return_value = ["gemini", "grok"]
        
        mock_gemini = MagicMock()
        mock_gemini.generate.return_value = {"status": "success", "text": "Gemini response"}
        mock_gemini.model = "gemini-2.5-flash"
        
        mock_grok = MagicMock()
        
        with patch.object(self.manager.registry, "get_provider", side_effect=lambda name: mock_gemini if name == "gemini" else mock_grok):
            res = self.manager.generate("test prompt")
            self.assertEqual(res["status"], "success")
            self.assertEqual(res["text"], "Gemini response")
            self.assertEqual(res["provider"], "gemini")
            mock_grok.generate.assert_not_called()

    @patch("app.llm.provider_registry.ProviderRegistry.get_active_providers_in_order")
    def test_fallback_on_first_provider_failure(self, mock_active):
        mock_active.return_value = ["gemini", "grok"]
        
        mock_gemini = MagicMock()
        mock_gemini.generate.return_value = {"status": "error", "error": "Quota exceeded"}
        
        mock_grok = MagicMock()
        mock_grok.generate.return_value = {"status": "success", "text": "Grok response"}
        mock_grok.model = "grok-beta"
        
        with patch.object(self.manager.registry, "get_provider", side_effect=lambda name: mock_gemini if name == "gemini" else mock_grok):
            res = self.manager.generate("test prompt")
            self.assertEqual(res["status"], "success")
            self.assertEqual(res["text"], "Grok response")
            self.assertEqual(res["provider"], "grok")

    def test_rag_fallback_when_all_fail(self):
        # Empty active providers queue to simulate all offline/unconfigured
        with patch.object(self.manager.registry, "get_active_providers_in_order", return_value=[]):
            chunks = [
                {
                    "source": "recipes",
                    "title": "Paneer Butter Masala",
                    "content": '{"recipe_name": "Paneer Butter Masala", "preparation_time_minutes": 25, "ingredients": ["Paneer", "Butter", "Tomato", "Cream"], "category": "North Indian", "description": "Rich cottage cheese curry."}'
                }
            ]
            res = self.manager.generate("how to make paneer", context_chunks=chunks)
            self.assertEqual(res["status"], "success")
            self.assertEqual(res["provider"], "RAG-only Fallback")
            self.assertIn("Paneer Butter Masala", res["text"])
            self.assertIn("Preparation Time:\n25 mins", res["text"])
            self.assertIn("Ingredients:\n• Paneer\n• Butter", res["text"])

    def test_rag_fallback_empty_chunks(self):
        with patch.object(self.manager.registry, "get_active_providers_in_order", return_value=[]):
            res = self.manager.generate("how to make paneer", context_chunks=[])
            self.assertEqual(res["status"], "success")
            self.assertEqual(res["text"], "I'm unable to find relevant information in the restaurant knowledge base.")
