import unittest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock

from app.routing.intent_router import IntentRouter
from app.services.context_builder import ContextBuilder
from app.models.intent_models import Intent, Route, IntentResult
from app.models.context_models import UnifiedContext

class TestContextBuilder(unittest.TestCase):
    """
    Unit tests for Phase 3 ContextBuilder module.
    """

    def setUp(self):
        self.router = IntentRouter()
        self.builder = ContextBuilder()

    @patch("app.services.spring_api.spring_client.get_inventory", new_callable=AsyncMock)
    def test_build_inventory_context_success(self, mock_get_inventory):
        mock_get_inventory.return_value = [{"ingredientName": "Onion", "quantity": 10.0}]
        
        route_res = IntentResult(
            intent=Intent.INVENTORY,
            route=Route.SPRING_INVENTORY,
            confidence=0.98,
            matched_keywords=["stock"],
            reason="Inventory test"
        )
        
        async def run_test():
            ctx = await self.builder.build_context("Show stock levels", route_res)
            self.assertEqual(ctx.route, Route.SPRING_INVENTORY.value)
            self.assertTrue("inventory" in ctx.live_data)
            self.assertEqual(ctx.live_data["inventory"][0]["ingredientName"], "Onion")
            self.assertEqual(ctx.metadata["spring_calls"], ["GET /api/inventory"])
            self.assertFalse(ctx.metadata["pinecone_used"])

        asyncio.run(run_test())

    @patch("app.services.spring_api.spring_client.get_recipes", new_callable=AsyncMock)
    def test_build_recipes_context_paginated_success(self, mock_get_recipes):
        # Mock Spring Boot Page<Recipe> paginated response
        mock_get_recipes.return_value = {
            "content": [{"recipeName": "Paneer Tikka", "costPrice": 5.0}],
            "totalPages": 1
        }
        
        route_res = IntentResult(
            intent=Intent.RECIPE,
            route=Route.SPRING_RECIPES,
            confidence=0.98,
            matched_keywords=["recipes"],
            reason="Recipe test"
        )
        
        async def run_test():
            ctx = await self.builder.build_context("Show paneer recipes", route_res)
            self.assertEqual(ctx.route, Route.SPRING_RECIPES.value)
            self.assertTrue("recipes" in ctx.live_data)
            # Verify the paginated content is extracted correctly
            self.assertEqual(ctx.live_data["recipes"][0]["recipeName"], "Paneer Tikka")
            self.assertEqual(ctx.metadata["spring_calls"], ["GET /api/recipes"])

        asyncio.run(run_test())

    @patch("app.services.spring_api.spring_client.get_inventory", new_callable=AsyncMock)
    @patch("app.rag.retriever.KnowledgeRetriever.retrieve")
    def test_build_hybrid_context_success(self, mock_retrieve, mock_get_inventory):
        mock_get_inventory.return_value = [{"ingredientName": "Chicken", "quantity": 5.0}]
        mock_retrieve.return_value = [{"id": "chunk_1", "metadata": {"text": "Clean chicken stored at 4C"}}]
        
        route_res = IntentResult(
            intent=Intent.HYBRID,
            route=Route.HYBRID,
            confidence=0.98,
            matched_keywords=["available"],
            reason="Hybrid test"
        )
        
        async def run_test():
            ctx = await self.builder.build_context("Suggest recipes with available chicken", route_res)
            self.assertEqual(ctx.route, Route.HYBRID.value)
            self.assertEqual(ctx.live_data["inventory"][0]["ingredientName"], "Chicken")
            self.assertEqual(ctx.knowledge[0]["id"], "chunk_1")
            self.assertTrue(ctx.metadata["pinecone_used"])
            self.assertEqual(ctx.metadata["spring_calls"], ["GET /api/inventory"])

        asyncio.run(run_test())

if __name__ == "__main__":
    unittest.main()
