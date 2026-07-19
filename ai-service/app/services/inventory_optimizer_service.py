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
    Uses regex word boundaries, interjections, and suffix patterns to prevent false positives.
    """
    if not text:
        return "english"
        
    if any(0x0C00 <= ord(char) <= 0x0C7F for char in text):
        return "telugu"
        
    text_lower = text.lower()
    tenglish_words = {
        "ohh", "oh", "oho", "ohho", "hurray", "hurey", "hurrah", "alright", "alrighty", "knaww",
        "knoww", "kneww", "accha", "aachcha", "acha", "aah", "aha", "ahha", "abba", "abbha",
        "ammo", "ammow", "ayyo", "ayyyo", "arey", "areyy", "are", "rey", "reyy", "ra", "raa",
        "bey", "bhey", "boss", "bro", "dude", "sir", "ji", "mama", "macha", "machi", "machan",
        "garu", "gaaru", "andi", "aandi", "ayya", "bhayya", "bhai", "bhaya", "anna", "annayya",
        "cheyyali", "migilindi", "ela", "enti", "avuthundi", "undhi", "vundhi", "leka", "mari",
        "kuda", "ala", "ippudu", "vacham", "cheddam", "ivvali", "ledu", "chesi", "tinna", "tinali",
        "chudu", "kavali", "ekkada", "vunai", "ayipoindhi", "valla", "cheyyi", "supliers", "nunchi",
        "kavalo", "tiskoni", "pettali", "kaavali", "undha", "kooda", "kaani", "enduku", "eppudu",
        "elaga", "alaage", "kudaa", "enni", "yenni", "etla", "yetla", "yela", "yenti", "yem", "emi",
        "sarlu", "saarlu", "chesukuntadu", "chesukuntaru", "chesukovali", "chesukoni", "chesku"
    }
    
    words = set(re.findall(r'\b[a-z]+\b', text_lower))
    if words.intersection(tenglish_words):
        return "tenglish"
        
    tenglish_regex = r'\b[a-z]+(?:kuntadu|kuntaru|kuntam|kovali|kovalani|kovalane|thundi|thunnaru|thari|thamu)\b'
    if re.search(tenglish_regex, text_lower):
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
        logger.info("[TIMING-START] Starting inventory optimization processing...")

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

        # 2.5 Filter inventory to only send expiring ingredients to LLM services
        llm_inventory = [item for item in optimized_inventory if int(item["expiry_days"]) <= 7]
        if not llm_inventory:
            llm_inventory = sorted(optimized_inventory, key=lambda x: int(x["expiry_days"]))[:5]

        # 3. Generate candidate dishes programmatically (0ms execution time!)
        candidate_dishes = []
        ing_names = [item["ingredient"].strip() for item in llm_inventory]
        
        # Fast programmatic candidate dish generation
        if len(ing_names) >= 2:
            candidate_dishes.append(f"{ing_names[0]} {ing_names[1]} Curry")
        if len(ing_names) >= 3:
            candidate_dishes.append(f"{ing_names[0]} {ing_names[2]} Masala")
        for ing in ing_names[:3]:
            candidate_dishes.append(f"Special {ing} Fry")

        candidates_strs = [f"- Special: {dish} (Utilizes expiring: {', '.join(ing_names[:3])})" for dish in candidate_dishes]
        candidates_context = "\n".join(candidates_strs)

        # 4. Retrieve general waste reduction context (Limit top_k to 3 for smaller prompt context)
        retriever_start = time.time()
        try:
            chunks = self.retriever.retrieve("food waste reduction ingredient shelf life inventory optimization", top_k=3)
        except Exception as e:
            logger.error(f"InventoryOptimizerService: Retriever failed: {str(e)}")
            chunks = []
        retriever_time_ms = int((time.time() - retriever_start) * 1000)

        # Filter general management guidelines or recipe context
        mgt_chunks = [c for c in chunks if "recipes" in c.get("source", "").lower() or "safety" in c.get("source", "").lower()]
        logger.info(f"InventoryOptimizerService: Retrieved {len(chunks)} chunks, filtered to {len(mgt_chunks)} context chunks in {retriever_time_ms}ms")
        logger.info(f"[TIMING] Pinecone retrieval and filtering took: {time.time() - retriever_start:.3f}s")

        # Format context block
        context_strs = []
        for i, chunk in enumerate(mgt_chunks):
            title = chunk.get("title", "unknown")
            content = chunk.get("content", "")
            context_strs.append(f"[Waste Control Info #{i+1}] (Title: {title})\n{content}\n")
        context_block = "\n".join(context_strs) if context_strs else "No BOH waste context available."

        # 7. Construct Prompt
        try:
            prompt = build_inventory_prompt(llm_inventory, candidates_context, context_block)
        except Exception as e:
            logger.error(f"InventoryOptimizerService: Prompt builder failed: {str(e)}")
            prompt = f"Optimize inventory: {llm_inventory}\nCandidates: {candidates_context}"

        # 8. Call LLM Router with optimized temperature and max_tokens
        router_start = time.time()
        router_result = None
        try:
            router_result = self.router.generate(prompt, temperature=0.2, max_tokens=700)
        except Exception as e:
            logger.error(f"InventoryOptimizerService: Router call failed: {str(e)}")
        logger.info(f"[TIMING] LLM Router call for optimization plan took: {time.time() - router_start:.3f}s")
        logger.info(f"[TIMING-TOTAL] Entire optimize_inventory runtime: {time.time() - start_time:.3f}s")

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
            # Plan 20 servings for candidate dishes
            for dish_name in candidate_dishes[:3]:
                recommended_dishes.append({
                    "dish": dish_name,
                    "servings": 20,
                    "priority": "HIGH"
                })
            purchase_required = False
            
            lang_key = detected_lang.lower()
            if "telugu" in lang_key:
                reason_text = "ప్రస్తుత నిల్వలు సరిపోతాయి. వృథాను అరికట్టడానికి ఈ వంటకాలను సిఫార్సు చేస్తున్నాము."
            elif "tenglish" in lang_key:
                reason_text = "Current stock saripotundhi. Waste reduction kosam ee items cook cheyyandi."
            else:
                reason_text = "Current inventory stock is sufficient. Focus on utilizing short-shelf-life specials for waste reduction."

        planned_dishes = []
        estimated_revenue = 0
        total_waste_saved = 0.0

        usage_map = {item["ingredient"].lower(): 0.0 for item in optimized_inventory}
        unit_map = {item["ingredient"].lower(): item["unit"] for item in optimized_inventory}
        stock_map = {item["ingredient"].lower(): item["quantity"] for item in optimized_inventory}
        expiry_map = {item["ingredient"].lower(): item["expiry_days"] for item in optimized_inventory}

        seen_dishes = set()
        cleaned_recs = []
        for dish_item in recommended_dishes:
            d_raw = dish_item.get("dish", "").strip()
            d_name = clean_menu_item_name(d_raw)
            if not d_name or d_name.lower() in seen_dishes:
                continue
            seen_dishes.add(d_name.lower())
            
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

        pricing_map = {}
        for rec in cleaned_recs:
            d_name = rec.get("dish")
            pricing_map[d_name] = self.pricing_service.generate_pricing_suggestion_fast(d_name, 150.0)

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

            dish_revenue = servings * selling_price
            dish_profit = servings * profit_per_serving
            estimated_revenue += dish_revenue

            planned_dishes.append({
                "dish": d_name,
                "servings": servings,
                "profit": dish_profit,
                "priority": priority
            })

            d_lower = d_name.lower()
            for ing_key in usage_map.keys():
                if ing_key in d_lower or any(w in d_lower for w in ing_key.split()):
                    available = stock_map[ing_key] - usage_map[ing_key]
                    needed = servings * 0.35
                    used = min(available, needed)
                    usage_map[ing_key] += used

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

            if expiry <= 2:
                total_waste_saved += used_qty

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

