import re
import time
import logging
from typing import List, Dict, Any, Optional
from fastapi import HTTPException
from app.rag.retriever import KnowledgeRetriever
from app.prompts.inventory_prompt import build_inventory_prompt
from app.llm.llm_router import LLMRouter
from app.llm.output_parser import OutputParser

# Composition Orchestration Services
from app.services.recipe_service import RecipeService
from app.services.menu_service import MenuService
from app.services.pricing_service import PricingService

logger = logging.getLogger("app.api")

def clean_menu_item_name(name: str) -> str:
    """
    Strips raw recipe markers, cuisine labels, and trailing details
    to return a clean, professional restaurant-quality menu dish name.
    """
    if not name:
        return "Chef's Special"
        
    # Strip suffixes like "Recipe" or "Style"
    name = re.sub(r'\s+recipe\b', "", name, flags=re.IGNORECASE)
    name = re.sub(r'\s+style\b', "", name, flags=re.IGNORECASE)
    
    # Strip text after hyphens (e.g. "-Bengali Style Paneer")
    name = re.sub(r'\s*-\s*.*$', "", name)
    # Strip content in parentheses
    name = re.sub(r'\(.*\)', "", name)
    
    # Remove common blog titles
    name = re.sub(r'\b(?:authentic|classic|traditional|homemade|tasty|delicious)\b', "", name, flags=re.IGNORECASE)
    
    # Clean double spaces
    name = re.sub(r'\s+', " ", name).strip()
    return name.title() if name else "Chef's Special"

def detect_language(text: str) -> str:
    """
    Heuristic helper to detect language (english | telugu | tenglish).
    """
    text_lower = text.lower()
    has_telugu = any(0x0C00 <= ord(char) <= 0x0C7F for char in text)
    if has_telugu:
        return "telugu"
    tenglish_keywords = [
        "cheyyali", "migilindi", "ela", "enti", "avuthundi", "undhi", 
        "leka", "mari", "kuda", "ala", "ippudu", "vacham", "cheddam", 
        "ivvali", "ledu", "chesi", "tinna", "tinali", "chudu", "kavali", "kalla"
    ]
    if any(word in text_lower for word in tenglish_keywords):
        return "tenglish"
    return "english"

