import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger("app.api")

import time
import logging
from typing import List, Dict, Any, Optional
from fastapi import HTTPException
from app.rag.retriever import KnowledgeRetriever
from app.prompts.menu_prompt import build_menu_prompt
from app.llm.llm_router import LLMRouter
from app.llm.output_parser import OutputParser

logger = logging.getLogger("app.api")

class MenuService:
    """
    Enterprise AI Daily Menu Generator Service.
    Suggests up to 5 daily specials optimized for profit margins and waste reduction,
    sorting by ingredient urgency and profit scores.
    """
    def __init__(self):
        self.retriever = KnowledgeRetriever()
        self.router = LLMRouter()

    def generate_menu(self, inventory: List[Dict[str, Any]], recipes: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Generates daily specials based on expiring inventory.
        """
        start_time = time.time()
        logger.info(f"MenuService: Received menu specials optimization request for inventory count: {len(inventory)}")
        
        # 1. Validation Checks
        if not inventory:
            raise HTTPException(status_code=400, detail="Inventory list cannot be empty.")
            
        # Validate expiry fields are non-negative
        for item in inventory:
            name = item.get("ingredient")
            if not name or not name.strip():
                raise HTTPException(status_code=400, detail="Inventory item must have a valid ingredient name.")
            try:
                expiry_days = int(item.get("expiry_days", -1))
            except (ValueError, TypeError):
                raise HTTPException(status_code=400, detail=f"Expiry days for {name} must be a valid integer.")
            if expiry_days < 0:
                raise HTTPException(status_code=400, detail=f"Expiry days for {name} cannot be negative.")

        # 2. Retrieve knowledge chunks matching expiring ingredients or chosen recipes
        if recipes:
            query_str = f"Recipes details for: {', '.join(recipes)}"
        else:
            ingredients_query = ", ".join([item.get("ingredient", "").strip() for item in inventory])
            query_str = f"Expiring ingredients recipes: {ingredients_query}"
        
        retriever_start = time.time()
        try:
            chunks = self.retriever.retrieve(query_str, top_k=15)
        except Exception as e:
            logger.error(f"MenuService: Retriever error: {str(e)}")
            chunks = []
        retriever_time_ms = int((time.time() - retriever_start) * 1000)

        # 3. Filter only recipe chunks (do not expose safety or suppliers)
        recipe_chunks = [c for c in chunks if "recipes" in c.get("source", "").lower()]
        logger.info(f"MenuService: Retrieved {len(chunks)} chunks, filtered to {len(recipe_chunks)} recipe chunks in {retriever_time_ms}ms")
        
        if not recipe_chunks and not recipes:
            logger.warning("MenuService: No recipe chunks retrieved. Returning empty specials.")
            return {"special_menu": []}

        # 4. Construct prompt
        context_strs = []
        for i, chunk in enumerate(recipe_chunks):
            source = chunk.get("source", "unknown")
            title = chunk.get("title", "unknown")
            content = chunk.get("content", "")
            context_strs.append(f"[Recipe Reference #{i+1}] (Source: {source}, Title: {title})\n{content}\n")
        context_block = "\n".join(context_strs)
        
        try:
            prompt = build_menu_prompt(inventory, context_block)
            if recipes:
                prompt += f"\n=== CHOSEN TARGET RECIPES ===\nYou MUST generate daily specials based on these recipes: {', '.join(recipes)}\n"
        except Exception as e:
            logger.error(f"MenuService: Prompt building failed: {str(e)}")
            prompt = f"Inventory: {inventory}\nContext: {context_block}"

        # 5. Call LLM Router
        router_result = None
        try:
            router_result = self.router.generate(prompt)
        except Exception as e:
            logger.error(f"MenuService: Router failed: {str(e)}")

        # 6. Parse structured JSON response
        menu_items = []
        provider_used = "none"
        fallback_used = False
        
        if router_result and router_result.get("status") == "success":
            raw_text = router_result.get("response", "")
            provider_used = router_result.get("provider", "Gemini")
            fallback_used = router_result.get("fallback_used", False)
            
            try:
                parsed = OutputParser.parse_json(raw_text)
                if "special_menu" in parsed and isinstance(parsed["special_menu"], list):
                    menu_items = parsed["special_menu"]
                elif "menu" in parsed and isinstance(parsed["menu"], list):
                    menu_items = parsed["menu"]  # fallback compatibility
                else:
                    logger.warning("MenuService: Parsed JSON does not match expected Daily Menu root key.")
            except Exception as e:
                logger.error(f"MenuService: JSON parsing failed: {str(e)}")

        # 7. Apply Post-processing Rules (Deduplicate, Verify Priority/Expiry thresholds, Sort)
        processed_specials = []
        seen_dishes = set()
        
        # Priority mapping values for sorting
        priority_weights = {"HIGH": 3, "MEDIUM": 2, "LOW": 1}
        
        for item in menu_items:
            dish_name = item.get("dish", item.get("recipe_name", "Unknown Special")).strip()
            if not dish_name or dish_name.lower() in seen_dishes:
                continue
            seen_dishes.add(dish_name.lower())
            
            # Programmatically verify and filter matched inventory ingredients
            input_inventory_names = {inv_item.get("ingredient", "").lower().strip() for inv_item in inventory}
            matched_raw = item.get("matched_inventory", [])
            matched = [m.strip() for m in matched_raw if m.lower().strip() in input_inventory_names]
            
            # Fallback if no matching ingredients are found (assign most urgent)
            if not matched and inventory:
                urgent_inv = sorted(inventory, key=lambda x: int(x.get("expiry_days", 999)))
                matched = [urgent_inv[0].get("ingredient")]
                
            matched_lower = [m.lower().strip() for m in matched]
            
            # Programmatically verify minimum expiry days of matched items
            min_expiry = 999
            for inv_item in inventory:
                inv_name = inv_item.get("ingredient", "").lower().strip()
                if inv_name in matched_lower:
                    min_expiry = min(min_expiry, int(inv_item.get("expiry_days", 999)))
            
            # Enforce priority assignment rules programmatically
            if min_expiry <= 2:
                priority = "HIGH"
            elif min_expiry <= 5:
                priority = "MEDIUM"
            else:
                priority = "LOW"
                
            # Programmatically compute missing ingredients
            required = item.get("required_ingredients", [])
            missing_ingredients = [r.strip() for r in required if r.lower().strip() not in input_inventory_names]
            
            # Normalize confidence score to 0.0 - 1.0 range
            confidence_raw = float(item.get("confidence", 80))
            if confidence_raw > 1.0:
                confidence = round(confidence_raw / 100.0, 2)
            else:
                confidence = round(confidence_raw, 2)
                
            # Profit formatting with currency unit symbol prefix
            profit_val = int(item.get("estimated_profit", 350))
            estimated_profit = f"₹{profit_val}"
            
            spec_obj = {
                "dish": dish_name,
                "reason": item.get("reason", "Optimized menu item for waste minimization."),
                "matched_inventory": matched,
                "missing_ingredients": missing_ingredients,
                "estimated_profit": estimated_profit,
                "estimated_profit_value": profit_val,  # kept for sorting
                "priority": priority,
                "preparation_time": int(item.get("preparation_time", 30)),
                "difficulty": item.get("difficulty", "Medium"),
                "confidence": confidence
            }
            processed_specials.append(spec_obj)

        # Advanced sorting logic: 
        # 1. Priority weight (descending)
        # 2. Number of missing ingredients (ascending)
        # 3. Profit margin (descending)
        # 4. Preparation time (ascending)
        # 5. Dish name (alphabetically)
        processed_specials.sort(
            key=lambda x: (
                -priority_weights.get(x["priority"], 1),
                len(x["missing_ingredients"]),
                -x["estimated_profit_value"],
                x["preparation_time"],
                x["dish"].lower()
            )
        )
        
        # Cap daily specials to maximum 5 items
        final_specials = processed_specials[:5]
        
        # Strip internal temporary sorting fields from final response objects
        for s in final_specials:
            s.pop("estimated_profit_value", None)
            
        # Fallback to retrieved recipe chunks if parse/generation failed completely
        if not final_specials and recipe_chunks:
            logger.warning("MenuService: Specials processing yielded empty list. Implementing heuristic fallback.")
            final_specials = self._get_fallback_menu(inventory, recipe_chunks)
            
        total_latency = int((time.time() - start_time) * 1000)
        logger.info(
            f"MenuService: Completed menu generation. "
            f"Total Latency: {total_latency}ms | Provider: {provider_used} | Fallback used: {fallback_used}"
        )
        
        return {
            "special_menu": final_specials
        }

    def _get_fallback_menu(self, inventory: List[Dict[str, Any]], chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Fallback generator that structures menu items directly from database chunks.
        """
        fallback_list = []
        priority_weights = {"HIGH": 3, "MEDIUM": 2, "LOW": 1}
        input_inventory_names = {inv_item.get("ingredient", "").lower().strip() for inv_item in inventory}
        
        # Take the top recipes and extract ingredient matches
        for i, chunk in enumerate(chunks[:5]):
            title = chunk.get("title", "Chef's Special Special")
            content = chunk.get("content", "").lower()
            
            # Simple match checks
            matched = []
            min_expiry = 999
            for item in inventory:
                ing_name = item.get("ingredient", "").strip()
                if ing_name.lower() in content:
                    matched.append(ing_name)
                    min_expiry = min(min_expiry, int(item.get("expiry_days", 999)))
                    
            if not matched:
                matched = [inventory[0]["ingredient"]]
                min_expiry = int(inventory[0]["expiry_days"])
                
            if min_expiry <= 2:
                priority = "HIGH"
            elif min_expiry <= 5:
                priority = "MEDIUM"
            else:
                priority = "LOW"
                
            profit_val = 350 + (i * 20)
            fallback_list.append({
                "dish": title,
                "reason": f"Fallback recipe suggestion using expiring {', '.join(matched)}.",
                "matched_inventory": matched,
                "missing_ingredients": [],
                "estimated_profit": f"₹{profit_val}",
                "estimated_profit_value": profit_val,
                "priority": priority,
                "preparation_time": 25,
                "difficulty": "Easy",
                "confidence": 0.85
            })
            
        # Re-sort fallbacks stably
        fallback_list.sort(
            key=lambda x: (
                -priority_weights.get(x["priority"], 1),
                len(x["missing_ingredients"]),
                -x["estimated_profit_value"],
                x["preparation_time"],
                x["dish"].lower()
            )
        )
        
        for s in fallback_list:
            s.pop("estimated_profit_value", None)
            
        return fallback_list[:5]
