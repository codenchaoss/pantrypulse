import logging
from typing import List, Dict, Any

logger = logging.getLogger("app.api")

import time
import logging
from typing import List, Dict, Any
from fastapi import HTTPException
from app.rag.retriever import KnowledgeRetriever
from app.prompts.recipe_prompt import build_recipe_prompt
from app.llm.llm_router import LLMRouter
from app.llm.output_parser import OutputParser

import re

logger = logging.getLogger("app.api")

def clean_recipe_description(desc: str) -> str:
    """
    Standardizes description formatting and strips web-scraping residues.
    """
    if not desc:
        return "A mouth-watering restaurant recipe."
    
    # Remove markdown formatting
    desc = desc.replace("**", "").replace("__", "").replace("*", "").replace("`", "")
    
    # Remove common web scraping text markers/links
    scraped_patterns = [
        r'\b(?:www\.)?[a-zA-Z0-9-]+\.(?:com|org|net|edu|gov|co|info)\b',
        r'\b(?:click here|read more|adapted from|photo by|submitted by|recipe by|print recipe|newsletter|subscribe|yummly)\b'
    ]
    
    desc_clean = desc
    for pat in scraped_patterns:
        desc_clean = re.sub(pat, "", desc_clean, flags=re.IGNORECASE)
        
    # Clean up double spaces or stray punctuation
    desc_clean = re.sub(r'\s+', " ", desc_clean)
    desc_clean = desc_clean.replace(" .", ".").replace(" ,", ",").strip()
    return desc_clean if desc_clean else "A mouth-watering restaurant recipe."