class InventoryOptimizerService:
    """
    Enterprise AI Flagship Ingredient Expiration & Intelligent Planner.
    Orchestrates recipe candidates, menu planning, and pricing suggestions
    to optimize ingredient utilization and calculate revenue improvements.
    """
    def __init__(self):
        self.retriever = KnowledgeRetriever()
        self.router = LLMRouter()
        
        # Compose internal services
        self.recipe_service = RecipeService()
        self.menu_service = MenuService()
        self.pricing_service = PricingService()

    def optimize_inventory(self, inventory: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generates a waste optimization plan by orchestrating multiple AI microservices.
        """
        start_time = time.time()
        logger.info(f"InventoryOptimizerService: Initiating optimization for {len(inventory)} items")

        # 1. Validation Checks
        if not inventory:
            raise HTTPException(status_code=400, detail="Inventory list cannot be empty.")

        for item in inventory:
            ing = item.get("ingredient")
            qty = item.get("quantity")
            unit = item.get("unit")
            exp = item.get("expiry_days")

            if not ing or not ing.strip():
                raise HTTPException(status_code=400, detail="Ingredient name cannot be empty.")
            if qty is None or float(qty) < 0:
                raise HTTPException(status_code=400, detail="Quantity cannot be negative.")
            if not unit or not unit.strip():
                raise HTTPException(status_code=400, detail="Unit cannot be empty.")
            if exp is None or int(exp) < 0:
                raise HTTPException(status_code=400, detail="Expiry days cannot be negative.")

        # 2. Programmatically merge duplicate ingredients (Sum quantities, take min expiry_days)
        merged_map = {}
        for item in inventory:
            name = item["ingredient"].strip().lower()
            qty = float(item["quantity"])
            unit = item["unit"].strip()
            exp = int(item["expiry_days"])

            if name in merged_map:
                merged_map[name]["quantity"] += qty
                merged_map[name]["expiry_days"] = min(merged_map[name]["expiry_days"], exp)
            else:
                merged_map[name] = {
                    "ingredient": item["ingredient"].strip(),
                    "quantity": qty,
                    "unit": unit,
                    "expiry_days": exp
                }
        
        optimized_inventory = list(merged_map.values())
        logger.info(f"InventoryOptimizerService: Merged duplicates. Reduced {len(inventory)} items to {len(optimized_inventory)}")

        # 3. Call Recipe Recommendation Service
        ingredient_names = [item["ingredient"] for item in optimized_inventory]
        try:
            recipes_res = self.recipe_service.generate_recipe(ingredient_names)
            recipes_list = recipes_res.get("recipes", [])
        except Exception as e:
            logger.error(f"InventoryOptimizerService: RecipeService failed: {str(e)}")
            recipes_list = []

        # 4. Call Menu Planner Service
        menu_items_input = []
        for item in optimized_inventory:
            menu_items_input.append({
                "ingredient": item["ingredient"],
                "quantity": f"{item['quantity']} {item['unit']}",
                "expiry_days": item["expiry_days"]
            })
            
        try:
            menu_res = self.menu_service.generate_menu(menu_items_input)
            specials_list = menu_res.get("special_menu", [])
        except Exception as e:
            logger.error(f"InventoryOptimizerService: MenuService failed: {str(e)}")
            specials_list = []

        # 5. Call Pricing Engine for suggested specials
        pricing_map = {}
        for special in specials_list:
            dish_name = special.get("dish", "")
            try:
                # Assume default ingredient cost based on historical recipes (₹150 baseline)
                pricing_res = self.pricing_service.generate_pricing_suggestion(dish_name, 150.0)
                pricing_map[dish_name] = pricing_res
            except Exception as e:
                logger.error(f"InventoryOptimizerService: PricingService failed for '{dish_name}': {str(e)}")
                pricing_map[dish_name] = {
                    "recommended_price": 450,
                    "estimated_profit": 300,
                    "category": "HIGH"
                }

        # 6. Retrieve general waste reduction context
        retriever_start = time.time()
        try:
            chunks = self.retriever.retrieve("food waste reduction ingredient shelf life inventory optimization", top_k=10)
        except Exception as e:
            logger.error(f"InventoryOptimizerService: Retriever failed: {str(e)}")
            chunks = []
        retriever_time_ms = int((time.time() - retriever_start) * 1000)

        # Filter general management guidelines or recipe context
        mgt_chunks = [c for c in chunks if "recipes" in c.get("source", "").lower() or "safety" in c.get("source", "").lower()]
        logger.info(f"InventoryOptimizerService: Retrieved {len(chunks)} chunks, filtered to {len(mgt_chunks)} context chunks in {retriever_time_ms}ms")

        # Format context block
        context_strs = []
        for i, chunk in enumerate(mgt_chunks):
            title = chunk.get("title", "unknown")
            content = chunk.get("content", "")
            context_strs.append(f"[Waste Control Info #{i+1}] (Title: {title})\n{content}\n")
        context_block = "\n".join(context_strs) if context_strs else "No BOH waste context available."

        # Compile candidates list description for prompt
        candidates_strs = []
        for spec in specials_list:
            dish = spec.get("dish")
            matched = ", ".join(spec.get("matched_inventory", []))
            candidates_strs.append(f"- Special: {dish} (Utilizes expiring: {matched})")
        for rec in recipes_list[:3]:
            dish = rec.get("recipe_name")
            matched = ", ".join(rec.get("matched_ingredients", []))
            candidates_strs.append(f"- Recipe: {dish} (Matches: {matched})")
        candidates_context = "\n".join(candidates_strs) if candidates_strs else "No specific candidate specials found."

        # 7. Construct Prompt
        try:
            prompt = build_inventory_prompt(optimized_inventory, candidates_context, context_block)
        except Exception as e:
            logger.error(f"InventoryOptimizerService: Prompt builder failed: {str(e)}")
            prompt = f"Optimize inventory: {optimized_inventory}\nCandidates: {candidates_context}"

        # 8. Call LLM Router
        router_result = None
        try:
            router_result = self.router.generate(prompt)
        except Exception as e:
            logger.error(f"InventoryOptimizerService: Router call failed: {str(e)}")

        # 9. Parse output JSON
        recommended_dishes = []
        purchase_required = False
        purchase_items = []
        reason_text = ""
        detected_lang = "english"
        
        if router_result and router_result.get("status") == "success":
            raw_text = router_result.get("response", "")
            try:
                parsed = OutputParser.parse_json(raw_text)
                recommended_dishes = parsed.get("recommended_dishes", [])
                purchase_required = bool(parsed.get("purchase_required", False))
                reason_text = parsed.get("reason", "").strip()
                detected_lang = parsed.get("language", "english")
                
                purchase_items_raw = parsed.get("purchase_items", [])
                for p in purchase_items_raw:
                    if isinstance(p, dict) and "ingredient" in p:
                        purchase_items.append({
                            "ingredient": p["ingredient"].strip().title(),
                            "required_quantity": str(p.get("required_quantity", "10 kg"))
                        })
            except Exception as e:
                logger.error(f"InventoryOptimizerService: JSON parsing failed: {str(e)}")

        # 10. Fallback Recovery if LLM output is empty/invalid
        if not recommended_dishes or not reason_text:
            logger.warning("InventoryOptimizerService: Parsing failed or empty list. Constructing fallback optimizer plan.")
            recommended_dishes = []
            # Plan 20 servings for first 3 specials
            for spec in specials_list[:3]:
                recommended_dishes.append({
                    "dish": spec.get("dish"),
                    "servings": 20,
                    "priority": spec.get("priority", "HIGH")
                })
            purchase_required = False
            
            lang_key = detected_lang.lower()
            if "telugu" in lang_key:
                reason_text = "ప్రస్తుత నిల్వలు సరిపోతాయి. వృథాను అరికట్టడానికి ఈ వంటకాలను సిఫార్సు చేస్తున్నాము."
            elif "tenglish" in lang_key:
                reason_text = "Current stock saripotundhi. Waste reduction kosam ee items cook cheyyandi."
            else:
                reason_text = "Current inventory stock is sufficient. Focus on utilizing short-shelf-life specials for waste reduction."

        # 11. Programmatic Math & Validation Calculations (Strictly Python-validated)
        planned_dishes = []
        estimated_revenue = 0
        total_waste_saved = 0.0

        # Build usage maps
        usage_map = {item["ingredient"].lower(): 0.0 for item in optimized_inventory}
        unit_map = {item["ingredient"].lower(): item["unit"] for item in optimized_inventory}
        stock_map = {item["ingredient"].lower(): item["quantity"] for item in optimized_inventory}
        expiry_map = {item["ingredient"].lower(): item["expiry_days"] for item in optimized_inventory}

        # Deduplicate and clean recommended dishes from LLM output
        seen_dishes = set()
        cleaned_recs = []
        for dish_item in recommended_dishes:
            d_raw = dish_item.get("dish", "").strip()
            d_name = clean_menu_item_name(d_raw)
            if not d_name or d_name.lower() in seen_dishes:
                continue
            seen_dishes.add(d_name.lower())
            
            # Programmatically override priority based on ingredient expiry!
            # If any matched ingredient expires in <= 2 days, force HIGH priority!
            min_exp_for_dish = 999
            d_lower = d_name.lower()
            for ing_key in usage_map.keys():
                if ing_key in d_lower or any(w in d_lower for w in ing_key.split()):
                    min_exp_for_dish = min(min_exp_for_dish, expiry_map[ing_key])
            
            if min_exp_for_dish <= 2:
                priority = "HIGH"
            elif min_exp_for_dish <= 5:
                priority = "MEDIUM"
            else:
                priority = "LOW"
                
            dish_item["dish"] = d_name
            dish_item["priority"] = priority
            cleaned_recs.append(dish_item)

        # Estimate revenue, servings, and usage programmatically
        for rec in cleaned_recs:
            d_name = rec.get("dish")
            servings = int(rec.get("servings", 15))
            priority = rec.get("priority", "HIGH")

            pricing = pricing_map.get(d_name, {
                "recommended_price": 400,
                "estimated_profit": 250,
                "category": "HIGH"
            })
            selling_price = pricing.get("recommended_price", 400)
            profit_per_serving = pricing.get("estimated_profit", 250)

            # Revenue contribution
            dish_revenue = servings * selling_price
            dish_profit = servings * profit_per_serving
            estimated_revenue += dish_revenue

            planned_dishes.append({
                "dish": d_name,
                "servings": servings,
                "profit": dish_profit,
                "priority": priority
            })

            # Consume matching expiring items (Assume 0.35 kg/unit per serving)
            d_lower = d_name.lower()
            for ing_key in usage_map.keys():
                # If ingredient matches dish name keywords
                if ing_key in d_lower or any(w in d_lower for w in ing_key.split()):
                    # Limit usage to available stock
                    available = stock_map[ing_key] - usage_map[ing_key]
                    needed = servings * 0.35
                    used = min(available, needed)
                    usage_map[ing_key] += used

        # Compiling usage & remaining lists
        usage_list = []
        remaining_list = []
        for ing_key, used_qty in usage_map.items():
            original_item = merged_map[ing_key]
            orig_name = original_item["ingredient"]
            unit = unit_map[ing_key]
            stock = stock_map[ing_key]
            expiry = expiry_map[ing_key]

            used_qty = round(used_qty, 2)
            remaining_qty = round(max(0.0, stock - used_qty), 2)
            
            usage_list.append({
                "ingredient": orig_name,
                "used_quantity": used_qty,
                "unit": unit
            })
            remaining_list.append({
                "ingredient": orig_name,
                "remaining_quantity": remaining_qty,
                "unit": unit
            })

            # Waste saved is calculated on items expiring within 2 days
            if expiry <= 2:
                total_waste_saved += used_qty

        # Auto-recommend purchase items if stock levels are critically low (<= 25% or < 2.0 remaining)
        already_listed = {p["ingredient"].lower() for p in purchase_items}
        for ing_key, used_qty in usage_map.items():
            original_item = merged_map[ing_key]
            orig_name = original_item["ingredient"]
            stock = stock_map[ing_key]
            unit = unit_map[ing_key]
            remaining = max(0.0, stock - used_qty)
            if (remaining < (stock * 0.25) or remaining < 2.0) and used_qty > 0:
                if orig_name.lower() not in already_listed:
                     replenish_qty = f"{round(stock * 2.0, 1)} {unit}"
                     purchase_items.append({
                         "ingredient": orig_name,
                         "required_quantity": replenish_qty
                     })
                     already_listed.add(orig_name.lower())

        if len(purchase_items) > 0:
            purchase_required = True

        # Stable Sorting of Dishes: Expiry Priority (HIGH -> MEDIUM -> LOW) -> Profit (descending) -> Alphabetical
        priority_weights = {"HIGH": 3, "MEDIUM": 2, "LOW": 1}
        planned_dishes.sort(
            key=lambda x: (
                -priority_weights.get(x["priority"], 0),
                -x["profit"],
                x["dish"].lower()
            )
        )

        # Bugfix: Detect language based on generated reason text instead of input ingredient list
        detected_lang = detect_language(reason_text)

        total_latency = int((time.time() - start_time) * 1000)
        logger.info(
            f"InventoryOptimizerService: Optimization complete. Latency: {total_latency}ms | "
            f"Revenue: ₹{estimated_revenue} | Waste Saved: {total_waste_saved}"
        )

        return {
            "recommended_dishes": planned_dishes,
            "inventory_usage": usage_list,
            "estimated_revenue": estimated_revenue,
            "waste_saved": round(total_waste_saved, 2),
            "remaining_inventory": remaining_list,
            "purchase_required": purchase_required,
            "purchase_items": purchase_items,
            "reason": reason_text,
            "language": detected_lang.capitalize()
        }

