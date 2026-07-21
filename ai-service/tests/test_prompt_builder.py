import unittest
from app.models.context_models import UnifiedContext
from app.services.prompt_builder import PromptBuilder

class TestPromptBuilder(unittest.TestCase):
    """
    Unit tests for Phase 4 PromptBuilder module.
    """

    def setUp(self):
        self.prompt_builder = PromptBuilder()

    def test_build_inventory_prompt_contains_data(self):
        ctx = UnifiedContext(
            intent="INVENTORY",
            route="SPRING_INVENTORY",
            live_data={"inventory": [{"ingredientName": "Tomatoes", "quantity": 10.0, "unit": "kg", "category": "VEGETABLES"}]},
            knowledge=[],
            metadata={"spring_calls": ["GET /api/inventory"], "pinecone_used": False}
        )
        
        prompt_obj = self.prompt_builder.build_prompt("Show stock levels", ctx)
        
        self.assertEqual(prompt_obj.intent, "INVENTORY")
        self.assertEqual(prompt_obj.route, "SPRING_INVENTORY")
        self.assertTrue("=== RESTAURANT LIVE STOCK INVENTORY ===" in prompt_obj.user_prompt)
        self.assertTrue("Tomatoes" in prompt_obj.user_prompt)
        self.assertTrue("10.0 kg" in prompt_obj.user_prompt)
        self.assertFalse("=== RAG KNOWLEDGE BASE DOMAIN TIPS ===" in prompt_obj.user_prompt)

    def test_build_knowledge_prompt_contains_rag_chunks(self):
        ctx = UnifiedContext(
            intent="KNOWLEDGE",
            route="PINECONE",
            live_data={},
            knowledge=[{"source": "safety", "title": "Danger Zone", "content": "Keep food out of 40F to 140F"}],
            metadata={"spring_calls": [], "pinecone_used": True}
        )
        
        prompt_obj = self.prompt_builder.build_prompt("Explain danger zone", ctx)
        
        self.assertEqual(prompt_obj.intent, "KNOWLEDGE")
        self.assertTrue("=== RAG KNOWLEDGE BASE DOMAIN TIPS ===" in prompt_obj.user_prompt)
        self.assertTrue("Keep food out of 40F to 140F" in prompt_obj.user_prompt)
        self.assertFalse("=== RESTAURANT LIVE STOCK INVENTORY ===" in prompt_obj.user_prompt)

    def test_build_hybrid_prompt_contains_both(self):
        ctx = UnifiedContext(
            intent="HYBRID",
            route="HYBRID",
            live_data={"inventory": [{"ingredientName": "Chicken", "quantity": 5.0, "unit": "kg"}]},
            knowledge=[{"source": "recipes", "title": "Butter Chicken", "content": "Standard cooking instructions"}],
            metadata={"spring_calls": ["GET /api/inventory"], "pinecone_used": True}
        )
        
        prompt_obj = self.prompt_builder.build_prompt("Suggest chicken recipe today", ctx)
        
        self.assertTrue("=== RESTAURANT LIVE STOCK INVENTORY ===" in prompt_obj.user_prompt)
        self.assertTrue("=== RAG KNOWLEDGE BASE DOMAIN TIPS ===" in prompt_obj.user_prompt)
        self.assertTrue("Chicken" in prompt_obj.user_prompt)
        self.assertTrue("Butter Chicken" in prompt_obj.user_prompt)

if __name__ == "__main__":
    unittest.main()
 sofa
