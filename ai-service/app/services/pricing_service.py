import time
import logging
from typing import Dict, Any
from fastapi import HTTPException
from app.rag.retriever import KnowledgeRetriever
from app.prompts.pricing_prompt import build_pricing_prompt
from app.llm.llm_router import LLMRouter
from app.llm.output_parser import OutputParser

logger = logging.getLogger("app.api")

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
        "ivvali", "ledu", "chesi", "tinna", "tinali", "chudu", "kavali"
    ]
    if any(word in text_lower for word in tenglish_keywords):
        return "tenglish"
    return "english"

class PricingService:
    """
    Enterprise AI Profit Suggestion and Pricing Engine.
    Estimates optimal selling prices, programmatically computes margins,
    and classifies dishes into margin tiers.
    """
    def __init__(self):
        self.retriever = KnowledgeRetriever()
        self.router = LLMRouter()

    def generate_pricing_suggestion(self, dish: str, ingredient_cost: float) -> Dict[str, Any]:
        """
        Generates selling price suggestion and computes profit margins.
        """
        start_time = time.time()
        logger.info(f"PricingService: Suggestions requested for dish: '{dish}' | Cost: {ingredient_cost}")

        # 1. Input Validation
        if not dish or not dish.strip():
            raise HTTPException(status_code=400, detail="Dish name cannot be empty.")
        if ingredient_cost < 0:
            raise HTTPException(status_code=400, detail="Ingredient cost cannot be negative.")

        clean_dish = dish.strip()

        # 2. Retrieve recipe pricing context
        search_query = f"{clean_dish} menu cost pricing recipe"
        retriever_start = time.time()
        try:
            chunks = self.retriever.retrieve(search_query, top_k=10)
        except Exception as e:
            logger.error(f"PricingService: Retriever failed: {str(e)}")
            chunks = []
        retriever_time_ms = int((time.time() - retriever_start) * 1000)

        # Filter only recipe chunks
        recipe_chunks = [c for c in chunks if "recipes" in c.get("source", "").lower()]
        logger.info(f"PricingService: Retrieved {len(chunks)} chunks, filtered to {len(recipe_chunks)} recipe chunks in {retriever_time_ms}ms")

        # 3. Format context block
        context_strs = []
        for i, chunk in enumerate(recipe_chunks):
            title = chunk.get("title", "unknown")
            content = chunk.get("content", "")
            context_strs.append(f"[Recipe Cost Info #{i+1}] (Title: {title})\n{content}\n")
        context_block = "\n".join(context_strs) if context_strs else "No pricing context available."

        # 4. Construct prompt
        try:
            prompt = build_pricing_prompt(clean_dish, ingredient_cost, context_block)
        except Exception as e:
            logger.error(f"PricingService: Prompt creation failed: {str(e)}")
            prompt = f"Dish: {clean_dish}\nCost: {ingredient_cost}\nContext: {context_block}"

        # 5. Call LLM Router
        router_result = None
        try:
            router_result = self.router.generate(prompt)
        except Exception as e:
            logger.error(f"PricingService: Router call failed: {str(e)}")

        # 6. Parse structured response
        recommended_price = 0
        reason_text = ""
        detected_lang = detect_language(clean_dish)
        provider_used = "none"
        fallback_used = False
        pricing_strategy = "Standard"
        market_position = "Mid-range"
        price_confidence = 90
        
        if router_result and router_result.get("status") == "success":
            raw_text = router_result.get("response", "")
            provider_used = router_result.get("provider", "Gemini")
            fallback_used = router_result.get("fallback_used", False)
            
            try:
                parsed = OutputParser.parse_json(raw_text)
                recommended_price = int(parsed.get("recommended_price", 0))
                pricing_strategy = parsed.get("pricing_strategy", "Standard").strip()
                market_position = parsed.get("market_position", "Mid-range").strip()
                try:
                    price_confidence = int(parsed.get("price_confidence", 90))
                except (ValueError, TypeError):
                    price_confidence = 90
                detected_lang = parsed.get("language", detected_lang)
            except Exception as e:
                logger.error(f"PricingService: JSON parsing failed: {str(e)}")

        # 7. Programmatic Calculations & Fallback Logic
        if recommended_price <= 0:
            logger.warning("PricingService: Price suggestion missing or invalid. Constructing BOH markup fallback.")
            # Calculate standard markup
            recommended_price = int(ingredient_cost * 3.0)
            if recommended_price == 0:
                recommended_price = 150 # default baseline minimum

        # Compute profit parameters programmatically in Python
        estimated_profit = recommended_price - int(ingredient_cost)
        profit_margin = int((estimated_profit / recommended_price) * 100) if recommended_price > 0 else 0

        # Programmatically infer or validate strategy & position
        if not pricing_strategy or pricing_strategy == "Standard":
            if profit_margin >= 70:
                pricing_strategy = "Premium"
                market_position = "Upscale"
            elif profit_margin >= 50:
                pricing_strategy = "Standard"
                market_position = "Mid-range"
            else:
                pricing_strategy = "Value"
                market_position = "Budget"

        total_latency = int((time.time() - start_time) * 1000)
        logger.info(
            f"PricingService: Suggestion generated. Price: {recommended_price} | Margin: {profit_margin}% | "
            f"Strategy: {pricing_strategy} | Latency: {total_latency}ms"
        )

        return {
            "dish": clean_dish,
            "ingredient_cost": float(ingredient_cost),
            "recommended_price": recommended_price,
            "estimated_profit": estimated_profit,
            "profit_margin": profit_margin,
            "pricing_strategy": pricing_strategy,
            "market_position": market_position,
            "price_confidence": price_confidence
        }

