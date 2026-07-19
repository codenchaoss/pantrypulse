import time
import logging
from typing import Dict, Any
from fastapi import HTTPException
from app.rag.retriever import KnowledgeRetriever
from app.prompts.pricing_prompt import build_pricing_prompt
from app.llm.llm_router import LLMRouter
from app.llm.output_parser import OutputParser

logger = logging.getLogger("app.api")

import re

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

        if not dish or not dish.strip():
            raise HTTPException(status_code=400, detail="Dish name cannot be empty.")
        if ingredient_cost < 0:
            raise HTTPException(status_code=400, detail="Ingredient cost cannot be negative.")

        clean_dish = dish.strip()
        return self.generate_pricing_suggestion_fast(clean_dish, ingredient_cost)
        retriever_start = time.time()
        try:
            chunks = self.retriever.retrieve(search_query, top_k=3)
        except Exception as e:
            logger.error(f"PricingService: Retriever failed: {str(e)}")
            chunks = []
        retriever_time_ms = int((time.time() - retriever_start) * 1000)

        recipe_chunks = [c for c in chunks if "recipes" in c.get("source", "").lower()]
        logger.info(f"PricingService: Retrieved {len(chunks)} chunks, filtered to {len(recipe_chunks)} recipe chunks in {retriever_time_ms}ms")

        context_strs = []
        for i, chunk in enumerate(recipe_chunks):
            title = chunk.get("title", "unknown")
            content = chunk.get("content", "")
            context_strs.append(f"[Recipe Cost Info #{i+1}] (Title: {title})\n{content}\n")
        context_block = "\n".join(context_strs) if context_strs else "No pricing context available."

        try:
            prompt = build_pricing_prompt(clean_dish, ingredient_cost, context_block)
        except Exception as e:
            logger.error(f"PricingService: Prompt creation failed: {str(e)}")
            prompt = f"Dish: {clean_dish}\nCost: {ingredient_cost}\nContext: {context_block}"

        router_result = None
        try:
            router_result = self.router.generate(prompt, temperature=0.2, max_tokens=300)
        except Exception as e:
            logger.error(f"PricingService: Router call failed: {str(e)}")

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

        if recommended_price <= 0:
            logger.warning("PricingService: Price suggestion missing or invalid. Constructing BOH markup fallback.")
            recommended_price = int(ingredient_cost * 3.0)
            if recommended_price == 0:
                recommended_price = 150

        estimated_profit = recommended_price - int(ingredient_cost)
        profit_margin = int((estimated_profit / recommended_price) * 100) if recommended_price > 0 else 0

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

    def generate_pricing_suggestion_fast(self, dish: str, ingredient_cost: float) -> Dict[str, Any]:
        """
        Fast programmatic pricing estimator to avoid calling LLM in a loop.
        """
        d_lower = dish.lower()
        if any(w in d_lower for w in ["special", "premium", "mutton", "chicken", "fish", "prawn", "crab"]):
            multiplier = 3.5
            pricing_strategy = "Premium"
            market_position = "Upscale"
        elif any(w in d_lower for w in ["veg", "paneer", "mushroom", "dosa", "idli", "sambar"]):
            multiplier = 2.8
            pricing_strategy = "Standard"
            market_position = "Mid-range"
        else:
            multiplier = 3.0
            pricing_strategy = "Standard"
            market_position = "Mid-range"

        recommended_price = int(ingredient_cost * multiplier)
        estimated_profit = int(recommended_price - ingredient_cost)
        profit_margin = int((estimated_profit / recommended_price) * 100) if recommended_price > 0 else 0
        price_confidence = 95

        return {
            "dish": dish,
            "ingredient_cost": float(ingredient_cost),
            "recommended_price": recommended_price,
            "estimated_profit": estimated_profit,
            "profit_margin": profit_margin,
            "pricing_strategy": pricing_strategy,
            "market_position": market_position,
            "price_confidence": price_confidence
        }

