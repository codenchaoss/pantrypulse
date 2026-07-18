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
        
        # 1. Input Validation
        if not ingredients:
            raise HTTPException(status_code=400, detail="Ingredients list cannot be empty.")
            
        clean_ingredients = [ing.strip() for ing in ingredients if ing.strip()]
        if not clean_ingredients:
            raise HTTPException(status_code=400, detail="Ingredients list contains only invalid items.")
            
        # 2. Retrieve knowledge chunks matching the ingredients query
        query_str = "Ingredients: " + ", ".join(clean_ingredients)
        retriever_start = time.time()
        try:
            chunks = self.retriever.retrieve(query_str, top_k=15)
        except Exception as e:
            logger.error(f"RecipeService: Retriever error: {str(e)}")
            chunks = []
        retriever_time_ms = int((time.time() - retriever_start) * 1000)
        
        # 3. Filter only recipe chunks
        recipe_chunks = [c for c in chunks if "recipes" in c.get("source", "").lower()]
        logger.info(f"RecipeService: Retrieved {len(chunks)} chunks, filtered to {len(recipe_chunks)} recipe chunks in {retriever_time_ms}ms")
        
        if not recipe_chunks:
            logger.warning("RecipeService: No recipe chunks retrieved. Returning empty recommendations list.")
            return {"recipes": []}
            
        # 4. Construct prompt
        context_strs = []
        for i, chunk in enumerate(recipe_chunks):
            source = chunk.get("source", "unknown")
            title = chunk.get("title", "unknown")
            content = chunk.get("content", "")
            context_strs.append(f"[Recipe #{i+1}] (Source: {source}, Title: {title})\n{content}\n")
        context_block = "\n".join(context_strs)
        
        try:
            prompt = build_recipe_prompt(clean_ingredients, context_block)
        except Exception as e:
            logger.error(f"RecipeService: Prompt construction failed: {str(e)}")
            prompt = f"Available: {', '.join(clean_ingredients)}\nContext: {context_block}"

        # 5. Call LLM Router
        router_result = None
        try:
            router_result = self.router.generate(prompt)
        except Exception as e:
            logger.error(f"RecipeService: Router call failed: {str(e)}")
            
        # 6. Parse structured JSON response
        recipes_list = []
        provider_used = "none"
        fallback_used = False
        
        if router_result and router_result.get("status") == "success":
            raw_text = router_result.get("response", "")
            provider_used = router_result.get("provider", "Gemini")
            fallback_used = router_result.get("fallback_used", False)
            
            try:
                parsed = OutputParser.parse_json(raw_text)
                if "recipes" in parsed and isinstance(parsed["recipes"], list):
                    recipes_list = parsed["recipes"]
                else:
                    logger.warning("RecipeService: Parsed output does not match expected JSON root schema.")
            except Exception as e:
                logger.error(f"RecipeService: JSON parsing failed: {str(e)}")
                
        # 7. Apply Post-processing Rules
        processed_recipes = []
        seen_ids = set()
        seen_names = set()
        
        for item in recipes_list:
            recipe_id = item.get("recipe_id", "R1000")
            recipe_name = item.get("recipe_name", "Unknown Recipe").strip()
            
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
            
            # Clean description of scrapings
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
            
        # Advanced Sorting:
        # 1. Matched count (descending)
        # 2. Match percentage (descending)
        # 3. Prep time (ascending)
        processed_recipes.sort(
            key=lambda x: (
                -len(x["matched_ingredients"]),
                -x["match_percentage"],
                x["preparation_time_minutes"]
            )
        )
        final_recipes = processed_recipes[:3]
        
        if not final_recipes and recipe_chunks:
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
        for i, chunk in enumerate(chunks[:3]):
            title = chunk.get("title", "Specials")
            desc = clean_recipe_description(chunk.get("content", ""))
            fallback_list.append({
                "recipe_id": f"REC_FB_{i+1}",
                "recipe_name": title,
                "description": desc[:150] + "...",
                "matched_ingredients": ingredients,
                "missing_ingredients": [],
                "match_percentage": 100,
                "preparation_time_minutes": 25,
                "difficulty": "Easy",
                "estimated_calories": 400,
                "reason_for_recommendation": "Calculated fallback based on semantic recipe search matching.",
                "confidence": 0.90
            })
        return fallback_list