class RecipeService:
    """
    Enterprise AI Recipe Recommendation Service.
    Retrieves candidate recipes, matches and ranks them based on ingredient compatibility,
    minimizes waste, and returns structured JSON recommendations.
    """
    def __init__(self):
        self.retriever = KnowledgeRetriever()
        self.router = LLMRouter()

    def generate_recipe(self, ingredients: List[str]) -> Dict[str, Any]:
        """
        Generates recipe recommendations based on input ingredients list.
        """
        start_time = time.time()
        logger.info(f"RecipeService: Initiating recommendation for ingredients: {ingredients}")
        
        if not ingredients:
            raise HTTPException(status_code=400, detail="Ingredients list cannot be empty.")
            
        clean_ingredients = [ing.strip() for ing in ingredients if ing.strip()]
        if not clean_ingredients:
            raise HTTPException(status_code=400, detail="Ingredients list contains only invalid items.")

        # Invoke the hybrid orchestration pipeline
        question = (
            f"Suggest recipes using available ingredients: {', '.join(clean_ingredients)}. "
            "You MUST respond with a valid JSON object matching the following structure:\n"
            "{\n"
            "  \"recipes\": [\n"
            "    {\n"
            "      \"recipe_id\": \"REC001\",\n"
            "      \"recipe_name\": \"Dish Name\",\n"
            "      \"description\": \"Description of the recipe suggestion.\",\n"
            "      \"matched_ingredients\": [\"ingredient1\"],\n"
            "      \"missing_ingredients\": [\"ingredient2\"],\n"
            "      \"match_percentage\": 80,\n"
            "      \"preparation_time_minutes\": 30,\n"
            "      \"difficulty\": \"Easy\",\n"
            "      \"estimated_calories\": 350,\n"
            "      \"reason_for_recommendation\": \"Why this is recommended.\",\n"
            "      \"confidence\": 0.85\n"
            "    }\n"
            "  ]\n"
            "}\n"
            "Return ONLY the raw JSON. Do not include markdown code block syntax (like ```json)."
        )
        # Retrieve grounding chunks from RAG vector database
        retriever_start = time.time()
        chunks = self.retriever.retrieve(question)
        retriever_time_ms = int((time.time() - retriever_start) * 1000)
        recipe_chunks = [c for c in chunks if "recipes" in c.get("source", "").lower()]
        logger.info(f"RecipeService: Retrieved {len(chunks)} chunks, filtered to {len(recipe_chunks)} recipe chunks in {retriever_time_ms}ms")
        from app.services.hybrid_chat_service import HybridChatService
        hybrid_service = HybridChatService()
        result = hybrid_service.get_response_sync(question)
        
        recipes_list = []
        provider_used = result.get("provider", "Gemini")
        fallback_used = result.get("fallback_used", False)
        raw_text = result.get("answer", "")
        
        try:
            parsed = OutputParser.parse_json(raw_text)
            if "recipes" in parsed and isinstance(parsed["recipes"], list):
                recipes_list = parsed["recipes"]
            else:
                logger.warning("RecipeService: Parsed output does not match expected JSON root schema.")
        except Exception as e:
            logger.error(f"RecipeService: JSON parsing failed: {str(e)}")
                
        processed_recipes = []
        seen_ids = set()
        seen_names = set()
        
        for item in recipes_list:
            recipe_id = item.get("recipe_id", "R1000")
            recipe_name = item.get("recipe_name", "Unknown Recipe").strip()
            
            if any(bad in recipe_name.lower() for bad in ["week", "seasonal", "supplier", "safety"]):
                continue
            if recipe_id in seen_ids or recipe_name.lower() in seen_names:
                continue
            seen_ids.add(recipe_id)
            seen_names.add(recipe_name.lower())
            
            matched = item.get("matched_ingredients", [])
            missing = item.get("missing_ingredients", [])
            
            total_ing = len(matched) + len(missing)
            calc_percentage = int((len(matched) / total_ing) * 100) if total_ing > 0 else 0
            match_percentage = min(100, max(0, item.get("match_percentage", calc_percentage)))
            confidence = round(float(match_percentage) / 100.0, 2)
            
            desc = clean_recipe_description(item.get("description", ""))
            
            rec_obj = {
                "recipe_id": recipe_id,
                "recipe_name": recipe_name,
                "description": desc,
                "matched_ingredients": matched,
                "missing_ingredients": missing,
                "match_percentage": match_percentage,
                "preparation_time_minutes": int(item.get("preparation_time_minutes", 30)),
                "difficulty": item.get("difficulty", "Medium"),
                "estimated_calories": int(item.get("estimated_calories", 350)),
                "reason_for_recommendation": item.get("reason_for_recommendation", "Uses available stock."),
                "confidence": confidence
            }
            processed_recipes.append(rec_obj)
            
        processed_recipes.sort(
            key=lambda x: (
                -len(x["matched_ingredients"]),
                -x["match_percentage"],
                x["preparation_time_minutes"]
            )
        )
        final_recipes = processed_recipes[:3]
        
        if not final_recipes:
            logger.warning("RecipeService: Processing yielded empty recommendations. Constructing heuristic fallback.")
            final_recipes = self._get_fallback_recommendations(clean_ingredients, recipe_chunks)
            
        total_latency = int((time.time() - start_time) * 1000)
        logger.info(
            f"RecipeService: Completed recommendation. "
            f"Total Latency: {total_latency}ms | Provider: {provider_used} | Fallback used: {fallback_used}"
        )
        
        return {
            "recipes": final_recipes
        }

    def _get_fallback_recommendations(self, ingredients: List[str], chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        fallback_list = []
        valid_chunks = [
            c for c in chunks 
            if not any(bad in c.get("title", "").lower() for bad in ["week", "seasonal", "supplier", "safety"])
        ]
        
        if valid_chunks:
            for i, chunk in enumerate(valid_chunks[:3]):
                title = chunk.get("title", "Specials")
                desc = clean_recipe_description(chunk.get("content", ""))
                fallback_list.append({
                    "recipe_id": f"REC_FB_{i+1}",
                    "recipe_name": title,
                    "description": desc[:150] + "...",
                    "matched_ingredients": ingredients[:3],
                    "missing_ingredients": [],
                    "match_percentage": 100,
                    "preparation_time_minutes": 25,
                    "difficulty": "Easy",
                    "estimated_calories": 400,
                    "reason_for_recommendation": "Calculated fallback based on semantic recipe search matching.",
                    "confidence": 0.90
                })
        else:
            ing_lowers = [ing.lower() for ing in ingredients]
            if any(w in ing_lowers for w in ["bread", "egg"]):
                fallback_dishes = ["Butter Egg Toast", "Black Pepper Omelette", "Egg & Pepper Scramble"]
            elif "rice" in ing_lowers and any(w in ing_lowers for w in ["carrot", "beans", "capsicum", "soy sauce"]):
                fallback_dishes = ["Vegetable Fried Rice", "Indo-Chinese Veg Stir-Fry Rice", "Mixed Veg Pulao"]
            elif any(w in ing_lowers for w in ["paneer"]):
                fallback_dishes = ["Paneer Butter Masala", "Kadai Paneer Special", "Paneer Tikka Masala"]
            elif any(w in ing_lowers for w in ["chicken"]):
                fallback_dishes = ["Butter Chicken Curry", "Chicken Tikka Masala", "Classic Chicken Biryani"]
            else:
                main_ing = ingredients[0].title() if ingredients else "Veg"
                sec_ing = ingredients[1].title() if len(ingredients) > 1 else "Spices"
                fallback_dishes = [
                    f"{main_ing} {sec_ing} Stir Fry",
                    f"Classic {main_ing} Special",
                    f"Chef's {main_ing} Delicacy"
                ]

            for i, d in enumerate(fallback_dishes):
                fallback_list.append({
                    "recipe_id": f"REC_GEN_{i+1}",
                    "recipe_name": d,
                    "description": f"A delicious restaurant dish freshly prepared using {', '.join(ingredients[:4])}.",
                    "matched_ingredients": ingredients[:4],
                    "missing_ingredients": [],
                    "match_percentage": 100,
                    "preparation_time_minutes": 20,
                    "difficulty": "Easy",
                    "estimated_calories": 380,
                    "reason_for_recommendation": f"Utilizes fresh available inventory ({', '.join(ingredients[:3])}).",
                    "confidence": 0.95
                })
        return fallback_list

    _local_recipes_cache = None

    def _get_local_matches(self, ingredients: List[str]) -> List[Dict[str, Any]]:
        import os, json
        if RecipeService._local_recipes_cache is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            path = os.path.join(base_dir, "knowledge", "recipes.json")
            if os.path.exists(path):
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        RecipeService._local_recipes_cache = json.load(f)
                except Exception as e:
                    logger.error(f"RecipeService: Failed to load local recipes dataset: {str(e)}")
                    RecipeService._local_recipes_cache = []
            else:
                RecipeService._local_recipes_cache = []

        if not RecipeService._local_recipes_cache:
            return []

        matched_results = []
        seen_names = set()
        for r in RecipeService._local_recipes_cache:
            r_ings = [i.lower() for i in r.get("ingredients", [])]
            r_name = r.get("recipe_name", "").strip()
            
            if not r_name or r_name.lower() in seen_names:
                continue
            if any(bad in r_name.lower() for bad in ["week", "seasonal", "supplier", "safety"]):
                continue

            matched = [ing for ing in ingredients if any(ing.lower() in ri for ri in r_ings)]
            if len(matched) >= 2:
                seen_names.add(r_name.lower())
                missing = [ri for ri in r.get("ingredients", []) if not any(ing.lower() in ri.lower() for ing in ingredients)]
                match_pct = int((len(matched) / (len(matched) + len(missing))) * 100) if (len(matched) + len(missing)) > 0 else 70
                matched_results.append({
                    "recipe_id": r.get("recipe_id", "R1000"),
                    "recipe_name": r_name,
                    "description": r.get("description", f"Freshly prepared dish utilizing {', '.join(matched)}."),
                    "matched_ingredients": matched,
                    "missing_ingredients": missing[:3],
                    "match_percentage": min(100, max(50, match_pct)),
                    "preparation_time_minutes": int(r.get("preparation_time_minutes", 25)),
                    "difficulty": r.get("difficulty", "Easy"),
                    "estimated_calories": int(r.get("estimated_calories", 350)),
                    "reason_for_recommendation": f"Directly matches available inventory ({', '.join(matched[:3])}).",
                    "confidence": round(min(1.0, 0.7 + len(matched) * 0.1), 2)
                })
                if len(matched_results) >= 3:
                    break
        return matched_results
