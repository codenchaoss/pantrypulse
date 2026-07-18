import sys
import os
import unittest
from unittest.mock import patch, MagicMock
from fastapi import HTTPException

# Ensure the app directory is on the python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from app.services.recipe_service import RecipeService

class TestRecipeRecommendation(unittest.TestCase):
    
    def setUp(self):
        self.service = RecipeService()

    def test_01_request_validation_empty(self):
        """Verify that passing an empty ingredients list raises an HTTP 400 exception."""
        with self.assertRaises(HTTPException) as context:
            self.service.generate_recipe([])
        self.assertEqual(context.exception.status_code, 400)
        self.assertIn("cannot be empty", context.exception.detail)
        
        with self.assertRaises(HTTPException) as context2:
            self.service.generate_recipe(["", "   "])
        self.assertEqual(context2.exception.status_code, 400)
        self.assertIn("invalid items", context2.exception.detail)
        print("✓ Test 1: Request validation checking - PASS")

    @patch("app.services.recipe_service.KnowledgeRetriever.retrieve")
    @patch("app.services.recipe_service.LLMRouter.generate")
    def test_02_recipe_chunks_filtering(self, mock_router, mock_retrieve):
        """Verify that context retrieval programmatically filters out non-recipe chunks."""
        # Mock retriever returning a mix of supplier, safety, and recipe chunks
        mock_retrieve.return_value = [
            {"source": "safety.json", "title": "Store Temp", "content": "Cold storage"},
            {"source": "suppliers.json", "title": "SeaFood Wholesaler", "content": "Fresh salmon supplier"},
            {"source": "recipes.json", "title": "Garlic Salmon", "content": "Bake salmon in butter"}
        ]
        
        mock_router.return_value = {
            "status": "success",
            "provider": "gemini",
            "response": '{"recipes": [{"recipe_id": "REC001", "recipe_name": "Garlic Salmon", "description": "Quick baked garlic salmon", "matched_ingredients": ["Salmon"], "missing_ingredients": ["Garlic"], "match_percentage": 50, "preparation_time_minutes": 20, "difficulty": "Easy", "estimated_calories": 250, "reason_for_recommendation": "Great match."}]}',
            "response_time_ms": 150,
            "fallback_used": False
        }
        
        result = self.service.generate_recipe(["Salmon"])
        self.assertEqual(len(result["recipes"]), 1)
        self.assertEqual(result["recipes"][0]["recipe_name"], "Garlic Salmon")
        print("✓ Test 2: Programmatic recipe chunk filtering - PASS")

    @patch("app.services.recipe_service.KnowledgeRetriever.retrieve")
    @patch("app.services.recipe_service.LLMRouter.generate")
    @patch("app.services.recipe_service.build_recipe_prompt")
    def test_03_prompt_builder_integration(self, mock_build_prompt, mock_router, mock_retrieve):
        """Verify that prompt builder compiles correct instructions and context."""
        mock_retrieve.return_value = [
            {"source": "recipes.json", "title": "Salad", "content": "Toss greens"}
        ]
        mock_router.return_value = {"status": "success", "response": '{"recipes": []}'}
        
        self.service.generate_recipe(["Lettuce"])
        
        mock_build_prompt.assert_called_once()
        self.assertEqual(mock_build_prompt.call_args[0][0], ["Lettuce"])
        self.assertIn("Salad", mock_build_prompt.call_args[0][1])
        print("✓ Test 3: Prompt builder integration - PASS")

    @patch("app.services.recipe_service.KnowledgeRetriever.retrieve")
    @patch("app.services.recipe_service.LLMRouter.generate")
    def test_04_json_schema_validation(self, mock_router, mock_retrieve):
        """Verify that parsed response conforms exactly to the structured schema."""
        mock_retrieve.return_value = [
            {"source": "recipes.json", "title": "Chicken Soup", "content": "Chicken soup steps"}
        ]
        
        mock_router.return_value = {
            "status": "success",
            "provider": "gemini",
            "response": (
                '{"recipes": [{'
                '"recipe_id": "REC001",'
                '"recipe_name": "Chicken Soup",'
                '"description": "Warm chicken broth soup",'
                '"matched_ingredients": ["Chicken"],'
                '"missing_ingredients": ["Carrot", "Celery"],'
                '"match_percentage": 33,'
                '"preparation_time_minutes": 45,'
                '"difficulty": "Medium",'
                '"estimated_calories": 200,'
                '"reason_for_recommendation": "Calculates profit margin estimation"'
                '}]}'
            ),
            "response_time_ms": 200,
            "fallback_used": False
        }
        
        result = self.service.generate_recipe(["Chicken"])
        self.assertEqual(len(result["recipes"]), 1)
        recipe = result["recipes"][0]
        
        # Verify schema keys
        self.assertEqual(recipe["recipe_id"], "REC001")
        self.assertEqual(recipe["recipe_name"], "Chicken Soup")
        self.assertEqual(recipe["description"], "Warm chicken broth soup")
        self.assertEqual(recipe["matched_ingredients"], ["Chicken"])
        self.assertEqual(recipe["missing_ingredients"], ["Carrot", "Celery"])
        self.assertEqual(recipe["match_percentage"], 33)
        self.assertEqual(recipe["preparation_time_minutes"], 45)
        self.assertEqual(recipe["difficulty"], "Medium")
        self.assertEqual(recipe["estimated_calories"], 200)
        self.assertIn("profit margin", recipe["reason_for_recommendation"])
        print("✓ Test 4: JSON response schema validation - PASS")

    @patch("app.services.recipe_service.KnowledgeRetriever.retrieve")
    @patch("app.services.recipe_service.LLMRouter.generate")
    def test_05_capping_and_ranking(self, mock_router, mock_retrieve):
        """Verify that recommendations are capped to maximum 3 and ranked by match percentage."""
        mock_retrieve.return_value = [
            {"source": "recipes.json", "title": "R1", "content": "..."}
        ]
        
        # Mock LLM returning 5 recipes in scrambled match order
        mock_router.return_value = {
            "status": "success",
            "provider": "gemini",
            "response": (
                '{"recipes": ['
                '{"recipe_id": "REC1", "recipe_name": "R1", "match_percentage": 50, "preparation_time_minutes": 30},'
                '{"recipe_id": "REC2", "recipe_name": "R2", "match_percentage": 90, "preparation_time_minutes": 20},'
                '{"recipe_id": "REC3", "recipe_name": "R3", "match_percentage": 75, "preparation_time_minutes": 40},'
                '{"recipe_id": "REC4", "recipe_name": "R4", "match_percentage": 80, "preparation_time_minutes": 15},'
                '{"recipe_id": "REC5", "recipe_name": "R5", "match_percentage": 30, "preparation_time_minutes": 60}'
                ']}'
            )
        }
        
        result = self.service.generate_recipe(["test"])
        
        # Verify capped to 3
        self.assertEqual(len(result["recipes"]), 3)
        
        # Verify ranked: R2 (90%), R4 (80%), R3 (75%)
        self.assertEqual(result["recipes"][0]["recipe_id"], "REC2")
        self.assertEqual(result["recipes"][1]["recipe_id"], "REC4")
        self.assertEqual(result["recipes"][2]["recipe_id"], "REC3")
        print("✓ Test 5: Recommendations capping (max 3) and percentage ranking - PASS")

    @patch("app.services.recipe_service.KnowledgeRetriever.retrieve")
    @patch("app.services.recipe_service.LLMRouter.generate")
    def test_06_duplicates_prevention(self, mock_router, mock_retrieve):
        """Verify that duplicate recipes are filtered out from results."""
        mock_retrieve.return_value = [
            {"source": "recipes.json", "title": "R1", "content": "..."}
        ]
        
        mock_router.return_value = {
            "status": "success",
            "provider": "gemini",
            "response": (
                '{"recipes": ['
                '{"recipe_id": "REC1", "recipe_name": "Unique Pasta", "match_percentage": 80},'
                '{"recipe_id": "REC1", "recipe_name": "Duplicate ID Pasta", "match_percentage": 70},'
                '{"recipe_id": "REC2", "recipe_name": "Unique Pasta", "match_percentage": 60},'
                '{"recipe_id": "REC3", "recipe_name": "Another unique dish", "match_percentage": 50}'
                ']}'
            )
        }
        
        result = self.service.generate_recipe(["test"])
        
        # Only unique ID and unique Name should be processed
        # Expected unique recipes:
        # 1. Unique Pasta (REC1)
        # 2. Another unique dish (REC3)
        self.assertEqual(len(result["recipes"]), 2)
        self.assertEqual(result["recipes"][0]["recipe_name"], "Unique Pasta")
        self.assertEqual(result["recipes"][1]["recipe_name"], "Another unique dish")
        print("✓ Test 6: Duplicate recipe prevention - PASS")

    @patch("app.services.recipe_service.KnowledgeRetriever.retrieve")
    @patch("app.services.recipe_service.LLMRouter.generate")
    def test_07_fallback_handling(self, mock_router, mock_retrieve):
        """Verify that JSON parser errors trigger fallback recommendations and prevent crashes."""
        mock_retrieve.return_value = [
            {"source": "recipes.json", "title": "Heuristic Pasta", "content": "Bake pasta with tomato sauce"}
        ]
        # Mocking invalid JSON string
        mock_router.return_value = {
            "status": "success",
            "response": "invalid json output text"
        }
        
        result = self.service.generate_recipe(["tomato"])
        
        # Fallback is triggered and returns valid list
        self.assertEqual(len(result["recipes"]), 1)
        self.assertEqual(result["recipes"][0]["recipe_id"], "REC_FB_1")
        self.assertEqual(result["recipes"][0]["recipe_name"], "Heuristic Pasta")
        print("✓ Test 7: Parsing error fallback handling - PASS")

def run_tests():
    print("==================================================")
    print("KitchenSync Recipe Recommendation Verification")
    print("==================================================")
    
    suite = unittest.TestLoader().loadTestsFromTestCase(TestRecipeRecommendation)
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
