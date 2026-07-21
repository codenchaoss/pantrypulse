import unittest
from app.routing.intent_router import IntentRouter
from app.models.intent_models import Intent, Route

class TestIntentRouter(unittest.TestCase):
    """
    Unit tests for Phase 2 IntentRouter module.
    """

    def setUp(self):
        self.router = IntentRouter()

    def test_detect_inventory_intent(self):
        res = self.router.detect_intent("Show current ingredients stock levels")
        self.assertEqual(res.intent, Intent.INVENTORY)
        self.assertEqual(res.route, Route.SPRING_INVENTORY)
        self.assertTrue("ingredients" in res.matched_keywords or "stock" in res.matched_keywords)

    def test_detect_supplier_intent(self):
        res = self.router.detect_intent("find active vendors email list")
        self.assertEqual(res.intent, Intent.SUPPLIER)
        self.assertEqual(res.route, Route.SPRING_SUPPLIERS)

    def test_detect_knowledge_intent(self):
        res = self.router.detect_intent("how should raw chicken be stored")
        self.assertEqual(res.intent, Intent.KNOWLEDGE)
        self.assertEqual(res.route, Route.PINECONE)

    def test_detect_hybrid_intent(self):
        res = self.router.detect_intent("suggest menu options using available tomatoes")
        self.assertEqual(res.intent, Intent.HYBRID)
        self.assertEqual(res.route, Route.HYBRID)

    def test_detect_general_chat_intent(self):
        res = self.router.detect_intent("hey there thanks for the help")
        self.assertEqual(res.intent, Intent.GENERAL_CHAT)
        self.assertEqual(res.route, Route.GEMINI_ONLY)

if __name__ == "__main__":
    unittest.main()
